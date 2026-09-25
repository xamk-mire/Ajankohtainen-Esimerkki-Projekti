import uuid

from fastapi.testclient import TestClient

from app.models.activity_type import ActivityType
from app.models.unit_type import UnitType
from app.models.workout_plan import WorkoutPlan


def _auth_header(client: TestClient, email: str) -> tuple[dict[str, str], str]:
    created = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "demo-pass-1",
            "display_name": "Session Tester",
        },
    )
    assert created.status_code == 201
    user_id = created.json()["id"]
    login = client.post(
        "/auth/login",
        json={"email": email, "password": "demo-pass-1"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}, user_id


def test_session_crud_is_owner_scoped(client: TestClient) -> None:
    missing = client.get("/sessions")
    assert missing.status_code == 401

    owner_headers, owner_id = _auth_header(client, f"s304-a-{uuid.uuid4().hex[:8]}@example.com")
    other_headers, other_id = _auth_header(client, f"s304-b-{uuid.uuid4().hex[:8]}@example.com")

    db = client.app.state.testing_sessionmaker()
    activity = ActivityType(name="Running", slug=f"running-{uuid.uuid4().hex[:6]}", is_system=True)
    unit = UnitType(name="Duration", slug=f"duration-{uuid.uuid4().hex[:6]}", is_system=True)
    own_plan = WorkoutPlan(user_id=uuid.UUID(owner_id), name="Owner plan")
    foreign_plan = WorkoutPlan(user_id=uuid.UUID(other_id), name="Other plan")
    db.add_all([activity, unit, own_plan, foreign_plan])
    db.commit()
    activity_id = str(activity.id)
    unit_id = str(unit.id)
    own_plan_id = str(own_plan.id)
    foreign_plan_id = str(foreign_plan.id)
    db.close()

    denied_plan = client.post(
        "/sessions",
        headers=owner_headers,
        json={"name": "Nope", "plan_id": foreign_plan_id},
    )
    assert denied_plan.status_code == 404

    created = client.post(
        "/sessions",
        headers=owner_headers,
        json={
            "name": "Easy run",
            "plan_id": own_plan_id,
            "items": [
                {
                    "activity_type_id": activity_id,
                    "sort_order": 0,
                    "measurements": [
                        {
                            "unit_type_id": unit_id,
                            "planned_value": "30",
                            "actual_value": None,
                        }
                    ],
                }
            ],
        },
    )
    assert created.status_code == 201
    body = created.json()
    session_id = body["id"]
    assert body["name"] == "Easy run"
    assert body["plan_id"] == own_plan_id
    assert body["items"][0]["activity_type_id"] == activity_id
    assert body["items"][0]["measurements"][0]["planned_value"] == "30.000"
    assert body["items"][0]["measurements"][0]["actual_value"] is None

    listed = client.get("/sessions", headers=owner_headers)
    assert listed.status_code == 200
    assert [row["id"] for row in listed.json()] == [session_id]

    hidden = client.get(f"/sessions/{session_id}", headers=other_headers)
    assert hidden.status_code == 404

    patched = client.patch(
        f"/sessions/{session_id}",
        headers=owner_headers,
        json={"name": "Easy run edited"},
    )
    assert patched.status_code == 200
    assert patched.json()["name"] == "Easy run edited"
    assert patched.json()["items"][0]["measurements"][0]["planned_value"] == "30.000"

    other_delete = client.delete(f"/sessions/{session_id}", headers=other_headers)
    assert other_delete.status_code == 404

    deleted = client.delete(f"/sessions/{session_id}", headers=owner_headers)
    assert deleted.status_code == 204
    gone = client.get(f"/sessions/{session_id}", headers=owner_headers)
    assert gone.status_code == 404
