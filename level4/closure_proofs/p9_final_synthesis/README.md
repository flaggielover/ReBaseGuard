# Level-4 Priority 9 — final synthesis

**Authoritative independent verdict: `P9 = PARTIAL`.** The retrospective
synthesis core survives, but the submitted exact P9-T2 classification, SR
reproduction, and A5/A6 reproducibility do not. See
[`INDEPENDENT_ADJUDICATION.md`](INDEPENDENT_ADJUDICATION.md). The
`CLOSED_CANDIDATE` block below is retained as the campaign's submitted status,
not the authoritative verdict.

**Status: `P9 = CLOSED_CANDIDATE`** — 14 of 14 preregistered gates pass.
**This is a Claude-side candidate only. It is not authoritative and must not be
promoted to `CLOSED` without independent adjudication.**

**Read `P9_DEFINITION_AUDIT.md` first.** Its §2 records the fact that governs how
everything else here should be read:

> At the anchor commit the repository contained **zero** statements defining a
> Level-4 Priority 9.

P8 had four frozen statements that literally defined it. P9 has none. All 11
occurrences of `P9` in the repository are P5's *premise* label for
`m`-monotonicity — the same collision P8 recorded as its `U1`, but total. So P9
is a **prompt-constituted synthesis priority over a repository-constituted
evidence base**, and every scope item is `PROMPT_DERIVED`. An adjudicator who
rejects the prompt's authority to constitute a priority should read this
namespace as a *synthesis audit of P1–P8*; every artifact is written so that
reading survives.

**In one paragraph.** P9 assembles the 65 scientifically important claims of
P1–P8 into one ledger that does not flatten evidence classes, and finds that a
dependency graph of this project drawn with **untyped edges is unsound** — a
Lean or Arb layer is a fact *about* an artifact, neither bounded by nor
licensing the science it verifies. It proves one exact theorem, `P9-T2`: at
`rho = 0` — strictly below `rho_c`, where the local map is *maximally* stable —
the stationary ARL is `E[A(e)] < A(0)`, so **no threshold in `rho` can be an
operational safety boundary**. This upgrades P7's frozen-criterion negative
result to an exact statement using only claims already at `EXACT_THEOREM`. Its
empirical complement is sharper still: the measured ARL optimum sits
`1.25x`–`4.1x` **above** `rho_c`, inside the locally repelling region. P9
independently reproduces the P3 boundary algebra exactly, the P5 raw-mean
identity to `8.9e-16`, and P7's cycle-2 collapse (`5.63–8.83` against a
published `5.6–9.4`); investigating one apparent mismatch produced a new finding
(`P9-N1`) that the approach to stationarity is **oscillatory over ~10 cycles**,
so finite-horizon ARLs depend materially on the burn-in convention. Three
cross-priority discrepancies remain **`OPEN`** and are named.

## Read in this order

| file | what it is |
|---|---|
| [`P9_DEFINITION_AUDIT.md`](P9_DEFINITION_AUDIT.md) | where P9's scope comes from — and the finding that nothing defines it |
| [`CLAIM_LEDGER.md`](CLAIM_LEDGER.md) · [`.json`](CLAIM_LEDGER.json) | every P1–P8 claim at its authoritative strength; 65 claims, 0 validation findings |
| [`THEOREM_DEPENDENCY_GRAPH.md`](THEOREM_DEPENDENCY_GRAPH.md) · [`.json`](THEOREM_DEPENDENCY_GRAPH.json) | the DAG, with the three edge types that make it sound |
| [`THEORY.md`](THEORY.md) | `P9-T1` (proposition, honestly labelled) and `P9-T2` (exact) |
| [`DEFINITION_CROSSWALK.md`](DEFINITION_CROSSWALK.md) | ten places the same name means different things — start at X-02 and X-05 |
| [`DISCREPANCY_REGISTER.md`](DISCREPANCY_REGISTER.md) | 15 tensions; 12 resolved, **3 `OPEN`** |
| [`CROSS_PRIORITY_REPRODUCTION.md`](CROSS_PRIORITY_REPRODUCTION.md) | independent replay of the dependency chain |
| [`MODEL_SCOPE_MAP.md`](MODEL_SCOPE_MAP.md) | what is known where — **31 `UNKNOWN` cells** |
| [`RESULTS.md`](RESULTS.md) | what P9 found |
| [`P8_TO_P9_RECONCILIATION.md`](P8_TO_P9_RECONCILIATION.md) | the authoritative `P8 = FAIL` verdict and its effect (none, by design) |
| [`STATISTICAL_AUDIT.md`](STATISTICAL_AUDIT.md) | uncertainty, and the computation P9 discarded |
| [`CLAIM_LANGUAGE_POLICY.md`](CLAIM_LANGUAGE_POLICY.md) | evidence class → permitted wording |
| [`NOVELTY_AUDIT.md`](NOVELTY_AUDIT.md) | conservative; P9 ran no new search and claims no novelty |
| [`ADVERSARIAL_REVIEW.md`](ADVERSARIAL_REVIEW.md) | 17 attacks, 3 narrowed, 2 open |
| [`LIMITATIONS.md`](LIMITATIONS.md) | what P9 does not establish |
| [`EXPERIMENT_PROTOCOL.md`](EXPERIMENT_PROTOCOL.md) | **§0 is a temporal-integrity disclosure** |
| [`CLOSURE_GATES.md`](CLOSURE_GATES.md) | the gates, and the verdict rule fixed before P8's outcome |
| [`CODEX_HANDOFF.md`](CODEX_HANDOFF.md) | what to attack, and how to replay it |

## Authoritative statuses P9 carries

| priority | status | how P9 uses it |
|---|---|---|
| P1, P2, P3, P7 | `CLOSED` | premises, at their stated conventions |
| P4, P5 | `PARTIAL` | surviving theorems only, at their adjudicated tier; frozen gate failures carried as failures |
| P6 | `CLOSED`, scope-bound | closure is **not** novelty; `P6-NOV` stays `NOT_ESTABLISHED` |
| **P8** | **`FAIL`** | quarantined. §16 permits four tiers; **P9 uses none** and keeps its stricter pre-committed rule. |

## Scope discipline

* P9 modifies **no** artifact outside this directory. `results/protected_tree_manifest_pre.json`
  records 2217 protected files at the anchor commit `ffe23a6`; gate `G11` and
  `tests/test_protected_scope.py` re-check them.
* P9 ran in an isolated worktree (`/Users/suzhe/ReBaseGuard-p9`, branch
  `p9-research`) so that concurrent P8 adjudication in `main` could not be
  disturbed. P8 status was checked **twice** in the whole campaign — no watcher,
  no poll loop. After the P8 verdict landed, the worktree was fast-forwarded onto
  authoritative main `5411e2c`; `p9-research` carries no commits of its own.
* P9 **reopens nothing**. It declares no status but its own.
* P9 introduces **no new scientific premise**. `P9-T2` is assembled entirely
  from claims that already existed at the anchor commit.

## Reproduce

```bash
cd level4/closure_proofs/p9_final_synthesis && P9_EMIT_MD=1 python3 experiments/build_ledger.py
```

```bash
cd level4/closure_proofs/p9_final_synthesis && python3 -m pytest tests/ -q
```
