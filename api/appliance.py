# api/appliance.py

import socket
from typing import List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel
import psutil
import time
import ctypes   # To access Windows API
import os

if os.name == 'nt':  # Windows
    import wmi


router = APIRouter()
# TODO: Move to routers

# ---------------
#   Appliance
# ---------------

# Get System Information (Windows)


class NetworkInfo(BaseModel):
    interface: str
    name: str
    ipaddr: str
    macaddr: str
    bytes_sent: str
    bytes_received: str
    packets_sent: str
    packets_received: str
    link_speed: Optional[str]
    link_status: Optional[str]

class DiskInfo(BaseModel):
    name: str
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
    network: List[NetworkInfo]
    temperature: str
    uptime: str
    version: str
    
def kelvin_to_celsius(kelvin):
    return kelvin - 273.15    
    
def get_cpu_temp():
    if os.name == 'nt':  # Windows
        try:
            # Connect to WMI
            c = wmi.WMI()
            # Run the WMI query
            thermal_zone_info = c.query("select * from Win32_PerfFormattedData_Counters_ThermalZoneInformation")
            # Print the results
            for item in thermal_zone_info:
                #print(f"Instance Name: {item.Name}")
                #print(f"Temperature: {item.Temperature}")
                #print(f"Throttle Reasons: {item.ThrottleReasons}")
                #print(f"Timestamp: {item.Timestamp_PerfTime}")
                #print(f"Timestamp_Sys100NS: {item.Timestamp_Sys100NS}")
                temp_c = kelvin_to_celsius(item.Temperature).__round__(2) # Convert Kelvin to Celsius
            temp = f"{temp_c: .2f} °C"  
        except:
            temp = "N/A"
            
    else:  # Linux, macOS, etc.
        try:
            temps = psutil.sensors_temperatures(fahrenheit=False)
            temp = temps['coretemp'][0].current
        except:
            temp = "N/A"
    return temp
    
def get_disk_info():
    disk_info_list = []
    disk_partitions = psutil.disk_partitions()
    #print("disk_partitions:", disk_partitions)  # Print disk_partitions

    for partition in disk_partitions:
        disk_usage = psutil.disk_usage(partition.mountpoint)
        
        disk_name = partition.device.split(":")[0]
        #print("disk_name:", disk_name)  # Print disk_name
        
        disk_info = DiskInfo(
            device=partition.device,
            total_space=f"{disk_usage.total} bytes",
            used_space=f"{disk_usage.used} bytes",
            free_space=f"{disk_usage.free} bytes",
            usage_percent=f"{disk_usage.percent}%",
            name = f"{disk_name}:"
        )
        # print("disk_info:", disk_info)  # Print disk_info
        disk_info_list.append(disk_info)

    # print("disk_info_list:", disk_info_list)  # Print disk_info_list

    # Return None if disk_info_list is empty
    if not disk_info_list:
        return None

    return disk_info_list

def get_link_status(interface):
    stats = psutil.net_if_stats()
    if interface in stats:
        return "Up" if stats[interface].isup else "Down"
    return "Unknown"

def get_interface_name(interface: str) -> str:
    addrs = psutil.net_if_addrs()
    for addr in addrs[interface]:
        
        if addr.family == socket.AF_INET:
            
            return addr.address
    return "Unknown"

def get_network_info():
    net_stats = psutil.net_io_counters(pernic=True)
    net_addrs = psutil.net_if_addrs()
    network_info_list = []
    
    for interface in net_stats.keys():
        if interface in net_addrs:
            stats = net_stats[interface]
            network_info = NetworkInfo(
                name=interface,
                macaddr=psutil.net_if_addrs()[interface][0].address,
                ipaddr=get_interface_name(interface),
                interface=interface,
                link_status=get_link_status(interface),
                bytes_sent=f"{stats.bytes_sent} bytes",
                bytes_received=f"{stats.bytes_recv} bytes",
                packets_sent=f"{stats.packets_sent}",
                packets_received=f"{stats.packets_recv}",
            )
            network_info_list.append(network_info)
    return network_info_list
 

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
        network=get_network_info(),
        uptime=calculate_uptime(),
        temperature=get_cpu_temp(),
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