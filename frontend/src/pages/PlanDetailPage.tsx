import { useState, type FormEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  ApiError,
  attachPlanSession,
  deletePlan,
  detachPlanSession,
  getPlan,
  listSessions,
  updatePlan,
  type PlanSession,
  type PlanWrite,
} from '@/api/client'
import { queryKeys } from '@/api/queryKeys'
import { EmptyState, ErrorBanner } from '@/components/StatusMessage'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { formatSessionAt, statusLabel } from '@/sessions/display'

const inputClassName =
  'h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50'

function planAccessMessage(error: unknown): string | null {
  if (!(error instanceof ApiError)) {
    return null
  }
  if (error.status === 404) {
    return error.message === 'Session not found' ? 'Session not found.' : 'Plan not found.'
  }
  if (error.status === 403) {
    return 'You cannot change this plan.'
  }
  return error.message
}

function writeFromForm(name: string, notes: string, startDate: string, lengthWeeks: string): PlanWrite | string {
  const trimmed = name.trim()
  if (!trimmed) {
    return 'Name is required.'
  }
  let weeks: number | null = null
  if (lengthWeeks.trim()) {
    const parsed = Number(lengthWeeks)
    if (!Number.isInteger(parsed) || parsed < 1) {
      return 'Length must be a whole number of weeks, at least 1.'
    }
    weeks = parsed
  }
  return {
    name: trimmed,
    notes: notes.trim() || null,
    start_date: startDate || null,
    length_weeks: weeks,
  }
}

function MemberList({
  title,
  sessions,
  onDetach,
  detachingId,
}: {
  title: string
  sessions: PlanSession[]
  onDetach: (sessionId: string) => void
  detachingId: string | null
}) {
  if (sessions.length === 0) {
    return null
  }
  return (
    <section className="flex flex-col gap-2">
      <h2 className="text-sm font-medium">{title}</h2>
      <ul className="flex flex-col gap-2">
        {sessions.map((session) => (
          <li key={session.id} className="flex items-center justify-between gap-3 rounded-lg border border-border px-3 py-2">
            <div className="flex min-w-0 flex-col gap-1">
              <Link className="truncate text-sm hover:underline" to={`/sessions/${session.id}`}>
                {session.name}
              </Link>
              <p className="text-xs text-muted-foreground">{formatSessionAt(session.session_at)}</p>
            </div>
            <div className="flex shrink-0 items-center gap-2">
              <Badge variant="outline">{statusLabel(session.status)}</Badge>
              <Button
                type="button"
                variant="outline"
                disabled={detachingId === session.id}
                onClick={() => onDetach(session.id)}
              >
                {detachingId === session.id ? 'Removing…' : 'Detach'}
              </Button>
            </div>
          </li>
        ))}
      </ul>
    </section>
  )
}

export default function PlanDetailPage() {
  const { planId = '' } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const planQuery = useQuery({
    queryKey: queryKeys.plan(planId),
    queryFn: () => getPlan(planId),
    enabled: planId.length > 0,
  })
  const sessionsQuery = useQuery({
    queryKey: queryKeys.sessions(),
    queryFn: () => listSessions(),
  })
  const plan = planQuery.data
  const [name, setName] = useState<string | null>(null)
  const [notes, setNotes] = useState<string | null>(null)
  const [startDate, setStartDate] = useState<string | null>(null)
  const [lengthWeeks, setLengthWeeks] = useState<string | null>(null)
  const [banner, setBanner] = useState<string | null>(null)
  const [sessionToAttach, setSessionToAttach] = useState('')
  const [confirmDelete, setConfirmDelete] = useState(false)

  const formName = name ?? plan?.name ?? ''
  const formNotes = notes ?? plan?.notes ?? ''
  const formStart = startDate ?? plan?.start_date ?? ''
  const formWeeks = lengthWeeks ?? (plan?.length_weeks == null ? '' : String(plan.length_weeks))

  async function refreshPlans() {
    await queryClient.invalidateQueries({ queryKey: queryKeys.plans })
    await queryClient.invalidateQueries({ queryKey: ['sessions'] })
    await queryClient.invalidateQueries({ queryKey: ['calendar'] })
  }

  const save = useMutation({
    mutationFn: (body: PlanWrite) => updatePlan(planId, body),
    onSuccess: async () => {
      setBanner(null)
      setName(null)
      setNotes(null)
      setStartDate(null)
      setLengthWeeks(null)
      await refreshPlans()
    },
  })
  const remove = useMutation({
    mutationFn: () => deletePlan(planId),
    onSuccess: async () => {
      await refreshPlans()
      navigate('/plans', { replace: true })
    },
  })
  const attach = useMutation({
    mutationFn: (sessionId: string) => attachPlanSession(planId, sessionId),
    onSuccess: async () => {
      setSessionToAttach('')
      await refreshPlans()
    },
  })
  const detach = useMutation({
    mutationFn: (sessionId: string) => detachPlanSession(planId, sessionId),
    onSuccess: refreshPlans,
  })

  function handleSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const body = writeFromForm(formName, formNotes, formStart, formWeeks)
    if (typeof body === 'string') {
      setBanner(body)
      return
    }
    setBanner(null)
    save.mutate(body)
  }

  const missing = planQuery.error instanceof ApiError && planQuery.error.status === 404
  const members = plan?.sessions ?? []
  const dated = members.filter((session) => session.session_at)
  const unscheduled = members.filter((session) => !session.session_at)
  const memberIds = new Set(members.map((session) => session.id))
  const attachable = (sessionsQuery.data?.items ?? []).filter((session) => !memberIds.has(session.id))
  const saveError = planAccessMessage(save.error) ?? (save.isError ? 'Could not save this plan.' : null)
  const deleteError = planAccessMessage(remove.error) ?? (remove.isError ? 'Could not delete this plan.' : null)
  const attachError = planAccessMessage(attach.error) ?? (attach.isError ? 'Could not attach that session.' : null)

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-col gap-6 p-6">
      <Link className="text-sm text-primary underline-offset-4 hover:underline" to="/plans">
        Back to plans
      </Link>
      <h1 className="text-2xl font-semibold">Plan</h1>
      {planQuery.isPending ? <p className="text-sm text-muted-foreground">Loading plan…</p> : null}
      {missing ? <p className="text-sm text-muted-foreground">Plan not found.</p> : null}
      {planQuery.isError && !missing ? (
        <ErrorBanner>
          {planAccessMessage(planQuery.error) ?? 'Could not load this plan.'}
        </ErrorBanner>
      ) : null}

      {plan ? (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Details</CardTitle>
              <CardDescription>Start date and length do not reorder sessions.</CardDescription>
            </CardHeader>
            <CardContent>
              <form className="grid gap-4 sm:grid-cols-2" onSubmit={handleSave}>
                <label className="flex flex-col gap-1.5 text-sm font-medium sm:col-span-2">
                  Name
                  <input className={inputClassName} value={formName} onChange={(event) => setName(event.target.value)} />
                </label>
                <label className="flex flex-col gap-1.5 text-sm font-medium">
                  Start date
                  <input
                    className={inputClassName}
                    type="date"
                    value={formStart}
                    onChange={(event) => setStartDate(event.target.value)}
                  />
                </label>
                <label className="flex flex-col gap-1.5 text-sm font-medium">
                  Length (weeks)
                  <input
                    className={inputClassName}
                    inputMode="numeric"
                    value={formWeeks}
                    onChange={(event) => setLengthWeeks(event.target.value)}
                  />
                </label>
                <label className="flex flex-col gap-1.5 text-sm font-medium sm:col-span-2">
                  Notes
                  <textarea
                    className="min-h-20 w-full rounded-lg border border-input bg-transparent px-2.5 py-2 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
                    value={formNotes}
                    onChange={(event) => setNotes(event.target.value)}
                  />
                </label>
                {banner || saveError ? (
                  <ErrorBanner className="sm:col-span-2">{banner || saveError}</ErrorBanner>
                ) : null}
                {save.isSuccess ? <p className="text-sm text-muted-foreground sm:col-span-2">Saved.</p> : null}
                <Button type="submit" disabled={save.isPending}>
                  {save.isPending ? 'Saving…' : 'Save plan'}
                </Button>
              </form>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Sessions</CardTitle>
              <CardDescription>
                Dated sessions follow session time, earliest first. Unscheduled sessions stay in their own section.
                You can attach only your own sessions. Attaching one that is already on another plan moves it here.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              {members.length === 0 ? (
                <EmptyState>No sessions on this plan yet.</EmptyState>
              ) : null}
              <MemberList
                title="Dated"
                sessions={dated}
                onDetach={(sessionId) => detach.mutate(sessionId)}
                detachingId={detach.isPending ? detach.variables : null}
              />
              <MemberList
                title="Unscheduled"
                sessions={unscheduled}
                onDetach={(sessionId) => detach.mutate(sessionId)}
                detachingId={detach.isPending ? detach.variables : null}
              />
              {detach.isError ? (
                <ErrorBanner>
                  {planAccessMessage(detach.error) ?? 'Could not detach that session.'}
                </ErrorBanner>
              ) : null}
              <div className="flex flex-wrap items-end gap-2">
                <label className="flex min-w-48 flex-1 flex-col gap-1.5 text-sm font-medium">
                  Attach a session
                  <select
                    className={inputClassName}
                    value={sessionToAttach}
                    onChange={(event) => setSessionToAttach(event.target.value)}
                  >
                    <option value="">Choose a session</option>
                    {attachable.map((session) => (
                      <option key={session.id} value={session.id}>
                        {session.name}
                        {session.session_at ? '' : ' (unscheduled)'}
                        {session.plan_id ? ' (moves from another plan)' : ''}
                      </option>
                    ))}
                  </select>
                </label>
                <Button
                  type="button"
                  variant="outline"
                  disabled={!sessionToAttach || attach.isPending}
                  onClick={() => attach.mutate(sessionToAttach)}
                >
                  {attach.isPending ? 'Attaching…' : 'Attach'}
                </Button>
              </div>
              {sessionsQuery.isError ? (
                <ErrorBanner>Could not load sessions to attach.</ErrorBanner>
              ) : null}
              {attachError ? <ErrorBanner>{attachError}</ErrorBanner> : null}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Delete</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col items-start gap-3">
              {confirmDelete ? (
                <>
                  <p className="text-sm">
                    Delete this plan? Sessions stay in your log and leave the plan.
                  </p>
                  {deleteError ? <ErrorBanner>{deleteError}</ErrorBanner> : null}
                  <div className="flex gap-2">
                    <Button
                      type="button"
                      variant="destructive"
                      disabled={remove.isPending}
                      onClick={() => remove.mutate()}
                    >
                      {remove.isPending ? 'Deleting…' : 'Delete plan'}
                    </Button>
                    <Button type="button" variant="outline" onClick={() => setConfirmDelete(false)}>
                      Cancel
                    </Button>
                  </div>
                </>
              ) : (
                <Button type="button" variant="destructive" onClick={() => setConfirmDelete(true)}>
                  Delete
                </Button>
              )}
            </CardContent>
          </Card>
        </>
      ) : null}
    </main>
  )
}
