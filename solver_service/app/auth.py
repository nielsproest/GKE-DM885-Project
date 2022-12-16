import jwt
import time

PUBLIC_KEY = ""

def setPublicKey(newKey):
    global PUBLIC_KEY
    PUBLIC_KEY = newKey

def validate_token(token: str) -> bool:
    try:
        payload = decode_jwt(token)

        if time.time() > float(payload["expiration"]):
            return False

    except jwt.exceptions.InvalidSignatureError:
        return False
    except KeyError:
        return False
    except:
        return False

    return True

def decode_jwt(token: str) -> str:
    return jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])