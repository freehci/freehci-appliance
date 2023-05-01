# File: rack_schemas.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RackBase (BaseModel):

    name: str = ""                          # name of rack
    description: Optional[str] = ""         # description of rack
    height: Optional[int] = 2000            # mm
    units: Optional[int] = 42               # number of units eg. 42U
    width: Optional[int] = 600              # mm
    depth: Optional[int] = 1000             # mm
    vendor: Optional[int] = 0               # vendor id
    asset_tag: Optional[str] = ""           # asset tag
    equipment_width: Optional[int] = 19     # inches
    room_id: Optional[int] = 0              # foreign key to room
    row: Optional[int] = 0                  # row number
    col: Optional[int] = 0                  # column number
    
    
class RackCreate (RackBase):
    pass
    
class RackUpdate (RackBase):
    pass
    
class RackRead (RackBase):
    id: int
    date: Optional[datetime]

    class Config:
        orm_mode = True # <-- This is important for SQLAlchemy to be able to read the data from the database
