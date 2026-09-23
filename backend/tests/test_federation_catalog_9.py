"""Trinn 9: federation eksporterer katalog og plattform etter slug, uten kjøringer."""

from fastapi.testclient import TestClient

from app.core.db import SessionLocal
from app.main import create_app
from app.services import federation as fed_svc


def test_snapshot_exports_platform_and_catalog_by_slug() -> None:
    app = create_app()
    with TestClient(app) as client:
        tenant = client.post("/api/v1/tenants", json={"name": "Fed 9", "slug": "fed-9-co"}).json()
        site = client.post(
            "/api/v1/dcim/sites",
            json={"name": "Fed 9 site", "slug": "site-9-fed", "tenant_id": tenant["id"]},
        ).json()
        role = client.post(
            "/api/v1/dcim/device-roles",
            json={"name": "Core 9", "slug": "role-9-core", "kind": "core"},
        ).json()
        device = client.post(
            "/api/v1/dcim/devices",
            json={"name": "hv-9", "site_id": site["id"], "device_role_id": role["id"]},
        ).json()
        cl = client.post(
            "/api/v1/clusters",
            json={"name": "px-9", "slug": "px-9-fed", "kind": "proxmox", "site_id": site["id"]},
        ).json()
        client.post(f"/api/v1/clusters/{cl['id']}/members", json={"device_id": device["id"], "role": "node"})
        vm = client.post(
            f"/api/v1/clusters/{cl['id']}/vms",
            json={"name": "web-9", "slug": "vm-9-web", "status": "active"},
        ).json()
        iface = client.post(
            f"/api/v1/clusters/{cl['id']}/vms/{vm['id']}/interfaces",
            json={"name": "eth0", "slug": "vif-9-eth0", "status": "active"},
        ).json()
        pfx = client.post(
            "/api/v1/ipam/ipv4-prefixes",
            json={"site_id": site["id"], "name": "fed-9", "cidr": "10.219.90.0/29"},
        ).json()
        assigned = client.post(
            f"/api/v1/clusters/{cl['id']}/vms/{vm['id']}/interfaces/{iface['id']}/ipv4",
            json={"ipv4_prefix_id": pfx["id"]},
        )
        assert assigned.status_code == 200, assigned.text
        tmpl = client.post(
            "/api/v1/service-catalog/templates",
            json={"name": "vif 9", "slug": "svc-9-fed", "spec": {"kind": "virtual_interface", "reserve_ipv4": False}},
        ).json()
        plan = client.post(
            "/api/v1/service-catalog/deployments",
            json={"template_version_id": tmpl["versions"][0]["id"], "vm_id": vm["id"], "name": "nic-9-fed"},
        )
        assert plan.status_code == 200, plan.text
        run = client.post(f"/api/v1/service-catalog/deployments/{plan.json()['id']}/run")
        assert run.status_code == 200, run.text
        assert run.json()["status"] == "succeeded"

        snap = client.get("/api/v1/federation/tenants/fed-9-co/snapshot")
        assert snap.status_code == 200, snap.text
        doc = snap.json()["document"]
        assert "catalog_deployments" not in doc
        assert "outbound_token" not in str(doc)
        assert "pairing_token" not in str(doc)
        assert doc["device_roles"][0]["slug"] == "role-9-core"
        assert doc["devices"][0]["device_role_slug"] == "role-9-core"
        assert doc["clusters"][0]["slug"] == "px-9-fed"
        assert doc["clusters"][0]["vms"][0]["slug"] == "vm-9-web"
        vif_slugs = {i["slug"] for i in doc["clusters"][0]["vms"][0]["interfaces"]}
        assert "vif-9-eth0" in vif_slugs
        addrs = doc["ipam"][0]["addresses"]
        assert any(a.get("virtual_interface_slug") == "vif-9-eth0" for a in addrs)
        assert any(t["slug"] == "svc-9-fed" for t in doc["catalog_templates"])
        assert doc["catalog_instances"]
        assert all("deployment_id" not in i for i in doc["catalog_instances"])

        db = SessionLocal()
        try:
            checksum = fed_svc.apply_document_locally(db, doc)
            assert checksum == snap.json()["checksum"]
        finally:
            db.close()


def test_apply_catalog_platform_on_new_tenant_without_running_deploy() -> None:
    app = create_app()
    with TestClient(app) as client:
        client.post("/api/v1/tenants", json={"name": "Rep 9", "slug": "rep-9-fed"})
        doc = {
            "apiVersion": "freehci.inventory/v1",
            "kind": "TenantInventory",
            "tenant": {"slug": "rep-9-fed", "name": "Rep 9", "description": None},
            "sites": [{"slug": "site-9-rep", "name": "Rep site", "description": None}],
            "rooms": [],
            "racks": [],
            "manufacturers": [],
            "device_types": [],
            "device_models": [],
            "device_roles": [{"slug": "role-9-edge", "name": "Edge 9", "kind": "edge", "description": None}],
            "devices": [
                {
                    "name": "edge-9",
                    "site_slug": "site-9-rep",
                    "device_role_slug": "role-9-edge",
                    "serial_number": None,
                    "asset_tag": None,
                    "model_name": None,
                    "manufacturer_name": None,
                }
            ],
            "placements": [],
            "ipam": [
                {
                    "site": {"slug": "site-9-rep"},
                    "prefixes": [{"cidr": "10.219.91.0/29", "name": "rep-9", "site_slug": "site-9-rep"}],
                    "addresses": [
                        {
                            "address": "10.219.91.1",
                            "status": "reserved",
                            "prefix_cidr": "10.219.91.0/29",
                            "site_slug": "site-9-rep",
                            "virtual_interface_slug": "vif-9-rep",
                        }
                    ],
                }
            ],
            "clusters": [
                {
                    "slug": "px-9-rep",
                    "name": "px-9-rep",
                    "kind": "proxmox",
                    "site_slug": "site-9-rep",
                    "members": [{"device_name": "edge-9", "site_slug": "site-9-rep", "role": "node"}],
                    "storage_pools": [],
                    "vms": [
                        {
                            "slug": "vm-9-rep",
                            "name": "web-rep",
                            "status": "active",
                            "interfaces": [{"slug": "vif-9-rep", "name": "eth0", "status": "active"}],
                            "disks": [],
                        }
                    ],
                }
            ],
            "cloud_subscriptions": [],
            "catalog_templates": [
                {
                    "slug": "tpl-9-rep",
                    "name": "vif record",
                    "description": None,
                    "versions": [{"version": "1.0.0", "spec": {"kind": "virtual_interface", "reserve_ipv4": False}}],
                }
            ],
            "catalog_instances": [
                {
                    "slug": "inst-9-rep",
                    "name": "nic-rep",
                    "status": "active",
                    "template_slug": "tpl-9-rep",
                    "template_version": "1.0.0",
                    "site_slug": "site-9-rep",
                    "device_name": "edge-9",
                    "cluster_slug": "px-9-rep",
                    "vm_slug": "vm-9-rep",
                    "virtual_interface_slug": "vif-9-rep",
                    "ipv4_address": "10.219.91.1",
                }
            ],
        }
        db = SessionLocal()
        try:
            fed_svc.apply_document_locally(db, doc)
        finally:
            db.close()

        roles = client.get("/api/v1/dcim/device-roles").json()
        assert any(r["slug"] == "role-9-edge" for r in roles)
        devices = client.get("/api/v1/dcim/devices").json()
        found = next(d for d in devices if d["name"] == "edge-9")
        role = next(r for r in roles if r["slug"] == "role-9-edge")
        assert found["device_role_id"] == role["id"]

        clusters = client.get("/api/v1/clusters").json()
        cluster = next(c for c in clusters if c["slug"] == "px-9-rep")
        assert cluster["vms"][0]["slug"] == "vm-9-rep"
        nic = cluster["vms"][0]["interfaces"][0]
        assert nic["slug"] == "vif-9-rep"
        assert nic["ipv4_addresses"]
        assert "mac" not in nic

        templates = client.get("/api/v1/service-catalog/templates").json()
        assert any(t["slug"] == "tpl-9-rep" for t in templates)
        instances = client.get("/api/v1/service-catalog/instances").json()
        inst = next(i for i in instances if i["slug"] == "inst-9-rep")
        assert inst["virtual_interface_id"] == nic["id"]
        assert inst["ipv4_address_id"]

        db = SessionLocal()
        try:
            first = fed_svc.document_checksum(fed_svc.export_tenant_document(db, fed_svc._tenant_by_slug(db, "rep-9-fed")))
            again = fed_svc.apply_document_locally(db, doc)
            assert again == first
        finally:
            db.close()
