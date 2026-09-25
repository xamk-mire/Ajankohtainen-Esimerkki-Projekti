import type { ActivityTypeSummary, ActivityUnitLink } from '@/api/client'
import type { SetDraft, UnitDraft } from '@/sessions/draft'

const inputClassName =
  'h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50'

type MeasurementEditorProps = {
  activity: ActivityTypeSummary | undefined
  once: UnitDraft[]
  sets: SetDraft[]
  onOnceChange: (once: UnitDraft[]) => void
  onSetsChange: (sets: SetDraft[]) => void
}

function linkFor(
  activity: ActivityTypeSummary | undefined,
  unitTypeId: string,
): ActivityUnitLink | undefined {
  return activity?.unit_links.find((link) => link.unit_type_id === unitTypeId)
}

function unitLabel(activity: ActivityTypeSummary | undefined, unitTypeId: string): string {
  const link = linkFor(activity, unitTypeId)
  if (!link) {
    return 'Value'
  }
  return link.unit_type.unit_label
    ? `${link.unit_type.name} (${link.unit_type.unit_label})`
    : link.unit_type.name
}

function updateUnit(units: UnitDraft[], index: number, patch: Partial<UnitDraft>): UnitDraft[] {
  return units.map((unit, unitIndex) => (unitIndex === index ? { ...unit, ...patch } : unit))
}

function ValuePair({
  label,
  unit,
  onChange,
}: {
  label: string
  unit: UnitDraft
  onChange: (patch: Partial<UnitDraft>) => void
}) {
  return (
    <div className="grid gap-2 sm:grid-cols-[minmax(0,10rem)_1fr_1fr] sm:items-center">
      <span className="text-sm">{label}</span>
      <label className="flex flex-col gap-1 text-xs text-muted-foreground">
        Planned
        <input
          className={inputClassName}
          inputMode="decimal"
          value={unit.planned}
          onChange={(event) => onChange({ planned: event.target.value })}
        />
      </label>
      <label className="flex flex-col gap-1 text-xs text-muted-foreground">
        Actual
        <input
          className={inputClassName}
          inputMode="decimal"
          value={unit.actual}
          onChange={(event) => onChange({ actual: event.target.value })}
        />
      </label>
    </div>
  )
}

export default function MeasurementEditor({
  activity,
  once,
  sets,
  onOnceChange,
  onSetsChange,
}: MeasurementEditorProps) {
  const perSetLinks = [...(activity?.unit_links ?? [])]
    .filter((link) => link.per_set)
    .sort((left, right) => left.sort_order - right.sort_order)

  function addSet() {
    const template =
      sets[0]?.units.map((unit) => unit.unitTypeId) ??
      perSetLinks.map((link) => link.unit_type_id)
    onSetsChange([
      ...sets,
      {
        units: template.map((unitTypeId) => ({
          unitTypeId,
          planned: '',
          actual: '',
        })),
      },
    ])
  }

  return (
    <div className="flex flex-col gap-4">
      {once.map((unit, index) => (
        <ValuePair
          key={unit.unitTypeId}
          label={unitLabel(activity, unit.unitTypeId)}
          unit={unit}
          onChange={(patch) => onOnceChange(updateUnit(once, index, patch))}
        />
      ))}
      {sets.map((set, setIndex) => (
        <div key={setIndex} className="flex flex-col gap-2 rounded-lg border border-border p-3">
          <div className="flex items-center justify-between gap-2">
            <p className="text-sm font-medium">Set {setIndex + 1}</p>
            <button
              type="button"
              className="text-sm text-muted-foreground underline-offset-4 hover:underline"
              onClick={() => onSetsChange(sets.filter((_, index) => index !== setIndex))}
            >
              Remove set
            </button>
          </div>
          {set.units.map((unit, unitIndex) => (
            <ValuePair
              key={`${setIndex}-${unit.unitTypeId}`}
              label={unitLabel(activity, unit.unitTypeId)}
              unit={unit}
              onChange={(patch) =>
                onSetsChange(
                  sets.map((current, index) =>
                    index === setIndex
                      ? { units: updateUnit(current.units, unitIndex, patch) }
                      : current,
                  ),
                )
              }
            />
          ))}
        </div>
      ))}
      {perSetLinks.length > 0 ? (
        <button
          type="button"
          className="self-start text-sm text-primary underline-offset-4 hover:underline"
          onClick={addSet}
        >
          Add set
        </button>
      ) : null}
      <p className="text-xs text-muted-foreground">
        Fill planned, actual, or both. A unit with neither is left off the session.
      </p>
    </div>
  )
}
