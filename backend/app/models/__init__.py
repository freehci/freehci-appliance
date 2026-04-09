from app.models.base import Base

# Importer sideeffekt: registrer DCIM-tabeller på Base.metadata (Alembic, create_all).
import app.models.dcim  # noqa: F401
import app.models.iam  # noqa: F401
import app.models.ipam  # noqa: F401

__all__ = ["Base"]
