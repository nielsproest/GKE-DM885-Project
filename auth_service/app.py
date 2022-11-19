""" """

import uvicorn
from fastapi import *
from typing import *
from decouple import config
from routers import *
from internal.auth import sign_jwt, decode_jwt

app = FastAPI()

app.include_router(users.router, prefix="/users", tags=["users"])


@app.get("/")
async def index():

    if not hasattr(index, "counter"):
        index.counter = 0

    token = sign_jwt(index.counter)
    index.counter += 1

    return {"token": token}


if __name__ == "__main__":
    uvicorn.run("app:app", host=config("HOST"), port=int(config("PORT")), reload=True)
