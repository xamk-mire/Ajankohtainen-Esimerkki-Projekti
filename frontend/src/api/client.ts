import { clearToken, getToken } from '@/auth/token'

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
).replace(/\/$/, '')

export function getApiBaseUrl(): string {
  return API_BASE_URL
}

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly fieldErrors: Record<string, string> = {},
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

type FastApiErrorBody = {
  detail?: string | { loc?: (string | number)[]; msg?: string }[]
}

function apiUrl(path: string): string {
  return `${API_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`
}

function requestHeaders(extra?: Record<string, string>): Headers {
  const headers = new Headers(extra)
  const token = getToken()
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }
  return headers
}

async function parseError(response: Response): Promise<ApiError> {
  const fallback = `API ${response.status} ${response.statusText}`
  try {
    const data = (await response.json()) as FastApiErrorBody
    if (typeof data.detail === 'string') {
      return new ApiError(data.detail, response.status)
    }
    if (Array.isArray(data.detail)) {
      const fieldErrors: Record<string, string> = {}
      const messages: string[] = []
      for (const item of data.detail) {
        const msg = item.msg ?? fallback
        messages.push(msg)
        const field = (item.loc ?? [])
          .filter((part) => part !== 'body')
          .join('.')
        if (field && !fieldErrors[field]) {
          fieldErrors[field] = msg
        }
      }
      return new ApiError(messages.join(' ') || fallback, response.status, fieldErrors)
    }
  } catch {
    // Non-JSON error body.
  }
  return new ApiError(fallback, response.status)
}

async function handleResponse<T>(path: string, response: Response): Promise<T> {
  if (!response.ok) {
    // Drop a stale JWT so later pages do not keep sending it. Leave login
    // 401s alone so a mistyped password does not wipe an existing session.
    if (response.status === 401 && path !== '/auth/login') {
      clearToken()
    }
    throw await parseError(response)
  }
  return (await response.json()) as T
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(apiUrl(path), {
    headers: requestHeaders(),
  })
  return handleResponse<T>(path, response)
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(apiUrl(path), {
    method: 'POST',
    headers: requestHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(body),
  })
  return handleResponse<T>(path, response)
}

export type HealthResponse = {
  status: string
}

export function getHealth(): Promise<HealthResponse> {
  return apiGet<HealthResponse>('/health')
}

export type UserPublic = {
  id: string
  email: string
  display_name: string
}

export type RegisterPayload = {
  email: string
  password: string
  display_name: string
}

export function registerUser(payload: RegisterPayload): Promise<UserPublic> {
  return apiPost<UserPublic>('/auth/register', payload)
}

export type LoginPayload = {
  email: string
  password: string
}

export type TokenResponse = {
  access_token: string
  token_type: string
}

export function loginUser(payload: LoginPayload): Promise<TokenResponse> {
  return apiPost<TokenResponse>('/auth/login', payload)
}
