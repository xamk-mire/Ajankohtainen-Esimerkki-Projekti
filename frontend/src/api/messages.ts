import { ApiError } from '@/api/client'

export function failureMessage(error: unknown, fallback: string, forbidden: string): string {
  if (error instanceof ApiError && error.status === 403) {
    return forbidden
  }
  if (error instanceof ApiError && error.message) {
    return error.message
  }
  return fallback
}
