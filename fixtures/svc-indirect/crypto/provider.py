"""Crypto provider used by the service. Usage here is direct."""

import hashlib


def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()


class RSA2048:
    def sign(self, data: bytes) -> bytes:
        return b"sig:" + data


_SIGNER = RSA2048()


def sign_token(token: str) -> bytes:
    return _SIGNER.sign(token.encode())
