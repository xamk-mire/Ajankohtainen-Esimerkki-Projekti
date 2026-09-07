import uuid

from fastapi.testclient import TestClient


def test_register_login_me(client: TestClient) -> None:
    email = f"s2s3-{uuid.uuid4().hex[:8]}@example.com"
    password = "demo-pass-1"
    display_name = "S2-S3 Tester"

    unauthenticated = client.get("/auth/me")
    assert unauthenticated.status_code == 401

    created = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
            "display_name": display_name,
        },
    )
    assert created.status_code == 201
    public_user = created.json()
    assert public_user["email"] == email
    assert public_user["display_name"] == display_name
    assert "password" not in public_user
    assert "password_hash" not in public_user

    login = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200
    token_body = login.json()
    assert token_body["token_type"] == "bearer"
    token = token_body["access_token"]
    assert token

    me = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me.status_code == 200
    profile = me.json()
    assert profile["id"] == public_user["id"]
    assert profile["email"] == email
    assert profile["display_name"] == display_name
