import type { Message, Model } from "../types"

export const MODEL_CATALOG: Model[] = [
  {
    id: "gemini-2.5-flash",
    name: "Gemini 2.5 Flash",
    provider: "Gemini",
    contextWindow: 8192,
    status: "available",
    description: "Fast, cost-efficient model for daily analysis."
  },
  {
    id: "gemini-2.5-pro",
    name: "Gemini 2.5 Pro",
    provider: "Gemini",
    contextWindow: 16384,
    status: "limited",
    description: "Higher quality reasoning for complex datasets."
  }
]

export const STARTER_MESSAGES: Message[] = [
  {
    id: "system-1",
    role: "system",
    content: "Upload a CSV or XLSX, then ask a question about the data.",
    createdAt: new Date().toISOString()
  }
]
