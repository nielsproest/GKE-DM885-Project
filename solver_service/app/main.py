from fastapi import FastAPI, Depends, HTTPException
import pydantic
import uuid
from . import models, crud, schemas
from decouple import config
from sqlalchemy.orm import Session

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

@app.get("/solver", response_model=[schemas.solver])
def getAllSolvers(db: Session = Depends(get_db)):

    if not (has_permission("TEMP_TOKEN", "???")):
        raise HTTPException(status_code=403)

    solvers = crud.getAllSolvers(db)
    return solvers

@app.get("/solver/{solverid}", response_model=schemas.solver)
def getSolver(solverId: str, db: Session = Depends(get_db)):

    if not (has_permission("TEMP_TOKEN", "???")):
        raise HTTPException(status_code=403)

    solver = crud.getSolver(db, solverId)
    return solver

@app.delete("/solver/{solverid}")
def deleteSolver(solverId: str, db: Session = Depends(get_db)):

    if not (has_permission("TEMP_TOKEN", "???")):
        raise HTTPException(status_code=403)

    crud.deleteSolver(db, solverId)
    return

@app.post("/solver/{name}/{dockerImage}")
def postSolver(name: str, dockerImage: str, db: Session = Depends(get_db)):
    
    if not (has_permission("TEMP_TOKEN", "???")):
        raise HTTPException(status_code=403)

    crud.postSolver(db, name, dockerImage)
    return