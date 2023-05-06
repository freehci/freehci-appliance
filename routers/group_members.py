from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
#from . import crud_group_members as crud
#from . import groups_members_schemas as schemas
#from .database import get_db

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import crud, database

from models.groups_members_schemas import GroupMemberCreate, GroupMemberRead

from datetime import datetime

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/group_members/", response_model=GroupMemberRead, tags=["Groups"])
def create_group_member(group_member: GroupMemberCreate, db: Session = Depends(get_db)):
    return crud.create_group_member(db=db, group_member=group_member)

"""@router.get("/group_members/{group_member_id}", response_model=GroupMemberRead, tags=["Groups"])
def read_group_member(group_member_id: int, db: Session = Depends(get_db)):
    db_group_member = crud.get_group_member_by_id(db=db, group_member_id=group_member_id)
    if not db_group_member:
        raise HTTPException(status_code=404, detail="Group member not found")
    return db_group_member
"""
@router.get("/group_members/{group_id}", response_model=List[GroupMemberRead], tags=["Groups"])
def read_group_members(group_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    group_members = crud.get_group_members_by_group_id(db=db, group_id=group_id, skip=skip, limit=limit)
    return group_members

@router.put("/group_members/{group_member_id}", response_model=GroupMemberRead, tags=["Groups"])
def update_group_member(group_member_id: int, group_member_update: GroupMemberCreate, db: Session = Depends(get_db)):
    updated_group_member = crud.update_group_member(db=db, group_member_id=group_member_id, group_member_update=group_member_update)
    if not updated_group_member:
        raise HTTPException(status_code=404, detail="Group member not found")
    return updated_group_member

@router.delete("/group_members/{group_member_id}", response_model=GroupMemberRead, tags=["Groups"])
def delete_group_member(group_member_id: int, db: Session = Depends(get_db)):
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