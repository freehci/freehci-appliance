"""Policy og API for effektive DCIM-site-tilganger per IAM-bruker."""

import uuid

from fastapi.testclient import TestClient

from app.main import create_app


def test_user_accessible_site_ids_grant_membership_and_site_access() -> None:
    app = create_app()
    with TestClient(app) as client:
        site_main = client.post(
            "/api/v1/dcim/sites",
            json={"name": "Main DC", "slug": f"main-{uuid.uuid4().hex[:8]}"},
        ).json()
        site_main_id = int(site_main["id"])

        site_other = client.post(
            "/api/v1/dcim/sites",
            json={"name": "Other DC", "slug": f"other-{uuid.uuid4().hex[:8]}"},
        ).json()
        site_other_id = int(site_other["id"])

        tenant_c = client.post(
            "/api/v1/tenants",
            json={"name": "Customer", "slug": f"cust-{uuid.uuid4().hex[:8]}"},
        )
        assert tenant_c.status_code == 200, tenant_c.text
        tid_c = int(tenant_c.json()["id"])

        u = client.post("/api/v1/ipam/users", json={"username": f"pol-{uuid.uuid4().hex[:8]}"})
        assert u.status_code == 200, u.text
        uid = int(u.json()["id"])

        # Ingen tilgang ennå (ikke medlem av default-tenant, ingen grants).
        empty = client.get(f"/api/v1/tenants/users/{uid}/accessible-site-ids")
        assert empty.status_code == 200, empty.text
        assert site_main_id not in empty.json()["site_ids"]
        assert site_other_id not in empty.json()["site_ids"]

        # Medlemskap + site-grant på kunde-tenant → ser site_main.
        m = client.post(f"/api/v1/tenants/{tid_c}/members", json={"user_id": uid, "role": "member"})
        assert m.status_code == 200, m.text

        g = client.post(
            f"/api/v1/tenants/{tid_c}/dcim-grants",
            json={"scope_type": "site", "scope_id": site_main_id, "access": "view"},
        )
        assert g.status_code == 200, g.text

        li = client.get(f"/api/v1/tenants/users/{uid}/accessible-site-ids")
        assert li.status_code == 200, li.text
        sids = li.json()["site_ids"]
        assert site_main_id in sids
        assert site_other_id not in sids

        # Direkte site-tilgang (dcim_site_access) uten tenant-medlemskap.
        u2 = client.post("/api/v1/ipam/users", json={"username": f"pol2-{uuid.uuid4().hex[:8]}"})
        assert u2.status_code == 200, u2.text
        uid2 = int(u2.json()["id"])

        rr = client.get("/api/v1/dcim/site-roles")
        assert rr.status_code == 200, rr.text
        role_id = rr.json()[0]["id"]

        acc = client.post(
            f"/api/v1/dcim/sites/{site_other_id}/access",
            json={"user_id": uid2, "role_id": role_id, "is_contact": False},
        )
        assert acc.status_code == 200, acc.text

        li2 = client.get(f"/api/v1/tenants/users/{uid2}/accessible-site-ids")
        assert li2.status_code == 200, li2.text
        assert site_other_id in li2.json()["site_ids"]

        nf = client.get("/api/v1/tenants/users/999999/accessible-site-ids")
        assert nf.status_code == 404
