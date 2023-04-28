# main.py

import logging
#from logging import SysLogHandler # This is not available on Windows

from fastapi import FastAPI, UploadFile, Query
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
from sqlalchemy import inspect
import aiofiles

# Modules required for plugins
import requests
import subprocess
import sys
import os
import importlib

# Addidional modules
from api.appliance import router as appliance_router
from api.hardware import router as hardware_router
from api.virtualization import router as virtualization_router
from api.authentication import router as authentication_router

from routers import user, role  # Importing API functions for user and role
from routers import equipment  # Importing API functions for equipment
#from routers import virtualization  # Importing API functions for virtualization
#from routers import authentication  # Importing API functions for authentication
#from routers import appliance  # Importing API functions for appliance
#from routers import hardware  # Importing API functions for hardware
#from routers import plugin  # Importing API functions for plugin
#from routers import settings  # Importing API functions for settings
from routers import rack  # Importing API functions for logs
#from routers import dashboard  # Importing API functions for dashboard


from models import database
from models import User, Role  # Importing user and role classes from models/
from models import Rack # Importing rack class from models/

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

#print("Imported User model")
User.__table__.create(database.engine, checkfirst=True)
Role.__table__.create(database.engine, checkfirst=True)
Rack.__table__.create(database.engine, checkfirst=True)
#print("Created users table")

database.Base.metadata.create_all(bind=database.engine)

# Inspect the database to check if the 'users' table was created
inspector = inspect(database.engine)
logger.debug("Tables in the database:")

# TODO: Change this to logger.debug
print("Tables in the database:")
for table_name in inspector.get_table_names():
    print(table_name)



 
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

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    title = "FreeHCI Appliance"
    update_url = "https://github.com/freehci/appliance.json" # this is the url for the update.json file. Check if remote file have higher version number than local file
    ui_url = "/ui/"
    message = "This is the landing page for the FreeHCI Appliance. You can find more information and documentation at the following links:"
    return templates.TemplateResponse("start.html", {"request": request, "title": title, "message": message, "update_url": update_url, "ui_url": ui_url})

# Serve the dashboard
@app.get("/ui/", response_class=HTMLResponse)
async def read_root():
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
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

# ------------------
#   Plugin Methods
# ------------------
@app.post("/install_plugin")
async def install_plugin(uploaded_plugin: UploadFile = File(...)):
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

# Include additional modules 
app.include_router(user.router)
app.include_router(role.router)
app.include_router(authentication_router)
app.include_router(appliance_router)
app.include_router(hardware_router)
app.include_router(virtualization_router)
app.include_router(rack.router)

