"""Checker: ML-KEM-768 encapsulation-key length validation."""


def check(mod):
    fn = getattr(mod, "validate_ek", None)
    if fn is None:
        return False, "missing function: validate_ek"
    cases = {1184: True, 800: False, 1568: False, 0: False, 1183: False, 1185: False}
    for n, expect in cases.items():
        got = fn(bytes(n))
        if bool(got) != expect:
            return False, f"validate_ek for length {n} should be {expect}"
    return True, "ok"
