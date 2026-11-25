"""Checker: FIPS 203 Compress_d / Decompress_d.

Compress_d(x)   = round((2^d / q) * x) mod 2^d
Decompress_d(y) = round((q / 2^d) * y)
with q = 3329 and 0 <= x < q.
"""

Q = 3329


def _ref_compress(x, d):
    return (((x << d) + Q // 2) // Q) & ((1 << d) - 1)


def _ref_decompress(y, d):
    return (y * Q + (1 << (d - 1))) >> d


def check(mod):
    for name in ("compress_d", "decompress_d"):
        if not hasattr(mod, name):
            return False, f"missing function: {name}"

    import random
    rng = random.Random(20240)

    for d in (1, 4, 10, 11):
        xs = [0, 1, Q - 1, Q // 2, 1234, 3000] + [rng.randrange(Q) for _ in range(64)]
        for x in xs:
            got = mod.compress_d(x, d)
            exp = _ref_compress(x, d)
            if got != exp:
                return False, f"compress_d({x},{d})={got} expected {exp}"

        ys = ([0, 1, (1 << d) - 1] + [rng.randrange(1 << d) for _ in range(64)])
        for y in ys:
            got = mod.decompress_d(y, d)
            exp = _ref_decompress(y, d)
            if got != exp:
                return False, f"decompress_d({y},{d})={got} expected {exp}"

    return True, "ok"
