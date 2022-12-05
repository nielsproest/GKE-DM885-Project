""" Utilities for hashing and verifying passwords. """

from passlib.hash import pbkdf2_sha256

def hash_password(password: str) -> str:
    """ Hashes a password using pbkdf2_sha256. """
    return pbkdf2_sha256.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:

    """ Verifies a password against a hash using pbkdf2_sha256. """
    return pbkdf2_sha256.verify(plain_password, hashed_password)