import type { ActivityTypeSummary, ActivityUnitLink } from '@/api/client'

const inputClassName =
  'h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50'

type ActivityTypeSelectProps = {
  activities: ActivityTypeSummary[]
  value: string
  onChange: (activityId: string) => void
  allowEmpty?: boolean
  emptyLabel?: string
}

function unitSummary(links: ActivityUnitLink[]): string {
  const ordered = [...links].sort((left, right) => left.sort_order - right.sort_order)
  if (ordered.length === 0) {
    return 'No units'
  }
  const parts = ordered.map((link) => {
    const label = link.unit_type.unit_label
    return label ? `${link.unit_type.name} (${label})` : link.unit_type.name
  })
  const summary = parts.join(', ')
  if (ordered.every((link) => link.per_set)) {
    return `${summary} · per set`
  }
  return ordered
    .map((link, index) => (link.per_set ? `${parts[index]} · per set` : parts[index]))
    .join(', ')
}

function byName(left: ActivityTypeSummary, right: ActivityTypeSummary): number {
  return left.name.localeCompare(right.name)
}

function optionLabel(activity: ActivityTypeSummary): string {
  return `${activity.name} — ${unitSummary(activity.unit_links)}`
}

export default function ActivityTypeSelect({
  activities,
  value,
  onChange,
  allowEmpty = false,
  emptyLabel = 'Any',
}: ActivityTypeSelectProps) {
  const system = activities.filter((activity) => activity.is_system).sort(byName)
  const custom = activities.filter((activity) => !activity.is_system).sort(byName)
  const selected = activities.find((activity) => activity.id === value)
  const known = !value || Boolean(selected)

  return (
    <div className="flex flex-col gap-1.5">
      <select
        className={inputClassName}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        {allowEmpty ? <option value="">{emptyLabel}</option> : null}
        {!known ? <option value={value}>Unknown exercise</option> : null}
        {system.length > 0 ? (
          <optgroup label="Exercises">
            {system.map((activity) => (
              <option key={activity.id} value={activity.id}>
                {optionLabel(activity)}
              </option>
            ))}
          </optgroup>
        ) : null}
        {custom.length > 0 ? (
          <optgroup label="Your exercises">
            {custom.map((activity) => (
              <option key={activity.id} value={activity.id}>
                {optionLabel(activity)}
              </option>
            ))}
          </optgroup>
        ) : null}
      </select>
      {selected ? (
        <p className="text-xs font-normal text-muted-foreground">{unitSummary(selected.unit_links)}</p>
      ) : null}
    </div>
  )
}
