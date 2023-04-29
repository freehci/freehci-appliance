from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from . import crud_location, locations_schemas
from database import get_db

router = APIRouter()

@router.get("/locations/", response_model=List[locations_schemas.LocationSchema])
def get_locations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    locations = crud_location.get_locations(db, skip=skip, limit=limit)
    return locations

@router.get("/locations/{location_id}", response_model=locations_schemas.LocationSchema)
def get_location(location_id: int, db: Session = Depends(get_db)):
    location = crud_location.get_location(db, location_id)
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

@router.post("/locations/", response_model=locations_schemas.LocationSchema)
def create_location(location: locations_schemas.LocationCreateSchema, db: Session = Depends(get_db)):
    return crud_location.create_location(db, location)

@router.put("/locations/{location_id}", response_model=locations_schemas.LocationSchema)
def update_location(location_id: int, updated_location: locations_schemas.LocationCreateSchema, db: Session = Depends(get_db)):
    location = crud_location.get_location(db, location_id)
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return crud_location.update_location(db, location_id, updated_location)

@router.delete("/locations/{location_id}")
def delete_location(location_id: int, db: Session = Depends(get_db)):
    location = crud_location.get_location(db, location_id)
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    crud_location.delete_location(db, location_id)
    return {"detail": "Location deleted successfully"}