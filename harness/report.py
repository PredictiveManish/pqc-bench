"""Markdown report rendering."""

from __future__ import annotations

import datetime


def _tier_table(summary: dict) -> str:
    rows = ["| Tier | n | Mean score | Pass rate |", "|---|---|---|---|"]
    for tier, b in summary["by_tier"].items():
        rows.append(f"| {tier} | {b['n']} | {b['mean_score']:.3f} | {b['pass_rate']:.3f} |")
    return "\n".join(rows)


def _type_table(summary: dict) -> str:
    rows = ["| Type | n | Mean score | Pass rate |", "|---|---|---|---|"]
    for typ, b in summary["by_type"].items():
        rows.append(f"| {typ} | {b['n']} | {b['mean_score']:.3f} | {b['pass_rate']:.3f} |")
    return "\n".join(rows)


def render_markdown(report: dict) -> str:
    s = report["summary"]
    u = report["usage"]
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# PQC-Eval report — {report['model']}",
        "",
        f"_Generated {now} · k={report['k']} · temperature={report['temperature']} · "
        f"duration {report['duration_s']}s_",
        "",
        f"**Overall mean score: {s['overall_mean_score']:.3f}** · "
        f"**pass rate: {s['overall_pass_rate']:.3f}** · {s['n']} tasks",
        "",
        "## By tier",
        "",
        _tier_table(s),
        "",
        "## By type",
        "",
        _type_table(s),
        "",
        "## Failures",
        "",
    ]
    fails = [r for r in report["results"] if r["score"] < 0.999]
    if not fails:
        lines.append("None — every task passed.")
    else:
        lines += ["| Task | Tier | Score | Reason |", "|---|---|---|---|"]
        for r in fails:
            d = r["samples"][0]
            reason = (d.get("error") or d.get("msg") or d.get("predicted")
                      or d.get("violation") or "")
            reason = str(reason).replace("|", "\\|")[:120]
            lines.append(f"| {r['id']} | {r['tier']} | {r['score']:.2f} | {reason} |")

    lines += [
        "",
        "## Usage",
        "",
        f"- model calls: {u['calls']} · cache hits: {u['cache_hits']} · errors: {u['errors']}",
        f"- tokens in: {u['prompt_tokens']} · tokens out: {u['completion_tokens']}",
    ]
    if report.get("est_cost_usd") is not None:
        lines.append(f"- estimated cost: ${report['est_cost_usd']:.4f}")
    lines.append("")
    return "\n".join(lines)
