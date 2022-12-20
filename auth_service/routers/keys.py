""" Endpoints relating to external authentication. """

from fastapi import APIRouter, HTTPException, status
from decouple import config
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router: APIRouter = APIRouter()

from models import Base, engine

Base.metadata.create_all(bind=engine)


class Message(BaseModel):
    message: str


@router.get(
    "/public_key",
    responses={
        500: {"message": "Public key not found"},
        405: {"message": "Method Not Allowed"},
    },
    response_model=Message,
)
async def get_public_key():
    """Expose the public key for external authentication."""

    try:
        return {"message": "".join(open(config("PUBLIC_KEY_FILE", "r")).read())}
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Public key not found",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
