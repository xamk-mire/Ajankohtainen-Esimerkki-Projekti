import { Link, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ApiError, getSession, listActivityTypes } from '@/api/client'
import { queryKeys } from '@/api/queryKeys'
import { Badge } from '@/components/ui/badge'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { exerciseSummary, formatSessionAt, statusLabel } from '@/sessions/display'

export default function SessionFormPage() {
  const { sessionId = '' } = useParams()
  const sessionQuery = useQuery({
    queryKey: queryKeys.session(sessionId),
    queryFn: () => getSession(sessionId),
    enabled: sessionId.length > 0,
  })
  const activitiesQuery = useQuery({
    queryKey: queryKeys.activityTypes,
    queryFn: listActivityTypes,
  })
  const activityNames = new Map(
    (activitiesQuery.data ?? []).map((activity) => [activity.id, activity.name]),
  )

  const missing =
    sessionQuery.error instanceof ApiError && sessionQuery.error.status === 404

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-col gap-6 p-6">
      <Link className="text-sm text-primary underline-offset-4 hover:underline" to="/sessions">
        Back to sessions
      </Link>
      {sessionQuery.isPending ? (
        <p className="text-sm text-muted-foreground">Loading session…</p>
      ) : null}
      {missing ? (
        <p className="text-sm text-muted-foreground">Session not found.</p>
      ) : null}
      {sessionQuery.isError && !missing ? (
        <p className="text-sm text-destructive" role="alert">
          Could not load this session.
        </p>
      ) : null}
      {sessionQuery.data ? (
        <Card>
          <CardHeader className="flex flex-row items-start justify-between gap-3">
            <div className="flex flex-col gap-1">
              <CardTitle>{sessionQuery.data.name}</CardTitle>
              <CardDescription>{formatSessionAt(sessionQuery.data.session_at)}</CardDescription>
            </div>
            <Badge variant="outline">{statusLabel(sessionQuery.data.status)}</Badge>
          </CardHeader>
          <CardContent className="flex flex-col gap-2 text-sm text-muted-foreground">
            <p>{exerciseSummary(sessionQuery.data.items, activityNames)}</p>
            <p>The session designer will edit this session in the next step.</p>
          </CardContent>
        </Card>
      ) : null}
    </main>
  )
}
