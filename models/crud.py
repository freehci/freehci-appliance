# models/crud.py
# Create, Read, Update, Delete

from sqlalchemy.orm import Session
import ipaddress

#
# models
#
from .user_models import User
from .role_models import Role
from .rack_models import Rack
from .ipaddresses_models import IPAddress
from .subnets_models import Subnet
from .customers_models import Customer
from .vlans_models import VLAN
from .sections_models import Section
from .vrf_models import Vrf
from .locations_models import Location

from .authentication import get_password_hash



#
# schemas
#
from .user_schemas import UserCreate
from .role_schemas import RoleCreate
from .rack_schemas import RackCreate
from .ipaddresses_schemas import IPAddressBase, IPAddressCreate, IPAddressUpdate, IPAddressInDBBase, IPAddress
from .subnets_schemas import SubnetBase, SubnetCreate, SubnetUpdate, SubnetInDBBase
from .customers_schemas import CustomerBase, CustomerCreate, CustomerUpdate, CustomerInDBBase, Customer
from .vlans_schemas import VLANBase, VLANCreate, VLANUpdate, VLANInDBBase, VLAN
from .sections_schemas import SectionBase, SectionCreate, SectionUpdate, SectionInDBBase, Section
from .vrf_schemas import VrfBaseSchema, VrfCreateSchema, VrfUpdateSchema, VrfInDBBaseSchema, VrfSchema
from .locations_schemas import LocationSchema, LocationCreateSchema

#
# User
#
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

def update_user_by_id(db: Session, user_id: int, user: UserCreate):
    db_user = db.query(User).filter(User.id == user_id).first()
    db_user.username = user.username
    db_user.email = user.email
    #db_user.password = get_password_hash(user.password)
    db.commit()
    db.refresh(db_user)
    return db_user



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
    db_rack.units = rack.units
    db_rack.width = rack.width
    db_rack.height = rack.height
    db_rack.depth = rack.depth
    db_rack.row = rack.row
    db_rack.col = rack.col
    db_rack.room_id = rack.room_id
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


# IPaddress



def get_ipaddress(db: Session, ipaddress_id: int):
    return db.query(IPAddress.IPAddress).filter(IPAddress.id == ipaddress_id).first()


def get_ipaddresses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(IPAddress.IPAddress).offset(skip).limit(limit).all()


def create_ipaddress(db: Session, ipaddress: IPAddressCreate):
    db_ipaddress = IPAddress.IPAddress(**ipaddress.dict())
    db.add(db_ipaddress)
    db.commit()
    db.refresh(db_ipaddress)
    return db_ipaddress


def update_ipaddress(db: Session, ipaddress: IPAddressUpdate, ipaddress_id: int):
    db_ipaddress = get_ipaddress(db, ipaddress_id)
    if db_ipaddress is None:
        return None

    for key, value in ipaddress.dict().items():
        if value is not None:
            setattr(db_ipaddress, key, value)

    db.add(db_ipaddress)
    db.commit()
    db.refresh(db_ipaddress)
    return db_ipaddress


def delete_ipaddress(db: Session, ipaddress_id: int):
    db_ipaddress = get_ipaddress(db, ipaddress_id)
    if db_ipaddress is None:
        return None

    db.delete(db_ipaddress)
    db.commit()
    return db_ipaddress

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


def update_subnet(db: Session, subnet_id: int, subnet_data: SubnetUpdate) -> Subnet:
    subnet = db.query(Subnet).filter(Subnet.id == subnet_id).first()
    if not subnet:
        return None

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

def is_valid_subnet(subnet: str, mask: str) -> bool:
    try:
        ipaddress.IPv4Network(f"{subnet}/{mask}", strict=False)
        return True
    except ValueError:
        #print("Invalid subnet : " + subnet + "/" + mask)
        return False

def is_subnet_overlapping(db: Session, subnet: str, mask: str) -> bool:
    new_subnet = IPv4Network(f"{subnet}/{mask}", strict=False)

    existing_subnets = db.query(Subnet).all()

    for existing_subnet in existing_subnets:
        existing_subnet_network = IPv4Network(f"{existing_subnet.subnet}/{existing_subnet.mask}", strict=False)

        if new_subnet.overlaps(existing_subnet_network):
            return True

    return False

# Customer

def get_customer(db: Session, customer_id: int):
    return db.query(Customer).filter(Customer.id == customer_id).first()


def get_customers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Customer).offset(skip).limit(limit).all()


def create_customer(db: Session, customer: CustomerCreate):
    db_customer = Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def update_customer(db: Session, customer: CustomerUpdate, customer_id: int):
    db_customer = get_customer(db, customer_id)
    if db_customer is None:
        return None

    for key, value in customer.dict().items():
        if value is not None:
            setattr(db_customer, key, value)

    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def delete_customer(db: Session, customer_id: int):
    db_customer = get_customer(db, customer_id)
    if db_customer is None:
        return None

    db.delete(db_customer)
    db.commit()
    return db_customer


# VLAN

def get_vlan(db: Session, vlan_id: int):
    return db.query(VLAN).filter(VLAN.vlanId == vlan_id).first()


def get_vlans(db: Session, skip: int = 0, limit: int = 100):
    return db.query(VLAN).offset(skip).limit(limit).all()


def create_vlan(db: Session, vlan: VLANCreate):
    db_vlan = VLAN(**vlan.dict())
    db.add(db_vlan)
    db.commit()
    db.refresh(db_vlan)
    return db_vlan


def update_vlan(db: Session, vlan: VLANUpdate, vlan_id: int):
    db_vlan = get_vlan(db, vlan_id)
    if db_vlan is None:
        return None

    for key, value in vlan.dict().items():
        if value is not None:
            setattr(db_vlan, key, value)

    db.add(db_vlan)
    db.commit()
    db.refresh(db_vlan)
    return db_vlan


def delete_vlan(db: Session, vlan_id: int):
    db_vlan = get_vlan(db, vlan_id)
    if db_vlan is None:
        return None

    db.delete(db_vlan)
    db.commit()
    return db_vlan

# Sections

def get_section(db: Session, section_id: int):
    return db.query(Section).filter(Section.id == section_id).first()


def get_sections(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Section).offset(skip).limit(limit).all()


def create_section(db: Session, section: SectionCreate):
    db_section = Section(**section.dict())
    db.add(db_section)
    db.commit()
    db.refresh(db_section)
    return db_section


def update_section(db: Session, section: SectionUpdate, section_id: int):
    db_section = get_section(db, section_id)
    if db_section is None:
        return None

    for key, value in section.dict().items():
        if value is not None:
            setattr(db_section, key, value)

    db.add(db_section)
    db.commit()
    db.refresh(db_section)
    return db_section


def delete_section(db: Session, section_id: int):
    db_section = get_section(db, section_id)
    if db_section is None:
        return None

    db.delete(db_section)
    db.commit()
    return db_section


# VRF

def get_vrf(db: Session, vrf_id: int):
    return db.query(Vrf).filter(Vrf.vrfId == vrf_id).first()


def get_vrfs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Vrf).offset(skip).limit(limit).all()


def create_vrf(db: Session, vrf: VrfCreateSchema):
    db_vrf = Vrf(**vrf.dict())
    db.add(db_vrf)
    db.commit()
    db.refresh(db_vrf)
    return db_vrf


def update_vrf(db: Session, vrf: VrfUpdateSchema, vrf_id: int):
    db_vrf = get_vrf(db, vrf_id)
    if db_vrf is None:
        return None

    for key, value in vrf.dict().items():
        if value is not None:
            setattr(db_vrf, key, value)

    db.add(db_vrf)
    db.commit()
    db.refresh(db_vrf)
    return db_vrf


def delete_vrf(db: Session, vrf_id: int):
    db_vrf = get_vrf(db, vrf_id)
    if db_vrf is None:
        return None

    db.delete(db_vrf)
    db.commit()
    return db_vrf

# Location

def get_location(db: Session, location_id: int):
    return db.query(Location).filter(Location.id == location_id).first()

def get_locations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Location).offset(skip).limit(limit).all()

def create_location(db: Session, location: LocationCreateSchema):
    db_location = Location(**location.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

def update_location(db: Session, location_id: int, updated_location: LocationCreateSchema):
    db_location = db.query(Location).filter(Location.id == location_id).one()
    db_location.name = updated_location.name
    db_location.description = updated_location.description
    db_location.address = updated_location.address
    db_location.lat = updated_location.lat
    db_location.long = updated_location.long
    db.commit()
    db.refresh(db_location)
    return db_location

def delete_location(db: Session, location_id: int):
    db_location = db.query(Location).filter(Location.id == location_id).one()
    db.delete(db_location)
    db.commit()