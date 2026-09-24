"""Trinn 28: sambands-eierskap uten gjetning fra type, leverandør eller is_leased=false."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_circuit_ownership_not_inferred_from_type_or_provider() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "OWN 28", "slug": "site-28-own"}).json()
        prov = client.post("/api/v1/ipam/providers", json={"name": "Telenor 28", "slug": "prov-28-own"}).json()
        bare = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-28-BARE",
                "name": "Bare",
                "circuit_type": "leased_line",
                "layer": "transport",
                "provider_id": prov["id"],
                "a_site_id": site["id"],
                "is_leased": False,
            },
        )
        assert bare.status_code == 200, bare.text
        body = bare.json()
        assert body["ownership"] is None
        assert body["is_leased"] is False
        assert body["circuit_type"] == "leased_line"
        assert body["provider_id"] == prov["id"]
        bad = client.post(
            "/api/v1/ipam/circuits",
            json={"circuit_number": "CIR-28-BAD", "name": "Bad", "circuit_type": "fiber", "ownership": "shared"},
        )
        assert bad.status_code == 422
        legacy = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-28-LEG",
                "name": "Legacy",
                "circuit_type": "fiber",
                "is_leased": True,
            },
        )
        assert legacy.status_code == 200, legacy.text
        assert legacy.json()["ownership"] == "leased"
        assert legacy.json()["is_leased"] is True
        owned = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-28-OWN",
                "name": "Dark own",
                "circuit_type": "fiber",
                "ownership": "owned",
                "provider_id": prov["id"],
            },
        )
        assert owned.status_code == 200, owned.text
        assert owned.json()["ownership"] == "owned"
        assert owned.json()["is_leased"] is False


def test_federation_exports_circuit_ownership() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Own Fed", "slug": "own-28-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "own-28-fed-oslo", "slug": "own-28-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        circ = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-28-FED",
                "name": "Own fiber",
                "circuit_type": "fiber",
                "layer": "transport",
                "ownership": "owned",
                "a_site_id": site["id"],
            },
        )
        assert circ.status_code == 200, circ.text
        snap = client.get("/api/v1/federation/tenants/own-28-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        match = next(c for c in doc["ipam"][0]["circuits"] if c["circuit_number"] == "CIR-28-FED")
        assert match["ownership"] == "owned"
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 28", "slug": "rep-28-own"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-28-own", "name": "Rep 28", "description": None},
            "sites": [{"slug": "site-28-rep", "name": "Rep site", "description": None}],
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
                    "site": {"slug": "site-28-rep", "name": "Rep site"},
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
                            "circuit_number": "CIR-28-REP",
                            "name": "Rep",
                            "circuit_type": "leased_line",
                            "layer": "transport",
                            "a_site_slug": "site-28-rep",
                            "is_leased": False,
                        }
                    ],
                    "circuit_terminations": [],
                    "circuit_strands": [],
                    "vpn_services": [],
                    "vpn_members": [],
                    "tunnels": [],
                    "tunnel_transports": [],
                    "autonomous_systems": [],
                    "as_assignments": [],
                    "bgp_sessions": [],
                    "bgp_instances": [],
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
        rep = next(c for c in circuits if c["circuit_number"] == "CIR-28-REP")
        assert rep["ownership"] is None
        assert rep["circuit_type"] == "leased_line"
