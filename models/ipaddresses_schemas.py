from typing import Optional
from pydantic import BaseModel


class IPAddressBase(BaseModel):
    subnetId: Optional[int] = None
    ip_addr: str
    is_gateway: bool = False
    description: Optional[str] = None
    hostname: Optional[str] = None
    mac: Optional[str] = None
    owner: Optional[str] = None
    state: Optional[int] = 2
    switch: Optional[int] = None
    location: Optional[int] = None
    port: Optional[str] = None
    note: Optional[str] = None
    lastSeen: Optional[str] = "1970-01-01 00:00:01"
    excludePing: bool = False
    PTRignore: bool = False
    PTR: Optional[int] = 0
    firewallAddressObject: Optional[str] = None
    editDate: Optional[str] = None
    customer_id: Optional[int] = None


class IPAddressCreate(IPAddressBase):
    pass


class IPAddressUpdate(IPAddressBase):
    pass


class IPAddressInDBBase(IPAddressBase):
    id: int

    class Config:
        orm_mode = True


class IPAddress(IPAddressInDBBase):
    pass
