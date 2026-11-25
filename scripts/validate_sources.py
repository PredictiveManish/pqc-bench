"""Provenance gate: every task must be grounded in at least one real source.

Fails if:
  - a task has no entry in provenance/sources.yaml;
  - an entry has no source URLs;
  - a source is not an http(s) URL;
  - the registry lists an id that is not a task (stale entry).

Run: python scripts/validate_sources.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml

from harness.runner import load_tasks

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> int:
    tasks = load_tasks()
    task_ids = {t["id"] for t in tasks}

    path = os.path.join(ROOT, "provenance", "sources.yaml")
    reg = yaml.safe_load(open(path, encoding="utf-8"))
    verified = reg.get("verified")
    entries = reg.get("tasks", {}) or {}

    problems = []

    if not verified:
        problems.append("registry has no 'verified' date")

    for tid in sorted(task_ids):
        e = entries.get(tid)
        if not e:
            problems.append(f"MISSING provenance: {tid}")
            continue
        srcs = e.get("sources") or []
        if not srcs:
            problems.append(f"NO SOURCES: {tid}")
            continue
        for s in srcs:
            if not (isinstance(s, str) and s.startswith(("http://", "https://"))):
                problems.append(f"BAD SOURCE URL for {tid}: {s!r}")

    for tid in sorted(set(entries) - task_ids):
        problems.append(f"STALE entry (no such task): {tid}")

    total_sources = sum(len(e.get("sources", [])) for e in entries.values())
    print(f"Tasks: {len(task_ids)}   Registry entries: {len(entries)}   "
          f"Source URLs: {total_sources}   Verified: {verified}")

    if problems:
        print(f"\nPROVENANCE FAILED ({len(problems)}):")
        for p in problems:
            print("  -", p)
        return 1

    print("\nPROVENANCE GATE PASSED: every task is grounded in >=1 real source")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
