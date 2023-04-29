# File: models\locations_models.py
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False, default="")
    description = Column(Text)
    address = Column(String(128), nullable=True, default=None)
    lat = Column(String(31), nullable=True, default=None)
    long = Column(String(31), nullable=True, default=None)

    ipaddresses = relationship("IPAddress", back_populates="location")
    subnets = relationship("Subnet", primaryjoin="Subnet.location_id == Location.id", back_populates="location")
    
    