# Filename: group_relations.py

from enum import Enum as PyEnum
import datetime

from sqlalchemy import Column, Integer, ForeignKey, String, Enum, DateTime
from sqlalchemy.orm import relationship
from .database import Base

class MemberType(PyEnum):
    USER = "user"
    GROUP = "group"

class GroupMember(Base):
    __tablename__ = "group_members"
    #__table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    member_group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    member_type = Column(Enum(MemberType), nullable=False)
    lastupdated = Column(DateTime, index=True, default=datetime.datetime.utcnow)
    lastupdatedby = Column(String, index=True, default="system")
    expires = Column(DateTime, index=True, nullable=True)
    status = Column(Enum("GroupStatus"), index=True, default="active")

    user = relationship("User", back_populates="group_members")
