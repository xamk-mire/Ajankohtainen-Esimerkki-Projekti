import uuid

from fastapi.testclient import TestClient

from app.models.unit_type import UnitType


def _auth_header(client: TestClient, email: str) -> dict[str, str]:
    created = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "demo-pass-1",
            "display_name": "Owner Tester",
        },
    )
    assert created.status_code == 201
    login = client.post(
        "/auth/login",
        json={"email": email, "password": "demo-pass-1"},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def _denied(response, detail: str) -> None:
    assert response.status_code == 404
    assert response.json()["detail"] == detail


def test_cross_user_object_access_is_404(client: TestClient) -> None:
    owner = _auth_header(client, f"s311-a-{uuid.uuid4().hex[:8]}@example.com")
    other = _auth_header(client, f"s311-b-{uuid.uuid4().hex[:8]}@example.com")

    db = client.app.state.testing_sessionmaker()
    unit = UnitType(
        name="Distance",
        slug=f"distance-{uuid.uuid4().hex[:6]}",
        is_system=True,
    )
    db.add(unit)
    db.commit()
    unit_id = str(unit.id)
    db.close()

    session = client.post(
        "/sessions",
        headers=owner,
        json={"name": "Easy run", "session_at": "2026-09-28T15:00:00Z"},
    )
    plan = client.post("/plans", headers=owner, json={"name": "Pull block"})
    goal = client.post(
        "/goals",
        headers=owner,
        json={"unit_type_id": unit_id, "target_value": "20", "period": "week"},
    )
    assert session.status_code == 201
    assert plan.status_code == 201
    assert goal.status_code == 201
    session_id = session.json()["id"]
    plan_id = plan.json()["id"]
    goal_id = goal.json()["id"]

    _denied(client.get(f"/sessions/{session_id}", headers=other), "Session not found")
    _denied(
        client.patch(f"/sessions/{session_id}", headers=other, json={"notes": "nope"}),
        "Session not found",
    )
    _denied(client.delete(f"/sessions/{session_id}", headers=other), "Session not found")
    _denied(client.post(f"/sessions/{session_id}/clone", headers=other), "Session not found")
    assert client.get(f"/sessions/{session_id}").status_code == 401

    other_plan = client.post("/plans", headers=other, json={"name": "Other plan"})
    assert other_plan.status_code == 201
    other_plan_id = other_plan.json()["id"]
    _denied(
        client.post(f"/plans/{other_plan_id}/sessions/{session_id}", headers=other),
        "Session not found",
    )

    _denied(client.get(f"/plans/{plan_id}", headers=other), "Plan not found")
    _denied(
        client.patch(f"/plans/{plan_id}", headers=other, json={"notes": "nope"}),
        "Plan not found",
    )
    _denied(client.delete(f"/plans/{plan_id}", headers=other), "Plan not found")
    _denied(
        client.post(f"/plans/{plan_id}/sessions/{session_id}", headers=other),
        "Plan not found",
    )

    other_session = client.post("/sessions", headers=other, json={"name": "Not yours"})
    assert other_session.status_code == 201
    _denied(
        client.post(
            f"/plans/{plan_id}/sessions/{other_session.json()['id']}",
            headers=owner,
        ),
        "Session not found",
    )

    _denied(client.get(f"/goals/{goal_id}", headers=other), "Goal not found")
    _denied(
        client.patch(f"/goals/{goal_id}", headers=other, json={"active": False}),
        "Goal not found",
    )
    _denied(client.delete(f"/goals/{goal_id}", headers=other), "Goal not found")

    assert client.get(f"/sessions/{session_id}", headers=owner).status_code == 200
    assert client.get(f"/plans/{plan_id}", headers=owner).status_code == 200
    assert client.get(f"/goals/{goal_id}", headers=owner).status_code == 200

    other_sessions = client.get("/sessions", headers=other).json()["items"]
    assert [row["id"] for row in other_sessions] == [other_session.json()["id"]]
    assert session_id not in {row["id"] for row in other_sessions}

    other_plans = client.get("/plans", headers=other).json()
    assert [row["id"] for row in other_plans] == [other_plan_id]
    assert plan_id not in {row["id"] for row in other_plans}

    other_goals = client.get("/goals", headers=other).json()
    assert goal_id not in {row["id"] for row in other_goals}

    other_calendar = client.get("/calendar", headers=other).json()
    assert session_id not in {row["id"] for row in other_calendar}
    owner_calendar = client.get("/calendar", headers=owner).json()
    assert session_id in {row["id"] for row in owner_calendar}

    foreign_sessions = client.get("/sessions", headers=other, params={"plan_id": plan_id})
    assert foreign_sessions.status_code == 200
    assert foreign_sessions.json()["items"] == []
    foreign_calendar = client.get("/calendar", headers=other, params={"plan_id": plan_id})
    assert foreign_calendar.status_code == 200
    assert foreign_calendar.json() == []
