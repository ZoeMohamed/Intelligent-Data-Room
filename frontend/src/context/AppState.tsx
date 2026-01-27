/* eslint-disable react-refresh/only-export-components */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode
} from "react"
import type { FileMetadata, Message, Model } from "../types"
import { MODEL_CATALOG, STARTER_MESSAGES } from "../data/seed"

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

// UI-only mock response; replace with real API calls when backend is connected.
const buildMockResponse = (prompt: string, model: Model | undefined, files: FileMetadata[]) => {
  const fileList = files.length
    ? files.map((file) => `- ${file.name} (${Math.round(file.size / 1024)} KB)`).join("\n")
    : "- No files attached"

  return `Planner summary:\n1. Interpret question intent\n2. Identify relevant columns\n3. Prepare aggregation steps\n4. Choose chart type\n\nExecutor notes:\n- Model: ${model?.name ?? "Local Model"}\n- Provider: ${model?.provider ?? "Local"}\n\nFiles in context:\n${fileList}\n\nExample transformation:\n\`\`\`python\nresult = df.groupby("Category")["Sales"].sum().reset_index()\n\`\`\`\n\nAsk a follow-up like "show the top 5 categories" or "plot the trend" and I will continue streaming results.\n\nOriginal prompt: ${prompt}`
}

export const AppStateProvider = ({ children }: { children: ReactNode }) => {
  const [models] = useState<Model[]>(MODEL_CATALOG)
  const [selectedModelId, setSelectedModelId] = useState(models[0]?.id ?? "")
  const [files, setFiles] = useState<FileMetadata[]>([])
  const [messages, setMessages] = useState<Message[]>(STARTER_MESSAGES)
  const streamingTimers = useRef<number[]>([])

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

  // Simulate token streaming by incrementally revealing the mock response.
  const sendMessage = useCallback(
    (content: string) => {
      const trimmed = content.trim()
      if (!trimmed) return

      const timestamp = new Date().toISOString()
      const userMessage: Message = {
        id: createId(),
        role: "user",
        content: trimmed,
        createdAt: timestamp
      }

      const assistantId = createId()
      const assistantMessage: Message = {
        id: assistantId,
        role: "assistant",
        content: "",
        createdAt: timestamp,
        isStreaming: true
      }

      setMessages((prev) => [...prev, userMessage, assistantMessage])

      // Pick the selected model to label the mock response.
      const model = models.find((entry) => entry.id === selectedModelId)
      const responseText = buildMockResponse(trimmed, model, files)
      let cursor = 0

      const intervalId = window.setInterval(() => {
        cursor = Math.min(responseText.length, cursor + Math.max(2, Math.floor(Math.random() * 6)))
        setMessages((prev) =>
          prev.map((message) =>
            message.id === assistantId
              ? {
                  ...message,
                  content: responseText.slice(0, cursor),
                  isStreaming: cursor < responseText.length
                }
              : message
          )
        )

        if (cursor >= responseText.length) {
          window.clearInterval(intervalId)
        }
      }, 18)

      streamingTimers.current.push(intervalId)
    },
    [files, models, selectedModelId]
  )

  useEffect(() => {
    const timers = streamingTimers.current
    return () => {
      timers.forEach((timer) => window.clearInterval(timer))
    }
  }, [])

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
