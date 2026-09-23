"""Trinn 15: kontrakt er førsteklasses, uten SLA eller oppetid."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_contract_is_first_class_without_sla() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "CTR 15", "slug": "site-15-ctr"}).json()
        other = client.post("/api/v1/ipam/providers", json={"name": "Other", "slug": "prov-15-other"}).json()
        prov = client.post("/api/v1/ipam/providers", json={"name": "Fiber", "slug": "prov-15-fiber"}).json()
        missing = client.post(
            "/api/v1/ipam/contracts",
            json={"provider_id": 99999, "name": "Ghost", "slug": "ctr-15-ghost"},
        )
        assert missing.status_code == 404
        created = client.post(
            "/api/v1/ipam/contracts",
            json={
                "provider_id": prov["id"],
                "name": "Dark fiber 2026",
                "slug": "ctr-15-dark",
                "reference": "AVT-15",
                "starts_on": "2026-01-01",
                "ends_on": "2027-12-31",
                "sla_percent": 99.9,
                "uptime": "99.99",
                "availability": "gold",
            },
        )
        assert created.status_code == 200, created.text
        body = created.json()
        assert body["slug"] == "ctr-15-dark"
        assert body["provider_id"] == prov["id"]
        assert body["reference"] == "AVT-15"
        assert "sla" not in body
        assert "uptime" not in body
        assert "availability" not in body
        dup = client.post(
            "/api/v1/ipam/contracts",
            json={"provider_id": prov["id"], "name": "Dup", "slug": "ctr-15-dark"},
        )
        assert dup.status_code == 409
        other_ok = client.post(
            "/api/v1/ipam/contracts",
            json={"provider_id": other["id"], "name": "Same slug other", "slug": "ctr-15-dark"},
        )
        assert other_ok.status_code == 200, other_ok.text
        inherit = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-15-DARK",
                "name": "Dark",
                "circuit_type": "fiber",
                "layer": "transport",
                "contract_id": body["id"],
                "a_site_id": site["id"],
            },
        )
        assert inherit.status_code == 200, inherit.text
        assert inherit.json()["contract_id"] == body["id"]
        assert inherit.json()["provider_id"] == prov["id"]
        mismatch = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-15-MIS",
                "name": "Mismatch",
                "circuit_type": "fiber",
                "provider_id": other["id"],
                "contract_id": body["id"],
            },
        )
        assert mismatch.status_code == 400
        assert mismatch.json()["detail"]["code"] == "contract_provider_mismatch"
        listed = client.get(f"/api/v1/ipam/contracts?provider_id={prov['id']}").json()
        assert [c["slug"] for c in listed] == ["ctr-15-dark"]
        assert client.delete(f"/api/v1/ipam/contracts/{body['id']}").status_code == 204
        refreshed = client.get("/api/v1/ipam/circuits").json()
        match = next(c for c in refreshed if c["circuit_number"] == "CIR-15-DARK")
        assert match["contract_id"] is None
        assert match["provider_id"] == prov["id"]


def test_federation_exports_contract_by_provider_slug() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Ctr Fed", "slug": "ctr-15-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "ctr-15-fed-oslo", "slug": "ctr-15-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        prov = client.post("/api/v1/ipam/providers", json={"name": "Fiber", "slug": "prov-15-fed"}).json()
        ctr = client.post(
            "/api/v1/ipam/contracts",
            json={"provider_id": prov["id"], "name": "Fed dark", "slug": "ctr-15-fed-dark", "reference": "FED-15"},
        )
        assert ctr.status_code == 200, ctr.text
        circ = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-15-FED",
                "name": "Fed fiber",
                "circuit_type": "fiber",
                "layer": "transport",
                "provider_id": prov["id"],
                "contract_id": ctr.json()["id"],
                "a_site_id": site["id"],
            },
        )
        assert circ.status_code == 200, circ.text
        snap = client.get("/api/v1/federation/tenants/ctr-15-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        contracts = doc["ipam"][0].get("contracts") or []
        assert any(c["slug"] == "ctr-15-fed-dark" and c["provider_slug"] == "prov-15-fed" for c in contracts)
        assert "sla" not in contracts[0]
        circuits = doc["ipam"][0].get("circuits") or []
        assert any(c["circuit_number"] == "CIR-15-FED" and c.get("contract_slug") == "ctr-15-fed-dark" for c in circuits)

        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()

        client.post("/api/v1/tenants", json={"name": "Rep 15", "slug": "rep-15-ctr"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-15-ctr", "name": "Rep 15", "description": None},
            "sites": [{"slug": "site-15-rep", "name": "Rep site", "description": None}],
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
                    "site": {"slug": "site-15-rep", "name": "Rep site"},
                    "vrfs": [],
                    "vlan_groups": [],
                    "vlans": [],
                    "prefixes": [],
                    "ipv4_ranges": [],
                    "addresses": [],
                    "ipv6_prefixes": [],
                    "ipv6_addresses": [],
                    "providers": [{"name": "Fiber", "slug": "prov-15-rep"}],
                    "contracts": [
                        {
                            "name": "Rep dark",
                            "slug": "ctr-15-rep-dark",
                            "provider_slug": "prov-15-rep",
                            "reference": "REP-15",
                        }
                    ],
                    "circuits": [
                        {
                            "circuit_number": "CIR-15-REP",
                            "name": "Rep fiber",
                            "circuit_type": "fiber",
                            "layer": "transport",
                            "a_site_slug": "site-15-rep",
                            "provider_slug": "prov-15-rep",
                            "contract_slug": "ctr-15-rep-dark",
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
        providers = client.get("/api/v1/ipam/providers").json()
        rep_prov = next(p for p in providers if p["slug"] == "prov-15-rep")
        contracts = client.get(f"/api/v1/ipam/contracts?provider_id={rep_prov['id']}").json()
        assert any(c["slug"] == "ctr-15-rep-dark" for c in contracts)
        circuits = client.get("/api/v1/ipam/circuits").json()
        match = next(c for c in circuits if c["circuit_number"] == "CIR-15-REP")
        assert match["contract_id"] == next(c["id"] for c in contracts if c["slug"] == "ctr-15-rep-dark")
        assert match["provider_id"] == rep_prov["id"]
