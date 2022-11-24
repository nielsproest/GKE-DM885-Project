""" """

import os
import uvicorn
from fastapi import *
from typing import *
from decouple import config
from routers import *
from internal.auth import sign_jwt, decode_jwt

app = FastAPI()

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(keys.router, prefix="/keys", tags=["keys"])


@app.get("/")
async def index():
    return {"message": "Hello, World!"}


if __name__ == "__main__":
    uvicorn.run("app:app", host=config("HOST"), port=int(config("PORT")), reload=True)
