"""Conformance check for the ML-KEM-512 encapsulation task.

Fails unless encaps(ek, m) reproduces the stored KAT vectors exactly, and
rejects submissions that import the reference implementation directly.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

SRC = os.path.join(HERE, "encaps.py")
with open(SRC, encoding="utf-8") as fh:
    source = fh.read()
for banned in ("kyber_py", "_k_pke_encrypt", "_encaps_internal"):
    if banned in source:
        raise SystemExit(f"submission must not use the reference implementation ({banned})")

import encaps  # noqa: E402

vectors = json.load(open(os.path.join(HERE, "kat.json"), encoding="utf-8"))
for i, v in enumerate(vectors):
    ek = bytes.fromhex(v["ek"])
    m = bytes.fromhex(v["m"])
    ss, ct = encaps.encaps(ek, m)
    if bytes(ss).hex() != v["ss"]:
        raise SystemExit(f"vector {i}: shared secret mismatch")
    if bytes(ct).hex() != v["ct"]:
        raise SystemExit(f"vector {i}: ciphertext mismatch")

print(f"KAT OK ({len(vectors)} vectors)")
