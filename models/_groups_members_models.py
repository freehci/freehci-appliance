# Filename: models/groups_members_models.py

from sqlalchemy import Column, Integer, ForeignKey, String, Enum, DateTime
from sqlalchemy.orm import relationship
from .database import Base # declarative_base() is defined in database.py
from .group_and_member_models import Group, GroupStatus, GroupType
from enum import Enum as PyEnum
import datetime

class MemberType(PyEnum):
    USER = "user"
    GROUP = "group"

class GroupMember(Base):
    __tablename__ = "group_members"
    

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    member_group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    #member_id = Column(Integer, nullable=False)
    member_type = Column(Enum(MemberType), nullable=False)
    lastupdated = Column(DateTime, index=True, default=datetime.datetime.utcnow)
    lastupdatedby = Column(String, index=True, default="system")
    expires = Column(DateTime, index=True, nullable=True)
    status = Column(Enum(GroupStatus), index=True, default=GroupStatus.ACTIVE)

    user = relationship("User", back_populates="group_members")
    group = relationship("Group", back_populates="group_members", foreign_keys=[group_id], remote_side="Group.group_members")
    member_group = relationship("Group", back_populates="member_group_members", foreign_keys=[member_group_id], remote_side="Group.member_group_members")

