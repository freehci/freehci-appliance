# File: models\Templatees_schemas.py
# This file contains the Pydantic classes

from typing import Optional
from pydantic import BaseModel


class TemplateBaseSchema(BaseModel):
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


class TemplateInCreateSchema(TemplateBaseSchema):
    pass


class TemplateInUpdateSchema(TemplateBaseSchema):
    pass


class TemplateOutSchema(TemplateBaseSchema):
    id: int # This is a read only variable

    class Config:
        orm_mode = True

"""
The Config class is an inner class of TemplateOutSchema and affects the behavior of this Pydantic model.

TemplateOutSchema is a Pydantic model used to define how an IP address should be serialized into a JSON response when emitted by the API. It inherits from TemplateBaseSchema and adds the id field, which is usually a unique identifier in the database.

The Config class inside TemplateOutSchema has one property, orm_mode, which is set to True. This allows the Pydantic model to read data directly from a SQLAlchemy ORM model, and convert it to a JSON representation. Without orm_mode set to True, Pydantic would not be able to automatically read data from the SQLAlchemy ORM model, and you would have to manually convert the data between the two models.

By setting orm_mode to True, you simplify the process of converting data between SQLAlchemy ORM models and Pydantic models in the API responses. It also makes it easier to keep your code DRY ("Don't Repeat Yourself"), since you don't have to write manual conversion code for every single instance of a model in your API.
"""


