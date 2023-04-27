# File: rack_schemas.py

from pydantic import BaseModel
from typing import Optional

class RackCreate (BaseModel):
    id: Optional[int] = 0
    name: str = "" # name of rack
    description: Optional[str] = ""
    date: Optional[str] = "" # date rack was created
    height: Optional[int] = 2000 # mm
    units: Optional[int] = 42
    width: Optional[int] = 600 # mm
    depth: Optional[int] = 1000 # mm
    vendor: Optional[int] = "" # vendor id
    asset_tag: Optional[str] = "" # asset tag
    equipment_width: Optional[int] = 19 # inches
    room_id: Optional[int] = 0 # foreign key to room
    row: Optional[int] = 0 # row number
    col: Optional[int] = 0 # column number
    