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
- [~] Process-level isolation only: temp cwd, scrubbed env, rlimits,
      `unshare -n` when permitted. No filesystem namespace, no container.

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

- [x] Repository-level cryptographic discovery with precision/recall/F1 + evidence
- [x] CycloneDX-style CBOM generation with schema validation
- [x] Patch tasks graded by the fixture's own `unittest` suite
- [x] Full-scheme KAT task (ML-KEM-512 encapsulation vs fixed vectors)
- [ ] Migration patches graded by compile + interoperability across repos
- [ ] Multi-language fixtures (Java/C++), which need those toolchains
- [ ] Side-channel and constant-time challenges

Repository-level tasks now live in PQC-Eval under a separate `engineering` tier,
scored on their own track. A full agentic migration benchmark (*PQC-Agent*:
workspace access, multi-file patches, interoperability) remains a separate
product. Keep the two leaderboards separate.

## Known limitations, stated plainly

- 30 of 57 tasks are multiple choice (53%): recall-heavy, though code is now 15 tasks and repo-level work is 5.
- The rubric scorer is keyword-based with a clause-scoped negation guard and
  criterion-level exclusions; it is a proxy, not a semantic evaluator.
- Graders for Barrett/compress/zetas encode the reference formula themselves.
- Facts are verified as of 2026-11-25 and will drift.
