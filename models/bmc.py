from pydantic import BaseModel, IPvAnyAddress
from typing import Optional

class BMC(BaseModel):
    name: str
    address: IPvAnyAddress
    username: Optional[str] = None
    password: Optional[str] = None
    port: Optional[int] = None
    vncconsoleport: Optional[int] = 5900
    
class IPMIoverLAN(BMC):
    port: int = 623
    
class Redfish(BMC):
    port = 443
    # https://ilorestfulapiexplorer.ext.hpe.com/
    # https://dell.github.io/iDRAC-Redfish-Scripting/
    # Add Redfish-specific properties and methods here

class SSH(BMC):
    port: int = 22
    # Add SSH-specific properties and methods here

class HTTTPS(BMC):
    port: int = 443
    # Add HTTPS-specific properties and methods here
    # https://iLO-address/images/thumbnail.bmp