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


@app.get("/job/{job_id}", dependencies=[Depends(JWTBearer())])
def get_job(job_id: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):
    decoded_token = auth_handler.decodeJWT(token)
    uuid = decoded_token.get('uuid')

    return crud.get_job(db, job_id, uuid)

@app.get("/job/{job_id}/solvers", dependencies=[Depends(JWTBearer())])
def get_job(job_id: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):
    decoded_token = auth_handler.decodeJWT(token)
    uuid = decoded_token.get('uuid')
    permissions = decoded_token.get('permissions')
    user_from_job = crud.get_user_from_job(db, job_id)

    if permissions.get('is_admin') or str(user_from_job) == str(uuid):
      return crud.get_solver_instances(db, job_id)
    else:
      raise HTTPException(status_code=401, detail="You do not have authorization to list this resource")

@app.delete("/job/{job_id}", dependencies=[Depends(JWTBearer())])
def delete_job(job_id: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):
    decoded_token = auth_handler.decodeJWT(token)
    uuid = decoded_token.get('uuid')
    permissions = decoded_token.get('permissions')
    user_from_job = crud.get_user_from_job(db, job_id)

    if permissions.get('is_admin') or str(user_from_job) == str(uuid):
      return crud.delete_job(db, job_id)
    else:
      raise HTTPException(status_code=401, detail="You do not have authorization to delete this resource")

@app.delete("/{user_id}/jobs", dependencies=[Depends(JWTBearer())])
def delete_all_job(user_id: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):
    decoded_token = auth_handler.decodeJWT(token)
    uuid = decoded_token.get('uuid')
    permissions = decoded_token.get('permissions')

    if permissions.get('is_admin') or str(user_id) == str(uuid):
      return crud.delete_all_jobs(db, user_id)
    else:
      raise HTTPException(status_code=401, detail="You do not have authorization to delete this resource")

@app.delete("/job/{job_id}/{solver_id}", dependencies=[Depends(JWTBearer())])
def stop_solver(job_id: str, solver_id: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):
    decoded_token = auth_handler.decodeJWT(token)
    uuid = decoded_token.get('uuid')
    permissions = decoded_token.get('permissions')
    user_from_job = crud.get_user_from_job(db, job_id)

    if permissions.get('is_admin') or str(user_from_job) == str(uuid):
      result = crud.stop_solver(db, job_id, solver_id, user_from_job)
      if crud.solvers_left(db, job_id) < 1:
          crud.delete_job(db, job_id)
      return result
    else:
      raise HTTPException(status_code=401, detail="You do not have authorization to delete this resource")

@app.get("/{user_id}/job", dependencies=[Depends(JWTBearer())])
def get_job_list(user_id: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):
    decoded_token = auth_handler.decodeJWT(token)
    uuid = decoded_token.get('uuid')
    permissions = decoded_token.get('permissions')

    if permissions.get('is_admin') or str(user_id) == str(uuid):
      return crud.get_jobs(db, user_id)
    else:
      raise HTTPException(status_code=401, detail="You do not have authorization to list this resource")


@app.post("/job", dependencies=[Depends(JWTBearer())])
def create_job(create_job_request: CreateJob, db: Session = Depends(get_db), token=Depends(JWTBearer())):

    decoded_token = auth_handler.decodeJWT(token)
    uuid = decoded_token.get('uuid')
    permissions = decoded_token.get('permissions')


    # Check vcpu usage
    # requested_vcpus = 0
    # for solver in create_job_request.solver_list:
    #   requested_vcpus += solver.vcpus

    # num_vcpus_in_use = crud.num_vcpus_in_use(db, uuid)
    # if num_vcpus_in_use + requested_vcpus > int(permissions.get('vcpu')):
    #   raise HTTPException(status_code=401, detail="User using too many vCPUs")

    # Check ram usage
    # requested_ram = 0
    # for solver in create_job_request.solver_list:
    #   requested_ram += solver.ram

    # ram_in_use = crud.ram_in_use(db, uuid)
    # print(ram_in_use)
    # if ram_in_use + requested_ram > int(permissions.get('ram')):
    #   raise HTTPException(status_code=401, detail="User using too much RAM")

    #TODO: Check permissions for RAM

    for s in create_job_request.solver_list:
      s.image = get_solver_image(s.id, token)

    # TODO: Verify that mzn file exists
    (mzn, dzn) = get_problem_files(create_job_request.mzn_id, create_job_request.dzn_id, uuid, token)

    new_job = crud.create_job(db, create_job_request, uuid)

    executor.execute_job(new_job, mzn, dzn, db)
    #TODO: Check if successful

    return new_job



def get_solver_image(solver_id, token):

    #TODO: Implement call to solver service
    if os.getenv('KUBERNETES_SERVICE_HOST'):
      headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
      }
      r = requests.get(url = solver_svc_url + f"/solver/{solver_id}", headers=headers)
      data = r.json()
      print(f"data: {data}")
      solver_image = data["dockerImage"]
      print(f"solver_image: {solver_image}")

      # TODO: Do try-catch and return 400 if solver does not exist
    else:
      solver_image = "hakankj/fzn-picat-sat"

    return solver_image
    #"gkgange/geas-mznc2022", "hakankj/fzn-picat-sat", "laurentperron/or-tools-minizinc-challenge"

def get_problem_files(mzn_id, dzn_id, uuid, token):

    headers = {
      "Authorization": f"Bearer {token}",
      "Content-Type": "application/json"
    }

    if os.getenv('KUBERNETES_SERVICE_HOST'):
      r = requests.get(url = fs_svc_url + f"/{uuid}/{mzn_id}", headers=headers)
      mzn = r.text

      # TODO: Handle file not existing.
    else:
      mzn = test_mzn

    if dzn_id != None:
      if os.getenv('KUBERNETES_SERVICE_HOST'):
        r = requests.get(url = fs_svc_url + f"/{uuid}/{dzn_id}", headers=headers)
        dzn = r.text

        # TODO: Handle file not existing.
      else:
        dzn = "max_per_block = [1, 2, 1, 2, 1]"
    else:
        dzn = None

    return (mzn, dzn)


# default user: ae5f1ccd-15db-454b-86bc-bcf5968987e4

