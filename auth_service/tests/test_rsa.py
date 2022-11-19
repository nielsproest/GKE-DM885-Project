""" Ensure that the token is signed with the private key and that the public key is the only one that can validate it """

import os
import jwt
from typing import *
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import pytest
from decouple import config

PRIVATE_KEY_FILE = config("PRIVATE_KEY_FILE")
PUBLIC_KEY_FILE = config("PUBLIC_KEY_FILE")
NOT_MY_KEY_FILE = config("NOT_MY_KEY_FILE")

with open(PRIVATE_KEY_FILE, "rb") as f:
    PRIVATE_KEY = serialization.load_pem_private_key(
        f.read(), password=None, backend=default_backend()
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
