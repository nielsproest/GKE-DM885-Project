# app/api.py


from fastapi import FastAPI, Body, Depends
from app.model import UserSchema, UserLoginSchema, RequestSchema
from app.auth.auth_handler import signJWT
from app.auth.auth_bearer import JWTBearer

users = []

app = FastAPI()


@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "auth service reached"}


# User Registration and Login Routes

@app.post("/signup", tags=["user"])
async def create_user(user: UserSchema = Body(...)):

    users.append(user) # replace with db call, making sure to hash the password first

    return signJWT(user.email)

def check_user(data: UserLoginSchema):
    for user in users:
        if user.email == data.email and user.password == data.password:
            return True
    return False

@app.post("/login", tags=["user"])
async def user_login(user: UserLoginSchema = Body(...)):
    if check_user(user):
        return signJWT(user.email)
    return {
        "error": "Wrong login details!"
    }


# Permission Routes
@app.get("/has_permissions/", tags=["permissions"])
async def get_permissions(current_user: UserSchema = Depends(JWTBearer()), request: RequestSchema = Body(...)):
    """ This route is used to check if a user has multiple permission """

    return {"message": {p: True for p in request.permissions}}


@app.get("/has_permission/", tags=["permissions"])
async def get_permission(current_user: UserSchema = Depends(JWTBearer()), request: RequestSchema = Body(...)):
    """ This route is used to check if a user has a single permission """

    if len(request.permissions) > 1:
        return {"message": "Please send only one permission"}
    elif len(request.permissions) == 0:
        return {"message": "Please send a permission"}
    else:
        return {"message": {request.permissions[0]: True}}