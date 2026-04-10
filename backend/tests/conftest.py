"""Opprett tabeller for tester (samme metadata som Alembic)."""

import os
import tempfile
from pathlib import Path

# Filbasert SQLite i temp-katalog: én DB for alle tilkoblinger (:memory: ville gitt tom DB per sesjon).
_tmp_db_dir = Path(tempfile.mkdtemp(prefix="freehci-pytest-"))
_tmp_db = _tmp_db_dir / "test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_db.as_posix()}"
os.environ["FREEHCI_SKIP_AUTH"] = "1"
_upload_root = Path(tempfile.mkdtemp(prefix="freehci-uploads-"))
os.environ["UPLOAD_ROOT"] = str(_upload_root)
_mib_root = Path(tempfile.mkdtemp(prefix="freehci-mibs-"))
os.environ["MIB_ROOT"] = str(_mib_root)

from app.core.config import get_settings

get_settings.cache_clear()

import pytest

import app.models.admin_account  # noqa: F401
import app.models.dcim  # noqa: F401
import app.models.ipam  # noqa: F401 — tabeller for IPAM + FK fra DCIM
from app.core.db import engine
from app.models.base import Base


@pytest.fixture(scope="session", autouse=True)
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
