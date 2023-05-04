# api/virtualization.py

from typing import List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()
# TODO: Move to routers

# ------------------
#   Virtualization
# ------------------

supported_virtualization_platforms = ["vSphere", "oVirt", "OpenStack", "MS VMM"]

class Cluster(BaseModel):
    id: int
    name: str
    platform: str
    nodes: List[int]  # Liste of node-IDs

clusters = [
    Cluster(id=1, name="cluster1", platform="vSphere", nodes=[1]),
    Cluster(id=2, name="cluster2", platform="oVirt", nodes=[2]),
    # ... more clusters
]

@router.get("/virtualization/platforms", response_model=List[str], tags=["virtualization"])
async def get_supported_virtualization_platforms():
    return supported_virtualization_platforms


@router.post("/virtualization/cluster/{cluster_id}/add_node/{node_id}", tags=["virtualization"])
async def add_node_to_cluster(cluster_id: int, node_id: int):
    for cluster in clusters:
        if cluster.id == cluster_id:
            if node_id not in cluster.nodes:
                cluster.nodes.append(node_id)
                return {"status": "success", "message": f"Node {node_id} added to cluster {cluster_id}"}
            return {"status": "error", "message": f"Node {node_id} is already in cluster {cluster_id}"}
    return {"status": "error", "message": "Cluster not found"}

@router.post("/virtualization/node/{node_id}/maintenance_mode", tags=["virtualization"])
async def set_node_maintenance_mode(node_id: int, mode: bool):
    
    # Here you need to implement the logic to set the maintenance mode for the node in question, depending on which virtualization platform it uses.
    return {"status": "success", "message": f"Node {node_id} maintenance mode set to {mode}"}


@router.post("/virtualization/node/{node_id}/shutdown", tags=["virtualization"])
async def shutdown_node(node_id: int, reason: Optional[str] = None, force: bool = False):
    
    # Here you need to implement the logic to shutdown the node via the OS, depending on which virtualization platform it uses.
    #You must also take into account the `reason` and `force` parameters in this logic.
    return {"status": "success", "message": f"Node {node_id} shutdown initiated", "reason": reason, "force": force}


@router.post("/virtualization/node/{node_id}/start", tags=["virtualization"])
async def start_node(node_id: int):
    # Here you need to implement the logic to start the node via the OS, depending on which virtualization platform it uses.
    return {"status": "success", "message": f"Node {node_id} start initiated"}

@router.delete("/virtualization/cluster/{cluster_id}/remove_node/{node_id}", tags=["virtualization"])
async def remove_node_from_cluster(cluster_id: int, node_id: int):
    for cluster in clusters:
        if cluster.id == cluster_id:
            if node_id in cluster.nodes:
                cluster.nodes.remove(node_id)
                return {"status": "success", "message": f"Node {node_id} removed from cluster {cluster_id}"}
            return {"status": "error", "message": f"Node {node_id} not found in cluster {cluster_id}"}
    return {"status": "error", "message": "Cluster not found"}
