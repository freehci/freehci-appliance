# models/crud.py
# Create, Read, Update, Delete

from sqlalchemy.orm import Session

# models
from .user_models import User
from .role_models import Role
from .rack_models import Rack

from .authentication import get_password_hash

# schemas
from .user_schemas import UserCreate
from .role_schemas import RoleCreate
from .rack_schemas import RackCreate

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


# Roles
def get_roles(db: Session):
    return db.query(Role).all()

def create_role(db: Session, role: RoleCreate):
    db_role = Role(
        name=role.name, 
        description=role.description
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def get_role_by_id(db: Session, role_id: int):
    return db.query(Role).filter(Role.id == role_id).first()

def get_role_by_name(db: Session, role_name: str):
    return db.query(Role).filter(Role.name == role_name).first()

def delete_role_by_id(db: Session, role_id: int):
    db.query(Role).filter(Role.id == role_id).delete()
    db.commit()
    return True

def delete_role_by_name(db: Session, role_name: str):
    db.query(Role).filter(Role.name == role_name).delete()
    db.commit()
    return True

def update_role_by_id(db: Session, role_id: int, role: RoleCreate):
    db_role = db.query(Role).filter(Role.id == role_id).first()
    db_role.name = role.name
    db_role.description = role.description
    db.commit()
    db.refresh(db_role)
    return db_role

def update_role_by_name(db: Session, role_name: str, role: RoleCreate):
    db_role = db.query(Role).filter(Role.name == role_name).first()
    db_role.name = role.name
    db_role.description = role.description
    db.commit()
    db.refresh(db_role)
    return db_role

def add_role_to_user(db: Session, user_id: int, role_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    db_role = db.query(Role).filter(Role.id == role_id).first()
    db_user.roles.append(db_role)
    db.commit()
    db.refresh(db_user)
    return db_user

def remove_role_from_user(db: Session, user_id: int, role_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    db_role = db.query(Role).filter(Role.id == role_id).first()
    db_user.roles.remove(db_role)
    db.commit()
    db.refresh(db_user)
    return db_user

# TODO: Add CRUD for Equipment



# Rack 

def get_racks(db: Session):
    return db.query(Rack).all()

def create_rack(db: Session, rack: RackCreate):
    db_rack = Rack(
        name=rack.name, 
        description=rack.description
    )
    db.add(db_rack)
    db.commit()
    db.refresh(db_rack)
    return db_rack

def get_rack_by_id(db: Session, rack_id: int):
    return db.query(Rack).filter(Rack.id == rack_id).first()

def get_rack_by_name(db: Session, rack_name: str):
    return db.query(Rack).filter(Rack.name == rack_name).first()

def delete_rack_by_id(db: Session, rack_id: int):
    db.query(Rack).filter(Rack.id == rack_id).delete()
    db.commit()
    return True

def delete_rack_by_name(db: Session, rack_name: str):
    db.query(Rack).filter(Rack.name == rack_name).delete()
    db.commit()
    return True

def update_rack_by_id(db: Session, rack_id: int, rack: RackCreate):
    db_rack = db.query(Rack).filter(Rack.id == rack_id).first()
    db_rack.name = rack.name
    db_rack.description = rack.description
    db.commit()
    db.refresh(db_rack)
    return db_rack

def update_rack_by_name(db: Session, rack_name: str, rack: RackCreate):
    db_rack = db.query(Rack).filter(Rack.name == rack_name).first()
    db_rack.name = rack.name
    db_rack.description = rack.description
    db.commit()
    db.refresh(db_rack)
    return db_rack
