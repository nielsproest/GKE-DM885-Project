import time
from typing import Dict

import jwt
from decouple import config
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

#TODO: Should be received from auth service
PUBLIC_KEY = '''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvpAXDxizoN4MHs0qJrQ9
J/Dc+95mLbT7o/haw2vXuB2LoSp855W/5hpPqyhAkPmKJEzICp6Ke72a2oUVeJb8
lckM3km9dxFBvNsbMEpKEOO1/WhmWw8aDwBI7E0s7KAXHSdqCBncB4L3W37O9c6b
Q2QrGpfrN82yFXez25tdv1ODc7bzfYFdD5LHNVymYl0E+dR/4P2P/+YxUX7omUI9
Bqt6jdw6uERt2tcyT0PFT2DQwf3mtrXCufo68uMfxKP0TN5c1Zan4jwXeiJE4wHP
zFgaWTzgKB6xayJqkgI9nhy5KaONIKe+ZCerrsBKztk9R8uH38GdI2rcwCPYi2Ak
kQIDAQAB
-----END PUBLIC KEY-----
'''

def set_public_key(pub_key):
  PUBLIC_KEY = pub_key

def decodeJWT(token: str) -> dict:
  try:
    decoded_token = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
    if float(decoded_token["expiration"]) < time.time():
      return None

  except jwt.exceptions.InvalidSignatureError:
      return None
  except KeyError:
      return None
  except:
      return None

  return decoded_token
