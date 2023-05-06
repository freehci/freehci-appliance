# File: models/groups_models.py
from importlib import import_module
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime
from sqlalchemy.orm import relationship, backref
from .database import Base # declarative_base() is defined in database.py
from .group_relations import GroupMember

import datetime
from enum import Enum as PyEnum

#GroupMember = import_module("models.groups_members_models").GroupMember

class GroupType(PyEnum):
    LOCAL = "local"
    LDAP = "ldap"
    RADIUS = "radius"

class GroupStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class Group(Base):
    __tablename__ = "groups"
    __table_args__ = {'extend_existing': True}

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
    
    group_members = relationship("GroupMember", foreign_keys=[GroupMember.group_id], back_populates="group")
    member_group_members = relationship("GroupMember", foreign_keys=[GroupMember.member_group_id], back_populates="member_group")
