# main.py

# ANSI color codes
RED = "\033[31m"
GREEN = "\033[32m"
BLUE = "\033[34m"
YELLOW = "\033[33m"
RESET = "\033[0m"

print("\033[32mStarting application...\033[0m")
import logging
#from logging import SysLogHandler # This is not available on Windows

print(f"{BLUE} Importing reqirements...{RESET}")
from fastapi import FastAPI, HTTPException, UploadFile, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from fastapi import File
from fastapi.middleware.cors import CORSMiddleware # For CORS support (Cross Origin Resource Sharing) 
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import engine_from_config, inspect
import aiofiles

# Modules required for plugins
import requests
import subprocess
import sys
import os
import importlib

print (f"{BLUE} Importing modules...{RESET}")
# Addidional modules
from api.appliance import router as appliance_router # TODO: Move this to routers/appliance.py
from api.hardware import router as hardware_router # TODO: Move this to routers/hardware.py
from api.virtualization import router as virtualization_router # TODO: Move this to routers/virtualization.py
from api.authentication import router as authentication_router # TODO: Move this to routers/authentication.py


from models import database
from models import User, Role  # Importing user and role classes from models/
#from models import Rack # Importing rack class from models/
from models import IPAddress
from models import Subnet
from models import VLAN
from models import Group
from models import GroupMember

from models.rack_models import Rack
from models.rack_models import Base as RackBase

# Importing routers
from routers import user, role  # Importing API functions for user and role
from routers import equipment  # Importing API functions for equipment
from routers import subnets  # Importing API functions for Subnets
from routers import vlans  # Importing API functions for VLANs
from routers import customers  # Importing API functions for customers
from routers import rack  # Importing API functions for 
#from routers import locations  # Importing API functions for locations
#from routers import vrf  # Importing API functions for VRFs
#from routers import sections  # Importing API functions for sections
from routers import groups  # Importing API functions for groups
from routers import group_members  # Importing API functions for groups members

#from routers import virtualization  # Importing API functions for virtualization
#from routers import authentication  # Importing API functions for authentication
#from routers import appliance  # Importing API functions for appliance
#from routers import hardware  # Importing API functions for hardware
#from routers import plugin  # Importing API functions for plugin
#from routers import settings  # Importing API functions for settings
#from routers import dashboard  # Importing API functions for dashboard


nocache = True # Add middleware and set nocache to True to disable caching
customize_swagger = False #Change this to True if you want to customize the swager docs
SYSLOG_HOST = "192.168.41.58"
SYSLOG_PORT = 514

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
#handler = SysLogHandler(address=(SYSLOG_HOST, SYSLOG_PORT))
#logger.addHandler(handler)

# Logging
# Warning: This will raise an error on Windows when running the app withouth admin rights
#syslogserver = "192.168.41.58"
#logger = SysLogHandler(address = (syslogserver,514))
#logger("FreeHCI Appliance started")

#.syslog("FreeHCI Appliance started")

print(f"{YELLOW} Initializing database...{RESET}")
#print("Imported User model")
User.__table__.create(database.engine, checkfirst=True)
Role.__table__.create(database.engine, checkfirst=True)
Rack.__table__.create(database.engine, checkfirst=True)
IPAddress.__table__.create(database.engine, checkfirst=True)

# Add these lines after creating the Rack table
metadata = {**database.Base.metadata.tables, **RackBase.metadata.tables}

#print("Created users table")

database.Base.metadata.create_all(bind=database.engine)

# Inspect the database to check if the 'users' table was created
inspector = inspect(database.engine)
logger.debug("Tables in the database:")

from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

# Opprett en session instans
#db = database.SessionLocal()

# TODO: Change this to logger.debug
print(f"{BLUE} Tables in the database:{RESET}")
for table_name in inspector.get_table_names():
    # Get tabel class based on table name
    print(f"{GREEN} - " + table_name + RESET)
#    columns = inspector.get_columns(table_name)
#    for column in columns:
#        print(f"    - {column['name']} ({column['type']})")
#    table_class = metadata[table_name] # <-- This is the line that causes the error
    
     # Utfør en COUNT(*)-spørring på tabellen og hent resultatet
#    count_query = db.query(func.count().label('total')).select_from(table_class)
#    record_count = count_query.scalar()
#
#    print(f" - {table_name}: {record_count} records")

#db.close()
#print("All tables in the dictionary:")
#print(database.Base.metadata.tables)
 
if (customize_swagger):
    from swagger_customization import swagger_ui_html
    app = FastAPI(docs_url=None)
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html(request: Request):
        return await swagger_ui_html(request)

    @app.get("/openapi.json", include_in_schema=False, name="get_openapi")
    async def custom_openapi():
        openapi_schema = get_openapi(
            title="Custom title",
            version="2.5.0",
            description="This is a very custom OpenAPI schema",
            routes=app.routes,
        )
        return openapi_schema
else:
    app = FastAPI()

# CORS (Cross Origin Resource Sharing) support
# Used to disable caching while developing
class CacheControlMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

# Add middleware to disable caching
if(nocache):
    print("Caching disabled")
    app.add_middleware(CacheControlMiddleware)

# Plugin 
def install_plugin_from_repository(plugin_url, plugin_name):
    response = requests.get(plugin_url)
    plugin_file_path = os.path.join("app", "plugins", f"{plugin_name}.tar.gz")
    
    with open(plugin_file_path, "wb") as plugin_file:
        plugin_file.write(response.content)

    subprocess.check_call([sys.executable, "-m", "pip", "install", plugin_file_path])


# Landing page static files
app.mount("/static", StaticFiles(directory="html/static"), name="static")

# Static files for the UI
app.mount("/ui/static", StaticFiles(directory="html/ui/static"), name="ui_static")
#app.mount("/ui", StaticFiles(directory="html/ui"), name="ui")

# Be aware that Vue.js and Jinja2 use the same syntax for variables
templates = Jinja2Templates(directory="html/templates")

@app.get("/", response_class=HTMLResponse, summary="This is the landing page where you can find information about the appliance")
async def read_root(request: Request):
    title = "FreeHCI Appliance"
    update_url = "https://github.com/freehci/appliance.json" # this is the url for the update.json file. Check if remote file have higher version number than local file
    ui_url = "/ui/"
    message = "This is the landing page for the FreeHCI Appliance. You can find more information and documentation at the following links:"
    return templates.TemplateResponse("start.html", {"request": request, "title": title, "message": message, "update_url": update_url, "ui_url": ui_url})

# Serve the dashboard
@app.get("/ui/", response_class=HTMLResponse, summary="This is the UI Dashboard")
async def read_ui_root():
    async with aiofiles.open("html/ui/dashboard.html", mode="r") as f:
        content = await f.read()
    return HTMLResponse(content=content)

# Serve the UI components
@app.get("/ui/components/{filename}")
async def serve_vue_component(filename: str):
    return FileResponse(f"html/ui/components/{filename}", media_type="application/javascript")

# ------------------
#   Example Method
# ------------------
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = ""):
    return {"item_id": item_id, "q": q}

# ------------------
#   Plugin Methods
# ------------------
@app.post("/install_plugin")
async def install_plugin(uploaded_plugin: UploadFile = File(...)):
    if uploaded_plugin.filename is None:
        raise HTTPException(status_code=400, detail="Invalid file name")
    
    plugin_file_path = os.path.join("app", "plugins", uploaded_plugin.filename)
    with open(plugin_file_path, "wb") as plugin_file:
        plugin_file.write(await uploaded_plugin.read())

    subprocess.check_call([sys.executable, "-m", "pip", "install", plugin_file_path])
    return JSONResponse(content={"message": "Plugin installed successfully"})

def discover_plugins():
    plugin_dir = os.path.join("plugins")
    sys.path.insert(0, plugin_dir)
    plugin_files = os.listdir(plugin_dir)
    
    plugins = []
    for plugin_file in plugin_files:
        if plugin_file.endswith(".py") and plugin_file != "__init__.py":
            module_name = plugin_file[:-3]  # remove .py extension
            module = importlib.import_module(module_name)
            plugins.append(module)
    
    return plugins

active_plugins = discover_plugins()

def run_plugins():
    for plugin_module in active_plugins:
        plugin_instance = plugin_module.Plugin(config={})  # add configurations here
        plugin_instance.execute()
        
@app.post("/run_plugins")
async def run_all_plugins():
    run_plugins()
    return JSONResponse(content={"message": "All plugins executed successfully"})        

print("Loading routers...")
# Include additional modules 
app.include_router(user.router)
app.include_router(role.router)
app.include_router(authentication_router)
app.include_router(appliance_router)
app.include_router(hardware_router)
app.include_router(virtualization_router)
app.include_router(rack.router)
app.include_router(subnets.router)
app.include_router(vlans.router)
app.include_router(customers.router)
app.include_router(groups.router)
app.include_router(group_members.router)

print("FreeHCI Appliance started")