# routers/role.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import crud, database
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
@router.get("/roles/")
def get_roles_endpoint(db: Session = Depends(get_db)):
    roles = crud.get_roles(db)
    return roles
