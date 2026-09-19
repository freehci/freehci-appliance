"""Site B-blokk: overlap-policy, IPv6, circuit uten tenant, audit."""

from fastapi.testclient import TestClient

from app.core.request_context import ipam_scope_allows
from app.main import create_app


def _site(client: TestClient, slug: str) -> int:
    return client.post("/api/v1/dcim/sites", json={"name": slug, "slug": slug}).json()["id"]


def test_overlay_cidr_is_globally_unique() -> None:
    app = create_app()
    with TestClient(app) as client:
        a = _site(client, "site-a-ov")
        b = _site(client, "site-b-ov")
        p1 = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": a, "name": "pods-a", "cidr": "10.80.0.0/16", "role": "overlay-pod"},
        )
        assert p1.status_code == 200, p1.text
        assert p1.json()["overlap_policy"] == "global-unique"

        p2 = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": b, "name": "pods-b", "cidr": "10.80.0.0/16", "role": "overlay-pod"},
        )
        assert p2.status_code == 409
        assert p2.json()["detail"]["code"] == "prefix_global_overlap"

        local = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": a, "name": "lan-a", "cidr": "10.71.10.0/24", "role": "active"},
        )
        assert local.status_code == 200
        same_other_site = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": b, "name": "lan-b", "cidr": "10.71.10.0/24", "role": "active"},
        )
        assert same_other_site.status_code == 200


def test_circuit_without_tenant_and_site_termination() -> None:
    app = create_app()
    with TestClient(app) as client:
        a = _site(client, "site-a-wg")
        b = _site(client, "site-b-wg")
        circ = client.post(
            "/api/v1/ipam/circuits",
            json={
                "circuit_number": "WG-AB",
                "name": "Site A–B",
                "circuit_type": "wireguard",
                "a_site_id": a,
                "z_site_id": b,
            },
        )
        assert circ.status_code == 200, circ.text
        assert circ.json()["tenant_id"] is None
        assert circ.json()["a_site_id"] == a
        cid = circ.json()["id"]
        term = client.post(
            f"/api/v1/ipam/circuits/{cid}/terminations",
            json={"endpoint": "a", "site_id": a, "label": "wg0"},
        )
        assert term.status_code == 200, term.text
        assert term.json()["site_id"] == a


def test_ipv6_ensure_request_and_dual_stack_pair() -> None:
    app = create_app()
    with TestClient(app) as client:
        sid = _site(client, "site-v6")
        v4 = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={
                "site_id": sid,
                "name": "pods4",
                "cidr": "10.89.0.0/16",
                "role": "overlay-pod",
                "dual_stack_group_id": 80,
            },
        )
        assert v4.status_code == 200, v4.text
        v6 = client.post(
            "/api/v1/ipam/ipv6-prefixes/ensure",
            json={
                "site_id": sid,
                "name": "pods6",
                "cidr": "fd80::/48",
                "role": "overlay-pod",
                "slug": "site-a-pod6",
                "dual_stack_group_id": 80,
            },
        )
        assert v6.status_code == 200, v6.text
        assert v6.json()["created"] is True
        assert v6.json()["overlap_policy"] == "global-unique"
        assert v6.json()["dual_stack_group_id"] == 80
        pid = v6.json()["id"]

        again = client.post(
            "/api/v1/ipam/ipv6-prefixes/ensure",
            json={"site_id": sid, "cidr": "fd80::/48", "name": "other"},
        )
        assert again.json()["id"] == pid
        assert again.json()["created"] is False

        req = client.post(
            "/api/v1/ipam/ipv6-addresses/request",
            json={"ipv6_prefix_id": pid, "mode": "reserve", "role": "host"},
        )
        assert req.status_code == 409  # overlay-pod forbids host alloc

        active = client.post(
            "/api/v1/ipam/ipv6-prefixes",
            json={"site_id": sid, "name": "ula-lan", "cidr": "fd71:10::/64", "role": "active"},
        )
        assert active.status_code == 200, active.text
        got = client.post(
            "/api/v1/ipam/ipv6-addresses/request",
            json={"ipv6_prefix_id": active.json()["id"], "mode": "reserve"},
        )
        assert got.status_code == 200, got.text
        assert got.json()["address"].startswith("fd71:10::")


def test_audit_records_prefix_create() -> None:
    app = create_app()
    with TestClient(app) as client:
        sid = _site(client, "site-audit")
        client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sid, "name": "lan", "cidr": "10.1.0.0/24"},
        )
        ev = client.get("/api/v1/ipam/audit", params={"site_id": sid, "resource_type": "prefix"})
        assert ev.status_code == 200
        assert any(x["action"] == "create" and x["resource_type"] == "prefix" for x in ev.json())


def test_ipam_scope_helper() -> None:
    read = frozenset({"ipam:read"})
    alloc = frozenset({"ipam:alloc"})
    admin = frozenset({"ipam:admin"})
    assert ipam_scope_allows("GET", "/api/v1/ipam/ipv4-prefixes", read)
    assert not ipam_scope_allows("DELETE", "/api/v1/ipam/vlans/1", read)
    assert ipam_scope_allows("POST", "/api/v1/ipam/ipv4-addresses/request", alloc)
    assert not ipam_scope_allows("DELETE", "/api/v1/ipam/vlans/1", alloc)
    assert ipam_scope_allows("DELETE", "/api/v1/ipam/vlans/1", admin)
    assert ipam_scope_allows("DELETE", "/api/v1/ipam/vlans/1", None)
