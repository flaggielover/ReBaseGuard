# P9 adversarial review

Every attack in prompt §21, plus attacks P9 raised against itself. Verdicts:
`SURVIVES` · `NARROWED` · `REJECTED` · `OPEN`.

Revisions were made **only** to P9-owned artifacts. No historical science was
rewritten.

---

## A1 — Are any `PARTIAL` priorities being used as `CLOSED`? · **NARROWED**

The attack landed, in the strongest possible place: **the campaign prompt itself
asserts `P6 = CLOSED`**, and the repository does not. P9's first substantive act
was to check, and the last independent verdict is `FINAL_P6_VERDICT = PARTIAL`
with `G6`/`G9`/`G12` `PARTIAL`; P6R2b is first-party and says verbatim
"`P6 = CLOSED` is **not** declared here."

**Revision:** every P6 claim is carried at `PARTIAL`-consistent strength, the
ledger section is titled `**PARTIAL**`, `D-10` records the conflict, and
`tests/test_partial_priorities.py` asserts it mechanically. P4 and P5 were
already correctly labelled.

## A2 — Are conditional theorems written as exact? · **SURVIVES (after revision)**

The no-inflation validator is what enforces this, and on its first run it
**failed**, catching `P4-L1` and `P4-R1`. Those were real errors (see A11).
After typing the edges, 0 violations. `P4-T2` is carried in narrowed form only;
`P7-B/C/D` are carried as conditional even though `P5-T7` later supplied the
missing stationary-law existence — because the kernels differ (`X-07`).

## A3 — Are finite-grid findings written universally? · **SURVIVES**

`P5-N1`–`P5-N4`, `P5-F1`, `P3-U1`, `PROJ-L4R13` all carry their grid scope.
P5's own `G3`/`G7`/`G9` failure — universal language over finite-grid Monte
Carlo — is carried as a `NEGATIVE_RESULT`, not paraphrased away. `MODEL_SCOPE_MAP`
leaves 31 cells `UNKNOWN` rather than extrapolating.

## A4 — Are local boundaries written operationally? · **SURVIVES, and strengthened**

This is the project's central hazard and P9 found **no** instance of
`rho < rho_c` presented as a safety rule anywhere in the repository. P6's
pre-design even registers it as failure mode `F15` and exclusion `X1`.

P9 strengthens the position: `P9-T2` proves that degradation is present at
`rho = 0`, strictly below `rho_c`, where the local map is maximally stable —
so no `rho` threshold can be an operational boundary. The empirical complement
(`X1`) is that the measured ARL optimum sits `1.25x`–`4.1x` **above** `rho_c`.

## A5 — Are detector transfers unsupported? · **SURVIVES**

No transfer is claimed. `P3-N2`'s SR-below-CUSUM ordering is explicitly "an
empirical ordering of the two frozen specializations only — not a
detector-universal theorem". `MODEL_SCOPE_MAP` §2 marks every third-detector
cell `UNKNOWN` and records that the frozen SR threshold is **Gaussian-only**.
Claude's provisional P8 report that detector transfer is *not* established is
quarantined — P9 does not even use it as a negative premise.

## A6 — Are stationary claims applied to adaptive kernels? · **SURVIVES**

`X-07` is dedicated to this. `P5-T7` is per fixed `(D,m,rho)`; `P6-T6B` is a
different kernel for memoryless policies with `rho_max < 1`. Policies that read
the detector state are `OUT_OF_SCOPE` — outside the hypothesis class, not merely
unproved.

## A7 — Are P6 novelty claims inflated? · **SURVIVES**

`P6-NOV` is `NOT_ESTABLISHED`; P6's own audit says `ALGORITHMIC_NOVELTY =
OVERLAPPING` and names adaptive EWMA as the closest prior art. `NOVELTY_AUDIT.md`
reproduces that unsoftened and adds nothing. P9 ran no new search and claims no
novelty for itself.

## A8 — Are negative results omitted? · **SURVIVES**

Nine `NEGATIVE_RESULT` and four `NOT_ESTABLISHED` claims are in the ledger at
full prominence. `RESULTS.md` §8 leads with what was *not* resolved.
`tests/test_document_consistency.py` fails if any `OPEN`/`CONTRADICTION`
discrepancy is missing from `LIMITATIONS.md`.

## A9 — Are P3/P7/P8 discrepancies unresolved? · **OPEN**

Partly, and P9 says so. `D-01` (P2 vs P4's re-run) is `CONSISTENT_WITH_MC` but
its literal gate still fails. `D-13` (P5-T11's `ACF1` residual at up to 16 chain
SE) is `OPEN`. `D-14` (model-class transfer) is blocked on P8. P9 does not claim
to have resolved these.

## A10 — Are model-class claims broader than evidence? · **SURVIVES**

31 `UNKNOWN` cells, the largest category after `PROVED`. Every non-Gaussian
column is `UNKNOWN` except where P4's theorem or Stage-D's calibration already
speaks, and `G13` tests that no scope-map cell was filled from P8.

## A11 — Are historical frozen failures being rewritten? · **SURVIVES**

`P4-F1/F2/F3` and `P5-F1` are carried as failures. `P4-R1` *diagnoses* `P4-F1`
without the gate passing — and this is precisely where P9's own validator caught
P9 modelling it as a `premise` edge, which would have let a resolved anomaly
propagate as if it were a passed gate. It is now a `diagnoses` edge. The
protected-tree test covers 2217 files.

---

## Attacks P9 raised against itself

## A12 — P9 has no frozen definition, so is it self-authorised? · **OPEN, disclosed**

Yes, and this is the most serious objection to the campaign. `P9_DEFINITION_AUDIT.md`
§2.1 states it in the first substantive section rather than burying it, and
`LIMITATIONS.md` §1 repeats it: an adjudicator who rejects the prompt's authority
to constitute a priority should read this as a synthesis *audit*, not a closure
step. Every artifact is written so that reading survives. P9 declares no status
but its own, and issues no verdict at all.

## A13 — P9's gates were written after its experiments · **NARROWED, disclosed**

True. `EXPERIMENT_PROTOCOL.md` §0 tabulates exactly what was and was not
pre-committed: the A1–A3 tolerances were hard-coded in the script before
execution and the seed rule is deterministic, but A4–A6 had **no** pre-set
threshold and `CLOSURE_GATES.md` came afterwards.

**Revision:** the gates were deliberately restricted to
verifiable-by-inspection artifact properties rather than numerical thresholds
P9 could have tuned to its own results. This is the same defect P3 was flagged
for (`P3-LIM1`), so P9 discloses rather than repeats it.

## A14 — Did P9 discard an inconvenient computation? · **SURVIVES**

The first A6 mixture used 21-node Gauss-Hermite and returned `134.19` against a
measured `82.08`. It was replaced by an 81-point half-grid, which agrees. That
replacement is reported in three places (`CROSS_PRIORITY_REPRODUCTION.md` §A6,
`EXPERIMENT_PROTOCOL.md` §4, `STATISTICAL_AUDIT.md` §8) with its diagnosis,
rather than deleted. Likewise `D-12`: P9 reports both the unfavourable `452.55`
and the favourable `467.6`.

## A15 — Is `P9-T1` dressed up? · **NARROWED**

It was. An early draft framed it as a theorem; the mathematics is a minimum over
a DAG.

**Revision:** `THEORY.md` §1.1 now opens by saying so, labels it `PROPOSITION`,
states that its soundness reading is a *policy* rather than a proved
metatheorem, and directs a reader wanting mathematical content to `P9-T2`
instead.

## A16 — Is `P9-T2` really exact, or is a premise smuggled in? · **SURVIVES**

The premise to check is `A` even and non-increasing in `|e|`, taken from
`P7-A`. Strictness additionally needs `A` non-constant, which P9 **proves** from
the frozen recurrences rather than assuming: `A(0) > 1` because an alarm at
`t=1` requires `|Z_1| >= 5.5` (CUSUM), and `A(e) -> 1` because
`{X_1 <= e - 5.5}` forces an immediate alarm and has probability `-> 1`. All
three premises (`P5-T1`, `P5-T7`, `P7-A`) are `EXACT_THEOREM`, so
`rho(P9-T2) = 6` and the bound is not violated. The monotonicity premise was
additionally corroborated numerically (0 violations at 3 SE over 320
comparisons).

## A17 — Did P9 contaminate Codex's P8 work? · **SURVIVES**

P9 ran in a separate worktree on a separate branch from the anchor commit. The
P8 tree was untracked at branch point, so it is not present on `p9-research` at
all. P8 files were read read-only from the `main` worktree; nothing was copied,
merged or cherry-picked. P8 status was checked **twice** in the whole campaign —
no watcher, no poll loop.

---

## Summary

| verdict | attacks |
|---|---|
| `SURVIVES` | A2, A3, A4, A5, A6, A7, A8, A10, A11, A14, A16, A17 |
| `NARROWED` | A1, A13, A15 |
| `REJECTED` | — |
| `OPEN` | A9, A12 |

Four revisions were made to P9-owned artifacts as a result: the P6 status
correction (A1), the edge retyping (A2/A11), the gate restriction and disclosure
(A13), and the `P9-T1` reframing (A15).
