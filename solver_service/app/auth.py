import jwt
import time

PUBLIC_KEY = '''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvpAXDxizoN4MHs0qJrQ9J/Dc+95mLbT7o/haw2vXuB2LoSp855W/5hpPqyhAkPmKJEzICp6Ke72a2oUVeJb8lckM3km9dxFBvNsbMEpKEOO1/WhmWw8aDwBI7E0s7KAXHSdqCBncB4L3W37O9c6bQ2QrGpfrN82yFXez25tdv1ODc7bzfYFdD5LHNVymYl0E+dR/4P2P/+YxUX7omUI9Bqt6jdw6uERt2tcyT0PFT2DQwf3mtrXCufo68uMfxKP0TN5c1Zan4jwXeiJE4wHPzFgaWTzgKB6xayJqkgI9nhy5KaONIKe+ZCerrsBKztk9R8uH38GdI2rcwCPYi2AkkQIDAQAB
-----END PUBLIC KEY-----'''

def setPublicKey(newKey):
    global PUBLIC_KEY
    PUBLIC_KEY = newKey

def validate_token(token: str) -> bool:
    try:
        print(PUBLIC_KEY)
        print(token)
        payload = decode_jwt(token)
        print(f'payload: {payload}')
        if time.time() > float(payload["expiration"]):
            return False

    except jwt.exceptions.InvalidSignatureError:
        print("except1")
        return False
    except KeyError:
        print("except2")
        return False
    except:
        print("except3")
        return False

    return True

def decode_jwt(token: str) -> str:
    return jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])