"""Skjemaer for plugin-installasjon (Git / ZIP)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class GitScanRequest(BaseModel):
    git_url: str = Field(..., min_length=8, description="HTTPS- eller SSH-URL til repo")
    ref: str = Field(default="main", max_length=255, description="Branch eller tag")


class GitRefsResponse(BaseModel):
    refs: list[str]


class GitScanResponse(BaseModel):
    ref_used: str
    plugin_py_relative_paths: list[str]


class GitInstallRequest(BaseModel):
    git_url: str = Field(..., min_length=8)
    ref: str = Field(default="main", max_length=255)
    slug: str = Field(..., min_length=2, max_length=63, description="Unik katalognavn under installed/")
    plugin_subpath: str | None = Field(
        default=None,
        max_length=512,
        description="Relativ sti inne i repo der plugin.py ligger (tom = repo-rot)",
    )


class PluginInstallResult(BaseModel):
    slug: str
    path: str
    restart_hint: str


class InstalledPluginRow(BaseModel):
    slug: str
    path: str
    has_plugin_py: bool


class InstalledPluginListResponse(BaseModel):
    items: list[InstalledPluginRow]
