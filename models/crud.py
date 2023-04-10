# models/crud.py
# Create, Read, Update, Delete

from sqlalchemy.orm import Session
from .user_models import User
from .role_models import Role
from .authentication import get_password_hash
from .user_schemas import UserCreate

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username, 
        email=user.email, 
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session):
    return db.query(User).all()

def get_roles(db: Session):
    return db.query(Role).all()
