# routers/user.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import crud, database
from models.user_models import User 
from models.user_schemas import UserCreate

router = APIRouter()

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get all users
@router.get("/users/")
def get_users_endpoint(db: Session = Depends(get_db)):
    users = crud.get_users(db)
    return users

# Create user
@router.post("/users/")
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

# Get user by id
@router.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Update user
@router.put("/users/{user_id}")
def update_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    
    user = crud.update_user_by_id(db, user_id=user_id)
    return user

# ---- Roles, Groups, Company ----
#
# Get all roles for user
@router.get("/users/roles/{user_id}")
def get_roles_endpoint(user_id: int, db: Session = Depends(get_db)):
    roles = crud.get_roles(db)
    return roles

# Remove role from user
@router.delete("/users/roles/{user_id}/{role_id}")
def remove_role_endpoint(user_id: int, role_id: int, db: Session = Depends(get_db)):
    roles = crud.get_roles(db)
    return roles

# Add role to user
@router.post("/users/roles/{user_id}/{role_id}")
def add_role_endpoint(user_id: int, role_id: int, db: Session = Depends(get_db)):
    roles = crud.get_roles(db)
    return roles


# Get all groups for user
@router.get("/users/groups/{user_id}")
def get_groups_endpoint(user_id: int, db: Session = Depends(get_db)):
    groups = crud.get_groups(db)
    return groups

# Remove group from user
@router.delete("/users/groups/{user_id}/{group_id}")
def remove_group_endpoint(user_id: int, group_id: int, db: Session = Depends(get_db)):
    groups = crud.get_groups(db)
    return groups

# Add group to user
@router.post("/users/groups/{user_id}/{group_id}")
def add_group_endpoint(user_id: int, group_id: int, db: Session = Depends(get_db)):
    groups = crud.get_groups(db)
    return groups


# Get Company Info
@router.get("/users/company/{user_id}")
def get_company_endpoint(user_id: int, db: Session = Depends(get_db)):
    company = crud.get_company(db)
    return company

# Add company to user
@router.post("/users/company/{user_id}/{company_id}")
def add_company_endpoint(user_id: int, company_id: int, db: Session = Depends(get_db)):
    company = crud.get_company(db)
    return company

# Remove company from user
@router.delete("/users/company/{user_id}/{company_id}")
def remove_company_endpoint(user_id: int, company_id: int, db: Session = Depends(get_db)):
    company = crud.get_company(db)
    return company

# ---- End Roles, Groups, Company ----

# ---- Applications ----
# Get all applications for user
@router.get("/users/applications/{user_id}")
def get_applications_endpoint(user_id: int, db: Session = Depends(get_db)):
    applications = crud.get_applications(db)
    return applications

# Remove application from user
@router.delete("/users/applications/{user_id}/{application_id}")
def remove_application_endpoint(user_id: int, application_id: int, db: Session = Depends(get_db)):
    applications = crud.get_applications(db)
    return applications

# Add application to user
@router.post("/users/applications/{user_id}/{application_id}")
def add_application_endpoint(user_id: int, application_id: int, db: Session = Depends(get_db)):
    applications = crud.get_applications(db)
    return applications

