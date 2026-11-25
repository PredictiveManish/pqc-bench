"""Markdown report rendering."""

from __future__ import annotations

import datetime


EM = "\u2014"


def _fail_detail(d: dict) -> str:
    if d.get("error"):
        return f"error: {d['error']}"
    if d.get("empty"):
        return (f"EMPTY response (finish_reason={d.get('finish_reason') or '?'})"
                + " " + EM + " raise --max-tokens")
    if d.get("type") == "mcq":
        return (f"predicted {d.get('predicted') or EM} "
                f"(via {d.get('method') or 'none'}); expected {d.get('expected')}")
    if d.get("type") == "rubric":
        if d.get("violation"):
            return f"VIOLATION: {d['violation']}"
        missed = [m.get("id") for m in d.get("matched", []) if not m.get("hit")]
        missed_text = ", ".join(missed) or EM
        return f"coverage {d.get('raw_coverage', 0.0):.0%}; missed: {missed_text}"
    return str(d.get("msg") or d.get("violation") or "")


def _snippet(d: dict, n: int = 160) -> str:
    s = (d.get("output") or "").replace("|", "\\|")
    s = " ".join(s.split())
    return s[:n] + ("\u2026" if len(s) > n else "")


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
        lines += ["| Task | Tier | Score | Detail | Model output (truncated) |",
                  "|---|---|---|---|---|"]
        for r in fails:
            d = r["samples"][0]
            detail = _fail_detail(d).replace("|", "\\|")
            lines.append(f"| {r['id']} | {r['tier']} | {r['score']:.2f} | "
                         f"{detail} | {_snippet(d)} |")

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
