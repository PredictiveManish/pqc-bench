# PQC-Eval

A runnable benchmark that scores large language models on **post-quantum
cryptography** — the algorithms, the standards that govern them, and the
real-world deployments where they are already in use.

Every task is grounded in a primary source (NIST, NSA CNSA 2.0, CERT-In, TEC,
DST/National Quantum Mission, BSI, ANSSI, ENISA, UK NCSC, OpenSSH, Cloudflare,
Apple, Signal). Nothing in the suite is an unsourced LLM assertion: the
provenance registry binds each task to its sources, and the build fails if any
task is ungrounded.

**v1.0.0 — standards-grounded.**

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
    --k 1 --workers 8 --md results/gpt-4o.md --out results/gpt-4o.json
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

## What it measures (57 tasks)

| Tier | What | Type | Ground truth |
|---|---|---|---|
| knowledge | security basis, FIPS numbers, parameter sizes, attack history | multiple choice | answer key |
| standards | real regulatory facts: NIST IR 8547, CNSA 2.0, NCSC, BSI, ANSSI, CERT-In, TEC, DST/NQM, HQC | multiple choice | primary-source documents |
| implementation | Compress_d, BitRev7, zeta table, Barrett reduction | code | FIPS 203, cross-checked vs `kyber-py` |
| debugging | find the latent defect in real PQC code | code | defect injected, graded by execution |
| judgment | IoT signature choice, TLS KEM trade-off, FALCON risk | open | weighted rubric |
| scenarios | India bank migration, SSH fleet, TLS PQ-signature gap, CNSA 2.0 firmware signing | open | weighted rubric + sources |
| engineering | repo discovery, indirect-usage audit, CBOM, patch, ML-KEM encapsulation | repo | P/R/F1 + evidence, or fixture tests / KAT |

**Repository tier (5 tasks):** `repo-discover-crypto` (token-recall audit),
`repo-discover-indirect` (precision / recall / F1 + evidence accuracy),
`repo-patch-crypto` (graded by the fixture's own `unittest` suite),
`repo-cbom` (CycloneDX-style schema validator) and
`fullscheme-mlkem-encaps` (fixed KAT vectors).

These are **repo-context** tasks: the fixture files named in `context_files` are
injected into the model's prompt. The model does **not** receive filesystem or
terminal access, so this measures repository *reasoning*, not agentic
engineering.

What happens to the output differs by task: discovery tasks have their
structured findings **scored**; patch and KAT tasks have submitted code
**executed** against fixture tests or KAT vectors; the CBOM task has submitted
JSON **validated** by a schema check. Where code does run, it runs in
process-level isolation (temp cwd, scrubbed env, rlimits, `unshare -n` when
permitted) — not a container.

**Not yet statistically validated.** 57 tasks support a research preview, not a
model ranking. There are no published baselines, no held-out split and no
human-calibrated scorer yet; treat scores as indicative.

## Why the numbers are trustworthy

Four gates run before any model result counts (`make all`):

1. **`scripts/validate_sources.py`** — every task has ≥1 real source URL
   (57/57 tasks, 74 sources, verified 2026-11-25).
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
graders/          resource-limited subprocess execution + per-task checkers
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
- **MCQ parsing** uses the last explicit answer marker and returns `ambiguous`
  rather than guessing when several letters appear.
- **Rubric scoring is keyword coverage** with a clause-scoped negation guard — a
  proxy. A fluent wrong answer can still slip through; an LLM judge calibrated
  against humans is the fix (`DESIGN.md`).
- **Code execution** is a resource-limited subprocess, not a security sandbox:
  environment secrets are scrubbed and rlimits applied, but it is not safe for
  hostile third-party submissions.
- **57 tasks** is a solid skeleton, not a statistically robust eval.
- **Repository tasks** run in process-level isolation (temp cwd, scrubbed env,
  rlimits, `unshare -n` when permitted), not a container.

## Scope and ethics

Tasks target published standards and documented attacks for evaluation and
education. Debugging tasks contain deliberately broken code to measure detection;
they are not tools for attacking deployed systems.

PQC-Eval is an independent evaluation project. It is **not a certification
scheme**, and it is not endorsed by, affiliated with, or approved by NIST,
CERT-In, TEC, the DST, NSA, BSI, ANSSI, ENISA, the NCSC or any government. A
score is not a compliance or certification claim about any model or product.
