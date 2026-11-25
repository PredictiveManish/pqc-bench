"""Checker: FIPS 203 BarrettReduce with q = 3329."""

Q = 3329


def _ref(a):
    v = ((1 << 26) + Q // 2) // Q
    t = (v * a + (1 << 25)) >> 26
    t *= Q
    return a - t


def check(mod):
    fn = getattr(mod, "barrett_reduce", None)
    if fn is None:
        return False, "missing function: barrett_reduce"

    import random
    rng = random.Random(3329)
    samples = list(range(-4000, 4000, 37)) + [rng.randrange(-Q * Q, Q * Q) for _ in range(256)]
    for a in samples:
        got = fn(a)
        exp = _ref(a)
        if got != exp:
            return False, f"barrett_reduce({a})={got} expected {exp}"
    return True, "ok"
