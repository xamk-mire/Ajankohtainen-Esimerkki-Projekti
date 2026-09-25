import uuid

from fastapi.testclient import TestClient


def _auth_header(client: TestClient, email: str) -> dict[str, str]:
    created = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "demo-pass-1",
            "display_name": "Calendar Tester",
        },
    )
    assert created.status_code == 201
    login = client.post(
        "/auth/login",
        json={"email": email, "password": "demo-pass-1"},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_calendar_returns_own_dated_sessions_in_order(client: TestClient) -> None:
    assert client.get("/calendar").status_code == 401

    owner = _auth_header(client, f"s312-a-{uuid.uuid4().hex[:8]}@example.com")
    other = _auth_header(client, f"s312-b-{uuid.uuid4().hex[:8]}@example.com")

    plan = client.post("/plans", headers=owner, json={"name": "September"})
    assert plan.status_code == 201
    plan_id = plan.json()["id"]
    foreign_plan = client.post("/plans", headers=other, json={"name": "Other"})
    assert foreign_plan.status_code == 201

    def make_session(headers: dict[str, str], name: str, session_at: str | None) -> str:
        body: dict[str, object] = {"name": name}
        if session_at is not None:
            body["session_at"] = session_at
        response = client.post("/sessions", headers=headers, json=body)
        assert response.status_code == 201
        return response.json()["id"]

    later_id = make_session(owner, "Later", "2026-09-12T10:00:00Z")
    earlier_id = make_session(owner, "Earlier", "2026-09-08T10:00:00Z")
    outside_id = make_session(owner, "Outside", "2026-09-01T10:00:00Z")
    unscheduled_id = make_session(owner, "Unscheduled", None)
    foreign_id = make_session(other, "Foreign", "2026-09-10T10:00:00Z")

    attached = client.post(f"/plans/{plan_id}/sessions/{earlier_id}", headers=owner)
    assert attached.status_code == 200

    listed = client.get(
        "/calendar",
        headers=owner,
        params={"from": "2026-09-05T00:00:00Z", "to": "2026-09-15T00:00:00Z"},
    )
    assert listed.status_code == 200
    rows = listed.json()
    assert [row["id"] for row in rows] == [earlier_id, later_id]
    assert rows[0]["plan_id"] == plan_id
    assert rows[0]["session_at"].startswith("2026-09-08")
    assert outside_id not in {row["id"] for row in rows}
    assert unscheduled_id not in {row["id"] for row in rows}
    assert foreign_id not in {row["id"] for row in rows}
    assert set(rows[0]) == {"id", "name", "session_at", "status", "plan_id"}

    by_plan = client.get(
        "/calendar",
        headers=owner,
        params={
            "from": "2026-09-05T00:00:00Z",
            "to": "2026-09-15T00:00:00Z",
            "plan_id": plan_id,
        },
    )
    assert [row["id"] for row in by_plan.json()] == [earlier_id]

    hidden_plan = client.get(
        "/calendar",
        headers=owner,
        params={"plan_id": foreign_plan.json()["id"]},
    )
    assert hidden_plan.status_code == 200
    assert hidden_plan.json() == []

    other_view = client.get(
        "/calendar",
        headers=other,
        params={"from": "2026-09-05T00:00:00Z", "to": "2026-09-15T00:00:00Z"},
    )
    assert [row["id"] for row in other_view.json()] == [foreign_id]

    bad_range = client.get(
        "/calendar",
        headers=owner,
        params={"from": "2026-09-15T00:00:00Z", "to": "2026-09-05T00:00:00Z"},
    )
    assert bad_range.status_code == 400
    assert bad_range.json()["detail"] == "from must not be after to"
