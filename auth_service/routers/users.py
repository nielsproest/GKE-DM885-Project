""" Endpoints relating to the creation, deletion, and modification of users. """

from fastapi import Depends, APIRouter, HTTPException, status, Body
from decouple import config
from internal import JWTBearer, sign_jwt, decode_jwt
from sqlalchemy.orm import Session


router: APIRouter = APIRouter()

#from models import User, Base, SessionLocal, engine
from models import get_database
#Base.metadata.create_all(bind=engine)


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

    if len(payload.get("username")) < config(
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
    if len(payload.get("password")) < config(
        "PASSWORD_MIN_LENGTH", cast=int, default=8
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters",
        )

    # TODO: Create user in database

    #db_user = User(name=username, password=password)
    #db.add(db_user)
    #db.commit()
    #db.refresh(db_user)


    # Generate a JWT token for the user TODO : Make this payload generation use some preset values from the database
    return {"token": sign_jwt(username, payload={
        "permissions": {
            "is_admin": True,
            "read": True,
            "write": True,
            "delete": False,
            "create": True,

        },
    })}



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

    # TODO: Check if user exists in database

    # Check if the user is already logged in

    # Check if Credentials are correct

    # Generate a JWT token for the user TODO : sign with more than username
    token = sign_jwt(payload["username"])

    return {"token": token}


@router.get("/modify")
async def modify_user(
    payload=Body(
        {"username": "myusername", "data": {"max_ram": 8, "max_cpu": 4, "foo": "bar", "is_admin": True}}
    ),
    token=Depends(JWTBearer()),
    db: Session = Depends(get_database)
):

    permissions = decode_jwt(token).get("permissions", None)

    # Sanity check
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

    # TODO: Modify user in database

    return {"message": "User modified successfully"}


@router.get("/delete", dependencies=[Depends(JWTBearer())])
async def delete_user(
    payload=Body({"username": "myusername"}), token=Depends(JWTBearer()),
    db: Session = Depends(get_database)
):

    permissions = decode_jwt(token).get("permissions", None)

    # Sanity check
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

    # TODO: Check if the user exists

    # TODO: Delete user from database

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

    # TODO: Check if the user exists

    # TODO: THIS IS HARD CODED!!! FIX IT!!!
    return {"message": True}
