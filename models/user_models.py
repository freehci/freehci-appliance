# models/user_models.py
# Author: Roy Michelsen

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from .database import Base
from .group_and_member_models import Group, GroupStatus, GroupType, MemberType

#Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    
    password = Column(String)
    #firstname  = Column(String)
    #lastname  = Column(String)
    #streetaddress1  = Column(String)
    #streetaddress2  = Column(String)
    
    group_members = relationship("GroupMember", back_populates="user")
    
    

    def __repr__(self):
        return f"<User id={self.id} username={self.username} email={self.email}>"

