"""Checker: NTT / inverse NTT against FIPS 203.

Fails CLOSED: if the independent reference (kyber-py) is unavailable, the
submission cannot be graded and scores nothing. A weak round-trip-only check is
never silently accepted, because any two mutually inverse transforms pass it.

When kyber-py is present:
  * submitted `ntt` must match its transform coefficient-for-coefficient;
  * submitted `invntt` must invert the reference transform;
  * round-trip invntt(ntt(a)) == a is also required.
"""

Q = 3329


def check(mod):
    for name in ("ntt", "invntt"):
        if not hasattr(mod, name):
            return False, f"missing function: {name}"

    try:
        from kyber_py.polynomials.polynomials import PolynomialRing
        ring = PolynomialRing()
    except Exception:
        return False, ("independent reference (kyber-py) unavailable; "
                       "refusing to grade (fail-closed)")

    import random
    rng = random.Random(9032)
    for _ in range(16):
        a = [rng.randrange(Q) for _ in range(256)]
        out = [int(x) % Q for x in mod.ntt(list(a))]

        p = ring(list(a))
        p.to_ntt()
        ref = [int(c) % Q for c in p.coeffs]
        if out != ref:
            return False, "ntt output does not match the FIPS 203 transform"

        inv = [int(x) % Q for x in mod.invntt(list(ref))]
        if inv != [x % Q for x in a]:
            return False, "invntt does not invert the reference NTT"

        back = [int(x) % Q for x in mod.invntt(list(out))]
        if back != [x % Q for x in a]:
            return False, "round-trip ntt -> invntt is not the identity"

    return True, "ok"
