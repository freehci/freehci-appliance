# File: groups_members_schemas.py
from pydantic import BaseModel
from typing import Optional
#from .groups_models import GroupStatus
from .group_and_member_models import GroupStatus, MemberType
from .groups_schemas import GroupRead as Group
from .user_schemas import UserRead as User
#from .groups_members_models import MemberType
from datetime import datetime

class GroupMemberCreate(BaseModel):
    group_id: int
    member_id: Optional[int] = None
    member_type: MemberType
    lastupdatedby: Optional[str] = "system"
    expires: Optional[datetime] = None
    status: GroupStatus = GroupStatus.ACTIVE
    member_group_id: Optional[int] = None

class GroupMemberRead(BaseModel):
    id: int
    group_id: int
    member_id: Optional[int] = None
    member_type: MemberType
    lastupdated: Optional[datetime]
    lastupdatedby: Optional[str]
    expires: Optional[datetime]
    status: GroupStatus
    user: Optional[User]
    member_group: Optional[Group]

    class Config:
        orm_mode = True

class GroupMemberResponse(BaseModel):
    id: int
    group_id: int
    member_id: Optional[int]
    member_group_id: Optional[int]
    member_type: MemberType
    lastupdated: Optional[datetime]
    lastupdatedby: Optional[str]
    expires: Optional[datetime]
    status: GroupStatus

    class Config:
        orm_mode = True
