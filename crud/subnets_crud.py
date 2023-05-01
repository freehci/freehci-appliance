# models/crud.py
# Create, Read, Update, Delete
from typing import Optional
from sqlalchemy.orm import Session
from models.subnets_models import Subnet
from models.subnets_schemas import SubnetCreate, SubnetUpdate, Subnet as SubnetBaseSchema

import ipaddress
from ipaddress import IPv4Network

# Subnet
from ipaddress import IPv4Network

def get_subnet(db: Session, subnet_id: int):
    return db.query(Subnet).filter(Subnet.id == subnet_id).first()


def get_subnets(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Subnet).offset(skip).limit(limit).all()


def create_subnet(db: Session, subnet: SubnetCreate):
    db_subnet = Subnet(**subnet.dict())
    db.add(db_subnet)
    db.commit()
    db.refresh(db_subnet)
    return db_subnet


def update_subnet(db: Session, subnet_id: int, subnet_data: SubnetUpdate) -> Optional[SubnetBaseSchema]:
    subnet = db.query(Subnet).filter(Subnet.id == subnet_id).first()
    if not subnet:
        return None  # TODO: Fix this

    for field, value in subnet_data.dict().items():
        if value is not None:
            setattr(subnet, field, value)
    
    db.add(subnet)
    db.commit()
    db.refresh(subnet)
    return subnet


def delete_subnet(db: Session, subnet_id: int):
    db_subnet = get_subnet(db, subnet_id)
    if db_subnet is None:
        return None

    db.delete(db_subnet)
    db.commit()
    return db_subnet

# Validation functions
def is_valid_subnet(subnet: str, mask: str) -> bool:
    try:
        ipaddress.IPv4Network(f"{subnet}/{mask}", strict=False)
        return True
    except ValueError:
        #print("Invalid subnet : " + subnet + "/" + mask)
        return False
    
# TODO: Check if subnet overlaps with existing subnets. Allow overlapping subnets with different customers, and allow overlapping subnets with the same customer if the subnet is smaller than the existing subnet.
# TODO: Allso allow overlapping subnets if the existing subnet for differnt environments (prod, test, dev)
def is_subnet_overlapping(db: Session, subnet: str, mask: str) -> bool:
    new_subnet = IPv4Network(f"{subnet}/{mask}", strict=False)

    existing_subnets = db.query(Subnet).all()

    for existing_subnet in existing_subnets:
        existing_subnet_network = IPv4Network(f"{existing_subnet.subnet}/{existing_subnet.mask}", strict=False)

        if new_subnet.overlaps(existing_subnet_network):
            return True

    return False

# TODO: Check if subnet is within a parent subnet

# Split a subnet into multipe smaller subnets
# Rules: 
# A subnetted subnet must be smaller than the parent subnet. 
# The subnetted subnet cannot have ip addresses. 
# The subnetted subnet cannot have a VLAN assigned.


