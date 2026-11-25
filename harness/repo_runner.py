"""Repository-level task execution.

Modes
-----
discovery : the model returns findings; scored with precision / recall / F1 and
            an evidence-accuracy term when structured findings are expected.
patch     : the model returns a full replacement for `target`; the fixture's
            own test suite is run and must pass.
kat       : the model returns a full replacement for `target`; a conformance
            script is run (e.g. comparing against stored KAT vectors).
artifact  : the model returns JSON; it is written to `target` and a validator
            script is run (e.g. CycloneDX CBOM schema + asset matching).
"""

import json
import os
from pathlib import Path

from graders.code_runner import extract_code
from harness import sandbox

ROOT = Path(__file__).resolve().parents[1]


def _extract_json(text: str):
    """Return the first JSON object/array embedded in text, or None."""
    if not text:
        return None
    dec = json.JSONDecoder()
    for i, ch in enumerate(text):
        if ch in "{[":
            try:
                obj, _ = dec.raw_decode(text[i:])
                return obj
            except json.JSONDecodeError:
                continue
    return None


def grade(task: dict, output: str) -> dict:
    mode = task["repo"]["mode"]
    if mode == "discovery":
        return _discovery(task, output)
    if mode in ("patch", "kat", "artifact"):
        return _write_and_run(task, output)
    return {"type": "repo", "score": 0.0, "error": f"unknown mode: {mode}"}


def _discovery(task: dict, output: str) -> dict:
    repo = task["repo"]
    expected = repo.get("expected_findings")

    if expected:
        doc = _extract_json(output)
        preds = doc.get("findings", []) if isinstance(doc, dict) else (doc or [])
        if not isinstance(preds, list):
            preds = []

        def key(f):
            return (str(f.get("file", "")).lower().strip(),
                    str(f.get("symbol", "")).lower().strip())

        exp = {key(e): e for e in expected}
        got = {}
        for p in preds:
            if isinstance(p, dict):
                got[key(p)] = p

        tp_keys = set(exp) & set(got)
        tp = len(tp_keys)
        precision = tp / len(got) if got else 0.0
        recall = tp / len(exp) if exp else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
        ev_ok = sum(1 for k in tp_keys
                    if str(got[k].get("algorithm", "")).lower().strip()
                    == str(exp[k].get("algorithm", "")).lower().strip())
        evidence = (ev_ok / tp) if tp else 0.0
        # Evidence is half the credit: right file but wrong algorithm is partial.
        score = f1 * (0.5 + 0.5 * evidence)
        return {"type": "repo", "score": score, "precision": precision,
                "recall": recall, "f1": f1, "evidence_accuracy": evidence,
                "tp": tp, "predicted": len(got), "expected": len(exp)}

    # Legacy token-recall mode (no structured ground truth).
    toks = [e.lower() for e in repo.get("expected", [])]
    text = (output or "").lower()
    found = [e for e in toks if e in text]
    missed = [e for e in toks if e not in found]
    score = len(found) / len(toks) if toks else 0.0
    return {"type": "repo", "score": score, "found": found, "missed": missed}


def _write_and_run(task: dict, output: str) -> dict:
    mode = task["repo"]["mode"]
    if mode == "artifact":
        doc = _extract_json(output)
        if doc is None:
            return {"type": "repo", "score": 0.0, "error": "no JSON found in output"}
        content = json.dumps(doc, indent=2)
    else:
        content = extract_code(output)

    if not content.strip():
        return {"type": "repo", "score": 0.0, "error": "empty submission"}

    fixture = ROOT / task["repo"]["fixture"]
    target = task["repo"]["target"]
    cmd = task["repo"]["run"]
    timeout = int(task["repo"].get("timeout", 90))

    with sandbox.workspace(str(fixture)) as ws:
        path = os.path.join(ws, target)
        os.makedirs(os.path.dirname(path) or ws, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        res = sandbox.run(cmd, cwd=ws, timeout=timeout)

    return {
        "type": "repo",
        "score": 1.0 if res["ok"] else 0.0,
        "ok": res["ok"],
        "returncode": res.get("returncode"),
        "stdout": res.get("stdout", "")[-600:],
        "stderr": res.get("stderr", "")[-600:],
        "network_isolated": res.get("network_isolated"),
    }
