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


_CHOICE_RE = re.compile(r"^\s*\(?([A-E])\)\s*(.+?)\s*$", re.M)


def _choices_from_prompt(prompt: str) -> dict[str, str]:
    """Recover the A)..E) options that are written inline in the prompt."""
    out: dict[str, str] = {}
    for m in _CHOICE_RE.finditer(prompt or ""):
        out[m.group(1)] = m.group(2)
    return out


_UNI = str.maketrans({"\u2010": "-", "\u2011": "-", "\u2012": "-",
                      "\u2013": "-", "\u2014": "-", "\u2212": "-",
                      "\u00a0": " ", "\u202f": " ", "\u2009": " "})


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.translate(_UNI).lower()).strip()


def _mcq(task: dict, output: str) -> dict:
    """Score an MCQ, tolerating answers given as text rather than a bare letter.

    Order of inference: explicit marker ("answer is B"), leading letter ("B)"),
    choice-text match ("ML-KEM-1024"), then any standalone letter.
    """
    expected = str(task["answer"]).strip().upper()
    text = output or ""
    up = text.upper()
    choices = _choices_from_prompt(task.get("prompt", ""))
    predicted = None
    method = None

    # Explicit answer statements: take the LAST one, so "I considered option A ...
    # but the correct answer is C" resolves to C, not A.
    ans = re.findall(
        r"\b(?:CORRECT\s+ANSWER|FINAL\s+ANSWER|ANSWER)\s*(?:IS|:)?\s*\(?\s*([A-E])\b", up)
    if ans:
        predicted, method = ans[-1], "answer-marker"

    if predicted is None:
        m = re.match(r"\s*\(?([A-E])\)?[\.\):\-]", text)
        if m:
            predicted, method = m.group(1).upper(), "leading"

    if predicted is None and choices:
        body = _norm(text)
        best = None
        for letter, ctext in choices.items():
            c = _norm(ctext)
            if len(c) >= 2 and c in body and (best is None or len(c) > best[1]):
                best = (letter, len(c))
        if best:
            predicted, method = best[0], "choice-text"

    if predicted is None:
        letters = set(re.findall(r"\b([A-E])\b", up))
        if len(letters) == 1:
            predicted, method = letters.pop(), "single-letter"
        elif len(letters) > 1:
            # Several candidate letters and no explicit answer: refuse to guess.
            method = "ambiguous"

    ok = predicted == expected
    return {
        "type": "mcq",
        "score": 1.0 if ok else 0.0,
        "correct": ok,
        "predicted": predicted,
        "expected": expected,
        "method": method,
        "ambiguous": method == "ambiguous",
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


_NEG_TOKENS = ("not ", "no ", "never ", "without ", "n't ", "cannot ",
               "fails to ", "does not ", "is not ", "are not ", "neither ")


def _negated(text: str, idx: int) -> bool:
    """True if a negation occurs in the same clause immediately before `idx`.

    The window is cut at the last clause boundary so that "Signatures are not:
    PQ certificates are rare" does not count as negating "certificate".
    """
    window = text[max(0, idx - 45):idx]
    for sep in (". ", "; ", ": ", "\n"):
        j = window.rfind(sep)
        if j >= 0:
            window = window[j + len(sep):]
    return any(tok in window for tok in _NEG_TOKENS)


def _kw_hit(text: str, kw: str) -> bool:
    """True if `kw` occurs at least once WITHOUT being negated.

    "LMS is not stateful" must not satisfy a `stateful` criterion.
    """
    start = 0
    while True:
        i = text.find(kw, start)
        if i < 0:
            return False
        if not _negated(text, i):
            return True
        start = i + len(kw)


def _rubric(task: dict, output: str) -> dict:
    # Normalise unicode dashes/NBSP: models emit "ML\u2011DSA" which would
    # otherwise fail to match "ml-dsa".
    text = (output or "").translate(_UNI).lower()
    criteria = task.get("rubric", [])
    matched = []
    wsum = 0.0
    wgot = 0.0
    critical_missed = []
    for c in criteria:
        w = float(c.get("weight", 1))
        wsum += w
        hit = any(_kw_hit(text, k.lower()) for k in c.get("match_any", []))
        matched.append({"id": c.get("id"), "hit": hit,
                        "critical": bool(c.get("critical"))})
        if hit:
            wgot += w
        elif c.get("critical"):
            critical_missed.append(c.get("id"))

    violation = None
    for group in task.get("must_not", []):
        if any(_kw_hit(text, k.lower()) for k in group):
            violation = group[0]
            break

    raw = (wgot / wsum) if wsum else 0.0
    final = 0.0 if violation else raw
    # Missing an essential criterion caps the score: breadth cannot compensate
    # for omitting the one thing the question is actually about.
    if critical_missed and not violation:
        final = min(final, 0.4)
    return {
        "type": "rubric",
        "score": final,
        "raw_coverage": raw,
        "matched": matched,
        "violation": violation,
        "critical_missed": critical_missed,
    }
