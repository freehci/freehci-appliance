from pydantic import BaseModel
from typing import Optional

class BMC(BaseModel):
    address: str
    username: Optional[str] = None
    password: Optional[str] = None
    port: Optional[int] = None

class IPMI(BMC):
    port: int = 623

class Redfish(BMC):
    pass  # Add Redfish-specific properties and methods here

class SSH(BMC):
    port: int = 22
    pass  # Add SSH-specific properties and methods here
