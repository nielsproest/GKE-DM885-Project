import uuid
from enum import Enum

from typing import Union
from typing import List
from xmlrpc.client import Boolean

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class Solver(BaseModel):
    id: str
    vcpus: int = 1
    ram: int = 1024

class CreateJob(BaseModel):
    solver_list: List[Solver]
    mzn: str
    dzn: Union[str, None] = None
    timeout: int = 60
    status: str

class Status(Enum):
    IN_PROGRESS = 1
    SUCCEEDED = 2
    SUBOPTIMAL = 3
    FAILED = 4

db = [{
  "job_id": "f3b8921c-3f0c-442e-82f4-8286e24bb50c",
  "status": 2,
  "user_id": "normal_user",
  "solvers": [
    {
      "id": "chuffed",
      "vcpus": 2,
      "ram": 64
    }
  ],
  "mzn": "123",
  "dzn": "123",
  "timeout": 120
  },
  {
  "job_id": "7712980b-80bf-489c-a510-d78a13de507a",
  "status": 1,
  "user_id": "normal_user",
  "solvers": [
    {
      "id": "gecode",
      "vcpus": 1,
      "ram": 256
    }
  ],
  "mzn": "123",
  "dzn": "123",
  "timeout": 120
  },
  {
  "job_id": "d808eada-08a1-42bd-8a59-b1442ec69652",
  "status": 1,
  "user_id": "other_user",
  "solvers": [
    {
      "id": "gecode",
      "vcpus": 4,
      "ram": 512
    }
  ],
  "mzn": "123",
  "dzn": "123",
  "timeout": 120
  }
]

app = FastAPI()


@app.get("/job")
def job():
    #TODO: Check
    user_id = get_user("TEMP_TOKEN")

    return list(filter(lambda x: x["user_id"] == user_id,db))


@app.post("/job")
def create_job(create_job_request: CreateJob):

    if not (has_permission("TEMP_TOKEN", "create_job") or has_permission("TEMP_TOKEN", "enough_ram_allowed")):
        raise HTTPException(status_code=403)

    available_solvers = get_solvers()

    if len(list(set(map(lambda x: x.id,create_job_request.solver_list)) - set(available_solvers))) > 0:
        raise HTTPException(status_code=400, detail="One or more of the requested solvers are not available")


    job_id = uuid.uuid4()
    user_id = get_user("TEMP_TOKEN")

    db.append({
        "job_id": job_id,
        "status": Status.IN_PROGRESS,
        "user_id": user_id,
        "solvers": create_job_request.solver_list,
        "mzn": create_job_request.mzn,
        "dzn": create_job_request.dzn,
        "timeout": create_job_request.timeout
      })

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

    return {"job_id": job_id}




def has_permission(token, permission):
    # TODO: Implement call to authentication service
    return True

def get_solvers():
    # TODO: Implement call to solver service
    return ["chuffed", "gecode"]

def get_problem_files(get_dzn):
    #TODO: Contact file services for mzn
    mzn = "var 1..nc: wa; var 1..nc: nt; var 1..nc: sa; var 1..nc: q;"

    if get_dzn:
        #TODO: Contact file services for dzn
        dzn = "max_per_block = [1, 2, 1, 2, 1]"

    return (mzn, dzn)

def get_user(token):
    #TODO: Contact authentication service
    return "normal_user"


'''
Test POST with curl:

curl -X POST http://localhost:8000/job -H 'Content-Type: application/json' -d '{"solver_list": [{"id": "chuffed","vcpus": 2,"ram": 64}],"mzn": "123","dzn": "123","timeout": 120,"status": "inprogress"}'

'''