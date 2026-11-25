"""Integrity gate for PQC-Eval.

Proves the scoring pipeline is sound before you trust any model result:
  1. gold oracle  -> overall 1.000   (correct answers earn full marks)
  2. null model   -> overall 0.000   (non-answers earn nothing)
  3. buggy code   -> 0.000 each      (debugging tasks discriminate)

Run:  python scripts/validate.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness.models import GoldModel, NullModel
from harness.runner import load_tasks, run
from harness.scorers import score


def main() -> int:
    tasks = load_tasks()
    print(f"Loaded {len(tasks)} tasks across {len({t['tier'] for t in tasks})} tiers.")

    gold = {t["prompt"]: t["gold"] for t in tasks}

    print("\n=== 1. GOLD ORACLE (expect 1.000) ===")
    r_gold = run(GoldModel(gold), tasks, out_path="results/gold.json", verbose=True)

    print("\n=== 2. NULL MODEL (expect 0.000) ===")
    r_null = run(NullModel(), tasks, out_path="results/null.json", verbose=False)
    print(f"  overall mean = {r_null['summary']['overall_mean_score']:.3f}")

    print("\n=== 3. DISCRIMINATION (buggy submissions must fail) ===")
    disc_ok = True
    n = 0
    for t in tasks:
        if t.get("buggy"):
            n += 1
            s = score(t, t["buggy"])
            ok = s["score"] == 0.0
            print(f"  {'ok' if ok else 'LEAK'}  {t['id']:<24} score={s['score']:.2f}")
            disc_ok = disc_ok and ok
    if n == 0:
        disc_ok = False

    g = r_gold["summary"]["overall_mean_score"]
    nu = r_null["summary"]["overall_mean_score"]
    ok = (g == 1.0) and (nu == 0.0) and disc_ok
    print("\n" + "=" * 48)
    print(f"gold={g:.3f} (want 1.0)  null={nu:.3f} (want 0.0)  "
          f"discrimination={'ok' if disc_ok else 'FAIL'}")
    print("INTEGRITY GATE PASSED" if ok else "INTEGRITY GATE FAILED")
    print("=" * 48)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
