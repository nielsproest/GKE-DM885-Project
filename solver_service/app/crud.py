from sqlalchemy.orm import Session
from sqlalchemy import delete

from models import Solver

def cGetAllSolvers(db: Session):
    return db.query(Solver).all()

def cGetSolver(db: Session, solverId: str):
    return db.query(Solver).filter(Solver.id == solverId).first()

def cDeleteSolver(db: Session, solverId: str):
    db_solver = db.query(Solver).filter(Solver.id == solverId).first()
    db.delete(db_solver)
    db.commit()
    return {"success"}

def cPostSolver(db: Session, name: str, dockerImage: str):
    db_solver = Solver(name = name, dockerImage = dockerImage)
    db.add(db_solver)
    db.commit()
    return {"success"}