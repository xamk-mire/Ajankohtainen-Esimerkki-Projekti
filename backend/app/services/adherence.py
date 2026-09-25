"""Planned-vs-actual comparison. No FastAPI and no database session.

Sprint 4 can chart this preview. Each result is one ``unit_type_id``.
Totals are not added across units.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class MeasurementSample:
    unit_type_id: UUID
    planned: Decimal | None
    actual: Decimal | None
    session_at: datetime | None


@dataclass(frozen=True)
class UnitAdherence:
    unit_type_id: UUID
    compared: int
    planned_total: Decimal
    actual_total: Decimal
    hit_count: int


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _in_range(
    session_at: datetime | None,
    starts_at: datetime | None,
    ends_at: datetime | None,
) -> bool:
    if session_at is None:
        return False
    moment = _as_utc(session_at)
    if starts_at is not None and moment < _as_utc(starts_at):
        return False
    if ends_at is not None and moment > _as_utc(ends_at):
        return False
    return True


def summarize_adherence(
    samples: list[MeasurementSample],
    *,
    starts_at: datetime | None,
    ends_at: datetime | None,
) -> list[UnitAdherence]:
    """Compare rows that have both values and a ``session_at`` inside the range.

    A null planned value, a null actual value, a null ``session_at``, or a
    session outside the inclusive bounds is skipped. ``hit_count`` is how many
    compared rows have ``actual >= planned``.
    """
    grouped: dict[UUID, list[tuple[Decimal, Decimal]]] = {}
    for sample in samples:
        if not _in_range(sample.session_at, starts_at, ends_at):
            continue
        if sample.planned is None or sample.actual is None:
            continue
        grouped.setdefault(sample.unit_type_id, []).append((sample.planned, sample.actual))

    summaries: list[UnitAdherence] = []
    for unit_type_id in sorted(grouped, key=str):
        pairs = grouped[unit_type_id]
        summaries.append(
            UnitAdherence(
                unit_type_id=unit_type_id,
                compared=len(pairs),
                planned_total=sum((planned for planned, _actual in pairs), Decimal(0)),
                actual_total=sum((actual for _planned, actual in pairs), Decimal(0)),
                hit_count=sum(1 for planned, actual in pairs if actual >= planned),
            )
        )
    return summaries
