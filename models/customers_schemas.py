from typing import Optional
from pydantic import BaseModel


class CustomerBase(BaseModel):
    title: str
    address: Optional[str] = None
    postcode: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    lat: Optional[str] = None
    long: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_mail: Optional[str] = None
    note: Optional[str] = None
    status: Optional[str] = "Active"


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    pass


class CustomerInDBBase(CustomerBase):
    id: int

    class Config:
        orm_mode = True


class Customer(CustomerInDBBase):
    pass
