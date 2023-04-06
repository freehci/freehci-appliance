# api/hardware.py

from typing import List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel
from models.bmc import IPMI, Redfish, SSH
from models.hardware import Node, Model

router = APIRouter()
# TODO: Move to routers

supported_manufacturers = ["Lenovo", "Dell", "HPE"]

nodes = [
    Node(id=1, name="node1", manufacturer="Lenovo", model="xyz", serial="cluster1", operating_system="Linux"),
    Node(id=2, name="node2", manufacturer="Dell", model="abc", serial="cluster2", operating_system="Windows"),
    # ... more nodes
]

models = [
    Model(id=1, name="Proliant DL380", manufacturer="HPE", model="xyz", pn="cluster1"),
    
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