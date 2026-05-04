"""API-tester for NetBox Device Type Library-import."""

from __future__ import annotations

import io
import zipfile

from fastapi.testclient import TestClient

from app.main import create_app


def _zip_bytes(files: dict[str, str | bytes]) -> bytes:
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return bio.getvalue()


def _dtl_zip(model: str = "TestSwitch 1000", slug: str = "testswitch-1000") -> bytes:
    yaml_text = f"""manufacturer: Example Networks
model: {model}
slug: {slug}
part_number: TS-1000
u_height: 1
is_full_depth: true
front_image: true
rear_image: true
interfaces:
  - name: ge-0/0/0
    type: 1000base-t
  - name: ge-0/0/1
    type: weird-fabric-port
power-ports:
  - name: PSU 1
    type: iec-60320-c14
    maximum_draw: 750
front-ports:
  - name: Front 1
    type: 8p8c
    rear_port: Rear 1
rear-ports:
  - name: Rear 1
    type: 8p8c
    positions: 1
"""
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="20"></svg>'
    return _zip_bytes(
        {
            f"devicetype-library-master/device-types/Example Networks/{slug}.yaml": yaml_text,
            f"devicetype-library-master/elevation-images/Example Networks/{slug}.front.svg": svg,
            f"devicetype-library-master/elevation-images/Example Networks/{slug}.rear.svg": svg,
        }
    )


def test_netbox_dtl_upload_rejects_path_traversal() -> None:
    app = create_app()
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/dcim/netbox-dtl/imports/upload",
            files={"file": ("bad.zip", _zip_bytes({"../evil.yaml": "bad: true"}), "application/zip")},
        )
        assert res.status_code == 400


def test_netbox_dtl_upload_indexes_preview_and_apply_is_idempotent() -> None:
    app = create_app()
    with TestClient(app) as client:
        upload = client.post(
            "/api/v1/dcim/netbox-dtl/imports/upload",
            files={"file": ("netbox-dtl.zip", _dtl_zip(), "application/zip")},
        )
        assert upload.status_code == 200, upload.text
        import_run = upload.json()
        assert import_run["item_count"] == 1
        assert import_run["manufacturer_count"] == 1
        assert import_run["image_count"] == 2
        assert import_run["component_template_count"] == 5

        items = client.get(f"/api/v1/dcim/netbox-dtl/items?import_id={import_run['id']}")
        assert items.status_code == 200, items.text
        item = items.json()[0]
        assert item["manufacturer"] == "Example Networks"
        assert item["component_counts_json"] == {"interfaces": 2, "power-ports": 1, "front-ports": 1, "rear-ports": 1}

        preview = client.post(
            "/api/v1/dcim/netbox-dtl/preview",
            json={"import_id": import_run["id"], "limit": 10},
        )
        assert preview.status_code == 200, preview.text
        assert preview.json()["items"][0]["action"] == "create_device_model"
        assert preview.json()["items"][0]["front_image"] is True

        apply_one = client.post(
            "/api/v1/dcim/netbox-dtl/apply",
            json={"import_id": import_run["id"], "limit": 10},
        )
        assert apply_one.status_code == 200, apply_one.text
        applied = apply_one.json()
        assert applied["created_count"] == 1
        assert applied["updated_count"] == 0
        assert applied["items"][0]["images_imported"] == 2
        assert applied["items"][0]["templates_imported"] == 5
        model_id = applied["items"][0]["device_model_id"]

        model = client.get(f"/api/v1/dcim/device-models/{model_id}")
        assert model.status_code == 200, model.text
        assert model.json()["has_image_front_file"] is True
        assert model.json()["has_image_back_file"] is True

        templates = client.get(f"/api/v1/dcim/device-models/{model_id}/templates")
        assert templates.status_code == 200, templates.text
        template_rows = templates.json()
        assert len(template_rows) == 5
        ge0 = next(row for row in template_rows if row["name"] == "ge-0/0/0")
        assert ge0["normalized_json"]["speed_mbps"] == 1000
        assert ge0["normalized_json"]["media_type"] == "copper"
        assert ge0["quality_score"] == 100
        weird = next(row for row in template_rows if row["name"] == "ge-0/0/1")
        assert "unknown_interface_type:weird-fabric-port" in weird["quality_warnings_json"]
        power = next(row for row in template_rows if row["component_type"] == "power-ports")
        assert power["normalized_json"]["maximum_draw_watts"] == 750
        assert power["normalized_json"]["connector_type"] == "iec-60320-c14"

        quality = client.get(f"/api/v1/dcim/device-models/{model_id}/template-quality")
        assert quality.status_code == 200, quality.text
        assert quality.json()["template_count"] == 5
        assert quality.json()["warning_count"] >= 1

        renormalized = client.post(f"/api/v1/dcim/device-models/{model_id}/templates/renormalize")
        assert renormalized.status_code == 200, renormalized.text
        assert len(renormalized.json()) == 5

        apply_two = client.post(
            "/api/v1/dcim/netbox-dtl/apply",
            json={"import_id": import_run["id"], "limit": 10},
        )
        assert apply_two.status_code == 200, apply_two.text
        assert apply_two.json()["created_count"] == 0
        assert apply_two.json()["updated_count"] == 1


def test_netbox_dtl_apply_accepts_large_device_model_images() -> None:
    yaml_text = """manufacturer: Example Networks
model: Large Image Switch
slug: large-image-switch
front_image: true
"""
    large_svg = b'<svg xmlns="http://www.w3.org/2000/svg">' + (b" " * (3 * 1024 * 1024)) + b"</svg>"
    app = create_app()
    with TestClient(app) as client:
        upload = client.post(
            "/api/v1/dcim/netbox-dtl/imports/upload",
            files={
                "file": (
                    "netbox-dtl.zip",
                    _zip_bytes(
                        {
                            "devicetype-library-master/device-types/Example Networks/large-image-switch.yaml": yaml_text,
                            "devicetype-library-master/elevation-images/Example Networks/large-image-switch.front.svg": large_svg,
                        }
                    ),
                    "application/zip",
                )
            },
        )
        assert upload.status_code == 200, upload.text

        apply_res = client.post(
            "/api/v1/dcim/netbox-dtl/apply",
            json={"import_id": upload.json()["id"], "limit": 10},
        )
        assert apply_res.status_code == 200, apply_res.text
        applied = apply_res.json()
        assert applied["items"][0]["images_imported"] == 1

        model = client.get(f"/api/v1/dcim/device-models/{applied['items'][0]['device_model_id']}")
        assert model.status_code == 200, model.text
        assert model.json()["has_image_front_file"] is True


def test_netbox_dtl_github_download_can_be_mocked(monkeypatch) -> None:
    from app.services import netbox_device_type_library as svc

    class _FakeResponse:
        content = _dtl_zip(model="GitHub Switch", slug="github-switch")

        def raise_for_status(self) -> None:
            return None

    class _FakeAsyncClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args) -> None:
            return None

        async def get(self, url: str) -> _FakeResponse:
            assert "devicetype-library" in url
            return _FakeResponse()

    monkeypatch.setattr(svc.httpx, "AsyncClient", _FakeAsyncClient)
    app = create_app()
    with TestClient(app) as client:
        res = client.post("/api/v1/dcim/netbox-dtl/imports/github", json={"branch": "master"})
        assert res.status_code == 200, res.text
        assert res.json()["source"] == "github"
