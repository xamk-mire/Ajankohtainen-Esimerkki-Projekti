import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createPlan, listPlans, type PlanWrite } from '@/api/client'
import { failureMessage } from '@/api/messages'
import { queryKeys } from '@/api/queryKeys'
import { EmptyState, ErrorBanner } from '@/components/StatusMessage'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

const inputClassName =
  'h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50'

function planMeta(startDate: string | null, lengthWeeks: number | null): string | null {
  const parts: string[] = []
  if (startDate) {
    parts.push(`Starts ${startDate}`)
  }
  if (lengthWeeks) {
    parts.push(`${lengthWeeks} weeks`)
  }
  return parts.length > 0 ? parts.join(' · ') : null
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

export default function PlansPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const plansQuery = useQuery({
    queryKey: queryKeys.plans,
    queryFn: listPlans,
  })
  const [name, setName] = useState('')
  const [notes, setNotes] = useState('')
  const [startDate, setStartDate] = useState('')
  const [lengthWeeks, setLengthWeeks] = useState('')
  const [banner, setBanner] = useState<string | null>(null)

  const create = useMutation({
    mutationFn: createPlan,
    onSuccess: async (plan) => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.plans })
      navigate(`/plans/${plan.id}`)
    },
  })

  function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const body = writeFromForm(name, notes, startDate, lengthWeeks)
    if (typeof body === 'string') {
      setBanner(body)
      return
    }
    setBanner(null)
    create.mutate(body)
  }

  const plans = plansQuery.data ?? []
  const createError = create.isError
    ? failureMessage(create.error, 'Could not create the plan.', 'You cannot change this plan.')
    : null

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-col gap-6 p-6">
      <div>
        <h1 className="text-2xl font-semibold">Plans</h1>
        <p className="text-sm text-muted-foreground">Your plans only. Sessions join a plan by date.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>New plan</CardTitle>
          <CardDescription>Start date and length are labels only. They do not place sessions.</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="grid gap-4 sm:grid-cols-2" onSubmit={handleCreate}>
            <label className="flex flex-col gap-1.5 text-sm font-medium sm:col-span-2">
              Name
              <input className={inputClassName} value={name} onChange={(event) => setName(event.target.value)} />
            </label>
            <label className="flex flex-col gap-1.5 text-sm font-medium">
              Start date
              <input
                className={inputClassName}
                type="date"
                value={startDate}
                onChange={(event) => setStartDate(event.target.value)}
              />
            </label>
            <label className="flex flex-col gap-1.5 text-sm font-medium">
              Length (weeks)
              <input
                className={inputClassName}
                inputMode="numeric"
                value={lengthWeeks}
                onChange={(event) => setLengthWeeks(event.target.value)}
              />
            </label>
            <label className="flex flex-col gap-1.5 text-sm font-medium sm:col-span-2">
              Notes
              <textarea
                className="min-h-20 w-full rounded-lg border border-input bg-transparent px-2.5 py-2 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
                value={notes}
                onChange={(event) => setNotes(event.target.value)}
              />
            </label>
            {banner || createError ? (
              <ErrorBanner className="sm:col-span-2">{banner || createError}</ErrorBanner>
            ) : null}
            <Button type="submit" disabled={create.isPending}>
              {create.isPending ? 'Creating…' : 'Create plan'}
            </Button>
          </form>
        </CardContent>
      </Card>

      {plansQuery.isPending ? <p className="text-sm text-muted-foreground">Loading plans…</p> : null}
      {plansQuery.isError ? (
        <ErrorBanner>
          {failureMessage(plansQuery.error, 'Could not load plans.', 'You cannot view these plans.')}
        </ErrorBanner>
      ) : null}
      {plansQuery.isSuccess && plans.length === 0 ? (
        <EmptyState>No plans yet. Use the form above to create one.</EmptyState>
      ) : null}

      <ul className="flex flex-col gap-3">
        {plans.map((plan) => {
          const meta = planMeta(plan.start_date, plan.length_weeks)
          return (
            <li key={plan.id}>
              <Card>
                <CardHeader>
                  <CardTitle>
                    <Link className="hover:underline" to={`/plans/${plan.id}`}>
                      {plan.name}
                    </Link>
                  </CardTitle>
                  {meta ? <CardDescription>{meta}</CardDescription> : null}
                </CardHeader>
                {plan.notes ? (
                  <CardContent>
                    <p className="text-sm text-muted-foreground">{plan.notes}</p>
                  </CardContent>
                ) : null}
              </Card>
            </li>
          )
        })}
      </ul>
    </main>
  )
}
