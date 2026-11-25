# Launch kit

Naming, publishing, and copy. Written to be used, not admired.

---

## Is it a benchmark?

Yes — but be precise about which stage it is, because "benchmark" gets you
scrutiny.

What makes it one: a fixed task set, a scoring spec, machine-checkable ground
truth, and integrity gates that prove the scorers work.

What it still needs before you put numbers in a headline: **baseline results from
named models**, a **held-out split**, and ideally a **leaderboard**. Until then,
call it *"a benchmark harness with verified ground truth — baselines in progress."*
That sentence is defensible. "State-of-the-art PQC benchmark" is not, yet.

---

## Name

**PQCBench** — recommended. Searchable, obvious to the community, reads well as a
repo (`pqcbench`), a package, and a leaderboard row.

Alternatives if `PQCBench` is taken on GitHub/PyPI/HuggingFace:

- **PQConform** — leans into the conformance angle (standards + capability).
  Distinctive; signals it's not another "can it do lattice math" test.
- **HNDL-Bench** — memorable, ties to harvest-now-decrypt-later. Narrower.
- **DeployedBench** — emphasises real deployments over textbook crypto.

Check availability on GitHub, PyPI and HuggingFace before committing. Keep the
subtitle that does the real work: *"the conformance-first PQC benchmark."*

---

## Where to push it

| Where | What goes there | Why |
|---|---|---|
| **GitHub** | the repo + CI gates | the canonical home; people read code |
| **HuggingFace Datasets** | `tasks/` as a dataset | discoverability for eval people |
| **HuggingFace Space** | leaderboard (Gradio) | where benchmarks actually get compared |
| **Zenodo** | tagged release | a DOI so it's citable |
| **PyPI** (optional) | `pip install pqcbench` | lowers the barrier to running |
| **Papers with Code / arXiv** | a short write-up | only if you want academic uptake |
| **pqc-forum / IETF PQUIP** | an announcement | the people who care about correctness |
| **r/cryptography, HN** | the post | traffic, and brutal but useful feedback |

Order: GitHub → Zenodo DOI → HuggingFace dataset → Space → then announce. Don't
announce before the repo is public and CI is green.

---

## X (Twitter)

### Main post (single)

> Ask a model when to migrate to post-quantum crypto and you get a confident
> answer. It's probably wrong for your country.
>
> US high-value assets: 2030. India CII: 2029. UK: 2035.
>
> So I built PQCBench — 57 tasks, each traced to a primary source. No source, no
> task.
>
> Repo + how to run it 👇

### Thread version

1/ Ask a model when to migrate to PQC. You get a confident, well-formatted
answer. It is probably wrong for your country.

There is no single deadline. US federal high-value assets: key establishment by
2030. India's CII sectors: full adoption by 2029. UK: plan by 2028, finish by
2035. BSI: classical key agreement alone ends 2031.

2/ Meanwhile the deployed reality is lopsided. In a 2026 measurement, ~49% of
TLS domains negotiated post-quantum key exchange — all X25519MLKEM768, codepoint
0x11ec. Post-quantum *signatures*: ~0%.

Key exchange and signatures are two different migrations, and almost nobody
says so.

3/ So I built PQCBench. 57 tasks, six tiers: the algorithms, the standards, real
FIPS 203 debugging, and scenario questions like "your bank is in India, what
applies?" and "your SSH fleet runs 9.6, are you exposed?"

The rule: every task is bound to a primary source. No source URL → the build
fails. It killed half my drafts.

4/ What's verified: ground truth matches kyber-py and dilithium-py exactly; a
gold/null/buggy gate proves the scoring isn't broken.

What's missing: I haven't run a frontier model yet — no API budget where I built
it. That's next, and I'd rather say it than post a chart.

Try to break a task. Link below.

---

## LinkedIn

> Ask a model when your organisation should migrate to post-quantum cryptography
> and you'll get a confident, well-structured answer.
>
> It will probably be wrong for your country.
>
> The US federal deadline for high-value assets (key establishment) is 2030, with
> disallowance after 2035. India's critical infrastructure sectors are targeting
> full adoption by 2029, and CERT-In's guidelines want a Cryptographic Bill of
> Materials. The UK says plan by 2028, finish by 2035. BSI ends classical key
> agreement on its own at end-2031. ANSSI makes hybrid mandatory.
>
> There is no single "PQC migration deadline." A model that can recite
> Module-LWE for ten paragraphs can still get every one of those wrong.
>
> That gap is what I wanted to measure, so I built PQCBench.
>
> 57 tasks across six tiers: the algorithms, the standards, debugging real
> FIPS 203 code, and scenario questions — a bank in India, an SSH fleet on 9.6,
> the fact that post-quantum key exchange is everywhere while post-quantum
> signatures are nowhere.
>
> The design rule did most of the work: every task is bound to a primary source.
> If a task has no source URL, the build fails. That single constraint threw out
> every "sounds plausible" question I'd drafted.
>
> What I can stand behind: the ground truth is cross-checked against kyber-py and
> dilithium-py, and a gold/null/buggy gate proves the scorer isn't broken.
>
> What I won't pretend: I haven't scored a frontier model on it yet — no API
> budget in the environment where I built it. Baselines are the next commit.
>
> If you work on LLM evaluation or on PQC migration, I'd value one thing over a
> like: point at a task you think a good model would get right and I got wrong.
> That's the fastest way to make this worth something.
>
> Repo link in the first comment.

---

## What not to say (the slop tells)

Avoid: "I'm thrilled to announce", "game-changer", "revolutionary",
"in today's rapidly evolving landscape", "let that sink in", emoji rockets,
a list of "5 lessons", and ending with "Thoughts?". They signal a template, and
template posts get skimmed past.

What makes these posts read as human: a specific number, a specific country, an
admission of what's missing, and a concrete ask that isn't "engage with me."

---

## Hashtags

Sparingly. On X: `#PQC #cryptography`. On LinkedIn: `#PostQuantum #Cryptography
#LLM`. Three at most — more looks like farming.
