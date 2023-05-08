# File: routers\group_members.py
# Author: Roy Michelsen

from typing import List, Optional
#from fastapi import FastAPI, Depends, HTTPException
#from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models import crud, database, GroupMember

from models.groups_members_schemas import GroupMemberCreate, GroupMemberRead, GroupMemberResponse

from datetime import datetime

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

################################################################################################################################################################
# Add group member                                                                                                                                             #
# TODO: Validate that either member_id or member_group_id is provided, and remove the other one.                                                               #
# STATUS: Finished                                                                                                                                             #
# TODO: Validate that the member_id or member_group_id exists in the database.                                                                                 #
# STATUS: Finished                                                                                                                                             #
################################################################################################################################################################
# BUG: -                                                                                                                                                       #
# FIXME: -                                                                                                                                                     #
################################################################################################################################################################

@router.post("/group_members/", response_model=GroupMemberResponse, tags=["Groups"])
def create_new_group_member(
    group_member: GroupMemberCreate,
    db: Session = Depends(get_db)
):
    #print("Inside create_group_member router endpoint:", group_member)
    
    # Check if either member_id or member_group_id is provided
    if not group_member.member_id and not group_member.member_group_id:
        raise HTTPException(status_code=400, detail="Either member_id or member_group_id must be provided")
    
    # Check if member_type is valid
    print("group_member.member_type:", group_member.member_type)
    if not group_member.member_type == group_member.member_type.GROUP and not group_member.member_type == group_member.member_type.USER:
        raise HTTPException(status_code=400, detail="Invalid member_type")
    
    # Removing member_group_id if member_type is user, and vice versa
    if group_member.member_type == group_member.member_type.USER:
        group_member.member_group_id = None
    else:
        group_member.member_id = None
        
    # For debugging
    """
    print("Before Pydantic validation:", group_member)
    validated_group_member = GroupMemberCreate(**group_member.dict())
    print("After Pydantic validation:", validated_group_member)
    """
    
    # This will raise a ValueError depending on the crud function called
    # Posible errors: ValueError("User or group is already a member of this group"), ValueError("Adding this group would create a circular membership")
    # TODO: Add CustomValueError to the crud functions and raise that instead of ValueError in order to provide a more descriptive error message
    try:
        return crud.create_group_member(db=db, group_member=group_member)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    #db_group_member = crud.create_group_member(db, group_member)
    #return db_group_member

"""
@router.post("/group_members/", response_model=GroupMemberRead, tags=["Groups"])
def create_group_member(group_member: GroupMemberCreate, db: Session = Depends(get_db)):
    return crud.create_group_member(db=db, group_member=group_member)
"""

"""@router.get("/group_members/{group_member_id}", response_model=GroupMemberRead, tags=["Groups"])
def read_group_member(group_member_id: int, db: Session = Depends(get_db)):
    db_group_member = crud.get_group_member_by_id(db=db, group_member_id=group_member_id)
    if not db_group_member:
        raise HTTPException(status_code=404, detail="Group member not found")
    return db_group_member
"""

@router.get("/group_members/{group_id}", response_model=List[GroupMemberRead], tags=["Groups"])
def read_group_members(
    group_id: int, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    group_members = crud.get_group_members_by_group_id(db=db, group_id=group_id, skip=skip, limit=limit)
    return group_members

@router.put("/group_members/{group_member_id}", response_model=GroupMemberRead, tags=["Groups"])
def update_group_member(
    group_member_id: int, 
    group_member_update: GroupMemberCreate, 
    db: Session = Depends(get_db)
):
    updated_group_member = crud.update_group_member(db=db, group_member_id=group_member_id, group_member_update=group_member_update)
    if not updated_group_member:
        raise HTTPException(status_code=404, detail="Group member not found")
    return updated_group_member

@router.delete("/group_members/{group_member_id}", response_model=GroupMemberRead, tags=["Groups"])
def delete_group_member(
    group_member_id: int, 
    db: Session = Depends(get_db)
):
    deleted_group_member = crud.delete_group_member(db=db, group_member_id=group_member_id)
    if not deleted_group_member:
        raise HTTPException(status_code=404, detail="Group member not found")
    return deleted_group_member

"""
@router.get("/group_members/", response_model=List[GroupMemberRead], tags=["Groups"])
def read_group_members(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    group_members = crud.get_group_members(db=db, skip=skip, limit=limit)
    return group_members

"""

@router.get("/group_members/{group_id}/is_member/", tags=["Groups"])
def is_member(
    group_id: int,
    member_id: Optional[int] = None,
    member_group_id: Optional[int] = None,
    depth: int = 1,
    db: Session = Depends(get_db),
    #current_user: User = Depends(get_current_user), # TODO: Add authentication
):
    if not member_id and not member_group_id:
        raise HTTPException(status_code=400, detail="Either member_id or member_group_id must be provided")
    try:
        is_member = crud.is_member_recursive(
            db,
            group_id=group_id,
            member_id=member_id,
            member_group_id=member_group_id,
            depth=depth,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"is_member": is_member}