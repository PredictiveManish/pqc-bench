"""Checker: FIPS 203 SamplePolyCBD with eta = 2 (coefficients mod q)."""

Q = 3329


def check(mod):
    fn = getattr(mod, "cbd2", None)
    if fn is None:
        return False, "missing function: cbd2"
    try:
        from kyber_py.polynomials.polynomials import PolynomialRing
        ring = PolynomialRing()
    except Exception:
        return False, ("independent reference (kyber-py) unavailable; "
                       "refusing to grade (fail-closed)")

    import random
    rng = random.Random(4242)
    for _ in range(8):
        b = bytes(rng.randrange(256) for _ in range(128))
        ref = [int(c) % Q for c in ring.cbd(b, 2).coeffs]
        got = [int(x) % Q for x in fn(b)]
        if len(got) != 256:
            return False, f"expected 256 coefficients, got {len(got)}"
        if got != ref:
            return False, "cbd2 does not match the FIPS 203 CBD_2 output"
    return True, "ok"
