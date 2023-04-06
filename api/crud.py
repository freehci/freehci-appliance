# api/crud.py

from sqlalchemy.orm import Session
from models.user_models import User
import bcrypt

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: User):
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
    user.password = hashed_password.decode("utf-8")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user