# models/user_schemas.py

from pydantic import BaseModel, validator, EmailStr
from typing import Optional

class UserBaseClass(BaseModel):
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
    
class UserCreate(UserBaseClass):
    username: str
    email: str
    password: str
    
    @validator('email')
    def email_must_contain_at(cls, v):
        if '@' not in v or '.' not in v:
            raise ValueError('must contain an @ and a .')
        return v
    
    

class UserUpdate(UserBaseClass):
    id: Optional[int]
    username: Optional[str]
    email: Optional[str]
    
class UserRead(UserBaseClass):
    id: int
    username: str
    email: str
    password: str

    class Config:
        orm_mode = True # <-- This is important for SQLAlchemy to be able to read the data from the database