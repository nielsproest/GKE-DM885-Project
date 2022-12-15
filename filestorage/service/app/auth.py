from os import getenv
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import jwt, json, time, requests
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


AUTH_HOST = getenv("_AUTH_HOST", "0.0.0.0:5000")
PUBLIC_KEY_FILE="pubkey.pem"
r = requests.get(f"http://{AUTH_HOST}/keys/public_key")
with open(PUBLIC_KEY_FILE, "w") as f:
	f.write(r.json()["message"])

with open(PUBLIC_KEY_FILE, "rb") as f:
    PUBLIC_KEY = serialization.load_pem_public_key(f.read(), backend=default_backend())

def decode_jwt(token: str) -> str:
    """Decode a JWT token using the public key

    Args:
        token (str): The token to decode

    Returns:
        str: The decoded token
    """


    return jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])


def validate_token(token: str) -> bool:
    """Validate a JWT token

    Args:
        token (str): The token to validate

    Returns:
        bool: True if the token is valid, False otherwise
    """

    try:
        payload = decode_jwt(token)

        # Check if the token has expired
        if time.time() > float(payload["expiration"]):
            return False

    # @TODO : Multiple exceptions for later logging purposes
    except jwt.exceptions.InvalidSignatureError:
        return False
    except KeyError:
        return False
    except:
        return False

    return True

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication scheme.",
                )
            if not validate_token(credentials.credentials):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid token or expired token, please login (again?).",
                )
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code.",
            )
