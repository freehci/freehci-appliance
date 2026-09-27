"""Trinn 48: IPv6-område som inventory, uten DHCP, lease eller gjettet ledig-CIDR."""

from fastapi.testclient import TestClient

from app.core.db import SessionLocal
from app.main import create_app
from app.services import federation as fed_svc


def _site_prefix(client: TestClient, *, site_slug: str, cidr: str):
    site = client.post("/api/v1/dcim/sites", json={"name": site_slug, "slug": site_slug}).json()
    pfx = client.post(
        "/api/v1/ipam/ipv6-prefixes",
        json={"site_id": site["id"], "name": site_slug, "cidr": cidr, "slug": site_slug, "role": "access", "status": "active"},
    )
    assert pfx.status_code == 200, pfx.text
    return site, pfx.json()


def test_ipv6_range_rejects_invented_kind_and_free_cidr() -> None:
    app = create_app()
    with TestClient(app) as client:
        _site, pfx = _site_prefix(client, site_slug="site-48-rng", cidr="fd48:1::/120")
        pid = pfx["id"]
        bad = client.post(
            f"/api/v1/ipam/ipv6-prefixes/{pid}/ranges",
            json={
                "name": "lease now",
                "slug": "rng-48-bad",
                "kind": "lease",
                "start_address": "fd48:1::10",
                "end_address": "fd48:1::1f",
            },
        )
        assert bad.status_code == 422
        free = client.get(f"/api/v1/ipam/ipv6-prefixes/{pid}/available-ranges")
        assert free.status_code == 200, free.text
        free_cidrs = free.json().get("free_cidrs") or []
        ok = client.post(
            f"/api/v1/ipam/ipv6-prefixes/{pid}/ranges",
            json={
                "name": "Pool",
                "slug": "rng-48-alloc",
                "kind": "allocation",
                "start_address": "fd48:1::10",
                "end_address": "fd48:1::1f",
                "infer_from_free": True,
                "free_cidrs": free_cidrs,
            },
        )
        assert ok.status_code == 200, ok.text
        body = ok.json()
        assert body["kind"] == "allocation"
        assert body["start_address"] == "fd48:1::10"
        listed = client.get(f"/api/v1/ipam/ipv6-prefixes/{pid}/ranges").json()
        assert len(listed) == 1
        assert listed[0]["slug"] == "rng-48-alloc"
        twin = client.post(
            "/api/v1/ipam/ipv6-prefixes",
            json={
                "site_id": _site["id"],
                "name": "Pool",
                "cidr": "fd48:2::/120",
                "slug": "site-48-twin",
                "role": "access",
                "status": "active",
            },
        )
        assert twin.status_code == 200, twin.text
        named = client.get(f"/api/v1/ipam/ipv6-prefixes/{twin.json()['id']}/ranges").json()
        assert named == []
        outside = client.post(
            f"/api/v1/ipam/ipv6-prefixes/{pid}/ranges",
            json={
                "name": "out",
                "slug": "rng-48-out",
                "kind": "other",
                "start_address": "fd48:9::1",
                "end_address": "fd48:9::2",
            },
        )
        assert outside.status_code == 400
        assert outside.json()["detail"]["code"] == "address_outside_prefix"
        overlap = client.post(
            f"/api/v1/ipam/ipv6-prefixes/{pid}/ranges",
            json={
                "name": "overlap",
                "slug": "rng-48-ovl",
                "kind": "reserved",
                "start_address": "fd48:1::18",
                "end_address": "fd48:1::22",
            },
        )
        assert overlap.status_code == 409
        assert overlap.json()["detail"]["code"] == "range_overlap"
        gone = client.delete(f"/api/v1/ipam/ipv6-ranges/{body['id']}")
        assert gone.status_code == 204
        after = client.get(f"/api/v1/ipam/ipv6-prefixes/{pid}/ranges").json()
        assert after == []


def test_ipv6_range_guides_allocation_without_lease() -> None:
    app = create_app()
    with TestClient(app) as client:
        _site, pfx = _site_prefix(client, site_slug="site-48-alloc", cidr="fd48:3::/120")
        pid = pfx["id"]
        alloc = client.post(
            f"/api/v1/ipam/ipv6-prefixes/{pid}/ranges",
            json={
                "name": "alloc",
                "slug": "rng-48-pool",
                "kind": "allocation",
                "start_address": "fd48:3::10",
                "end_address": "fd48:3::12",
            },
        )
        assert alloc.status_code == 200, alloc.text
        dhcp = client.post(
            f"/api/v1/ipam/ipv6-prefixes/{pid}/ranges",
            json={
                "name": "dhcp win",
                "slug": "rng-48-dhcp",
                "kind": "dhcp",
                "start_address": "fd48:3::20",
                "end_address": "fd48:3::2f",
            },
        )
        assert dhcp.status_code == 200, dhcp.text
        blocked = client.post(
            "/api/v1/ipam/ipv6-addresses/ensure",
            json={"ipv6_prefix_id": pid, "address": "fd48:3::21", "mode": "reserve"},
        )
        assert blocked.status_code == 409
        assert blocked.json()["detail"]["code"] == "dhcp_range_protected"
        ok_dhcp = client.post(
            "/api/v1/ipam/ipv6-addresses/ensure",
            json={"ipv6_prefix_id": pid, "address": "fd48:3::21", "mode": "reserve", "role": "dhcp"},
        )
        assert ok_dhcp.status_code == 200, ok_dhcp.text
        req = client.post("/api/v1/ipam/ipv6-addresses/request", json={"ipv6_prefix_id": pid, "mode": "reserve"})
        assert req.status_code == 200, req.text
        assert req.json()["address"] == "fd48:3::10"


def test_ipv6_range_federation_export_apply() -> None:
    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Fed 48", "slug": "fed-48-rng"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "Fed 48 site", "slug": "site-48-fed", "tenant_id": tenant["id"]},
        ).json()
        pfx = client.post(
            "/api/v1/ipam/ipv6-prefixes",
            json={
                "site_id": site["id"],
                "name": "fed-48",
                "cidr": "fd48:4::/120",
                "slug": "px-48-fed",
                "role": "access",
                "status": "active",
            },
        ).json()
        rng = client.post(
            f"/api/v1/ipam/ipv6-prefixes/{pfx['id']}/ranges",
            json={
                "name": "fed pool",
                "slug": "rng-48-fed",
                "kind": "allocation",
                "start_address": "fd48:4::10",
                "end_address": "fd48:4::12",
            },
        )
        assert rng.status_code == 200, rng.text

        exported = client.get(f"/api/v1/ipam/export?site_id={site['id']}")
        assert exported.status_code == 200, exported.text
        assert any(r["slug"] == "rng-48-fed" for r in exported.json().get("ipv6_ranges") or [])
        assert "id" not in (exported.json().get("ipv6_ranges") or [{}])[0]

        snap = client.get("/api/v1/federation/tenants/fed-48-rng/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        ranges = doc["ipam"][0].get("ipv6_ranges") or []
        assert any(r["slug"] == "rng-48-fed" and r["prefix_cidr"] == "fd48:4::/120" for r in ranges)

        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()

        client.post("/api/v1/tenants", json={"name": "Rep 48", "slug": "rep-48-rng"})
        replica = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-48-rng", "name": "Rep 48", "description": None},
            "sites": [{"slug": "site-48-rep", "name": "Rep site", "description": None}],
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
                    "site": {"slug": "site-48-rep", "name": "Rep site"},
                    "vrfs": [],
                    "vlan_groups": [],
                    "vlans": [],
                    "prefixes": [],
                    "ipv4_ranges": [],
                    "addresses": [],
                    "ipv6_prefixes": [
                        {"cidr": "fd48:5::/120", "slug": "px-48-rep", "name": "rep-48", "role": "access", "status": "active"}
                    ],
                    "ipv6_ranges": [
                        {
                            "prefix_cidr": "fd48:5::/120",
                            "site_slug": "site-48-rep",
                            "slug": "rng-48-rep",
                            "name": "rep pool",
                            "kind": "allocation",
                            "start_address": "fd48:5::10",
                            "end_address": "fd48:5::12",
                            "infer_from_free": True,
                        }
                    ],
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
        rep_site = next(s for s in sites if s["slug"] == "site-48-rep")
        prefixes = client.get(f"/api/v1/ipam/ipv6-prefixes?site_id={rep_site['id']}").json()
        assert prefixes
        listed = client.get(f"/api/v1/ipam/ipv6-prefixes/{prefixes[0]['id']}/ranges").json()
        assert any(r["slug"] == "rng-48-rep" for r in listed)
        assert len(listed) == 1
