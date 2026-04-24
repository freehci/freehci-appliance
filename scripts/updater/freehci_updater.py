#!/usr/bin/env python3
"""FreeHCI host-updater (Debian 13).

Kjører utenfor Docker som root (systemd), og kan trigges av UI via backend-proxy.

Endpoints (localhost):
  POST /update  -> starter oppdatering (asynkront), returnerer {job_id}
  GET  /status  -> status + log-tail

Oppdatering utføres ved å kjøre den samme install-kommandoen som manuell fallback bruker:
  bash -c "$(curl -fsSL https://raw.githubusercontent.com/freehci/freehci-appliance/main/scripts/install-debian13.sh)"
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import threading
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

try:
    import fcntl
except ImportError:
    fcntl = None  # type: ignore[assignment, misc]


HOST = os.environ.get("FREEHCI_UPDATER_HOST", "127.0.0.1")
PORT = int(os.environ.get("FREEHCI_UPDATER_PORT", "8765"))

LOG_PATH = Path(os.environ.get("FREEHCI_UPDATER_LOG", "/var/log/freehci-updater.log"))
STATE_PATH = Path(os.environ.get("FREEHCI_UPDATER_STATE", "/run/freehci-updater/status.json"))
LOCK_PATH = Path(os.environ.get("FREEHCI_UPDATER_LOCK", "/run/freehci-updater/lock"))

INSTALL_CMD = os.environ.get(
    "FREEHCI_UPDATER_INSTALL_CMD",
    'bash -c "$(curl -fsSL https://raw.githubusercontent.com/freehci/freehci-appliance/main/scripts/install-debian13.sh)"',
)

LOG_TAIL_LINES = int(os.environ.get("FREEHCI_UPDATER_LOG_TAIL_LINES", "120"))


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_dirs() -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)


def _read_log_tail_lines(max_lines: int) -> list[str]:
    try:
        data = LOG_PATH.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return []
    lines = data.splitlines()
    if len(lines) <= max_lines:
        return lines
    return lines[-max_lines:]


def _atomic_write_json(path: Path, obj: dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


class _JobState:
    def __init__(self) -> None:
        self._mu = threading.Lock()
        self.running = False
        self.job_id: str | None = None
        self.started_at: str | None = None
        self.finished_at: str | None = None
        self.exit_code: int | None = None
        self.detail: str | None = None

    def to_public(self) -> dict[str, Any]:
        with self._mu:
            return {
                "running": bool(self.running),
                "job_id": self.job_id,
                "started_at": self.started_at,
                "finished_at": self.finished_at,
                "exit_code": self.exit_code,
                "detail": self.detail,
                "log_tail": _read_log_tail_lines(LOG_TAIL_LINES),
            }

    def _persist(self) -> None:
        _atomic_write_json(STATE_PATH, self.to_public())

    def _set(self, **patch: Any) -> None:
        with self._mu:
            for k, v in patch.items():
                setattr(self, k, v)
        self._persist()


STATE = _JobState()

# Åpen fil med advisory flock (Linux). Låsen slippes automatisk når fd lukkes / prosess dør.
_lock_fp: Any = None


def _try_acquire_lock() -> bool:
    global _lock_fp
    _ensure_dirs()
    if fcntl is not None:
        try:
            fp = open(LOCK_PATH, "a+", encoding="utf-8")
        except OSError:
            return False
        try:
            fcntl.flock(fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            fp.close()
            return False
        fp.seek(0)
        fp.truncate()
        fp.write(f"{os.getpid()}\n")
        fp.flush()
        _lock_fp = fp
        return True

    try:
        fd = os.open(str(LOCK_PATH), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    except FileExistsError:
        return False
    try:
        os.write(fd, str(os.getpid()).encode("ascii", errors="ignore"))
    finally:
        os.close(fd)
    return True


def _release_lock() -> None:
    global _lock_fp
    if fcntl is not None and _lock_fp is not None:
        try:
            fcntl.flock(_lock_fp.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        try:
            _lock_fp.close()
        except OSError:
            pass
        _lock_fp = None
        try:
            LOCK_PATH.unlink()
        except FileNotFoundError:
            pass
        except OSError as e:
            try:
                _append_log(f"!! lock unlink failed: {e!r}")
            except Exception:
                pass
        return

    try:
        LOCK_PATH.unlink()
    except FileNotFoundError:
        return


def _reconcile_stale_lock() -> None:
    """Fjern gjenværende lock-fil når ingen holder flock (etter crash/kill -9)."""
    _ensure_dirs()
    if fcntl is not None:
        if not LOCK_PATH.exists():
            return
        try:
            fp = open(LOCK_PATH, "a+", encoding="utf-8")
        except OSError:
            return
        try:
            fcntl.flock(fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            fp.close()
            return
        try:
            fp.close()
        except OSError:
            pass
        try:
            LOCK_PATH.unlink()
        except FileNotFoundError:
            pass
        except OSError as e:
            try:
                _append_log(f"!! stale lock cleanup unlink failed: {e!r}")
            except Exception:
                pass
        return

    # Ikke-Unix: eksisterende O_EXCL-fil — slett hvis ingen kjent jobb (best effort).
    if not LOCK_PATH.is_file():
        return
    try:
        raw = LOCK_PATH.read_text(encoding="utf-8", errors="replace").strip().splitlines()
    except OSError:
        return
    if not raw:
        _release_lock()
        return
    token = raw[0].strip()
    if not token.isdigit():
        _release_lock()
        return
    pid = int(token, 10)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        pass
    except PermissionError:
        return
    else:
        return
    _release_lock()


def _append_log(line: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line.rstrip("\n") + "\n")


def _run_update_job(job_id: str) -> None:
    started = _utcnow().isoformat()
    STATE._set(running=True, job_id=job_id, started_at=started, finished_at=None, exit_code=None, detail=None)
    _append_log(f"==> [{job_id}] update started at {started}")
    _append_log(f"==> [{job_id}] cmd: {INSTALL_CMD}")

    p: subprocess.Popen[str] | None = None
    try:
        p = subprocess.Popen(
            ["bash", "-lc", INSTALL_CMD],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            start_new_session=True,
        )
    except Exception as e:
        finished = _utcnow().isoformat()
        _append_log(f"!! [{job_id}] failed to start: {e!r}")
        STATE._set(running=False, finished_at=finished, exit_code=127, detail="kunne ikke starte oppdatering")
        _release_lock()
        return

    try:
        assert p.stdout is not None
        try:
            for line in p.stdout:
                _append_log(line.rstrip("\n"))
        finally:
            try:
                p.stdout.close()
            except Exception:
                pass

        rc = p.wait()
        finished = _utcnow().isoformat()
        _append_log(f"==> [{job_id}] update finished at {finished} (exit_code={rc})")
        STATE._set(
            running=False,
            finished_at=finished,
            exit_code=int(rc),
            detail="ok" if rc == 0 else "feilet",
        )
    except Exception as e:
        finished = _utcnow().isoformat()
        _append_log(f"!! [{job_id}] unexpected error while running update: {e!r}")
        try:
            if p is not None and p.poll() is None:
                p.send_signal(signal.SIGTERM)
        except Exception:
            pass
        STATE._set(running=False, finished_at=finished, exit_code=127, detail="feilet (uventet avbrudd)")
    finally:
        _release_lock()


def start_update() -> tuple[bool, str | None]:
    if not _try_acquire_lock():
        return (False, None)
    job_id = uuid.uuid4().hex[:12]
    t = threading.Thread(target=_run_update_job, args=(job_id,), daemon=True)
    t.start()
    # Gi status et lite forsprang slik at /status direkte etter /update gir job_id.
    time.sleep(0.05)
    return (True, job_id)


class Handler(BaseHTTPRequestHandler):
    server_version = "freehci-updater/1.0"

    def _json(self, status: int, obj: Any) -> None:
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        if self.path.rstrip("/") == "/status":
            self._json(200, STATE.to_public())
            return
        self._json(404, {"detail": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path.rstrip("/") != "/update":
            self._json(404, {"detail": "not found"})
            return
        ok, job_id = start_update()
        if not ok:
            self._json(409, {"detail": "update already running"})
            return
        self._json(200, {"job_id": job_id})

    def log_message(self, fmt: str, *args: Any) -> None:
        # Unngå å spamme systemd-journal; vi logger til fil i stedet.
        return


def main() -> None:
    _ensure_dirs()
    # Init statefil hvis den mangler
    try:
        if not STATE_PATH.exists():
            STATE._persist()
    except Exception:
        pass

    _reconcile_stale_lock()

    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    _append_log(f"==> updater listening on http://{HOST}:{PORT} (pid={os.getpid()})")
    httpd.serve_forever()


if __name__ == "__main__":
    main()

