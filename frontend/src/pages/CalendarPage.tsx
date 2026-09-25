import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  ApiError,
  cloneSession,
  listCalendar,
  listPlans,
  type CalendarSession,
} from '@/api/client'
import { queryKeys } from '@/api/queryKeys'
import {
  dayKey,
  dayKeyFromIso,
  rangeIso,
  rangeTitle,
  sessionAtOnDate,
  shiftCursor,
  visibleDays,
  type CalendarView,
} from '@/calendar/range'
import { Button } from '@/components/ui/button'
import { statusLabel } from '@/sessions/display'

const inputClassName =
  'h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50'

const WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

function statusClass(status: string): string {
  if (status === 'completed') {
    return 'bg-muted text-muted-foreground'
  }
  if (status === 'in_progress') {
    return 'bg-primary/15 text-foreground'
  }
  return 'border border-border bg-background text-foreground'
}

function cloneMessage(error: unknown): string {
  if (error instanceof ApiError && error.status === 404) {
    return 'Session not found.'
  }
  if (error instanceof ApiError && error.status === 403) {
    return 'You cannot change this session.'
  }
  if (error instanceof ApiError) {
    return error.message
  }
  return 'Could not clone this session.'
}

export default function CalendarPage() {
  const queryClient = useQueryClient()
  const [cursor, setCursor] = useState(() => new Date())
  const [view, setView] = useState<CalendarView>('month')
  const [planId, setPlanId] = useState('')
  const [cloneTarget, setCloneTarget] = useState<CalendarSession | null>(null)
  const [cloneDate, setCloneDate] = useState('')
  const [cloneName, setCloneName] = useState('')
  const [cloneBanner, setCloneBanner] = useState<string | null>(null)
  const [cloned, setCloned] = useState<{ id: string; name: string } | null>(null)

  const days = useMemo(() => visibleDays(cursor, view), [cursor, view])
  const range = useMemo(() => rangeIso(days), [days])
  const todayKey = dayKey(new Date())
  const plansQuery = useQuery({
    queryKey: queryKeys.plans,
    queryFn: listPlans,
  })
  const calendarQuery = useQuery({
    queryKey: queryKeys.calendar(range.from, range.to, planId || null),
    queryFn: () => listCalendar(range.from, range.to, planId || null),
  })

  const byDay = useMemo(() => {
    const grouped = new Map<string, CalendarSession[]>()
    for (const session of calendarQuery.data ?? []) {
      const key = dayKeyFromIso(session.session_at)
      const current = grouped.get(key) ?? []
      current.push(session)
      grouped.set(key, current)
    }
    return grouped
  }, [calendarQuery.data])

  const clone = useMutation({
    mutationFn: () => {
      if (!cloneTarget || !cloneDate) {
        throw new Error('Choose a date')
      }
      return cloneSession(cloneTarget.id, {
        ...(cloneName.trim() ? { name: cloneName.trim() } : {}),
        session_at: sessionAtOnDate(cloneTarget.session_at, cloneDate),
      })
    },
    onSuccess: async (saved) => {
      await queryClient.invalidateQueries({ queryKey: ['calendar'] })
      await queryClient.invalidateQueries({ queryKey: ['sessions'] })
      await queryClient.invalidateQueries({ queryKey: queryKeys.plans })
      if (saved.session_at) {
        setCursor(new Date(saved.session_at))
      }
      setCloned({ id: saved.id, name: saved.name })
      setCloneTarget(null)
      setCloneBanner(null)
    },
  })

  function openClone(session: CalendarSession) {
    setCloneTarget(session)
    setCloneName(session.name)
    setCloneDate(dayKeyFromIso(session.session_at))
    setCloneBanner(null)
    setCloned(null)
  }

  function submitClone() {
    if (!cloneDate) {
      setCloneBanner('Choose a date.')
      return
    }
    setCloneBanner(null)
    clone.mutate()
  }

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-col gap-4 p-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Calendar</h1>
          <p className="text-sm text-muted-foreground">Dated sessions for your account. Unscheduled sessions stay off the grid.</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Button type="button" variant={view === 'month' ? 'default' : 'outline'} onClick={() => setView('month')}>
            Month
          </Button>
          <Button type="button" variant={view === 'week' ? 'default' : 'outline'} onClick={() => setView('week')}>
            Week
          </Button>
        </div>
      </div>

      <div className="flex flex-wrap items-end justify-between gap-3">
        <div className="flex items-center gap-2">
          <Button type="button" variant="outline" onClick={() => setCursor((current) => shiftCursor(current, view, -1))}>
            Previous
          </Button>
          <Button type="button" variant="outline" onClick={() => setCursor(new Date())}>
            Today
          </Button>
          <Button type="button" variant="outline" onClick={() => setCursor((current) => shiftCursor(current, view, 1))}>
            Next
          </Button>
          <p className="text-sm font-medium">{rangeTitle(cursor, days, view)}</p>
        </div>
        <label className="flex min-w-48 flex-col gap-1.5 text-sm font-medium">
          Plan
          <select className={inputClassName} value={planId} onChange={(event) => setPlanId(event.target.value)}>
            <option value="">All plans</option>
            {(plansQuery.data ?? []).map((plan) => (
              <option key={plan.id} value={plan.id}>
                {plan.name}
              </option>
            ))}
          </select>
        </label>
      </div>

      {calendarQuery.isPending ? <p className="text-sm text-muted-foreground">Loading calendar…</p> : null}
      {calendarQuery.isError ? (
        <p className="text-sm text-destructive" role="alert">
          Could not load the calendar.
        </p>
      ) : null}

      <div className="grid grid-cols-7 gap-1 text-center text-xs text-muted-foreground">
        {WEEKDAYS.map((label) => (
          <div key={label}>{label}</div>
        ))}
      </div>
      <div className={`grid grid-cols-7 gap-1 ${view === 'week' ? 'min-h-80' : ''}`}>
        {days.map((day) => {
          const key = dayKey(day)
          const inMonth = day.getMonth() === cursor.getMonth()
          const sessions = byDay.get(key) ?? []
          return (
            <section
              key={key}
              className={`flex min-h-24 flex-col gap-1 rounded-lg border border-border p-1.5 ${
                view === 'month' && !inMonth ? 'bg-muted/40 text-muted-foreground' : 'bg-background'
              } ${key === todayKey ? 'ring-1 ring-primary' : ''}`}
            >
              <p className="text-xs font-medium">{day.getDate()}</p>
              <ul className={`flex flex-col gap-1 ${view === 'month' ? 'max-h-28 overflow-auto' : ''}`}>
                {sessions.map((session) => (
                  <li key={session.id} className={`rounded-md px-1.5 py-1 text-left text-xs ${statusClass(session.status)}`}>
                    <Link className="block truncate font-medium hover:underline" to={`/sessions/${session.id}`}>
                      {session.name}
                    </Link>
                    <div className="mt-0.5 flex items-center justify-between gap-1">
                      <span>{statusLabel(session.status)}</span>
                      <button type="button" className="underline-offset-2 hover:underline" onClick={() => openClone(session)}>
                        Clone
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            </section>
          )
        })}
      </div>

      {cloneTarget ? (
        <section className="rounded-lg border border-border p-4">
          <h2 className="text-sm font-medium">Clone {cloneTarget.name}</h2>
          <p className="mt-1 text-xs text-muted-foreground">
            Planned values are kept and actuals are cleared. The copy does not stay on the original plan.
          </p>
          <div className="mt-3 grid gap-3 sm:grid-cols-2">
            <label className="flex flex-col gap-1.5 text-sm font-medium">
              Copy name
              <input className={inputClassName} value={cloneName} onChange={(event) => setCloneName(event.target.value)} />
            </label>
            <label className="flex flex-col gap-1.5 text-sm font-medium">
              Date
              <input
                className={inputClassName}
                type="date"
                value={cloneDate}
                onChange={(event) => setCloneDate(event.target.value)}
              />
            </label>
          </div>
          {cloneBanner || clone.isError ? (
            <p className="mt-3 text-sm text-destructive" role="alert">
              {cloneBanner || cloneMessage(clone.error)}
            </p>
          ) : null}
          <div className="mt-3 flex gap-2">
            <Button type="button" disabled={clone.isPending} onClick={submitClone}>
              {clone.isPending ? 'Cloning…' : 'Clone onto date'}
            </Button>
            <Button type="button" variant="outline" onClick={() => setCloneTarget(null)}>
              Cancel
            </Button>
          </div>
        </section>
      ) : null}

      {cloned ? (
        <p className="text-sm text-muted-foreground">
          Cloned.{' '}
          <Link className="text-primary underline-offset-4 hover:underline" to={`/sessions/${cloned.id}`}>
            Open {cloned.name}
          </Link>
          . Editing the original will not change this copy.
        </p>
      ) : null}
    </main>
  )
}
