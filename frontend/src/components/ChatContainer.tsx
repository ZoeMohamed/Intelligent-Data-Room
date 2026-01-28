import { useEffect, useRef, useState } from "react"
import { useAppState } from "../context/AppState"
import MarkdownRenderer from "./MarkdownRenderer"
import ChartRenderer from "./ChartRenderer"
import { buildApiUrl } from "../api/client"
import type { FileMetadata, FileStatus } from "../types"

// Keep file validation aligned with the backend CSV/XLSX support.
const MAX_FILE_MB = 10
const ALLOWED_EXTENSIONS = ["csv", "xlsx"]

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
  const activeFile = files[0]
  const showFileHighlight = Boolean(activeFile && activeFile.status === "ready")

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])


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
    const firstFile = fileArray[0]
    if (!firstFile) return
    files.forEach((file) => removeFile(file.id))

    const entries: FileMetadata[] = [firstFile].map((file) => {
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
      const entry = entries[0]
      if (entry.status === "uploading") {
        uploadFile(firstFile, entry.id)
      }
    }
  }

  return (
    <div className="flex h-full flex-col rounded-[32px] border border-white/45 bg-white/65 p-6 shadow-[0_35px_90px_-55px_rgba(15,23,42,0.35)] backdrop-blur-2xl">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/50 pb-4">
        <div className="flex items-center gap-3">
          <img src="/logo.svg" alt="Intelligent Data Room logo" className="h-11 w-11" />
          <div>
            <p className="text-[0.6rem] uppercase tracking-[0.3em] text-muted">Chat</p>
            <h2 className="font-display text-2xl text-ink">Intelligent Data Room</h2>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <label className="text-xs text-muted">Model</label>
          <select
            value={selectedModelId}
            onChange={(event) => selectModel(event.target.value)}
            className="rounded-full border border-white/60 bg-white/70 px-3 py-1 text-xs text-ink shadow-soft backdrop-blur"
          >
            {models.map((model) => (
              <option key={model.id} value={model.id}>
                {model.name}
              </option>
            ))}
          </select>
        </div>
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
                  ? "ml-auto border-accent/30 bg-accent/10 text-ink"
                  : isSystem
                    ? "border-white/60 bg-white/60 text-muted"
                    : isError
                      ? "border-red-200 bg-red-50/80 text-red-700"
                      : isWarning
                        ? "border-amber-200 bg-amber-50/80 text-amber-800"
                        : "border-white/60 bg-white/70 text-ink"
              }`}
            >
              <div className="space-y-2">
                {message.role === "assistant" ? (
                  <>
                    <MarkdownRenderer content={message.content || "Streaming response..."} />
                    {message.details && (
                      <details className="rounded-xl border border-white/70 bg-white/70 p-3 text-xs text-ink">
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
        <div className="relative overflow-hidden rounded-[28px] border border-white/70 bg-white/85 p-3 shadow-[0_30px_80px_-50px_rgba(15,23,42,0.35)] backdrop-blur">
          <div className="pointer-events-none absolute inset-0 bg-gradient-to-r from-white/80 via-white/50 to-accentSoft/35 opacity-70" />
          <div className="relative flex items-center gap-3">
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="flex h-11 w-11 items-center justify-center rounded-full border border-white/80 bg-white/90 text-lg text-muted shadow-[0_10px_30px_-18px_rgba(47,91,255,0.35)] transition hover:border-accent/50 hover:text-ink"
            aria-label="Attach file"
          >
            +
          </button>
          {/* Hidden input is triggered by the plus button for native file selection. */}
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
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
            rows={1}
            placeholder="Ask about your data..."
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
                event.preventDefault()
                sendCurrentInput()
              }
            }}
            className="h-11 flex-1 resize-none bg-transparent py-2.5 text-sm leading-6 text-ink outline-none placeholder:text-muted"
          />
          <button
            type="submit"
            className="h-11 rounded-full bg-gradient-to-r from-accent to-[#4f7dff] px-6 text-sm font-semibold text-white shadow-[0_18px_40px_-22px_rgba(47,91,255,0.8)] transition hover:brightness-110"
          >
            Send
          </button>
          </div>
        </div>
        {activeFile && (
          <div
            className={`mt-3 flex flex-wrap items-center gap-3 rounded-2xl border px-4 py-2 text-xs ${
              activeFile.status === "error"
                ? "border-red-300 bg-red-50/80 text-red-600"
                : showFileHighlight
                  ? "border-emerald/50 bg-emerald/10 text-ink shadow-[0_20px_40px_-30px_rgba(16,185,129,0.35)]"
                  : "border-white/60 bg-white/70 text-ink"
            }`}
          >
            <span className="font-semibold">
              {showFileHighlight ? "File uploaded" : activeFile.status === "uploading" ? "Uploading" : "File"}
            </span>
            <span className="text-muted">{activeFile.name}</span>
            <span className="text-muted">{formatBytes(activeFile.size)}</span>
            {activeFile.error && <span className="text-red-500">{activeFile.error}</span>}
            <button
              type="button"
              onClick={() => removeFile(activeFile.id)}
              className="ml-auto rounded-full border border-white/70 px-2 py-1 text-[0.65rem] font-semibold text-muted transition hover:border-red-200 hover:text-red-500"
            >
              Remove
            </button>
          </div>
        )}
      </form>
    </div>
  )
}

export default ChatContainer
