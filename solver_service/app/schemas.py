from typing import List
from pydantic import BaseModel

class Solver(BaseModel):
    id: str
    name: str
    dockerImage: str

    class Config:
        orm_mode = True