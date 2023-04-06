# models/hardware.py

from pydantic import BaseModel
from typing import List, Optional

# -----------------
#   Hardware Node
# -----------------

class Model(BaseModel):
    model: str
    manufacturer: str
    gen: Optional[str] = None
    rac_proto: Optional[str] = None
    pn: Optional[str] = None
    image_front: Optional[str] = None
    image_rear: Optional[str] = None

class Node(Model):
    id: int
    name: str
    serial: str
    operating_system: str
    ip_addr: Optional[str] = None
    rack: Optional[str] = None
    rack_pos: Optional[int] = None