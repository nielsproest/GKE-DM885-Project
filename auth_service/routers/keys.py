""" Endpoints relating to external authentication. """

from fastapi import APIRouter, HTTPException, status
from decouple import config
router: APIRouter = APIRouter()
from models import Base, engine
Base.metadata.create_all(bind=engine)

@router.get(
    "/public_key",
)
async def get_public_key():
    """ Expose the public key for external authentication. """

    try:
        return {"message":
            ''.join(open(config("PUBLIC_KEY_FILE", "r")).read().splitlines())
        }
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
    