from sqlalchemy.orm import Session
from sqlalchemy import delete
import uuid

import models, schemas

def get_job(db: Session, job_id: str, user_id: str):
    return db.query(models.Job).filter(models.Job.user_id == user_id).filter(models.Job.id == job_id).first()

def get_jobs(db: Session, user_id: str):
    return list(db.query(models.Job).filter(models.Job.user_id == user_id))

def get_solver_instances(db: Session, job_id: str, user_id: str):
    solvers = db.query(models.Job).filter(models.Job.user_id == user_id).filter(models.Job.id == job_id).first().solver_instances
    return list(solvers)

def delete_job(db: Session, job_id: str, user_id: str):
    #TODO: Check that user owns this JOB
    job = db.query(models.Job).filter(models.Job.id == job_id).filter(models.Job.user_id == user_id).first()
    db.delete(job)
    db.commit()
    return {"success"}

def stop_solver(db: Session, job_id: str, solver_id: str, user_id: str):
    job = db.query(models.Job).filter(models.Job.id == job_id).filter(models.Job.user_id == user_id).first()
    for solver in job.solver_instances:
        if str(solver.id) == str(solver_id):
          db.delete(solver)
          db.commit()
          return {"success"}
    return {"failed to stop solver"}

def solvers_left(db, job_id: str):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    return len(job.solver_instances)

def create_job(db: Session, job: schemas.CreateJob, user_id: str):
    db_job = models.Job(
      user_id=user_id,
      mzn_id=job.mzn_id,
      dzn_id=job.dzn_id,
      result="test",
      timeout=job.timeout,
      status="running")
    db.add(db_job)
    for solver in job.solver_list:
        db_solver = models.SolverInstance(
          status="running",
          name=solver.name,
          job_id=db_job.id
        )
        db_job.solver_instances.append(db_solver)
    db.commit()
    db.refresh(db_job)
    return db_job

def update_solver_instance_result(db: Session, job_id: str, solver_id: str, result: str):
    solvers = db.query(models.Job).filter(models.Job.id == job_id).first().solver_instances
    for solver in solvers:
        if str(solver.id) == str(solver_id):
          solver.result = result
          db.commit()
          return {"success"}
    return {"error"}

def found_result(db: Session, job_id: str, solver_id: str, result: str):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    job.status = "completed"
    job.result = result
    for solver in job.solver_instances:
      if str(solver.id) == str(solver_id):
        solver.status = "completed"
      else:
        solver.status = "stopped"

    db.commit()
    return {"success"}
