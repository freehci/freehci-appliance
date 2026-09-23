"""Trinn 16: redundansgruppe knytter samband uten å påstå uavhengighet."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_circuit_group_records_shared_risk_not_independence() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "GRP 16", "slug": "site-16-grp"}).json()
        tenant_a = client.post("/api/v1/tenants", json={"name": "Grp A", "slug": "tn-16-a"}).json()
        tenant_b = client.post("/api/v1/tenants", json={"name": "Grp B", "slug": "tn-16-b"}).json()
        created = client.post(
            "/api/v1/ipam/circuit-groups",
            json={
                "name": "Metro ring",
                "slug": "grp-16-metro",
                "shared_risk": "samme grøft mot Eggkleiva",
                "independent": True,
                "diverse": True,
                "failover_percent": 99.9,
            },
        )
        assert created.status_code == 200, created.text
        body = created.json()
        assert body["slug"] == "grp-16-metro"
        assert body["shared_risk"] == "samme grøft mot Eggkleiva"
        assert "independent" not in body
        assert "diverse" not in body
        assert "failover" not in body
        dup = client.post(
            "/api/v1/ipam/circuit-groups",
            json={"name": "Dup", "slug": "grp-16-metro"},
        )
        assert dup.status_code == 409
        scoped = client.post(
            "/api/v1/ipam/circuit-groups",
            json={"name": "Tenant A", "slug": "grp-16-metro", "tenant_id": tenant_a["id"]},
        )
        assert scoped.status_code == 200, scoped.text
        pri = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-16-PRI",
                "name": "Primary",
                "circuit_type": "fiber",
                "layer": "transport",
                "group_id": body["id"],
                "a_site_id": site["id"],
            },
        )
        assert pri.status_code == 200, pri.text
        assert pri.json()["group_id"] == body["id"]
        sec = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-16-SEC",
                "name": "Secondary",
                "circuit_type": "fiber",
                "layer": "transport",
                "group_id": body["id"],
                "a_site_id": site["id"],
            },
        )
        assert sec.status_code == 200, sec.text
        mismatch = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-16-MIS",
                "name": "Wrong tenant",
                "circuit_type": "fiber",
                "tenant_id": tenant_b["id"],
                "group_id": scoped.json()["id"],
            },
        )
        assert mismatch.status_code == 400
        assert mismatch.json()["detail"]["code"] == "circuit_group_tenant_mismatch"
        listed = client.get(f"/api/v1/ipam/circuits?group_id={body['id']}").json()
        assert {c["circuit_number"] for c in listed} == {"CIR-16-PRI", "CIR-16-SEC"}
        assert client.delete(f"/api/v1/ipam/circuit-groups/{body['id']}").status_code == 204
        refreshed = client.get("/api/v1/ipam/circuits").json()
        for number in ("CIR-16-PRI", "CIR-16-SEC"):
            match = next(c for c in refreshed if c["circuit_number"] == number)
            assert match["group_id"] is None


def test_federation_exports_circuit_group_by_slug() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Grp Fed", "slug": "grp-16-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "grp-16-fed-oslo", "slug": "grp-16-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        grp = client.post(
            "/api/v1/ipam/circuit-groups",
            json={"name": "Fed metro", "slug": "grp-16-fed-metro", "shared_risk": "felles mast"},
        )
        assert grp.status_code == 200, grp.text
        circ = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-16-FED",
                "name": "Fed fiber",
                "circuit_type": "fiber",
                "layer": "transport",
                "group_id": grp.json()["id"],
                "a_site_id": site["id"],
            },
        )
        assert circ.status_code == 200, circ.text
        snap = client.get("/api/v1/federation/tenants/grp-16-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        groups = doc["ipam"][0].get("circuit_groups") or []
        assert any(g["slug"] == "grp-16-fed-metro" and g["shared_risk"] == "felles mast" for g in groups)
        assert "independent" not in groups[0]
        circuits = doc["ipam"][0].get("circuits") or []
        assert any(c["circuit_number"] == "CIR-16-FED" and c.get("group_slug") == "grp-16-fed-metro" for c in circuits)

        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()

        client.post("/api/v1/tenants", json={"name": "Rep 16", "slug": "rep-16-grp"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-16-grp", "name": "Rep 16", "description": None},
            "sites": [{"slug": "site-16-rep", "name": "Rep site", "description": None}],
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
                    "site": {"slug": "site-16-rep", "name": "Rep site"},
                    "vrfs": [],
                    "vlan_groups": [],
                    "vlans": [],
                    "prefixes": [],
                    "ipv4_ranges": [],
                    "addresses": [],
                    "ipv6_prefixes": [],
                    "ipv6_addresses": [],
                    "providers": [],
                    "circuit_groups": [
                        {"name": "Rep metro", "slug": "grp-16-rep-metro", "shared_risk": "samme kulvert"}
                    ],
                    "contracts": [],
                    "circuits": [
                        {
                            "circuit_number": "CIR-16-REP",
                            "name": "Rep fiber",
                            "circuit_type": "fiber",
                            "layer": "transport",
                            "a_site_slug": "site-16-rep",
                            "group_slug": "grp-16-rep-metro",
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
        groups = client.get("/api/v1/ipam/circuit-groups").json()
        rep = next(g for g in groups if g["slug"] == "grp-16-rep-metro")
        circuits = client.get(f"/api/v1/ipam/circuits?group_id={rep['id']}").json()
        assert any(c["circuit_number"] == "CIR-16-REP" for c in circuits)
