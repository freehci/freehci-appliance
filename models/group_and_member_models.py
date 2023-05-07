# File: models/group_and_member_models.py
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table, Column as SchemaColumn
from .database import Base

import datetime
from enum import Enum as PyEnum

class GroupType(PyEnum):
    LOCAL = "local"
    LDAP = "ldap"
    RADIUS = "radius"
    
class GroupStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class MemberType(PyEnum):
    USER = "user"
    GROUP = "group"
    
# Define group_members table schema
group_members_table = Table(
    "group_members",
    Base.metadata,
    Column("id", Integer, primary_key=True, index=True, autoincrement=True),
    Column("group_id", Integer, ForeignKey("groups.id"), nullable=False),
    Column("member_id", Integer, ForeignKey("users.id"), nullable=True),
    Column("member_group_id", Integer, ForeignKey("groups.id"), nullable=True),
    Column("member_type", Enum(MemberType), nullable=False),  # Add missing member_type column
    Column("lastupdated", DateTime, index=True, default=datetime.datetime.utcnow),  # Add missing lastupdated column
    Column("lastupdatedby", String, index=True, default="system"),  # Add missing lastupdatedby column
    Column("expires", DateTime, index=True, nullable=True),  # Add missing expires column
    Column("status", Enum(GroupStatus), index=True, default=GroupStatus.ACTIVE),  # Add missing status column
    extend_existing=True,
)

class GroupMember(Base):
    __tablename__ = group_members_table
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    member_group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    #member_id = Column(Integer, nullable=False)
    member_type = Column(Enum(MemberType), nullable=False)
    lastupdated = Column(DateTime, index=True, default=datetime.datetime.utcnow)
    lastupdatedby = Column(String, index=True, default="system")
    expires = Column(DateTime, index=True, nullable=True)
    status = Column(Enum(GroupStatus), index=True, default=GroupStatus.ACTIVE)
    
    user = relationship("User", back_populates="group_members")
    group = relationship("Group", back_populates="group_members", foreign_keys=[group_id])
    member_group = relationship("Group", back_populates="member_group_members", foreign_keys=[member_group_id])

class Group(Base):
    __tablename__ = "groups"
    #__table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)                      # Group id (autoincrement) 
    name = Column(String, unique=True, index=True)                                              # name of group (unique) - Required
    email = Column(String, unique=True, index=True, nullable=True)                              # email address of group - Optional
    description = Column(String, unique=False, index=True, nullable=True)                       # description of group - Optional
    grouptype = Column(Enum(GroupType), unique=False, index=True)                               # type of group (eg. 1=local, 2=ldap, 3=radius, etc.) - Required
    lastupdated = Column(DateTime, unique=False, index=True, default=datetime.datetime.utcnow)  # date/time when group was last updated - Will be auto-populated
    lastupdatedby = Column(String, unique=False, index=True, default="system")                  # user id - Will be auto-populated, but chould have default of 'admin' or 'system' 
    expires = Column(DateTime, unique=False, index=True, nullable=True)                         # date/time when group expires - Optional
    status = Column(Enum(GroupStatus), unique=False, index=True, default=GroupStatus.ACTIVE)    # status of group (active, inactive, etc.) - Required (default=active)
    manager = Column(String, unique=False, index=True, nullable=True)                           # user id of group manager - Optional
    
    group_members = relationship("GroupMember", back_populates="group", foreign_keys=[GroupMember.group_id])
    member_group_members = relationship("GroupMember", back_populates="member_group", foreign_keys=[GroupMember.member_group_id])

