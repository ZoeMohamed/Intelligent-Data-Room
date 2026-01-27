export type MessageRole = "user" | "assistant" | "system"

export interface Message {
  id: string
  role: MessageRole
  content: string
  createdAt: string
  isStreaming?: boolean
  chart?: Record<string, unknown>
  variant?: "normal" | "warning" | "error"
  details?: string
}

export type ModelStatus = "available" | "limited" | "offline"

export interface Model {
  id: string
  name: string
  provider: string
  contextWindow: number
  status: ModelStatus
  description: string
}

export type FileStatus = "queued" | "uploading" | "ready" | "error"

export interface FileMetadata {
  id: string
  name: string
  size: number
  type: string
  status: FileStatus
  progress: number
  error?: string
  filepath?: string
  columnNames?: string[]
  preview?: Record<string, unknown>[]
  rows?: number
}
