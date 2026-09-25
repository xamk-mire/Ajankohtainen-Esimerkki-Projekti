import type { SessionItem } from '@/api/client'

const STATUS_LABELS: Record<string, string> = {
  planned: 'Planned',
  in_progress: 'In progress',
  completed: 'Completed',
}

export function statusLabel(status: string): string {
  return STATUS_LABELS[status] ?? status
}

export function formatSessionAt(value: string | null): string {
  if (!value) {
    return 'Unscheduled'
  }
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return 'Unscheduled'
  }
  return date.toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}

export function exerciseSummary(
  items: SessionItem[],
  names: ReadonlyMap<string, string>,
): string {
  if (items.length === 0) {
    return 'No exercises'
  }
  const labels = [...items]
    .sort((left, right) => left.sort_order - right.sort_order)
    .map((item) => names.get(item.activity_type_id) ?? 'Exercise')
  if (labels.length <= 3) {
    return labels.join(', ')
  }
  return `${labels.slice(0, 3).join(', ')} +${labels.length - 3}`
}

export function dayStartIso(date: string): string {
  return new Date(`${date}T00:00:00`).toISOString()
}

export function dayEndIso(date: string): string {
  return new Date(`${date}T23:59:59.999`).toISOString()
}
