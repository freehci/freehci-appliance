"""Kompiler ASN.1 MIB-er til PySNMP Python-moduler via pysmi."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from pysmi.borrower import PyFileBorrower
from pysmi.codegen import PySnmpCodeGen
from pysmi.compiler import MibCompiler
from pysmi.parser.smiv1compat import SmiV1CompatParser
from pysmi.reader.url import get_readers_from_urls
from pysmi.searcher.pyfile import PyFileSearcher
from pysmi.searcher.pypackage import PyPackageSearcher
from pysmi.searcher.stub import StubSearcher
from pysmi.writer.pyfile import PyFileWriter

from app.core.config import Settings

# pysmi MibStatus-strenger som betyr at PySNMP kan bruke modulen (.py finnes eller er hentet).
_COMPILE_OK = frozenset({"compiled", "untouched", "borrowed"})


def compile_status_is_success(status: str) -> bool:
    return status in _COMPILE_OK


def _build_compiler(settings: Settings, *, cache_dir: str | None) -> MibCompiler:
    mib_root = settings.mib_root_path.resolve()
    compiled_root = settings.mib_compiled_path.resolve()
    compiled_root.mkdir(parents=True, exist_ok=True)

    # Lokale MIB-er først; deretter ASN.1 fra pysnmp (samme som mibdump-default).
    # Uten HTTP-kilde blir aldri SNMPv2-SMI/SNMPv2-TC parsert → symbolTable mangler og codegen feiler.
    mib_sources = [
        mib_root.as_uri() + "/",
        "https://mibs.pysnmp.com/asn1/@mib@",
    ]
    mib_stubs = [x for x in PySnmpCodeGen.baseMibs if x not in PySnmpCodeGen.fakeMibs]
    mib_borrowers = [
        ("https://mibs.pysnmp.com:443/mibs/notexts/@mib@", False),
        ("https://mibs.pysnmp.com:443/mibs/fulltexts/@mib@", True),
    ]

    borrowers = [
        PyFileBorrower(x[1], genTexts=mib_borrowers[x[0]][1])
        for x in enumerate(
            get_readers_from_urls(
                *[m[0] for m in mib_borrowers],
                **dict(lowcaseMatching=False),
            ),
        )
    ]

    searchers: list[Any] = [PyFileSearcher(str(compiled_root))]
    for pkg in PySnmpCodeGen.defaultMibPackages:
        searchers.append(PyPackageSearcher(pkg))
    searchers.append(StubSearcher(*mib_stubs))

    file_writer = PyFileWriter(str(compiled_root)).set_options(pyCompile=True, pyOptimizationLevel=0)
    code_gen = PySnmpCodeGen()
    parser = SmiV1CompatParser(tempdir=cache_dir or tempfile.mkdtemp(prefix="pysmi-"))

    mib_compiler = MibCompiler(parser, code_gen, file_writer)
    mib_compiler.add_sources(
        *get_readers_from_urls(*mib_sources, **dict(fuzzyMatching=True)),
    )
    mib_compiler.add_searchers(*searchers)
    mib_compiler.add_borrowers(*borrowers)
    return mib_compiler


def compile_mib_modules(
    settings: Settings,
    module_names: list[str],
    *,
    ignore_errors: bool = False,
    rebuild: bool = False,
) -> dict[str, tuple[str, str | None, str | None]]:
    """Kompiler MIB-modulnavn. Returnerer modul -> (status, feilmelding, kanonisk modulnavn fra pysmi)."""
    if not module_names:
        return {}

    cache_dir = tempfile.mkdtemp(prefix="pysmi-cache-")
    mib_compiler = _build_compiler(settings, cache_dir=cache_dir)
    processed = mib_compiler.compile(
        *module_names,
        **dict(
            noDeps=False,
            rebuild=rebuild,
            dryRun=False,
            genTexts=False,
            writeMibs=True,
            ignoreErrors=ignore_errors,
        ),
    )

    def status_for(requested: str) -> tuple[str, str | None, str | None]:
        ru = requested.upper()
        for k, v in processed.items():
            if k.upper() == ru:
                err = None
                if str(v) == "failed" and hasattr(v, "error"):
                    err = str(getattr(v, "error", ""))
                return (str(v), err, k)
        if requested in mib_compiler.failedMibs:
            return ("failed", str(mib_compiler.failedMibs[requested]), None)
        return ("missing", "MIB ikke funnet eller ikke prosessert", None)

    return {req: status_for(req) for req in module_names}


def compiled_py_path(settings: Settings, module_name: str) -> Path | None:
    """Returner sti til .py om den finnes etter kompilering."""
    root = settings.mib_compiled_path.resolve()
    if not root.is_dir():
        return None
    for p in root.glob("*.py"):
        if p.stem.upper() == module_name.upper():
            return p
    return None
