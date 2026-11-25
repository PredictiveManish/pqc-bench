"""Per-task-type scorers.

Every scorer returns a dict with at least {"type", "score"} where score is in
[0.0, 1.0]. Higher is better. Types:
  * mcq    - single-letter multiple choice
  * rubric - weighted criteria + must_not penalties (v0 keyword coverage)
  * code   - executed against a checker; binary pass/fail
"""

from __future__ import annotations

import re

from graders.code_runner import extract_code, run_check


def score(task: dict, output: str) -> dict:
    t = task.get("type")
    if t == "mcq":
        return _mcq(task, output)
    if t == "rubric":
        return _rubric(task, output)
    if t == "code":
        return _code(task, output)
    return {"type": t, "score": 0.0, "error": f"unknown task type: {t}"}


def _mcq(task: dict, output: str) -> dict:
    expected = str(task["answer"]).strip().upper()
    letters = re.findall(r"\b([A-E])\b", (output or "").upper())
    predicted = letters[0] if letters else None
    ok = predicted == expected
    return {
        "type": "mcq",
        "score": 1.0 if ok else 0.0,
        "correct": ok,
        "predicted": predicted,
        "expected": expected,
    }


def _code(task: dict, output: str) -> dict:
    code = extract_code(output)
    res = run_check(code, task["checker"])
    out = {"type": "code", "score": 1.0 if res.get("ok") else 0.0,
           "ok": bool(res.get("ok"))}
    for k, v in res.items():
        if k != "ok":
            out[k] = v
    return out


def _rubric(task: dict, output: str) -> dict:
    text = (output or "").lower()
    criteria = task.get("rubric", [])
    matched = []
    wsum = 0.0
    wgot = 0.0
    for c in criteria:
        w = float(c.get("weight", 1))
        wsum += w
        hit = any(k.lower() in text for k in c.get("match_any", []))
        matched.append({"id": c.get("id"), "hit": hit})
        if hit:
            wgot += w

    violation = None
    for group in task.get("must_not", []):
        if any(k.lower() in text for k in group):
            violation = group[0]
            break

    raw = (wgot / wsum) if wsum else 0.0
    final = 0.0 if violation else raw
    return {
        "type": "rubric",
        "score": final,
        "raw_coverage": raw,
        "matched": matched,
        "violation": violation,
    }
