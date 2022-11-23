from fastapi import FastAPI, Depends, HTTPException
import pydantic
import uuid
from . import models, crud, schemas
from decouple import config
from sqlalchemy.orm import Session
from typing import List, Union

from .database import engine, SessionLocal

models.Solver.metadata.create_all(bind=engine)

has_permission = True; # Temp solution until i get to security part.

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

@app.get("/solver")
def getAllSolvers(db: Session = Depends(get_db)):

    #if not (has_permission("TEMP_TOKEN", "???")):
    #    raise HTTPException(status_code=403)

    return crud.getAllSolvers(db)

@app.get("/solver/{id}", response_model=schemas.Solver)
def getSolver(solverId: str, db: Session = Depends(get_db)):

    #if not (has_permission("TEMP_TOKEN", "???")):
    #    raise HTTPException(status_code=403)

    solver = crud.getSolver(db, solverId)
    return solver

@app.delete("/solver/{id}")
def deleteSolver(solverId: str, db: Session = Depends(get_db)):

    #if not (has_permission("TEMP_TOKEN", "???")):
    #    raise HTTPException(status_code=403)

    crud.deleteSolver(db, solverId)
    return

@app.post("/solver/{name}/{dockerName}")
def postSolver(name: str, dockerName: str, dockerAuthor: Union[str, None] = None, db: Session = Depends(get_db)):
    
    #if not (has_permission("TEMP_TOKEN", "???")):
    #    raise HTTPException(status_code=403)
    if not dockerAuthor:
        crud.postSolver(db, name, dockerName)
    else:    
        crud.postSolver(db, name, dockerAuthor + "/" + dockerName)
    return