# models/user_models.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

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

    def __repr__(self):
        return f"<User id={self.id} username={self.username} email={self.email}>"

