"""Aggregation of per-task results into a summary."""

from __future__ import annotations

from collections import defaultdict


def aggregate(results: list[dict]) -> dict:
    by_tier: dict[str, list[float]] = defaultdict(list)
    by_type: dict[str, list[float]] = defaultdict(list)
    for r in results:
        s = float(r["score"])
        by_tier[r["tier"]].append(s)
        by_type[r["type"]].append(s)

    def _block(scores: list[float]) -> dict:
        n = len(scores)
        return {
            "n": n,
            "mean_score": (sum(scores) / n) if n else 0.0,
            "pass_rate": (sum(1 for x in scores if x >= 0.999) / n) if n else 0.0,
        }

    all_scores = [float(r["score"]) for r in results]
    overall = (sum(all_scores) / len(all_scores)) if all_scores else 0.0
    return {
        "n": len(results),
        "overall_mean_score": overall,
        "overall_pass_rate": (sum(1 for x in all_scores if x >= 0.999)
                              / len(all_scores)) if all_scores else 0.0,
        "by_tier": {k: _block(v) for k, v in sorted(by_tier.items())},
        "by_type": {k: _block(v) for k, v in sorted(by_type.items())},
    }
