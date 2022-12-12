from fastapi import FastAPI, Depends, HTTPException
import uuid

#from . import models, crud, schemas

from fastapi.middleware.cors import CORSMiddleware
from models import Solver
from crud import cGetAllSolvers, cPostSolver, cDeleteSolver, cGetSolver
from schemas import SolverSchema


from decouple import config
from sqlalchemy.orm import Session
from typing import List, Union

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

def has_permission(token: str, permission: str):
    return True

@app.get("/solver")
def getAllSolvers(db: Session = Depends(get_db)):

    if not (has_permission("TEMP_TOKEN", "???")):
        raise HTTPException(status_code=403)

    #return crud.getAllSolvers(db)
    return cGetAllSolvers(db)

@app.get("/solver/{id}")
def getSolver(solverId: str, db: Session = Depends(get_db)):

    if not (has_permission("TEMP_TOKEN", "???")):
        raise HTTPException(status_code=403)

    if not isValidUuid(solverId):
        raise HTTPException(status_code=500)
        
    #solver = crud.getSolver(db, solverId)
    solver = cGetSolver(db, solverId)
    return solver

@app.delete("/solver/{id}")
def deleteSolver(solverId: str, db: Session = Depends(get_db)):

    if not (has_permission("TEMP_TOKEN", "???")):
        raise HTTPException(status_code=403)

    if not isValidUuid(solverId):
        raise HTTPException(status_code=500)
        #return {"Id not valid"}

    #crud.deleteSolver(db, solverId)
    cDeleteSolver(db, solverId)
    return

@app.post("/solver/{name}/{dockerName}")
def postSolver(name: str, dockerName: str, dockerAuthor: Union[str, None] = None, db: Session = Depends(get_db)):
    
    if not (has_permission("TEMP_TOKEN", "???")):
        raise HTTPException(status_code=403)
    if not dockerAuthor:
        #crud.postSolver(db, name, dockerName)
        cPostSolver(db, name, dockerName)
    else:    
        #crud.postSolver(db, name, dockerAuthor + "/" + dockerName)
        cPostSolver(db, name, dockerAuthor + "/" + dockerName)
    return

def isValidUuid(solverId):
    try:
        uuid.UUID(str(solverId))
        return True
    except ValueError:
        return False
