import { useEffect, useRef, useState } from "react"
import { useAppState } from "../context/AppState"
import MarkdownRenderer from "./MarkdownRenderer"
import ChartRenderer from "./ChartRenderer"
import { buildApiUrl } from "../api/client"
import type { FileMetadata, FileStatus } from "../types"

// Keep file validation aligned with the backend CSV/XLSX support.
const MAX_FILE_MB = 10
const ALLOWED_EXTENSIONS = ["csv", "xlsx"]
const MEMORY_LIMIT = 5

const truncateText = (value: string, max = 90) =>
  value.length > max ? `${value.slice(0, max).trimEnd()}…` : value

const formatBytes = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`
  const kb = bytes / 1024
  if (kb < 1024) return `${kb.toFixed(1)} KB`
  return `${(kb / 1024).toFixed(1)} MB`
}

const createId = () =>
  typeof crypto !== "undefined" && "randomUUID" in crypto
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(16).slice(2)}`

const isAllowedType = (file: File) => {
  const extension = file.name.split(".").pop()?.toLowerCase() ?? ""
  return ALLOWED_EXTENSIONS.includes(extension)
}

const StreamingDots = () => (
  <span className="inline-flex items-center gap-1 text-muted">
    <span className="h-1 w-1 animate-pulse rounded-full bg-muted" />
    <span className="h-1 w-1 animate-pulse rounded-full bg-muted [animation-delay:150ms]" />
    <span className="h-1 w-1 animate-pulse rounded-full bg-muted [animation-delay:300ms]" />
  </span>
)

const ChatContainer = () => {
  const { messages, sendMessage, selectedModelId, models, files, addFiles, updateFile, removeFile, selectModel } =
    useAppState()
  const [input, setInput] = useState("")
  const bottomRef = useRef<HTMLDivElement | null>(null)
  const textareaRef = useRef<HTMLTextAreaElement | null>(null)
  const fileInputRef = useRef<HTMLInputElement | null>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const memoryPreview = messages
    .filter((message) => message.role !== "system" && message.content.trim().length > 0)
    .slice(-MEMORY_LIMIT)

  const sendCurrentInput = () => {
    if (!input.trim()) return
    sendMessage(input)
    setInput("")
    textareaRef.current?.focus()
  }

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    sendCurrentInput()
  }

  const uploadFile = async (file: File, entryId: string) => {
    const form = new FormData()
    form.append("file", file)

    updateFile(entryId, { status: "uploading", progress: 30 })

    try {
      const response = await fetch(buildApiUrl("/api/upload"), {
        method: "POST",
        body: form
      })
      const data = (await response.json()) as {
        filepath?: string
        column_names?: string[]
        preview?: Record<string, unknown>[]
        rows?: number
        error?: string
      }

      if (!response.ok || data.error) {
        throw new Error(data.error || "Upload failed.")
      }

      updateFile(entryId, {
        status: "ready",
        progress: 100,
        filepath: data.filepath,
        columnNames: data.column_names,
        preview: data.preview,
        rows: data.rows
      })
    } catch (error) {
      const message = error instanceof Error ? error.message : "Upload failed."
      updateFile(entryId, { status: "error", progress: 0, error: message })
    }
  }

  // Convert native File objects into UI metadata for chips and progress.
  const handleFiles = (selected: FileList | File[]) => {
    const fileArray = Array.from(selected)
    const entries: FileMetadata[] = fileArray.map((file) => {
      const sizeMb = file.size / (1024 * 1024)
      const isValidType = isAllowedType(file)
      const isValidSize = sizeMb <= MAX_FILE_MB
      const id = createId()

      const status: FileStatus = isValidType && isValidSize ? "uploading" : "error"
      const entry: FileMetadata = {
        id,
        name: file.name,
        size: file.size,
        type: file.type || "unknown",
        status,
        progress: status === "uploading" ? 10 : 0,
        error: !isValidType
          ? `Unsupported file type. Allowed: ${ALLOWED_EXTENSIONS.join(", ")}.`
          : !isValidSize
            ? `File too large. Max ${MAX_FILE_MB} MB.`
            : undefined
      }

      return entry
    })

    if (entries.length) {
      addFiles(entries)
      entries.forEach((entry, index) => {
        if (entry.status === "uploading") {
          uploadFile(fileArray[index], entry.id)
        }
      })
    }
  }

  return (
    <div className="flex h-full flex-col rounded-2xl border border-border bg-panel/90 p-6 shadow-soft">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border pb-4">
        <div className="flex items-center gap-3">
          <img src="/logo.svg" alt="Intelligent Data Room logo" className="h-11 w-11" />
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-muted">Chat</p>
            <h2 className="font-display text-2xl text-ink">Intelligent Data Room</h2>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <label className="text-xs text-muted">Model</label>
          <select
            value={selectedModelId}
            onChange={(event) => selectModel(event.target.value)}
            className="rounded-full border border-border bg-surface px-3 py-1 text-xs text-ink"
          >
            {models.map((model) => (
              <option key={model.id} value={model.id}>
                {model.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="mt-4 rounded-2xl border border-border/80 bg-gradient-to-br from-white via-white to-accentSoft/40 p-4 shadow-soft">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center rounded-full bg-accentSoft px-2.5 py-1 text-[0.6rem] font-semibold uppercase tracking-[0.2em] text-accent">
              Memory
            </span>
            <span className="text-[0.7rem] text-muted">Last {MEMORY_LIMIT} messages</span>
          </div>
          <span className="text-[0.65rem] text-muted">Used for follow-up questions</span>
        </div>
        {memoryPreview.length === 0 ? (
          <p className="mt-3 text-[0.8rem] text-muted">No recent context yet.</p>
        ) : (
          <div className="mt-3 space-y-2">
            {memoryPreview.map((message) => (
              <div
                key={message.id}
                className="flex items-start gap-3 rounded-xl border border-border/70 bg-white/70 px-3 py-2 text-[0.78rem] text-ink shadow-[0_10px_30px_-25px_rgba(15,23,42,0.35)]"
              >
                <span
                  className={`mt-0.5 inline-flex min-w-[72px] items-center justify-center rounded-full px-2 py-0.5 text-[0.65rem] font-semibold uppercase tracking-[0.12em] ${
                    message.role === "user"
                      ? "bg-accentSoft text-accent"
                      : "bg-surface text-muted"
                  }`}
                >
                  {message.role === "user" ? "User" : "Assistant"}
                </span>
                <span className="leading-relaxed">{truncateText(message.content, 140)}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="mt-4 flex-1 space-y-4 overflow-y-auto pr-2">
        {messages.map((message) => {
          const isUser = message.role === "user"
          const isSystem = message.role === "system"
          const isError = message.variant === "error"
          const isWarning = message.variant === "warning"
          return (
            <div
              key={message.id}
              className={`rounded-2xl border px-4 py-3 text-sm ${
                isUser
                  ? "ml-auto border-accent/40 bg-accentSoft text-ink"
                  : isSystem
                    ? "border-border bg-surface text-muted"
                    : isError
                      ? "border-red-200 bg-red-50 text-red-700"
                      : isWarning
                        ? "border-amber-200 bg-amber-50 text-amber-800"
                        : "border-border bg-surface text-ink"
              }`}
            >
              <div className="space-y-2">
                {message.role === "assistant" ? (
                  <>
                    <MarkdownRenderer content={message.content || "Streaming response..."} />
                    {message.details && (
                      <details className="rounded-xl border border-border bg-white/70 p-3 text-xs text-ink">
                        <summary className="cursor-pointer text-xs font-semibold text-muted">
                          Details
                        </summary>
                        <pre className="mt-2 whitespace-pre-wrap text-[0.72rem] text-ink">
                          {message.details}
                        </pre>
                      </details>
                    )}
                    <ChartRenderer figure={message.chart ?? null} />
                  </>
                ) : (
                  <p className="leading-relaxed text-ink">{message.content}</p>
                )}
                {message.isStreaming && (
                  <div className="pt-2">
                    <StreamingDots />
                  </div>
                )}
              </div>
            </div>
          )
        })}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSubmit} className="mt-5">
        <div className="flex items-end gap-3 rounded-2xl border border-border bg-surface p-3">
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="flex h-11 w-11 items-center justify-center rounded-full border border-border text-lg text-muted transition hover:border-accent/50 hover:text-ink"
            aria-label="Attach file"
          >
            +
          </button>
          {/* Hidden input is triggered by the plus button for native file selection. */}
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            multiple
            accept=".csv,.xlsx"
            onChange={(event) => {
              if (event.target.files?.length) {
                handleFiles(event.target.files)
                event.target.value = ""
              }
            }}
          />
          <textarea
            ref={textareaRef}
            rows={2}
            placeholder="Ask about your data..."
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
                event.preventDefault()
                sendCurrentInput()
              }
            }}
            className="h-14 flex-1 resize-none bg-transparent text-sm text-ink outline-none placeholder:text-muted"
          />
          <button type="submit" className="h-12 rounded-full bg-accent px-5 text-sm font-semibold text-white shadow-glow">
            Send
          </button>
        </div>
        {files.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {files.map((file) => (
              <div
                key={file.id}
                title={file.error}
                className={`flex items-center gap-2 rounded-full border px-3 py-1 text-xs ${
                  file.status === "error"
                    ? "border-red-300 bg-red-50 text-red-600"
                    : "border-border bg-panel text-ink"
                }`}
              >
                <span>{file.name}</span>
                <span className="text-muted">{formatBytes(file.size)}</span>
                <button type="button" onClick={() => removeFile(file.id)} className="text-muted hover:text-ink">
                  ×
                </button>
              </div>
            ))}
          </div>
        )}
      </form>
    </div>
  )
}

export default ChatContainer
