""" Endpoints relating to the creation, deletion, and modification of users. """
import json
import uuid as uuid_pkg
from fastapi import Depends, APIRouter, HTTPException, status, Body
from decouple import config
from internal import JWTBearer, sign_jwt, decode_jwt, hash_password, verify_password
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router: APIRouter = APIRouter()

from models import User, Base, engine, get_database

Base.metadata.create_all(bind=engine)


class Message(BaseModel):
    message: str


class Token(BaseModel):
    token: str


@router.post(
    "/signup",
    responses={
        400: {"message": "Payload does not fullfill requirements", "model": Message},
        409: {"message": "User already exists", "model": Message},
        415: {
            "message": "Invalid content type, remember to set content-type to application/json",
            "model": Message,
        },
        200: {"token": "signed_token", "model": Token},
        405: {"message": "Method not allowed", "model": Message},
    },
)
async def create_new_user(
    payload=Body({"username": "myusername", "password": "mypassword"}),
    db: Session = Depends(get_database),
):

    try:
        if (username := payload.get("username", None)) is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Missing username"
            )
    except AttributeError:
        raise HTTPException(
            status_code=415,
            detail="Invalid content type, remember to set content-type to application/json",
        )

    if len(username) < config("USERNAME_MIN_LENGTH", cast=int, default=3):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 3 characters",
        )

    if (password := payload.get("password", None)) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing password"
        )

    # TODO: Better password validation
    if len(password) < config("PASSWORD_MIN_LENGTH", cast=int, default=8):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters",
        )

    if db.query(User).filter(User.username == username).first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    base_permissions = json.load(open(config("PATH_TO_BASE_PERMISSIONS"), "r"))

    # Passwords are hashed before being stored in the database
    hashed_password = hash_password(password)
    uuid = uuid_pkg.uuid4()
    new_user = User(
        username=username,
        password=hashed_password,
        permissions=base_permissions,
        uuid=uuid,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate a JWT token for the user TODO : Make this payload generation use some preset values from the database
    return {"token": sign_jwt(username, base_permissions, uuid=uuid)}


@router.post(
    "/login",
    responses={
        400: {"message": "Payload does not fullfill requirements", "model": Message},
        404: {"message": "User not found", "model": Message},
        401: {"message": "Invalid credentials", "model": Message},
        415: {
            "message": "Invalid content type, remember to set content-type to application/json",
            "model": Message,
        },
        200: {"token": "signed_token", "model": Token},
        405: {"message": "Method not allowed", "model": Message},
    },
)
async def login_user(
    payload=Body({"username": "myusername", "password": "mypassword"}),
    db: Session = Depends(get_database),
):

    try:
        if (username := payload.get("username", None)) is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Missing username"
            )
    except AttributeError:
        raise HTTPException(
            status_code=415,
            detail="Invalid content type, remember to set content-type to application/json",
        )

    if (password := payload.get("password", None)) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing password"
        )

    # Check if user exists in database
    if (user := db.query(User).filter(User.username == username).first()) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check if password is correct
    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Retrieve the user's permissions from the database
    permissions = user.permissions
    uuid = user.uuid

    # Generate a JWT token for the user
    return {"token": sign_jwt(username, permissions, uuid=uuid)}


@router.post(
    "/modify",
    responses={
        400: {"message": "Payload does not fullfill requirements", "model": Message},
        403: {"message": "Only administators can modify users", "model": Message},
        415: {
            "message": "Invalid content type, remember to set content-type to application/json",
            "model": Message,
        },
        200: {"token": "signed_token", "model": Token},
        405: {"message": "Method not allowed", "model": Message},
    },
)
async def modify_user(
    payload=Body(
        {
            "uuid": "some-uuid-here",
            "data": {"ram": 2048, "vcpu": 600, "foo": "bar", "is_admin": True},
        }
    ),
    token=Depends(JWTBearer()),
    db: Session = Depends(get_database),
):

    try:
        permissions = decode_jwt(token).get("permissions", None)
    except AttributeError:
        raise HTTPException(
            status_code=415,
            detail="Invalid content type, remember to set content-type to application/json",
        )

    if permissions is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing permissions"
        )

    if permissions.get("is_admin", False) is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administators can modify users",
        )

    if (uuid := payload.get("uuid", None)) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing uuid"
        )

    new_user_data = payload.get("data", None)

    if new_user_data is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing new user data"
        )

    # Get current permissions
    if (user := db.query(User).filter(User.uuid == uuid).first()) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update previous permissions with new permissions given in the payload
    current_permissions = user.permissions
    current_permissions.update(new_user_data)

    # Update the user's permissions in the database
    db.query(User).filter(User.uuid == uuid).update(
        {"permissions": current_permissions}
    )
    db.commit()
    db.refresh(user)

    # Generate a new updated JWT token for the user
    return {"token": sign_jwt(user.username, current_permissions, uuid=user.uuid)}


@router.post(
    "/delete",
    dependencies=[Depends(JWTBearer())],
    responses={
        400: {"message": "Payload does not fullfill requirements", "model": Message},
        403: {"message": "Only administators can delete users", "model": Message},
        415: {
            "message": "Invalid content type, remember to set content-type to application/json",
            "model": Message,
        },
        404: {"message": "User not found", "model": Message},
        200: {"message": "User deleted successfully", "model": Message},
        405: {"message": "Method not allowed", "model": Message},
    },
)
async def delete_user(
    payload=Body({"uuid": "some-uuid-here"}),
    token=Depends(JWTBearer()),
    db: Session = Depends(get_database),
):

    try:
        permissions = decode_jwt(token).get("permissions", None)
    except AttributeError:
        raise HTTPException(
            status_code=415,
            detail="Invalid content type, remember to set content-type to application/json",
        )

    # Sanity Checks
    if permissions is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing permissions"
        )

    if permissions.get("is_admin", False) is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administators can delete users",
        )

    if (uuid := payload.get("uuid", None)) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing uuid"
        )

    # Check if the user exists
    if (user := db.query(User).filter(User.uuid == uuid).first()) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Delete the user from the database
    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}


@router.get(
    "/is_username_available/{username}",
    responses={
        400: {"message": "Missing username"},
        200: {"message": "True/False"},
        405: {"message": "Method not allowed"},
    },
)
async def is_username_available(
    username: str,
    db: Session = Depends(get_database),
):

    if username is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing username"
        )

    # Check if a user exists with the given username
    if (user := db.query(User).filter(User.username == username).first()) is None:
        return {"message": True}

    return {"message": False}


@router.get(
    "/list_users",
    responses={
        415: {
            "message": "Invalid content type, remember to set content-type to application/json",
            "model": Message,
        },
        403: {"message": "Only administators can list users", "model": Message},
        400: {"message": "Missing permissions", "model": Message},
        200: {
            "message": [{"username": "some-username", "uuid": "some-uuid"}],
            "model": Message,
        },
        405: {"message": "Method not allowed", "model": Message},
    },
)
async def list_users(
    token=Depends(JWTBearer()),
    db: Session = Depends(get_database),
):

    try:
        permissions = decode_jwt(token).get("permissions", None)
    except AttributeError:
        raise HTTPException(
            status_code=415,
            detail="Invalid content type, remember to set content-type to application/json",
        )

    # Sanity Checks
    if permissions is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing permissions"
        )

    if permissions.get("is_admin", False) is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administators can list users",
        )

    # Get all users from the database
    users = db.query(User).all()

    # Return a list of all users
    return {
        "message": [{"username": user.username, "uuid": user.uuid} for user in users]
    }


@router.get(
    "/get_my_permissions",
    responses={
        415: {
            "message": "Invalid content type, remember to set content-type to application/json",
            "model": Message,
        },
        400: {"message": "Can not find UUID inside JWT Token", "model": Message},
        404: {"message": "User not found", "model": Message},
        200: {"message": {"permission_a": "value_a"}, "model": Message},
        405: {"message": "Method not allowed", "model": Message},
    },
)
async def get_my_permissions(
    token=Depends(JWTBearer()),
    db: Session = Depends(get_database),
):

    try:
        uuid = decode_jwt(token).get("uuid", None)
    except AttributeError:
        raise HTTPException(
            status_code=415,
            detail="Invalid content type, remember to set content-type to application/json",
        )

    # Sanity Checks, this should never happen as we're decoding the JWT token
    if uuid is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can not find UUID inside JWT Token",
        )

    # Check if the user exists. this should never happen as we're decoding the JWT token
    if (user := db.query(User).filter(User.uuid == uuid).first()) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Return the users permissions
    return {"message": dict({"uuid": user.uuid}, **user.permissions)}


@router.get(
    "/get_permissions/{uuid}",
    responses={
        415: {
            "message": "Invalid content type, remember to set content-type to application/json",
            "model": Message,
        },
        403: {
            "message": "Only administators can get user permissions",
            "model": Message,
        },
        400: {"message": "Missing permissions", "model": Message},
        404: {"message": "User not found", "model": Message},
        200: {"message": {"permission_a": "value_a"}, "model": Message},
        405: {"message": "Method not allowed", "model": Message},
    },
)
async def get_permissions(
    uuid: str,
    token=Depends(JWTBearer()),
    db: Session = Depends(get_database),
):
    try:
        permissions = decode_jwt(token).get("permissions", None)
    except AttributeError:
        raise HTTPException(
            status_code=415,
            detail="Invalid content type, remember to set content-type to application/json",
        )

    # Sanity Checks
    if permissions is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing permissions"
        )

    if permissions.get("is_admin", False) is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administators can get user permissions",
        )

    if uuid is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing username"
        )

    # Check if the user exists
    if (user := db.query(User).filter(User.uuid == uuid).first()) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Return the user's permissions
    return {"message": dict({"uuid": user.uuid}, **user.permissions)}


@router.get(
    "/decode_jwt",
    responses={
        415: {
            "message": "Invalid content type, remember to set content-type to application/json",
            "model": Message,
        },
        403: {
            "message": "Only administators can get user permissions",
            "model": Message,
        },
        400: {"message": "Missing permissions", "model": Message},
        200: {"message": {"permission_a": "value_a"}, "model": Message},
        405: {"message": "Method not allowed", "model": Message},
    },
)
async def _decode_jwt(
    token=Depends(JWTBearer()),
):

    decoded_token = decode_jwt(token)

    try:
        permissions = decoded_token.get("permissions", None)
    except AttributeError:
        raise HTTPException(
            status_code=415,
            detail="Invalid content type, remember to set content-type to application/json",
        )

    # Sanity Checks
    if permissions is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing permissions"
        )

    if permissions.get("is_admin", False) is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administators can get user permissions",
        )

    return {"message": decoded_token}


@router.get(
    "/wave",
    responses={
        200: {"message": "Hello World", "model": Message},
        405: {"message": "Method not allowed", "model": Message},
    },
)
async def wave(token=Depends(JWTBearer())):
    return {"message": "Hello World"}
