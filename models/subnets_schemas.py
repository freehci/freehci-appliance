# This file contains the schemas for the subnets table.
# File location: models\subnets_schemas.py

from typing import Optional
from pydantic import BaseModel, validator
from datetime import datetime
import ipaddress


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
    #location: Optional[int] = None
    location_id: Optional[int] = None # Location ID must exist in the locations table
    #editDate: Optional[str] = None
    lastScan: Optional[str] = None
    lastDiscovery: Optional[str] = None
    
    # Validators
    #
    # Validate date format are by now not needed for lastScan and lastDiscovery, but other date fields may be added in the future
    @validator("lastScan", "lastDiscovery", pre=True, allow_reuse=True, always=True)
    def validate_date_format(cls, date_str):
        if date_str is None:
            return date_str
    
        try:
            datetime.fromisoformat(date_str)
            return date_str
        except ValueError:
            raise ValueError("Invalid date format. Please use ISO 8601 format (YYYY-MM-DDTHH:MM:SS.mmmmmm).")

    @validator("subnet", pre=True, always=True)
    def validate_subnet(cls, subnet):
        if subnet is None:
            return subnet

        try:
            ipaddress.IPv4Network(subnet, strict=False)
            return subnet
        except ValueError:
            raise ValueError("Invalid subnet. Please use a valid IPv4 address.")

    @validator("mask", pre=True, always=True)
    def validate_mask(cls, mask):
        if mask is None:
            return mask

        try:
            # Check if mask is in CIDR format
            mask_int = int(mask)
            if 0 <= mask_int <= 32:
                return mask
        except ValueError:
            pass

        try:
            # Check if mask is in decimal format
            mask_ip = ipaddress.IPv4Address(mask)
            mask_bits = bin(int(mask_ip)).count("1")
            if 0 <= mask_bits <= 32:
                return str(mask_bits)
        except ValueError:
            raise ValueError("Invalid mask. Please use a valid CIDR mask (0-32) or decimal notation (e.g., 255.255.255.0).")

        return mask

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
