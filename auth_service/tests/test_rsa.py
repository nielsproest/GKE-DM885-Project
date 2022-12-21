""" Ensure that the token is signed with the private key and that the public key is the only one that can validate it """

import os
import jwt
import base64
import pytest
from typing import *
from decouple import config

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


# Get key frm environtment variable
PRIVATE_KEY_FILE = os.environ.get("AUTH_PRIVATE_KEY")
PUBLIC_KEY_FILE = config("PUBLIC_KEY_FILE")
NOT_MY_KEY_FILE = config("NOT_MY_KEY_FILE")


# Base64 decode the key
PRIVATE_KEY_FILE = base64.b64decode(PRIVATE_KEY_FILE)

PRIVATE_KEY = serialization.load_pem_private_key(
    PRIVATE_KEY_FILE, password=None, backend=default_backend()
)

with open(PUBLIC_KEY_FILE, "rb") as f:
    PUBLIC_KEY = serialization.load_pem_public_key(f.read(), backend=default_backend())

with open(NOT_MY_KEY_FILE, "rb") as f:
    NOT_MY_PUBLIC_KEY = serialization.load_pem_public_key(
        f.read(), backend=default_backend()
    )


def test_internal_decode():
    """This will work because the token was signed with the private key and the public key is the only one that can validate it"""
    jwt_token = jwt.encode({"foo": "bar"}, key=PRIVATE_KEY, algorithm="RS256")

    jwt.decode(jwt_token, PRIVATE_KEY.public_key(), algorithms=["RS256"])


def test_external_decode():
    """This will work because the token was signed with the private key and the public key is the only one that can validate it"""
    jwt_token = jwt.encode({"foo": "bar"}, key=PRIVATE_KEY, algorithm="RS256")

    jwt.decode(jwt_token, PUBLIC_KEY, algorithms=["RS256"])


def test_invalid_decode():
    """This will fail because the token was signed with a different key"""

    jwt_token = jwt.encode({"foo": "bar"}, key=PRIVATE_KEY, algorithm="RS256")

    with pytest.raises(jwt.exceptions.InvalidSignatureError):
        jwt.decode(jwt_token, NOT_MY_PUBLIC_KEY, algorithms=["RS256"])
