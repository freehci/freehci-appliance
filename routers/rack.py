# routers/rack.py
# This file will contain the endpoints for the Rack model

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import database
from crud import rack_crud
from models.rack_schemas import RackCreate      # RackCreate is a Pydantic model
#from models.rack_models import Rack            # Rack is a SQLAlchemy model


router = APIRouter()

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Get all racks
@router.get("/rack/", tags=["Rack"])
def get_racks_endpoint(db: Session = Depends(get_db)):
    racks = rack_crud.get_racks(db)
    return racks

# Create rack
@router.post("/rack/", tags=["Rack"])
def create_rack_endpoint(rack: RackCreate, db: Session = Depends(get_db)):
    return rack_crud.create_rack(db=db, rack=rack)

# Get rack by id
@router.get("/rack/{rack_id}", tags=["Rack"])
def read_rack(rack_id: int, db: Session = Depends(get_db)):
    rack = rack_crud.get_rack_by_id(db, rack_id=rack_id)
    if rack is None:
        raise HTTPException(status_code=404, detail="Rack not found")
    return rack

# Update rack
@router.put("/rack/{rack_id}", tags=["Rack"])
def update_rack_endpoint(rack_id: int, rack: RackCreate, db: Session = Depends(get_db)):
    updated_rack = rack_crud.update_rack(db, rack_id=rack_id, rack=rack)
    return updated_rack


# This is equipment related to a rack. Maybe this should be in a separate router?
# Get all equipment for rack 
# TODO: Implement this in rack_crud.py
"""
@router.get("/rack/equipment/{rack_id}", tags=["Rack"])
def get_equipment_endpoint(rack_id: int, db: Session = Depends(get_db)):
    equipment = rack_crud.get_equipment(db)
    return equipment
"""


# Remove equipment from rack
# TODO: Implement this in rack_crud.py
"""
@router.delete("/rack/equipment/{rack_id}/{equipment_id}", tags=["Rack"])
def remove_equipment_endpoint(rack_id: int, equipment_id: int, db: Session = Depends(get_db)):
    equipment = rack_crud.get_equipment(db)
    return equipment
"""    


# Add equipment to rack
# TODO: Implement this in rack_crud.py
"""
@router.post("/rack/equipment/{rack_id}/{equipment_id}", tags=["Rack"])
def add_equipment_endpoint(rack_id: int, equipment_id: int, db: Session = Depends(get_db)):
    equipment = rack_crud.get_equipment(db)
    return equipment

"""