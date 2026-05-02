"""API-tester for DCIM custom components."""

import uuid

from fastapi.testclient import TestClient

from app.main import create_app


def test_custom_components_validate_impact_and_copy_to_device() -> None:
    app = create_app()
    suffix = uuid.uuid4().hex[:8]

    with TestClient(app) as client:
        cls = client.post(
            "/api/v1/dcim/component-classes",
            json={"name": f"RAM {suffix}", "slug": f"ram-{suffix}"},
        )
        assert cls.status_code == 200, cls.text
        class_id = cls.json()["id"]

        fld = client.post(
            f"/api/v1/dcim/component-classes/{class_id}/fields",
            json={
                "key": "size_gb",
                "label": "Size",
                "data_type": "integer",
                "unit": "GB",
                "required": True,
                "min_number": 1,
            },
        )
        assert fld.status_code == 200, fld.text
        field_id = fld.json()["id"]

        bad_component = client.post(
            "/api/v1/dcim/components",
            json={"class_id": class_id, "name": f"Broken DIMM {suffix}", "specs_json": {}},
        )
        assert bad_component.status_code == 422

        component = client.post(
            "/api/v1/dcim/components",
            json={
                "class_id": class_id,
                "name": f"128GB DIMM {suffix}",
                "part_number": f"DIMM-{suffix}",
                "specs_json": {"size_gb": 128},
            },
        )
        assert component.status_code == 200, component.text
        component_id = component.json()["id"]

        impact = client.post(
            f"/api/v1/dcim/component-class-fields/{field_id}/impact",
            json={"max_number": 64},
        )
        assert impact.status_code == 200, impact.text
        assert impact.json()["breaking"] is True
        assert impact.json()["affected_components"] == 1

        blocked = client.patch(
            f"/api/v1/dcim/component-class-fields/{field_id}",
            json={"max_number": 64},
        )
        assert blocked.status_code == 409

        model = client.post("/api/v1/dcim/device-models", json={"name": f"Server {suffix}"})
        assert model.status_code == 200, model.text
        model_id = model.json()["id"]

        bom = client.post(
            f"/api/v1/dcim/device-models/{model_id}/components",
            json={"component_id": component_id, "quantity": 8, "slot_label": "DIMM"},
        )
        assert bom.status_code == 200, bom.text
        assert bom.json()["quantity"] == 8

        device = client.post(
            "/api/v1/dcim/devices",
            json={"device_model_id": model_id, "name": f"server-01-{suffix}"},
        )
        assert device.status_code == 200, device.text
        device_id = device.json()["id"]

        copied = client.post(f"/api/v1/dcim/devices/{device_id}/components/copy-from-model")
        assert copied.status_code == 200, copied.text
        assert len(copied.json()) == 1
        assert copied.json()[0]["component_id"] == component_id
        assert copied.json()[0]["quantity"] == 8


def test_component_class_inheritance_children_and_interface_materialization() -> None:
    app = create_app()
    suffix = uuid.uuid4().hex[:8]

    with TestClient(app) as client:
        physical = client.post(
            "/api/v1/dcim/component-classes",
            json={"name": f"Physical Device {suffix}", "slug": f"physical-{suffix}"},
        )
        assert physical.status_code == 200, physical.text
        physical_id = physical.json()["id"]
        height_field = client.post(
            f"/api/v1/dcim/component-classes/{physical_id}/fields",
            json={"key": "height_mm", "label": "Height", "data_type": "integer", "unit": "mm"},
        )
        assert height_field.status_code == 200, height_field.text

        net = client.post(
            "/api/v1/dcim/component-classes",
            json={"name": f"Network Capable {suffix}", "slug": f"netcap-{suffix}"},
        )
        assert net.status_code == 200, net.text
        net_id = net.json()["id"]

        nic = client.post(
            "/api/v1/dcim/component-classes",
            json={"name": f"NIC {suffix}", "slug": f"nic-{suffix}"},
        )
        assert nic.status_code == 200, nic.text
        nic_id = nic.json()["id"]
        assert client.post(f"/api/v1/dcim/component-classes/{nic_id}/parents", json={"parent_class_id": physical_id}).status_code == 200
        assert client.post(f"/api/v1/dcim/component-classes/{nic_id}/parents", json={"parent_class_id": net_id}).status_code == 200
        cycle = client.post(f"/api/v1/dcim/component-classes/{physical_id}/parents", json={"parent_class_id": nic_id})
        assert cycle.status_code == 409

        effective = client.get(f"/api/v1/dcim/component-classes/{nic_id}/effective-fields")
        assert effective.status_code == 200, effective.text
        assert any(f["key"] == "height_mm" and f["inherited"] for f in effective.json())

        port = client.post(
            "/api/v1/dcim/component-classes",
            json={"name": f"Port {suffix}", "slug": f"port-{suffix}"},
        )
        assert port.status_code == 200, port.text
        port_id = port.json()["id"]
        speed_field = client.post(
            f"/api/v1/dcim/component-classes/{port_id}/fields",
            json={"key": "speed_mbps", "label": "Speed", "data_type": "integer", "unit": "Mbps"},
        )
        assert speed_field.status_code == 200, speed_field.text
        media_field = client.post(
            f"/api/v1/dcim/component-classes/{port_id}/fields",
            json={
                "key": "media_type",
                "label": "Media type",
                "data_type": "choice",
                "choices_json": ["copper", "fiber"],
            },
        )
        assert media_field.status_code == 200, media_field.text

        nic_component = client.post(
            "/api/v1/dcim/components",
            json={"class_id": nic_id, "name": f"NIC-344435 {suffix}", "specs_json": {"height_mm": 42}},
        )
        assert nic_component.status_code == 200, nic_component.text
        nic_component_id = nic_component.json()["id"]

        child = client.post(
            f"/api/v1/dcim/components/{nic_component_id}/children",
            json={
                "child_class_id": port_id,
                "quantity": 2,
                "name_pattern": "eth{n}",
                "overrides_json": {"speed_mbps": 1000, "media_type": "copper"},
                "materialize_as": "interface",
            },
        )
        assert child.status_code == 200, child.text

        model = client.post("/api/v1/dcim/device-models", json={"name": f"Server NIC {suffix}"})
        assert model.status_code == 200, model.text
        model_id = model.json()["id"]
        bom = client.post(f"/api/v1/dcim/device-models/{model_id}/components", json={"component_id": nic_component_id})
        assert bom.status_code == 200, bom.text
        device = client.post("/api/v1/dcim/devices", json={"device_model_id": model_id, "name": f"server-nic-{suffix}"})
        assert device.status_code == 200, device.text
        device_id = device.json()["id"]
        copied = client.post(f"/api/v1/dcim/devices/{device_id}/components/copy-from-model")
        assert copied.status_code == 200, copied.text
        link_id = copied.json()[0]["id"]

        materialized = client.post(
            f"/api/v1/dcim/devices/{device_id}/components/materialize-interfaces",
            json={"component_link_id": link_id},
        )
        assert materialized.status_code == 200, materialized.text
        assert [x["name"] for x in materialized.json()] == ["eth1", "eth2"]
        assert all(x["speed_mbps"] == 1000 for x in materialized.json())


def test_standard_component_catalog_seed_is_idempotent_and_creates_canonical_classes() -> None:
    app = create_app()

    with TestClient(app) as client:
        first = client.post("/api/v1/dcim/component-classes/seed-standard")
        assert first.status_code == 200, first.text
        assert first.json()["classes_created"] >= 10
        assert first.json()["fields_created"] > 0
        assert "network-adapter" in first.json()["class_slugs"]

        second = client.post("/api/v1/dcim/component-classes/seed-standard")
        assert second.status_code == 200, second.text
        assert second.json()["classes_created"] == 0
        assert second.json()["fields_created"] == 0
        assert second.json()["parents_created"] == 0

        classes = client.get("/api/v1/dcim/component-classes")
        assert classes.status_code == 200, classes.text
        by_slug = {row["slug"]: row for row in classes.json()}
        nic_id = by_slug["network-adapter"]["id"]
        port_id = by_slug["network-port"]["id"]

        nic_fields = client.get(f"/api/v1/dcim/component-classes/{nic_id}/effective-fields")
        assert nic_fields.status_code == 200, nic_fields.text
        nic_keys = {row["key"]: row for row in nic_fields.json()}
        assert nic_keys["height_mm"]["inherited"] is True
        assert nic_keys["media_type"]["inherited"] is True
        assert nic_keys["port_count"]["inherited"] is False

        port_fields = client.get(f"/api/v1/dcim/component-classes/{port_id}/effective-fields")
        assert port_fields.status_code == 200, port_fields.text
        port_keys = {row["key"]: row for row in port_fields.json()}
        assert "speed_mbps" in port_keys
        assert "connector_type" in port_keys


def test_component_external_mapping_registry_exposes_reference_profiles() -> None:
    app = create_app()

    with TestClient(app) as client:
        profiles = client.get("/api/v1/dcim/component-mappings")
        assert profiles.status_code == 200, profiles.text
        sources = {row["source"] for row in profiles.json()}
        assert {"redfish", "smbios", "lshw", "netbox", "openbmc"}.issubset(sources)

        redfish = client.get("/api/v1/dcim/component-mappings/redfish")
        assert redfish.status_code == 200, redfish.text
        resources = {row["source_type"]: row for row in redfish.json()["resources"]}
        assert resources["NetworkAdapter"]["target_class_slug"] == "network-adapter"
        assert resources["NetworkPort"]["target_class_slug"] == "network-port"
        assert any(f["target_field_key"] == "speed_mbps" for f in resources["NetworkPort"]["fields"])

        missing = client.get("/api/v1/dcim/component-mappings/does-not-exist")
        assert missing.status_code == 404


def test_component_external_mapping_preview_transforms_payload() -> None:
    app = create_app()

    with TestClient(app) as client:
        preview = client.post(
            "/api/v1/dcim/component-mappings/preview",
            json={
                "source": "redfish",
                "resource_type": "NetworkPort",
                "payload": {
                    "CurrentLinkSpeedMbps": 1000,
                    "SupportedLinkCapabilities": [{"LinkSpeedMbps": 1000}, {"LinkSpeedMbps": 10000}],
                    "ActiveLinkTechnology": "Ethernet",
                },
            },
        )
        assert preview.status_code == 200, preview.text
        body = preview.json()
        assert body["target_class_slug"] == "network-port"
        assert body["relation"] == "child_template"
        assert body["mapped_values"]["speed_mbps"] == 1000
        assert body["mapped_values"]["supported_speeds"] == "1000,10000"
        assert body["mapped_values"]["media_type"] == "copper"
        assert body["missing_paths"] == ["PhysicalPortNumber"]

        missing = client.post(
            "/api/v1/dcim/component-mappings/preview",
            json={"source": "redfish", "resource_type": "NotAThing", "payload": {}},
        )
        assert missing.status_code == 404
