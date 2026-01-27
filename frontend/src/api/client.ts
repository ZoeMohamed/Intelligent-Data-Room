export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "https://be-intelligent.onrender.com"

export const buildApiUrl = (path: string) => {
  const base = API_BASE_URL.replace(/\/$/, "")
  const cleanedPath = path.startsWith("/") ? path : `/${path}`
  return `${base}${cleanedPath}`
}
