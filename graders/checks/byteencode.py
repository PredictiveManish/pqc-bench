"""Checker: FIPS 203 ByteEncode_12 (256 coefficients -> 384 bytes)."""

Q = 3329


def check(mod):
    fn = getattr(mod, "byteencode12", None)
    if fn is None:
        return False, "missing function: byteencode12"
    try:
        from kyber_py.polynomials.polynomials import PolynomialRing
        ring = PolynomialRing()
    except Exception:
        return False, ("independent reference (kyber-py) unavailable; "
                       "refusing to grade (fail-closed)")

    import random
    rng = random.Random(9090)
    for _ in range(8):
        a = [rng.randrange(Q) for _ in range(256)]
        ref = ring(a).encode(12)
        got = fn(list(a))
        if not isinstance(got, (bytes, bytearray)):
            return False, "byteencode12 must return bytes"
        if bytes(got) != ref:
            return False, "byteencode12 does not match FIPS 203 ByteEncode_12"
    return True, "ok"
