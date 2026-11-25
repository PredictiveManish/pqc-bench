# PQC-Eval — Standards & Real-World Grounding

Every fact used in the task suite traces to a primary source below. Verified
2026-11-25. The per-task mapping lives in `provenance/sources.yaml`; the
validator (`scripts/validate_sources.py`) fails if any task lacks provenance.

> This file states what the sources say. It is not legal or compliance advice;
> deadlines and scopes change — always confirm against the current text.

## 1. NIST — algorithm standards

- **FIPS 203** (ML-KEM, from CRYSTALS-Kyber), **FIPS 204** (ML-DSA, from
  CRYSTALS-Dilithium), **FIPS 205** (SLH-DSA, from SPHINCS+) were approved
  13 Aug 2024 and effective 14 Aug 2024.
  https://www.nist.gov/news-events/news/2024/08/announcing-approval-three-federal-information-processing-standards-fips
  https://csrc.nist.gov/pubs/fips/203/final
  https://csrc.nist.gov/pubs/fips/204/final
  https://www.federalregister.gov/documents/2024/08/14/2024-17956/announcing-issuance-of-federal-information-processing-standards-fips-fips-203-module-lattice-based
- **FIPS 206** (FN-DSA, from FALCON) is still in development — not final.
  (Same NIST announcement: "NIST is also developing a FIPS … derived from FALCON".)
- **HQC** was selected on 11 Mar 2025 as a *backup* KEM (code-based, different
  math from ML-KEM); draft expected ~1 year, final ~2027. ML-KEM remains the
  primary recommendation.
  https://www.nist.gov/news-events/news/2025/03/nist-selects-hqc-fifth-algorithm-post-quantum-encryption
  https://csrc.nist.gov/News/2025/hqc-announced-as-a-4th-round-selection
  https://nvlpubs.nist.gov/nistpubs/ir/2025/NIST.IR.8545.pdf

## 2. NIST — transition timeline (IR 8547, final Oct 2026)

- NIST will **deprecate** quantum-vulnerable public-key crypto **after 2030** and
  **disallow** it under NIST standards **after 2035**.
- Accelerated federal deadlines (EO 14412 / OMB M-26-15): high-value assets must
  adopt PQC key establishment by **31 Dec 2030** and signatures by **31 Dec 2031**.
- Federal agencies must support **TLS 1.3 by 2 Jan 2030**.
- NSM-10 sets 2035 as the overall federal migration target.
  https://nvlpubs.nist.gov/nistpubs/ir/2026/NIST.IR.8547.pdf
  https://www.nist.gov/news-events/news/2026/10/nist-report-provides-guidelines-transition-post-quantum-cryptography

## 3. NSA — CNSA 2.0

- Required algorithms: **ML-KEM-1024** (key establishment), **ML-DSA-87**
  (signatures), **LMS / XMSS** per NIST SP 800-208 (software/firmware signing),
  AES-256, SHA-384/512.
- Timeline (exclusive use): software/firmware signing and traditional networking
  equipment by **2030**; browsers, servers, cloud, operating systems, niche
  equipment by **2033**; overall NSS transition by **2035**. New NSS acquisitions
  CNSA 2.0-compliant from **Jan 2027**.
- Note: X25519MLKEM768 (what browsers negotiate) is *not* CNSA 2.0 — that suite
  names ML-KEM-1024.
  https://media.defense.gov/2025/May/30/2003728741/-1/-1/0/CSA_CNSA_2.0_ALGORITHMS.PDF
  https://pqcstatus.com/articles/cnsa-2-0-timeline/

## 4. India — CERT-In, TEC, DST / National Quantum Mission

- **CERT-In**, Technical Guidelines on SBOM, **QBOM & CBOM**, AIBOM, HBOM,
  Version 2.0, 09 Jul 2025: organisations shall maintain Cryptographic BOM and
  Quantum BOM; suppliers must provide them; aligned with NIST/ETSI/CERT-In.
  https://cert-in.org.in/PDF/TechnicalGuidelines-on-SBOM,QBOM&CBOM,AIBOM_and_HBOM_ver2.0.pdf
- **CERT-In + SISA whitepaper**, "Transitioning to Quantum Cyber Readiness",
  launched by MeitY on 11 Jul 2025.
  https://www.pib.gov.in/PressReleseDetailm.aspx?PRID=2144023
  https://documents.sisa.ai/whitepaper/transitioning-to-quantum-cyber-readiness-a-white-paper-by-cert-in-in-collaboration-with-sisa.pdf
- **TEC** technical report "Migration to Post Quantum Cryptography",
  **TEC 910018:2025**, Release 1.0, Jan 2025.
  https://tec.gov.in/pdf/TR/Final%20technical%20report%20on%20migration%20to%20PQC%2028-03-25.pdf
- **DST / National Quantum Mission Task Force** (chaired by C-DOT CEO
  Dr. Rajkumar Upadhyay; sub-groups TEC and DSCI), "Quantum Safe Ecosystem in
  India": national testing & certification framework with assurance levels
  **L1–L4** (validity 3–10 years), Tier-1/Tier-2 labs by **Dec 2026**, and a
  phased migration — **CII sectors: Foundations 2027, High Priority 2028, Full
  adoption 2029**; other enterprises **2028 / 2030 / 2033**. The report states this
  framework is **not itself a regulatory mandate** — sectoral regulators set
  timelines and enforcement. "Assume-breach" principle for HNDL.
  https://www.dst.gov.in/static/uploads/2026/07/dba5f97fa8f4c8db5ef668306548a470.pdf
  https://www.thehindu.com/news/national/critical-sectors-must-have-quantum-safe-encryption-urges-task-force/article71029610.ece
  https://tec.gov.in/pdf/TR/Quantum-Safe-Ecosystem-in-India_260514_174510_.pdf

## 5. Europe — BSI, ANSSI, ENISA

- **BSI TR-02102-1** (version 2026-01, 23 Jan 2026): classical asymmetric key
  agreement alone recommended only until **end 2031** (**end 2030** for
  highest-sensitivity); classical signatures alone until **end 2035**; recommends
  **hybrid** use. PQC recommendations include ML-KEM, FrodoKEM, Classic McEliece
  (KEM) and ML-DSA, SLH-DSA, LMS/HSS, XMSS/XMSS-MT (signatures). BSI does not
  recommend QKD at this time.
  https://www.bsi.bund.de/SharedDocs/Downloads/DE/BSI/Publikationen/TechnischeRichtlinien/TR02102/BSI-TR-02102.pdf?__blob=publicationFile
  https://www.bsi.bund.de/DE/Service-Navi/Presse/Pressemitteilungen/Presse2026/260211_Ende_klassischer_Verschluesselungsverfahren.html
- **ANSSI** (position paper, Mar 2022): 3-phase roadmap — Phase 1 hybrid as
  defence-in-depth; Phase 2 (≥2025) hybrid with claimed PQ security; Phase 3
  (≥2030) optional standalone PQC. Hybridation mandatory in phases 1–2;
  hash-based signatures are an exception (may be used without hybridation).
  https://messervices.cyber.gouv.fr/documents-guides/EN_Position.pdf
- **ENISA**: PQC integration guidance (2022); hybridisation standardisation
  status report (Apr 2026); supports an EU-coordinated transition roadmap.
  https://www.enisa.europa.eu/news/enisa-news/post-quantum-cryptography-anticipating-threats-and-preparing-the-future
  https://certification.enisa.europa.eu/document/download/02f54596-6a99-4c9e-88c4-8c711ebff9c1_en

## 6. UK — NCSC

- Migration milestones: by **2028** complete discovery and an initial migration
  plan; by **2031** complete highest-priority migration; by **2035** complete
  migration of all systems.
  https://www.ncsc.gov.uk/guidance/pqc-migration-timelines

## 7. Real-world deployments

- **TLS hybrid key exchange**: `X25519MLKEM768`, TLS codepoint **0x11ec**
  (recommended); the earlier `X25519Kyber768Draft00` **0x6399** is obsolete.
  Chrome 131+ enables ML-KEM by default; Cloudflare deployed it and reports a
  large share of traffic protected.
  https://developers.cloudflare.com/ssl/post-quantum-cryptography/
  https://security.googleblog.com/2024/09/a-new-path-for-kyber-on-the-web.html
- **Measurement (IMC 2026 study)**: among ~684k domains answering all rounds,
  post-quantum key exchange by default rose from 31.26% to 49.22%; all used
  X25519MLKEM768; **0% PQ signature adoption** was observed; Cloudflare + Fastly
  account for ~70% of observed deployment.
  https://cacm.acm.org/news/post-quantum-tls-finished-the-easy-half/
- **OpenSSH**: `mlkem768x25519-sha256` added in **9.9** (19 Sep 2024) and made
  the **default** in **10.0** (9 Apr 2025); `sntrup761x25519-sha512` has been
  default since **9.0** (2022); **10.1** warns on non-PQ key exchange.
  https://www.openssh.org/txt/release-9.9
  https://www.openssh.org/txt/release-10.0
  https://www.openssh.org/pq.html
- **Signal PQXDH** (Sep 2023): combines X25519 with CRYSTALS-Kyber; an attacker
  must break both.
  https://signal.org/blog/pqxdh/
- **Apple iMessage PQ3** (Feb 2024, iOS 17.4): Kyber/ML-KEM, hybrid, periodic
  post-quantum rekeying; Apple describes it as "Level 3" security; formally
  verified (TAMARIN).
  https://security.apple.com/blog/imessage-pq3/
  https://www.usenix.org/system/files/usenixsecurity25-linker.pdf

## 8. Notes on interpreting this

- Dates differ by jurisdiction and by asset class; a single "deadline" is wrong.
  Federal US, CNSA, UK, EU and India all differ.
- "Hybrid" means combining a classical and a post-quantum algorithm so the result
  is secure if *either* holds — recommended by BSI, ANSSI, and used by TLS, SSH,
  Signal, iMessage.
- ML-KEM-768 is what browsers negotiate; CNSA 2.0 requires ML-KEM-1024. A product
  can be "post-quantum" without being CNSA 2.0 compliant.
