from typing import List
from pydantic import BaseModel

class SolverSchema(BaseModel):
    id: str
    name: str
    dockerImage: str

    class Config:
        orm_mode = True