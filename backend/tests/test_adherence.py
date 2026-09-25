import uuid
from datetime import datetime, timezone
from decimal import Decimal

from fastapi.testclient import TestClient

from app.models.activity_type import ActivityType
from app.models.activity_type_unit_type import ActivityTypeUnitType
from app.models.unit_type import UnitType
from app.services.adherence import MeasurementSample, summarize_adherence

START = datetime(2026, 9, 1, tzinfo=timezone.utc)
END = datetime(2026, 9, 30, 23, 59, tzinfo=timezone.utc)
INSIDE = datetime(2026, 9, 10, 12, tzinfo=timezone.utc)


def test_summarize_adherence_compares_pairs_and_skips_gaps() -> None:
    distance = uuid.uuid4()
    weight = uuid.uuid4()
    rows = summarize_adherence(
        [
            MeasurementSample(distance, Decimal("30"), Decimal("28"), INSIDE),
            MeasurementSample(distance, Decimal("10"), Decimal("10"), INSIDE),
            MeasurementSample(distance, Decimal("5"), None, INSIDE),
            MeasurementSample(distance, None, Decimal("8"), INSIDE),
            MeasurementSample(weight, Decimal("40"), Decimal("42"), INSIDE),
            MeasurementSample(
                distance,
                Decimal("99"),
                Decimal("99"),
                datetime(2026, 8, 1, tzinfo=timezone.utc),
            ),
            MeasurementSample(distance, Decimal("7"), Decimal("7"), None),
        ],
        starts_at=START,
        ends_at=END,
    )
    by_unit = {row.unit_type_id: row for row in rows}
    distance_row = by_unit[distance]
    assert distance_row.compared == 2
    assert distance_row.planned_total == Decimal("40")
    assert distance_row.actual_total == Decimal("38")
    assert distance_row.hit_count == 1
    weight_row = by_unit[weight]
    assert weight_row.compared == 1
    assert weight_row.planned_total == Decimal("40")
    assert weight_row.actual_total == Decimal("42")
    assert weight_row.hit_count == 1


def test_summarize_adherence_empty_input() -> None:
    assert summarize_adherence([], starts_at=START, ends_at=END) == []


def _auth_header(client: TestClient, email: str) -> dict[str, str]:
    created = client.post(
        "/auth/register",
        json={"email": email, "password": "demo-pass-1", "display_name": "Adherence"},
    )
    assert created.status_code == 201
    login = client.post(
        "/auth/login",
        json={"email": email, "password": "demo-pass-1"},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_adherence_route_counts_only_the_caller(client: TestClient) -> None:
    assert client.get("/sessions/adherence").status_code == 401

    owner = _auth_header(client, f"s3s4-a-{uuid.uuid4().hex[:8]}@example.com")
    other = _auth_header(client, f"s3s4-b-{uuid.uuid4().hex[:8]}@example.com")

    db = client.app.state.testing_sessionmaker()
    activity = ActivityType(name="Run", slug=f"run-{uuid.uuid4().hex[:6]}", is_system=True)
    unit = UnitType(name="Minutes", slug=f"min-{uuid.uuid4().hex[:6]}", is_system=True)
    db.add_all([activity, unit])
    db.flush()
    db.add(
        ActivityTypeUnitType(
            activity_type_id=activity.id,
            unit_type_id=unit.id,
            sort_order=0,
            per_set=False,
        )
    )
    db.commit()
    activity_id = str(activity.id)
    unit_id = str(unit.id)
    db.close()

    def log(headers: dict[str, str], name: str, session_at: str | None, planned: str, actual: str | None) -> None:
        created = client.post(
            "/sessions",
            headers=headers,
            json={
                "name": name,
                "session_at": session_at,
                "items": [
                    {
                        "activity_type_id": activity_id,
                        "measurements": [
                            {
                                "unit_type_id": unit_id,
                                "planned_value": planned,
                                "actual_value": actual,
                            }
                        ],
                    }
                ],
            },
        )
        assert created.status_code == 201

    log(owner, "In range", "2026-09-10T12:00:00Z", "30", "28")
    log(owner, "Unscheduled", None, "100", "100")
    log(owner, "Outside", "2026-08-01T12:00:00Z", "50", "50")
    log(other, "Other user", "2026-09-10T12:00:00Z", "9", "9")

    reversed_range = client.get(
        "/sessions/adherence",
        headers=owner,
        params={"from": "2026-09-20T00:00:00Z", "to": "2026-09-01T00:00:00Z"},
    )
    assert reversed_range.status_code == 400
    assert reversed_range.json()["detail"] == "from must not be after to"

    listed = client.get(
        "/sessions/adherence",
        headers=owner,
        params={"from": "2026-09-01T00:00:00Z", "to": "2026-09-30T23:59:59Z"},
    )
    assert listed.status_code == 200
    body = listed.json()
    assert len(body) == 1
    row = body[0]
    assert row["unit_type_id"] == unit_id
    assert row["compared"] == 1
    assert Decimal(row["planned_total"]) == Decimal("30")
    assert Decimal(row["actual_total"]) == Decimal("28")
    assert row["hit_count"] == 0

    spec = client.get("/openapi.json").json()
    parameters = {
        parameter["name"]
        for parameter in spec["paths"]["/sessions/adherence"]["get"]["parameters"]
    }
    assert {"from", "to"} <= parameters
