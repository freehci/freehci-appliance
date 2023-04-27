# routers/equipment.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import crud, database

# TODO: Create equipment_models.py and equipment_schemas.py
from models.role_models import Role
from models.role_schemas import RoleCreate

router = APIRouter()

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get all roles
@router.get("/equipment/")
def get_roles_endpoint(db: Session = Depends(get_db)):
    roles = crud.get_roles(db)
    return roles
