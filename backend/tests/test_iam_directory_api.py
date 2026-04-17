"""IAM API: personer, roller, grupper og nestede undergrupper."""

import uuid

from fastapi.testclient import TestClient

from app.main import create_app


def test_iam_nested_groups_and_effective_users() -> None:
    app = create_app()
    with TestClient(app) as client:
        u = client.post(
            "/api/v1/iam/persons",
            json={"username": f"u-{uuid.uuid4().hex[:8]}", "display_name": "U1"},
        )
        assert u.status_code == 200, u.text
        user_id = u.json()["id"]

        inner = client.post("/api/v1/iam/groups", json={"name": "Inner", "slug": f"inner-{uuid.uuid4().hex[:6]}"})
        assert inner.status_code == 200, inner.text
        inner_id = inner.json()["id"]

        outer = client.post("/api/v1/iam/groups", json={"name": "Outer", "slug": f"outer-{uuid.uuid4().hex[:6]}"})
        assert outer.status_code == 200, outer.text
        outer_id = outer.json()["id"]

        r = client.post(f"/api/v1/iam/groups/{inner_id}/members/users", json={"user_id": user_id})
        assert r.status_code == 204, r.text

        r2 = client.post(f"/api/v1/iam/groups/{outer_id}/members/groups", json={"child_group_id": inner_id})
        assert r2.status_code == 204, r2.text

        det = client.get(f"/api/v1/iam/groups/{outer_id}")
        assert det.status_code == 200, det.text
        body = det.json()
        assert user_id in body["effective_user_ids"]
        assert body["direct_users"] == []

        pd = client.get(f"/api/v1/iam/persons/{user_id}")
        assert pd.status_code == 200, pd.text
        gdir = {x["slug"] for x in pd.json()["groups_direct"]}
        geff = {x["slug"] for x in pd.json()["groups_effective"]}
        assert inner.json()["slug"] in gdir
        assert outer.json()["slug"] in geff


def test_iam_subgroup_cycle_rejected() -> None:
    app = create_app()
    with TestClient(app) as client:
        a = client.post("/api/v1/iam/groups", json={"name": "A", "slug": f"a-{uuid.uuid4().hex[:6]}"})
        b = client.post("/api/v1/iam/groups", json={"name": "B", "slug": f"b-{uuid.uuid4().hex[:6]}"})
        aid, bid = a.json()["id"], b.json()["id"]
        assert client.post(f"/api/v1/iam/groups/{aid}/members/groups", json={"child_group_id": bid}).status_code == 204
        bad = client.post(f"/api/v1/iam/groups/{bid}/members/groups", json={"child_group_id": aid})
        assert bad.status_code == 400
        dup = client.post(f"/api/v1/iam/groups/{aid}/members/groups", json={"child_group_id": bid})
        assert dup.status_code == 409


def test_iam_list_persons_filters_by_kind() -> None:
    app = create_app()
    with TestClient(app) as client:
        p = client.post("/api/v1/iam/persons", json={"username": f"human-{uuid.uuid4().hex[:6]}", "kind": "person"})
        assert p.status_code == 200, p.text
        s = client.post(
            "/api/v1/iam/persons",
            json={"username": f"svc-{uuid.uuid4().hex[:6]}", "kind": "service_account"},
        )
        assert s.status_code == 200, s.text
        only_p = client.get("/api/v1/iam/persons?kind=person&limit=500")
        assert only_p.status_code == 200, only_p.text
        usernames_p = {x["username"] for x in only_p.json()}
        assert p.json()["username"] in usernames_p
        assert s.json()["username"] not in usernames_p
        only_s = client.get("/api/v1/iam/persons?kind=service_account&limit=500")
        assert only_s.status_code == 200, only_s.text
        usernames_s = {x["username"] for x in only_s.json()}
        assert s.json()["username"] in usernames_s
        assert p.json()["username"] not in usernames_s


def test_iam_roles_assign() -> None:
    app = create_app()
    with TestClient(app) as client:
        u = client.post("/api/v1/iam/persons", json={"username": f"r-{uuid.uuid4().hex[:8]}"})
        assert u.status_code == 200, u.text
        uid = u.json()["id"]
        ro = client.post("/api/v1/iam/roles", json={"name": "Viewer", "slug": f"viewer-{uuid.uuid4().hex[:6]}"})
        assert ro.status_code == 200, ro.text
        rid = ro.json()["id"]
        assert client.post(f"/api/v1/iam/persons/{uid}/roles", json={"role_id": rid}).status_code == 204
        d = client.get(f"/api/v1/iam/roles/{rid}")
        assert d.status_code == 200, d.text
        assert d.json()["member_count"] == 1
        assert len(d.json()["assignees"]) == 1
