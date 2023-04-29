# File: routers\subnets.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import crud, database

from models.subnets_schemas import SubnetCreate, SubnetUpdate, Subnet
from models.subnets_models import Subnet as SubnetModel

router = APIRouter()

# Dependency
# Move this to database.py ?

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get all subnets
@router.get("/ipam/subnets/")
def get_subnets_endpoint(db: Session = Depends(get_db)):
    subnets = crud.get_subnets(db)
    return subnets

# Get subnet by id
@router.get("/ipam/subnets/{subnet_id}")
def read_subnet(subnet_id: int, db: Session = Depends(get_db)):
    subnet = crud.get_subnet(db, subnet_id=subnet_id)
    if subnet is None:
        raise HTTPException(status_code=404, detail="Subnet not found")
    return subnet

# Create subnet
# TODO: Validate all date fields in the request body to be in the correct format
@router.post("/ipam/subnets/", response_model=Subnet)
def create_subnet(subnet: SubnetCreate, db: Session = Depends(get_db)):
    if not crud.is_valid_subnet(subnet.subnet, subnet.mask):
        raise HTTPException(status_code=400, detail="Invalid subnet.")
    
    if crud.is_subnet_overlapping(db, subnet.subnet, subnet.mask):
        raise HTTPException(status_code=400, detail="Overlapping subnet.")
    return crud.create_subnet(db=db, subnet=subnet)

# Update subnet
# TODO: Validate all date fields in the request body to be in the correct format
@router.put("/ipam/subnets/{subnet_id}", response_model=Subnet)
def update_subnet(subnet_id: int, updated_subnet: SubnetUpdate, db: Session = Depends(get_db)):
    existing_subnet = crud.get_subnet(db, subnet_id)

    if not existing_subnet:
        raise HTTPException(status_code=404, detail="Subnet not found")

    if crud.is_subnet_overlapping(db, updated_subnet.subnet, updated_subnet.mask):
        raise HTTPException(status_code=400, detail="Subnet overlapping with existing subnet.")

    return crud.update_subnet(db, subnet_id, updated_subnet)
