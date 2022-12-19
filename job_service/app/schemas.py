
from typing import List, Union
from enum import Enum
from sqlalchemy.dialects.postgresql import UUID

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

### Base models

class JobBase(BaseModel):
    mzn_id: int
    dzn_id: Union[int, None] = None
    timeout: int = 60

class SolverInstance(BaseModel):
    id: str
    status: str
    name: str
    result: str
    timeout: int = 60
    vcpus: int = 10
    ram: int = 10
    pod_name: str = ""
    job_id: str

    class Config:
        orm_mode = True

### DB Models

class Job(JobBase):
    id: str
    user_id: str
    result: str
    winning_solver: str
    status: str
    solver_instances: List[SolverInstance] = []

    class Config:
      orm_mode = True

### API related models

class Solver(BaseModel):
    name: str
    id: str
    image: Union[str, None]
    vcpus: int = 1
    timeout: int = 180
    ram: int = 1024

class CreateJob(JobBase):
    solver_list: List[Solver]

    # This class is just for getting a nice example in the FastAPI docs
    class Config:
        schema_extra = {
            "example": {
                "mzn_id": 1,
                "dzn_id": None,
                "timeout": 120,
                "solver_list": [
                  {
                    "id": "213c7f36-dad8-4316-aaac-1a43a4f9062c",
                    "name": "Good Solver",
                    "vcpus": 10,
                    "ram": 10
                  },
                  {
                    "id": "f54aa3f0-85fd-46e5-afd3-b0d534b4ae44",
                    "name": "Another Good Solver",
                    "vcpus": 10,
                    "ram": 10
                  }
                ]
            }
        }

class Status(Enum):
    IN_PROGRESS = 1
    SUCCEEDED = 2
    SUBOPTIMAL = 3
    FAILED = 4

