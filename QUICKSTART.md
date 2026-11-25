# Quickstart — set up, verify, and run PQCBench

Three audiences, three paths. Pick yours.

---

## 1. Someone who just wants to check it's real (5 minutes, no API key)

```bash
git clone <your-repo-url> pqcbench && cd pqcbench
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Run the four gates. These need **no credentials** and prove the suite is sound:

```bash
python scripts/validate_sources.py         # every task has a real source URL
python scripts/validate_ground_truth.py    # checkers match kyber-py / dilithium-py
python scripts/validate.py                 # gold=1.0, null=0.0, bugs rejected
python tests/test_plumbing.py              # providers, cache, runner, reports
```

Expected: each prints `... PASSED`. If any fails, the suite is broken — stop and
open an issue. That is the whole point of the gates.

---

## 2. Someone who wants to score a model (10 minutes + a key)

```bash
export OPENAI_API_KEY=sk-...          # or ANTHROPIC_API_KEY / GEMINI_API_KEY / SARVAM_API_KEY

# full suite
python scripts/run_eval.py --provider openai --model gpt-4o \
    --k 3 --workers 8 --md results/gpt-4o.md --out results/gpt-4o.json

# just the standards + scenarios tiers (the real-world part)
python scripts/run_eval.py --provider openai --model gpt-4o \
    --tiers standards,scenarios --k 1 --md results/gpt-4o-rw.md
```

Sarvam AI (Indian models; uses your Sarvam credits):

```bash
export SARVAM_API_KEY=sk_...          # from dashboard.sarvam.ai

# flagship, /v1 endpoint
python scripts/run_eval.py --provider sarvam --model sarvam-105b \
    --k 1 --workers 4 --md results/sarvam-105b.md

# open-weight models on /v2 (glm5.3, gemma4, deepseekv4.1-flash-1017, ...)
python scripts/run_eval.py --provider sarvam --model glm5.3 \
    --base-url https://api.sarvam.ai/v2 --md results/sarvam-glm.md
```

Notes: `--model` defaults to `sarvam-105b`. `sarvam-m` is deprecated. Sarvam
returns **HTTP 403** (not 401) for a bad key; the harness turns that into a clear
message. Start with `--tiers standards,scenarios` to spend credits on the
real-world part first.

Local / self-hosted models (no vendor key):

```bash
python scripts/run_eval.py --provider compatible \
    --base-url http://localhost:11434/v1 --model qwen2.5:7b
```

Read `results/<model>.md`. It has per-tier tables, a failures list with reasons,
and token/cost usage. Re-running the same command hits the disk cache and costs
nothing — use `--no-cache` to force fresh calls.

Notes:
- `--k N` = pass@k (best of N). At temperature 0 it samples once and replicates.
- `--workers` controls concurrency; lower it if you hit rate limits.
- `--price-in/--price-out` (USD per 1M tokens) add a cost estimate.
- Keys are read from the environment only and never written to disk.

---

## 3. Someone who wants to add or break a task (contributor)

1. Add a task to `tasks/<tier>.yaml`. Tiers: `knowledge`, `standards`,
   `implementation`, `debugging`, `judgment`, `scenarios`.
2. Add its provenance to `provenance/sources.yaml`:
   ```yaml
   my-task-id:
     basis: "one line: what the source says"
     sources:
       - https://primary-source.example/doc
   ```
3. If it's a `code` task, add a checker at `graders/checks/<name>.py` exposing
   `check(mod) -> bool | (bool, str)`, and point `checker:` at it.
4. Re-run all four gates. A task is only "real" when:
   - it has a source URL,
   - its `gold` scores 1.0,
   - (if supplied) its `buggy` scores 0.0.

The gates will reject an unsourced task. That is deliberate.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `OPENAI_API_KEY is not set` | no credentials | export the key, or use `--provider compatible` against a local server |
| `error: unknown provider` | typo | one of `openai, anthropic, gemini, compatible` |
| Slow run | concurrency too low | raise `--workers` |
| `HTTP 429` | rate limited | lower `--workers`; retries already back off |
| Scores all zero | key invalid or model refusing | check the `failures` list in the report |
| Gate fails after editing tasks | missing provenance / wrong gold | read the failing gate's message; it names the task id |

---

## Publishing checklist (maintainers)

- [ ] CI runs the four gates on every push (`.github/workflows/ci.yml`).
- [ ] `LICENSE` chosen (MIT by default — change if you prefer Apache-2.0).
- [ ] Repo public; README renders; `STANDARDS.md` links resolve.
- [ ] Tag a release (`v0.3`) and mint a Zenodo DOI.
- [ ] HuggingFace: dataset for `tasks/`, Space for the leaderboard.
- [ ] Add baseline results from at least 2–3 named models before calling it a
      leaderboard.
