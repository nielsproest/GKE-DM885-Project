import jwt
import time

publicKey = ""

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
    return jwt.decode(token, publicKey, algorithms=["RS256"])