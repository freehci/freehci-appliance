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

# Vanlige avhengigheter som ikke er «leverandørens» hovedmodul ved én-fil-kompilering.
_PYSMI_INFRA_MODULES = frozenset(
    {
        "RFC-1212",
        "RFC1212",
        "RFC-1215",
        "RFC1155-SMI",
        "RFC1158-MIB",
        "RFC1065-SMI",
        "RFC1213-MIB",
        "SNMPv2-SMI",
        "SNMPv2-TC",
        "SNMPv2-CONF",
        "SNMPv2-TM",
        "SNMPv2-MIB",
        "SNMP-FRAMEWORK-MIB",
        "IANAifType-MIB",
        "INET-ADDRESS-MIB",
        "IP-MIB",
        "IF-MIB",
        "ASN1",
        "ASN1-ENUMERATION",
        "ASN1-REFINEMENT",
    },
)


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
    resolution_hints: list[str] | None = None,
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

    def _alnum_upper(s: str) -> str:
        return "".join(c for c in s.upper() if c.isalnum())

    def _tuple_for_key(k: str, v: Any) -> tuple[str, str | None, str | None]:
        st = str(v)
        err = None
        if st == "failed" and hasattr(v, "error"):
            err = str(getattr(v, "error", ""))
        elif st == "missing":
            err = (
                f'ASN.1-kilde for modul «{k}» ble ikke funnet (sjekk DEFINITIONS-navn, '
                f"filnavn og at filen ligger i MIB_ROOT)"
            )
        elif st == "unprocessed":
            err = "Modulen ble ikke ferdigskrevet (ofte stopp pga. feil i en avhengighet)"
        return (st, err, k)

    def status_for(requested: str) -> tuple[str, str | None, str | None]:
        cands = list(dict.fromkeys([requested, *(resolution_hints or [])]))
        for cand in cands:
            ru = cand.upper()
            for k, v in processed.items():
                if k.upper() == ru:
                    return _tuple_for_key(k, v)

        for cand in cands:
            ca = _alnum_upper(cand)
            if len(ca) >= 3:
                for k, v in processed.items():
                    if _alnum_upper(k) == ca:
                        return _tuple_for_key(k, v)

        for cand in cands:
            ar = _alnum_upper(cand)
            if ar:
                for k, v in processed.items():
                    ak = _alnum_upper(k)
                    if len(ar) >= 4 and len(ak) >= 4 and (ar in ak or ak in ar):
                        return _tuple_for_key(k, v)

        missing_msgs: list[str] = []
        for k, v in processed.items():
            if str(v) == "missing":
                missing_msgs.append(f"{k}: mangler ASN.1-kilde")
        if missing_msgs:
            return ("missing", "; ".join(missing_msgs[:12]), None)

        failed_msgs: list[str] = []
        for k, v in processed.items():
            if str(v) != "failed":
                continue
            msg = str(getattr(v, "error", "")) if hasattr(v, "error") else ""
            failed_msgs.append(f"{k}: {msg}" if msg else f"{k}: failed")
        if failed_msgs:
            return ("failed", "; ".join(failed_msgs[:10]), None)

        if len(processed) == 1:
            k, v = next(iter(processed.items()))
            return _tuple_for_key(k, v)

        unproc = [k for k, v in processed.items() if str(v) == "unprocessed"]
        if unproc:
            return (
                "failed",
                f"Kompilering stoppet (uprossesserte moduler: {', '.join(unproc[:8])})",
                None,
            )

        vendor_ok = [
            (k, v)
            for k, v in processed.items()
            if str(v) in _COMPILE_OK and k not in _PYSMI_INFRA_MODULES
        ]
        if len(vendor_ok) == 1:
            k, v = vendor_ok[0]
            return _tuple_for_key(k, v)

        keys = sorted(processed.keys())
        hint = ", ".join(keys[:30]) + ("…" if len(keys) > 30 else "")
        # Engelsk, stabil form — oversettes i frontend (i18n).
        return (
            "missing",
            f"Could not map the requested module to the pysmi compiler result "
            f"({len(processed)} modules: {hint}).",
            None,
        )

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
