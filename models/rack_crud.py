# File: models/rack_crud.py
# This file will contain the CRUD functions for the Rack model (CRUD = Create, Read, Update, Delete)


from sqlalchemy.orm import Session
from models.rack_models import Rack
from models.rack_schemas import RackCreate




# Get all racks
def get_racks(db: Session):
    return db.query(Rack).all()

# Create rack
def create_rack(db: Session, rack: RackCreate):
    db_rack = Rack(**rack.dict())
    db.add(db_rack)
    db.commit()
    db.refresh(db_rack)
    return db_rack

# Update rack
def update_rack(db: Session, rack_id: int, rack: RackCreate):
    db_rack = db.query(Rack).filter(Rack.id == rack_id).first()
    db_rack.name = rack.name
    db_rack.description = rack.description
    db.commit()
    db.refresh(db_rack)
    return db_rack

# Get rack by id
def get_rack_by_id(db: Session, rack_id: int):
    return db.query(Rack).filter(Rack.id == rack_id).first()

# Get rack by name
def get_rack_by_name(db: Session, rack_name: str):
    return db.query(Rack).filter(Rack.name == rack_name).first()

# Delete rack by id
def delete_rack_by_id(db: Session, rack_id: int):
    db.query(Rack).filter(Rack.id == rack_id).delete()
    db.commit()
    return True



#
# Validators
#

