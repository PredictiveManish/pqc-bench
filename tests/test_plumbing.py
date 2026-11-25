"""Plumbing tests: provider parsing, concurrency, cache, report rendering.

These use stubs so they run with no credentials. They prove the production code
paths are correct; they are NOT model results. Run: python tests/test_plumbing.py
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import harness.providers as P
from harness.cache import DiskCache
from harness.providers import (AnthropicProvider, GeminiProvider,
                               OpenAIProvider, SarvamProvider, BaseProvider)
from harness.report import render_markdown
from harness.runner import load_tasks, run
from harness.types import Completion

FAILS = []


def check(name, cond, detail=""):
    print(f"  [{'ok' if cond else 'FAIL'}] {name}" + ("" if cond else f"  {detail}"))
    if not cond:
        FAILS.append(name)


class StubProvider(BaseProvider):
    name = "stub:test"

    def __init__(self):
        self.calls = 0

    def complete(self, prompt, *, system="", temperature=0.0, max_tokens=4096):
        self.calls += 1
        return Completion(text="A", model=self.name,
                          prompt_tokens=10, completion_tokens=2)


def test_provider_parsing():
    print("\n[providers] response parsing (network stubbed)")
    orig = P._post_json

    P._post_json = lambda url, headers, payload, **kw: {
        "choices": [{"message": {"content": "hello"}}],
        "model": "gpt-x",
        "usage": {"prompt_tokens": 5, "completion_tokens": 7},
    }
    c = OpenAIProvider("gpt-x", api_key="x").complete("p")
    check("openai parse", c.text == "hello" and c.prompt_tokens == 5
          and c.completion_tokens == 7, c)

    P._post_json = lambda url, headers, payload, **kw: {
        "content": [{"type": "text", "text": "hi"}],
        "model": "claude-x",
        "usage": {"input_tokens": 3, "output_tokens": 4},
    }
    c = AnthropicProvider("claude-x", api_key="x").complete("p")
    check("anthropic parse", c.text == "hi" and c.prompt_tokens == 3
          and c.completion_tokens == 4, c)

    P._post_json = lambda url, headers, payload, **kw: {
        "candidates": [{"content": {"parts": [{"text": "yo"}]}}],
        "usageMetadata": {"promptTokenCount": 2, "candidatesTokenCount": 1},
    }
    c = GeminiProvider("gemini-x", api_key="x").complete("p")
    check("gemini parse", c.text == "yo" and c.prompt_tokens == 2
          and c.completion_tokens == 1, c)

    P._post_json = lambda url, headers, payload, **kw: {
        "choices": [{"message": {"content": "namaste"}}],
        "model": "sarvam-105b",
        "usage": {"prompt_tokens": 6, "completion_tokens": 3},
    }
    c = SarvamProvider("sarvam-105b", api_key="x").complete("p")
    check("sarvam parse", c.text == "namaste" and c.prompt_tokens == 6
          and c.completion_tokens == 3, c)

    def _boom(url, headers, payload, **kw):
        raise P.ProviderError("HTTP 403: {\"error\":{\"code\":\"invalid_api_key_error\"}}")
    P._post_json = _boom
    ok403 = False
    try:
        SarvamProvider("sarvam-105b", api_key="x").complete("p")
    except P.ProviderError as e:
        ok403 = "403" in str(e) and "SARVAM_API_KEY" in str(e)
    check("sarvam 403 handled clearly", ok403)

    P._post_json = orig


def test_concurrency_and_cache():
    print("\n[runner] concurrency + disk cache")
    tasks = load_tasks(tiers=["knowledge"])[:3]
    with tempfile.TemporaryDirectory() as d:
        cache = DiskCache(os.path.join(d, "cache"))
        m = StubProvider()
        r1 = run(m, tasks, k=2, workers=4, cache=cache, verbose=False)
        check("first run: 3 model calls (temp0 dedupe)", r1["usage"]["calls"] == 3, r1["usage"])
        check("first run: 0 cache hits", r1["usage"]["cache_hits"] == 0, r1["usage"])
        check("first run: all tasks scored", len(r1["results"]) == 3)
        check("first run: k samples replicated", len(r1["results"][0]["samples"]) == 2)

        m2 = StubProvider()
        r2 = run(m2, tasks, k=2, workers=4, cache=cache, verbose=False)
        check("second run: served from cache (0 calls)", m2.calls == 0, m2.calls)
        check("second run: 3 cache hits", r2["usage"]["cache_hits"] == 3, r2["usage"])

        md = os.path.join(d, "r.md")
        run(m2, tasks, k=1, workers=2, cache=cache, md_path=md, verbose=False)
        text = open(md).read()
        check("markdown has tier table", "| Tier |" in text)
        check("markdown has overall line", "Overall mean score" in text)


def main() -> int:
    print("=" * 56)
    print("PQC-Eval plumbing tests (no credentials required)")
    print("=" * 56)
    test_provider_parsing()
    test_concurrency_and_cache()
    print("\n" + "=" * 56)
    if FAILS:
        print(f"FAILED: {FAILS}")
        return 1
    print("ALL PLUMBING TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
