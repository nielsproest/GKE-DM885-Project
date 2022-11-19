import uuid
import os
from decouple import config
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

from sqlalchemy.dialects.postgresql import UUID

import models
import crud
import schemas
from schemas import *
from auth.auth_bearer import JWTBearer
from auth.auth_handler import signJWT


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session


SQLALCHEMY_DATABASE_URL = config('DATABASE_URL')

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()

#@app.get("/job/{job_id}", dependencies=[Depends(JWTBearer())])
@app.get("/job/{job_id}", response_model=schemas.Job)
def get_job(job_id: str, db: Session = Depends(get_db)):
    #TODO: Check if user is authenticated
    if not (has_permission("TEMP_TOKEN", "list_jobs")):
        raise HTTPException(status_code=403)

    user_id = get_user("TEMP_TOKEN")

    return crud.get_job(db, job_id, user_id)

@app.delete("/job/{job_id}")
def delete_job(job_id: str, db: Session = Depends(get_db)):
    #TODO: Check if user is authenticated
    if not (has_permission("TEMP_TOKEN", "delete_job")):
        raise HTTPException(status_code=403)

    user_id = get_user("TEMP_TOKEN")

    #TODO: Stop the execution of the job
    return crud.delete_job(db, job_id, user_id)

@app.patch("/job/{job_id}")
def stop_solver(job_id: str, solver_id: str, db: Session = Depends(get_db)):
    #TODO: Check if user is authenticated
    if not (has_permission("TEMP_TOKEN", "stop_solver")):
        raise HTTPException(status_code=403)

    user_id = get_user("TEMP_TOKEN")

    result = crud.stop_solver(db, job_id, solver_id)
    #TODO: Stop the execution of the job

    if crud.solvers_left(db, job_id) < 1:
        crud.delete_job(db, job_id)
    #TODO: Check if no solvers left for job, and delete job if that is the case
    return result

@app.get("/job")
def get_job_list(db: Session = Depends(get_db)):
    #TODO: Check if user is authenticated
    if not (has_permission("TEMP_TOKEN", "list_jobs")):
        raise HTTPException(status_code=403)

    user_id = get_user("TEMP_TOKEN")
    #TODO: Connect to DB
    return crud.get_jobs(db, user_id)


@app.post("/job")
def create_job(create_job_request: CreateJob, db: Session = Depends(get_db)):

    if not (has_permission("TEMP_TOKEN", "create_job") or has_permission("TEMP_TOKEN", "enough_ram_allowed")):
        raise HTTPException(status_code=403)

    available_solvers = get_solvers()

    if len(list(set(map(lambda x: x.name,create_job_request.solver_list)) - set(available_solvers))) > 0:
        raise HTTPException(status_code=400, detail="One or more of the requested solvers are not available")

    #TODO: Check that solvers are unique?

    user_id = get_user("TEMP_TOKEN")

    (mzn, dzn) = get_problem_files(create_job_request.mzn_id, create_job_request.dzn_id)


    #TODO: Run Job

    # Check if valid
        # User is authenticated
        # Solvers exist
        # mzn (and possibly dzn) instance(s) exist
        # Not too many vCPUs
    # Store in DB
    # Create jobs
    # Await return?
        # Update entries in DB
        # Update UI of user

    for solver in create_job_request.solver_list:
      start_job(create_job_request, solver, mzn, dzn)

    return crud.create_job(db, create_job_request, user_id)


def start_job(create_job_request: CreateJob, solver: Solver, mzn, dzn):
  #TODO: Actually spawn a new Pod to run the job
  print(f"Starting job with solver: {solver.name}")
  return


def has_permission(token, permission):
    # TODO: Implement call to authentication service
    return True

def get_solvers():
    # TODO: Implement call to solver service
    return ["chuffed", "gecode", "OR-Tools"] #TODO: Remove, only for testing

def get_problem_files(mzn_id, dzn_id):
    #TODO: Contact file services for mzn
    mzn = "var 1..nc: wa; var 1..nc: nt; var 1..nc: sa; var 1..nc: q;"

    if dzn_id != None:
        #TODO: Contact file services for dzn
        dzn = "max_per_block = [1, 2, 1, 2, 1]"
    else:
        dzn = None

    return (mzn, dzn)

def get_user(token):
    #TODO: Contact authentication service

    #TODO: Remove static user_id for testing
    return "ae5f1ccd-15db-454b-86bc-bcf5968987e4"