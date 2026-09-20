"""Trinn 2c: AS, tilordning per rutingsdomene, én BGP-sesjon for flere AF."""

from fastapi.testclient import TestClient

from app.core.asn import is_private_asn, normalize_asn
from app.main import create_app


def test_normalize_asn() -> None:
    assert normalize_asn(65000) == 65000
    assert normalize_asn(4_200_000_001) == 4_200_000_001
    assert is_private_asn(65000) is True
    assert is_private_asn(15169) is False
    try:
        normalize_asn(0)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_public_asn_unique_private_per_tenant() -> None:
    app = create_app()
    with TestClient(app) as client:
        t1 = client.post("/api/v1/tenants", json={"name": "T1", "slug": "t1-as"}).json()
        t2 = client.post("/api/v1/tenants", json={"name": "T2", "slug": "t2-as"}).json()
        pub = client.post("/api/v1/ipam/autonomous-systems", json={"asn": 64496, "name": "Doc AS"})
        assert pub.status_code == 200, pub.text
        assert pub.json()["is_private"] is False
        dup = client.post("/api/v1/ipam/autonomous-systems", json={"asn": 64496, "name": "Dup"})
        assert dup.status_code == 409
        a = client.post(
            "/api/v1/ipam/autonomous-systems",
            json={"asn": 65021, "name": "Priv A", "tenant_id": t1["id"]},
        )
        b = client.post(
            "/api/v1/ipam/autonomous-systems",
            json={"asn": 65021, "name": "Priv B", "tenant_id": t2["id"]},
        )
        assert a.status_code == 200, a.text
        assert b.status_code == 200, b.text
        assert a.json()["is_private"] is True
        same = client.post(
            "/api/v1/ipam/autonomous-systems",
            json={"asn": 65021, "name": "Priv A2", "tenant_id": t1["id"]},
        )
        assert same.status_code == 409


def test_as_assignment_unique_per_site_vrf() -> None:
    app = create_app()
    with TestClient(app) as client:
        s1 = client.post("/api/v1/dcim/sites", json={"name": "S1", "slug": "as-s1"}).json()
        s2 = client.post("/api/v1/dcim/sites", json={"name": "S2", "slug": "as-s2"}).json()
        asys = client.post("/api/v1/ipam/autonomous-systems", json={"asn": 65022, "name": "Lab AS"}).json()
        vrf = client.post("/api/v1/ipam/vrfs", json={"site_id": s1["id"], "name": "underlay"}).json()
        a1 = client.post(
            "/api/v1/ipam/as-assignments",
            json={"autonomous_system_id": asys["id"], "site_id": s1["id"]},
        )
        assert a1.status_code == 200, a1.text
        a2 = client.post(
            "/api/v1/ipam/as-assignments",
            json={"autonomous_system_id": asys["id"], "site_id": s2["id"]},
        )
        assert a2.status_code == 200, a2.text
        dup = client.post(
            "/api/v1/ipam/as-assignments",
            json={"autonomous_system_id": asys["id"], "site_id": s1["id"]},
        )
        assert dup.status_code == 409
        other_vrf = client.post(
            "/api/v1/ipam/as-assignments",
            json={"autonomous_system_id": asys["id"], "site_id": s1["id"], "vrf_id": vrf["id"]},
        )
        assert other_vrf.status_code == 200, other_vrf.text


def test_bgp_one_session_two_families_no_invented_observed() -> None:
    app = create_app()
    with TestClient(app) as client:
        site = client.post("/api/v1/dcim/sites", json={"name": "Edge", "slug": "bgp-edge"}).json()
        local = client.post("/api/v1/ipam/autonomous-systems", json={"asn": 65023, "name": "Local"}).json()
        sess = client.post(
            "/api/v1/ipam/bgp-sessions",
            json={
                "site_id": site["id"],
                "local_as_id": local["id"],
                "remote_asn": 65024,
                "peer_ip": "192.0.2.1",
                "address_families": ["ipv4-unicast", "ipv6-unicast"],
            },
        )
        assert sess.status_code == 200, sess.text
        body = sess.json()
        assert body["remote_asn"] == 65024
        assert body["address_families"] == ["ipv4-unicast", "ipv6-unicast"]
        assert body["desired_status"] == "planned"
        assert body["observed_status"] is None
        dup = client.post(
            "/api/v1/ipam/bgp-sessions",
            json={
                "site_id": site["id"],
                "local_as_id": local["id"],
                "remote_asn": 65024,
                "peer_ip": "192.0.2.1",
                "address_families": ["ipv6-unicast"],
            },
        )
        assert dup.status_code == 409
        listed = client.get(f"/api/v1/ipam/bgp-sessions?site_id={site['id']}").json()
        assert len(listed) == 1


def test_four_byte_private_asn_persists() -> None:
    app = create_app()
    with TestClient(app) as client:
        row = client.post(
            "/api/v1/ipam/autonomous-systems",
            json={"asn": 4_200_000_001, "name": "4byte priv"},
        )
        assert row.status_code == 200, row.text
        assert row.json()["asn"] == 4_200_000_001
        assert row.json()["is_private"] is True


def test_federation_snapshot_includes_as_and_bgp() -> None:
    from app.core.db import SessionLocal
    from app.services import federation as fed_svc

    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "AS Fed", "slug": "as-fed"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "as-fed-oslo", "slug": "as-fed-oslo", "tenant_id": tenant["id"]},
        ).json()
        local = client.post(
            "/api/v1/ipam/autonomous-systems",
            json={"asn": 65025, "name": "Fed Local", "tenant_id": tenant["id"]},
        ).json()
        assigned = client.post(
            "/api/v1/ipam/as-assignments",
            json={"autonomous_system_id": local["id"], "site_id": site["id"]},
        )
        assert assigned.status_code == 200, assigned.text
        sess = client.post(
            "/api/v1/ipam/bgp-sessions",
            json={
                "site_id": site["id"],
                "local_as_id": local["id"],
                "remote_asn": 65026,
                "peer_ip": "192.0.2.8",
                "address_families": ["ipv4-unicast", "ipv6-unicast"],
                "name": "edge-peer",
            },
        )
        assert sess.status_code == 200, sess.text

        snap = client.get("/api/v1/federation/tenants/as-fed/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        ipam = doc["ipam"][0]
        assert any(a["asn"] == 65025 for a in ipam["autonomous_systems"])
        assert any(x["asn"] == 65025 for x in ipam["as_assignments"])
        bgp = ipam["bgp_sessions"][0]
        assert bgp["peer_ip"] == "192.0.2.8"
        assert bgp["remote_asn"] == 65026
        assert bgp["address_families"] == ["ipv4-unicast", "ipv6-unicast"]
        assert "observed_status" not in bgp

        doc["tenant"] = {"slug": "as-fed-replica", "name": "AS Fed Replica", "description": None}
        doc["sites"][0]["slug"] = "as-fed-replica-oslo"
        ipam["site"]["slug"] = "as-fed-replica-oslo"
        for x in ipam["as_assignments"]:
            x["site_slug"] = "as-fed-replica-oslo"
        for s in ipam["bgp_sessions"]:
            s["site_slug"] = "as-fed-replica-oslo"

        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, doc)
        finally:
            db.close()

        replica = next(s for s in client.get("/api/v1/dcim/sites").json() if s["slug"] == "as-fed-replica-oslo")
        copied = client.get(f"/api/v1/ipam/bgp-sessions?site_id={replica['id']}").json()
        assert len(copied) == 1
        assert copied[0]["remote_asn"] == 65026
        assert copied[0]["address_families"] == ["ipv4-unicast", "ipv6-unicast"]
        assert copied[0]["observed_status"] is None
        assigns = client.get(f"/api/v1/ipam/as-assignments?site_id={replica['id']}").json()
        assert len(assigns) == 1
        assert assigns[0]["asn"] == 65025
