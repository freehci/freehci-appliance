"""Skjemaer for IPAM API (IPv4 prefiks per site)."""

from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Ipv4PrefixCreate(BaseModel):
    site_id: int
    name: str = Field(..., min_length=1, max_length=255)
    cidr: str = Field(..., min_length=1, max_length=32)
    description: str | None = None

    @field_validator("cidr")
    @classmethod
    def cidr_not_empty(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("cidr kan ikke være tom")
        return s


class Ipv4PrefixUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    cidr: str | None = Field(None, min_length=1, max_length=32)
    description: str | None = None

    @field_validator("cidr")
    @classmethod
    def cidr_strip(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip()
        if not s:
            raise ValueError("cidr kan ikke være tom")
        return s


class Ipv4PrefixRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    site_id: int
    name: str
    cidr: str
    description: str | None
    created_at: dt.datetime
