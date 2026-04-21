"""Tenants, site.tenant_id og IPAM VRF/VLAN/samband API."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_default_tenant_on_site_create_and_vrf_vlan_circuit() -> None:
    app = create_app()
    with TestClient(app) as client:
        tenants_before = client.get("/api/v1/tenants").json()
        assert isinstance(tenants_before, list)

        site = client.post("/api/v1/dcim/sites", json={"name": "Lab", "slug": "lab-ipam-fac"}).json()
        assert site.get("tenant_id") is not None
        tid = int(site["tenant_id"])

        tenants_after = client.get("/api/v1/tenants").json()
        assert any(t["id"] == tid for t in tenants_after)

        vrf = client.post(
            "/api/v1/ipam/vrfs",
            json={"site_id": site["id"], "name": "default-evpn", "route_distinguisher": "65000:1"},
        )
        assert vrf.status_code == 200, vrf.text
        vrf_id = vrf.json()["id"]

        vlan = client.post(
            "/api/v1/ipam/vlans",
            json={"site_id": site["id"], "vid": 100, "name": "Servers", "vrf_id": vrf_id},
        )
        assert vlan.status_code == 200, vlan.text
        vlan_id = int(vlan.json()["id"])

        circ = client.post(
            "/api/v1/ipam/circuits",
            json={
                "tenant_id": tid,
                "circuit_number": "SB-001",
                "name": "Oslo–Bergen",
                "circuit_type": "fiber",
                "is_leased": True,
                "provider_name": "Telenor",
            },
        )
        assert circ.status_code == 200, circ.text
        cid = circ.json()["id"]

        term = client.post(
            f"/api/v1/ipam/circuits/{cid}/terminations",
            json={"endpoint": "a", "interface_id": None},
        )
        assert term.status_code == 200, term.text

        li = client.get(f"/api/v1/ipam/circuits/{cid}/terminations")
        assert li.status_code == 200
        assert len(li.json()) == 1

        pfx = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={
                "site_id": site["id"],
                "name": "LAN",
                "cidr": "10.99.0.0/24",
                "vlan_id": vlan_id,
                "vrf_id": vrf_id,
            },
        )
        assert pfx.status_code == 200, pfx.text
        assert pfx.json().get("vlan_id") == vlan_id
        assert pfx.json().get("vrf_id") == vrf_id
