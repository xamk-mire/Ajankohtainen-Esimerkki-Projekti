import { useEffect, useState } from 'react'
import { getApiBaseUrl, getHealth } from '@/api/client'
import { Badge } from '@/components/ui/badge'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

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
  const healthVariant =
    health === 'ok' ? 'default' : health === 'failed' ? 'destructive' : 'outline'

  return (
    <main className="flex min-h-svh items-center justify-center bg-background p-6">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <CardTitle className="text-2xl">Exercise Progress Tracker</CardTitle>
          <CardDescription>
            Sprint 1 placeholder. Login, sessions, plans, calendar, and progress
            pages will be added in later sprints.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <p className="text-sm text-muted-foreground">
            API base URL:{' '}
            <code className="rounded-md bg-muted px-1.5 py-0.5 font-mono text-foreground">
              {apiBaseUrl}
            </code>
          </p>
          <p className="flex items-center gap-2 text-sm">
            API health:{' '}
            <Badge variant={healthVariant}>{healthLabel}</Badge>
          </p>
        </CardContent>
      </Card>
    </main>
  )
}
