"""Checker: ML-KEM zeta table zetas[i] = 17^BitRev7(i) mod 3329, i = 0..127."""

Q = 3329


def _br7(i):
    return int(format(i, "07b")[::-1], 2)


def _ref():
    return [pow(17, _br7(i), Q) for i in range(128)]


def check(mod):
    z = getattr(mod, "zetas", None)
    if z is None:
        z = getattr(mod, "ZETAS", None)
    if z is None:
        return False, "missing zetas()/ZETAS"
    if callable(z):
        z = z()
    z = list(z)
    exp = _ref()
    if len(z) != 128:
        return False, f"length {len(z)} != 128"
    for i, (a, b) in enumerate(zip(z, exp)):
        if a != b:
            return False, f"zetas[{i}]={a} expected {b}"
    return True, "ok"
