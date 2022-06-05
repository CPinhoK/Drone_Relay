from fastapi import FastAPI , HTTPException, Request ,WebSocket
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import random
import string

import os
import time


##MODELS


class Droneinfo(BaseModel):
    id : str
    lat: float
    lon: float
    has_package: bool
    
class Packageinfo(BaseModel):
    has_arrived:bool

class Stationinfo(BaseModel):
    id : str
    lat: float
    lon: float
    drones: List[str]
    
    
DRONES=[]
STATIONS=[]
PACKAGE=[]



app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/img", StaticFiles(directory="./img"), name="img")
app.mount("/js", StaticFiles(directory="./js"), name="js")
templates = Jinja2Templates(directory="./")

@app.get("/")
async def root():
    return {"message": "Hello Payz"}

@app.get("/status")
async def get_status():
    return 0

@app.post("/drone")
async def Add_drone_info(request: Request,dinfo: Droneinfo):
    print(request)
    global DRONES
    for i in range(len(DRONES)):
        if DRONES[i].id==dinfo.id:
            DRONES[i]=dinfo
            return {"Message":"Droneinfo"+dinfo.id+" replaced"}
    DRONES.append(dinfo)
    return {"Message":"Droneinfo "+dinfo.id+" added"}

@app.get("/drone")
async def GET_drone_info(request: Request,id:str = None):
    global DRONES
    if id==None:
        return DRONES
    for i in range(len(DRONES)):
        if DRONES[i].id==id:
            return DRONES[i]
    raise HTTPException(status_code=404, detail="Drone id:"+id+" not found")


@app.post("/package")
async def Add_package_info(request: Request,pinfo: Packageinfo):
    global PACKAGE
    PACKAGE.append(pinfo)
    return {"Message":"Packageinfo "+pinfo+" added"}

@app.get("/package")
async def GET_package_info(request: Request,id:str = None):
    global PACKAGE
    return PACKAGE

@app.post("/station")
async def Add_Station_info(request: Request,sinfo: Stationinfo):
    global STATIONS
    for i in range(len(STATIONS)):
        if STATIONS[i].id==sinfo.id:
            STATIONS[i]=sinfo
            return {"Message":"Stationinfo"+sinfo.id+" replaced"}
    STATIONS.append(sinfo)
    return {"Message":"Stationinfo "+sinfo.id+" added"}

@app.get("/station")
async def GET_Station_info(request: Request,id:str = None):
    global STATIONS
    if id==None:
        return STATIONS
    for i in range(len(STATIONS)):
        if STATIONS[i].id==id:
            return STATIONS[i]
    raise HTTPException(status_code=404, detail="STATION id:"+id+" not found")



@app.get("/map")
def form_post(request: Request):
    return templates.TemplateResponse('index.html', context={'request': request})

