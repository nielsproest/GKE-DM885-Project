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


@app.on_event("startup")
async def startup_event():
  if os.getenv('KUBERNETES_SERVICE_HOST'):
    r = requests.get(url = auth_url + "/keys/public_key")
    data = r.json()
    print(data)
    auth_handler.set_public_key(data)


@app.get("/job/{job_id}", dependencies=[Depends(JWTBearer())])
def get_job(job_id: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):
    decoded_token = auth_handler.decodeJWT(token)
    user_id = decoded_token.get('user_id')

    return crud.get_job(db, job_id, user_id)

@app.get("/job/{job_id}/solvers", dependencies=[Depends(JWTBearer())])
def get_job(job_id: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):
    decoded_token = auth_handler.decodeJWT(token)
    user_id = decoded_token.get('user_id')

    return crud.get_solver_instances(db, job_id, user_id)

@app.delete("/job/{job_id}", dependencies=[Depends(JWTBearer())])
def delete_job(job_id: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):
    decoded_token = auth_handler.decodeJWT(token)
    user_id = decoded_token.get('user_id')

    #TODO: Stop the execution of the job
    return crud.delete_job(db, job_id, user_id)

@app.patch("/job/{job_id}", dependencies=[Depends(JWTBearer())])
def stop_solver(job_id: str, solver_id: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):
    decoded_token = auth_handler.decodeJWT(token)
    user_id = decoded_token.get('user_id')

    result = crud.stop_solver(db, job_id, solver_id, user_id)
    #TODO: Stop the execution of the solver

    if crud.solvers_left(db, job_id) < 1:
        crud.delete_job(db, job_id)
        #TODO: Stop the execution of the job
    return result

@app.get("/job", dependencies=[Depends(JWTBearer())])
def get_job_list(db: Session = Depends(get_db), token=Depends(JWTBearer())):
    decoded_token = auth_handler.decodeJWT(token)
    user_id = decoded_token.get('user_id')

    return crud.get_jobs(db, user_id)


@app.post("/job", dependencies=[Depends(JWTBearer())])
def create_job(create_job_request: CreateJob, db: Session = Depends(get_db), token=Depends(JWTBearer())):

    decoded_token = auth_handler.decodeJWT(token)
    user_id = decoded_token.get('user_id')
    #TODO: Check permissions for vCPUs and RAM count

    available_solvers = get_solvers()


    # TODO: Check that solvers exist and are unique
    if len(list(set(map(lambda x: x.name,create_job_request.solver_list)) - set(available_solvers))) > 0:
        raise HTTPException(status_code=400, detail="One or more of the requested solvers are not available")

    # TODO: Verify that mzn file exists
    (mzn, dzn) = get_problem_files(create_job_request.mzn_id, create_job_request.dzn_id)

    executor.execute_job(create_job_request, mzn, dzn)
    #TODO: Check if successful

    return crud.create_job(db, create_job_request, user_id)



def get_solvers():
    # TODO: Implement call to solver service
    return ["hakankj/fzn-picat-sat", "gkgange/geas-mznc2022", "chuffed", "gecode", "OR-Tools"] #TODO: Remove, only for testing

def get_problem_files(mzn_id, dzn_id):
    #TODO: Contact file services for mzn
    mzn = test_mzn

    if dzn_id != None:
        #TODO: Contact file services for dzn
        dzn = "max_per_block = [1, 2, 1, 2, 1]"
    else:
        dzn = None

    return (mzn, dzn)
