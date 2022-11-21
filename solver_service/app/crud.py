from sqlalchemy.orm import Session
from sqlalchemy import delete
import uuid

from . import models, schemas

def getAllSolvers(db: Session):
    return db.select([models.Solver.solverId, models.Solver.name])

def getSolver(db: Session, solverId: str):
    return db.query(models.Solver).filter(models.Solver.solverId == solverId).first()

def deleteSolver(db: Session, solverId: str):
    db.query(models.Solver).filter(models.Solver.solverId == solverId).first().delete()
    db.commit()
    return {"success"}

def postSolver(db: Session, name: str, dockerImage: str):
    db_solver = models.Solver(name = name, dockerImage = dockerImage)
    db.add(db_solver)
    db.commit()
    return {"success"}