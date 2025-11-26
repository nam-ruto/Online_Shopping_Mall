import hashlib
import os
from typing import Tuple


def generate_salt(length: int = 16) -> bytes:
    if length <= 0:
        raise ValueError("salt length must be positive")
    return os.urandom(length)


def hash_password(password: str, salt: bytes, iterations: int = 100_000) -> str:
    if not password:
        raise ValueError("password must be non-empty")
    if not isinstance(salt, (bytes, bytearray)):
        raise ValueError("salt must be bytes")
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen=32)
    return dk.hex()


def make_password_hash(password: str, salt_length: int = 16) -> Tuple[str, bytes]:
    salt = generate_salt(salt_length)
    pwd_hash = hash_password(password, salt)
    return pwd_hash, salt


def verify_password(password: str, salt: bytes, expected_hash_hex: str) -> bool:
    actual = hash_password(password, salt)
    # constant-time compare
    if len(actual) != len(expected_hash_hex):
        return False
    result = 0
    for x, y in zip(actual.encode("utf-8"), expected_hash_hex.encode("utf-8")):
        result |= x ^ y
    return result == 0


