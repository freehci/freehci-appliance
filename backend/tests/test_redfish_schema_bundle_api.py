"""API-tester for Redfish DSP8010 schema bundle import."""

from __future__ import annotations

import io
import json
import zipfile

from fastapi.testclient import TestClient

from app.main import create_app


def _zip_bytes(files: dict[str, object]) -> bytes:
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            if isinstance(content, (dict, list)):
                zf.writestr(name, json.dumps(content))
            else:
                zf.writestr(name, str(content))
    return bio.getvalue()


def _processor_schema_zip() -> bytes:
    return _zip_bytes(
        {
            "DSP8010/json-schema/Processor.v1_0_0.json": {
                "$id": "https://redfish.dmtf.org/schemas/v1/Processor.v1_0_0.json",
                "title": "Processor",
                "type": "object",
                "required": ["Id", "@odata.type"],
                "properties": {
                    "Id": {"type": "string"},
                    "@odata.type": {"type": "string"},
                    "Socket": {"type": "string"},
                    "TotalCores": {"type": "integer"},
                },
            },
            "DSP8010/csdl/Processor_v1.xml": (
                '<edmx:Edmx xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx">'
                '<edmx:DataServices><Schema xmlns="http://docs.oasis-open.org/odata/ns/edm" '
                'Namespace="Processor.v1_0_0"/></edmx:DataServices></edmx:Edmx>'
            ),
            "DSP8010/openapi/openapi.json": {"openapi": "3.0.0", "info": {"title": "Redfish", "version": "1.0"}},
            "DSP8010/dictionaries/Resource.json": {"Language": "en"},
        }
    )


def test_redfish_schema_bundle_upload_rejects_path_traversal() -> None:
    app = create_app()
    bad_zip = _zip_bytes({"../evil.json": {"bad": True}})
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/dcim/redfish/schema-bundles/upload",
            files={"file": ("bad.zip", bad_zip, "application/zip")},
        )
        assert res.status_code == 400


def test_redfish_schema_bundle_upload_indexes_resources_and_previews_inventory() -> None:
    app = create_app()
    with TestClient(app) as client:
        seed = client.post("/api/v1/dcim/component-classes/seed-standard")
        assert seed.status_code == 200, seed.text

        upload = client.post(
            "/api/v1/dcim/redfish/schema-bundles/upload",
            files={"file": ("DSP8010_2026.1.zip", _processor_schema_zip(), "application/zip")},
        )
        assert upload.status_code == 200, upload.text
        bundle = upload.json()
        assert bundle["json_schema_count"] == 1
        assert bundle["csdl_count"] == 1
        assert bundle["openapi_count"] == 1
        assert bundle["dictionaries_count"] == 1

        resources = client.get(f"/api/v1/dcim/redfish/schema-bundles/{bundle['id']}/resources")
        assert resources.status_code == 200, resources.text
        assert any(row["resource_type"] == "Processor" and row["format"] == "json_schema" for row in resources.json())

        payload = {
            "@odata.type": "#Processor.v1_0_0.Processor",
            "Id": "CPU1",
            "Name": "CPU 1",
            "Socket": "CPU.Socket.1",
            "TotalCores": 16,
        }
        preview = client.post(
            "/api/v1/dcim/redfish/inventory/preview",
            json={"bundle_id": bundle["id"], "payload": payload},
        )
        assert preview.status_code == 200, preview.text
        first = preview.json()["resources"][0]
        assert first["resource_type"] == "Processor"
        assert first["validation"]["schema_known"] is True
        assert first["validation"]["valid"] is True
        assert first["component_preview"]["target_class_slug"] == "processor"

        apply = client.post(
            "/api/v1/dcim/redfish/inventory/apply",
            json={"bundle_id": bundle["id"], "payload": payload},
        )
        assert apply.status_code == 200, apply.text
        assert apply.json()["applied_count"] == 1
        assert apply.json()["resources"][0]["apply_result"]["component"]["class_id"] > 0


def test_redfish_schema_bundle_download_can_be_mocked(monkeypatch) -> None:
    from app.services import redfish_schema_bundle as svc

    class _FakeResponse:
        content = _zip_bytes(
            {
                "DSP8010/json-schema/Memory.v1_0_0.json": {
                    "$id": "https://redfish.dmtf.org/schemas/v1/Memory.v1_0_0.json",
                    "title": "Memory",
                    "type": "object",
                }
            }
        )

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
            assert url == "https://example.test/DSP8010.zip"
            return _FakeResponse()

    monkeypatch.setattr(svc.httpx, "AsyncClient", _FakeAsyncClient)
    app = create_app()
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/dcim/redfish/schema-bundles/download",
            json={"url": "https://example.test/DSP8010.zip"},
        )
        assert res.status_code == 200, res.text
        assert res.json()["source"] == "download"
