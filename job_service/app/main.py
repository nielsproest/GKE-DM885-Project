import uuid
import os
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import requests

from sqlalchemy.dialects.postgresql import UUID

import models
import crud
import schemas
from schemas import *
import executor
from auth.auth_bearer import JWTBearer
import auth.auth_handler as auth_handler


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

if os.getenv('KUBERNETES_SERVICE_HOST'):
  SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:{os.getenv('POSTGRES_PASSWORD')}@postgres.default.svc.cluster.local:5432/job_service_db"
else:
  SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/job_service_db"

test_mzn = '''int: amount = 78;
array[1..4] of int: denoms = [25, 10, 5, 1];

array[1..4] of var 0..100: counts;

% ------------------------------------------

constraint sum(i in 1..4) ( counts[i] * denoms[i] ) = amount;

var int: coins = sum(counts);
solve minimize coins;

output [
  "coins = ", show(coins), ";",
  "denoms = ", show(denoms), ";",
  "counts = ", show(counts), ";"
];'''


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


app = FastAPI(root_path="/api/jobs" if os.getenv('KUBERNETES_SERVICE_HOST') else "")

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
solver_svc_url = "http://solverservice.default.svc.cluster.local:8080"
fs_svc_url = "http://fs-service.default.svc.cluster.local:9090"


@app.on_event("startup")
async def startup_event():
    if os.getenv('KUBERNETES_SERVICE_HOST'):
      r = requests.get(url = auth_url + "/keys/public_key")
      data = r.json()
      print(data)
      print(data["message"])
      auth_handler.set_public_key(data["message"])

class Detail(BaseModel):
    detail: str = "error message"

class Success(BaseModel):
    success: str = "success message"

'''
Returns job with given job_id
'''
@app.get("/job/{job_id}", dependencies=[Depends(JWTBearer())], responses={
        404: {"model": Detail, "description": "The job was not found"},
        200: {"model": Job, "description": "Job with given job_id"},})
def get_job(job_id: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):
    decoded_token = auth_handler.decodeJWT(token)
    uuid = decoded_token.get('uuid')

    job = crud.get_job(db, job_id, uuid)
    if job == None:
      raise HTTPException(status_code=404, detail="Job not found")
    else:
      return job

'''
Returns the list of solvers belonging to the job with the given job_id
'''
@app.get("/job/{job_id}/solvers", dependencies=[Depends(JWTBearer())], responses={
        404: {"model": Detail, "description": "The job was not found"},
        401: {"model": Detail, "description": "User is not authorized to perform this action (due to not being admin, or not having enough available resources, etc.)"},
        200: {"model": List[SolverInstance], "description": "List of solvers belonging to the job with the given job_id"},})
def get_solvers_from_job(job_id: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):
    decoded_token = auth_handler.decodeJWT(token)
    uuid = decoded_token.get('uuid')
    permissions = decoded_token.get('permissions')
    user_from_job = crud.get_user_from_job(db, job_id)

    if permissions.get('is_admin') or str(user_from_job) == str(uuid):
      job = crud.get_solver_instances(db, job_id)
      if job:
        return job
      else:
        raise HTTPException(status_code=404, detail="Job not found")
    else:
      raise HTTPException(status_code=401, detail="You do not have authorization to list this resource")

'''
Deletes the job
This both deletes it from the database and also stops the pod if it is currently running
'''
@app.delete("/job/{job_id}", dependencies=[Depends(JWTBearer())], responses={
        404: {"model": Detail, "description": "The job was not found"},
        401: {"model": Detail, "description": "User is not authorized to perform this action (due to not being admin, or not having enough available resources, etc.)"},
        200: {"model": Success, "description": "Deletes the job"},})
def delete_job(job_id: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):
    decoded_token = auth_handler.decodeJWT(token)
    uuid = decoded_token.get('uuid')
    permissions = decoded_token.get('permissions')
    user_from_job = crud.get_user_from_job(db, job_id)
    if user_from_job == None:
      raise HTTPException(status_code=404, detail="Job not found")

    if permissions.get('is_admin') or str(user_from_job) == str(uuid):
      job = crud.delete_job(db, job_id)
      if job:
        return {"success": "Job deleted successfully"}
      else:
        raise HTTPException(status_code=404, detail="Job not found")
    else:
      raise HTTPException(status_code=401, detail="You do not have authorization to delete this resource")

'''
Deletes all of jobs belonging to the user
This both deletes the jobs from the database and also stops the respective pods if they is currently running
'''
@app.delete("/{user_id}/jobs", dependencies=[Depends(JWTBearer())], responses={
        404: {"model": Detail, "description": "The user was not found"},
        401: {"model": Detail, "description": "User is not authorized to perform this action (due to not being admin, or not having enough available resources, etc.)"},
        200: {"model": Success, "description": "Deletes all of jobs belonging to the user"},})
def delete_all_jobs(user_id: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):
    decoded_token = auth_handler.decodeJWT(token)
    uuid = decoded_token.get('uuid')
    permissions = decoded_token.get('permissions')

    if permissions.get('is_admin') or str(user_id) == str(uuid):
      job = crud.delete_all_jobs(db, user_id)
      if job:
        return {"success": "All of the users jobs where deleted successfully"}
      else:
        raise HTTPException(status_code=404, detail="User not found")
    else:
      raise HTTPException(status_code=401, detail="You do not have authorization to delete this resource")

'''
Stops the given solver from the given job.
This both deletes it from the database and also stops the pod if it is currently running.
If this solver is the last for the job, the job will also be deleted
'''
@app.delete("/job/{job_id}/{solver_id}", dependencies=[Depends(JWTBearer())], responses={
        404: {"model": Detail, "description": "The job or solver was not found"},
        401: {"model": Detail, "description": "User is not authorized to perform this action (due to not being admin, or not having enough available resources, etc.)"},
        200: {"model": Success, "description": "Stops the given solver from the given job"},})
def stop_solver(job_id: str, solver_id: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):
    decoded_token = auth_handler.decodeJWT(token)
    uuid = decoded_token.get('uuid')
    permissions = decoded_token.get('permissions')
    user_from_job = crud.get_user_from_job(db, job_id)
    if user_from_job == None:
      raise HTTPException(status_code=404, detail="Job not found")

    if permissions.get('is_admin') or str(user_from_job) == str(uuid):
      crud.stop_solver(db, job_id, solver_id, user_from_job)
      if crud.solvers_left(db, job_id) < 1:
          crud.delete_job(db, job_id)
      return {"success": "The solver was successfully deleted from the job"}
    else:
      raise HTTPException(status_code=401, detail="You do not have authorization to delete this resource")

'''
Returns list of jobs belonging to the user with the given user_id.
If user does not exist, it returns an empty list
'''
@app.get("/{user_id}/job", dependencies=[Depends(JWTBearer())], responses={
        401: {"model": Detail, "description": "User is not authorized to perform this action (due to not being admin, or not having enough available resources, etc.)"},
        200: {"model": List[Job], "description": "List of jobs belonging to the user with the given user_id"},})
def list_users_jobs(user_id: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):
    decoded_token = auth_handler.decodeJWT(token)
    uuid = decoded_token.get('uuid')
    permissions = decoded_token.get('permissions')

    if permissions.get('is_admin') or str(user_id) == str(uuid):
      return crud.get_jobs(db, user_id)
    else:
      raise HTTPException(status_code=401, detail="You do not have authorization to list this resource")

'''
Creates a job with the parameters from the CreateJob object.
The job is automatically started when first created
'''
@app.post("/job", dependencies=[Depends(JWTBearer())], responses={
        404: {"model": Detail, "description": "One of the specified solvers or files do not exist in the system"},
        401: {"model": Detail, "description": "User is not authorized to perform this action (due to not being admin, or not having enough available resources, etc.)"},
        200: {"model": Job, "description": "Returns the newly created job"},})
def start_job(create_job_request: CreateJob, db: Session = Depends(get_db), token=Depends(JWTBearer())):

    decoded_token = auth_handler.decodeJWT(token)
    uuid = decoded_token.get('uuid')
    permissions = decoded_token.get('permissions')
    print(decoded_token)

    #Check vcpu usage
    requested_vcpus = 0
    for solver in create_job_request.solver_list:
      requested_vcpus += solver.vcpus

    num_vcpus_in_use = crud.num_vcpus_in_use(db, uuid)
    if num_vcpus_in_use + requested_vcpus > int(permissions.get('vcpu')):
      raise HTTPException(status_code=401, detail="User using too many vCPUs")

    #Check ram usage
    requested_ram = 0
    for solver in create_job_request.solver_list:
      requested_ram += solver.ram

    ram_in_use = crud.ram_in_use(db, uuid)
    if ram_in_use + requested_ram > int(permissions.get('ram')):
      raise HTTPException(status_code=401, detail="User using too much RAM")

    for s in create_job_request.solver_list:
      s.image = get_solver_image(s.id, token)

    (mzn, dzn) = get_problem_files(create_job_request.mzn_id, create_job_request.dzn_id, uuid, token)

    new_job = crud.create_job(db, create_job_request, uuid)
    executor.execute_job(new_job, mzn, dzn, db)

    return new_job

'''
Function for getting the docker image associated with the given solver_id, from the solver service.
Needs a valid token to communicate with the solver service
'''
def get_solver_image(solver_id, token):
    if os.getenv('KUBERNETES_SERVICE_HOST'):
      headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
      }
      try:
        r = requests.get(url = solver_svc_url + f"/solver/{solver_id}", headers=headers)
        data = r.json()
        solver_image = data["dockerImage"]
      except:
        raise HTTPException(status_code=404, detail="One of the specified solver images does not exist on the solver servicer")
    else:
      # default if running locally
      solver_image = "gkgange/geas-mznc2022"

    return solver_image


'''
Gets the content of the mzn and/or dzn file of the user with uuid, from the filestorage service.
Needs a valid token to communicate with the solver service.
'''
def get_problem_files(mzn_id, dzn_id, uuid, token):

    headers = {
      "Authorization": f"Bearer {token}",
      "Content-Type": "application/json"
    }

    if os.getenv('KUBERNETES_SERVICE_HOST'):
      try:
        r = requests.get(url = fs_svc_url + f"/{uuid}/{mzn_id}", headers=headers)
        mzn = r.text
      except:
        raise HTTPException(status_code=404, detail="The specified .mzn file does not exist on the file storage service")
    else:
      # default if running locally
      mzn = test_mzn

    if dzn_id != None:
      try:
        r = requests.get(url = fs_svc_url + f"/{uuid}/{dzn_id}", headers=headers)
        dzn = r.text
      except:
        raise HTTPException(status_code=404, detail="The specified .dzn file does not exist on the file storage service")
    else:
        dzn = None

    return (mzn, dzn)


# default user: ae5f1ccd-15db-454b-86bc-bcf5968987e4

