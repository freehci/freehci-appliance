"""API-tester for IPAM IPv4-adresse-inventory og request."""

import uuid

from fastapi.testclient import TestClient

from app.main import create_app


def test_ipam_users_create_and_list() -> None:
    app = create_app()
    with TestClient(app) as client:
        u = client.post("/api/v1/ipam/users", json={"username": "alice", "display_name": "Alice"})
        assert u.status_code == 200, u.text
        li = client.get("/api/v1/ipam/users")
        assert li.status_code == 200
        assert any(x["username"] == "alice" for x in li.json())


def test_ipam_request_ipv4_batch_preferred_then_auto() -> None:
    app = create_app()
    with TestClient(app) as client:
        sa = client.post("/api/v1/dcim/sites", json={"name": "S-batch", "slug": "s-batch"}).json()["id"]
        pfx = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sa, "name": "LAN", "cidr": "10.10.0.0/29"},
        )
        assert pfx.status_code == 200, pfx.text
        pid = pfx.json()["id"]

        r = client.post(
            "/api/v1/ipam/ipv4-addresses/request-batch",
            json={
                "ipv4_prefix_id": pid,
                "mode": "reserve",
                "count": 2,
                "preferred_addresses": ["10.10.0.6", "10.10.0.2"],
            },
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["requested_count"] == 2
        assert body["allocated_count"] == 2
        addrs = {x["address"] for x in body["addresses"]}
        assert addrs == {"10.10.0.6", "10.10.0.2"}


def test_ipam_patch_prefix_subnet_services() -> None:
    app = create_app()
    with TestClient(app) as client:
        sa = client.post("/api/v1/dcim/sites", json={"name": "S-svc", "slug": "s-svc"}).json()["id"]
        pfx = client.post("/api/v1/ipam/ipv4-prefixes", json={"site_id": sa, "name": "LAN", "cidr": "10.11.0.0/24"})
        assert pfx.status_code == 200
        pid = pfx.json()["id"]
        svc = {"gateway": "10.11.0.1", "dns": "10.11.0.2", "dhcp_server": "10.11.0.3"}
        u = client.patch(f"/api/v1/ipam/ipv4-prefixes/{pid}", json={"subnet_services": svc})
        assert u.status_code == 200, u.text
        assert u.json()["subnet_services"] == svc


def test_ipam_request_ipv4_reserve_next_free() -> None:
    app = create_app()
    with TestClient(app) as client:
        sa = client.post("/api/v1/dcim/sites", json={"name": "S1", "slug": "s1"}).json()["id"]
        pfx = client.post("/api/v1/ipam/ipv4-prefixes", json={"site_id": sa, "name": "LAN", "cidr": "10.0.0.0/30"})
        assert pfx.status_code == 200, pfx.text
        pid = pfx.json()["id"]

        r1 = client.post("/api/v1/ipam/ipv4-addresses/request", json={"ipv4_prefix_id": pid, "mode": "reserve"})
        assert r1.status_code == 200, r1.text
        assert r1.json()["address"] == "10.0.0.1"
        assert r1.json()["status"] == "reserved"

        r2 = client.post("/api/v1/ipam/ipv4-addresses/request", json={"ipv4_prefix_id": pid, "mode": "reserve"})
        assert r2.status_code == 200, r2.text
        assert r2.json()["address"] == "10.0.0.2"

        r3 = client.post("/api/v1/ipam/ipv4-addresses/request", json={"ipv4_prefix_id": pid, "mode": "reserve"})
        assert r3.status_code == 409


def test_ipam_request_ipv4_assign_to_interface() -> None:
    app = create_app()
    with TestClient(app) as client:
        sa = client.post("/api/v1/dcim/sites", json={"name": "S1", "slug": "as1"}).json()["id"]
        ra = client.post("/api/v1/dcim/rooms", json={"site_id": sa, "name": "R1"}).json()["id"]
        rk = client.post("/api/v1/dcim/racks", json={"room_id": ra, "name": "K1"}).json()["id"]

        mid = client.post("/api/v1/dcim/manufacturers", json={"name": "M-Assign"}).json()["id"]
        tid = client.post("/api/v1/dcim/device-types", json={"name": "SrvAssign", "slug": "srv-assign"}).json()["id"]
        dmod = client.post(
            "/api/v1/dcim/device-models",
            json={"manufacturer_id": mid, "device_type_id": tid, "name": "X1", "u_height": 1},
        ).json()["id"]
        dev_id = client.post("/api/v1/dcim/devices", json={"device_model_id": dmod, "name": "host-a"}).json()["id"]
        if_id = client.post(f"/api/v1/dcim/devices/{dev_id}/interfaces", json={"name": "eth0"}).json()["id"]

        pl = client.post(
            "/api/v1/dcim/placements",
            json={"rack_id": rk, "device_id": dev_id, "u_position": 1, "mounting": "front"},
        )
        assert pl.status_code == 200

        pfx = client.post("/api/v1/ipam/ipv4-prefixes", json={"site_id": sa, "name": "LAN", "cidr": "10.0.2.0/30"})
        assert pfx.status_code == 200
        pid = pfx.json()["id"]

        r = client.post(
            "/api/v1/ipam/ipv4-addresses/request",
            json={"ipv4_prefix_id": pid, "mode": "assign", "interface_id": if_id},
        )
        assert r.status_code == 200, r.text
        assert r.json()["status"] == "assigned"
        assert r.json()["interface_id"] == if_id
        assert r.json()["interface_name"] == "eth0"
        assert r.json()["interface_ip_assignment_id"] is not None

        ifs = client.get(f"/api/v1/dcim/devices/{dev_id}/interfaces")
        assert ifs.status_code == 200
        iface = next(x for x in ifs.json() if x["id"] == if_id)
        assert any(a["address"] == "10.0.2.1" for a in iface["ip_assignments"])


def test_ipam_request_assign_rejects_wrong_device_id() -> None:
    u = uuid.uuid4().hex[:10]
    app = create_app()
    with TestClient(app) as client:
        sa = client.post("/api/v1/dcim/sites", json={"name": "S", "slug": f"s-mis-{u}"}).json()["id"]
        ra = client.post("/api/v1/dcim/rooms", json={"site_id": sa, "name": "R"}).json()["id"]
        rk = client.post("/api/v1/dcim/racks", json={"room_id": ra, "name": "K"}).json()["id"]
        mid = client.post("/api/v1/dcim/manufacturers", json={"name": f"M-mis-{u}"}).json()["id"]
        tid = client.post(
            "/api/v1/dcim/device-types",
            json={"name": f"T-mis-{u}", "slug": f"t-mis-{u}"},
        ).json()["id"]
        dmod = client.post(
            "/api/v1/dcim/device-models",
            json={"manufacturer_id": mid, "device_type_id": tid, "name": "X", "u_height": 1},
        ).json()["id"]
        dev_a = client.post("/api/v1/dcim/devices", json={"device_model_id": dmod, "name": f"a-{u}"}).json()["id"]
        dev_b = client.post("/api/v1/dcim/devices", json={"device_model_id": dmod, "name": f"b-{u}"}).json()["id"]
        if_a = client.post(f"/api/v1/dcim/devices/{dev_a}/interfaces", json={"name": "eth0"}).json()["id"]
        assert (
            client.post(
                "/api/v1/dcim/placements",
                json={"rack_id": rk, "device_id": dev_a, "u_position": 1, "mounting": "front"},
            ).status_code
            == 200
        )
        assert (
            client.post(
                "/api/v1/dcim/placements",
                json={"rack_id": rk, "device_id": dev_b, "u_position": 2, "mounting": "front"},
            ).status_code
            == 200
        )
        pfx = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sa, "name": "LAN", "cidr": "10.0.88.0/30"},
        )
        assert pfx.status_code == 200
        pid = pfx.json()["id"]
        bad = client.post(
            "/api/v1/ipam/ipv4-addresses/request",
            json={
                "ipv4_prefix_id": pid,
                "mode": "assign",
                "interface_id": if_a,
                "device_id": dev_b,
            },
        )
        assert bad.status_code == 400
        ok = client.post(
            "/api/v1/ipam/ipv4-addresses/request",
            json={
                "ipv4_prefix_id": pid,
                "mode": "assign",
                "interface_id": if_a,
                "device_id": dev_a,
            },
        )
        assert ok.status_code == 200, ok.text


def test_ipam_ipv4_address_patch_note_and_owner() -> None:
    app = create_app()
    with TestClient(app) as client:
        u = client.post("/api/v1/ipam/users", json={"username": "bob"}).json()["id"]
        sa = client.post("/api/v1/dcim/sites", json={"name": "S1", "slug": "ps1"}).json()["id"]
        pfx = client.post("/api/v1/ipam/ipv4-prefixes", json={"site_id": sa, "name": "LAN", "cidr": "10.0.3.0/30"})
        pid = pfx.json()["id"]
        r = client.post("/api/v1/ipam/ipv4-addresses/request", json={"ipv4_prefix_id": pid, "mode": "reserve"})
        addr_id = r.json()["id"]

        up = client.patch(f"/api/v1/ipam/ipv4-addresses/{addr_id}", json={"owner_user_id": u, "note": "x"})
        assert up.status_code == 200, up.text
        assert up.json()["owner_user_id"] == u
        assert up.json()["note"] == "x"


def test_ipam_ipv4_address_release_reserved() -> None:
    app = create_app()
    with TestClient(app) as client:
        sa = client.post("/api/v1/dcim/sites", json={"name": "S1", "slug": "rel1"}).json()["id"]
        pfx = client.post("/api/v1/ipam/ipv4-prefixes", json={"site_id": sa, "name": "LAN", "cidr": "10.0.4.0/30"})
        pid = pfx.json()["id"]
        r = client.post("/api/v1/ipam/ipv4-addresses/request", json={"ipv4_prefix_id": pid, "mode": "reserve"})
        addr_id = r.json()["id"]
        assert r.json()["status"] == "reserved"

        rel = client.post(f"/api/v1/ipam/ipv4-addresses/{addr_id}/release")
        assert rel.status_code == 200, rel.text
        assert rel.json()["status"] == "discovered"
        assert rel.json()["interface_ip_assignment_id"] is None


def test_ipam_ipv4_address_release_assigned_deletes_dcim_assignment() -> None:
    app = create_app()
    with TestClient(app) as client:
        sa = client.post("/api/v1/dcim/sites", json={"name": "S1", "slug": "rel2"}).json()["id"]
        ra = client.post("/api/v1/dcim/rooms", json={"site_id": sa, "name": "R1"}).json()["id"]
        rk = client.post("/api/v1/dcim/racks", json={"room_id": ra, "name": "K1"}).json()["id"]

        mid = client.post("/api/v1/dcim/manufacturers", json={"name": "M-Rel"}).json()["id"]
        tid = client.post("/api/v1/dcim/device-types", json={"name": "SrvRel", "slug": "srv-rel"}).json()["id"]
        dmod = client.post(
            "/api/v1/dcim/device-models",
            json={"manufacturer_id": mid, "device_type_id": tid, "name": "X1", "u_height": 1},
        ).json()["id"]
        dev_id = client.post("/api/v1/dcim/devices", json={"device_model_id": dmod, "name": "host-a"}).json()["id"]
        if_id = client.post(f"/api/v1/dcim/devices/{dev_id}/interfaces", json={"name": "eth0"}).json()["id"]
        pl = client.post(
            "/api/v1/dcim/placements",
            json={"rack_id": rk, "device_id": dev_id, "u_position": 1, "mounting": "front"},
        )
        assert pl.status_code == 200

        pfx = client.post("/api/v1/ipam/ipv4-prefixes", json={"site_id": sa, "name": "LAN", "cidr": "10.0.5.0/30"})
        pid = pfx.json()["id"]
        r = client.post(
            "/api/v1/ipam/ipv4-addresses/request",
            json={"ipv4_prefix_id": pid, "mode": "assign", "interface_id": if_id},
        )
        assert r.status_code == 200, r.text
        addr_id = r.json()["id"]
        aid = r.json()["interface_ip_assignment_id"]
        assert aid is not None

        rel = client.post(f"/api/v1/ipam/ipv4-addresses/{addr_id}/release")
        assert rel.status_code == 200, rel.text
        assert rel.json()["status"] == "discovered"
        assert rel.json()["interface_ip_assignment_id"] is None

        ifs = client.get(f"/api/v1/dcim/devices/{dev_id}/interfaces")
        iface = next(x for x in ifs.json() if x["id"] == if_id)
        assert all(a["id"] != aid for a in iface["ip_assignments"])


def test_ipam_ipv4_address_interface_name_for_subinterface() -> None:
    u = uuid.uuid4().hex[:10]
    app = create_app()
    with TestClient(app) as client:
        sa = client.post("/api/v1/dcim/sites", json={"name": "S", "slug": f"s-ifn-{u}"}).json()["id"]
        ra = client.post("/api/v1/dcim/rooms", json={"site_id": sa, "name": "R1"}).json()["id"]
        rk = client.post("/api/v1/dcim/racks", json={"room_id": ra, "name": "K1"}).json()["id"]

        mid = client.post("/api/v1/dcim/manufacturers", json={"name": f"M-ifn-{u}"}).json()["id"]
        tid = client.post(
            "/api/v1/dcim/device-types",
            json={"name": f"Srv-ifn-{u}", "slug": f"srv-ifn-{u}"},
        ).json()["id"]
        dmod = client.post(
            "/api/v1/dcim/device-models",
            json={"manufacturer_id": mid, "device_type_id": tid, "name": "X1", "u_height": 1},
        ).json()["id"]
        dev_id = client.post("/api/v1/dcim/devices", json={"device_model_id": dmod, "name": f"sw-{u}"}).json()["id"]
        me0 = client.post(f"/api/v1/dcim/devices/{dev_id}/interfaces", json={"name": "me0"}).json()["id"]
        me00 = client.post(
            f"/api/v1/dcim/devices/{dev_id}/interfaces",
            json={"name": "me0.0", "parent_interface_id": me0},
        ).json()["id"]

        pl = client.post(
            "/api/v1/dcim/placements",
            json={"rack_id": rk, "device_id": dev_id, "u_position": 1, "mounting": "front"},
        )
        assert pl.status_code == 200

        pfx = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sa, "name": "LAN", "cidr": "10.0.9.0/30"},
        )
        assert pfx.status_code == 200
        pid = pfx.json()["id"]

        r = client.post(
            "/api/v1/ipam/ipv4-addresses/request",
            json={"ipv4_prefix_id": pid, "mode": "assign", "interface_id": me00},
        )
        assert r.status_code == 200, r.text
        assert r.json()["interface_name"] == "me0.0"

        li = client.get(f"/api/v1/ipam/ipv4-addresses?ipv4_prefix_id={pid}")
        assert li.status_code == 200
        row = next(x for x in li.json() if x["address"] == "10.0.9.1")
        assert row["interface_name"] == "me0.0"
