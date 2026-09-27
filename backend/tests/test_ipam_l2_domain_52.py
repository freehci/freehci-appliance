"""Trinn 52: L2-domene uten gjettet medlemskap fra VID, navn eller A–B-strekning."""

from fastapi.testclient import TestClient

from app.main import create_app


def _vlan(client: TestClient, site_id: int, vid: int, slug: str, **extra):
    return client.post(
        "/api/v1/ipam/vlans",
        json={"site_id": site_id, "vid": vid, "name": "corp", "slug": slug, **extra},
    )


def test_typed_id_and_matching_vid_do_not_invent_a_domain() -> None:
    app = create_app()
    with TestClient(app) as client:
        site_a = client.post("/api/v1/dcim/sites", json={"name": "L2 52 A", "slug": "site-52-a"}).json()
        site_b = client.post("/api/v1/dcim/sites", json={"name": "L2 52 B", "slug": "site-52-b"}).json()
        site_c = client.post("/api/v1/dcim/sites", json={"name": "L2 52 C", "slug": "site-52-c"}).json()
        missing = _vlan(client, site_a["id"], 100, "vlan-52-missing", l2_domain_id=80, infer_from_vid=True)
        assert missing.status_code == 400, missing.text
        assert missing.json()["detail"]["code"] == "l2_domain"
        a = _vlan(client, site_a["id"], 100, "vlan-52-a", infer_from_vid=True)
        assert a.status_code == 200, a.text
        assert a.json()["l2_domain_id"] is None
        b = _vlan(client, site_b["id"], 100, "vlan-52-b", infer_from_vid=True, match_name="corp")
        assert b.status_code == 200, b.text
        assert b.json()["l2_domain_id"] is None
        c = _vlan(client, site_c["id"], 100, "vlan-52-c")
        assert c.status_code == 200, c.text
        assert c.json()["l2_domain_id"] is None
        domain = client.post(
            "/api/v1/ipam/l2-domains",
            json={"name": "campus", "slug": "l2-52-campus", "match_vids": True},
        )
        assert domain.status_code == 200, domain.text
        assert domain.json()["slug"] == "l2-52-campus"
        still = client.get(f"/api/v1/ipam/vlans/{a.json()['id']}").json()
        assert still["l2_domain_id"] is None
        stretch = client.post(
            "/api/v1/ipam/vlan-stretches",
            json={
                "vlan_a_id": a.json()["id"],
                "vlan_b_id": b.json()["id"],
                "name": "ab-52",
                "slug": "stretch-52-ab",
            },
        )
        assert stretch.status_code == 200, stretch.text
        after_stretch_a = client.get(f"/api/v1/ipam/vlans/{a.json()['id']}").json()
        after_stretch_b = client.get(f"/api/v1/ipam/vlans/{b.json()['id']}").json()
        assert after_stretch_a["l2_domain_id"] is None
        assert after_stretch_b["l2_domain_id"] is None
        linked = client.patch(
            f"/api/v1/ipam/vlans/{a.json()['id']}",
            json={"l2_domain_id": domain.json()["id"]},
        )
        assert linked.status_code == 200, linked.text
        assert linked.json()["l2_domain_id"] == domain.json()["id"]
        assert linked.json()["l2_domain_slug"] == "l2-52-campus"
        linked_c = client.patch(
            f"/api/v1/ipam/vlans/{c.json()['id']}",
            json={"l2_domain_slug": "l2-52-campus"},
        )
        assert linked_c.status_code == 200, linked_c.text
        assert linked_c.json()["l2_domain_slug"] == "l2-52-campus"
        assert client.delete(f"/api/v1/ipam/l2-domains/{domain.json()['id']}").status_code == 204
        after_del = client.get(f"/api/v1/ipam/vlans/{a.json()['id']}").json()
        assert after_del["l2_domain_id"] is None


def test_federation_exports_l2_domain_by_slug() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "L2 Fed 52", "slug": "l2-52-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "l2-52-fed-oslo", "slug": "l2-52-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        domain = client.post("/api/v1/ipam/l2-domains", json={"name": "fed-l2", "slug": "l2-52-fed"})
        assert domain.status_code == 200, domain.text
        vlan = _vlan(client, site["id"], 200, "vlan-52-fed", l2_domain_id=domain.json()["id"])
        assert vlan.status_code == 200, vlan.text
        snap = client.get("/api/v1/federation/tenants/l2-52-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        assert isinstance(doc["l2_domains"], list)
        match = next(r for r in doc["l2_domains"] if r["slug"] == "l2-52-fed")
        assert match["name"] == "fed-l2"
        vmatch = next(v for v in doc["ipam"][0]["vlans"] if v["slug"] == "vlan-52-fed")
        assert vmatch["l2_domain_slug"] == "l2-52-fed"
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 52", "slug": "rep-52-l2"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-52-l2", "name": "Rep 52", "description": None},
            "sites": [{"slug": "site-52-rep", "name": "Rep site", "description": None}],
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
            "l2_domains": [],
            "ipam": [
                {
                    "site": {"slug": "site-52-rep", "name": "Rep site"},
                    "vrfs": [],
                    "vlans": [
                        {
                            "vid": 300,
                            "name": "corp",
                            "slug": "vlan-52-rep",
                            "infer_from_vid": True,
                            "l2_domain_id": 80,
                        }
                    ],
                    "prefixes": [],
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
        after = client.get("/api/v1/ipam/vlans").json()
        row = next(r for r in after if r["slug"] == "vlan-52-rep")
        assert row["l2_domain_id"] is None
        replica["l2_domains"] = [{"slug": "l2-52-rep", "name": "rep-l2"}]
        replica["ipam"][0]["vlans"] = [
            {
                "vid": 301,
                "name": "corp",
                "slug": "vlan-52-rep2",
                "l2_domain_slug": "l2-52-rep",
            }
        ]
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, replica)
        finally:
            db.close()
        row2 = next(r for r in client.get("/api/v1/ipam/vlans").json() if r["slug"] == "vlan-52-rep2")
        assert row2["l2_domain_slug"] == "l2-52-rep"
