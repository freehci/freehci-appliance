"""Trinn 50: adresseplan uten gjettet medlemskap fra CIDR, VRF-navn eller tall."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_typed_id_and_matching_cidr_do_not_invent_a_space() -> None:
    app = create_app()
    with TestClient(app) as client:
        site_a = client.post("/api/v1/dcim/sites", json={"name": "AS 50 A", "slug": "site-50-a"}).json()
        site_b = client.post("/api/v1/dcim/sites", json={"name": "AS 50 B", "slug": "site-50-b"}).json()
        missing = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={
                "site_id": site_a["id"],
                "name": "lan",
                "cidr": "10.50.0.0/24",
                "slug": "px-50-missing",
                "role": "access",
                "status": "active",
                "address_space_id": 80,
                "infer_from_cidr": True,
            },
        )
        assert missing.status_code == 400, missing.text
        assert missing.json()["detail"]["code"] == "address_space"
        a = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={
                "site_id": site_a["id"],
                "name": "lan",
                "cidr": "10.50.0.0/24",
                "slug": "px-50-a",
                "role": "access",
                "status": "active",
                "infer_from_cidr": True,
            },
        )
        assert a.status_code == 200, a.text
        assert a.json()["address_space_id"] is None
        b = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={
                "site_id": site_b["id"],
                "name": "lan",
                "cidr": "10.50.0.0/24",
                "slug": "px-50-b",
                "role": "access",
                "status": "active",
                "infer_from_cidr": True,
                "match_name": "lan",
            },
        )
        assert b.status_code == 200, b.text
        assert b.json()["address_space_id"] is None
        space = client.post(
            "/api/v1/ipam/address-spaces",
            json={"name": "campus", "slug": "as-50-campus", "match_cidrs": True},
        )
        assert space.status_code == 200, space.text
        assert space.json()["slug"] == "as-50-campus"
        still = client.get(f"/api/v1/ipam/ipv4-prefixes/{a.json()['id']}").json()
        assert still["address_space_id"] is None
        linked = client.patch(
            f"/api/v1/ipam/ipv4-prefixes/{a.json()['id']}",
            json={"address_space_id": space.json()["id"]},
        )
        assert linked.status_code == 200, linked.text
        assert linked.json()["address_space_id"] == space.json()["id"]
        assert linked.json()["address_space_slug"] == "as-50-campus"
        v6 = client.post(
            "/api/v1/ipam/ipv6-prefixes/ensure?update=true",
            json={
                "site_id": site_a["id"],
                "cidr": "fd50::/64",
                "slug": "px-50-a6",
                "address_space_slug": "as-50-campus",
            },
        )
        assert v6.status_code == 200, v6.text
        assert v6.json()["address_space_slug"] == "as-50-campus"
        assert client.delete(f"/api/v1/ipam/address-spaces/{space.json()['id']}").status_code == 204
        after_del = client.get(f"/api/v1/ipam/ipv4-prefixes/{a.json()['id']}").json()
        assert after_del["address_space_id"] is None


def test_federation_exports_address_space_by_slug() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "AS Fed 50", "slug": "as-50-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "as-50-fed-oslo", "slug": "as-50-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        space = client.post("/api/v1/ipam/address-spaces", json={"name": "fed-plan", "slug": "as-50-fed"})
        assert space.status_code == 200, space.text
        v4 = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={
                "site_id": site["id"],
                "name": "fed4",
                "cidr": "10.50.8.0/24",
                "slug": "px-50-fed-v4",
                "role": "access",
                "status": "active",
                "address_space_id": space.json()["id"],
            },
        )
        assert v4.status_code == 200, v4.text
        snap = client.get("/api/v1/federation/tenants/as-50-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        assert isinstance(doc["address_spaces"], list)
        match = next(r for r in doc["address_spaces"] if r["slug"] == "as-50-fed")
        assert match["name"] == "fed-plan"
        pmatch = next(p for p in doc["ipam"][0]["prefixes"] if p["slug"] == "px-50-fed-v4")
        assert pmatch["address_space_slug"] == "as-50-fed"
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 50", "slug": "rep-50-as"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-50-as", "name": "Rep 50", "description": None},
            "sites": [{"slug": "site-50-rep", "name": "Rep site", "description": None}],
            "rooms": [],
            "racks": [],
            "manufacturers": [],
            "device_types": [],
            "device_models": [],
            "device_roles": [],
            "devices": [],
            "placements": [],
            "dual_stack_groups": [],
            "address_spaces": [],
            "ipam": [
                {
                    "site": {"slug": "site-50-rep", "name": "Rep site"},
                    "vrfs": [],
                    "vlans": [],
                    "prefixes": [
                        {
                            "cidr": "10.50.9.0/24",
                            "slug": "px-50-rep",
                            "role": "access",
                            "status": "active",
                            "infer_from_cidr": True,
                            "address_space_id": 80,
                        }
                    ],
                    "ipv6_prefixes": [],
                }
            ],
            "clusters": [],
            "catalog_templates": [],
            "catalog_instances": [],
        }
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, replica)
        finally:
            db.close()
        after = client.get("/api/v1/ipam/ipv4-prefixes").json()
        row = next(r for r in after if r["slug"] == "px-50-rep")
        assert row["address_space_id"] is None
        replica["address_spaces"] = [{"slug": "as-50-rep", "name": "rep-plan"}]
        replica["ipam"][0]["prefixes"] = [
            {
                "cidr": "10.50.10.0/24",
                "slug": "px-50-rep2",
                "role": "access",
                "status": "active",
                "address_space_slug": "as-50-rep",
            }
        ]
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, replica)
        finally:
            db.close()
        row2 = next(r for r in client.get("/api/v1/ipam/ipv4-prefixes").json() if r["slug"] == "px-50-rep2")
        assert row2["address_space_slug"] == "as-50-rep"
