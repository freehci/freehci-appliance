# This file contains the schemas for the subnets table.
# File location: app\models\subnets_schemas.py

from typing import Optional
from pydantic import BaseModel


class SubnetBase(BaseModel):
    subnet: Optional[str] = None
    mask: Optional[str] = None
    sectionId: Optional[int] = None
    description: Optional[str] = None
    linked_subnet: Optional[int] = None
    firewallAddressObject: Optional[str] = None
    vrfId: Optional[int] = None
    masterSubnetId: int = 0
    allowRequests: bool = False
    vlanId: Optional[int] = None
    showName: bool = False
    device: Optional[int] = 0
    permissions: Optional[str] = None
    pingSubnet: bool = False
    discoverSubnet: bool = False
    resolveDNS: bool = False
    DNSrecursive: bool = False
    DNSrecords: bool = False
    nameserverId: Optional[int] = 0
    scanAgent: Optional[int] = None
    customer_id: Optional[int] = None
    isFolder: bool = False
    isFull: bool = False
    isPool: bool = False
    state: Optional[int] = 2
    threshold: Optional[int] = 0
    location: Optional[int] = None
    editDate: Optional[str] = None
    lastScan: Optional[str] = None
    lastDiscovery: Optional[str] = None


class SubnetCreate(SubnetBase):
    pass


class SubnetUpdate(SubnetBase):
    pass


class SubnetInDBBase(SubnetBase):
    id: int

    class Config:
        orm_mode = True


class Subnet(SubnetInDBBase):
    pass
