# File: models/groups_schemas.py
from pydantic import BaseModel
from typing import Optional
from .group_and_member_models import GroupStatus, GroupType
from datetime import datetime

class GroupCreate(BaseModel):
    name: str
    email: Optional[str] = None
    description: Optional[str] = None
    grouptype: GroupType
    lastupdatedby: Optional[str] = "system"
    expires: Optional[datetime] = None
    status: GroupStatus = GroupStatus.ACTIVE
    manager: Optional[str] = None

class GroupRead(BaseModel):
    id: int
    name: str
    email: Optional[str]
    description: Optional[str]
    grouptype: GroupType
    lastupdated: datetime
    lastupdatedby: str
    expires: Optional[datetime]
    status: GroupStatus
    manager: Optional[str]

    class Config:
        orm_mode = True
