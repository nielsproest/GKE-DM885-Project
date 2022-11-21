from typing import List, Union

from pydantic import BaseModel

class Solver(BaseModel):
    solverId: str
    name: str
    dockerImage: str

    class Config:
        orm_mode = True

        