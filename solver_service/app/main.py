from fastapi import FastAPI, Depends, HTTPException
import uuid
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
from sqlalchemy.orm import Session
from typing import List, Union

from models import Solver
from crud import cGetAllSolvers, cPostSolver, cDeleteSolver, cGetSolver
from auth.auth import decode_jwt, verify_jwt
from database import engine, SessionLocal

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

@app.on_event("startup")
async def startup_event():

    #TODO: fill initial database with common images - probably redo this part.
    
    db = get_db
    solvers = getAllSolvers(db)

    startupSolvers = {"gecode": True, "chuffed": True}

    for solver in solvers:
        if solver.name in startupSolvers:
            startupSolvers[solver.name] = False

    for item in startupSolvers:
        if startupSolvers[item] == True:
            cPostSolver(db, item, item)
            
    return

@app.get("/solver")
def getAllSolvers(db: Session = Depends(get_db)):

    #Maybe don't return image url

    if not (has_permission("TEMP_TOKEN")):
        raise HTTPException(status_code=403)

    return cGetAllSolvers(db)

@app.get("/solver/{id}")
def getSolver(solverId: str, db: Session = Depends(get_db)):

    if not (has_permission("TEMP_TOKEN")):
        raise HTTPException(status_code=403)

    if not isValidUuid(solverId):
        raise HTTPException(status_code=500, detail=f"Id not valid")
        
    solver = cGetSolver(db, solverId)

    return solver

@app.delete("/solver/{id}")
def deleteSolver(solverId: str, db: Session = Depends(get_db)):

    if not (has_permission("TEMP_TOKEN")):
        raise HTTPException(status_code=403)

    if not isValidUuid(solverId):
        raise HTTPException(status_code=500, detail=f"Id not valid")

    cDeleteSolver(db, solverId)

    return

@app.post("/solver/{name}/{dockerName}")
def postSolver(name: str, dockerName: str, dockerAuthor: Union[str, None] = None, db: Session = Depends(get_db)):

    if not (has_permission("TEMP_TOKEN")):
        raise HTTPException(status_code=403)

    dockerImage: str

    if not dockerAuthor:
        dockerImage = dockerName
    else:
        dockerImage = (dockerAuthor + "/" + dockerName)
    
    if not verify_image(dockerImage):
        raise HTTPException(status_code=405, detail=f"image could not be verified")

    cPostSolver(db, name, dockerImage)

    return

def isValidUuid(solverId):
    try:
        uuid.UUID(str(solverId))
        return True
    except ValueError:
        return False

def has_permission(token: str):
    #TODO: check permission properly
    
    decoded = decode_jwt(token)

    if verify_jwt(decoded):
        return True
    
    return True        

def verify_image(dockerImage: str):
    #TODO: verify image by building imgage in container

    #Get and test image

    return True