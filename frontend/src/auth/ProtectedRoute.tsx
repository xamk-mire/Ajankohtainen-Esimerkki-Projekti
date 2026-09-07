import { useEffect, useState } from 'react'
import { Link, Navigate, Outlet } from 'react-router-dom'
import { ApiError, getMe } from '@/api/client'
import { clearToken, getToken } from '@/auth/token'

type GateState = 'loading' | 'ok' | 'unauthenticated' | 'error'

export default function ProtectedRoute() {
  const [state, setState] = useState<GateState>('loading')

  useEffect(() => {
    let cancelled = false

    if (!getToken()) {
      setState('unauthenticated')
      return
    }

    getMe()
      .then(() => {
        if (!cancelled) {
          setState('ok')
        }
      })
      .catch((error) => {
        if (cancelled) {
          return
        }
        if (error instanceof ApiError && error.status === 401) {
          clearToken()
          setState('unauthenticated')
          return
        }
        setState('error')
      })

    return () => {
      cancelled = true
    }
  }, [])

  if (state === 'loading') {
    return (
      <main className="flex min-h-svh items-center justify-center bg-background p-6">
        <p className="text-sm text-muted-foreground">Checking session…</p>
      </main>
    )
  }

  if (state === 'unauthenticated') {
    return <Navigate to="/login" replace />
  }

  if (state === 'error') {
    return (
      <main className="flex min-h-svh items-center justify-center bg-background p-6">
        <p className="text-sm text-muted-foreground">
          Could not verify your session. Refresh the page, or{' '}
          <Link className="text-primary underline-offset-4 hover:underline" to="/login">
            go to login
          </Link>
          .
        </p>
      </main>
    )
  }

  return <Outlet />
}
