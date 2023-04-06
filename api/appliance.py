# api/appliance.py

from typing import List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()
# TODO: Move to routers

# ---------------
#   Appliance
# ---------------
class ApplianceMetrics(BaseModel):
    nodes: int
    cpu: str
    memory: str
    disk: str
    uptime: str
    version: str

@router.get("/appliance/metrics", response_model=ApplianceMetrics)
def get_appliance_metrics():
    return ApplianceMetrics(
        nodes=7,
        cpu="36%",
        memory="2.7GB / 16GB",
        disk="260GB / 500GB",
        uptime="36 days",
        version="1.0.26"
    )

#
# TODO: Consider to change this namespace to "/engine/", and put it in a dedicated module 
#
class ApplianceJob(BaseModel):
    jobid: str
    owner: str
    status: str
    progress: int
    model: str
    comment: str
    
appliance_jobs = [
    ApplianceJob(jobid="1", owner="Peter Parker", status="completed", progress=100, model="Disk Check", comment="Finished successfully"),
    ApplianceJob(jobid="2", owner="Peter Parker", status="running", progress=50, model="Cleanup", comment="In progress"),
    # ... more jobs
]

        
@router.get("/appliance/jobs", response_model=List[ApplianceJob])
def get_appliance_jobs():
    return appliance_jobs


class Scheduler(BaseModel):
    id: int
    name: str
    description: str
    owner: str
    runas: str
    job: ApplianceJob
    start: str #Crontab syntax (m h dom mon dow)
    timeout: int
    
schedulers = [
    Scheduler(id=1, name="diskcheck", description="Run disk check on /dev/sda1", owner="Peter Parker", runas="root", job=appliance_jobs[0], start="47 6    * * 7", timeout=300),
    Scheduler(id=2, name="run cleanup", description="Run cleanup script", owner="Peter Parker", runas="janitor", job=appliance_jobs[1], start="25 6    * * *", timeout=300),
    # ... more schedulers
]

@router.get("/appliance/scheduler", response_model=List[Scheduler])
def get_scheduler():
    return schedulers