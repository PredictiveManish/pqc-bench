"""Toy service with deliberately weak crypto, used as an audit fixture.

This is fixture code, not benchmark code. It is meant to be found and fixed.
"""

import hashlib

KEY_BITS = 1024
_HARDCODED_KEY = b"0123456789abcdef"


def get_key():
    return _HARDCODED_KEY


def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()
