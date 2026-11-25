"""Checker: BitRev7 (reverse the 7-bit representation of an index)."""


def _ref(i):
    r = 0
    for b in range(7):
        r |= ((i >> b) & 1) << (6 - b)
    return r


def check(mod):
    fn = getattr(mod, "bitrev7", None) or getattr(mod, "bit_reverse_7", None)
    if fn is None:
        return False, "missing function: bitrev7"
    for i in range(128):
        got = fn(i)
        exp = _ref(i)
        if got != exp:
            return False, f"bitrev7({i})={got} expected {exp}"
    return True, "ok"
