"""Trinn 19: samband knyttes til registrert fiberstreng uten par- eller tap-gjetning."""

from fastapi.testclient import TestClient

from app.main import create_app


def _fiber_and_circuit(client: TestClient, slug: str) -> tuple[int, int, int]:
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
    circ = client.post(
        "/api/v1/ipam/circuits",
        json={
            "circuit_number": f"CIR-{slug}",
            "name": "Dark",
            "circuit_type": "fiber",
            "layer": "transport",
            "a_site_id": site["id"],
        },
    )
    assert circ.status_code == 200, circ.text
    return site["id"], circ.json()["id"], strand.json()["id"]


def test_circuit_binds_recorded_strand_without_invented_pair() -> None:
    app = create_app()
    with TestClient(app) as client:
        _site_id, circuit_id, strand_id = _fiber_and_circuit(client, "site-19-bind")
        bound = client.post(
            f"/api/v1/ipam/circuits/{circuit_id}/strands",
            json={"strand_id": strand_id, "pair_count": 12, "loss_db": 0.2, "complete": True},
        )
        assert bound.status_code == 200, bound.text
        body = bound.json()
        assert body["strand_id"] == strand_id
        assert body["position"] == 1
        assert body["label"] == "blue"
        assert body["status"] == "unused"
        assert "loss" not in body
        assert "pair" not in body
        assert "complete" not in body
        strand = client.get(f"/api/v1/dcim/fiber-strands/{strand_id}").json()
        assert strand["status"] == "unused"
        listed = client.get(f"/api/v1/ipam/circuits/{circuit_id}/strands").json()
        assert [b["strand_id"] for b in listed] == [strand_id]
        other = client.post(
            "/api/v1/ipam/circuits",
            json={"circuit_number": "CIR-19-OTH", "name": "Other", "circuit_type": "fiber"},
        ).json()
        taken = client.post(
            f"/api/v1/ipam/circuits/{other['id']}/strands",
            json={"strand_id": strand_id},
        )
        assert taken.status_code == 409
        assert taken.json()["detail"]["code"] == "circuit_strand_taken"
        missing = client.post(
            f"/api/v1/ipam/circuits/{circuit_id}/strands",
            json={"strand_id": 999999},
        )
        assert missing.status_code == 404
        assert client.delete(f"/api/v1/ipam/circuit-strands/{body['id']}").status_code == 204
        assert client.get(f"/api/v1/ipam/circuits/{circuit_id}/strands").json() == []


def test_delete_circuit_or_strand_clears_binding() -> None:
    app = create_app()
    with TestClient(app) as client:
        _site_id, circuit_id, strand_id = _fiber_and_circuit(client, "site-19-del")
        bound = client.post(
            f"/api/v1/ipam/circuits/{circuit_id}/strands",
            json={"strand_id": strand_id},
        )
        assert bound.status_code == 200, bound.text
        assert client.delete(f"/api/v1/ipam/circuits/{circuit_id}").status_code == 204
        assert client.get(f"/api/v1/dcim/fiber-strands/{strand_id}").json()["status"] == "unused"
        _site_id, circuit_id, strand_id = _fiber_and_circuit(client, "site-19-del-s")
        bound = client.post(
            f"/api/v1/ipam/circuits/{circuit_id}/strands",
            json={"strand_id": strand_id},
        )
        assert bound.status_code == 200, bound.text
        assert client.delete(f"/api/v1/dcim/fiber-strands/{strand_id}").status_code == 204
        assert client.get(f"/api/v1/ipam/circuits/{circuit_id}/strands").json() == []


def test_federation_exports_circuit_strand_by_cable_position() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Bind Fed", "slug": "bind-19-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "bind-19-fed-oslo", "slug": "bind-19-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        a = client.post("/api/v1/dcim/devices", json={"name": "bind-19-a", "site_id": site["id"]}).json()
        z = client.post("/api/v1/dcim/devices", json={"name": "bind-19-z", "site_id": site["id"]}).json()
        pa = client.post(f"/api/v1/dcim/devices/{a['id']}/ports", json={"kind": "front-port", "name": "P1"}).json()
        pz = client.post(f"/api/v1/dcim/devices/{z['id']}/ports", json={"kind": "front-port", "name": "P1"}).json()
        cab = client.post(
            "/api/v1/dcim/cables",
            json={
                "site_id": site["id"],
                "name": "Dark OS2",
                "slug": "cab-19-os2",
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
        circ = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "CIR-19-DARK",
                "name": "Dark",
                "circuit_type": "fiber",
                "layer": "transport",
                "a_site_id": site["id"],
            },
        )
        assert circ.status_code == 200, circ.text
        bound = client.post(
            f"/api/v1/ipam/circuits/{circ.json()['id']}/strands",
            json={"strand_id": strand.json()["id"]},
        )
        assert bound.status_code == 200, bound.text
        snap = client.get("/api/v1/federation/tenants/bind-19-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        binds = doc["ipam"][0].get("circuit_strands") or []
        match = next(b for b in binds if b["circuit_number"] == "CIR-19-DARK")
        assert match["cable_slug"] == "cab-19-os2"
        assert match["position"] == 1
        assert "loss" not in match
        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()
        client.post("/api/v1/tenants", json={"name": "Rep 19", "slug": "rep-19-bind"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-19-bind", "name": "Rep 19", "description": None},
            "sites": [{"slug": "site-19-rep", "name": "Rep site", "description": None}],
            "rooms": [],
            "racks": [],
            "manufacturers": [],
            "device_types": [],
            "device_models": [],
            "device_roles": [],
            "devices": [
                {"name": "bind-19-rep-a", "site_slug": "site-19-rep"},
                {"name": "bind-19-rep-z", "site_slug": "site-19-rep"},
            ],
            "device_artifacts": [],
            "device_artifact_records": [],
            "placements": [],
            "device_ports": [
                {"device_name": "bind-19-rep-a", "kind": "front-port", "name": "P1"},
                {"device_name": "bind-19-rep-z", "kind": "front-port", "name": "P1"},
            ],
            "cables": [
                {
                    "site_slug": "site-19-rep",
                    "name": "Dark OS2",
                    "slug": "cab-19-os2",
                    "cable_type": "sm-os2",
                    "status": "connected",
                    "terminations": [
                        {
                            "end": "a",
                            "object_type": "device-port",
                            "device_name": "bind-19-rep-a",
                            "port_kind": "front-port",
                            "port_name": "P1",
                        },
                        {
                            "end": "z",
                            "object_type": "device-port",
                            "device_name": "bind-19-rep-z",
                            "port_kind": "front-port",
                            "port_name": "P1",
                        },
                    ],
                }
            ],
            "fiber_strands": [
                {
                    "site_slug": "site-19-rep",
                    "cable_slug": "cab-19-os2",
                    "position": 1,
                    "label": "blue",
                    "status": "unused",
                }
            ],
            "ipam": [
                {
                    "site": {"slug": "site-19-rep", "name": "Rep site"},
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
                            "circuit_number": "CIR-19-REP",
                            "name": "Rep dark",
                            "circuit_type": "fiber",
                            "layer": "transport",
                            "a_site_slug": "site-19-rep",
                        }
                    ],
                    "circuit_strands": [
                        {
                            "circuit_number": "CIR-19-REP",
                            "site_slug": "site-19-rep",
                            "cable_slug": "cab-19-os2",
                            "position": 1,
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
        rep = next(c for c in circuits if c["circuit_number"] == "CIR-19-REP")
        binds = client.get(f"/api/v1/ipam/circuits/{rep['id']}/strands").json()
        assert [b["position"] for b in binds] == [1]
        assert binds[0]["cable_slug"] == "cab-19-os2"
