import { useEffect, useState } from 'react'
import { Link, Navigate, Outlet } from 'react-router-dom'
import { ApiError, getMe, type UserPublic } from '@/api/client'
import { clearToken, getToken } from '@/auth/token'
import Header from '@/components/Header'

type GateState = 'loading' | 'ok' | 'unauthenticated' | 'error'

export default function ProtectedRoute() {
  const [state, setState] = useState<GateState>('loading')
  const [user, setUser] = useState<UserPublic | null>(null)

  useEffect(() => {
    let cancelled = false

    if (!getToken()) {
      setUser(null)
      setState('unauthenticated')
      return
    }

    getMe()
      .then((profile) => {
        if (!cancelled) {
          setUser(profile)
          setState('ok')
        }
      })
      .catch((error) => {
        if (cancelled) {
          return
        }
        setUser(null)
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

  function handleLogout() {
    clearToken()
    setUser(null)
    setState('unauthenticated')
  }

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

  if (state === 'error' || !user) {
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

  return (
    <div className="flex min-h-svh flex-col bg-background">
      <Header user={user} onLogout={handleLogout} />
      <Outlet />
    </div>
  )
}
