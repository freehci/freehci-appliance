"""Tester for ZIP-utpakking og slug-validering for dynamiske plugins."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest
from fastapi import HTTPException

from app.core.config import Settings
from app.services import plugin_install_service as pis


def test_validate_slug_ok() -> None:
    assert pis.validate_slug("my-plugin_1") == "my-plugin_1"


def test_validate_slug_rejects_dotdot() -> None:
    with pytest.raises(HTTPException):
        pis.validate_slug("..")


def test_safe_extract_rejects_path_traversal(tmp_path: Path) -> None:
    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w") as zf:
        zf.writestr("../evil.txt", b"x")
    zbuf.seek(0)
    raw = zbuf.read()
    dest = tmp_path / "out"
    with pytest.raises(HTTPException):
        pis.extract_uploaded_zip(raw, dest)


def test_install_zip_flat_plugin_py(tmp_path: Path) -> None:
    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w") as zf:
        zf.writestr("plugin.py", b"# test plugin\n")
    zbuf.seek(0)
    raw = zbuf.read()

    root = tmp_path / "proot"
    settings = Settings(plugins_path=str(root), database_url="sqlite:///:memory:")
    r = pis.install_from_zip_bytes(settings, slug="testplug", zip_bytes=raw)
    assert r["slug"] == "testplug"
    assert (pis.installed_dir(settings) / "testplug" / "plugin.py").is_file()
