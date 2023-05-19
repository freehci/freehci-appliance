# File: integrations/HPE/iLO.py
# Author: Roy Michelsen
#
# Description: This file contains the functions for interacting with HPE iLO.
# Goal: Create a websocket connection to the iLO Remote Console and act like a proxy between the iLO Remote Console and the user.
# Consider using a web proxy to avoid firewall opening between the user and the iLO Remote Console. This will allow use of a PAM solution for authentication.
# 
# Description                   Port    Protocol
# IPMI/DCMI over LAN port	    623	    UDP
# Remote Console Port	        17990	TCP
# Virtual Media Port	        17988	TCP
# Secure Shell (SSH) Port	    22	    TCP
# HTTPS Port	                443     TCP
# HTTP Port	                    80      TCP

# https://ilorestfulapiexplorer.ext.hpe.com/

# iLO Remote Console
# KVM-over-IP (Keyboard, Video, Mouse over IP)
# https://iLO-address:17990/rcclient.html

# https://10.208.6.101/images/thumbnail.bmp <-- This is the thumbnail image for the remote console

# wss://{iLO_address}/wss/ircport <-- This is the websocket for the remote console


# https://github.com/mildsunrise/ilo-protocol


import websockets.client
from fastapi import FastAPI, WebSocket, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
#from typing import Optional

app = FastAPI()

class ILOCredentials(BaseModel):
    iLO_address: str
    iLO_username: str
    iLO_password: str

async def ilo_remote_console(iLO_address: str, iLO_username: str, iLO_password: str):
    async with websockets.client.connect(f"wss://{iLO_address}:17990/rcclient.html") as websocket:
        # TODO: Implement the logic for interacting with iLO Remote Console.
        # You may need to authenticate with the provided iLO_username and iLO_password.
        pass

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, ilo_credentials: ILOCredentials = Depends()):
    await websocket.accept()
    await ilo_remote_console(ilo_credentials.iLO_address, ilo_credentials.iLO_username, ilo_credentials.iLO_password)
