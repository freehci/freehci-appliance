# app.py

from fastapi import FastAPI
from api.hardware import router as hardware_router
from api.virtualization import router as virtualization_router


