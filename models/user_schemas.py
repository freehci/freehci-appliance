# models/user_schemas.py

from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    firstname: Optional[str] = ""
    lasttname: Optional[str] = ""
    phone: Optional[str] = ""
    
