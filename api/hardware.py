# api/hardware.py

from typing import List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel
from models.bmc import IPMIoverLAN, Redfish, SSH
from models.hardware import Node, Model

# TODO: Move to routers
# TODO: Add support for Redfish and SSH

router = APIRouter()

supported_manufacturers = [
    "Lenovo", 
    "Dell", 
    "HPE", 
    "Huawei",
    "Supermicro",
    "Cisco",
    "Oracle",
    "IBM",
    "Quanta",
    "RackTop",
    "Raritan",
    "Rittal",
    "Schneider Electric",
    "Server Technology"
] 

nodes = [
    Node(id=1, name="dc3-web-205", manufacturer="HPE", model="Proliant DL 380", serial="US2022001", operating_system="CentOS 7"),
    Node(id=2, name="dc3-web-206", manufacturer="Dell", model="PowerEdge R740", serial="US2022002", operating_system="Windows Server 2019"),
    Node(id=3, name="dc3-web-207", manufacturer="Lenovo", model="ThinkSystem SR650", serial="US2022003", operating_system="Ubuntu 20.04"),
    Node(id=4, name="dc3-web-208", manufacturer="Huawei", model="FusionServer 2288H", serial="CN2022004", operating_system="Debian 10"),
    Node(id=5, name="dc3-web-209", manufacturer="HPE", model="Proliant DL 360", serial="US2022005", operating_system="CentOS 8"),
    Node(id=6, name="dc3-web-210", manufacturer="Dell", model="PowerEdge R640", serial="US2022006", operating_system="Windows Server 2022"),
    Node(id=7, name="dc3-web-211", manufacturer="Lenovo", model="ThinkSystem SR630", serial="US2022007", operating_system="Ubuntu 18.04"),
    Node(id=8, name="dc3-web-212", manufacturer="Huawei", model="FusionServer 1288H", serial="CN2022008", operating_system="Debian 9"),
    Node(id=9, name="dc3-web-213", manufacturer="HPE", model="Proliant DL 580", serial="US2022009", operating_system="CentOS 7"),
    Node(id=10, name="dc3-web-214", manufacturer="Dell", model="PowerEdge R440", serial="US2022010", operating_system="Windows Server 2016"),
]


models = [
    # FIXME: Fix Pydanctic model for hardware (Mismatch). Mypy is complaining about this.
    #Model(id=1, name="Proliant DL380", manufacturer="HPE", model="xyz", pn="cluster1"),
    ...
    
]

@router.get("/hardware/manufacturers", response_model=List[str])
async def get_supported_manufacturers():
    return supported_manufacturers

@router.get("/hardware/nodes", response_model=List[Node])
async def get_nodes(manufacturer: Optional[str] = Query(None), model: Optional[str] = Query(None), serial: Optional[str] = Query(None), operating_system: Optional[str] = Query(None)):
    filtered_nodes = nodes

    if manufacturer:
        filtered_nodes = [node for node in filtered_nodes if node.manufacturer == manufacturer]
    if model:
        filtered_nodes = [node for node in filtered_nodes if node.model == model]
    if serial:
        filtered_nodes = [node for node in filtered_nodes if node.serial == serial]
    if operating_system:
        filtered_nodes = [node for node in filtered_nodes if node.operating_system == operating_system]

    return filtered_nodes

@router.post("/hardware/node/add", response_model=Node)
async def add_node(node: Node):
    nodes.append(node)
    return node

@router.get("/hardware/node/{node_id}", response_model=Node)
async def get_node(node_id: int):
    for node in nodes:
        if node.id == node_id:
            return node
    return None  # Or custom error response