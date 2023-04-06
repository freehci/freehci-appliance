# main.py

from fastapi import FastAPI
from fastapi import FastAPI, UploadFile, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from fastapi import File
from starlette.requests import Request
from starlette.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import inspect

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

from routers import user # Importing API functions for user

from models import database
from models import User # Importing user class from models/

#print("Imported User model")
User.__table__.create(database.engine, checkfirst=True)
#print("Created users table")

database.Base.metadata.create_all(bind=database.engine)

# Inspect the database to check if the 'users' table was created
inspector = inspect(database.engine)
print("Tables in the database:")
for table_name in inspector.get_table_names():
    print(table_name)

customize_swagger = False #Change this to True if you want to customize the swager docs
 
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


# Plugin 
def install_plugin_from_repository(plugin_url, plugin_name):
    response = requests.get(plugin_url)
    plugin_file_path = os.path.join("app", "plugins", f"{plugin_name}.tar.gz")
    
    with open(plugin_file_path, "wb") as plugin_file:
        plugin_file.write(response.content)

    subprocess.check_call([sys.executable, "-m", "pip", "install", plugin_file_path])


# Landing page
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    title = "FreeHCI Appliance"
    update_url = "https://github.com/freehci/appliance.json"
    message = "This is the landing page for the FreeHCI Appliance. You can find more information and documentation at the following links:"
    return templates.TemplateResponse("my_template.html", {"request": request, "title": title, "message": message, "update_url": update_url})

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
        plugin_instance = plugin_module.Plugin(config={})  # Legg til nødvendig konfigurasjon her
        plugin_instance.execute()
        
@app.post("/run_plugins")
async def run_all_plugins():
    run_plugins()
    return JSONResponse(content={"message": "All plugins executed successfully"})        

# Include additional modules 
app.include_router(user.router)
app.include_router(authentication_router)
app.include_router(appliance_router)
app.include_router(hardware_router)
app.include_router(virtualization_router)

