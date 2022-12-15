import time
from typing import Dict

import jwt
from decouple import config
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

#TODO: Should be received from auth service
PUBLIC_KEY = ""

def set_public_key(pub_key):
  global PUBLIC_KEY
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
