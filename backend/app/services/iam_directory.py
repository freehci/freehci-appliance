"""IAM-katalog: personer (`users`), roller, grupper og nestede undergrupper."""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.iam import (
    IamGroup,
    IamGroupSubgroup,
    IamGroupUserMember,
    IamRole,
    IamUserRole,
    User,
)
from app.schemas.iam import (
    IamAssignRoleBody,
    IamGroupAddSubgroupMember,
    IamGroupAddUserMember,
    IamGroupCreate,
    IamGroupDetailRead,
    IamGroupMemberSubgroupRead,
    IamGroupMemberUserRead,
    IamGroupRead,
    IamGroupUpdate,
    IamPersonBrief,
    IamRef,
    IamRoleCreate,
    IamRoleDetailRead,
    IamRoleRead,
    IamRoleUpdate,
    PersonDetailRead,
)
from app.schemas.ipam import UserCreate, UserPatch, UserRead
from app.services import ipam_address as addr_svc


def list_persons(db: Session, *, limit: int = 500) -> list[UserRead]:
    return addr_svc.list_users(db, limit=limit)


def get_person(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def create_person(db: Session, data: UserCreate) -> UserRead:
    return addr_svc.create_user(db, data)


def patch_person(db: Session, row: User, data: UserPatch) -> UserRead:
    patch = data.model_dump(exclude_unset=True)
    for key in ("display_name", "email", "phone", "kind", "notes", "external_subject_id", "identity_provider"):
        if key in patch:
            setattr(row, key, patch[key])
    db.commit()
    db.refresh(row)
    return UserRead.model_validate(row)


def _ancestor_group_ids(db: Session, start_ids: set[int]) -> set[int]:
    """Alle grupper som inneholder minst én av start_ids (direkte eller via undergruppe)."""
    out: set[int] = set(start_ids)
    frontier = list(start_ids)
    while frontier:
        gid = frontier.pop()
        q = select(IamGroupSubgroup.group_id).where(IamGroupSubgroup.child_group_id == gid)
        for (parent_id,) in db.execute(q).all():
            if parent_id not in out:
                out.add(parent_id)
                frontier.append(parent_id)
    return out


def _direct_group_ids_for_user(db: Session, user_id: int) -> set[int]:
    q = select(IamGroupUserMember.group_id).where(IamGroupUserMember.user_id == user_id)
    return {r for (r,) in db.execute(q).all()}


def person_detail(db: Session, row: User) -> PersonDetailRead:
    base = UserRead.model_validate(row)
    role_rows = db.execute(
        select(IamRole.id, IamRole.name, IamRole.slug)
        .join(IamUserRole, IamUserRole.role_id == IamRole.id)
        .where(IamUserRole.user_id == row.id)
        .order_by(IamRole.name),
    ).all()
    roles = [IamRef(id=a, name=b, slug=c) for a, b, c in role_rows]

    direct_gids = _direct_group_ids_for_user(db, row.id)
    eff_gids = _ancestor_group_ids(db, direct_gids) if direct_gids else set()

    def _refs(gids: set[int]) -> list[IamRef]:
        if not gids:
            return []
        q2 = select(IamGroup.id, IamGroup.name, IamGroup.slug).where(IamGroup.id.in_(gids)).order_by(IamGroup.name)
        return [IamRef(id=a, name=b, slug=c) for a, b, c in db.execute(q2).all()]

    groups_direct = _refs(direct_gids)
    groups_effective = _refs(eff_gids)
    return PersonDetailRead(
        **base.model_dump(),
        roles=roles,
        groups_direct=groups_direct,
        groups_effective=groups_effective,
    )


def _descendant_subgroup_ids(db: Session, root: int) -> set[int]:
    """Alle undergruppe-id-er som er nøstet inni `root` (ikke inkl. root selv)."""
    seen: set[int] = set()
    stack = [root]
    while stack:
        g = stack.pop()
        q = select(IamGroupSubgroup.child_group_id).where(IamGroupSubgroup.group_id == g)
        for (cid,) in db.execute(q).all():
            if cid not in seen:
                seen.add(cid)
                stack.append(cid)
    return seen


def list_roles(db: Session) -> list[IamRoleRead]:
    rows = db.execute(select(IamRole).order_by(IamRole.name)).scalars().all()
    return [IamRoleRead.model_validate(r) for r in rows]


def create_role(db: Session, data: IamRoleCreate) -> IamRoleRead:
    row = IamRole(name=data.name.strip(), slug=data.slug, description=data.description, system=False)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="rolle med samme navn eller slug finnes allerede") from None
    db.refresh(row)
    return IamRoleRead.model_validate(row)


def get_role(db: Session, role_id: int) -> IamRole | None:
    return db.get(IamRole, role_id)


def patch_role(db: Session, row: IamRole, data: IamRoleUpdate) -> IamRoleRead:
    patch = data.model_dump(exclude_unset=True)
    if row.system and "name" in patch and patch["name"] is not None and str(patch["name"]).strip() != row.name:
        raise HTTPException(status_code=400, detail="systemrolle kan ikke omdøpes")
    if "name" in patch and patch["name"] is not None:
        row.name = str(patch["name"]).strip()
    if "description" in patch:
        row.description = patch["description"]
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="navn-konflikt for rolle") from None
    db.refresh(row)
    return IamRoleRead.model_validate(row)


def delete_role(db: Session, row: IamRole) -> None:
    if row.system:
        raise HTTPException(status_code=400, detail="kan ikke slette systemrolle")
    db.delete(row)
    db.commit()


def role_detail(db: Session, row: IamRole) -> IamRoleDetailRead:
    n = db.execute(select(func.count()).select_from(IamUserRole).where(IamUserRole.role_id == row.id)).scalar_one()
    base = IamRoleRead.model_validate(row)
    assign_rows = db.execute(
        select(User.id, User.username, User.display_name)
        .join(IamUserRole, IamUserRole.user_id == User.id)
        .where(IamUserRole.role_id == row.id)
        .order_by(User.username),
    ).all()
    assignees = [IamPersonBrief(id=a, username=b, display_name=c) for a, b, c in assign_rows]
    return IamRoleDetailRead(**base.model_dump(), member_count=int(n), assignees=assignees)


def list_groups(db: Session) -> list[IamGroupRead]:
    rows = db.execute(select(IamGroup).order_by(IamGroup.name)).scalars().all()
    return [IamGroupRead.model_validate(r) for r in rows]


def create_group(db: Session, data: IamGroupCreate) -> IamGroupRead:
    row = IamGroup(
        name=data.name.strip(),
        slug=data.slug,
        description=data.description,
        external_subject_id=data.external_subject_id,
        identity_provider=data.identity_provider,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="gruppe med samme navn eller slug finnes allerede") from None
    db.refresh(row)
    return IamGroupRead.model_validate(row)


def get_group(db: Session, group_id: int) -> IamGroup | None:
    return db.get(IamGroup, group_id)


def patch_group(db: Session, row: IamGroup, data: IamGroupUpdate) -> IamGroupRead:
    patch = data.model_dump(exclude_unset=True)
    if "name" in patch and patch["name"] is not None:
        row.name = str(patch["name"]).strip()
    if "description" in patch:
        row.description = patch["description"]
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="navn-konflikt for gruppe") from None
    db.refresh(row)
    return IamGroupRead.model_validate(row)


def delete_group(db: Session, row: IamGroup) -> None:
    db.delete(row)
    db.commit()


def _effective_user_ids_in_group(db: Session, group_id: int) -> set[int]:
    users: set[int] = set()
    q_u = select(IamGroupUserMember.user_id).where(IamGroupUserMember.group_id == group_id)
    users.update(r for (r,) in db.execute(q_u).all())
    q_c = select(IamGroupSubgroup.child_group_id).where(IamGroupSubgroup.group_id == group_id)
    for (cid,) in db.execute(q_c).all():
        users |= _effective_user_ids_in_group(db, cid)
    return users


def group_detail(db: Session, row: IamGroup) -> IamGroupDetailRead:
    base = IamGroupRead.model_validate(row)
    du = db.execute(
        select(User.id, User.username, User.display_name)
        .join(IamGroupUserMember, IamGroupUserMember.user_id == User.id)
        .where(IamGroupUserMember.group_id == row.id)
        .order_by(User.username),
    ).all()
    direct_users = [IamGroupMemberUserRead(user_id=a, username=b, display_name=c) for a, b, c in du]

    ds = db.execute(
        select(IamGroupSubgroup.child_group_id, IamGroup.name, IamGroup.slug)
        .join(IamGroup, IamGroup.id == IamGroupSubgroup.child_group_id)
        .where(IamGroupSubgroup.group_id == row.id)
        .order_by(IamGroup.name),
    ).all()
    direct_subgroups = [
        IamGroupMemberSubgroupRead(child_group_id=a, name=b, slug=c) for a, b, c in ds
    ]
    eff = sorted(_effective_user_ids_in_group(db, row.id))
    return IamGroupDetailRead(
        **base.model_dump(),
        direct_users=direct_users,
        direct_subgroups=direct_subgroups,
        effective_user_ids=eff,
    )


def add_user_to_group(db: Session, group: IamGroup, body: IamGroupAddUserMember) -> None:
    if db.get(User, body.user_id) is None:
        raise HTTPException(status_code=404, detail="person ikke funnet")
    row = IamGroupUserMember(group_id=group.id, user_id=body.user_id)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="person er allerede medlem av gruppen") from None


def remove_user_from_group(db: Session, group: IamGroup, user_id: int) -> None:
    r = db.execute(
        delete(IamGroupUserMember).where(
            IamGroupUserMember.group_id == group.id,
            IamGroupUserMember.user_id == user_id,
        )
    )
    if r.rowcount == 0:
        raise HTTPException(status_code=404, detail="medlemskap ikke funnet")
    db.commit()


def add_subgroup_to_group(db: Session, group: IamGroup, body: IamGroupAddSubgroupMember) -> None:
    child_id = body.child_group_id
    if child_id == group.id:
        raise HTTPException(status_code=400, detail="gruppe kan ikke inneholde seg selv")
    if db.get(IamGroup, child_id) is None:
        raise HTTPException(status_code=404, detail="undergruppe ikke funnet")
    descendants = _descendant_subgroup_ids(db, child_id)
    if group.id in descendants:
        raise HTTPException(status_code=400, detail="sirkulær gruppestruktur er ikke tillatt")
    row = IamGroupSubgroup(group_id=group.id, child_group_id=child_id)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="undergruppe er allerede koblet") from None


def remove_subgroup_from_group(db: Session, group: IamGroup, child_group_id: int) -> None:
    r = db.execute(
        delete(IamGroupSubgroup).where(
            IamGroupSubgroup.group_id == group.id,
            IamGroupSubgroup.child_group_id == child_group_id,
        )
    )
    if r.rowcount == 0:
        raise HTTPException(status_code=404, detail="undergruppekobling ikke funnet")
    db.commit()


def assign_role_to_person(db: Session, user: User, body: IamAssignRoleBody) -> None:
    if db.get(IamRole, body.role_id) is None:
        raise HTTPException(status_code=404, detail="rolle ikke funnet")
    row = IamUserRole(user_id=user.id, role_id=body.role_id)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="person har allerede denne rollen") from None


def revoke_role_from_person(db: Session, user: User, role_id: int) -> None:
    r = db.execute(delete(IamUserRole).where(IamUserRole.user_id == user.id, IamUserRole.role_id == role_id))
    if r.rowcount == 0:
        raise HTTPException(status_code=404, detail="rolletildeling ikke funnet")
    db.commit()
