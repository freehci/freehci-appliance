"""API-tester for site-roller og tilgang/kontakt-grants."""

import uuid

from fastapi.testclient import TestClient

from app.main import create_app


def test_site_roles_and_access_grants_flow() -> None:
    app = create_app()
    with TestClient(app) as client:
        slug = f"site-{uuid.uuid4().hex[:8]}"
        s = client.post("/api/v1/dcim/sites", json={"name": "Test Site", "slug": slug})
        assert s.status_code == 200, s.text
        site_id = s.json()["id"]

        # Sikrer default-roller.
        rr = client.get("/api/v1/dcim/site-roles")
        assert rr.status_code == 200, rr.text
        roles = rr.json()
        assert isinstance(roles, list) and roles, "forventet default-roller"
        role_id = roles[0]["id"]

        # Opprett en 'user' (kontaktperson-katalog).
        u = client.post(
            "/api/v1/ipam/users",
            json={
                "username": f"p-{uuid.uuid4().hex[:8]}",
                "display_name": "Per",
                "email": "per@example.com",
                "phone": "+4712345678",
                "kind": "person",
                "notes": "Kontaktperson",
            },
        )
        assert u.status_code == 200, u.text
        user_id = u.json()["id"]
        assert u.json()["email"] == "per@example.com"

        g = client.post(
            f"/api/v1/dcim/sites/{site_id}/access",
            json={"user_id": user_id, "role_id": role_id, "is_contact": True, "notes": "Primær kontakt"},
        )
        assert g.status_code == 200, g.text
        assert g.json()["is_contact"] is True

        li = client.get(f"/api/v1/dcim/sites/{site_id}/access")
        assert li.status_code == 200, li.text
        assert len(li.json()) == 1

