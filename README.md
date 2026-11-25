# PQC-Eval

A runnable benchmark that scores large language models on **post-quantum
cryptography** — the algorithms, the standards that govern them, and the
real-world deployments where they are already in use.

Every task is grounded in a primary source (NIST, NSA CNSA 2.0, CERT-In, TEC,
DST/National Quantum Mission, BSI, ANSSI, ENISA, UK NCSC, OpenSSH, Cloudflare,
Apple, Signal). Nothing in the suite is an unsourced LLM assertion: the
provenance registry binds each task to its sources, and the build fails if any
task is ungrounded.

**v0.3 — standards-grounded.**

## What's grounded, and how

- **`STANDARDS.md`** — the verified reference: FIPS 203/204/205, NIST IR 8547
  (final, Oct 2026), CNSA 2.0, India's CERT-In / TEC / DST-NQM framework, BSI,
  ANSSI, ENISA, UK NCSC, and the live deployments (TLS, OpenSSH, Signal, iMessage).
- **`provenance/sources.yaml`** — task id → primary source URLs + basis.
- **`scripts/validate_sources.py`** — fails if any task lacks a real source URL.

Verified 2026-11-25. Deadlines and scopes change; confirm against the current text.

## Install

```bash
pip install -r requirements.txt      # pyyaml, kyber-py, dilithium-py
```

## Run it against a real model

```bash
export OPENAI_API_KEY=sk-...
python scripts/run_eval.py --provider openai --model gpt-4o \
    --k 3 --workers 8 --md results/gpt-4o.md --out results/gpt-4o.json
```

Providers: `sarvam`, `openai`, `anthropic`, `gemini`, or `compatible` (vLLM,
Ollama, LM Studio, Groq, Together, OpenRouter) via `--base-url`. Keys are read
from the environment only.

Sarvam AI:

```bash
export SARVAM_API_KEY=sk_...
python scripts/run_eval.py --provider sarvam --model sarvam-105b \
    --tiers standards,scenarios --k 1 --md results/sarvam.md
```

Flags: `--k` (pass@k), `--workers`, `--temperature`, `--tiers` (e.g.
`standards,scenarios`), `--no-cache`, `--price-in/--price-out`.

## What it measures (41 tasks)

| Tier | What | Type | Ground truth |
|---|---|---|---|
| knowledge | security basis, FIPS numbers, parameter sizes, attack history | multiple choice | answer key |
| standards | real regulatory facts: NIST IR 8547, CNSA 2.0, NCSC, BSI, ANSSI, CERT-In, TEC, DST/NQM, HQC | multiple choice | primary-source documents |
| implementation | Compress_d, BitRev7, zeta table, Barrett reduction | code | FIPS 203, cross-checked vs `kyber-py` |
| debugging | find the latent defect in real PQC code | code | defect injected, graded by execution |
| judgment | IoT signature choice, TLS KEM trade-off, FALCON risk | open | weighted rubric |
| scenarios | India bank migration, SSH fleet, TLS PQ-signature gap, CNSA 2.0 firmware signing | open | weighted rubric + sources |

## Why the numbers are trustworthy

Four gates run before any model result counts (`make all`):

1. **`scripts/validate_sources.py`** — every task has ≥1 real source URL
   (41/41 tasks, 58 sources, verified 2026-11-25).
2. **`scripts/validate_ground_truth.py`** — our zeta/compress formulas match
   `kyber-py` exactly, and ML-KEM-512/768/1024 and ML-DSA-44/65/87 round-trip at
   the standard's sizes. Checked against the real implementations.
3. **`scripts/validate.py`** — gold oracle 1.000, null model 0.000, every injected
   bug rejected. If the scorers drift, this fails.
4. **`tests/test_plumbing.py`** — provider parsing, concurrent runner, cache,
   Markdown rendering.

```
make sources       # every task grounded in a real source
make groundtruth   # ground truth vs reference implementations
make validate      # gold / null / buggy integrity gate
make test          # plumbing
```

## Layout

```
STANDARDS.md      verified standards & deployment reference
provenance/       task id -> sources registry
harness/          providers, runner, cache, scorers, metrics, report
graders/          sandboxed code execution + per-task checkers
tasks/            knowledge / standards / implementation / debugging /
                  judgment / scenarios (.yaml)
scripts/          run_eval, validate, validate_ground_truth, validate_sources
tests/            plumbing tests
```

## Adding tasks

Add a task to `tasks/*.yaml`, then add its entry to `provenance/sources.yaml`.
For a code task, add a checker in `graders/checks/`. Run `make all`: your task is
only real once it has a source, its `gold` passes, and (if supplied) its `buggy`
fails.

## Honest limitations

- **No frontier run in the build environment** — that sandbox had no LLM
  credentials, so no live frontier scores are included. Plumbing and ground truth
  are fully verified; a key is the only missing piece. Run the command above.
- **Standards move.** Facts are verified as of 2026-11-25; re-verify before relying
  on any date. The registry makes that cheap.
- **MCQ parsing** takes the first standalone A–E letter; narration before the
  answer can mis-score. Fix: answer-span extraction.
- **Rubric scoring is keyword coverage**, a proxy — a fluent wrong answer can hit
  keywords. LLM-judge upgrade is in `DESIGN.md`.
- **41 tasks** is a solid skeleton, not a statistically robust eval.

## Scope and ethics

Tasks target published standards and documented attacks for evaluation and
education. Debugging tasks contain deliberately broken code to measure detection;
they are not tools for attacking deployed systems.
