"""Trinn 22: tjenestetype, medium og driftsstatus uten gjetning fra circuit_type."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_fiber_circuit_does_not_invent_medium_or_status() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "ATTR 22", "slug": "site-22-attr"}).json()
        guessed = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-22-BARE",
                "name": "Bare fiber",
                "circuit_type": "fiber",
                "layer": "transport",
                "a_site_id": site["id"],
                "observed_status": "up",
                "wavelength": "1310",
            },
        )
        assert guessed.status_code == 200, guessed.text
        body = guessed.json()
        assert body["circuit_type"] == "fiber"
        assert body["service_type"] is None
        assert body["medium"] is None
        assert body["operational_status"] is None
        assert "observed" not in body
        assert "wavelength" not in body
        bad = client.post(
            "/api/v1/ipam/circuits",
            json={"circuit_number": "CIR-22-BAD", "name": "Bad", "circuit_type": "fiber", "medium": "os2"},
        )
        assert bad.status_code == 422
        created = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-22-DARK",
                "name": "Dark",
                "circuit_type": "fiber",
                "layer": "transport",
                "service_type": "dark-fiber",
                "medium": "fiber",
                "operational_status": "planned",
                "a_site_id": site["id"],
            },
        )
        assert created.status_code == 200, created.text
        out = created.json()
        assert out["service_type"] == "dark-fiber"
        assert out["medium"] == "fiber"
        assert out["operational_status"] == "planned"
        patched = client.patch(
            f"/api/v1/ipam/circuits/{out['id']}",
            json={"operational_status": "active", "observed_status": "up"},
        )
        assert patched.status_code == 200, patched.text
        assert patched.json()["operational_status"] == "active"
        assert patched.json()["medium"] == "fiber"
        assert "observed" not in patched.json()


def test_federation_exports_circuit_attributes() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Attr Fed", "slug": "attr-22-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "attr-22-fed-oslo", "slug": "attr-22-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        circ = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-22-FED",
                "name": "Internet",
                "circuit_type": "fiber",
                "layer": "transport",
                "service_type": "internet",
                "medium": "fiber",
                "operational_status": "active",
                "a_site_id": site["id"],
            },
        )
        assert circ.status_code == 200, circ.text
        snap = client.get("/api/v1/federation/tenants/attr-22-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        match = next(c for c in (doc["ipam"][0].get("circuits") or []) if c["circuit_number"] == "CIR-22-FED")
        assert match["service_type"] == "internet"
        assert match["medium"] == "fiber"
        assert match["operational_status"] == "active"
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 22", "slug": "rep-22-attr"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-22-attr", "name": "Rep 22", "description": None},
            "sites": [{"slug": "site-22-rep", "name": "Rep site", "description": None}],
            "rooms": [],
            "racks": [],
            "manufacturers": [],
            "device_types": [],
            "device_models": [],
            "device_roles": [],
            "devices": [],
            "device_artifacts": [],
            "device_artifact_records": [],
            "placements": [],
            "ipam": [
                {
                    "site": {"slug": "site-22-rep", "name": "Rep site"},
                    "vrfs": [],
                    "vlan_groups": [],
                    "vlans": [],
                    "prefixes": [],
                    "ipv4_ranges": [],
                    "addresses": [],
                    "ipv6_prefixes": [],
                    "ipv6_addresses": [],
                    "providers": [],
                    "circuit_groups": [],
                    "contracts": [],
                    "circuits": [
                        {
                            "circuit_number": "CIR-22-REP",
                            "name": "Rep ethernet",
                            "circuit_type": "fiber",
                            "layer": "transport",
                            "a_site_slug": "site-22-rep",
                            "service_type": "ethernet",
                            "medium": "fiber",
                            "operational_status": "offline",
                        }
                    ],
                    "circuit_strands": [],
                    "vpn_services": [],
                    "vpn_members": [],
                    "tunnels": [],
                    "tunnel_transports": [],
                    "autonomous_systems": [],
                    "as_assignments": [],
                    "bgp_sessions": [],
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
        circuits = client.get("/api/v1/ipam/circuits").json()
        rep = next(c for c in circuits if c["circuit_number"] == "CIR-22-REP")
        assert rep["service_type"] == "ethernet"
        assert rep["medium"] == "fiber"
        assert rep["operational_status"] == "offline"
