""" Endpoints relating to the creation, deletion, and modification of users. """
import json

from fastapi import Depends, APIRouter, HTTPException, status, Body
from decouple import config
from internal import JWTBearer, sign_jwt, decode_jwt
from sqlalchemy.orm import Session
router: APIRouter = APIRouter()
from models import User, Base, engine, get_database
Base.metadata.create_all(bind=engine)


@router.get(
    "/signup",
)
async def create_new_user(
    payload=Body({"username": "myusername", "password": "mypassword"}),
    db: Session = Depends(get_database)
):


    if (username := payload.get("username", None)) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing username"
        )

    if len(username) < config(
        "USERNAME_MIN_LENGTH", cast=int, default=3
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 3 characters",
        )

    if (password := payload.get("password", None)) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing password"
        )

    # TODO: Better password validation
    if len(password) < config(
        "PASSWORD_MIN_LENGTH", cast=int, default=8
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters",
        )

    if db.query(User).filter(User.username == username).first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )
    

    base_permissions = json.load(open("base_permissions.json", "r"))

    # TODO : Refactor this out to another module
    new_user = User(username=username, password=password, permissions=base_permissions)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate a JWT token for the user TODO : Make this payload generation use some preset values from the database
    return {"token": sign_jwt(username, base_permissions)}



@router.get("/login")
async def login_user(
    payload=Body({"username": "myusername", "password": "mypassword"}),
    db: Session = Depends(get_database)
):

    if (username := payload.get("username", None)) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing username"
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
    if user.password != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Retrieve the user's permissions from the database
    permissions = user.permissions

    # Generate a JWT token for the user
    return {"token": sign_jwt(username, permissions)}



@router.get("/modify")
async def modify_user(
    payload=Body(
        {"username": "myusername", "data": {"max_ram": 8, "max_cpu": 4, "foo": "bar", "is_admin": True}}
    ),
    token=Depends(JWTBearer()),
    db: Session = Depends(get_database)
):

    permissions = decode_jwt(token).get("permissions", None)
    if permissions is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing permissions"
        )

    if permissions.get("is_admin", False) is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administators can modify users",
        )

    if (username := payload.get("username", None)) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing username"
        )

    new_user_data = payload.get("data", None)

    if new_user_data is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing new user data"
        )


    # Get current permissions
    if (user := db.query(User).filter(User.username == username).first()) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update previous permissions with new permissions given in the payload
    current_permissions = user.permissions
    current_permissions.update(new_user_data)

    # Update the user's permissions in the database
    db.query(User).filter(User.username == username).update({"permissions": current_permissions})
    db.commit()
    db.refresh(user)

    return {"message": "User modified successfully"}


@router.get("/delete", dependencies=[Depends(JWTBearer())])
async def delete_user(
    payload=Body({"username": "myusername"}), token=Depends(JWTBearer()),
    db: Session = Depends(get_database)
):

    permissions = decode_jwt(token).get("permissions", None)

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

    if (username := payload.get("username", None)) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing username"
        )

    # Check if the user exists
    if (user := db.query(User).filter(User.username == username).first()) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Delete the user from the database
    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}


@router.get("/is_username_available")
async def is_username_available(
    payload=Body({"username": "myusername"}), token=Depends(JWTBearer()),
    db: Session = Depends(get_database)
):

    if (username := payload.get("username", None)) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing username"
        )

    # Check if a user exists with the given username
    if (user := db.query(User).filter(User.username == username).first()) is None:
        return {"message": True}

    return {"message": False}

