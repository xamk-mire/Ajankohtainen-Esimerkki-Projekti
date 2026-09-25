import { clearToken, getToken } from '@/auth/token'
import type { SessionListFilters } from '@/api/queryKeys'

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

export async function apiPatch<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(apiUrl(path), {
    method: 'PATCH',
    headers: requestHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(body),
  })
  return handleResponse<T>(path, response)
}

export async function apiDelete(path: string): Promise<void> {
  const response = await fetch(apiUrl(path), {
    method: 'DELETE',
    headers: requestHeaders(),
  })
  if (!response.ok) {
    if (response.status === 401 && path !== '/auth/login') {
      clearToken()
    }
    throw await parseError(response)
  }
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

export function getMe(): Promise<UserPublic> {
  return apiGet<UserPublic>('/auth/me')
}

export type SessionMeasurement = {
  id: string
  unit_type_id: string
  planned_value: string | null
  actual_value: string | null
  set_index: number | null
}

export type SessionItem = {
  id: string
  activity_type_id: string
  sort_order: number
  notes: string | null
  measurements: SessionMeasurement[]
}

export type Session = {
  id: string
  user_id: string
  name: string
  session_at: string | null
  status: string
  notes: string | null
  intensity: number | null
  plan_id: string | null
  source_session_id: string | null
  created_at: string
  updated_at: string
  items: SessionItem[]
}

export type PlanSummary = {
  id: string
  name: string
}

export type UnitTypeSummary = {
  id: string
  name: string
  slug: string
  unit_label: string | null
}

export type ActivityUnitLink = {
  unit_type_id: string
  sort_order: number
  is_required: boolean
  per_set: boolean
  unit_type: UnitTypeSummary
}

export type ActivityTypeSummary = {
  id: string
  name: string
  unit_links: ActivityUnitLink[]
}

export type SessionMeasurementWrite = {
  unit_type_id: string
  planned_value: string | null
  actual_value: string | null
  set_index: number | null
}

export type SessionItemWrite = {
  activity_type_id: string
  sort_order: number
  notes: string | null
  measurements: SessionMeasurementWrite[]
}

export type SessionWrite = {
  name: string
  session_at: string | null
  status: 'planned' | 'in_progress' | 'completed'
  notes: string | null
  intensity: number | null
  plan_id: string | null
  items: SessionItemWrite[]
}

export function listSessions(filters: SessionListFilters = {}): Promise<Session[]> {
  const params = new URLSearchParams()
  if (filters.from) {
    params.set('from', filters.from)
  }
  if (filters.to) {
    params.set('to', filters.to)
  }
  if (filters.status) {
    params.set('status', filters.status)
  }
  if (filters.activityTypeId) {
    params.set('activity_type_id', filters.activityTypeId)
  }
  if (filters.unscheduled === true) {
    params.set('unscheduled', 'true')
  } else if (filters.unscheduled === false) {
    params.set('unscheduled', 'false')
  }
  if (filters.planId) {
    params.set('plan_id', filters.planId)
  }
  const query = params.toString()
  return apiGet<Session[]>(query ? `/sessions?${query}` : '/sessions')
}

export function getSession(sessionId: string): Promise<Session> {
  return apiGet<Session>(`/sessions/${sessionId}`)
}

export function listPlans(): Promise<PlanSummary[]> {
  return apiGet<PlanSummary[]>('/plans')
}

export function listActivityTypes(): Promise<ActivityTypeSummary[]> {
  return apiGet<ActivityTypeSummary[]>('/activity-types')
}

export function createSession(body: SessionWrite): Promise<Session> {
  return apiPost<Session>('/sessions', body)
}

export function updateSession(sessionId: string, body: SessionWrite): Promise<Session> {
  return apiPatch<Session>(`/sessions/${sessionId}`, body)
}

export type SessionCloneBody = {
  name?: string
  session_at?: string | null
}

export function cloneSession(sessionId: string, body: SessionCloneBody): Promise<Session> {
  return apiPost<Session>(`/sessions/${sessionId}/clone`, body)
}

export function deleteSession(sessionId: string): Promise<void> {
  return apiDelete(`/sessions/${sessionId}`)
}
