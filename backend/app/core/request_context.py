"""Request-lokal aktør for audit og token-scopes."""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, field

IPAM_SCOPES = frozenset({"ipam:read", "ipam:alloc", "ipam:admin"})
_ALLOC_HINTS = (
    "/ensure",
    "/request",
    "/request-batch",
    "/allocate",
    "/bind",
    "/release",
)


@dataclass(frozen=True)
class AuthActor:
    actor_type: str = "system"
    actor_id: int | None = None
    actor_name: str | None = None
    scopes: frozenset[str] | None = None
    token_id: int | None = None


_actor: ContextVar[AuthActor] = ContextVar("auth_actor", default=AuthActor())


def set_actor(actor: AuthActor) -> None:
    _actor.set(actor)


def get_actor() -> AuthActor:
    return _actor.get()


def ipam_scope_allows(method: str, path: str, scopes: frozenset[str] | None) -> bool:
    """None/tomt = ubegrenset (legacy JWT og gamle nøkler)."""
    if not scopes:
        return True
    if "ipam:admin" in scopes:
        return True
    m = method.upper()
    if m == "GET" or m == "HEAD":
        return bool(scopes & {"ipam:read", "ipam:alloc"})
    if m == "POST" and any(h in path for h in _ALLOC_HINTS):
        return "ipam:alloc" in scopes
    return False
