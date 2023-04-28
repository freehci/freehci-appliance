from typing import Optional
from pydantic import BaseModel


class SectionBase(BaseModel):
    name: str
    description: Optional[str] = None
    masterSection: Optional[int] = 0
    permissions: Optional[str] = None
    strictMode: Optional[bool] = True
    subnetOrdering: Optional[str] = None
    order: Optional[int] = None
    showSubnet: Optional[bool] = True
    showVLAN: Optional[bool] = False
    showVRF: Optional[bool] = False
    showSupernetOnly: Optional[bool] = False
    DNS: Optional[str] = None


class SectionCreate(SectionBase):
    pass


class SectionUpdate(SectionBase):
    pass


class SectionInDBBase(SectionBase):
    id: int

    class Config:
        orm_mode = True


class Section(SectionInDBBase):
    pass
