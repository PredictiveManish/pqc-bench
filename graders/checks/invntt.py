"""Checker: NTT then inverse NTT is the identity mod q (q = 3329)."""

Q = 3329


def check(mod):
    for name in ("ntt", "invntt"):
        if not hasattr(mod, name):
            return False, f"missing function: {name}"

    import random
    rng = random.Random(9032)
    for _ in range(16):
        a = [rng.randrange(Q) for _ in range(256)]
        b = mod.invntt(mod.ntt(list(a)))
        b = [int(x) % Q for x in b]
        if b != [x % Q for x in a]:
            return False, "round-trip ntt -> invntt is not the identity"
    return True, "ok"
