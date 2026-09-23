"""Trinn 18: fiberstreng på optisk kabel, uten gjettet antall eller tap."""

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


def test_fiber_strand_recorded_without_loss_or_count() -> None:
    app = create_app()
    with TestClient(app) as client:
        _site_id, cable_id = _fiber_cable(client, "site-18-str")
        created = client.post(
            f"/api/v1/dcim/cables/{cable_id}/strands",
            json={"position": 1, "label": "blue", "loss_db": 0.2, "wavelength_nm": 1310},
        )
        assert created.status_code == 200, created.text
        body = created.json()
        assert body["position"] == 1
        assert body["label"] == "blue"
        assert body["status"] == "unused"
        assert "loss" not in body
        assert "wavelength" not in body
        listed = client.get(f"/api/v1/dcim/cables/{cable_id}/strands").json()
        assert [s["position"] for s in listed] == [1]
        dup = client.post(
            f"/api/v1/dcim/cables/{cable_id}/strands",
            json={"position": 1, "label": "again"},
        )
        assert dup.status_code == 409
        assert dup.json()["detail"] == "fiberposisjon finnes allerede"
        zero = client.post(
            f"/api/v1/dcim/cables/{cable_id}/strands",
            json={"position": 0},
        )
        assert zero.status_code == 422
        patched = client.patch(
            f"/api/v1/dcim/fiber-strands/{body['id']}",
            json={"status": "reserved"},
        )
        assert patched.status_code == 200, patched.text
        assert patched.json()["status"] == "reserved"
        assert client.delete(f"/api/v1/dcim/fiber-strands/{body['id']}").status_code == 204
        assert client.get(f"/api/v1/dcim/cables/{cable_id}/strands").json() == []


def test_fiber_strand_rejects_copper_and_survives_cable_delete() -> None:
    app = create_app()
    with TestClient(app) as client:
        _site_id, copper_id = _fiber_cable(client, "site-18-cat6", cable_type="cat6")
        rejected = client.post(
            f"/api/v1/dcim/cables/{copper_id}/strands",
            json={"position": 1},
        )
        assert rejected.status_code == 400
        assert rejected.json()["detail"] == "kabelen er ikke fiber"
        _site_id, fiber_id = _fiber_cable(client, "site-18-del")
        strand = client.post(
            f"/api/v1/dcim/cables/{fiber_id}/strands",
            json={"position": 2, "label": "keep-until-cable"},
        )
        assert strand.status_code == 200, strand.text
        assert client.delete(f"/api/v1/dcim/cables/{fiber_id}").status_code == 204
        assert client.get(f"/api/v1/dcim/fiber-strands/{strand.json()['id']}").status_code == 404


def test_federation_exports_fiber_strand_by_cable_slug() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Str Fed", "slug": "str-18-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "str-18-fed-oslo", "slug": "str-18-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        a = client.post("/api/v1/dcim/devices", json={"name": "str-18-a", "site_id": site["id"]}).json()
        z = client.post("/api/v1/dcim/devices", json={"name": "str-18-z", "site_id": site["id"]}).json()
        pa = client.post(f"/api/v1/dcim/devices/{a['id']}/ports", json={"kind": "front-port", "name": "P1"}).json()
        pz = client.post(f"/api/v1/dcim/devices/{z['id']}/ports", json={"kind": "front-port", "name": "P1"}).json()
        cab = client.post(
            "/api/v1/dcim/cables",
            json={
                "site_id": site["id"],
                "name": "Dark OS2",
                "slug": "cab-18-os2",
                "cable_type": "sm-os2",
                "a": {"object_type": "device-port", "object_id": pa["id"]},
                "z": {"object_type": "device-port", "object_id": pz["id"]},
            },
        )
        assert cab.status_code == 200, cab.text
        strand = client.post(
            f"/api/v1/dcim/cables/{cab.json()['id']}/strands",
            json={"position": 1, "label": "blue"},
        )
        assert strand.status_code == 200, strand.text
        snap = client.get("/api/v1/federation/tenants/str-18-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        assert isinstance(doc["fiber_strands"], list)
        match = next(s for s in doc["fiber_strands"] if s["cable_slug"] == "cab-18-os2")
        assert match["position"] == 1
        assert match["label"] == "blue"
        assert match["status"] == "unused"
        assert "loss" not in match
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 18", "slug": "rep-18-str"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-18-str", "name": "Rep 18", "description": None},
            "sites": [{"slug": "site-18-rep", "name": "Rep site", "description": None}],
            "rooms": [],
            "racks": [],
            "manufacturers": [],
            "device_types": [],
            "device_models": [],
            "device_roles": [],
            "devices": [
                {"name": "str-18-rep-a", "site_slug": "site-18-rep"},
                {"name": "str-18-rep-z", "site_slug": "site-18-rep"},
            ],
            "device_artifacts": [],
            "device_artifact_records": [],
            "placements": [],
            "device_ports": [
                {"device_name": "str-18-rep-a", "kind": "front-port", "name": "P1"},
                {"device_name": "str-18-rep-z", "kind": "front-port", "name": "P1"},
            ],
            "cables": [
                {
                    "site_slug": "site-18-rep",
                    "name": "Dark OS2",
                    "slug": "cab-18-os2",
                    "cable_type": "sm-os2",
                    "status": "connected",
                    "terminations": [
                        {
                            "end": "a",
                            "object_type": "device-port",
                            "device_name": "str-18-rep-a",
                            "port_kind": "front-port",
                            "port_name": "P1",
                        },
                        {
                            "end": "z",
                            "object_type": "device-port",
                            "device_name": "str-18-rep-z",
                            "port_kind": "front-port",
                            "port_name": "P1",
                        },
                    ],
                }
            ],
            "fiber_strands": [
                {
                    "site_slug": "site-18-rep",
                    "cable_slug": "cab-18-os2",
                    "position": 1,
                    "label": "blue",
                    "status": "unused",
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
        replica_site = next(s for s in client.get("/api/v1/dcim/sites").json() if s["slug"] == "site-18-rep")
        cables = client.get(f"/api/v1/dcim/cables?site_id={replica_site['id']}").json()
        cable = next(c for c in cables if c["slug"] == "cab-18-os2")
        strands = client.get(f"/api/v1/dcim/cables/{cable['id']}/strands").json()
        assert [s["position"] for s in strands] == [1]
        assert strands[0]["label"] == "blue"
