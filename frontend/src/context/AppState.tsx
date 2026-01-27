/* eslint-disable react-refresh/only-export-components */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode
} from "react"
import type { FileMetadata, Message, Model } from "../types"
import { MODEL_CATALOG, STARTER_MESSAGES } from "../data/seed"
import { buildApiUrl } from "../api/client"

type QueryResponse = {
  success?: boolean
  result?: unknown
  plan?: unknown
  chart?: unknown
  error?: string
}

interface AppState {
  models: Model[]
  selectedModelId: string
  files: FileMetadata[]
  messages: Message[]
}

interface AppActions {
  selectModel: (id: string) => void
  addFiles: (entries: FileMetadata[]) => void
  updateFile: (id: string, updates: Partial<FileMetadata>) => void
  removeFile: (id: string) => void
  sendMessage: (content: string) => void
}

type AppContextValue = AppState & AppActions

const AppStateContext = createContext<AppContextValue | undefined>(undefined)

// Shared ID helper for UI-only entities (messages/files).
const createId = () =>
  typeof crypto !== "undefined" && "randomUUID" in crypto
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(16).slice(2)}`

const MAX_ERROR_DETAILS = 280

const truncate = (value: string, maxLength: number) =>
  value.length > maxLength ? `${value.slice(0, maxLength)}…` : value

const extractRetrySeconds = (message: string) => {
  const retryMatch = message.match(/retry in ([0-9.]+)s/i)
  if (retryMatch?.[1]) {
    return Math.ceil(Number(retryMatch[1]))
  }

  const delayMatch = message.match(/retry_delay\s*{[^}]*seconds:\s*(\d+)/i)
  if (delayMatch?.[1]) {
    return Number(delayMatch[1])
  }

  return null
}

const NONSENSE_PATTERNS = [/^test+$/i, /^tes+$/i, /^asdf+$/i, /^qwer+$/i, /^ffff+$/i, /^ggg+$/i, /^aaa+$/i, /^bbb+$/i, /^xxx+$/i]

const isLowIntentPrompt = (prompt: string) => {
  const trimmed = prompt.trim()
  if (!trimmed) return true
  if (!/[a-zA-Z]/.test(trimmed)) return true
  if (trimmed.length < 4) return true
  if (trimmed.split(/\s+/).length === 1 && trimmed.length < 6) return true
  return NONSENSE_PATTERNS.some((pattern) => pattern.test(trimmed))
}

const summarizeError = (message: string, modelId: string) => {
  const lower = message.toLowerCase()
  const retrySeconds = extractRetrySeconds(message)

  if (lower.includes("quota") || lower.includes("rate limit") || lower.includes("429")) {
    const retryNote = retrySeconds ? ` Try again in about ${retrySeconds}s.` : ""
    return {
      variant: "error" as const,
      summary: `Rate limit reached for ${modelId}.${retryNote} Wait a bit, reduce requests, or switch models.`,
      details: truncate(message, MAX_ERROR_DETAILS)
    }
  }

  if (lower.includes("tabulate")) {
    return {
      variant: "error" as const,
      summary:
        "Backend is missing the 'tabulate' dependency (needed for table formatting). Install it on the server and retry.",
      details: truncate(message, MAX_ERROR_DETAILS)
    }
  }

  return {
    variant: "error" as const,
    summary: `Error: ${truncate(message, MAX_ERROR_DETAILS)}`,
    details: undefined
  }
}

const toChartPayload = (payload: unknown): Record<string, unknown> | undefined =>
  payload && typeof payload === "object" ? (payload as Record<string, unknown>) : undefined

export const AppStateProvider = ({ children }: { children: ReactNode }) => {
  const [models, setModels] = useState<Model[]>(MODEL_CATALOG)
  const [selectedModelId, setSelectedModelId] = useState(MODEL_CATALOG[0]?.id ?? "")
  const [files, setFiles] = useState<FileMetadata[]>([])
  const [messages, setMessages] = useState<Message[]>(STARTER_MESSAGES)

  const selectModel = useCallback((id: string) => {
    setSelectedModelId(id)
  }, [])

  const addFiles = useCallback((entries: FileMetadata[]) => {
    setFiles((prev) => [...entries, ...prev])
  }, [])

  const updateFile = useCallback((id: string, updates: Partial<FileMetadata>) => {
    setFiles((prev) => prev.map((file) => (file.id === id ? { ...file, ...updates } : file)))
  }, [])

  const removeFile = useCallback((id: string) => {
    setFiles((prev) => prev.filter((file) => file.id !== id))
  }, [])

  // Fetch available models from the backend; fall back to local catalog if unavailable.
  useEffect(() => {
    let isMounted = true

    const loadModels = async () => {
      try {
        const response = await fetch(buildApiUrl("/api/models"))
        if (!response.ok) {
          throw new Error("Unable to load models")
        }
        const data = (await response.json()) as { models?: Record<string, string> | string[] }
        const modelsPayload = data.models

        const cleanName = (label: string) => label.split(" - ")[0].trim()
        const normalized: Model[] = Array.isArray(modelsPayload)
          ? modelsPayload.map((modelId) => ({
              id: modelId,
              name: cleanName(modelId),
              provider: "Gemini",
              contextWindow: 8192,
              status: "available",
              description: "Available via backend"
            }))
          : modelsPayload
            ? Object.entries(modelsPayload).map(([modelId, label]) => ({
                id: modelId,
                name: cleanName(label),
                provider: "Gemini",
                contextWindow: 8192,
                status: "available",
                description: label
              }))
            : MODEL_CATALOG

        if (isMounted) {
          setModels(normalized)
          setSelectedModelId((prev) =>
            normalized.find((model) => model.id === prev) ? prev : normalized[0]?.id ?? ""
          )
        }
      } catch {
        if (isMounted) {
          setModels(MODEL_CATALOG)
          setSelectedModelId((prev) =>
            MODEL_CATALOG.find((model) => model.id === prev) ? prev : MODEL_CATALOG[0]?.id ?? ""
          )
        }
      }
    }

    loadModels()
    return () => {
      isMounted = false
    }
  }, [])

  // Send the prompt to the backend and append the response to the chat.
  const sendMessage = useCallback(
    async (content: string) => {
      const trimmed = content.trim()
      if (!trimmed) return

      const timestamp = new Date().toISOString()
      const userMessage: Message = {
        id: createId(),
        role: "user",
        content: trimmed,
        createdAt: timestamp
      }

      if (isLowIntentPrompt(trimmed)) {
        const assistantMessage: Message = {
          id: createId(),
          role: "assistant",
          content:
            "Your question is a bit vague. Please be more specific about what you want from the data (e.g., \"top 5 states by sales\", \"profit trend per year\").",
          createdAt: timestamp,
          variant: "warning"
        }
        setMessages((prev) => [...prev, userMessage, assistantMessage])
        return
      }

      const assistantId = createId()
      const assistantMessage: Message = {
        id: assistantId,
        role: "assistant",
        content: "Thinking...",
        createdAt: timestamp,
        isStreaming: true
      }

      setMessages((prev) => [...prev, userMessage, assistantMessage])

      const latestFile = [...files]
        .reverse()
        .find((file) => file.status === "ready" && file.filepath)

      if (!latestFile?.filepath) {
        setMessages((prev) =>
          prev.map((message) =>
            message.id === assistantId
              ? {
                  ...message,
                  content: "Please upload a CSV or XLSX file first.",
                  variant: "warning",
                  isStreaming: false
                }
              : message
          )
        )
        return
      }

      try {
        const response = await fetch(buildApiUrl("/api/query"), {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            query: trimmed,
            model: selectedModelId,
            filepath: latestFile.filepath
          })
        })

        let data: QueryResponse | null = null

        try {
          data = (await response.json()) as QueryResponse
        } catch {
          data = null
        }

        if (!response.ok) {
          const fallback = data?.error ?? `Request failed (${response.status})`
          throw new Error(fallback)
        }

        if (data?.success === false) {
          const fallback =
            data?.error ?? (typeof data?.result === "string" ? data.result : "The request failed.")
          throw new Error(fallback)
        }

        const rawResult = data?.result ?? "No result returned."
        const contentText =
          typeof rawResult === "string" ? rawResult : `\`\`\`json\n${JSON.stringify(rawResult, null, 2)}\n\`\`\``

        let composed = contentText

        const chartPayload = toChartPayload(data?.chart)
        if (chartPayload) {
          composed += `\n\nChart ready below.`
        }

        setMessages((prev) =>
          prev.map((message) =>
            message.id === assistantId
              ? {
                  ...message,
                  content: composed,
                  chart: chartPayload,
                  isStreaming: false
                }
              : message
          )
        )
      } catch (error) {
        const messageText = error instanceof Error ? error.message : "Something went wrong."
        const summarized = summarizeError(messageText, selectedModelId)
        setMessages((prev) =>
          prev.map((message) =>
            message.id === assistantId
              ? {
                  ...message,
                  content: summarized.summary,
                  details: summarized.details,
                  variant: summarized.variant,
                  isStreaming: false
                }
              : message
          )
        )
      }
    },
    [files, selectedModelId]
  )

  const value = useMemo<AppContextValue>(
    () => ({
      models,
      selectedModelId,
      files,
      messages,
      selectModel,
      addFiles,
      updateFile,
      removeFile,
      sendMessage
    }),
    [models, selectedModelId, files, messages, selectModel, addFiles, updateFile, removeFile, sendMessage]
  )

  return <AppStateContext.Provider value={value}>{children}</AppStateContext.Provider>
}

export const useAppState = () => {
  const context = useContext(AppStateContext)
  if (!context) {
    throw new Error("useAppState must be used within AppStateProvider")
  }
  return context
}
