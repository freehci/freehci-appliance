"""Tester for DCIM site geocode endpoint (uten ekte nettverk)."""

import uuid

from fastapi.testclient import TestClient

from app.main import create_app
from app.services.geocoding import GeocodeCandidate


def test_dcim_site_geocode_uses_site_fields(monkeypatch) -> None:
    app = create_app()

    def fake_geocode(query: str, *, limit: int = 5, timeout_s: float = 20.0):  # noqa: ARG001
        assert "Oslo" in query
        return [
            GeocodeCandidate(display_name="Oslo, Norway", latitude=59.9139, longitude=10.7522),
        ]

    monkeypatch.setattr("app.services.geocoding.geocode_nominatim", fake_geocode)

    with TestClient(app) as client:
        slug = f"oslo-dc-{uuid.uuid4().hex[:8]}"
        s = client.post(
            "/api/v1/dcim/sites",
            json={
                "name": "Oslo DC",
                "slug": slug,
                "address_line1": "Karl Johans gate 1",
                "postal_code": "0154",
                "city": "Oslo",
                "country": "Norway",
            },
        )
        assert s.status_code == 200, s.text
        site_id = s.json()["id"]

        r = client.post(f"/api/v1/dcim/sites/{site_id}/geocode", json={"limit": 5})
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["candidates"]
        assert data["candidates"][0]["display_name"] == "Oslo, Norway"

