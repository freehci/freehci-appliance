# File: routers\customers.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import crud, database

from models import customers_models
from models import customers_schemas

router = APIRouter()

# Dependency
# Move this to database.py ?

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
# Get all customers
@router.get("/ipam/customers/")
def get_customers_endpoint(db: Session = Depends(get_db)):
    customers = crud.get_customers(db)
    return customers

# Create customer
@router.post("/ipam/customers/")
def create_customer_endpoint(customer: customers_schemas.CustomerCreate, db: Session = Depends(get_db)):
    return crud.create_customer(db=db, customer=customer)

# Get customer by id
@router.get("/ipam/customers/{customer_id}")
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = crud.get_customer_by_id(db, customer_id=customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

# Update customer
@router.put("/ipam/customers/{customer_id}")
def update_customer_endpoint(customer_id: int, db: Session = Depends(get_db)):
    
    customer = crud.update_customer_by_id(db, customer_id=customer_id)
    return customer 

# Delete customer
@router.delete("/ipam/customers/{customer_id}")
def delete_customer_endpoint(customer_id: int, db: Session = Depends(get_db)):
    customer = crud.delete_customer_by_id(db, customer_id=customer_id)
    return customer 

# Get customer by name
@router.get("/ipam/customers/name/{customer_name}")
def read_customer_by_name(customer_name: str, db: Session = Depends(get_db)):
    customer = crud.get_customer_by_name(db, customer_name=customer_name)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer 

