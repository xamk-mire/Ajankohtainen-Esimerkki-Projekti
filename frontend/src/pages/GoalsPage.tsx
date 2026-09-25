import { useMemo, useState, type FormEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  createGoal,
  listActivityTypes,
  listGoals,
  updateGoal,
  type ActivityTypeSummary,
  type Goal,
  type GoalWrite,
  type UnitTypeSummary,
} from '@/api/client'
import { failureMessage } from '@/api/messages'
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

const inputClassName =
  'h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50'

function unitsFromActivities(activities: ActivityTypeSummary[]): UnitTypeSummary[] {
  const byId = new Map<string, UnitTypeSummary>()
  for (const activity of activities) {
    for (const link of activity.unit_links) {
      byId.set(link.unit_type.id, link.unit_type)
    }
  }
  return [...byId.values()].sort((left, right) => left.name.localeCompare(right.name))
}

function unitLabel(unit: UnitTypeSummary | undefined): string {
  if (!unit) {
    return 'Unknown unit'
  }
  return unit.unit_label ? `${unit.name} (${unit.unit_label})` : unit.name
}

function targetLabel(value: string | number): string {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? String(parsed) : String(value)
}

function writeFromForm(
  unitTypeId: string,
  activityTypeId: string,
  target: string,
  period: string,
): GoalWrite | string {
  if (!unitTypeId) {
    return 'Choose a unit.'
  }
  const parsed = Number(target)
  if (!target.trim() || !Number.isFinite(parsed) || parsed <= 0) {
    return 'Target must be a number greater than 0.'
  }
  if (period !== 'week' && period !== 'month') {
    return 'Choose a week or a month.'
  }
  return {
    unit_type_id: unitTypeId,
    activity_type_id: activityTypeId || null,
    target_value: parsed,
    period,
  }
}

export default function GoalsPage() {
  const queryClient = useQueryClient()
  const [activeFilter, setActiveFilter] = useState<'all' | 'true' | 'false'>('all')
  const active = activeFilter === 'all' ? null : activeFilter === 'true'
  const [unitTypeId, setUnitTypeId] = useState('')
  const [activityTypeId, setActivityTypeId] = useState('')
  const [target, setTarget] = useState('')
  const [period, setPeriod] = useState<'week' | 'month'>('week')
  const [banner, setBanner] = useState<string | null>(null)

  const activitiesQuery = useQuery({
    queryKey: queryKeys.activityTypes,
    queryFn: listActivityTypes,
  })
  const goalsQuery = useQuery({
    queryKey: queryKeys.goals(active),
    queryFn: () => listGoals(active),
  })
  const units = useMemo(
    () => unitsFromActivities(activitiesQuery.data ?? []),
    [activitiesQuery.data],
  )
  const unitById = useMemo(() => new Map(units.map((unit) => [unit.id, unit])), [units])
  const activityById = useMemo(
    () => new Map((activitiesQuery.data ?? []).map((activity) => [activity.id, activity.name])),
    [activitiesQuery.data],
  )

  const create = useMutation({
    mutationFn: createGoal,
    onSuccess: async () => {
      setBanner(null)
      setTarget('')
      await queryClient.invalidateQueries({ queryKey: ['goals'] })
    },
  })
  const toggle = useMutation({
    mutationFn: (goal: Goal) => updateGoal(goal.id, { active: !goal.active }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['goals'] })
    },
  })

  function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const body = writeFromForm(unitTypeId, activityTypeId, target, period)
    if (typeof body === 'string') {
      setBanner(body)
      return
    }
    setBanner(null)
    create.mutate(body)
  }

  const goals = goalsQuery.data ?? []
  const createError = create.isError
    ? failureMessage(create.error, 'Could not create the period goal.', 'You cannot change this period goal.')
    : null
  const toggleError = toggle.isError
    ? failureMessage(toggle.error, 'Could not update the period goal.', 'You cannot change this period goal.')
    : null

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-col gap-6 p-6">
      <div>
        <h1 className="text-2xl font-semibold">Period goals</h1>
        <p className="text-sm text-muted-foreground">
          A period goal is a week or month target for a unit. It is not a planned set on a session.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>New period goal</CardTitle>
          <CardDescription>Pick a unit from the exercise catalog. An exercise is optional.</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="grid gap-4 sm:grid-cols-2" onSubmit={handleCreate}>
            <label className="flex flex-col gap-1.5 text-sm font-medium">
              Unit
              <select
                className={inputClassName}
                value={unitTypeId}
                onChange={(event) => setUnitTypeId(event.target.value)}
              >
                <option value="">Choose a unit</option>
                {units.map((unit) => (
                  <option key={unit.id} value={unit.id}>
                    {unitLabel(unit)}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1.5 text-sm font-medium">
              Period
              <select
                className={inputClassName}
                value={period}
                onChange={(event) => setPeriod(event.target.value === 'month' ? 'month' : 'week')}
              >
                <option value="week">Week</option>
                <option value="month">Month</option>
              </select>
            </label>
            <label className="flex flex-col gap-1.5 text-sm font-medium">
              Target
              <input
                className={inputClassName}
                inputMode="decimal"
                value={target}
                onChange={(event) => setTarget(event.target.value)}
              />
            </label>
            <label className="flex flex-col gap-1.5 text-sm font-medium">
              Exercise
              <select
                className={inputClassName}
                value={activityTypeId}
                onChange={(event) => setActivityTypeId(event.target.value)}
              >
                <option value="">Any exercise</option>
                {(activitiesQuery.data ?? []).map((activity) => (
                  <option key={activity.id} value={activity.id}>
                    {activity.name}
                  </option>
                ))}
              </select>
            </label>
            {banner || createError ? (
              <ErrorBanner className="sm:col-span-2">{banner || createError}</ErrorBanner>
            ) : null}
            <Button type="submit" disabled={create.isPending || units.length === 0}>
              {create.isPending ? 'Creating…' : 'Create period goal'}
            </Button>
          </form>
        </CardContent>
      </Card>

      <label className="flex max-w-xs flex-col gap-1.5 text-sm font-medium">
        Show
        <select
          className={inputClassName}
          value={activeFilter}
          onChange={(event) => {
            const next = event.target.value
            setActiveFilter(next === 'true' || next === 'false' ? next : 'all')
          }}
        >
          <option value="all">All period goals</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>
      </label>

      {activitiesQuery.isError ? (
        <ErrorBanner>
          {failureMessage(
            activitiesQuery.error,
            'Could not load units.',
            'You cannot view these units.',
          )}
        </ErrorBanner>
      ) : null}
      {activitiesQuery.isSuccess && units.length === 0 ? (
        <EmptyState>No units in the catalog yet. Seed exercises before creating a period goal.</EmptyState>
      ) : null}
      {goalsQuery.isPending ? <p className="text-sm text-muted-foreground">Loading period goals…</p> : null}
      {goalsQuery.isError ? (
        <ErrorBanner>
          {failureMessage(goalsQuery.error, 'Could not load period goals.', 'You cannot view these period goals.')}
        </ErrorBanner>
      ) : null}
      {toggleError ? <ErrorBanner>{toggleError}</ErrorBanner> : null}
      {goalsQuery.isSuccess && goals.length === 0 ? (
        <EmptyState>
          {activeFilter === 'all' ? 'No period goals yet.' : 'No period goals match this filter.'}
        </EmptyState>
      ) : null}

      <ul className="flex flex-col gap-3">
        {goals.map((goal) => (
          <li key={goal.id}>
            <Card>
              <CardHeader className="flex flex-row items-start justify-between gap-3">
                <div className="flex flex-col gap-1">
                  <CardTitle>
                    {targetLabel(goal.target_value)} {unitLabel(unitById.get(goal.unit_type_id))}
                  </CardTitle>
                  <CardDescription>
                    {goal.period === 'month' ? 'Each month' : 'Each week'}
                    {goal.activity_type_id
                      ? ` · ${activityById.get(goal.activity_type_id) ?? 'Unknown exercise'}`
                      : ''}
                  </CardDescription>
                </div>
                <Badge variant={goal.active ? 'default' : 'outline'}>
                  {goal.active ? 'Active' : 'Inactive'}
                </Badge>
              </CardHeader>
              <CardContent>
                <Button
                  type="button"
                  variant="outline"
                  disabled={toggle.isPending}
                  onClick={() => toggle.mutate(goal)}
                >
                  {goal.active ? 'Deactivate' : 'Activate'}
                </Button>
              </CardContent>
            </Card>
          </li>
        ))}
      </ul>
    </main>
  )
}
