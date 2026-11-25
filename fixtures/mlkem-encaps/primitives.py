"""Primitives available to the implementation under test.

Provided so the task is about FIPS 203 encapsulation logic, not about
re-deriving SHA-3 or the K-PKE layer.
"""

import hashlib

from kyber_py.ml_kem import ML_KEM_512 as _K


def H(x: bytes) -> bytes:
    return hashlib.sha3_256(x).digest()


def G(x: bytes) -> bytes:
    return hashlib.sha3_512(x).digest()


def KDF(x: bytes, n: int = 32) -> bytes:
    return hashlib.shake_256(x).digest(n)


def k_pke_encrypt(ek: bytes, m: bytes, r: bytes) -> bytes:
    return _K._k_pke_encrypt(ek, m, r)
