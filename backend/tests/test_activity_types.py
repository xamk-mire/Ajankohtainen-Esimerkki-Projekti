import uuid

from fastapi.testclient import TestClient

from app.models.activity_type import ActivityType
from app.models.activity_type_unit_type import ActivityTypeUnitType
from app.models.unit_type import UnitType


def _auth_header(client: TestClient, email: str) -> tuple[dict[str, str], str]:
    created = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "demo-pass-1",
            "display_name": "Catalog Tester",
        },
    )
    assert created.status_code == 201
    user_id = created.json()["id"]
    login = client.post(
        "/auth/login",
        json={"email": email, "password": "demo-pass-1"},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}, user_id


def test_activity_types_include_links_and_own_custom_only(client: TestClient) -> None:
    assert client.get("/activity-types").status_code == 401

    owner, owner_id = _auth_header(client, f"s309-a-{uuid.uuid4().hex[:8]}@example.com")
    other, _other_id = _auth_header(client, f"s309-b-{uuid.uuid4().hex[:8]}@example.com")

    db = client.app.state.testing_sessionmaker()
    duration = UnitType(
        name="Duration",
        slug=f"duration-{uuid.uuid4().hex[:6]}",
        unit_label="min",
        is_system=True,
    )
    distance = UnitType(
        name="Distance",
        slug=f"distance-{uuid.uuid4().hex[:6]}",
        unit_label="km",
        is_system=True,
    )
    running = ActivityType(name="Running", slug=f"running-{uuid.uuid4().hex[:6]}", is_system=True)
    db.add_all([duration, distance, running])
    db.flush()
    db.add_all(
        [
            ActivityTypeUnitType(
                activity_type_id=running.id,
                unit_type_id=distance.id,
                sort_order=1,
                is_required=True,
                per_set=False,
            ),
            ActivityTypeUnitType(
                activity_type_id=running.id,
                unit_type_id=duration.id,
                sort_order=0,
                is_required=True,
                per_set=False,
            ),
        ]
    )
    db.commit()
    duration_id = str(duration.id)
    distance_id = str(distance.id)
    duration_slug = duration.slug
    distance_slug = distance.slug
    running_slug = running.slug
    db.close()

    foreign = client.post(
        "/activity-types",
        headers=other,
        json={
            "name": "Sled push",
            "slug": "sled_push",
            "unit_links": [{"unit_type_id": distance_id, "per_set": True}],
        },
    )
    assert foreign.status_code == 201
    assert foreign.json()["is_system"] is False
    assert foreign.json()["user_id"] != owner_id

    created = client.post(
        "/activity-types",
        headers=owner,
        json={
            "name": "Farmer carry",
            "unit_links": [
                {"unit_type_id": distance_id, "sort_order": 1, "per_set": True},
                {"unit_type_id": duration_id, "sort_order": 0, "per_set": False},
            ],
        },
    )
    assert created.status_code == 201
    body = created.json()
    assert body["slug"] == "farmer_carry"
    assert body["user_id"] == owner_id
    assert "unit_hint" not in body
    assert [link["unit_type"]["id"] for link in body["unit_links"]] == [
        duration_id,
        distance_id,
    ]
    assert body["unit_links"][1]["per_set"] is True

    listed = client.get("/activity-types", headers=owner)
    assert listed.status_code == 200
    rows = listed.json()
    slugs = {row["slug"] for row in rows}
    assert running_slug in slugs
    assert "farmer_carry" in slugs
    assert "sled_push" not in slugs
    running_row = next(row for row in rows if row["slug"] == running_slug)
    assert [link["unit_type"]["slug"] for link in running_row["unit_links"]] == [
        duration_slug,
        distance_slug,
    ]
    assert "unit_hint" not in running_row

    duplicate = client.post(
        "/activity-types",
        headers=owner,
        json={
            "name": "Farmer carry again",
            "slug": "farmer_carry",
            "unit_links": [{"unit_type_id": duration_id}],
        },
    )
    assert duplicate.status_code == 409

    unknown = client.post(
        "/activity-types",
        headers=owner,
        json={
            "name": "Ghost",
            "unit_links": [{"unit_type_id": str(uuid.uuid4())}],
        },
    )
    assert unknown.status_code == 422
