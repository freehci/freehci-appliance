"""Trinn 23: navngitt fiberbunt uten gjettet antall, par eller rør."""

from fastapi.testclient import TestClient

from app.main import create_app


def _fiber_cable(client: TestClient, slug: str, cable_type: str = "sm-os2") -> tuple[int, int]:
    site = client.post("/api/v1/dcim/sites", json={"name": slug, "slug": slug}).json()
    a = client.post("/api/v1/dcim/devices", json={"name": f"{slug}-a", "site_id": site["id"]}).json()
    z = client.post("/api/v1/dcim/devices", json={"name": f"{slug}-z", "site_id": site["id"]}).json()
    pa = client.post(f"/api/v1/dcim/devices/{a['id']}/ports", json={"kind": "front-port", "name": "P1"}).json()
    pz = client.post(f"/api/v1/dcim/devices/{z['id']}/ports", json={"kind": "front-port", "name": "P1"}).json()
    cab = client.post(
        "/api/v1/dcim/cables",
        json={
            "site_id": site["id"],
            "name": f"{slug}-os2",
            "slug": f"cab-{slug}",
            "cable_type": cable_type,
            "a": {"object_type": "device-port", "object_id": pa["id"]},
            "z": {"object_type": "device-port", "object_id": pz["id"]},
        },
    )
    assert cab.status_code == 200, cab.text
    return site["id"], cab.json()["id"]


def test_fiber_bundle_does_not_invent_count_or_pairs() -> None:
    app = create_app()
    with TestClient(app) as client:
        _site_id, cable_id = _fiber_cable(client, "site-23-bun")
        s1 = client.post(f"/api/v1/dcim/cables/{cable_id}/strands", json={"position": 1, "label": "blue"}).json()
        s2 = client.post(f"/api/v1/dcim/cables/{cable_id}/strands", json={"position": 2, "label": "orange"}).json()
        created = client.post(
            f"/api/v1/dcim/cables/{cable_id}/bundles",
            json={"name": "Tube blue", "pair_count": 6, "strand_count": 12, "color": "blue"},
        )
        assert created.status_code == 200, created.text
        body = created.json()
        assert body["name"] == "Tube blue"
        assert body["slug"] == "tube-blue"
        assert body["members"] == []
        assert "strand_count" not in body
        assert "pair_count" not in body
        listed = client.get(f"/api/v1/dcim/cables/{cable_id}/bundles").json()
        assert [b["slug"] for b in listed] == ["tube-blue"]
        bound = client.post(
            f"/api/v1/dcim/fiber-bundles/{body['id']}/members",
            json={"strand_id": s1["id"], "role": "tx"},
        )
        assert bound.status_code == 200, bound.text
        assert [m["position"] for m in bound.json()["members"]] == [1]
        assert bound.json()["members"][0]["label"] == "blue"
        again = client.post(
            f"/api/v1/dcim/fiber-bundles/{body['id']}/members",
            json={"strand_id": s1["id"]},
        )
        assert again.status_code == 409
        assert again.json()["detail"] == "fiber_bundle_member_taken"
        other = client.post(f"/api/v1/dcim/cables/{cable_id}/bundles", json={"name": "Other"})
        assert other.status_code == 200, other.text
        stolen = client.post(
            f"/api/v1/dcim/fiber-bundles/{other.json()['id']}/members",
            json={"strand_id": s1["id"]},
        )
        assert stolen.status_code == 409
        second = client.post(
            f"/api/v1/dcim/fiber-bundles/{body['id']}/members",
            json={"strand_id": s2["id"]},
        )
        assert second.status_code == 200, second.text
        assert [m["position"] for m in second.json()["members"]] == [1, 2]
        assert client.delete(f"/api/v1/dcim/fiber-bundle-members/{second.json()['members'][1]['id']}").status_code == 204
        after = client.get(f"/api/v1/dcim/fiber-bundles/{body['id']}").json()
        assert [m["position"] for m in after["members"]] == [1]
        assert client.delete(f"/api/v1/dcim/fiber-bundles/{body['id']}").status_code == 204
        remaining = client.get(f"/api/v1/dcim/cables/{cable_id}/bundles").json()
        assert [b["slug"] for b in remaining] == ["other"]
        assert remaining[0]["members"] == []


def test_fiber_bundle_rejects_copper_and_foreign_strand() -> None:
    app = create_app()
    with TestClient(app) as client:
        _site_id, copper_id = _fiber_cable(client, "site-23-cat6", cable_type="cat6")
        rejected = client.post(f"/api/v1/dcim/cables/{copper_id}/bundles", json={"name": "Pair"})
        assert rejected.status_code == 400
        assert rejected.json()["detail"] == "kabelen er ikke fiber"
        _site_a, fiber_a = _fiber_cable(client, "site-23-a")
        _site_b, fiber_b = _fiber_cable(client, "site-23-b")
        foreign = client.post(f"/api/v1/dcim/cables/{fiber_b}/strands", json={"position": 1}).json()
        bun = client.post(f"/api/v1/dcim/cables/{fiber_a}/bundles", json={"name": "Local"}).json()
        cross = client.post(
            f"/api/v1/dcim/fiber-bundles/{bun['id']}/members",
            json={"strand_id": foreign["id"]},
        )
        assert cross.status_code == 400
        assert cross.json()["detail"] == "strengen tilhører en annen kabel"
        missing = client.post(
            f"/api/v1/dcim/fiber-bundles/{bun['id']}/members",
            json={"strand_id": 999999},
        )
        assert missing.status_code == 404


def test_federation_exports_fiber_bundle_by_cable_slug() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Bun Fed", "slug": "bun-23-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "bun-23-fed-oslo", "slug": "bun-23-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        a = client.post("/api/v1/dcim/devices", json={"name": "bun-23-a", "site_id": site["id"]}).json()
        z = client.post("/api/v1/dcim/devices", json={"name": "bun-23-z", "site_id": site["id"]}).json()
        pa = client.post(f"/api/v1/dcim/devices/{a['id']}/ports", json={"kind": "front-port", "name": "P1"}).json()
        pz = client.post(f"/api/v1/dcim/devices/{z['id']}/ports", json={"kind": "front-port", "name": "P1"}).json()
        cab = client.post(
            "/api/v1/dcim/cables",
            json={
                "site_id": site["id"],
                "name": "Dark OS2",
                "slug": "cab-23-os2",
                "cable_type": "sm-os2",
                "a": {"object_type": "device-port", "object_id": pa["id"]},
                "z": {"object_type": "device-port", "object_id": pz["id"]},
            },
        )
        assert cab.status_code == 200, cab.text
        s1 = client.post(f"/api/v1/dcim/cables/{cab.json()['id']}/strands", json={"position": 1, "label": "blue"})
        assert s1.status_code == 200, s1.text
        bun = client.post(f"/api/v1/dcim/cables/{cab.json()['id']}/bundles", json={"name": "Tube blue", "slug": "tube-blue"})
        assert bun.status_code == 200, bun.text
        bound = client.post(
            f"/api/v1/dcim/fiber-bundles/{bun.json()['id']}/members",
            json={"strand_id": s1.json()["id"]},
        )
        assert bound.status_code == 200, bound.text
        snap = client.get("/api/v1/federation/tenants/bun-23-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        assert isinstance(doc["fiber_bundles"], list)
        match = next(b for b in doc["fiber_bundles"] if b["cable_slug"] == "cab-23-os2")
        assert match["slug"] == "tube-blue"
        assert match["strand_positions"] == [1]
        assert "pair_count" not in match
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 23", "slug": "rep-23-bun"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-23-bun", "name": "Rep 23", "description": None},
            "sites": [{"slug": "site-23-rep", "name": "Rep site", "description": None}],
            "rooms": [],
            "racks": [],
            "manufacturers": [],
            "device_types": [],
            "device_models": [],
            "device_roles": [],
            "devices": [
                {"name": "bun-23-rep-a", "site_slug": "site-23-rep"},
                {"name": "bun-23-rep-z", "site_slug": "site-23-rep"},
            ],
            "device_artifacts": [],
            "device_artifact_records": [],
            "placements": [],
            "device_ports": [
                {"device_name": "bun-23-rep-a", "kind": "front-port", "name": "P1"},
                {"device_name": "bun-23-rep-z", "kind": "front-port", "name": "P1"},
            ],
            "cables": [
                {
                    "site_slug": "site-23-rep",
                    "name": "Dark OS2",
                    "slug": "cab-23-os2",
                    "cable_type": "sm-os2",
                    "status": "connected",
                    "terminations": [
                        {
                            "end": "a",
                            "object_type": "device-port",
                            "device_name": "bun-23-rep-a",
                            "port_kind": "front-port",
                            "port_name": "P1",
                        },
                        {
                            "end": "z",
                            "object_type": "device-port",
                            "device_name": "bun-23-rep-z",
                            "port_kind": "front-port",
                            "port_name": "P1",
                        },
                    ],
                }
            ],
            "fiber_strands": [
                {
                    "site_slug": "site-23-rep",
                    "cable_slug": "cab-23-os2",
                    "position": 1,
                    "label": "blue",
                    "status": "unused",
                }
            ],
            "fiber_bundles": [
                {
                    "site_slug": "site-23-rep",
                    "cable_slug": "cab-23-os2",
                    "slug": "tube-blue",
                    "name": "Tube blue",
                    "description": None,
                    "strand_positions": [1],
                    "pair_count": 6,
                }
            ],
            "ipam": [],
            "clusters": [],
            "catalog_templates": [],
            "catalog_instances": [],
        }
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, replica)
        finally:
            db.close()
        replica_site = next(s for s in client.get("/api/v1/dcim/sites").json() if s["slug"] == "site-23-rep")
        cables = client.get(f"/api/v1/dcim/cables?site_id={replica_site['id']}").json()
        cable = next(c for c in cables if c["slug"] == "cab-23-os2")
        bundles = client.get(f"/api/v1/dcim/cables/{cable['id']}/bundles").json()
        assert [b["slug"] for b in bundles] == ["tube-blue"]
        assert [m["position"] for m in bundles[0]["members"]] == [1]
        assert "pair_count" not in bundles[0]
