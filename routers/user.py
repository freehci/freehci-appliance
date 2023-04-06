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


@router.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
