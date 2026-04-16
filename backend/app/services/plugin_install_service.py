"""Installasjon av dynamiske backend-plugins (zip-opplasting eller git-klon)."""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

from fastapi import HTTPException

from app.core.config import Settings

_SLUG_RE = re.compile(r"^[a-z][a-z0-9_.-]{1,62}$", re.IGNORECASE)
_MAX_ZIP_BYTES = 8 * 1024 * 1024


def plugins_root(settings: Settings) -> Path:
    return Path(settings.plugins_path).expanduser().resolve()


def installed_dir(settings: Settings) -> Path:
    root = plugins_root(settings)
    out = root / "installed"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_slug(slug: str) -> str:
    s = slug.strip()
    if not _SLUG_RE.fullmatch(s):
        raise HTTPException(
            status_code=400,
            detail="Ugyldig slug: bruk 2–63 tegn, start med bokstav, kun a-z, 0-9, _, . og -.",
        )
    return s


def _safe_extract_zip_member(dest: Path, member_name: str) -> Path:
    if member_name.startswith("/") or ".." in Path(member_name).parts:
        raise HTTPException(status_code=400, detail="Ugyldig sti i ZIP-fil")
    target = (dest / member_name).resolve()
    if not str(target).startswith(str(dest.resolve())):
        raise HTTPException(status_code=400, detail="ZIP prøver å skrive utenfor målkatalog")
    return target


def extract_uploaded_zip(zip_bytes: bytes, dest: Path) -> None:
    if len(zip_bytes) > _MAX_ZIP_BYTES:
        raise HTTPException(status_code=400, detail="ZIP-filen er for stor (maks 8 MiB)")
    dest.mkdir(parents=True, exist_ok=True)
    tmp = dest.parent / f".extract-{dest.name}.zip"
    try:
        tmp.write_bytes(zip_bytes)
        with zipfile.ZipFile(tmp, "r") as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                out_path = _safe_extract_zip_member(dest, info.filename)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(info, "r") as src, out_path.open("wb") as dst:
                    shutil.copyfileobj(src, dst)
    finally:
        tmp.unlink(missing_ok=True)


def _find_plugin_py_files(root: Path) -> list[str]:
    out: list[str] = []
    for p in root.rglob("plugin.py"):
        try:
            rel = p.relative_to(root)
            out.append(str(rel).replace("\\", "/"))
        except ValueError:
            continue
    return sorted(out)


def git_ls_remote_refs(git_url: str, *, timeout_s: int = 60) -> list[str]:
    proc = subprocess.run(
        ["git", "ls-remote", "--heads", "--tags", git_url],
        capture_output=True,
        text=True,
        timeout=timeout_s,
        check=False,
    )
    if proc.returncode != 0:
        raise HTTPException(
            status_code=400,
            detail=f"git ls-remote feilet: {(proc.stderr or proc.stdout or '').strip()[:800]}",
        )
    names: list[str] = []
    for line in proc.stdout.splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        ref = parts[1]
        if ref.startswith("refs/heads/"):
            names.append(ref.removeprefix("refs/heads/"))
        elif ref.startswith("refs/tags/"):
            names.append(ref.removeprefix("refs/tags/"))
    return sorted(set(names))


def scan_git_for_plugins(git_url: str, ref: str, *, timeout_s: int = 120) -> dict[str, object]:
    ref = ref.strip() or "main"
    with tempfile.TemporaryDirectory(prefix="freehci-git-scan-") as tmp:
        tmp_path = Path(tmp)
        clone_dest = tmp_path / "repo"
        proc = subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", ref, git_url, str(clone_dest)],
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
        if proc.returncode != 0:
            proc2 = subprocess.run(
                ["git", "clone", "--depth", "1", git_url, str(clone_dest)],
                capture_output=True,
                text=True,
                timeout=timeout_s,
                check=False,
            )
            if proc2.returncode != 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"git clone feilet for ref «{ref}»: "
                    f"{(proc.stderr or proc.stdout or proc2.stderr or proc2.stdout or '').strip()[:800]}",
                )
            proc3 = subprocess.run(
                ["git", "-C", str(clone_dest), "checkout", ref],
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            if proc3.returncode != 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"git checkout «{ref}» feilet: {(proc3.stderr or proc3.stdout or '').strip()[:500]}",
                )
        rels = _find_plugin_py_files(clone_dest)
        return {"ref_used": ref, "plugin_py_relative_paths": rels}


def install_plugin_tree(source_dir: Path, dest: Path) -> None:
    if dest.exists():
        raise HTTPException(status_code=409, detail="Målkatalog finnes allerede — velg annen slug.")
    if not (source_dir / "plugin.py").is_file():
        raise HTTPException(status_code=400, detail="Kilden mangler plugin.py på rot etter utpakking.")
    shutil.copytree(source_dir, dest)


def install_from_git(
    settings: Settings,
    *,
    git_url: str,
    ref: str,
    slug: str,
    plugin_subpath: str | None,
) -> dict[str, str]:
    slug = validate_slug(slug)
    dest = installed_dir(settings) / slug
    if dest.exists():
        raise HTTPException(status_code=409, detail="Plugin med denne slugen er allerede installert.")
    ref = ref.strip() or "main"
    sub = (plugin_subpath or "").strip().strip("/").replace("\\", "/")
    with tempfile.TemporaryDirectory(prefix="freehci-git-install-") as tmp:
        clone_dest = Path(tmp) / "repo"
        proc = subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", ref, git_url, str(clone_dest)],
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        if proc.returncode != 0:
            proc2 = subprocess.run(
                ["git", "clone", "--depth", "1", git_url, str(clone_dest)],
                capture_output=True,
                text=True,
                timeout=180,
                check=False,
            )
            if proc2.returncode != 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"git clone feilet: {(proc2.stderr or proc2.stdout or '').strip()[:800]}",
                )
            proc3 = subprocess.run(
                ["git", "-C", str(clone_dest), "checkout", ref],
                capture_output=True,
                text=True,
                timeout=90,
                check=False,
            )
            if proc3.returncode != 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"git checkout feilet: {(proc3.stderr or proc3.stdout or '').strip()[:500]}",
                )
        src = clone_dest / sub if sub else clone_dest
        if not src.is_dir():
            raise HTTPException(status_code=400, detail=f"plugin_subpath finnes ikke: {sub or '(rot)'}")
        install_plugin_tree(src, dest)
    return {"slug": slug, "path": str(dest), "restart_hint": "Start API på nytt for å laste inn pluginen."}


def install_from_zip_bytes(settings: Settings, *, slug: str, zip_bytes: bytes) -> dict[str, str]:
    slug = validate_slug(slug)
    dest = installed_dir(settings) / slug
    if dest.exists():
        raise HTTPException(status_code=409, detail="Plugin med denne slugen er allerede installert.")
    with tempfile.TemporaryDirectory(prefix="freehci-zip-") as tmp:
        tmp_path = Path(tmp)
        extract_uploaded_zip(zip_bytes, tmp_path)
        # Tillat én rotmappe i ZIP: foo/plugin.py → bruk foo som kilde
        root = tmp_path
        entries = [p for p in tmp_path.iterdir() if p.name not in (".",)]
        if len(entries) == 1 and entries[0].is_dir() and not (tmp_path / "plugin.py").is_file():
            root = entries[0]
        install_plugin_tree(root, dest)
    return {"slug": slug, "path": str(dest), "restart_hint": "Start API på nytt for å laste inn pluginen."}


def list_installed(settings: Settings) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for child in sorted(installed_dir(settings).iterdir()):
        if not child.is_dir():
            continue
        has = (child / "plugin.py").is_file()
        out.append({"slug": child.name, "path": str(child), "has_plugin_py": has})
    return out


def slug_from_git_url(git_url: str) -> str:
    base = git_url.rstrip("/").split("/")[-1]
    if base.endswith(".git"):
        base = base[: -len(".git")]
    base = re.sub(r"[^a-zA-Z0-9_.-]+", "-", base).strip("-").lower()
    if len(base) < 2:
        base = "plugin"
    return base[:63]
