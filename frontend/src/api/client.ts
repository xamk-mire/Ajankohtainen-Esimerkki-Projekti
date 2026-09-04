const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
).replace(/\/$/, '')

export function getApiBaseUrl(): string {
  return API_BASE_URL
}

export async function apiGet<T>(path: string): Promise<T> {
  const url = `${API_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`
  const response = await fetch(url)
  if (!response.ok) {
    throw new Error(`API ${response.status} ${response.statusText}`)
  }
  return (await response.json()) as T
}

export type HealthResponse = {
  status: string
}

export function getHealth(): Promise<HealthResponse> {
  return apiGet<HealthResponse>('/health')
}
