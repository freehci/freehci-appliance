# api/appliance.py

from typing import List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel
import psutil
import time

router = APIRouter()
# TODO: Move to routers

# ---------------
#   Appliance
# ---------------

class DiskInfo(BaseModel):
    device: str
    total_space: str
    used_space: str
    free_space: str
    usage_percent: str

class ApplianceMetrics(BaseModel):
    nodes: int
    cpu: str
    total_memory: str
    free_memory: str
    disks: Optional[List[DiskInfo]]
    uptime: str
    version: str
    
def get_disk_info():
    disk_info_list = []
    disk_partitions = psutil.disk_partitions()
    print("disk_partitions:", disk_partitions)  # Print disk_partitions

    for partition in disk_partitions:
        disk_usage = psutil.disk_usage(partition.mountpoint)

        disk_info = DiskInfo(
            device=partition.device,
            total_space=f"{disk_usage.total} bytes",
            used_space=f"{disk_usage.used} bytes",
            free_space=f"{disk_usage.free} bytes",
            usage_percent=f"{disk_usage.percent}%",
        )
        print("disk_info:", disk_info)  # Print disk_info
        disk_info_list.append(disk_info)

    print("disk_info_list:", disk_info_list)  # Print disk_info_list

    # Return None if disk_info_list is empty
    if not disk_info_list:
        return None

    return disk_info_list

 

def calculate_uptime():
    boot_time = psutil.boot_time()
    current_time = time.time()

    # Calculate uptime in seconds
    uptime_seconds = current_time - boot_time

    # Convert uptime from seconds to days, hours, minutes and seconds
    uptime_days, rem_seconds = divmod(uptime_seconds, 86400)
    uptime_hours, rem_seconds = divmod(rem_seconds, 3600)
    uptime_minutes, uptime_seconds = divmod(rem_seconds, 60)

    # Return uptime as a string
    return f"{int(uptime_days)} days, {int(uptime_hours)} hours, {int(uptime_minutes)} minutes, {int(uptime_seconds)} seconds"

@router.get("/appliance/metrics", response_model=ApplianceMetrics, tags=["Appliance"], summary="Get appliance metrics (Memory, CPU, Disks, Uptime))")
def get_appliance_metrics():
    return ApplianceMetrics(
        nodes=7,
        cpu=psutil.cpu_percent(interval=1),
        total_memory=psutil.virtual_memory().total,
        free_memory=psutil.virtual_memory().free,
        disks=get_disk_info(),
        uptime=calculate_uptime(),
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

        
@router.get("/appliance/jobs", response_model=List[ApplianceJob], tags=["Appliance"], summary="Get appliance jobs")
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

@router.get("/appliance/scheduler", response_model=List[Scheduler], tags=["Appliance"], summary="Get appliance schedulers")
def get_scheduler():
    return schedulers