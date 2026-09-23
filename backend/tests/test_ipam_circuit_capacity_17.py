"""Trinn 17: kapasitet, CIR og leverandør-circuit-ID uten observert last."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_circuit_records_cir_without_observed_load() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "CAP 17", "slug": "site-17-cap"}).json()
        prov = client.post("/api/v1/ipam/providers", json={"name": "Fiber", "slug": "prov-17-fiber"}).json()
        other = client.post("/api/v1/ipam/providers", json={"name": "Other", "slug": "prov-17-other"}).json()
        guessed = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-17-BARE",
                "name": "Bare fiber",
                "circuit_type": "fiber",
                "layer": "transport",
                "a_site_id": site["id"],
            },
        )
        assert guessed.status_code == 200, guessed.text
        assert guessed.json()["capacity_mbps"] is None
        assert guessed.json()["cir_mbps"] is None
        assert guessed.json()["provider_circuit_id"] is None
        over = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-17-OVER",
                "name": "Over",
                "circuit_type": "fiber",
                "capacity_mbps": 200,
                "cir_mbps": 1000,
            },
        )
        assert over.status_code == 400
        assert over.json()["detail"]["code"] == "circuit_cir_exceeds_capacity"
        created = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-17-A",
                "name": "Dark",
                "circuit_type": "fiber",
                "layer": "transport",
                "provider_id": prov["id"],
                "provider_circuit_id": "cid-17-dark",
                "capacity_mbps": 1000,
                "cir_mbps": 200,
                "observed_mbps": 180,
                "utilization": 0.18,
                "sla_percent": 99.9,
                "a_site_id": site["id"],
            },
        )
        assert created.status_code == 200, created.text
        body = created.json()
        assert body["provider_circuit_id"] == "cid-17-dark"
        assert body["capacity_mbps"] == 1000
        assert body["cir_mbps"] == 200
        assert "observed" not in body
        assert "utilization" not in body
        assert "sla" not in body
        dup = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-17-DUP",
                "name": "Dup",
                "circuit_type": "fiber",
                "provider_id": prov["id"],
                "provider_circuit_id": "cid-17-dark",
            },
        )
        assert dup.status_code == 409
        assert dup.json()["detail"]["code"] == "provider_circuit_id_conflict"
        other_ok = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-17-OTH",
                "name": "Other cid",
                "circuit_type": "fiber",
                "provider_id": other["id"],
                "provider_circuit_id": "cid-17-dark",
            },
        )
        assert other_ok.status_code == 200, other_ok.text


def test_federation_exports_circuit_rates_and_provider_id() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Cap Fed", "slug": "cap-17-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "cap-17-fed-oslo", "slug": "cap-17-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        prov = client.post("/api/v1/ipam/providers", json={"name": "Fiber", "slug": "prov-17-fed"}).json()
        circ = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-17-FED",
                "name": "Fed fiber",
                "circuit_type": "fiber",
                "layer": "transport",
                "provider_id": prov["id"],
                "provider_circuit_id": "cid-17-fed",
                "capacity_mbps": 10000,
                "cir_mbps": 2000,
                "a_site_id": site["id"],
            },
        )
        assert circ.status_code == 200, circ.text
        snap = client.get("/api/v1/federation/tenants/cap-17-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        circuits = doc["ipam"][0].get("circuits") or []
        match = next(c for c in circuits if c["circuit_number"] == "CIR-17-FED")
        assert match["provider_circuit_id"] == "cid-17-fed"
        assert match["capacity_mbps"] == 10000
        assert match["cir_mbps"] == 2000
        assert "observed" not in match

        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()

        client.post("/api/v1/tenants", json={"name": "Rep 17", "slug": "rep-17-cap"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-17-cap", "name": "Rep 17", "description": None},
            "sites": [{"slug": "site-17-rep", "name": "Rep site", "description": None}],
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
                    "site": {"slug": "site-17-rep", "name": "Rep site"},
                    "vrfs": [],
                    "vlan_groups": [],
                    "vlans": [],
                    "prefixes": [],
                    "ipv4_ranges": [],
                    "addresses": [],
                    "ipv6_prefixes": [],
                    "ipv6_addresses": [],
                    "providers": [{"name": "Fiber", "slug": "prov-17-rep"}],
                    "circuit_groups": [],
                    "contracts": [],
                    "circuits": [
                        {
                            "circuit_number": "CIR-17-REP",
                            "name": "Rep fiber",
                            "circuit_type": "fiber",
                            "layer": "transport",
                            "a_site_slug": "site-17-rep",
                            "provider_slug": "prov-17-rep",
                            "provider_circuit_id": "cid-17-rep",
                            "capacity_mbps": 1000,
                            "cir_mbps": 100,
                        }
                    ],
                    "vpn_services": [],
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
        rep = next(c for c in circuits if c["circuit_number"] == "CIR-17-REP")
        assert rep["provider_circuit_id"] == "cid-17-rep"
        assert rep["capacity_mbps"] == 1000
        assert rep["cir_mbps"] == 100
