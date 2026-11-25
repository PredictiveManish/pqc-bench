"""Sandboxed execution of model-submitted code against a per-task checker.

A checker module exposes `check(mod) -> bool | (bool, str)`, where `mod` is
the submitted module imported by name. Each checker returns True only if the
submission is correct.

Safety: submitted code is executed in a subprocess with CPU and address-space
rlimits and a wall-clock timeout. This is a research harness for grading your
own model outputs; it is not a hardened sandbox for hostile third-party code.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def extract_code(text: str) -> str:
    """Pull the largest fenced python block, else treat the whole text as code."""
    if not text:
        return ""
    blocks = re.findall(r"```(?:python|py)?\s*\n(.*?)```", text, re.S)
    if blocks:
        return max(blocks, key=len).strip()
    return text.strip()


_INNER = r'''
import json, importlib.util, sys

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

try:
    sub = _load("submission", %(modp)r)
except BaseException as e:
    print(json.dumps({"ok": False, "error": "import failed: " + repr(e)}))
    sys.exit(0)

try:
    chk = _load("checker", %(chk)r)
except BaseException as e:
    print(json.dumps({"ok": False, "error": "checker load failed: " + repr(e)}))
    sys.exit(0)

try:
    res = chk.check(sub)
    ok, msg = res if isinstance(res, tuple) else (bool(res), "")
    print(json.dumps({"ok": bool(ok), "msg": str(msg)}))
except BaseException as e:
    print(json.dumps({"ok": False, "error": "check raised: " + repr(e)}))
'''


def _limits(cpu_seconds: int):
    try:
        import resource

        def _apply():
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
            resource.setrlimit(resource.RLIMIT_AS, (1 << 30, 1 << 30))
        return _apply
    except Exception:
        return None


def run_check(code: str, checker_path: str, timeout: int = 20) -> dict:
    """Execute `code` and run the checker at `checker_path` (relative to repo root)."""
    if not code or not code.strip():
        return {"ok": False, "error": "empty submission"}

    chk = (ROOT / checker_path).resolve()
    if not chk.exists():
        return {"ok": False, "error": f"checker not found: {checker_path}"}

    with tempfile.TemporaryDirectory() as d:
        modp = os.path.join(d, "submission.py")
        with open(modp, "w", encoding="utf-8") as fh:
            fh.write(code)
        script = os.path.join(d, "run_check.py")
        with open(script, "w", encoding="utf-8") as fh:
            fh.write(_INNER % {"modp": modp, "chk": str(chk)})
        try:
            proc = subprocess.run(
                [sys.executable, script],
                capture_output=True, text=True, timeout=timeout + 5,
                preexec_fn=_limits(timeout),
            )
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "timeout"}

    for line in reversed(proc.stdout.strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    return {
        "ok": False,
        "error": "no result from checker",
        "stdout": proc.stdout[-400:],
        "stderr": proc.stderr[-400:],
    }
