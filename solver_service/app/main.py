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
#import verifier

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

    #TODO: fill initial database with common images - probably redo this part.
    '''
    db = get_db
    solvers = getAllSolvers(db)

    startupSolvers = {"gecode": True, "chuffed": True}

    for solver in solvers:
        if solver.name in startupSolvers:
            startupSolvers[solver.name] = False

    for item in startupSolvers:
        if startupSolvers[item] == True:
            cPostSolver(db, item, item)
    '''

    if os.getenv('KUBERNETES_SERVICE_HOST'):
        r = requests.get(url = auth_url + "/keys/public_key")
        data = r.json()
        print(data)
        setPublicKey(data)

    return

@app.get("/solver", dependencies=[Depends(JWTBearer())])
def getAllSolvers(db: Session = Depends(get_db), token=Depends(JWTBearer())):

    #Maybe don't return image url

    return cGetAllSolvers(db)

@app.get("/solver/{id}", dependencies=[Depends(JWTBearer())])
def getSolver(solverId: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):

    if not isValidUuid(solverId):
        raise HTTPException(status_code=500, detail=f"Id not valid")
        
    solver = cGetSolver(db, solverId)

    return solver

@app.delete("/solver/{id}", dependencies=[Depends(JWTBearer())])
def deleteSolver(solverId: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):

    if not isValidUuid(solverId):
        raise HTTPException(status_code=500, detail=f"Id not valid")

    cDeleteSolver(db, solverId)

    return

@app.post("/solver/{name}/{dockerName}", dependencies=[Depends(JWTBearer())])
def postSolver(name: str, dockerName: str, dockerAuthor: Union[str, None] = None, db: Session = Depends(get_db), token=Depends(JWTBearer())):

    dockerImage = dockerName

    if dockerAuthor:
        dockerImage = (dockerAuthor + "/" + dockerName)
    
    if not verify_image(dockerImage):
        raise HTTPException(status_code=405, detail=f"Docker image could not be verified")

    cPostSolver(db, name, dockerImage)

    return

def isValidUuid(solverId):
    try:
        uuid.UUID(str(solverId))
        return True
    except ValueError:
        return False


def verify_image(dockerImage: str):
    #TODO: verify image by building imgage in container

    #Get and test image

    return True