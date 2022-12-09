
from typing import List, Union
from enum import Enum
from sqlalchemy.dialects.postgresql import UUID

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

### Base models

class JobBase(BaseModel):
    mzn_id: str
    dzn_id: Union[str, None] = None
    timeout: int = 60

class SolverInstance(BaseModel):
    id: str
    status: str
    name: str
    timeout: int = 60
    job_id: str

    class Config:
        orm_mode = True

### DB Models

class Job(JobBase):
    id: str
    user_id: str
    result: str
    status: str
    solver_instances: List[SolverInstance] = []

    class Config:
      orm_mode = True

### API related models

class Solver(BaseModel):
    name: str
    vcpus: int = 1
    ram: int = 1024

class CreateJob(JobBase):
    solver_list: List[Solver]

    # This class is just for getting a nice example in the FastAPI docs
    class Config:
        schema_extra = {
            "example": {
                "mzn_id": "6c68de18-43ea-467e-86c9-fd72f7940bec",
                "dzn_id": None,
                "timeout": 120,
                "solver_list": [
                  {
                    "name": "hakankj/fzn-picat-sat",
                    "vcpus": 1,
                    "ram": 1024
                  },
                  {
                    "name": "gkgange/geas-mznc2022",
                    "vcpus": 1,
                    "ram": 1024
                  }
                ]
            }
        }

class Status(Enum):
    IN_PROGRESS = 1
    SUCCEEDED = 2
    SUBOPTIMAL = 3
    FAILED = 4

