import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  getApiBaseUrl,
  getHealth,
  listActivityTypes,
  listSessions,
  type Session,
} from '@/api/client'
import { queryKeys } from '@/api/queryKeys'
import { failureMessage } from '@/api/messages'
import { EmptyState, ErrorBanner } from '@/components/StatusMessage'
import { Badge } from '@/components/ui/badge'
import { buttonVariants } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { exerciseSummary, formatSessionAt, statusLabel } from '@/sessions/display'

const recentFilters = { unscheduled: false }
const recentLimit = 8

type HealthState = 'loading' | 'ok' | 'failed'

function recentDated(sessions: Session[]): Session[] {
  return sessions
    .filter((session) => session.session_at)
    .sort((left, right) => {
      const leftTime = new Date(left.session_at ?? 0).getTime()
      const rightTime = new Date(right.session_at ?? 0).getTime()
      return rightTime - leftTime
    })
    .slice(0, recentLimit)
}

export default function DashboardPage() {
  const apiBaseUrl = getApiBaseUrl()
  const healthQuery = useQuery({
    queryKey: queryKeys.health,
    queryFn: getHealth,
  })
  const sessionsQuery = useQuery({
    queryKey: queryKeys.sessions(recentFilters),
    queryFn: () => listSessions(recentFilters),
  })
  const activitiesQuery = useQuery({
    queryKey: queryKeys.activityTypes,
    queryFn: listActivityTypes,
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

  const activityNames = new Map(
    (activitiesQuery.data ?? []).map((activity) => [activity.id, activity.name]),
  )
  const recent = recentDated(sessionsQuery.data?.items ?? [])
  const listError = sessionsQuery.isError
    ? failureMessage(sessionsQuery.error, 'Could not load sessions.', 'You cannot view these sessions.')
    : null

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-col gap-6 p-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Dashboard</h1>
          <p className="text-sm text-muted-foreground">
            Your recent dated sessions. Unscheduled ones stay on the session list.
          </p>
        </div>
        <Link className={buttonVariants()} to="/sessions/new">
          New session
        </Link>
      </div>

      <p className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground">
        <span>
          API health: <Badge variant={healthVariant}>{healthLabel}</Badge>
        </span>
        <code className="rounded-md bg-muted px-1.5 py-0.5 font-mono text-foreground">
          {apiBaseUrl}
        </code>
      </p>

      {sessionsQuery.isPending ? (
        <p className="text-sm text-muted-foreground">Loading sessions…</p>
      ) : null}
      {listError ? <ErrorBanner>{listError}</ErrorBanner> : null}
      {sessionsQuery.isSuccess && recent.length === 0 ? (
        <EmptyState actionTo="/sessions/new" actionLabel="New session">
          Create your first session.
        </EmptyState>
      ) : null}

      <ul className="flex flex-col gap-3">
        {recent.map((session) => (
          <li key={session.id}>
            <Card>
              <CardHeader className="flex flex-row items-start justify-between gap-3">
                <div className="flex flex-col gap-1">
                  <CardTitle>{session.name}</CardTitle>
                  <CardDescription>{formatSessionAt(session.session_at)}</CardDescription>
                </div>
                <Badge variant="outline">{statusLabel(session.status)}</Badge>
              </CardHeader>
              <CardContent className="flex items-center justify-between gap-3">
                <p className="text-sm text-muted-foreground">
                  {exerciseSummary(session.items, activityNames)}
                </p>
                <Link
                  className="text-sm text-primary underline-offset-4 hover:underline"
                  to={`/sessions/${session.id}`}
                >
                  Edit
                </Link>
              </CardContent>
            </Card>
          </li>
        ))}
      </ul>
    </main>
  )
}
