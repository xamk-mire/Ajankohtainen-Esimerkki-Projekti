export type CalendarView = 'month' | 'week'

function startOfDay(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate())
}

export function endOfDay(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate(), 23, 59, 59, 999)
}

export function addDays(date: Date, days: number): Date {
  const next = new Date(date)
  next.setDate(next.getDate() + days)
  return next
}

export function startOfWeek(date: Date): Date {
  const next = startOfDay(date)
  const weekday = next.getDay()
  const mondayOffset = weekday === 0 ? -6 : 1 - weekday
  return addDays(next, mondayOffset)
}

export function dayKey(date: Date): string {
  const pad = (part: number) => String(part).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
}

export function dayKeyFromIso(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return ''
  }
  return dayKey(date)
}

export function visibleDays(cursor: Date, view: CalendarView): Date[] {
  if (view === 'week') {
    const start = startOfWeek(cursor)
    return Array.from({ length: 7 }, (_, index) => addDays(start, index))
  }
  const firstOfMonth = new Date(cursor.getFullYear(), cursor.getMonth(), 1)
  const start = startOfWeek(firstOfMonth)
  return Array.from({ length: 42 }, (_, index) => addDays(start, index))
}

export function rangeIso(days: Date[]): { from: string; to: string } {
  const first = days[0] ?? new Date()
  const last = days[days.length - 1] ?? first
  return {
    from: startOfDay(first).toISOString(),
    to: endOfDay(last).toISOString(),
  }
}

export function shiftCursor(cursor: Date, view: CalendarView, direction: -1 | 1): Date {
  if (view === 'week') {
    return addDays(cursor, direction * 7)
  }
  return new Date(cursor.getFullYear(), cursor.getMonth() + direction, 1)
}

export function rangeTitle(cursor: Date, days: Date[], view: CalendarView): string {
  if (view === 'month') {
    return cursor.toLocaleDateString(undefined, { month: 'long', year: 'numeric' })
  }
  const first = days[0] ?? cursor
  const last = days[days.length - 1] ?? first
  const sameMonth = first.getMonth() === last.getMonth()
  const startLabel = first.toLocaleDateString(undefined, {
    day: 'numeric',
    month: sameMonth ? undefined : 'short',
  })
  const endLabel = last.toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' })
  return `${startLabel} – ${endLabel}`
}

export function sessionAtOnDate(sourceIso: string, date: string): string {
  const source = new Date(sourceIso)
  const [year, month, day] = date.split('-').map(Number)
  const next = Number.isNaN(source.getTime()) ? new Date() : new Date(source)
  next.setFullYear(year ?? next.getFullYear(), (month ?? next.getMonth() + 1) - 1, day ?? next.getDate())
  return next.toISOString()
}
