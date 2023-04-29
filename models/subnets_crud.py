# models/crud.py
# Create, Read, Update, Delete

from sqlalchemy.orm import Session
from .subnets_models import Subnet
from .subnets_schemas import SubnetBase, SubnetCreate, SubnetUpdate, SubnetInDBBase, Subnet
import ipaddress
from ipaddress import IPv4Network

# Subnet
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


def update_subnet(db: Session, subnet: SubnetUpdate, subnet_id: int):
    db_subnet = get_subnet(db, subnet_id)
    if db_subnet is None:
        return None

    for key, value in subnet.dict().items():
        if value is not None:
            setattr(db_subnet, key, value)

    db.add(db_subnet)
    db.commit()
    db.refresh(db_subnet)
    return db_subnet


def delete_subnet(db: Session, subnet_id: int):
    db_subnet = get_subnet(db, subnet_id)
    if db_subnet is None:
        return None

    db.delete(db_subnet)
    db.commit()
    return db_subnet


# Subnet helper functions
def is_valid_subnet(subnet: str, mask: str) -> bool:
    try:
        ipaddress.IPv4Network(f"{subnet}/{mask}", strict=False)
        return True
    except ValueError:
        return False

def is_subnet_overlapping(db: Session, subnet: str, mask: str) -> bool:
    new_subnet = IPv4Network(f"{subnet}/{mask}", strict=False)

    existing_subnets = db.query(Subnet).all()

    for existing_subnet in existing_subnets:
        existing_subnet_network = IPv4Network(f"{existing_subnet.subnet}/{existing_subnet.mask}", strict=False)

        if new_subnet.overlaps(existing_subnet_network):
            return True

    return False