# routers/rack.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import crud, database

# TODO: Create rack_models.py and rack_schemas.py
#from models.role_models import Role
#from models.role_schemas import RoleCreate
from models.rack_schemas import RackCreate
from models.rack_models import Rack


router = APIRouter()

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Get all racks
@router.get("/rack/")
def get_racks_endpoint(db: Session = Depends(get_db)):
    racks = crud.get_racks(db)
    return racks

# Create rack
@router.post("/rack/")
def create_rack_endpoint(rack: RackCreate, db: Session = Depends(get_db)):
    return crud.create_rack(db=db, rack=rack)

# Get rack by id
@router.get("/rack/{rack_id}")
def read_rack(rack_id: int, db: Session = Depends(get_db)):
    rack = crud.get_rack_by_id(db, rack_id=rack_id)
    if rack is None:
        raise HTTPException(status_code=404, detail="Rack not found")
    return rack


# Get all equipment for rack
@router.get("/rack/equipment/{rack_id}")
def get_equipment_endpoint(rack_id: int, db: Session = Depends(get_db)):
    equipment = crud.get_equipment(db)
    return equipment


# Remove equipment from rack
@router.delete("/rack/equipment/{rack_id}/{equipment_id}")
def remove_equipment_endpoint(rack_id: int, equipment_id: int, db: Session = Depends(get_db)):
    equipment = crud.get_equipment(db)
    return equipment


# Add equipment to rack
@router.post("/rack/equipment/{rack_id}/{equipment_id}")
def add_equipment_endpoint(rack_id: int, equipment_id: int, db: Session = Depends(get_db)):
    equipment = crud.get_equipment(db)
    return equipment


# Update rack
@router.put("/rack/{rack_id}")
def update_rack_endpoint(rack_id: int, db: Session = Depends(get_db)):
    equipment = crud.get_equipment(db)
    return equipment


