
from typing import Union
from typing import List
from enum import Enum

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
