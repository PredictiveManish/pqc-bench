"""Re-score a saved results JSON with the current tasks and scorers.

No model calls, no credits: it reads the stored `output` of every sample and
re-runs the scorer. Use it after changing a rubric, a checker or a scorer.

    python scripts/rescore.py --in results/sarvam-105b.json --md results/rescored.md
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness.metrics import aggregate
from harness.report import render_markdown
from harness.runner import load_tasks
from harness.scorers import score


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="results JSON to re-score")
    ap.add_argument("--md", default=None, help="write a Markdown report here")
    ap.add_argument("--out", default=None, help="write the re-scored JSON here")
    args = ap.parse_args()

    old = json.load(open(args.inp, encoding="utf-8"))
    tasks = {t["id"]: t for t in load_tasks()}

    results = []
    missing = []
    for r in old.get("results", []):
        t = tasks.get(r["id"])
        if not t:
            missing.append(r["id"])
            continue
        samples = []
        for sm in r.get("samples", []):
            out = sm.get("output") or ""
            s = score(t, out)
            s["status"] = sm.get("status")
            s["output"] = out
            if not out.strip():
                s["empty"] = True
                s["finish_reason"] = sm.get("finish_reason")
            samples.append(s)
        best = max((x["score"] for x in samples), default=0.0)
        results.append({"id": r["id"], "tier": r["tier"], "type": r["type"],
                        "score": best, "samples": samples})

    new = {
        "model": old.get("model", "unknown"),
        "k": old.get("k", 1),
        "temperature": old.get("temperature", 0.0),
        "duration_s": 0.0,
        "usage": old.get("usage", {}),
        "est_cost_usd": old.get("est_cost_usd"),
        "summary": aggregate(results),
        "results": results,
    }

    print(f"re-scored {len(results)} tasks from {args.inp}")
    if missing:
        print(f"  skipped (unknown task ids): {missing}")
    s = new["summary"]
    print(f"  overall mean: {s['overall_mean_score']:.3f}  pass: {s['overall_pass_rate']:.3f}")
    for tier, b in s["by_tier"].items():
        print(f"    {tier:<12} n={b['n']} mean={b['mean_score']:.3f}")
    print("  per task:")
    for r in results:
        d = r["samples"][0]
        extra = ""
        if d.get("critical_missed"):
            extra = f" critical_missed={d['critical_missed']}"
        if d.get("violation"):
            extra = f" VIOLATION={d['violation']}"
        print(f"    {r['id']:<26} {r['score']:.2f}{extra}")

    if args.out:
        open(args.out, "w", encoding="utf-8").write(json.dumps(new, indent=2, default=str))
        print(f"  wrote {args.out}")
    if args.md:
        open(args.md, "w", encoding="utf-8").write(render_markdown(new))
        print(f"  wrote {args.md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
