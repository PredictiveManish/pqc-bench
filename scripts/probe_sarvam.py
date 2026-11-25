"""One-call probe: confirm what Sarvam actually returns.

Costs a single request. Prints the response shape (content vs reasoning_content,
finish_reason, token usage) so you can tell truncation from an empty answer.

    export SARVAM_API_KEY=sk_...
    python scripts/probe_sarvam.py                 # default 4096 tokens
    python scripts/probe_sarvam.py --max-tokens 16384
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness.providers import ProviderError, SarvamProvider


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="sarvam-105b")
    ap.add_argument("--max-tokens", type=int, default=4096)
    ap.add_argument("--base-url", default=None)
    args = ap.parse_args()

    prompt = (
        "Answer in at most three sentences. Which key-establishment algorithm does "
        "NSA's CNSA 2.0 require, and by which year must web browsers and servers "
        "exclusively use CNSA 2.0? Name the parameter set and the year."
    )

    try:
        p = SarvamProvider(args.model, base_url=args.base_url)
        c = p.complete(prompt, max_tokens=args.max_tokens)
    except ProviderError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    raw = c.raw or {}
    choice = (raw.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    content = msg.get("content") or ""
    reasoning = msg.get("reasoning_content") or ""

    print("=== response shape ===")
    print(f"finish_reason      : {c.finish_reason!r}")
    print(f"content length     : {len(content)}")
    print(f"reasoning length   : {len(reasoning)}")
    print(f"completion_tokens  : {c.completion_tokens}")
    print(f"message keys       : {list(msg.keys())}")
    print(f"usage              : {json.dumps(raw.get('usage', {}))}")
    print()
    print("content   :", content[:300].replace("\n", " ") or "<EMPTY>")
    print("reasoning :", reasoning[:300].replace("\n", " ") or "<EMPTY>")

    print()
    if not content.strip() and c.finish_reason == "length":
        print("DIAGNOSIS: truncated — reasoning consumed the whole budget. "
              "Raise --max-tokens.")
    elif not content.strip():
        print("DIAGNOSIS: empty content, not a length stop. Answer may live in "
              "reasoning_content; consider a provider-level fallback.")
    else:
        print("DIAGNOSIS: normal — content is populated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
