import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getApiBaseUrl, getHealth } from '@/api/client'
import { queryKeys } from '@/api/queryKeys'
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
  const apiBaseUrl = getApiBaseUrl()
  const healthQuery = useQuery({
    queryKey: queryKeys.health,
    queryFn: getHealth,
  })

  const health: HealthState = healthQuery.isPending
    ? 'loading'
    : healthQuery.isError || healthQuery.data.status !== 'ok'
      ? 'failed'
      : 'ok'

  const healthLabel =
    health === 'loading' ? 'checking…' : health === 'ok' ? 'OK' : 'failed'
  const healthVariant =
    health === 'ok' ? 'default' : health === 'failed' ? 'destructive' : 'outline'

  return (
    <main className="flex flex-1 items-center justify-center p-6">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <CardTitle className="text-2xl">Exercise Progress Tracker</CardTitle>
          <CardDescription>
            Protected app shell. Sessions, plans, calendar, and progress pages
            will nest here in later sprints.
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
          <p className="flex gap-4 text-sm">
            <Link className="text-primary underline-offset-4 hover:underline" to="/sessions">
              Sessions
            </Link>
            <Link className="text-primary underline-offset-4 hover:underline" to="/plans">
              Plans
            </Link>
            <Link className="text-primary underline-offset-4 hover:underline" to="/calendar">
              Calendar
            </Link>
          </p>
        </CardContent>
      </Card>
    </main>
  )
}
