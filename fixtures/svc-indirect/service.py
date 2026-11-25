"""Application service. Crypto is used INDIRECTLY via crypto.provider."""

from crypto import provider


def register_user(username: str, password: str) -> dict:
    return {"user": username, "pw_hash": provider.hash_password(password)}


def issue_token(token: str) -> bytes:
    return provider.sign_token(token)
