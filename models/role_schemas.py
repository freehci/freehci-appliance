# models/role_schemas.py

from pydantic import BaseModel
from typing import Optional

class RoleCreate(BaseModel):
    name: str
