"""Trinn 47: dual-stack-gruppe uten gjettet paring fra tall, navn eller CIDR."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_typed_id_and_matching_cidr_do_not_invent_a_group() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "DS 47", "slug": "site-47-ds"}).json()
        missing = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={
                "site_id": site["id"],
                "name": "lan4",
                "cidr": "10.47.0.0/24",
                "slug": "px-47-v4-missing",
                "role": "access",
                "status": "active",
                "dual_stack_group_id": 80,
                "infer_pair": True,
                "match_cidr": True,
            },
        )
        assert missing.status_code == 400, missing.text
        assert missing.json()["detail"]["code"] == "dual_stack_group"
        created = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={
                "site_id": site["id"],
                "name": "lan4",
                "cidr": "10.47.0.0/24",
                "slug": "px-47-v4",
                "role": "access",
                "status": "active",
                "infer_pair": True,
                "match_name": "lan6",
            },
        )
        assert created.status_code == 200, created.text
        assert created.json()["dual_stack_group_id"] is None
        assert created.json()["dual_stack_group_slug"] is None
        v6 = client.post(
            "/api/v1/ipam/ipv6-prefixes",
            json={
                "site_id": site["id"],
                "name": "lan6",
                "cidr": "fd47::/64",
                "slug": "px-47-v6",
                "role": "access",
                "status": "active",
                "infer_pair": True,
            },
        )
        assert v6.status_code == 200, v6.text
        assert v6.json()["dual_stack_group_id"] is None
        group = client.post(
            "/api/v1/ipam/dual-stack-groups",
            json={"name": "lan-pair", "slug": "ds-47-lan", "match_prefixes": True},
        )
        assert group.status_code == 200, group.text
        assert group.json()["slug"] == "ds-47-lan"
        listed = client.get("/api/v1/ipam/dual-stack-groups").json()
        assert any(g["slug"] == "ds-47-lan" for g in listed)
        still = client.get(f"/api/v1/ipam/ipv4-prefixes/{created.json()['id']}").json()
        assert still["dual_stack_group_id"] is None
        linked = client.patch(
            f"/api/v1/ipam/ipv4-prefixes/{created.json()['id']}",
            json={"dual_stack_group_id": group.json()["id"]},
        )
        assert linked.status_code == 200, linked.text
        assert linked.json()["dual_stack_group_id"] == group.json()["id"]
        assert linked.json()["dual_stack_group_slug"] == "ds-47-lan"
        assert linked.json()["dual_stack_group_name"] == "lan-pair"
        v6_link = client.post(
            "/api/v1/ipam/ipv6-prefixes/ensure?update=true",
            json={
                "site_id": site["id"],
                "cidr": "fd47::/64",
                "dual_stack_group_slug": "ds-47-lan",
            },
        )
        assert v6_link.status_code == 200, v6_link.text
        assert v6_link.json()["dual_stack_group_slug"] == "ds-47-lan"
        assert client.delete(f"/api/v1/ipam/dual-stack-groups/{group.json()['id']}").status_code == 204
        after_del = client.get(f"/api/v1/ipam/ipv4-prefixes/{created.json()['id']}").json()
        assert after_del["dual_stack_group_id"] is None


def test_federation_exports_dual_stack_by_slug() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "DS Fed 47", "slug": "ds-47-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "ds-47-fed-oslo", "slug": "ds-47-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        group = client.post(
            "/api/v1/ipam/dual-stack-groups",
            json={"name": "fed-pair", "slug": "ds-47-fed"},
        )
        assert group.status_code == 200, group.text
        v4 = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={
                "site_id": site["id"],
                "name": "fed4",
                "cidr": "10.47.8.0/24",
                "slug": "px-47-fed-v4",
                "role": "access",
                "status": "active",
                "dual_stack_group_id": group.json()["id"],
            },
        )
        assert v4.status_code == 200, v4.text
        snap = client.get("/api/v1/federation/tenants/ds-47-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        assert isinstance(doc["dual_stack_groups"], list)
        match = next(r for r in doc["dual_stack_groups"] if r["slug"] == "ds-47-fed")
        assert match["name"] == "fed-pair"
        pmatch = next(p for p in doc["ipam"][0]["prefixes"] if p["slug"] == "px-47-fed-v4")
        assert pmatch["dual_stack_group_slug"] == "ds-47-fed"
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 47", "slug": "rep-47-ds"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-47-ds", "name": "Rep 47", "description": None},
            "sites": [{"slug": "site-47-rep", "name": "Rep site", "description": None}],
            "rooms": [],
            "racks": [],
            "manufacturers": [],
            "device_types": [],
            "device_models": [],
            "device_roles": [],
            "devices": [],
            "placements": [],
            "dual_stack_groups": [],
            "ipam": [
                {
                    "site": {"slug": "site-47-rep", "name": "Rep site"},
                    "vrfs": [],
                    "vlans": [],
                    "prefixes": [
                        {
                            "cidr": "10.47.9.0/24",
                            "slug": "px-47-rep",
                            "role": "access",
                            "status": "active",
                            "infer_pair": True,
                            "dual_stack_group_id": 80,
                        }
                    ],
                    "ipv6_prefixes": [
                        {"cidr": "fd47:9::/64", "slug": "px-47-rep6", "role": "access", "status": "active"}
                    ],
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
        row = next(r for r in after if r["slug"] == "px-47-rep")
        assert row["dual_stack_group_id"] is None
        replica["dual_stack_groups"] = [{"slug": "ds-47-rep", "name": "rep-pair"}]
        replica["ipam"][0]["prefixes"] = [
            {
                "cidr": "10.47.9.0/24",
                "slug": "px-47-rep",
                "role": "access",
                "status": "active",
                "dual_stack_group_slug": "ds-47-rep",
            }
        ]
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, replica)
        finally:
            db.close()
        linked = client.get("/api/v1/ipam/ipv4-prefixes").json()
        row2 = next(r for r in linked if r["slug"] == "px-47-rep")
        assert row2["dual_stack_group_slug"] == "ds-47-rep"
        _ = site
