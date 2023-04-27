# models/role_schemas.py

from pydantic import BaseModel
from typing import Optional

class RoleCreate(BaseModel):
    id: Optional[int] = 0
    name: str
    description: Optional[str] = ""
    notes: Optional[str] = ""