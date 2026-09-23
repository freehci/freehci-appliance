"""Trinn 11: IPv4-område/pool som inventory, uten DHCP-tjeneste eller lease."""

from fastapi.testclient import TestClient

from app.core.db import SessionLocal
from app.main import create_app
from app.services import federation as fed_svc


def _site_prefix(client: TestClient, *, site_slug: str, cidr: str, extra: dict | None = None):
    site = client.post("/api/v1/dcim/sites", json={"name": site_slug, "slug": site_slug}).json()
    body = {"site_id": site["id"], "name": site_slug, "cidr": cidr, "slug": site_slug}
    if extra:
        body.update(extra)
    pfx = client.post("/api/v1/ipam/ipv4-prefixes", json=body)
    assert pfx.status_code == 200, pfx.text
    return site, pfx.json()


def test_ipv4_range_crud_rejects_invented_kind() -> None:
    app = create_app()
    with TestClient(app) as client:
        _site, pfx = _site_prefix(client, site_slug="site-11-rng", cidr="10.219.92.0/28")
        bad = client.post(
            f"/api/v1/ipam/ipv4-prefixes/{pfx['id']}/ranges",
            json={
                "name": "lease now",
                "slug": "rng-11-bad",
                "kind": "lease",
                "start_address": "10.219.92.4",
                "end_address": "10.219.92.7",
            },
        )
        assert bad.status_code == 422
        ok = client.post(
            f"/api/v1/ipam/ipv4-prefixes/{pfx['id']}/ranges",
            json={
                "name": "Pool",
                "slug": "rng-11-alloc",
                "kind": "allocation",
                "start_address": "10.219.92.4",
                "end_address": "10.219.92.7",
            },
        )
        assert ok.status_code == 200, ok.text
        body = ok.json()
        assert body["kind"] == "allocation"
        assert body["start_address"] == "10.219.92.4"
        listed = client.get(f"/api/v1/ipam/ipv4-prefixes/{pfx['id']}/ranges").json()
        assert any(r["slug"] == "rng-11-alloc" for r in listed)
        outside = client.post(
            f"/api/v1/ipam/ipv4-prefixes/{pfx['id']}/ranges",
            json={
                "name": "out",
                "slug": "rng-11-out",
                "kind": "other",
                "start_address": "10.219.92.200",
                "end_address": "10.219.92.201",
            },
        )
        assert outside.status_code == 400
        assert outside.json()["detail"]["code"] == "address_outside_prefix"
        overlap = client.post(
            f"/api/v1/ipam/ipv4-prefixes/{pfx['id']}/ranges",
            json={
                "name": "overlap",
                "slug": "rng-11-ovl",
                "kind": "reserved",
                "start_address": "10.219.92.6",
                "end_address": "10.219.92.8",
            },
        )
        assert overlap.status_code == 409
        assert overlap.json()["detail"]["code"] == "range_overlap"
        gone = client.delete(f"/api/v1/ipam/ipv4-ranges/{body['id']}")
        assert gone.status_code == 204
        after = client.get(f"/api/v1/ipam/ipv4-prefixes/{pfx['id']}/ranges").json()
        assert after == []


def test_json_dhcp_range_still_protected() -> None:
    app = create_app()
    with TestClient(app) as client:
        _site, pfx = _site_prefix(
            client,
            site_slug="site-11-rng-json",
            cidr="10.219.93.0/24",
            extra={
                "subnet_services": {
                    "gateway": "10.219.93.1",
                    "dhcp_range": {"start": "10.219.93.100", "end": "10.219.93.200"},
                }
            },
        )
        dhcp = client.post(
            "/api/v1/ipam/ipv4-addresses/ensure",
            json={"ipv4_prefix_id": pfx["id"], "address": "10.219.93.150", "mode": "reserve"},
        )
        assert dhcp.status_code == 409
        assert dhcp.json()["detail"]["code"] == "dhcp_range_protected"
        r = client.post("/api/v1/ipam/ipv4-addresses/request", json={"ipv4_prefix_id": pfx["id"], "mode": "reserve"})
        assert r.status_code == 200, r.text
        assert r.json()["address"] == "10.219.93.2"


def test_first_class_ranges_guide_allocation_without_lease() -> None:
    app = create_app()
    with TestClient(app) as client:
        _site, pfx = _site_prefix(client, site_slug="site-11-rng-alloc", cidr="10.219.92.0/28")
        pid = pfx["id"]
        alloc = client.post(
            f"/api/v1/ipam/ipv4-prefixes/{pid}/ranges",
            json={
                "name": "alloc",
                "slug": "rng-11-pool",
                "kind": "allocation",
                "start_address": "10.219.92.4",
                "end_address": "10.219.92.7",
            },
        )
        assert alloc.status_code == 200, alloc.text
        rsv = client.post(
            f"/api/v1/ipam/ipv4-prefixes/{pid}/ranges",
            json={
                "name": "rsv",
                "slug": "rng-11-rsv",
                "kind": "reserved",
                "start_address": "10.219.92.8",
                "end_address": "10.219.92.9",
            },
        )
        assert rsv.status_code == 200, rsv.text
        dhcp = client.post(
            f"/api/v1/ipam/ipv4-prefixes/{pid}/ranges",
            json={
                "name": "dhcp win",
                "slug": "rng-11-dhcp",
                "kind": "dhcp",
                "start_address": "10.219.92.10",
                "end_address": "10.219.92.12",
            },
        )
        assert dhcp.status_code == 200, dhcp.text

        first = client.post("/api/v1/ipam/ipv4-addresses/request", json={"ipv4_prefix_id": pid, "mode": "reserve"})
        assert first.status_code == 200, first.text
        assert first.json()["address"] == "10.219.92.4"
        second = client.post("/api/v1/ipam/ipv4-addresses/request", json={"ipv4_prefix_id": pid, "mode": "reserve"})
        assert second.json()["address"] == "10.219.92.5"

        explicit_rsv = client.post(
            "/api/v1/ipam/ipv4-addresses/ensure",
            json={"ipv4_prefix_id": pid, "address": "10.219.92.8", "mode": "reserve"},
        )
        assert explicit_rsv.status_code == 200, explicit_rsv.text

        blocked = client.post(
            "/api/v1/ipam/ipv4-addresses/ensure",
            json={"ipv4_prefix_id": pid, "address": "10.219.92.10", "mode": "reserve"},
        )
        assert blocked.status_code == 409
        assert blocked.json()["detail"]["code"] == "dhcp_range_protected"
        ok_dhcp = client.post(
            "/api/v1/ipam/ipv4-addresses/ensure",
            json={"ipv4_prefix_id": pid, "address": "10.219.92.10", "mode": "reserve", "role": "dhcp"},
        )
        assert ok_dhcp.status_code == 200, ok_dhcp.text


def test_ipv4_range_federation_export_apply() -> None:
    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Fed 11", "slug": "fed-11-rng"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "Fed 11 site", "slug": "site-11-fed", "tenant_id": tenant["id"]},
        ).json()
        pfx = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": site["id"], "name": "fed-11", "cidr": "10.219.94.0/29", "slug": "px-11-fed"},
        ).json()
        rng = client.post(
            f"/api/v1/ipam/ipv4-prefixes/{pfx['id']}/ranges",
            json={
                "name": "fed pool",
                "slug": "rng-11-fed",
                "kind": "allocation",
                "start_address": "10.219.94.1",
                "end_address": "10.219.94.2",
            },
        )
        assert rng.status_code == 200, rng.text

        exported = client.get(f"/api/v1/ipam/export?site_id={site['id']}")
        assert exported.status_code == 200, exported.text
        assert any(r["slug"] == "rng-11-fed" for r in exported.json().get("ipv4_ranges") or [])

        snap = client.get("/api/v1/federation/tenants/fed-11-rng/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        ranges = doc["ipam"][0].get("ipv4_ranges") or []
        assert any(r["slug"] == "rng-11-fed" and r["prefix_cidr"] == "10.219.94.0/29" for r in ranges)

        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()

        client.post("/api/v1/tenants", json={"name": "Rep 11", "slug": "rep-11-rng"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-11-rng", "name": "Rep 11", "description": None},
            "sites": [{"slug": "site-11-rep", "name": "Rep site", "description": None}],
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
                    "site": {"slug": "site-11-rep", "name": "Rep site"},
                    "vrfs": [],
                    "vlan_groups": [],
                    "vlans": [],
                    "prefixes": [{"cidr": "10.219.95.0/29", "slug": "px-11-rep", "name": "rep-11", "role": "access", "status": "active"}],
                    "ipv4_ranges": [
                        {
                            "prefix_cidr": "10.219.95.0/29",
                            "site_slug": "site-11-rep",
                            "slug": "rng-11-rep",
                            "name": "rep pool",
                            "kind": "allocation",
                            "start_address": "10.219.95.1",
                            "end_address": "10.219.95.2",
                        }
                    ],
                    "addresses": [],
                    "ipv6_prefixes": [],
                    "ipv6_addresses": [],
                    "providers": [],
                    "circuits": [],
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
        sites = client.get("/api/v1/dcim/sites").json()
        rep_site = next(s for s in sites if s["slug"] == "site-11-rep")
        prefixes = client.get(f"/api/v1/ipam/ipv4-prefixes?site_id={rep_site['id']}").json()
        assert prefixes
        listed = client.get(f"/api/v1/ipam/ipv4-prefixes/{prefixes[0]['id']}/ranges").json()
        assert any(r["slug"] == "rng-11-rep" for r in listed)
