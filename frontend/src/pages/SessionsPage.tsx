import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { listActivityTypes, listPlans, listSessions } from '@/api/client'
import { failureMessage } from '@/api/messages'
import { queryKeys, type SessionListFilters } from '@/api/queryKeys'
import { EmptyState, ErrorBanner } from '@/components/StatusMessage'
import { Badge } from '@/components/ui/badge'
import ActivityTypeSelect from '@/components/ActivityTypeSelect'
import { Button, buttonVariants } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { dayEndIso, dayStartIso, exerciseSummary, formatSessionAt, statusLabel } from '@/sessions/display'

const inputClassName =
  'h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:opacity-50'

const emptyFilters: SessionListFilters = {
  from: null,
  to: null,
  status: null,
  activityTypeId: null,
  unscheduled: null,
  planId: null,
}

type DraftFilters = {
  from: string
  to: string
  status: string
  unscheduled: string
  planId: string
  activityTypeId: string
}

const emptyDraft: DraftFilters = {
  from: '',
  to: '',
  status: '',
  unscheduled: '',
  planId: '',
  activityTypeId: '',
}

function filtersFromDraft(draft: DraftFilters): SessionListFilters | string {
  if (draft.from && draft.to && draft.from > draft.to) {
    return 'From must not be after to.'
  }
  const unscheduledOnly = draft.unscheduled === 'true'
  return {
    from: draft.from && !unscheduledOnly ? dayStartIso(draft.from) : null,
    to: draft.to && !unscheduledOnly ? dayEndIso(draft.to) : null,
    status: draft.status || null,
    activityTypeId: draft.activityTypeId || null,
    unscheduled:
      draft.unscheduled === 'true' ? true : draft.unscheduled === 'false' ? false : null,
    planId: draft.planId || null,
  }
}

export default function SessionsPage() {
  const [draft, setDraft] = useState<DraftFilters>(emptyDraft)
  const [applied, setApplied] = useState<SessionListFilters>(emptyFilters)
  const [rangeError, setRangeError] = useState<string | null>(null)

  const plansQuery = useQuery({
    queryKey: queryKeys.plans,
    queryFn: listPlans,
  })
  const activitiesQuery = useQuery({
    queryKey: queryKeys.activityTypes,
    queryFn: listActivityTypes,
  })
  const sessionsQuery = useQuery({
    queryKey: queryKeys.sessions(applied),
    queryFn: () => listSessions(applied),
  })

  const activityNames = new Map(
    (activitiesQuery.data ?? []).map((activity) => [activity.id, activity.name]),
  )
  const datesDisabled = draft.unscheduled === 'true'

  function updateDraft(patch: Partial<DraftFilters>) {
    setDraft((current) => ({ ...current, ...patch }))
  }

  function handleApply(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const next = filtersFromDraft(draft)
    if (typeof next === 'string') {
      setRangeError(next)
      return
    }
    setRangeError(null)
    setApplied(next)
  }

  function handleClear() {
    setDraft(emptyDraft)
    setApplied(emptyFilters)
    setRangeError(null)
  }

  const sessions = sessionsQuery.data ?? []
  const filtersActive = Object.values(applied).some((value) => value !== null)
  const listError = sessionsQuery.isError
    ? failureMessage(sessionsQuery.error, 'Could not load sessions.', 'You cannot view these sessions.')
    : null

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-col gap-6 p-6">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Sessions</h1>
          <p className="text-sm text-muted-foreground">
            Your sessions only. Filters are sent to the API.
          </p>
        </div>
        <Link className={buttonVariants()} to="/sessions/new">
          New session
        </Link>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
          <CardDescription>
            Date bounds cover the whole local day. Unscheduled hides the date range.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form className="grid gap-4 sm:grid-cols-2" onSubmit={handleApply}>
            <label className="flex flex-col gap-1.5 text-sm font-medium">
              From
              <input
                className={inputClassName}
                type="date"
                value={draft.from}
                disabled={datesDisabled}
                onChange={(event) => updateDraft({ from: event.target.value })}
              />
            </label>
            <label className="flex flex-col gap-1.5 text-sm font-medium">
              To
              <input
                className={inputClassName}
                type="date"
                value={draft.to}
                disabled={datesDisabled}
                onChange={(event) => updateDraft({ to: event.target.value })}
              />
            </label>
            <label className="flex flex-col gap-1.5 text-sm font-medium">
              Status
              <select
                className={inputClassName}
                value={draft.status}
                onChange={(event) => updateDraft({ status: event.target.value })}
              >
                <option value="">Any</option>
                <option value="planned">Planned</option>
                <option value="in_progress">In progress</option>
                <option value="completed">Completed</option>
              </select>
            </label>
            <label className="flex flex-col gap-1.5 text-sm font-medium">
              Schedule
              <select
                className={inputClassName}
                value={draft.unscheduled}
                onChange={(event) => updateDraft({ unscheduled: event.target.value })}
              >
                <option value="">Any</option>
                <option value="true">Unscheduled</option>
                <option value="false">Dated</option>
              </select>
            </label>
            <label className="flex flex-col gap-1.5 text-sm font-medium">
              Plan
              <select
                className={inputClassName}
                value={draft.planId}
                onChange={(event) => updateDraft({ planId: event.target.value })}
              >
                <option value="">Any</option>
                {(plansQuery.data ?? []).map((plan) => (
                  <option key={plan.id} value={plan.id}>
                    {plan.name}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1.5 text-sm font-medium">
              Activity
              <ActivityTypeSelect
                activities={activitiesQuery.data ?? []}
                value={draft.activityTypeId}
                onChange={(activityId) => updateDraft({ activityTypeId: activityId })}
                allowEmpty
                emptyLabel="Any"
              />
            </label>
            {rangeError ? <ErrorBanner className="sm:col-span-2">{rangeError}</ErrorBanner> : null}
            <div className="flex gap-2 sm:col-span-2">
              <Button type="submit">Apply</Button>
              <Button type="button" variant="outline" onClick={handleClear}>
                Clear
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {sessionsQuery.isPending ? (
        <p className="text-sm text-muted-foreground">Loading sessions…</p>
      ) : null}
      {plansQuery.isError ? (
        <ErrorBanner>
          {failureMessage(plansQuery.error, 'Could not load plans.', 'You cannot view these plans.')}
        </ErrorBanner>
      ) : null}
      {activitiesQuery.isError ? (
        <ErrorBanner>
          {failureMessage(
            activitiesQuery.error,
            'Could not load exercises.',
            'You cannot view these exercises.',
          )}
        </ErrorBanner>
      ) : null}
      {listError ? <ErrorBanner>{listError}</ErrorBanner> : null}
      {sessionsQuery.isSuccess && sessions.length === 0 ? (
        filtersActive ? (
          <EmptyState>No sessions match these filters.</EmptyState>
        ) : (
          <EmptyState actionTo="/sessions/new" actionLabel="New session">
            Create your first session.
          </EmptyState>
        )
      ) : null}

      <ul className="flex flex-col gap-3">
        {sessions.map((session) => (
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
