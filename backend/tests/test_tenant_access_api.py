"""Tenant-medlemskap, DCIM-grants og tenant_id på IPv4-prefiks."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_tenant_member_and_dcim_grant_and_prefix_tenant() -> None:
    app = create_app()
    with TestClient(app) as client:
        site0 = client.post(
            "/api/v1/dcim/sites",
            json={"name": "TA-seed", "slug": "ta-seed-site"},
        ).json()
        tid = int(site0["tenant_id"])

        u = client.post("/api/v1/ipam/users", json={"username": "tenant-access-u1", "display_name": "U1"})
        assert u.status_code == 200, u.text
        uid = int(u.json()["id"])

        m = client.post(f"/api/v1/tenants/{tid}/members", json={"user_id": uid, "role": "admin"})
        assert m.status_code == 200, m.text
        assert m.json()["role"] == "admin"

        dup = client.post(f"/api/v1/tenants/{tid}/members", json={"user_id": uid, "role": "member"})
        assert dup.status_code == 409

        li = client.get(f"/api/v1/tenants/{tid}/members")
        assert li.status_code == 200
        assert any(x["user_id"] == uid for x in li.json())

        site = client.post("/api/v1/dcim/sites", json={"name": "GrantSite", "slug": "grant-site-2"}).json()
        sid = int(site["id"])

        g = client.post(
            f"/api/v1/tenants/{tid}/dcim-grants",
            json={"scope_type": "site", "scope_id": sid, "access": "view"},
        )
        assert g.status_code == 200, g.text
        gid = int(g.json()["id"])

        grants = client.get(f"/api/v1/tenants/{tid}/dcim-grants")
        assert grants.status_code == 200
        assert any(x["id"] == gid for x in grants.json())

        dup_g = client.post(
            f"/api/v1/tenants/{tid}/dcim-grants",
            json={"scope_type": "site", "scope_id": sid, "access": "manage"},
        )
        assert dup_g.status_code == 409

        pfx = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={
                "site_id": sid,
                "name": "Kunde",
                "cidr": "10.40.0.0/24",
                "tenant_id": tid,
            },
        )
        assert pfx.status_code == 200, pfx.text
        assert pfx.json()["tenant_id"] == tid

        by_tenant = client.get("/api/v1/ipam/ipv4-prefixes", params={"tenant_id": tid})
        assert by_tenant.status_code == 200
        assert any(p["cidr"] == "10.40.0.0/24" for p in by_tenant.json())

        rm = client.delete(f"/api/v1/tenants/{tid}/members/{uid}")
        assert rm.status_code == 204

        rm_g = client.delete(f"/api/v1/tenants/{tid}/dcim-grants/{gid}")
        assert rm_g.status_code == 204
