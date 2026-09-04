import { useEffect, useState } from 'react'
import { getApiBaseUrl, getHealth } from '../api/client'

type HealthState = 'loading' | 'ok' | 'failed'

export default function HomePage() {
  const [health, setHealth] = useState<HealthState>('loading')
  const apiBaseUrl = getApiBaseUrl()

  useEffect(() => {
    let cancelled = false

    getHealth()
      .then((data) => {
        if (!cancelled) {
          setHealth(data.status === 'ok' ? 'ok' : 'failed')
        }
      })
      .catch(() => {
        if (!cancelled) {
          setHealth('failed')
        }
      })

    return () => {
      cancelled = true
    }
  }, [])

  const healthLabel =
    health === 'loading' ? 'checking…' : health === 'ok' ? 'OK' : 'failed'

  return (
    <main className="home">
      <h1>Exercise Progress Tracker</h1>
      <p>
        Sprint 1 placeholder. Login, sessions, plans, calendar, and progress
        pages will be added in later sprints.
      </p>
      <p className="api-base">
        API base URL: <code>{apiBaseUrl}</code>
      </p>
      <p className={`health health-${health}`}>API health: {healthLabel}</p>
    </main>
  )
}
