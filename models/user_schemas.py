# models/user_schemas.py

from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    firstname: Optional[str] = ""
    lastname: Optional[str] = ""
    phone: Optional[str] = ""
    streetaddress1: Optional[str] = ""
    streetaddress2: Optional[str] = ""
    postalcode: Optional[str] = ""
    city: Optional[str] = ""
    company: Optional[str] = ""
    department: Optional[str] = ""
    country: Optional[str] = ""
    
    
    
