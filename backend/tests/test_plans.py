import uuid

from fastapi.testclient import TestClient


def _auth_header(client: TestClient, email: str) -> dict[str, str]:
    created = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "demo-pass-1",
            "display_name": "Plan Tester",
        },
    )
    assert created.status_code == 201
    login = client.post(
        "/auth/login",
        json={"email": email, "password": "demo-pass-1"},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_plan_crud_attach_orders_sessions(client: TestClient) -> None:
    assert client.get("/plans").status_code == 401

    owner = _auth_header(client, f"s308-a-{uuid.uuid4().hex[:8]}@example.com")
    other = _auth_header(client, f"s308-b-{uuid.uuid4().hex[:8]}@example.com")

    created = client.post(
        "/plans",
        headers=owner,
        json={"name": "Pull block", "length_weeks": 4},
    )
    assert created.status_code == 201
    plan_id = created.json()["id"]
    assert created.json()["sessions"] == []

    hidden = client.get(f"/plans/{plan_id}", headers=other)
    assert hidden.status_code == 404

    def make_session(headers: dict[str, str], name: str, session_at: str | None) -> str:
        body: dict[str, object] = {"name": name}
        if session_at is not None:
            body["session_at"] = session_at
        response = client.post("/sessions", headers=headers, json=body)
        assert response.status_code == 201
        return response.json()["id"]

    later_id = make_session(owner, "Later", "2026-09-20T10:00:00Z")
    earlier_id = make_session(owner, "Earlier", "2026-09-01T10:00:00Z")
    unscheduled_id = make_session(owner, "Unscheduled", None)
    foreign_session_id = make_session(other, "Not mine", "2026-09-02T10:00:00Z")

    denied = client.post(
        f"/plans/{plan_id}/sessions/{foreign_session_id}",
        headers=owner,
    )
    assert denied.status_code == 404

    for session_id in (later_id, unscheduled_id, earlier_id):
        attached = client.post(
            f"/plans/{plan_id}/sessions/{session_id}",
            headers=owner,
        )
        assert attached.status_code == 200

    detail = client.get(f"/plans/{plan_id}", headers=owner)
    assert detail.status_code == 200
    assert [row["id"] for row in detail.json()["sessions"]] == [
        earlier_id,
        later_id,
        unscheduled_id,
    ]

    detached = client.delete(
        f"/plans/{plan_id}/sessions/{unscheduled_id}",
        headers=owner,
    )
    assert detached.status_code == 200
    assert [row["id"] for row in detached.json()["sessions"]] == [earlier_id, later_id]

    renamed = client.patch(f"/plans/{plan_id}", headers=owner, json={"name": "Pull A"})
    assert renamed.status_code == 200
    assert renamed.json()["name"] == "Pull A"

    deleted = client.delete(f"/plans/{plan_id}", headers=owner)
    assert deleted.status_code == 204
    assert client.get(f"/plans/{plan_id}", headers=owner).status_code == 404
