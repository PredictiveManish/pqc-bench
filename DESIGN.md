# PQC-Eval — Design

## 1. Why this benchmark is worth building

PQC is an unusually clean substrate for AI evaluation:

- **Specified reference behaviour.** FIPS 203/204/205 pin down exact algorithms;
  correctness is machine-checkable.
- **A real regulatory surface.** NIST, NSA CNSA 2.0, UK NCSC, BSI, ANSSI, ENISA
  and India's CERT-In / TEC / DST-NQM all set concrete requirements and dates.
  Getting them wrong is a real failure with real consequences.
- **Live deployments to reason about.** TLS, OpenSSH, Signal and iMessage have
  shipped PQC; models should reason about what is actually deployed, not a
  textbook abstraction.
- **A documented capability gap.** LLMs hallucinate crypto APIs and misstate
  standards.

## 2. Grounding (the core design constraint)

No task is an unsourced LLM assertion. Each task is bound in
`provenance/sources.yaml` to ≥1 primary source URL and a one-line basis, and
`scripts/validate_sources.py` fails the build if any task is ungrounded or a
source is not a real URL. `STANDARDS.md` is the human-readable reference.

This is what separates the suite from "LLM-generated questions": a reviewer can
trace any fact to the document that states it, and re-verify dates cheaply.

## 3. Task taxonomy

| Tier | Ground truth | Scoring | Failure it catches |
|---|---|---|---|
| knowledge | fixed answer key | exact letter match | factual hallucination |
| standards | primary-source documents | exact letter match | misstating regulation / dates |
| implementation | FIPS 203 formulas | code executes & matches | wrong algorithm / arithmetic |
| debugging | injected defect | code executes & matches | inability to localise a bug |
| judgment | expert rubric | weighted criteria + must_not | shallow trade-off reasoning |
| scenarios | rubric + sources | weighted criteria + must_not | unusable real-world advice |

## 4. Ground truth, validated

- **Component checks** are reference formulas computed live (no stored vectors).
- **Cross-validated against reference implementations.**
  `scripts/validate_ground_truth.py` proves our zeta table and compress/decompress
  match `kyber-py`, and that ML-KEM-512/768/1024 and ML-DSA-44/65/87 round-trip at
  the standard's sizes.
- **Standards facts** are quoted from the primary documents in `STANDARDS.md`.
- **Debugging tasks** carry both `gold` and `buggy` submissions so we can assert
  the task discriminates.

## 5. Execution architecture

- **Providers**: OpenAI, Anthropic, Gemini, any OpenAI-compatible endpoint, over
  stdlib HTTP. Transient errors (429/5xx/network) retry with backoff + jitter.
- **Concurrency**: a thread pool over `(task, sample)` jobs.
- **Determinism**: at temperature 0 a task is sampled once and replicated across
  `k`; at temperature > 0 each sample is salted in the cache key.
- **Cache**: content-addressed; re-runs are free.
- **Usage & cost**: tokens in/out summed; `--price-in/--price-out` give a USD
  estimate; cache hits reported separately.
- **Reports**: JSON (per-sample) and Markdown (tables + failures + usage).

## 6. Metrics

- Per task: score in [0,1]. Overall: mean score and pass rate (pass ≥ 0.999).
- Slices by tier and type. pass@k = best of k samples.
- Planned: calibration, hallucination rate, insecure-code rate.

## 7. Integrity gates (`make all`)

1. provenance: every task grounded in a real source;
2. ground truth vs reference implementations;
3. gold=1.0, null=0.0, bugs rejected;
4. provider/cache/runner/report plumbing.

## 8. Known limitations

- **No frontier run in the build environment** — no LLM credentials there. The
  harness is verified end to end with stubs; a key is the only missing piece.
- **Standards drift.** Facts verified 2026-11-25; deadlines change. The registry
  makes re-verification cheap but does not automate it.
- **MCQ parsing** picks the first standalone A–E letter.
- **Rubric keyword scoring** rewards mention, not correctness.
- **43 tasks** is a skeleton, not a statistically robust eval.

## 9. Roadmap

1. ~~Cross-validate ground truth against reference implementations~~ — done.
2. ~~Ground every task in a primary source~~ — done.
3. **Grow the debugging tier** by generating verified defect variants.
4. **LLM-judge for judgment/scenarios** — replace keyword scoring; calibrate
   against expert answers.
5. **Full-scheme KAT tasks** via `kyber-py`.
6. **Agentic migration tier** — repos with quantum-vulnerable crypto; grade on
   precision/recall + compiling, test-passing patches.
7. **Re-verification job** — a scheduled check that source URLs still resolve and
   dates still hold.

## 10. Threats to validity

- **Memorisation vs. reasoning.** Public standards invite recall; the generated
  debugging tier and scenario reasoning are the main defences.
- **Scorer gaming.** Letter parsing and keyword rubrics are gameable.
- **Jurisdiction confusion.** Deadlines differ by country and asset class; tasks
  test the distinctions deliberately, but a single "correct date" is a trap the
  suite is designed to avoid.
- **Construct validity.** Component tasks ≠ a secure full implementation.
