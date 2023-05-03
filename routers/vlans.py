# File: routers\vlans.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import crud, database

from models import vlans_models
from models import vlans_schemas

router = APIRouter()

# Dependency
# Move this to database.py ?

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

# Get all vlans
@router.get("/ipam/vlans/")
def get_vlans_endpoint(db: Session = Depends(get_db)):
    vlans = crud.get_vlans(db)
    return vlans

# TODO: Fix Customer functionality before implementing test for existing customers
# STATUS: Fixed
#
@router.post("/ipam/vlans/")
def create_vlan_endpoint(vlan: vlans_schemas.VLANCreate, db: Session = Depends(get_db)):
    # Check if customer_id is anything but 0 and if so, check if customer exists
    if vlan.customer_id and vlan.customer_id != 0:
        customer = crud.get_customer(db, vlan.customer_id)
        if not customer:
            raise HTTPException(status_code=400, detail="Customer not found") # TODO: Change to 404?

    return crud.create_vlan(db=db, vlan=vlan)

# Create vlan
# TODO: This function is obsolete, remove it
# STATUS: Obsolete
#
#@router.post("/ipam/vlans/")
#def create_vlan_endpoint(vlan: vlans_schemas.VLANCreate, db: Session = Depends(get_db)):
#    return crud.create_vlan(db=db, vlan=vlan)

# Get vlan by id
@router.get("/ipam/vlans/{vlan_id}")
def read_vlan(vlan_id: int, db: Session = Depends(get_db)):
    vlan = crud.get_vlan(db, vlan_id=vlan_id)
    if vlan is None:
        raise HTTPException(status_code=404, detail="Vlan not found")
    return vlan

# Update vlan
@router.put("/ipam/vlans/{vlan_id}")
def update_vlan_endpoint(vlan: vlans_schemas.VLANUpdate, db: Session = Depends(get_db)):
    # Check if customer_id is anything but 0 and if so, check if customer exists
    if vlan.customer_id and vlan.customer_id != 0:
        customer = crud.get_customer(db, vlan.customer_id)
        if not customer:
            raise HTTPException(status_code=400, detail="Customer not found") # TODO: Change to 404?
    
    vlan = crud.update_vlan(db, vlan=vlan)
    return vlan

# Delete vlan
@router.delete("/ipam/vlans/{vlan_id}")
def delete_vlan_endpoint(vlan_id: int, db: Session = Depends(get_db)):
    
    vlan = crud.delete_vlan(db, vlan_id=vlan_id)
    return vlan

