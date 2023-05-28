# routers/user.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import crud, database
from models.user_models import User 
from models.user_schemas import UserCreate, UserUpdate

router = APIRouter()

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get all users
@router.get("/users/", tags=["Users"])
def get_users_endpoint(db: Session = Depends(get_db)):
    users = crud.get_users(db)
    return users

# Create user
@router.post("/users/", tags=["Users"])
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

# Get user by id
@router.get("/users/{user_id}", tags=["Users"])
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Update user
@router.put("/users/{user_id}", tags=["Users"])
def update_user_endpoint(user: UserUpdate, user_id: int, db: Session = Depends(get_db)):
    
    user = crud.update_user_by_id(db, user_id=user_id, user=user) # FIXME
    return user

@router.delete("/users/{user_id}", tags=["Users"])
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    user = crud.delete_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ---- Roles, Groups, Company ----
#
# Get all roles for user
@router.get("/users/roles/{user_id}", tags=["Users"])
def get_roles_endpoint(user_id: int, db: Session = Depends(get_db)):
    roles = crud.get_roles(db)
    return roles

# Remove role from user
@router.delete("/users/roles/{user_id}/{role_id}", tags=["Users"])
def remove_role_endpoint(user_id: int, role_id: int, db: Session = Depends(get_db)):
    roles = crud.get_roles(db)
    return roles

# Add role to user
@router.post("/users/roles/{user_id}/{role_id}", tags=["Users"])
def add_role_endpoint(user_id: int, role_id: int, db: Session = Depends(get_db)):
    roles = crud.get_roles(db)
    return roles


# Get all groups for user
@router.get("/users/groups/{user_id}", tags=["Users"])
def get_groups_endpoint(user_id: int, db: Session = Depends(get_db)):
    groups = crud.get_groups(db)
    return groups

# Remove group from user
@router.delete("/users/groups/{user_id}/{group_id}", tags=["Users"])
def remove_group_endpoint(user_id: int, group_id: int, db: Session = Depends(get_db)):
    groups = crud.get_groups(db)
    return groups

# Add group to user
@router.post("/users/groups/{user_id}/{group_id}", tags=["Users"])
def add_group_endpoint(user_id: int, group_id: int, db: Session = Depends(get_db)):
    groups = crud.get_groups(db)
    return groups


# Get Company Info
@router.get("/users/company/{user_id}", tags=["Users"])
def get_company_endpoint(user_id: int, db: Session = Depends(get_db)):
    company = crud.get_company(db) # FIXME: Add function in crud.py
    return company

# Add company to user
@router.post("/users/company/{user_id}/{company_id}", tags=["Users"])
def add_company_endpoint(user_id: int, company_id: int, db: Session = Depends(get_db)):
    company = crud.get_company(db) # FIXME: Add function in crud.py
    return company

# Remove company from user
@router.delete("/users/company/{user_id}/{company_id}", tags=["Users"])
def remove_company_endpoint(user_id: int, company_id: int, db: Session = Depends(get_db)):
    company = crud.get_company(db) # FIXME: Add function in crud.py
    return company

# ---- End Roles, Groups, Company ----

# ---- Applications ----
# Get all applications for user
@router.get("/users/applications/{user_id}", tags=["Users"])
def get_applications_endpoint(user_id: int, db: Session = Depends(get_db)):
    applications = crud.get_applications(db) # FIXME: Add function in crud.py
    return applications

# Remove application from user
@router.delete("/users/applications/{user_id}/{application_id}", tags=["Users"])
def remove_application_endpoint(user_id: int, application_id: int, db: Session = Depends(get_db)):
    applications = crud.get_applications(db) # FIXME: Add function in crud.py
    return applications

# Add application to user
# This endpoint is used to add an application to a user, and to update the user's permissions for the application.
# The application_id will be used to determine which application to add to the user, and wich thechnology / platform to use. Eg. VMware Horizon, Citrix, etc.
# Consider adding a technology_id to the endpoint, to make it possible to add multiple applications of the same type to a user.
# A posible solution can be to use a prefix for the application_id, eg. vmware-horizon-1, vmware-horizon-2, citrix-1, citrix-2, etc, or use a unique id for each application that is tracked in the database.
@router.post("/users/applications/{user_id}/{application_id}", tags=["Users"])
def add_application_endpoint(user_id: int, application_id: int, db: Session = Depends(get_db)):
    applications = crud.get_applications(db) # FIXME: Add function in crud.py
    return applications

