"""Checker: ML-KEM implicit rejection  K_bar = SHAKE256(z || c, 32)."""

import hashlib


def check(mod):
    fn = getattr(mod, "implicit_reject", None)
    if fn is None:
        return False, "missing function: implicit_reject"

    import random
    rng = random.Random(77)
    for _ in range(8):
        z = bytes(rng.randrange(256) for _ in range(32))
        c = bytes(rng.randrange(256) for _ in range(rng.choice([768, 1088, 1568])))
        ref = hashlib.shake_256(z + c).digest(32)
        got = fn(z, c)
        if not isinstance(got, (bytes, bytearray)):
            return False, "implicit_reject must return bytes"
        if bytes(got) != ref:
            return False, "implicit_reject must equal SHAKE256(z || c, 32)"
    return True, "ok"
