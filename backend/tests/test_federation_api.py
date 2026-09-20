"""Federation: paring, skrivesteng, snapshot/apply og promote."""

from uuid import uuid4

from fastapi.testclient import TestClient

from sqlalchemy import select

from app.core.db import SessionLocal
from app.main import create_app
from app.models.federation import FederationTenantRole
from app.services import federation as fed_svc


def _client() -> TestClient:
    return TestClient(create_app())


def test_hello_and_pairing_accept() -> None:
    with _client() as client:
        hello = client.get("/api/v1/federation/hello")
        assert hello.status_code == 200, hello.text
        local_uuid = hello.json()["instance_uuid"]
        assert local_uuid

        pair = client.post("/api/v1/federation/pairing-tokens")
        assert pair.status_code == 200, pair.text
        token = pair.json()["token"]
        assert token.startswith("fhpair_")

        self_peer = client.post(
            "/api/v1/federation/accept-peer",
            json={
                "pairing_token": token,
                "instance_uuid": local_uuid,
                "name": "self",
                "base_url": "http://127.0.0.1:9",
            },
        )
        assert self_peer.status_code == 400

        pair2 = client.post("/api/v1/federation/pairing-tokens")
        accepted = client.post(
            "/api/v1/federation/accept-peer",
            json={
                "pairing_token": pair2.json()["token"],
                "instance_uuid": str(uuid4()),
                "name": "replica-b",
                "base_url": "http://192.0.2.10:8080",
            },
        )
        assert accepted.status_code == 200, accepted.text
        body = accepted.json()
        assert body["instance_uuid"] == local_uuid
        assert body["token"].startswith("fhci_")

        status = client.get("/api/v1/federation/status")
        assert status.status_code == 200
        assert any(p["name"] == "replica-b" for p in status.json()["peers"])


def test_write_fence_and_freeze() -> None:
    with _client() as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Fence Co", "slug": "fence-co"})
        assert tenant.status_code == 200, tenant.text
        tid = tenant.json()["id"]
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "fence-site", "slug": "fence-site", "tenant_id": tid},
        )
        assert site.status_code == 200, site.text
        sid = site.json()["id"]

        pair = client.post("/api/v1/federation/pairing-tokens")
        client.post(
            "/api/v1/federation/accept-peer",
            json={
                "pairing_token": pair.json()["token"],
                "instance_uuid": str(uuid4()),
                "name": "other",
                "base_url": "http://192.0.2.20:8080",
            },
        )

        db = SessionLocal()
        try:
            role = db.execute(select(FederationTenantRole).where(FederationTenantRole.tenant_id == tid)).scalar_one()
            role.primary_instance_uuid = "00000000-0000-0000-0000-000000000099"
            db.commit()
        finally:
            db.close()

        blocked = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sid, "name": "LAN", "cidr": "10.66.1.0/24"},
        )
        assert blocked.status_code == 409, blocked.text
        assert blocked.json()["detail"]["code"] == "tenant_not_primary"

        listed = client.get("/api/v1/ipam/ipv4-prefixes", params={"site_id": sid})
        assert listed.status_code == 200

        db = SessionLocal()
        try:
            local = fed_svc.local_instance(db)
            role = db.execute(select(FederationTenantRole).where(FederationTenantRole.tenant_id == tid)).scalar_one()
            role.primary_instance_uuid = local.instance_uuid
            role.frozen = True
            db.commit()
        finally:
            db.close()

        frozen = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sid, "name": "LAN", "cidr": "10.66.2.0/24"},
        )
        assert frozen.status_code == 409, frozen.text
        assert frozen.json()["detail"]["code"] == "tenant_frozen"


def test_snapshot_apply_and_promote_checksum() -> None:
    with _client() as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Snap Co", "slug": "snap-co"})
        tid = tenant.json()["id"]
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "snap-oslo", "slug": "snap-oslo", "tenant_id": tid, "city": "Oslo"},
        )
        sid = site.json()["id"]
        room = client.post("/api/v1/dcim/rooms", json={"site_id": sid, "name": "R1"})
        rid = room.json()["id"]
        client.post("/api/v1/dcim/racks", json={"room_id": rid, "name": "RACK-1", "u_height": 15})
        pfx = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sid, "name": "LAN", "cidr": "10.77.1.0/24", "slug": "snap-lan", "role": "active"},
        )
        assert pfx.status_code == 200, pfx.text

        snap = client.get("/api/v1/federation/tenants/snap-co/snapshot")
        assert snap.status_code == 200, snap.text
        body = snap.json()
        assert body["kind"] == "TenantInventory"
        assert body["checksum"]
        doc = body["document"]
        assert doc["tenant"]["slug"] == "snap-co"
        assert doc["sites"][0]["slug"] == "snap-oslo"
        assert "id" not in doc["sites"][0]
        assert doc["racks"][0]["name"] == "RACK-1"
        assert doc["ipam"][0]["prefixes"][0]["cidr"] == "10.77.1.0/24"
        assert doc["ipam"][0]["prefixes"][0]["site_slug"] == "snap-oslo"
        again = client.get("/api/v1/federation/tenants/snap-co/snapshot")
        assert again.json()["checksum"] == body["checksum"]

        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == body["checksum"]
            tenant_row = fed_svc._tenant_by_slug(db, "snap-co")
            result = fed_svc.promote_if_match(db, tenant_row, remote_checksum=checksum, remote_frozen=True)
            assert result.match is True
            local = fed_svc.local_instance(db)
            assert result.primary_instance_uuid == local.instance_uuid

            miss = fed_svc.promote_if_match(db, tenant_row, remote_checksum="0" * 64, remote_frozen=True)
            assert miss.match is False

            cons = client.get("/api/v1/federation/tenants/snap-co/consistency")
            assert cons.status_code == 200
            assert cons.json()["checksum"] == checksum
        finally:
            db.close()
