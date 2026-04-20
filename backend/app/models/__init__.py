from app.models.base import Base

# Importer sideeffekt: registrer tabeller på Base.metadata (Alembic, create_all).
# Tenant før DCIM (sites har FK til tenants).
import app.models.tenant  # noqa: F401
import app.models.dcim  # noqa: F401
import app.models.iam  # noqa: F401
import app.models.tenant_access  # noqa: F401
import app.models.ipam  # noqa: F401
import app.models.snmp_catalog  # noqa: F401
import app.models.network_scan  # noqa: F401

__all__ = ["Base"]
