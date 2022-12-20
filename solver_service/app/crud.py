from sqlalchemy.orm import Session

from models import Solver

def cGetAllSolvers(db: Session):
    return db.query(Solver).all()

def cGetSolver(db: Session, solverId: str):
    db_solver = db.query(Solver).filter(Solver.id == solverId).first()
    if db_solver:
        return db_solver
    return None
    
def cDeleteSolver(db: Session, solverId: str):
    db_solver = db.query(Solver).filter(Solver.id == solverId).first()
    if db_solver:
        db.delete(db_solver)
        db.commit()
        return {"success"}
    return None

def cPostSolver(db: Session, name: str, dockerImage: str):
    db_solver = Solver(name = name, dockerImage = dockerImage)
    if db_solver:
        db.add(db_solver)
        db.commit()
        return {"success"}
    return None

def cGetSolverByImage(db: Session, dockerImage: str):
    db_solver = db.query(Solver).filter(Solver.dockerImage == dockerImage).first()
    if db_solver:
        return db_solver
    return None