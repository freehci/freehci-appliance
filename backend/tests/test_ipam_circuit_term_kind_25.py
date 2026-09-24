"""Trinn 25: terminering kind uten gjetning fra manglende enhet eller leverandør."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_termination_kind_not_inferred_from_missing_device_or_provider() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "TERM 25", "slug": "site-25-term"}).json()
        prov = client.post("/api/v1/ipam/providers", json={"name": "Telenor 25", "slug": "prov-25-term"}).json()
        circ = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-25-BARE",
                "name": "Bare",
                "circuit_type": "fiber",
                "layer": "transport",
                "provider_id": prov["id"],
                "a_site_id": site["id"],
            },
        )
        assert circ.status_code == 200, circ.text
        bare = client.post(
            f"/api/v1/ipam/circuits/{circ.json()['id']}/terminations",
            json={"endpoint": "z", "loa": "LOA-1", "cross_connect": True},
        )
        assert bare.status_code == 200, bare.text
        assert bare.json()["kind"] is None
        assert bare.json()["device_id"] is None
        assert "loa" not in bare.json()
        device = client.post("/api/v1/dcim/devices", json={"name": "edge-25", "site_id": site["id"]}).json()
        iface = client.post(f"/api/v1/dcim/devices/{device['id']}/interfaces", json={"name": "xe-0/0/1"}).json()
        local = client.post(
            f"/api/v1/ipam/circuits/{circ.json()['id']}/terminations",
            json={"endpoint": "a", "device_id": device["id"], "interface_id": iface["id"], "site_id": site["id"]},
        )
        assert local.status_code == 200, local.text
        assert local.json()["kind"] is None
        unknown = client.post(
            f"/api/v1/ipam/circuits/{circ.json()['id']}/terminations",
            json={"endpoint": "z", "kind": "unknown", "label": "carrier handoff"},
        )
        assert unknown.status_code == 200, unknown.text
        assert unknown.json()["kind"] == "unknown"
        assert unknown.json()["device_id"] is None
        assert unknown.json()["label"] == "carrier handoff"
        clash = client.post(
            f"/api/v1/ipam/circuits/{circ.json()['id']}/terminations",
            json={"endpoint": "z", "kind": "provider-network", "device_id": device["id"]},
        )
        assert clash.status_code == 400
        assert clash.json()["detail"]["code"] == "circuit_term_kind"
        bad = client.post(
            f"/api/v1/ipam/circuits/{circ.json()['id']}/terminations",
            json={"endpoint": "a", "kind": "demarc"},
        )
        assert bad.status_code == 422


def test_federation_exports_termination_kind_without_invented_device() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Term Fed", "slug": "term-25-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "term-25-fed-oslo", "slug": "term-25-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        circ = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-25-FED",
                "name": "Access",
                "circuit_type": "fiber",
                "layer": "transport",
                "a_site_id": site["id"],
            },
        )
        assert circ.status_code == 200, circ.text
        term = client.post(
            f"/api/v1/ipam/circuits/{circ.json()['id']}/terminations",
            json={"endpoint": "z", "kind": "provider-network", "label": "N1 meet-me"},
        )
        assert term.status_code == 200, term.text
        snap = client.get("/api/v1/federation/tenants/term-25-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        match = next(t for t in (doc["ipam"][0].get("circuit_terminations") or []) if t["endpoint"] == "z")
        assert match["circuit_number"] == "CIR-25-FED"
        assert match["kind"] == "provider-network"
        assert match["device_name"] is None
        assert "loa" not in match
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 25", "slug": "rep-25-term"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-25-term", "name": "Rep 25", "description": None},
            "sites": [{"slug": "site-25-rep", "name": "Rep site", "description": None}],
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
                    "site": {"slug": "site-25-rep", "name": "Rep site"},
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
                            "circuit_number": "CIR-25-REP",
                            "name": "Rep",
                            "circuit_type": "fiber",
                            "layer": "transport",
                            "a_site_slug": "site-25-rep",
                        }
                    ],
                    "circuit_terminations": [
                        {
                            "circuit_number": "CIR-25-REP",
                            "endpoint": "z",
                            "kind": "unknown",
                            "label": "far end",
                            "device_name": None,
                            "loa": "x",
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
        rep = next(c for c in circuits if c["circuit_number"] == "CIR-25-REP")
        terms = client.get(f"/api/v1/ipam/circuits/{rep['id']}/terminations").json()
        assert terms[0]["kind"] == "unknown"
        assert terms[0]["device_id"] is None
        assert terms[0]["label"] == "far end"
        devices = client.get("/api/v1/dcim/devices").json()
        assert all(d["name"] != "far end" for d in devices)
