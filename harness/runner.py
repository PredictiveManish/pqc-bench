"""Task loading and the concurrent evaluation loop."""

from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import yaml

from harness.metrics import aggregate
from harness.scorers import score
from harness.types import Completion

ROOT = Path(__file__).resolve().parents[1]


def load_tasks(tasks_dir: str | None = None, tiers: list[str] | None = None) -> list[dict]:
    d = Path(tasks_dir) if tasks_dir else ROOT / "tasks"
    tasks: list[dict] = []
    seen: set[str] = set()
    for f in sorted(d.glob("*.yaml")):
        data = yaml.safe_load(f.read_text(encoding="utf-8")) or []
        for t in data:
            if t["id"] in seen:
                raise ValueError(f"duplicate task id: {t['id']}")
            seen.add(t["id"])
            t["_file"] = f.name
            if not tiers or t["tier"] in tiers:
                tasks.append(t)
    return tasks


def _complete(model, prompt: str, **kw) -> Completion:
    if hasattr(model, "complete"):
        return model.complete(prompt, **kw)
    text = model.generate(prompt, **kw)
    return Completion(text=text, model=getattr(model, "name", "unknown"))


def run(model, tasks: list[dict], *, k: int = 1, out_path: str | None = None,
        md_path: str | None = None, workers: int = 4, cache=None,
        temperature: float = 0.0, max_tokens: int = 4096, system: str = "",
        pricing: tuple[float, float] | None = None, verbose: bool = True) -> dict:
    pname = getattr(model, "name", "unknown")
    # Deterministic decoding: sample once per task and replicate; sampling k
    # times at temperature 0 only wastes tokens and races the cache.
    jobs = ([(t, 0) for t in tasks] if temperature == 0
            else [(t, i) for t in tasks for i in range(k)])
    collected: dict[str, list] = {t["id"]: [None] * k for t in tasks}
    usage = {"calls": 0, "cache_hits": 0, "errors": 0,
             "prompt_tokens": 0, "completion_tokens": 0}

    def work(task, idx):
        key = None
        if cache is not None:
            salt = str(idx) if temperature > 0 else ""
            key = cache.key(pname, task["prompt"], system, temperature, max_tokens, salt)
            hit = cache.get(key)
            if hit is not None:
                return task["id"], idx, hit, "hit", None
        try:
            comp = _complete(model, task["prompt"], system=system,
                             temperature=temperature, max_tokens=max_tokens)
        except Exception as e:  # noqa: BLE001 - surfaced per task
            return task["id"], idx, None, "error", str(e)
        if cache is not None and key is not None:
            cache.put(key, comp)
        return task["id"], idx, comp, "call", None

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        futures = [ex.submit(work, t, i) for t, i in jobs]
        for fut in as_completed(futures):
            tid, idx, comp, status, err = fut.result()
            collected[tid][idx] = (comp, status, err)
            if status == "hit":
                usage["cache_hits"] += 1
            elif status == "call":
                usage["calls"] += 1
                usage["prompt_tokens"] += comp.prompt_tokens
                usage["completion_tokens"] += comp.completion_tokens
            else:
                usage["errors"] += 1

    results = []
    for t in tasks:
        samples = []
        for i in range(k):
            slot = 0 if temperature == 0 else i
            comp, status, err = collected[t["id"]][slot]
            if comp is None:
                samples.append({"type": t["type"], "score": 0.0,
                                "status": status, "error": err})
                continue
            s = score(t, comp.text)
            s["status"] = status
            s["output"] = comp.text
            samples.append(s)
        best = max((s["score"] for s in samples), default=0.0)
        results.append({"id": t["id"], "tier": t["tier"], "type": t["type"],
                        "score": best, "samples": samples})

    cost = None
    if pricing:
        pin, pout = pricing
        cost = (usage["prompt_tokens"] / 1e6 * pin
                + usage["completion_tokens"] / 1e6 * pout)

    report = {
        "model": pname,
        "k": k,
        "temperature": temperature,
        "duration_s": round(time.time() - t0, 2),
        "usage": usage,
        "est_cost_usd": cost,
        "summary": aggregate(results),
        "results": results,
    }

    if out_path:
        p = Path(out_path)
        p = p if p.is_absolute() else ROOT / p
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")

    if md_path:
        from harness.report import render_markdown
        p = Path(md_path)
        p = p if p.is_absolute() else ROOT / p
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(render_markdown(report), encoding="utf-8")

    if verbose:
        print_report(report)
    return report


def print_report(report: dict) -> None:
    s = report["summary"]
    u = report["usage"]
    print(f"\nModel: {report['model']}   (k={report['k']}, temp={report['temperature']})")
    print(f"Tasks: {s['n']}   Overall mean: {s['overall_mean_score']:.3f}   "
          f"Pass rate: {s['overall_pass_rate']:.3f}   Time: {report['duration_s']}s")
    print("  by tier:")
    for tier, b in s["by_tier"].items():
        print(f"    {tier:<16} n={b['n']:<3} mean={b['mean_score']:.3f} pass={b['pass_rate']:.3f}")
    print("  by type:")
    for typ, b in s["by_type"].items():
        print(f"    {typ:<16} n={b['n']:<3} mean={b['mean_score']:.3f} pass={b['pass_rate']:.3f}")
    print(f"  usage: calls={u['calls']} cache_hits={u['cache_hits']} errors={u['errors']} "
          f"tokens_in={u['prompt_tokens']} tokens_out={u['completion_tokens']}")
    if report.get("est_cost_usd") is not None:
        print(f"  est cost: ${report['est_cost_usd']:.4f}")
    fails = [r for r in report["results"] if r["score"] < 0.999]
    if fails:
        print("  failures:")
        for r in fails:
            d = r["samples"][0]
            reason = d.get("error") or d.get("msg") or d.get("predicted") or d.get("violation")
            print(f"    - {r['id']:<24} score={r['score']:.2f} {reason or ''}")
