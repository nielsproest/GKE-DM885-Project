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
  SQLALCHEMY_DATABASE_URL = "postgresql://postgres:psltest@postgres.default.svc.cluster.local:5432/job_service_db"
else:
  SQLALCHEMY_DATABASE_URL = "postgresql://postgres:psltest@localhost:5432/job_service_db"

# user = os.environ.get('POSTGRES_USER')
# password = os.environ.get('POSTGRES_PASSWORD')
# postgres_db = os.environ.get('POSTGRES_DB')
# if user and password and postgres_db:
#   SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@postgres.default.svc.cluster.local:5432/{postgres_db}"
#   print(f"postgres URL: {SQLALCHEMY_DATABASE_URL}")
# else:
#   print("Could not access POSTGRES environment vars")
#   print(user)
#   print(password)
#  print(postgres_db)

test_mzn = '''% Colouring Australia using nc colours
int: nc = 3;

var 1..nc: wa;   var 1..nc: nt;  var 1..nc: sa;   var 1..nc: q;
var 1..nc: nsw;  var 1..nc: v;   var 1..nc: t;

constraint wa != nt;
constraint wa != sa;
constraint nt != sa;
constraint nt != q;
constraint sa != q;
constraint sa != nsw;
constraint sa != v;
constraint q != nsw;
constraint nsw != v;
solve satisfy;

output ["wa=\(wa)\t nt=\(nt)\t sa=\(sa)\n",
        "q=\(q)\t nsw=\(nsw)\t v=\(v)\n",
         "t=", show(t),  "\n"];'''

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


@app.get("/job/{job_id}", dependencies=[Depends(JWTBearer())])
def get_job(job_id: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):
    decoded_token = auth_handler.decodeJWT(token)
    uuid = decoded_token.get('uuid')

    return crud.get_job(db, job_id, uuid)

@app.get("/job/{job_id}/solvers", dependencies=[Depends(JWTBearer())])
def get_job(job_id: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):
    decoded_token = auth_handler.decodeJWT(token)
    uuid = decoded_token.get('uuid')

    return crud.get_solver_instances(db, job_id, uuid)

@app.delete("/job/{job_id}", dependencies=[Depends(JWTBearer())])
def delete_job(job_id: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):
    decoded_token = auth_handler.decodeJWT(token)
    uuid = decoded_token.get('uuid')

    #TODO: Stop the execution of the job
    return crud.delete_job(db, job_id, uuid)

@app.delete("/job/{job_id}/{solver_id}", dependencies=[Depends(JWTBearer())])
def stop_solver(job_id: str, solver_id: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):
    decoded_token = auth_handler.decodeJWT(token)
    uuid = decoded_token.get('uuid')

    result = crud.stop_solver(db, job_id, solver_id, uuid)
    #TODO: Stop the execution of the solver

    if crud.solvers_left(db, job_id) < 1:
        # TODO: Does not seem to work...
        crud.delete_job(db, job_id)
        #TODO: Stop the execution of the job
    return result

@app.get("/job", dependencies=[Depends(JWTBearer())])
def get_job_list(db: Session = Depends(get_db), token=Depends(JWTBearer())):
    decoded_token = auth_handler.decodeJWT(token)
    uuid = decoded_token.get('uuid')

    return crud.get_jobs(db, uuid)


@app.post("/job", dependencies=[Depends(JWTBearer())])
def create_job(create_job_request: CreateJob, db: Session = Depends(get_db), token=Depends(JWTBearer())):

    decoded_token = auth_handler.decodeJWT(token)
    uuid = decoded_token.get('uuid')
    #TODO: Check permissions for vCPUs and RAM count

    available_solvers = get_solvers()


    # TODO: Check that solvers exist and are unique
    if len(list(set(map(lambda x: x.name,create_job_request.solver_list)) - set(available_solvers))) > 0:
        raise HTTPException(status_code=400, detail="One or more of the requested solvers are not available")

    # TODO: Verify that mzn file exists
    (mzn, dzn) = get_problem_files(create_job_request.mzn_id, create_job_request.dzn_id, uuid)

    new_job = crud.create_job(db, create_job_request, uuid)

    executor.execute_job(new_job, mzn, dzn, db)
    #TODO: Check if successful

    return new_job



def get_solvers():

    # TODO: Implement call to solver service
    if os.getenv('KUBERNETES_SERVICE_HOST'):
      r = requests.get(url = solver_svc_url + "/solver")
      data = r.json()
      print(data)
      #return list(data)

    return ["hakankj/fzn-picat-sat", "gkgange/geas-mznc2022", "chuffed", "gecode", "OR-Tools"] #TODO: Remove, only for testing

def get_problem_files(mzn_id, dzn_id, uuid):
    #TODO: Contact file services for mzn
    if os.getenv('KUBERNETES_SERVICE_HOST'):
      r = requests.get(url = fs_svc_url + f"/{uuid}/{mzn_id}")
      data = r.json()
      print(data)

    mzn = test_mzn

    if dzn_id != None:
        #TODO: Contact file services for dzn
        dzn = "max_per_block = [1, 2, 1, 2, 1]"
    else:
        dzn = None

    return (mzn, dzn)


# default user: ae5f1ccd-15db-454b-86bc-bcf5968987e4