# routers/groups.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import crud, database
from models import Group

from models.groups_schemas import GroupCreate

router = APIRouter()

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get all Groups
@router.get("/groups/", tags=["Groups"])
def get_groups_endpoint(db: Session = Depends(get_db)):
    groups = crud.get_groups(db)
    return groups

@router.post("/groups/", tags=["Groups"])
def create_groups_endpoint(group: GroupCreate, db: Session = Depends(get_db)):
    return crud.create_group(db=db, group=group)

@router.get("/groups/{group_id}", tags=["Groups"])
def read_group(group_id: int, db: Session = Depends(get_db)):
    group = crud.get_group_by_id(db, group_id=group_id)
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@router.put("/groups/{group_id}", tags=["Groups"])
def update_group_endpoint(group_id: int, group: GroupCreate, db: Session = Depends(get_db)):
    
    group = crud.update_group(db, group_id=group_id, group=group)
    return group

@router.delete("/groups/{group_id}", tags=["Groups"])
def delete_group_endpoint(group_id: int, db: Session = Depends(get_db)):
    group = crud.delete_group(db, group_id=group_id)
    return group

