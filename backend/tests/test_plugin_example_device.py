"""Eksempel-plugin: enhets-stubber for DCIM device detail."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_example_plugin_device_hardware_stub() -> None:
    app = create_app()
    with TestClient(app) as client:
        r = client.get("/api/v1/plugins/freehci/example/devices/42/hardware")
        assert r.status_code == 200
        j = r.json()
        assert j["device_id"] == 42
        assert j["kind"] == "hardware_stub"
        assert j["plugin_id"] == "freehci.example"


def test_example_plugin_device_os_stub() -> None:
    app = create_app()
    with TestClient(app) as client:
        r = client.get("/api/v1/plugins/freehci/example/devices/7/os")
        assert r.status_code == 200
        j = r.json()
        assert j["device_id"] == 7
        assert j["kind"] == "os_stub"
        assert j["plugin_id"] == "freehci.example"
