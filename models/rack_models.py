# Filename: rack_models.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, TIMESTAMP
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Rack(Base):
    __tablename__ = "racks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True) # <-- This should be autoincrement
    name = Column(String, unique=True, index=True) # name of rack
    date = Column(TIMESTAMP, nullable=True, default=func.now(), onupdate=func.now()) # date rack was created
    description = Column(String) # description of rack
    vendor = Column(String) # vendor id
    asset_tag = Column(String) # asset tag
    units = Column(Integer) # number of units eg. 42U
    height = Column(Integer) # in mm
    width = Column(Integer) # in mm
    equipment_width = Column(Integer) # in inches (19" standard)
    depth = Column(Integer) # in mm
    room_id = Column(Integer) # foreign key to room
    row = Column(Integer) # row number
    col = Column(Integer) # column number
    