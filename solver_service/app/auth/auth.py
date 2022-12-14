import jwt
import time

decoded: dict
publicKey = ""

def validate_token(token: str) -> bool:
    try:
        decoded = jwt.decode(token, publicKey, algorithms=["RS256"])
        if float(decoded["expiration"]) < time.time():
            return None
    except jwt.exceptions.InvalidSignatureError:
        return False
    except KeyError:
        return False
    except:
        return False

    return True

def decode_jwt(token: str) -> str:
    
    if not validate_token(token):
        return None

    return decoded