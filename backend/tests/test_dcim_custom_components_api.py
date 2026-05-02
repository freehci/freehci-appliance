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
