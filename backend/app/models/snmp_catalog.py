"""SNMP MIB-metadata og IANA enterprise-register (database)."""

from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SnmpIanaEnterprise(Base):
    """IANA Private Enterprise Numbers (synkronisert fra enterprise-numbers.txt)."""

    __tablename__ = "snmp_iana_enterprises"

    pen: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    organization: Mapped[str] = mapped_column(String(1024), nullable=False)


class SnmpMibFileMeta(Base):
    """Metadata per opplastet MIB-kildefil (filnavn = nøkkel, matcher disk i MIB_ROOT)."""

    __tablename__ = "snmp_mib_file_meta"

    filename: Mapped[str] = mapped_column(String(255), primary_key=True)
    module_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    enterprise_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    compile_status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    compile_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    compiled_module_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    compiled_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    missing_import_modules_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
