import { useState, type FormEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  ApiError,
  createSession,
  listActivityTypes,
  listPlans,
  getSession,
  updateSession,
  type ActivityTypeSummary,
  type PlanSummary,
  type SessionWrite,
} from '@/api/client'
import { queryKeys } from '@/api/queryKeys'
import MeasurementEditor from '@/components/MeasurementEditor'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  draftFromSession,
  emptySessionDraft,
  itemFromActivity,
  toSessionWrite,
  type ItemDraft,
  type SessionDraft,
} from '@/sessions/draft'

const inputClassName =
  'h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50'

type DesignerProps = {
  isNew: boolean
  sessionId?: string
  initial: SessionDraft
  activities: ActivityTypeSummary[]
  plans: PlanSummary[]
}

function SessionDesigner({ isNew, sessionId, initial, activities, plans }: DesignerProps) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [draft, setDraft] = useState(initial)
  const [banner, setBanner] = useState<string | null>(null)
  const [activityToAdd, setActivityToAdd] = useState(activities[0]?.id ?? '')

  const save = useMutation({
    mutationFn: (body: SessionWrite) =>
      isNew || !sessionId ? createSession(body) : updateSession(sessionId, body),
    onSuccess: async (saved) => {
      await queryClient.invalidateQueries({ queryKey: ['sessions'] })
      await queryClient.invalidateQueries({ queryKey: queryKeys.plans })
      await queryClient.invalidateQueries({ queryKey: ['calendar'] })
      if (isNew) {
        navigate(`/sessions/${saved.id}`, { replace: true })
      } else {
        setBanner(null)
      }
    },
  })

  function updateItem(key: string, patch: Partial<ItemDraft>) {
    setDraft((current) => ({
      ...current,
      items: current.items.map((item) => (item.key === key ? { ...item, ...patch } : item)),
    }))
  }

  function moveItem(index: number, direction: -1 | 1) {
    setDraft((current) => {
      const next = [...current.items]
      const target = index + direction
      const item = next[index]
      const swap = next[target]
      if (!item || !swap) {
        return current
      }
      next[index] = swap
      next[target] = item
      return { ...current, items: next }
    })
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const body = toSessionWrite(draft)
    if (typeof body === 'string') {
      setBanner(body)
      return
    }
    setBanner(null)
    save.mutate(body)
  }

  const saveError =
    save.error instanceof ApiError
      ? save.error.message
      : save.isError
        ? 'Could not save this session.'
        : null

  return (
    <form className="flex flex-col gap-6" onSubmit={handleSubmit}>
      <Card>
        <CardHeader>
          <CardTitle>Session</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <label className="flex flex-col gap-1.5 text-sm font-medium sm:col-span-2">
            Name
            <input
              className={inputClassName}
              value={draft.name}
              onChange={(event) => setDraft((current) => ({ ...current, name: event.target.value }))}
            />
          </label>
          <label className="flex flex-col gap-1.5 text-sm font-medium">
            When
            <input
              className={inputClassName}
              type="datetime-local"
              value={draft.sessionAt}
              onChange={(event) =>
                setDraft((current) => ({ ...current, sessionAt: event.target.value }))
              }
            />
          </label>
          <label className="flex flex-col gap-1.5 text-sm font-medium">
            Status
            <select
              className={inputClassName}
              value={draft.status}
              onChange={(event) =>
                setDraft((current) => ({
                  ...current,
                  status: event.target.value as SessionDraft['status'],
                }))
              }
            >
              <option value="planned">Planned</option>
              <option value="in_progress">In progress</option>
              <option value="completed">Completed</option>
            </select>
          </label>
          <label className="flex flex-col gap-1.5 text-sm font-medium">
            Plan
            <select
              className={inputClassName}
              value={draft.planId}
              onChange={(event) =>
                setDraft((current) => ({ ...current, planId: event.target.value }))
              }
            >
              <option value="">None</option>
              {plans.map((plan) => (
                <option key={plan.id} value={plan.id}>
                  {plan.name}
                </option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1.5 text-sm font-medium">
            Intensity (1–10)
            <input
              className={inputClassName}
              inputMode="numeric"
              value={draft.intensity}
              onChange={(event) =>
                setDraft((current) => ({ ...current, intensity: event.target.value }))
              }
            />
          </label>
          <label className="flex flex-col gap-1.5 text-sm font-medium sm:col-span-2">
            Notes
            <textarea
              className="min-h-20 w-full rounded-lg border border-input bg-transparent px-2.5 py-2 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
              value={draft.notes}
              onChange={(event) =>
                setDraft((current) => ({ ...current, notes: event.target.value }))
              }
            />
          </label>
          <p className="text-xs text-muted-foreground sm:col-span-2">
            Leave the time empty to keep this session unscheduled.
          </p>
        </CardContent>
      </Card>

      {draft.items.map((item, index) => {
        const activity = activities.find((candidate) => candidate.id === item.activityTypeId)
        return (
          <Card key={item.key}>
            <CardHeader className="flex flex-row items-center justify-between gap-3">
              <CardTitle>Exercise {index + 1}</CardTitle>
              <div className="flex gap-3 text-sm">
                <button
                  type="button"
                  className="text-muted-foreground underline-offset-4 hover:underline disabled:opacity-40"
                  disabled={index === 0}
                  onClick={() => moveItem(index, -1)}
                >
                  Up
                </button>
                <button
                  type="button"
                  className="text-muted-foreground underline-offset-4 hover:underline disabled:opacity-40"
                  disabled={index === draft.items.length - 1}
                  onClick={() => moveItem(index, 1)}
                >
                  Down
                </button>
                <button
                  type="button"
                  className="text-destructive underline-offset-4 hover:underline"
                  onClick={() =>
                    setDraft((current) => ({
                      ...current,
                      items: current.items.filter((candidate) => candidate.key !== item.key),
                    }))
                  }
                >
                  Remove
                </button>
              </div>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <label className="flex flex-col gap-1.5 text-sm font-medium">
                Activity
                <select
                  className={inputClassName}
                  value={item.activityTypeId}
                  onChange={(event) => {
                    const next = activities.find((candidate) => candidate.id === event.target.value)
                    if (!next) {
                      return
                    }
                    const rebuilt = itemFromActivity(next)
                    updateItem(item.key, {
                      activityTypeId: rebuilt.activityTypeId,
                      once: rebuilt.once,
                      sets: rebuilt.sets,
                    })
                  }}
                >
                  {activities.map((candidate) => (
                    <option key={candidate.id} value={candidate.id}>
                      {candidate.name}
                    </option>
                  ))}
                </select>
              </label>
              <MeasurementEditor
                activity={activity}
                once={item.once}
                sets={item.sets}
                onOnceChange={(once) => updateItem(item.key, { once })}
                onSetsChange={(sets) => updateItem(item.key, { sets })}
              />
              <label className="flex flex-col gap-1.5 text-sm font-medium">
                Exercise notes
                <input
                  className={inputClassName}
                  value={item.notes}
                  onChange={(event) => updateItem(item.key, { notes: event.target.value })}
                />
              </label>
            </CardContent>
          </Card>
        )
      })}

      <div className="flex flex-wrap items-end gap-2">
        <label className="flex min-w-48 flex-1 flex-col gap-1.5 text-sm font-medium">
          Add exercise
          <select
            className={inputClassName}
            value={activityToAdd}
            onChange={(event) => setActivityToAdd(event.target.value)}
          >
            {activities.map((activity) => (
              <option key={activity.id} value={activity.id}>
                {activity.name}
              </option>
            ))}
          </select>
        </label>
        <Button
          type="button"
          variant="outline"
          disabled={!activityToAdd}
          onClick={() => {
            const activity = activities.find((candidate) => candidate.id === activityToAdd)
            if (!activity) {
              return
            }
            setDraft((current) => ({
              ...current,
              items: [...current.items, itemFromActivity(activity)],
            }))
          }}
        >
          Add
        </Button>
      </div>

      {banner || saveError ? (
        <p className="rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive" role="alert">
          {banner || saveError}
        </p>
      ) : null}
      {save.isSuccess && !isNew ? (
        <p className="text-sm text-muted-foreground">Saved.</p>
      ) : null}
      <Button type="submit" disabled={save.isPending}>
        {save.isPending ? 'Saving…' : 'Save session'}
      </Button>
    </form>
  )
}

export default function SessionFormPage() {
  const { sessionId } = useParams()
  const isNew = !sessionId
  const activitiesQuery = useQuery({
    queryKey: queryKeys.activityTypes,
    queryFn: listActivityTypes,
  })
  const plansQuery = useQuery({
    queryKey: queryKeys.plans,
    queryFn: listPlans,
  })
  const sessionQuery = useQuery({
    queryKey: queryKeys.session(sessionId ?? 'new'),
    queryFn: () => getSession(sessionId ?? ''),
    enabled: !isNew,
  })

  const missing = sessionQuery.error instanceof ApiError && sessionQuery.error.status === 404
  const activities = activitiesQuery.data ?? []
  const ready =
    activitiesQuery.isSuccess &&
    !plansQuery.isPending &&
    (isNew || sessionQuery.isSuccess)

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-col gap-6 p-6">
      <Link className="text-sm text-primary underline-offset-4 hover:underline" to="/sessions">
        Back to sessions
      </Link>
      <h1 className="text-2xl font-semibold">{isNew ? 'New session' : 'Edit session'}</h1>
      {!ready && !missing && !activitiesQuery.isError && !sessionQuery.isError ? (
        <p className="text-sm text-muted-foreground">Loading session…</p>
      ) : null}
      {activitiesQuery.isError ? (
        <p className="text-sm text-destructive" role="alert">
          Could not load exercises.
        </p>
      ) : null}
      {missing ? <p className="text-sm text-muted-foreground">Session not found.</p> : null}
      {sessionQuery.isError && !missing ? (
        <p className="text-sm text-destructive" role="alert">
          Could not load this session.
        </p>
      ) : null}
      {ready ? (
        <SessionDesigner
          key={isNew ? 'new' : sessionQuery.data?.id}
          isNew={isNew}
          sessionId={sessionId}
          initial={
            sessionQuery.data
              ? draftFromSession(sessionQuery.data, activities)
              : emptySessionDraft()
          }
          activities={activities}
          plans={plansQuery.data ?? []}
        />
      ) : null}
    </main>
  )
}
