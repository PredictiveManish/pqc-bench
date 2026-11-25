"""Cross-validate PQC-Eval ground truth against reference implementations.

This is not a mock. It checks that the reference formulas our graders use agree
with kyber-py / dilithium-py (independent, widely used implementations of the
FIPS 203 / 204 standards), and that those implementations pass round-trip
consistency checks at the sizes the standards specify.

These are NOT official NIST known-answer tests (KATs). Round-trip consistency
shows two operations agree; it does not establish FIPS conformance. ACVP/KAT
vectors are the missing piece (see ROADMAP.md).

Run:  python scripts/validate_ground_truth.py
Exit code is non-zero if any cross-check fails.
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import graders.checks.compress as C
import graders.checks.zetas as Z

failures = []


def check(name, cond, detail=""):
    status = "ok" if cond else "FAIL"
    print(f"  [{status}] {name}" + (f"  {detail}" if detail and not cond else ""))
    if not cond:
        failures.append(name)


def validate_kyber():
    print("\n[kyber-py] reference cross-checks")
    from kyber_py.polynomials.polynomials import PolynomialRing

    ring = PolynomialRing()
    check("ring params n=256,q=3329", ring.n == 256 and ring.q == 3329,
          f"n={ring.n},q={ring.q}")

    # 1. zeta table: our formula vs the reference implementation's table
    ours = Z._ref()
    check("zeta table matches reference", list(ring.ntt_zetas) == ours,
          f"len ours={len(ours)} ref={len(ring.ntt_zetas)}")

    # 2. compress / decompress vs reference element routines
    rng = random.Random(203)
    ok_c = ok_d = True
    bad = None
    for d in (1, 4, 10, 11):
        for x in [0, 1, 1664, 3328] + [rng.randrange(3329) for _ in range(40)]:
            p = ring([x] + [0] * 255)
            if p._compress_ele(x, d) != C._ref_compress(x, d):
                ok_c = False
                bad = f"compress d={d} x={x}"
                break
        for y in [0, 1, (1 << d) - 1] + [rng.randrange(1 << d) for _ in range(40)]:
            p = ring([0] * 256)
            if p._decompress_ele(y, d) != C._ref_decompress(y, d):
                ok_d = False
                bad = f"decompress d={d} y={y}"
                break
    check("compress_d matches reference", ok_c, bad or "")
    check("decompress_d matches reference", ok_d, bad or "")

    # 3. scheme sizes + round-trip consistency (not official KATs)
    from kyber_py.ml_kem import ML_KEM_512, ML_KEM_768, ML_KEM_1024
    for name, mod, ek_len, ct_len in [
        ("ML-KEM-512", ML_KEM_512, 800, 768),
        ("ML-KEM-768", ML_KEM_768, 1184, 1088),
        ("ML-KEM-1024", ML_KEM_1024, 1568, 1568),
    ]:
        ek, dk = mod.keygen()
        k, c = mod.encaps(ek)
        k2 = mod.decaps(dk, c)
        check(f"{name} round-trip + sizes",
              k == k2 and len(ek) == ek_len and len(c) == ct_len,
              f"ek={len(ek)} ct={len(c)} rt={k == k2}")


def validate_dilithium():
    print("\n[dilithium-py] reference cross-checks")
    from dilithium_py.ml_dsa import ML_DSA_44, ML_DSA_65, ML_DSA_87
    for name, mod, pk_len, sig_len in [
        ("ML-DSA-44", ML_DSA_44, 1312, 2420),
        ("ML-DSA-65", ML_DSA_65, 1952, 3309),
        ("ML-DSA-87", ML_DSA_87, 2592, 4627),
    ]:
        pk, sk = mod.keygen()
        sig = mod.sign(sk, b"pqc-eval")
        good = mod.verify(pk, b"pqc-eval", sig)
        tampered = bytearray(sig); tampered[0] ^= 1
        rejects = not mod.verify(pk, b"pqc-eval", bytes(tampered))
        check(f"{name} sign/verify + sizes",
              good and rejects and len(pk) == pk_len and len(sig) == sig_len,
              f"pk={len(pk)} sig={len(sig)} verify={good} rejects_tamper={rejects}")


def main() -> int:
    print("=" * 60)
    print("PQC-Eval ground-truth validation (against reference impls)")
    print("=" * 60)
    try:
        validate_kyber()
        validate_dilithium()
    except ImportError as e:
        print(f"\nReference libs not installed ({e}). "
              f"Run: pip install kyber-py dilithium-py")
        return 2

    print("\n" + "=" * 60)
    if failures:
        print(f"VALIDATION FAILED ({len(failures)}): {failures}")
        return 1
    print("ALL GROUND-TRUTH CHECKS PASSED against reference implementations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
