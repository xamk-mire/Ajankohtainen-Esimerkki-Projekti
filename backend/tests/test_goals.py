import uuid

from fastapi.testclient import TestClient

from app.models.activity_type import ActivityType
from app.models.unit_type import UnitType


def _auth_header(client: TestClient, email: str) -> dict[str, str]:
    created = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "demo-pass-1",
            "display_name": "Goal Tester",
        },
    )
    assert created.status_code == 201
    login = client.post(
        "/auth/login",
        json={"email": email, "password": "demo-pass-1"},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_goal_crud_is_owner_scoped_and_validates_unit(client: TestClient) -> None:
    assert client.get("/goals").status_code == 401

    owner = _auth_header(client, f"s310-a-{uuid.uuid4().hex[:8]}@example.com")
    other = _auth_header(client, f"s310-b-{uuid.uuid4().hex[:8]}@example.com")

    db = client.app.state.testing_sessionmaker()
    distance = UnitType(
        name="Distance",
        slug=f"distance-{uuid.uuid4().hex[:6]}",
        unit_label="km",
        is_system=True,
    )
    running = ActivityType(
        name="Running",
        slug=f"running-{uuid.uuid4().hex[:6]}",
        is_system=True,
    )
    db.add_all([distance, running])
    db.commit()
    distance_id = str(distance.id)
    running_id = str(running.id)
    db.close()

    hidden_type = client.post(
        "/activity-types",
        headers=other,
        json={
            "name": "Sled push",
            "unit_links": [{"unit_type_id": distance_id}],
        },
    )
    assert hidden_type.status_code == 201
    hidden_activity_id = hidden_type.json()["id"]

    unknown = client.post(
        "/goals",
        headers=owner,
        json={
            "unit_type_id": str(uuid.uuid4()),
            "target_value": "30",
            "period": "week",
        },
    )
    assert unknown.status_code == 422

    denied_activity = client.post(
        "/goals",
        headers=owner,
        json={
            "unit_type_id": distance_id,
            "activity_type_id": hidden_activity_id,
            "target_value": "30",
            "period": "week",
        },
    )
    assert denied_activity.status_code == 422

    created = client.post(
        "/goals",
        headers=owner,
        json={
            "unit_type_id": distance_id,
            "activity_type_id": running_id,
            "target_value": "30",
            "period": "week",
        },
    )
    assert created.status_code == 201
    goal_id = created.json()["id"]
    assert created.json()["target_value"] == "30.000"
    assert created.json()["active"] is True

    assert client.get(f"/goals/{goal_id}", headers=other).status_code == 404

    paused = client.patch(
        f"/goals/{goal_id}",
        headers=owner,
        json={"active": False},
    )
    assert paused.status_code == 200
    assert paused.json()["active"] is False

    active_only = client.get("/goals", headers=owner, params={"active": "true"})
    assert active_only.status_code == 200
    assert active_only.json() == []

    inactive = client.get("/goals", headers=owner, params={"active": "false"})
    assert [row["id"] for row in inactive.json()] == [goal_id]

    deleted = client.delete(f"/goals/{goal_id}", headers=owner)
    assert deleted.status_code == 204
    assert client.get(f"/goals/{goal_id}", headers=owner).status_code == 404
