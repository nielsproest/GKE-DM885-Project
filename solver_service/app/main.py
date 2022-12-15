from fastapi import FastAPI, Depends, HTTPException
import uuid
import os
import requests
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
from sqlalchemy.orm import Session
from typing import List, Union

from models import Solver
from crud import cGetAllSolvers, cPostSolver, cDeleteSolver, cGetSolver
from database import engine, SessionLocal
from auth_handler import JWTBearer
from auth import setPublicKey

Solver.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

# CHANGE FOR PRODUCTION
origins = [
    "http://localhost",
    "http://localhost:3000",
]

# Adding cors rules
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

auth_url = "http://auth-service.default.svc.cluster.local:5000"

@app.on_event("startup")
async def startup_event():    
    db = SessionLocal()
    solvers = getAllSolvers(db)

    #Change name, and potentially add more solvers

    permSolvers = {"solver1": "hakankj/fzn-picat-sat", "solver2": "gkgange/geas-mznc2022"}

    solverURLs = []

    for solver in solvers:
        solverURLs.append(solver.dockerImage)

    for perm in permSolvers:
        if not permSolvers.get(perm) in solverURLs:
            print("added solver: " + permSolvers.get(perm))
            cPostSolver(db, perm, permSolvers.get(perm))

    if os.getenv('KUBERNETES_SERVICE_HOST'):
        r = requests.get(url = auth_url + "/keys/public_key")
        data = r.json()
        setPublicKey(data)
    else:
        setPublicKey('''-----BEGIN PUBLIC KEY-----
            MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvpAXDxizoN4MHs0qJrQ9J/Dc+95mLbT7o/haw2vXuB2LoSp855W/5hpPqyhAkPmKJEzICp6Ke72a2oUVeJb8lckM3km9dxFBvNsbMEpKEOO1/WhmWw8aDwBI7E0s7KAXHSdqCBncB4L3W37O9c6bQ2QrGpfrN82yFXez25tdv1ODc7bzfYFdD5LHNVymYl0E+dR/4P2P/+YxUX7omUI9Bqt6jdw6uERt2tcyT0PFT2DQwf3mtrXCufo68uMfxKP0TN5c1Zan4jwXeiJE4wHPzFgaWTzgKB6xayJqkgI9nhy5KaONIKe+ZCerrsBKztk9R8uH38GdI2rcwCPYi2AkkQIDAQAB
            -----END PUBLIC KEY-----''')
    
    return

@app.get("/solver", dependencies=[Depends(JWTBearer())])
def getAllSolvers(db: Session = Depends(get_db)):
    
    return cGetAllSolvers(db)

@app.get("/solver/{id}", dependencies=[Depends(JWTBearer())])
def getSolver(solverId: str, db: Session = Depends(get_db)):

    if not isValidUuid(solverId):
        raise HTTPException(status_code=500, detail=f"Id not valid")
        
    solver = cGetSolver(db, solverId)

    return solver

@app.delete("/solver/{id}", dependencies=[Depends(JWTBearer())])
def deleteSolver(solverId: str, db: Session = Depends(get_db)):

    if not isValidUuid(solverId):
        raise HTTPException(status_code=500, detail=f"Id not valid")

    cDeleteSolver(db, solverId)

    return

@app.post("/solver/{name}", dependencies=[Depends(JWTBearer())])
def postSolver(name: str, image: str, db: Session = Depends(get_db)):

    if not verify_image(image):
        raise HTTPException(status_code=405, detail=f"Docker image could not be verified")

    cPostSolver(db, name, image)

    return

def isValidUuid(solverId) -> bool:
    try:
        uuid.UUID(str(solverId))
        return True
    except ValueError:
        return False


def verify_image(dockerImage: str) -> bool:
    #TODO: verify image by building imgage in container

    dockerRepository = "https://hub.docker.com/r/"
    dockerOfficial = "https://hub.docker.com/_/"

    print(dockerOfficial+dockerImage)

    dockerTest = dockerOfficial+dockerImage
    print(dockerTest)
    r = requests.get(dockerTest)
    print(r)

    return True