import type {
  ActivityTypeSummary,
  ActivityUnitLink,
  Session,
  SessionItem,
  SessionMeasurementWrite,
  SessionWrite,
} from '@/api/client'

export type UnitDraft = {
  unitTypeId: string
  planned: string
  actual: string
}

export type SetDraft = {
  units: UnitDraft[]
}

export type ItemDraft = {
  key: string
  activityTypeId: string
  notes: string
  once: UnitDraft[]
  sets: SetDraft[]
}

export type SessionDraft = {
  name: string
  sessionAt: string
  status: SessionWrite['status']
  notes: string
  intensity: string
  planId: string
  items: ItemDraft[]
}

function newKey(): string {
  return crypto.randomUUID()
}

function sortedLinks(activity: ActivityTypeSummary | undefined): ActivityUnitLink[] {
  return [...(activity?.unit_links ?? [])].sort((left, right) => left.sort_order - right.sort_order)
}

function blankUnits(links: ActivityUnitLink[]): UnitDraft[] {
  return links.map((link) => ({
    unitTypeId: link.unit_type_id,
    planned: '',
    actual: '',
  }))
}

function displayValue(value: string | null | undefined): string {
  if (!value) {
    return ''
  }
  const number = Number(value)
  return Number.isFinite(number) ? String(number) : value
}

export function emptySessionDraft(): SessionDraft {
  return {
    name: '',
    sessionAt: '',
    status: 'planned',
    notes: '',
    intensity: '',
    planId: '',
    items: [],
  }
}

export function itemFromActivity(activity: ActivityTypeSummary): ItemDraft {
  const links = sortedLinks(activity)
  const perSet = links.filter((link) => link.per_set)
  return {
    key: newKey(),
    activityTypeId: activity.id,
    notes: '',
    once: blankUnits(links.filter((link) => !link.per_set)),
    sets: perSet.length > 0 ? [{ units: blankUnits(perSet) }] : [],
  }
}

function unitsFor(
  links: ActivityUnitLink[],
  measurements: SessionItem['measurements'],
  setIndex: number | null,
): UnitDraft[] {
  const matched = new Set<string>()
  const fromLinks = links.map((link) => {
    const found = measurements.find(
      (measurement) =>
        measurement.unit_type_id === link.unit_type_id && measurement.set_index === setIndex,
    )
    if (found) {
      matched.add(found.id)
    }
    return {
      unitTypeId: link.unit_type_id,
      planned: displayValue(found?.planned_value),
      actual: displayValue(found?.actual_value),
    }
  })
  const extras = measurements
    .filter((measurement) => measurement.set_index === setIndex && !matched.has(measurement.id))
    .map((measurement) => ({
      unitTypeId: measurement.unit_type_id,
      planned: displayValue(measurement.planned_value),
      actual: displayValue(measurement.actual_value),
    }))
  return [...fromLinks, ...extras]
}

function itemFromSession(item: SessionItem, activities: ActivityTypeSummary[]): ItemDraft {
  const activity = activities.find((candidate) => candidate.id === item.activity_type_id)
  const links = sortedLinks(activity)
  const perSet = links.filter((link) => link.per_set)
  const onceLinks = links.filter((link) => !link.per_set)
  const setIndexes = [
    ...new Set(
      item.measurements
        .map((measurement) => measurement.set_index)
        .filter((setIndex): setIndex is number => setIndex !== null),
    ),
  ].sort((left, right) => left - right)
  const indexes = setIndexes.length > 0 ? setIndexes : perSet.length > 0 ? [1] : []
  return {
    key: item.id,
    activityTypeId: item.activity_type_id,
    notes: item.notes ?? '',
    once: unitsFor(onceLinks, item.measurements, null),
    sets: indexes.map((setIndex) => ({
      units: unitsFor(perSet, item.measurements, setIndex),
    })),
  }
}

export function draftFromSession(session: Session, activities: ActivityTypeSummary[]): SessionDraft {
  return {
    name: session.name,
    sessionAt: toDatetimeLocal(session.session_at),
    status:
      session.status === 'in_progress' || session.status === 'completed'
        ? session.status
        : 'planned',
    notes: session.notes ?? '',
    intensity: session.intensity === null ? '' : String(session.intensity),
    planId: session.plan_id ?? '',
    items: [...session.items]
      .sort((left, right) => left.sort_order - right.sort_order)
      .map((item) => itemFromSession(item, activities)),
  }
}

function toDatetimeLocal(value: string | null): string {
  if (!value) {
    return ''
  }
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return ''
  }
  const pad = (part: number) => String(part).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

function isDecimal(value: string): boolean {
  return /^\d+(\.\d+)?$/.test(value)
}

function measurementFromDraft(
  unit: UnitDraft,
  setIndex: number | null,
): SessionMeasurementWrite | null | 'invalid' {
  const planned = unit.planned.trim()
  const actual = unit.actual.trim()
  if (!planned && !actual) {
    return null
  }
  if ((planned && !isDecimal(planned)) || (actual && !isDecimal(actual))) {
    return 'invalid'
  }
  return {
    unit_type_id: unit.unitTypeId,
    planned_value: planned || null,
    actual_value: actual || null,
    set_index: setIndex,
  }
}

export function toSessionWrite(draft: SessionDraft): SessionWrite | string {
  const name = draft.name.trim()
  if (!name) {
    return 'Name is required.'
  }
  let intensity: number | null = null
  if (draft.intensity.trim()) {
    const parsed = Number(draft.intensity)
    if (!Number.isInteger(parsed) || parsed < 1 || parsed > 10) {
      return 'Intensity must be a whole number from 1 to 10.'
    }
    intensity = parsed
  }
  let sessionAt: string | null = null
  if (draft.sessionAt) {
    const parsed = new Date(draft.sessionAt)
    if (Number.isNaN(parsed.getTime())) {
      return 'Session time is invalid.'
    }
    sessionAt = parsed.toISOString()
  }

  const items: SessionWrite['items'] = []
  for (const [index, item] of draft.items.entries()) {
    if (!item.activityTypeId) {
      return 'Each exercise needs an activity.'
    }
    const measurements: SessionMeasurementWrite[] = []
    for (const unit of item.once) {
      const row = measurementFromDraft(unit, null)
      if (row === 'invalid') {
        return 'Measurement values must be numbers.'
      }
      if (row) {
        measurements.push(row)
      }
    }
    for (const [setPosition, set] of item.sets.entries()) {
      for (const unit of set.units) {
        const row = measurementFromDraft(unit, setPosition + 1)
        if (row === 'invalid') {
          return 'Measurement values must be numbers.'
        }
        if (row) {
          measurements.push(row)
        }
      }
    }
    items.push({
      activity_type_id: item.activityTypeId,
      sort_order: index,
      notes: item.notes.trim() || null,
      measurements,
    })
  }

  return {
    name,
    session_at: sessionAt,
    status: draft.status,
    notes: draft.notes.trim() || null,
    intensity,
    plan_id: draft.planId || null,
    items,
  }
}
