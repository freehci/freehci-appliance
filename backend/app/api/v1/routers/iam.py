"""IAM REST: personer (users-katalog), globale roller og grupper med undergrupper."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
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
def list_persons(limit: int = Query(500, ge=1, le=1000), db: Session = Depends(get_db)) -> list[UserRead]:
    return iam_svc.list_persons(db, limit=limit)


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
