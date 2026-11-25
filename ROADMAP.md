# Roadmap and explicit non-claims

## What PQC-Eval is not

- Not a certification scheme, and not a FIPS conformance test suite.
- Not a validated leaderboard.
- Not a measure of production PQC engineering capability.
- Not endorsed by, affiliated with, or approved by NIST, CERT-In, TEC, the DST,
  NSA, BSI, ANSSI, ENISA, the NCSC or any government.

## Release posture

> PQC-Eval: an experimental benchmark for evaluating LLM knowledge, standards
> reasoning and selected implementation tasks in post-quantum cryptography.

Suitable to publish as a research preview. Not suitable for ranking models in
public, and not suitable for compliance claims.

## Blockers before any leaderboard or "validated" claim

### P0 — correctness and safety

- [x] NTT grader fails closed without an independent reference
- [x] MCQ answer-span: last explicit marker wins; ambiguous answers refused
- [x] Cache identity includes the endpoint
- [x] Code runner scrubs secret-bearing environment variables
- [x] Benchmark-version hash covers prompts, task metadata, checker contents and
      the scorer implementation
- [ ] Official ACVP / NIST KAT vectors — round-trip consistency is not conformance
- [ ] Container or VM isolation for untrusted submissions (network off, read-only
      filesystem, non-root)

### P1 — evidence quality

- [ ] Claim-level provenance: `claim -> source -> section -> evidence_type`
      instead of a URL per task
- [ ] Source reachability and document-version checks
- [ ] Distinguish primary from secondary sources in the registry
- [ ] SLH-DSA validation coverage

### P2 — research validity

- [ ] Human baselines from at least three expertise levels
- [ ] Held-out task split, private until evaluation
- [ ] Calibrated LLM judge, with human/evaluator agreement reported
- [ ] Multi-model baselines under reproducible conditions
- [ ] Confidence intervals and score variance

### P3 — capability depth

- [ ] Repository-level cryptographic discovery and CBOM generation
- [ ] Migration patches graded by compile + test + interoperability
- [ ] Side-channel and constant-time challenges

P3 is a different product (a *PQC-Migrate* agent benchmark), not an expansion of
this task list. Keep the two leaderboards separate.

## Known limitations, stated plainly

- 30 of 44 tasks are multiple choice: this measures recall more than engineering.
- The rubric scorer is keyword-based with a clause-scoped negation guard and
  criterion-level exclusions; it is a proxy, not a semantic evaluator.
- Graders for Barrett/compress/zetas encode the reference formula themselves.
- Facts are verified as of 2026-11-25 and will drift.
