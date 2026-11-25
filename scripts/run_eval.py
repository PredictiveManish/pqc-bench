"""Run PQC-Eval against a real model.

Examples
--------
OpenAI:
    export OPENAI_API_KEY=sk-...
    python scripts/run_eval.py --provider openai --model gpt-4o \
        --k 1 --workers 8 --md results/gpt-4o.md

Anthropic:
    export ANTHROPIC_API_KEY=sk-ant-...
    python scripts/run_eval.py --provider anthropic --model claude-3-5-sonnet-latest

Gemini:
    export GEMINI_API_KEY=...
    python scripts/run_eval.py --provider gemini --model gemini-2.0-flash

A local / self-hosted OpenAI-compatible server (vLLM, Ollama, LM Studio, Groq,
Together, OpenRouter ...):
    python scripts/run_eval.py --provider compatible \
        --base-url http://localhost:11434/v1 --model qwen2.5:7b

Keys are read from the environment only and never written to disk.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness.cache import DiskCache
from harness.providers import ProviderError, make_provider
from harness.runner import load_tasks, run


def main() -> int:
    ap = argparse.ArgumentParser(description="Run PQC-Eval against a model.")
    ap.add_argument("--provider", required=True,
                    choices=["sarvam", "openai", "anthropic", "gemini", "compatible"])
    ap.add_argument("--model", default=None,
                    help="model id (default sarvam-105b for --provider sarvam)")
    ap.add_argument("--base-url", default=None,
                    help="required for --provider compatible")
    ap.add_argument("--k", type=int, default=1, help="samples per task (pass@k)")
    ap.add_argument("--workers", type=int, default=4, help="concurrent requests")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--max-tokens", type=int, default=4096)
    ap.add_argument("--tiers", default=None,
                    help="comma-separated tiers to run (default: all)")
    ap.add_argument("--out", default=None, help="JSON report path")
    ap.add_argument("--md", default=None, help="Markdown report path")
    ap.add_argument("--cache-dir", default=".cache")
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--price-in", type=float, default=None,
                    help="USD per 1M input tokens (for cost estimate)")
    ap.add_argument("--price-out", type=float, default=None,
                    help="USD per 1M output tokens (for cost estimate)")
    args = ap.parse_args()

    if not args.model:
        if args.provider == "sarvam":
            args.model = "sarvam-105b"
        else:
            print("error: --model is required", file=sys.stderr)
            return 2

    try:
        model = make_provider(args.provider, args.model,
                              base_url=args.base_url)
    except ProviderError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    tiers = [t.strip() for t in args.tiers.split(",")] if args.tiers else None
    tasks = load_tasks(tiers=tiers)
    if not tasks:
        print("error: no tasks matched", file=sys.stderr)
        return 2

    cache = None if args.no_cache else DiskCache(args.cache_dir)
    pricing = None
    if args.price_in is not None and args.price_out is not None:
        pricing = (args.price_in, args.price_out)

    out = args.out or f"results/{args.model.replace('/', '_')}.json"
    run(model, tasks, k=args.k, workers=args.workers, cache=cache,
        temperature=args.temperature, max_tokens=args.max_tokens,
        pricing=pricing, out_path=out, md_path=args.md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
