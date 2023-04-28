from typing import Optional
from pydantic import BaseModel


class VLANBase(BaseModel):
    domainId: int = 1
    name: str
    number: Optional[int] = None
    description: Optional[str] = None
    customer_id: Optional[int] = None


class VLANCreate(VLANBase):
    pass


class VLANUpdate(VLANBase):
    pass


class VLANInDBBase(VLANBase):
    vlanId: int

    class Config:
        orm_mode = True


class VLAN(VLANInDBBase):
    pass
