"""Checker: FIPS 203 ByteDecode_12 (384 bytes -> 256 coefficients)."""

Q = 3329


def check(mod):
    fn = getattr(mod, "bytedecode12", None)
    if fn is None:
        return False, "missing function: bytedecode12"
    try:
        from kyber_py.polynomials.polynomials import PolynomialRing
        ring = PolynomialRing()
    except Exception:
        return False, ("independent reference (kyber-py) unavailable; "
                       "refusing to grade (fail-closed)")

    import random
    rng = random.Random(1212)
    for _ in range(8):
        a = [rng.randrange(Q) for _ in range(256)]
        enc = ring(a).encode(12)          # valid encoding of coefficients in [0,q)
        got = [int(x) % Q for x in fn(enc)]
        if len(got) != 256:
            return False, f"expected 256 coefficients, got {len(got)}"
        if got != a:
            return False, "bytedecode12 does not invert ByteEncode_12"
    return True, "ok"
