"""IAM REST: personer (users-katalog), globale roller og grupper med undergrupper."""

import os
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.auth_deps import get_current_admin
from app.api.deps import get_db
from app.core.config import get_settings
from app.models.admin_account import AdminAccount
from app.schemas.iam import (
    IamAssignRoleBody,
    IamGroupAddSubgroupMember,
    IamGroupAddUserMember,
    IamGroupCreate,
    IamGroupDetailRead,
    IamGroupRead,
    IamGroupUpdate,
    IamRoleCreate,
    IamRoleDetailRead,
    IamRoleRead,
    IamRoleUpdate,
    PersonCreate,
    PersonDetailRead,
)
from app.schemas.ipam import UserPatch, UserRead
from app.services import iam_directory as iam_svc

router = APIRouter(prefix="/iam", tags=["iam"])


# --- Personer ---


@router.get("/persons", response_model=list[UserRead])
def list_persons(
    limit: int = Query(500, ge=1, le=1000),
    kind: str | None = Query(None, max_length=32, description="Filtrer på users.kind, f.eks. person eller service_account"),
    db: Session = Depends(get_db),
) -> list[UserRead]:
    return iam_svc.list_persons(db, limit=limit, kind=kind)


@router.post("/persons", response_model=UserRead)
def create_person(data: PersonCreate, db: Session = Depends(get_db)) -> UserRead:
    return iam_svc.create_person(db, data)


@router.get("/persons/{person_id}", response_model=PersonDetailRead)
def get_person(person_id: int, db: Session = Depends(get_db)) -> PersonDetailRead:
    row = iam_svc.get_person(db, person_id)
    if row is None:
        raise HTTPException(status_code=404, detail="person ikke funnet")
    return iam_svc.person_detail(db, row)


@router.patch("/persons/{person_id}", response_model=UserRead)
def patch_person(person_id: int, data: UserPatch, db: Session = Depends(get_db)) -> UserRead:
    row = iam_svc.get_person(db, person_id)
    if row is None:
        raise HTTPException(status_code=404, detail="person ikke funnet")
    return iam_svc.patch_person(db, row, data)


@router.post("/persons/{person_id}/roles", status_code=204)
def assign_role_to_person(person_id: int, body: IamAssignRoleBody, db: Session = Depends(get_db)) -> None:
    row = iam_svc.get_person(db, person_id)
    if row is None:
        raise HTTPException(status_code=404, detail="person ikke funnet")
    iam_svc.assign_role_to_person(db, row, body)


@router.delete("/persons/{person_id}/roles/{role_id}", status_code=204)
def revoke_role_from_person(person_id: int, role_id: int, db: Session = Depends(get_db)) -> None:
    row = iam_svc.get_person(db, person_id)
    if row is None:
        raise HTTPException(status_code=404, detail="person ikke funnet")
    iam_svc.revoke_role_from_person(db, row, role_id)


# --- Roller ---


@router.get("/roles", response_model=list[IamRoleRead])
def list_roles(db: Session = Depends(get_db)) -> list[IamRoleRead]:
    return iam_svc.list_roles(db)


@router.post("/roles", response_model=IamRoleRead)
def create_role(data: IamRoleCreate, db: Session = Depends(get_db)) -> IamRoleRead:
    return iam_svc.create_role(db, data)


@router.get("/roles/{role_id}", response_model=IamRoleDetailRead)
def get_role(role_id: int, db: Session = Depends(get_db)) -> IamRoleDetailRead:
    row = iam_svc.get_role(db, role_id)
    if row is None:
        raise HTTPException(status_code=404, detail="rolle ikke funnet")
    return iam_svc.role_detail(db, row)


@router.patch("/roles/{role_id}", response_model=IamRoleRead)
def patch_role(role_id: int, data: IamRoleUpdate, db: Session = Depends(get_db)) -> IamRoleRead:
    row = iam_svc.get_role(db, role_id)
    if row is None:
        raise HTTPException(status_code=404, detail="rolle ikke funnet")
    return iam_svc.patch_role(db, row, data)


@router.delete("/roles/{role_id}", status_code=204)
def delete_role(role_id: int, db: Session = Depends(get_db)) -> None:
    row = iam_svc.get_role(db, role_id)
    if row is None:
        raise HTTPException(status_code=404, detail="rolle ikke funnet")
    iam_svc.delete_role(db, row)


# --- Grupper ---


@router.get("/groups", response_model=list[IamGroupRead])
def list_groups(db: Session = Depends(get_db)) -> list[IamGroupRead]:
    return iam_svc.list_groups(db)


@router.post("/groups", response_model=IamGroupRead)
def create_group(data: IamGroupCreate, db: Session = Depends(get_db)) -> IamGroupRead:
    return iam_svc.create_group(db, data)


@router.get("/groups/{group_id}", response_model=IamGroupDetailRead)
def get_group(group_id: int, db: Session = Depends(get_db)) -> IamGroupDetailRead:
    row = iam_svc.get_group(db, group_id)
    if row is None:
        raise HTTPException(status_code=404, detail="gruppe ikke funnet")
    return iam_svc.group_detail(db, row)


@router.patch("/groups/{group_id}", response_model=IamGroupRead)
def patch_group(group_id: int, data: IamGroupUpdate, db: Session = Depends(get_db)) -> IamGroupRead:
    row = iam_svc.get_group(db, group_id)
    if row is None:
        raise HTTPException(status_code=404, detail="gruppe ikke funnet")
    return iam_svc.patch_group(db, row, data)


@router.delete("/groups/{group_id}", status_code=204)
def delete_group(group_id: int, db: Session = Depends(get_db)) -> None:
    row = iam_svc.get_group(db, group_id)
    if row is None:
        raise HTTPException(status_code=404, detail="gruppe ikke funnet")
    iam_svc.delete_group(db, row)


@router.post("/groups/{group_id}/members/users", status_code=204)
def add_user_member(group_id: int, body: IamGroupAddUserMember, db: Session = Depends(get_db)) -> None:
    row = iam_svc.get_group(db, group_id)
    if row is None:
        raise HTTPException(status_code=404, detail="gruppe ikke funnet")
    iam_svc.add_user_to_group(db, row, body)


@router.delete("/groups/{group_id}/members/users/{user_id}", status_code=204)
def remove_user_member(group_id: int, user_id: int, db: Session = Depends(get_db)) -> None:
    row = iam_svc.get_group(db, group_id)
    if row is None:
        raise HTTPException(status_code=404, detail="gruppe ikke funnet")
    iam_svc.remove_user_from_group(db, row, user_id)


@router.post("/groups/{group_id}/members/groups", status_code=204)
def add_subgroup_member(group_id: int, body: IamGroupAddSubgroupMember, db: Session = Depends(get_db)) -> None:
    row = iam_svc.get_group(db, group_id)
    if row is None:
        raise HTTPException(status_code=404, detail="gruppe ikke funnet")
    iam_svc.add_subgroup_to_group(db, row, body)


@router.delete("/groups/{group_id}/members/groups/{child_group_id}", status_code=204)
def remove_subgroup_member(group_id: int, child_group_id: int, db: Session = Depends(get_db)) -> None:
    row = iam_svc.get_group(db, group_id)
    if row is None:
        raise HTTPException(status_code=404, detail="gruppe ikke funnet")
    iam_svc.remove_subgroup_from_group(db, row, child_group_id)


# --- Avatar ---


def _avatar_dir() -> Path:
    settings = get_settings()
    return settings.upload_root_path / "avatars" / "persons"


def _safe_avatar_ext(content_type: str | None, filename: str | None) -> str | None:
    ct = (content_type or "").lower().strip()
    if ct in ("image/png", "image/x-png"):
        return "png"
    if ct in ("image/jpeg", "image/jpg"):
        return "jpg"
    if ct == "image/webp":
        return "webp"
    # fallback på filending (svakere)
    if filename:
        fn = filename.lower()
        for ext in ("png", "jpg", "jpeg", "webp"):
            if fn.endswith("." + ext):
                return "jpg" if ext == "jpeg" else ext
    return None


@router.get("/persons/{person_id}/avatar")
def get_person_avatar(person_id: int, db: Session = Depends(get_db)) -> FileResponse:
    row = iam_svc.get_person(db, person_id)
    if row is None:
        raise HTTPException(status_code=404, detail="person ikke funnet")
    rel = getattr(row, "avatar_file", None)
    if not rel:
        raise HTTPException(status_code=404, detail="ingen avatar")
    p = get_settings().upload_root_path / rel
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail="ingen avatar")
    mt = "application/octet-stream"
    s = str(p).lower()
    if s.endswith(".png"):
        mt = "image/png"
    elif s.endswith(".jpg") or s.endswith(".jpeg"):
        mt = "image/jpeg"
    elif s.endswith(".webp"):
        mt = "image/webp"
    return FileResponse(path=str(p), media_type=mt)


@router.post("/persons/{person_id}/avatar", response_model=UserRead)
def upload_person_avatar(
    person_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: AdminAccount = Depends(get_current_admin),
) -> UserRead:
    row = iam_svc.get_person(db, person_id)
    if row is None:
        raise HTTPException(status_code=404, detail="person ikke funnet")
    ext = _safe_avatar_ext(file.content_type, file.filename)
    if ext is None:
        raise HTTPException(status_code=400, detail="ugyldig filtype (tillat: png, jpg, webp)")

    # max 2 MiB
    raw = file.file.read()
    if raw is None:
        raise HTTPException(status_code=400, detail="tom fil")
    if len(raw) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="fil for stor (maks 2 MiB)")

    d = _avatar_dir()
    d.mkdir(parents=True, exist_ok=True)
    fname = f"{person_id}.{ext}"
    out = d / fname
    tmp = d / f".{fname}.tmp"
    tmp.write_bytes(raw)
    os.replace(tmp, out)

    rel = str(Path("avatars") / "persons" / fname)
    row.avatar_file = rel
    db.commit()
    db.refresh(row)
    return UserRead.model_validate(row)


@router.delete("/persons/{person_id}/avatar", status_code=204)
def delete_person_avatar(
    person_id: int,
    db: Session = Depends(get_db),
    _: AdminAccount = Depends(get_current_admin),
) -> None:
    row = iam_svc.get_person(db, person_id)
    if row is None:
        raise HTTPException(status_code=404, detail="person ikke funnet")
    rel = getattr(row, "avatar_file", None)
    row.avatar_file = None
    db.commit()
    if rel:
        p = get_settings().upload_root_path / rel
        try:
            p.unlink()
        except FileNotFoundError:
            pass
