"""Policy: hvilke DCIM-sites en IAM-bruker (users.id) effektivt kan nå.

Kombinerer:
- direkte site-tilgang (`dcim_site_access`) med gyldighetsvindu
- medlemskap i tenant som eier site (`dcim_sites.tenant_id`)
- `tenant_dcim_grants` for samme tenant som brukeren er medlem av (site / rom / rack-scope)
"""

from __future__ import annotations

import datetime as dt

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dcim import Rack, Room, Site, SiteAccessGrant
from app.models.tenant_access import TenantDcimGrant, TenantUserMembership


def _as_utc(t: dt.datetime | None) -> dt.datetime | None:
    if t is None:
        return None
    if t.tzinfo is None:
        return t.replace(tzinfo=dt.UTC)
    return t.astimezone(dt.UTC)


def _window_active(now: dt.datetime, valid_from: dt.datetime | None, valid_to: dt.datetime | None) -> bool:
    vf = _as_utc(valid_from)
    vt = _as_utc(valid_to)
    if vf is not None and now < vf:
        return False
    if vt is not None and now > vt:
        return False
    return True


def list_accessible_site_ids_for_user(
    db: Session,
    user_id: int,
    *,
    now: dt.datetime | None = None,
) -> list[int]:
    """Returnerer sorterte site-id-er brukeren har lesetilgang til via policy over.

    Forvent at `user_id` finnes i `users` når resultatet brukes i API (ellers 404 i router).
    """
    now_ = now or dt.datetime.now(dt.UTC)
    if now_.tzinfo is None:
        now_ = now_.replace(tzinfo=dt.UTC)

    site_ids: set[int] = set()

    for g in db.execute(select(SiteAccessGrant).where(SiteAccessGrant.user_id == user_id)).scalars().all():
        if _window_active(now_, g.valid_from, g.valid_to):
            site_ids.add(g.site_id)

    member_tids = {
        m.tenant_id
        for m in db.execute(select(TenantUserMembership).where(TenantUserMembership.user_id == user_id)).scalars().all()
    }

    sites = list(db.execute(select(Site)).scalars().all())
    site_by_id = {s.id: s for s in sites}
    for s in sites:
        if s.tenant_id in member_tids:
            site_ids.add(s.id)

    rooms = list(db.execute(select(Room)).scalars().all())
    room_to_site = {r.id: r.site_id for r in rooms}

    racks = list(db.execute(select(Rack)).scalars().all())
    rack_to_site: dict[int, int] = {}
    for k in racks:
        sid = room_to_site.get(k.room_id)
        if sid is not None:
            rack_to_site[k.id] = sid

    if member_tids:
        grants = db.execute(
            select(TenantDcimGrant).where(TenantDcimGrant.tenant_id.in_(member_tids)),
        ).scalars().all()
        for gr in grants:
            st = gr.scope_type
            sid_scope = gr.scope_id
            if st == "site":
                if sid_scope in site_by_id:
                    site_ids.add(sid_scope)
            elif st == "room":
                s2 = room_to_site.get(sid_scope)
                if s2 is not None:
                    site_ids.add(s2)
            elif st == "rack":
                s2 = rack_to_site.get(sid_scope)
                if s2 is not None:
                    site_ids.add(s2)

    return sorted(site_ids)


def user_can_access_site(
    db: Session,
    user_id: int,
    site_id: int,
    *,
    now: dt.datetime | None = None,
) -> bool:
    """True dersom `site_id` er i effektiv tilgangsliste for brukeren."""
    return site_id in set(list_accessible_site_ids_for_user(db, user_id, now=now))
