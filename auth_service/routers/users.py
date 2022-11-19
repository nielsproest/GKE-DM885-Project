""" Endpoints relating to the creation, deletion, and modification of users. """

from fastapi import Depends, APIRouter, HTTPException, status, Body
from decouple import config
from internal import JWTBearer, sign_jwt, decode_jwt

router: APIRouter = APIRouter()


@router.get(
    "/signup",
)
async def create_new_user(
    payload=Body({"username": "myusername", "password": "mypassword"}),
):

    if payload.get("username", None) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing username"
        )

    if len(payload.get("username")) < config(
        "USERNAME_MIN_LENGTH", cast=int, default=3
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 3 characters",
        )

    if payload.get("password", None) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing password"
        )

    # TODO: Better password validation
    if len(payload.get("password")) < config(
        "PASSWORD_MIN_LENGTH", cast=int, default=8
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters",
        )

    # TODO: Create user in database

    # Generate a JWT token for the user
    token = sign_jwt(payload["username"], payload={"admin": True})

    return {"token": token}


@router.get("/login")
async def login_user(
    payload=Body({"username": "myusername", "password": "mypassword"})
):

    if payload.get("username", None) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing username"
        )

    if payload.get("password", None) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing password"
        )

    # TODO: Check if user exists in database

    # Check if the user is already logged in

    # Check if Credentials are correct

    # Generate a JWT token for the user TODO : sign with more than username
    token = sign_jwt(payload["username"])

    return {"token": token}


@router.get("/modify")
async def modify_user(
    payload=Body(
        {"username": "myusername", "data": {"max_ram": 8, "max_cpu": 4, "foo": "bar"}}
    ),
    token=Depends(JWTBearer()),
):

    permissions = decode_jwt(token)

    if permissions.get("admin", False) is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administators can modify users",
        )

    if payload.get("username", None) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing username"
        )

    new_user_data = payload.get("data", None)

    if new_user_data is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing new user data"
        )

    # TODO: Modify user in database

    return {"message": "User modified successfully"}


@router.get("/delete", dependencies=[Depends(JWTBearer())])
async def delete_user(
    payload=Body({"username": "myusername"}), token=Depends(JWTBearer())
):

    permissions = decode_jwt(token)

    if permissions.get("admin", False) is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administators can delete users",
        )

    if payload.get("username", None) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing username"
        )

    # TODO: Check if the user exists

    # TODO: Delete user from database

    return {"message": "User deleted successfully"}


@router.get("/is_username_available")
async def is_username_available(
    payload=Body({"username": "myusername"}), token=Depends(JWTBearer())
):

    if payload.get("username", None) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing username"
        )

    # TODO: Check if the user exists

    # TODO: THIS IS HARD CODED!!! FIX IT!!!
    return {"message": True}
