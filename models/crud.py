# models/crud.py
# Create, Read, Update, Delete
# Author: Roy Michelsen

from sqlalchemy.orm import Session, joinedload
import ipaddress
from typing import Optional

#
# models
#
from .user_models import User
from .role_models import Role
#from .groups_models import Group
#from .groups_members_models import GroupMember

from models import Group
from models import GroupMember
from .group_and_member_models import MemberType, GroupStatus

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
from .user_schemas import UserCreate, UserUpdate
from .role_schemas import RoleCreate
from .groups_schemas import GroupCreate
from .groups_members_schemas import GroupMemberCreate, GroupMemberResponse
from .rack_schemas import RackCreate
from .ipaddresses_schemas import IPAddressBase, IPAddressCreate, IPAddressUpdate, IPAddressInDBBase
from .subnets_schemas import SubnetBase, SubnetCreate, SubnetUpdate, SubnetInDBBase
from .customers_schemas import CustomerBase, CustomerCreate, CustomerUpdate, CustomerInDBBase
from .vlans_schemas import VLANBase, VLANCreate, VLANUpdate, VLANInDBBase
from .sections_schemas import SectionBase, SectionCreate, SectionUpdate, SectionInDBBase
from .vrf_schemas import VrfBaseSchema, VrfCreateSchema, VrfUpdateSchema, VrfInDBBaseSchema, VrfSchema
from .locations_schemas import LocationSchema, LocationCreateSchema

############################################################################################################################################################################
# User
############################################################################################################################################################################
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

def delete_user_by_id(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    db.delete(db_user)
    db.commit()
    return db_user

def delete_user_by_username(db: Session, username: str):
    db_user = db.query(User).filter(User.username == username).first()
    db.delete(db_user)
    db.commit()
    return db_user

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session):
    return db.query(User).all()

def update_user_by_id(db: Session, user_id: int, user: UserUpdate): #TODO: This should be UserBaseSchema instead of UserCreate
    db_user = db.query(User).filter(User.id == user_id).first()
    db_user.username = user.username
    db_user.email = user.email
    #db_user.password = get_password_hash(user.password)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_by_username(db: Session, username: str, user: UserUpdate):
    db_user = db.query(User).filter(User.username == username).first()
    db_user.username = user.username
    db_user.email = user.email
    #db_user.password = get_password_hash(user.password)
    db.commit()
    db.refresh(db_user)
    return db_user

def reset_user_password_by_id(db: Session, user_id: int, user: UserCreate):
    db_user = db.query(User).filter(User.id == user_id).first()
    db_user.password = get_password_hash(user.password)
    db.commit()
    db.refresh(db_user)
    return db_user

def reset_user_password_by_username(db: Session, username: str, user: UserCreate):
    db_user = db.query(User).filter(User.username == username).first()
    db_user.password = get_password_hash(user.password)
    db.commit()
    db.refresh(db_user)
    return db_user 

############################################################################################################################################################################
# Roles
############################################################################################################################################################################
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

############################################################################################################################################################################
#   Groups
############################################################################################################################################################################

def create_group(db: Session, group: GroupCreate):
    db_group = Group(**group.dict())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

def get_group_by_id(db: Session, group_id: int):
    return db.query(Group).filter(Group.id == group_id).first()

def get_groups(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Group).offset(skip).limit(limit).all()

def update_group(db: Session, group_id: int, group: GroupCreate):
    db_group = db.query(Group).filter(Group.id == group_id).first()
    for key, value in group.dict().items():
        setattr(db_group, key, value)
    db.commit()
    db.refresh(db_group)
    return db_group

def delete_group(db: Session, group_id: int):
    db_group = db.query(Group).filter(Group.id == group_id).first()
    db.delete(db_group)
    db.commit()
    return db_group

############################################################################################################################################################################
#   Group Members
############################################################################################################################################################################
"""
def create_group_member(db: Session, group_member: GroupMemberCreate):
    db_group_member = GroupMember(**group_member.dict())
    db.add(db_group_member)
    db.commit()
    db.refresh(db_group_member)
    return db_group_member
"""

"""
def create_group_member(db: Session, group_member: GroupMemberCreate):
    
    print("Inside create_group_member function:", group_member)
    db_group_member = GroupMember(**group_member.dict())
    print("db_group_member:", db_group_member)
    
    if group_member.member_type == MemberType.USER:
        db_group_member = GroupMember(
            group_id=group_member.group_id,
            member_id=group_member.member_id,
            member_type=group_member.member_type,
            lastupdatedby=group_member.lastupdatedby,
            expires=group_member.expires,
            status=group_member.status
        )
    elif group_member.member_type == MemberType.GROUP:
        db_group_member = GroupMember(
            group_id=group_member.group_id,
            member_group_id=group_member.member_group_id,
            member_type=group_member.member_type,
            lastupdatedby=group_member.lastupdatedby,
            expires=group_member.expires,
            status=group_member.status
        )
    else:
        raise ValueError("Invalid member type")
        
    db.add(db_group_member)
    db.commit()
    db.refresh(db_group_member)
    return db_group_member
"""
############################################################################################################################################################################
# Detect loops in group membership (detects circular membership) 2023-05-07 21:12                                                                                          #
############################################################################################################################################################################
def detect_loop(db: Session, group_id: int, member_group_id: int) -> bool:
    visited = set()

    def dfs(current_group_id: int) -> bool:
        if current_group_id in visited:
            return False
        visited.add(current_group_id)

        query = db.query(GroupMember).filter(GroupMember.group_id == current_group_id, GroupMember.member_type == MemberType.GROUP)

        for group_member in query:
            if group_member.member_group_id == member_group_id:
                return True
            if dfs(group_member.member_group_id):
                return True

        visited.remove(current_group_id)
        return False

    if group_id == member_group_id:
        return True

    return dfs(group_id)



""" Removed 2021-05-07 21:12
def detect_loop(db: Session, group_id: int, member_group_id: int) -> bool:
    visited = set()

    def dfs(current_group_id: int) -> bool:
        if current_group_id in visited:
            return False
        visited.add(current_group_id)

        query = db.query(GroupMember).filter(GroupMember.group_id == current_group_id, GroupMember.member_type == MemberType.GROUP)

        for group_member in query:
            if group_member.member_group_id == member_group_id:
                return True
            if dfs(group_member.member_group_id):
                return True

        visited.remove(current_group_id)
        return False

    return dfs(group_id)
"""
def create_group_member(db: Session, group_member: GroupMemberCreate):
    existing_membership = db.query(GroupMember).filter(
        GroupMember.group_id == group_member.group_id,
        GroupMember.member_group_id == group_member.member_group_id,
        GroupMember.member_type == group_member.member_type
    ).first()
    
    if existing_membership:
        raise ValueError("User or group is already a member of this group")
    
    if group_member.member_type == MemberType.GROUP and group_member.member_group_id is not None:
        if detect_loop(db, group_member.group_id, group_member.member_group_id):
            raise ValueError("Adding this group would create a circular membership")

    db_group_member = GroupMember(**group_member.dict())
    db.add(db_group_member)
    db.commit()
    db.refresh(db_group_member)
    return db_group_member


def get_group_member_by_id(db: Session, group_member_id: int):
    return db.query(GroupMember).filter(GroupMember.id == group_member_id).first()


def get_group_members(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(GroupMember)
        .options(
            joinedload(GroupMember.user),
            joinedload(GroupMember.group),
            joinedload(GroupMember.member_group)
        )
        .offset(skip)
        .limit(limit)
        .all()
    )
    
def get_group_members_by_group_id(db: Session, group_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(GroupMember)
        .filter(GroupMember.group_id == group_id)
        .options(
            joinedload(GroupMember.user),
            joinedload(GroupMember.group),
            joinedload(GroupMember.member_group)
        )
        .offset(skip)
        .limit(limit)
        .all()
    )
############################################################################################################################################################################
# Update group member                                                                                                                                                      #
# FIXME: This function does not work on group members with member_type == MemberType.GROUP                                                                                 #
############################################################################################################################################################################

def update_group_member(db: Session, group_member_id: int, group_member_update: GroupMemberCreate):
    db_group_member = get_group_member_by_id(db, group_member_id)
    if not db_group_member:
        return None

    for key, value in group_member_update.dict().items():
        setattr(db_group_member, key, value)

    db.add(db_group_member)
    db.commit()
    db.refresh(db_group_member)
    return db_group_member

def delete_group_member(db: Session, group_member_id: int):
    db_group_member = get_group_member_by_id(db, group_member_id)
    if not db_group_member:
        return None

    db.delete(db_group_member)
    db.commit()
    return db_group_member


############################################################################################################################################################################
#   Group Members (Recursive)   2021-05-07  23:33                                                                                                                          #
############################################################################################################################################################################

def is_member_recursive(
    db: Session,
    group_id: int,
    member_id: Optional[int] = None,
    member_group_id: Optional[int] = None,
    member_type: Optional[MemberType] = None,
    depth: int = 1,
    current_depth: int = 0
) -> bool:
    if member_id is not None:
        member_type = MemberType.USER
    elif member_group_id is not None:
        member_type = MemberType.GROUP
    else:
        raise ValueError("Either member_id or member_group_id must be provided")
    
    if member_id is not None and member_group_id is not None:
        raise ValueError("Only one of member_id or member_group_id must be provided")

    if current_depth > depth:
        return False

    direct_membership = (
        db.query(GroupMember)
        .filter(
            GroupMember.group_id == group_id,
            GroupMember.member_type == member_type,
            GroupMember.status == GroupStatus.ACTIVE,
        )
    )

    if member_type == MemberType.USER:
        direct_membership = direct_membership.filter(GroupMember.member_id == member_id)
    else:
        direct_membership = direct_membership.filter(GroupMember.member_group_id == member_group_id)

    if direct_membership.first():
        return True

    if member_type == MemberType.GROUP:
        subgroups = (
            db.query(GroupMember)
            .filter(
                GroupMember.member_group_id == member_group_id,
                GroupMember.member_type == MemberType.GROUP,
                GroupMember.status == GroupStatus.ACTIVE,
            )
            .all()
        )

        for subgroup in subgroups:
            if is_member_recursive(
                db,
                group_id,
                member_group_id=subgroup.group_id,
                depth=depth,
                current_depth=current_depth + 1,
            ):
                return True

    return False



# TODO: Add CRUD for Equipment


# Rack (Moved to crud/crud_rack.py)

"""
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
"""

############################################################################################################################################################################
# IPaddress
############################################################################################################################################################################
from ipaddress import IPv4Address

# Get ipaddress by id
def get_ipaddress(db: Session, ipaddress_id: int):
    return db.query(IPAddress.IPAddress).filter(IPAddress.id == ipaddress_id).first()

# Get all ipaddresses
def get_ipaddresses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(IPAddress.IPAddress).offset(skip).limit(limit).all()

# Create ipaddress
def create_ipaddress(db: Session, ipaddress: IPAddressCreate):
    db_ipaddress = IPAddress.IPAddress(**ipaddress.dict())
    db.add(db_ipaddress)
    db.commit()
    db.refresh(db_ipaddress)
    return db_ipaddress

# Update ipaddress
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

# Delete ipaddress
def delete_ipaddress(db: Session, ipaddress_id: int):
    db_ipaddress = get_ipaddress(db, ipaddress_id)
    if db_ipaddress is None:
        return None

    db.delete(db_ipaddress)
    db.commit()
    return db_ipaddress
############################################################################################################################################################################
# Subnet
############################################################################################################################################################################

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


def update_subnet(db: Session, subnet_id: int, subnet_data: SubnetUpdate) -> Optional[Subnet]:
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

# Split a subnet into multiple smaller subnets
# This funcctions needs some work. It should be able to split a subnet into multiple smaller subnets.
def split_subnet(subnet: str, new_mask_bits: int, db: Session):
    # Parse input subnet and new mask
    original_network = IPv4Network(subnet)
    new_mask = int(new_mask_bits)

    if new_mask <= original_network.prefixlen:
        raise ValueError("New mask must be greater than the original mask")

    # Split the subnet into smaller subnets
    new_subnets = list(original_network.subnets(new_prefix=new_mask))

    # Create SubnetCreate instances for each new subnet
    subnet_create_list = []
    for new_subnet in new_subnets:
        new_subnet_create = SubnetCreate(subnet=str(new_subnet.network_address), mask=f"{new_mask}")# FIXME: This should be saved as an integer in the database. (CIDR notation))
        subnet_create_list.append(new_subnet_create)

    # Save new subnets to the database
    new_subnets_in_db = []
    for new_subnet_create in subnet_create_list:
        new_subnet_in_db = create_subnet(db=db, subnet=new_subnet_create)
        new_subnets_in_db.append(new_subnet_in_db)

    return new_subnets_in_db

def scan_subnet(db: Session, subnet_id: int, method: str = "ping"):
    subnet = db.query(Subnet).filter(Subnet.id == subnet_id).first()
    

    if not subnet:
        return None

# Get all registered IP addresses in subnet
# Comments: Roy Michelsen 2021-05-09 07:00
# TODO: This function should be moved to crud_ipaddress.py or crud_subnet.py
# TODO: Implememnt some checks to ensure that we are getting the IP addresses mapped to the spesific subnet id, due to the fact that we can have overlapping subnets.
# We have no way of knowing witch subnet we are checking, as we need some function to map both the FreeHCI appliance and subnet to the same "visibility domain", "isolation domain" or something like that.
# We can solve this by having distributed FreeHCI appliances, and have a central database that keeps track of all the appliances, subnets, vlans eg. AKA: FreeHCI orchestrator and FreeHCI satellites.
# At least we need some way to identify wich subnets and vlans that are mapped to the same FreeHCI appliance.
# Not sure if my explenation makes any sense, but I hope you get the idea.

def get_ip_addresses_in_subnet(db: Session, subnet: str):
    # Parse input subnet
    network = IPv4Network(subnet)

    # Get all IP addresses in the database
    all_ip_addresses = db.query(IPAddress).all()

    # Filter IP addresses that belong to the input subnet
    ip_addresses_in_subnet = []
    for ip_address in all_ip_addresses:
        ip = IPv4Address(ip_address.ip)
        if ip in network:
            ip_addresses_in_subnet.append(ip_address)

    return ip_addresses_in_subnet


"""
def split_subnet(db: Session, subnet_id: int, mask: int) -> Optional[Subnet]:
    subnet_to_split = db.query(Subnet).filter(Subnet.id == subnet_id).first()
    new_subnets = IPv4Network.subnets(subnet_to_split, new_prefix=mask)
    #new_subnets = subnet_to_split #subnet.split(new_prefix=mask)
    return new_subnets
"""


############################################################################################################################################################################
# Customer
############################################################################################################################################################################

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

############################################################################################################################################################################
#  VLAN
############################################################################################################################################################################
def get_vlan(db: Session, vlan_id: int):
    return db.query(VLAN).filter(VLAN.vlanId == vlan_id).first()


def get_vlans(db: Session, skip: int = 0, limit: int = 100):
    return db.query(VLAN).offset(skip).limit(limit).all()

# File: models\crud.py
def create_vlan(db: Session, vlan: VLANCreate):
    db_vlan = VLAN(**vlan.dict())
    db.add(db_vlan)
    db.commit()
    db.refresh(db_vlan)
    return db_vlan

def update_vlan(db: Session, vlan: VLANUpdate):
    db_vlan = get_vlan(db, vlan.vlanId)
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

############################################################################################################################################################################
# Sections
############################################################################################################################################################################

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

############################################################################################################################################################################
# VRF
############################################################################################################################################################################

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

############################################################################################################################################################################
# Location
############################################################################################################################################################################

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