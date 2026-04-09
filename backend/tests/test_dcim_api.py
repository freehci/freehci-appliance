"""API-tester for DCIM (enkel flyt)."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_dcim_site_room_rack_device_flow() -> None:
    app = create_app()
    with TestClient(app) as client:
        s = client.post(
            "/api/v1/dcim/sites",
            json={"name": "Oslo DC", "slug": "oslo-dc"},
        )
        assert s.status_code == 200
        site_id = s.json()["id"]

        r = client.post(
            "/api/v1/dcim/rooms",
            json={"site_id": site_id, "name": "Hall A"},
        )
        assert r.status_code == 200, r.text
        room_id = r.json()["id"]

        k = client.post(
            "/api/v1/dcim/racks",
            json={"room_id": room_id, "name": "R42", "u_height": 42},
        )
        assert k.status_code == 200
        rack_id = k.json()["id"]

        m = client.post(
            "/api/v1/dcim/manufacturers",
            json={
                "name": "Dell",
                "description": "Test vendor",
                "website_url": "https://example.com/dell",
            },
        )
        assert m.status_code == 200, m.text
        mid = m.json()["id"]
        assert m.json()["has_logo"] is False
        assert m.json()["description"] == "Test vendor"

        d0 = client.get(f"/api/v1/dcim/manufacturers/{mid}")
        assert d0.status_code == 200
        assert d0.json()["name"] == "Dell"
        assert d0.json()["device_models"] == []

        tiny_png = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
            b"\x00\x00\x05\x00\x01\r\n\x2db\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        up = client.post(
            f"/api/v1/dcim/manufacturers/{mid}/logo",
            files={"file": ("x.png", tiny_png, "image/png")},
        )
        assert up.status_code == 200, up.text
        assert up.json()["has_logo"] is True

        lg = client.get(f"/api/v1/dcim/manufacturers/{mid}/logo")
        assert lg.status_code == 200
        assert lg.content == tiny_png

        dtp = client.post(
            "/api/v1/dcim/device-types",
            json={"name": "Server", "slug": "server", "description": "Compute"},
        )
        assert dtp.status_code == 200, dtp.text
        type_id = dtp.json()["id"]

        dm = client.post(
            "/api/v1/dcim/device-models",
            json={
                "manufacturer_id": mid,
                "device_type_id": type_id,
                "name": "R740",
                "u_height": 2,
            },
        )
        assert dm.status_code == 200
        dmod_id = dm.json()["id"]
        assert dm.json()["device_type_id"] == type_id
        assert dm.json()["has_image_front_file"] is False

        dm_img = client.post(
            f"/api/v1/dcim/device-models/{dmod_id}/image-front",
            files={"file": ("f.png", tiny_png, "image/png")},
        )
        assert dm_img.status_code == 200, dm_img.text
        assert dm_img.json()["has_image_front_file"] is True
        gf = client.get(f"/api/v1/dcim/device-models/{dmod_id}/image-front")
        assert gf.status_code == 200
        assert gf.content == tiny_png

        d = client.post(
            "/api/v1/dcim/devices",
            json={
                "device_model_id": dmod_id,
                "name": "srv-01",
                "attributes": {"os": "Linux"},
            },
        )
        assert d.status_code == 200
        dev_id = d.json()["id"]
        assert d.json()["effective_device_type_id"] == type_id
        assert d.json()["attributes"] == {"os": "Linux"}
        assert d.json()["effective_site_id"] is None

        if_empty = client.get(f"/api/v1/dcim/devices/{dev_id}/interfaces")
        assert if_empty.status_code == 200
        assert if_empty.json() == []

        if1 = client.post(
            f"/api/v1/dcim/devices/{dev_id}/interfaces",
            json={
                "name": "eth0",
                "speed_mbps": 1000,
                "mac_address": "aa:bb:cc:dd:ee:ff",
                "vlan_id": 100,
            },
        )
        assert if1.status_code == 200, if1.text
        if1_id = if1.json()["id"]
        assert if1.json()["enabled"] is True
        assert if1.json()["vlan_id"] == 100

        bad_vlan = client.post(
            f"/api/v1/dcim/devices/{dev_id}/interfaces",
            json={"name": "eth99", "vlan_id": 5000},
        )
        assert bad_vlan.status_code == 422

        dup = client.post(
            f"/api/v1/dcim/devices/{dev_id}/interfaces",
            json={"name": "eth0"},
        )
        assert dup.status_code == 409

        li = client.get(f"/api/v1/dcim/devices/{dev_id}/interfaces")
        assert len(li.json()) == 1

        up_if = client.patch(
            f"/api/v1/dcim/devices/{dev_id}/interfaces/{if1_id}",
            json={"description": "uplink", "enabled": False, "vlan_id": None},
        )
        assert up_if.status_code == 200
        assert up_if.json()["enabled"] is False
        assert up_if.json()["description"] == "uplink"
        assert up_if.json()["vlan_id"] is None
        assert up_if.json()["ip_assignments"] == []

        up_vlan = client.patch(
            f"/api/v1/dcim/devices/{dev_id}/interfaces/{if1_id}",
            json={"vlan_id": 200},
        )
        assert up_vlan.status_code == 200
        assert up_vlan.json()["vlan_id"] == 200

        ip_a = client.post(
            f"/api/v1/dcim/devices/{dev_id}/interfaces/{if1_id}/ip-assignments",
            json={"address": "192.168.1.10", "is_primary": True},
        )
        assert ip_a.status_code == 200, ip_a.text
        assert ip_a.json()["family"] == "ipv4"
        assert ip_a.json()["address"] == "192.168.1.10"
        assert ip_a.json()["is_primary"] is True
        assert ip_a.json()["ipv4_prefix_id"] is None

        bad_ip = client.post(
            f"/api/v1/dcim/devices/{dev_id}/interfaces/{if1_id}/ip-assignments",
            json={"address": "not-an-ip"},
        )
        assert bad_ip.status_code == 400

        li2 = client.get(f"/api/v1/dcim/devices/{dev_id}/interfaces")
        assert len(li2.json()) == 1
        assert len(li2.json()[0]["ip_assignments"]) == 1

        p = client.post(
            "/api/v1/dcim/placements",
            json={
                "rack_id": rack_id,
                "device_id": dev_id,
                "u_position": 10,
                "mounting": "front",
            },
        )
        assert p.status_code == 200, p.text
        assert p.json()["u_position"] == 10

        g_placed = client.get(f"/api/v1/dcim/devices/{dev_id}")
        assert g_placed.json()["effective_site_id"] == site_id

        p2 = client.post(
            "/api/v1/dcim/placements",
            json={
                "rack_id": rack_id,
                "device_id": dev_id,
                "u_position": 20,
                "mounting": "front",
            },
        )
        assert p2.status_code == 400

        pid = p.json()["id"]
        mv = client.patch(
            f"/api/v1/dcim/placements/{pid}",
            json={"u_position": 25},
        )
        assert mv.status_code == 200, mv.text
        assert mv.json()["u_position"] == 25


def test_dcim_iface_ip_ipv4_prefix_validation() -> None:
    app = create_app()
    with TestClient(app) as client:
        sa = client.post("/api/v1/dcim/sites", json={"name": "S1", "slug": "ipam-s1"}).json()["id"]
        sb = client.post("/api/v1/dcim/sites", json={"name": "S2", "slug": "ipam-s2"}).json()["id"]
        ra = client.post("/api/v1/dcim/rooms", json={"site_id": sa, "name": "R1"}).json()["id"]
        rb = client.post("/api/v1/dcim/rooms", json={"site_id": sb, "name": "R2"}).json()["id"]
        ka = client.post("/api/v1/dcim/racks", json={"room_id": ra, "name": "K1"}).json()["id"]
        kb = client.post("/api/v1/dcim/racks", json={"room_id": rb, "name": "K2"}).json()["id"]

        mid = client.post(
            "/api/v1/dcim/manufacturers",
            json={"name": "MIP", "description": "x"},
        ).json()["id"]
        tid = client.post(
            "/api/v1/dcim/device-types",
            json={"name": "Srv", "slug": "srv-ipam"},
        ).json()["id"]
        dmod = client.post(
            "/api/v1/dcim/device-models",
            json={"manufacturer_id": mid, "device_type_id": tid, "name": "X1", "u_height": 1},
        ).json()["id"]
        dev_id = client.post(
            "/api/v1/dcim/devices",
            json={"device_model_id": dmod, "name": "host-a"},
        ).json()["id"]
        if_id = client.post(
            f"/api/v1/dcim/devices/{dev_id}/interfaces",
            json={"name": "eth0"},
        ).json()["id"]

        pfx_a = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sa, "name": "LAN", "cidr": "10.10.0.0/16"},
        )
        assert pfx_a.status_code == 200, pfx_a.text
        pfx_aid = pfx_a.json()["id"]

        pfx_b = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": sb, "name": "LAN", "cidr": "10.10.0.0/16"},
        )
        assert pfx_b.status_code == 200
        pfx_bid = pfx_b.json()["id"]

        no_pl = client.post(
            f"/api/v1/dcim/devices/{dev_id}/interfaces/{if_id}/ip-assignments",
            json={"address": "10.10.1.1", "ipv4_prefix_id": pfx_aid},
        )
        assert no_pl.status_code == 400

        pl = client.post(
            "/api/v1/dcim/placements",
            json={"rack_id": ka, "device_id": dev_id, "u_position": 1, "mounting": "front"},
        )
        assert pl.status_code == 200

        wrong_site = client.post(
            f"/api/v1/dcim/devices/{dev_id}/interfaces/{if_id}/ip-assignments",
            json={"address": "10.10.1.2", "ipv4_prefix_id": pfx_bid},
        )
        assert wrong_site.status_code == 400

        outside = client.post(
            f"/api/v1/dcim/devices/{dev_id}/interfaces/{if_id}/ip-assignments",
            json={"address": "192.168.1.1", "ipv4_prefix_id": pfx_aid},
        )
        assert outside.status_code == 400

        ok = client.post(
            f"/api/v1/dcim/devices/{dev_id}/interfaces/{if_id}/ip-assignments",
            json={"address": "10.10.1.5", "ipv4_prefix_id": pfx_aid},
        )
        assert ok.status_code == 200, ok.text
        assert ok.json()["ipv4_prefix_id"] == pfx_aid

        gpx = client.get(f"/api/v1/ipam/ipv4-prefixes/{pfx_aid}")
        assert gpx.status_code == 200
        assert gpx.json()["used_count"] == 1
        assert gpx.json()["address_total"] == 65536

        v6 = client.post(
            f"/api/v1/dcim/devices/{dev_id}/interfaces/{if_id}/ip-assignments",
            json={"address": "2001:db8::1", "ipv4_prefix_id": pfx_aid},
        )
        assert v6.status_code == 400

        clr = client.patch(
            f"/api/v1/dcim/devices/{dev_id}/interfaces/{if_id}/ip-assignments/{ok.json()['id']}",
            json={"ipv4_prefix_id": None},
        )
        assert clr.status_code == 200
        assert clr.json()["ipv4_prefix_id"] is None

        gpx2 = client.get(f"/api/v1/ipam/ipv4-prefixes/{pfx_aid}")
        # Utnyttelse følger adresse i CIDR, ikke bare FK: fjernet prefiks-lenke, IP ligger fortsatt i /16
        assert gpx2.json()["used_count"] == 1


def test_patch_device_device_type_override_and_clear() -> None:
    app = create_app()
    with TestClient(app) as client:
        s = client.post("/api/v1/dcim/sites", json={"name": "S", "slug": "s"})
        assert s.status_code == 200
        site_id = s.json()["id"]
        r = client.post("/api/v1/dcim/rooms", json={"site_id": site_id, "name": "R"})
        assert r.status_code == 200
        room_id = r.json()["id"]
        client.post("/api/v1/dcim/racks", json={"room_id": room_id, "name": "K", "u_height": 42})

        m = client.post(
            "/api/v1/dcim/manufacturers",
            json={"name": "M", "description": None, "website_url": None},
        )
        assert m.status_code == 200
        mid = m.json()["id"]

        t1 = client.post("/api/v1/dcim/device-types", json={"name": "Server", "slug": "server"})
        assert t1.status_code == 200
        tid1 = t1.json()["id"]
        t2 = client.post("/api/v1/dcim/device-types", json={"name": "Switch", "slug": "switch"})
        assert t2.status_code == 200
        tid2 = t2.json()["id"]

        dm = client.post(
            "/api/v1/dcim/device-models",
            json={"manufacturer_id": mid, "device_type_id": tid1, "name": "X", "u_height": 1},
        )
        assert dm.status_code == 200
        dmod_id = dm.json()["id"]

        d = client.post(
            "/api/v1/dcim/devices",
            json={"device_model_id": dmod_id, "name": "dev1"},
        )
        assert d.status_code == 200
        did = d.json()["id"]
        assert d.json()["device_type_id"] is None
        assert d.json()["effective_device_type_id"] == tid1

        p = client.patch(f"/api/v1/dcim/devices/{did}", json={"device_type_id": tid2})
        assert p.status_code == 200, p.text
        assert p.json()["device_type_id"] == tid2
        assert p.json()["effective_device_type_id"] == tid2

        c = client.patch(f"/api/v1/dcim/devices/{did}", json={"device_type_id": None})
        assert c.status_code == 200, c.text
        assert c.json()["device_type_id"] is None
        assert c.json()["effective_device_type_id"] == tid1
