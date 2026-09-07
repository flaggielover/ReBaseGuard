# P4ZA Phases 1–2 — may historical evidence be composed, and for which cells?

This is a governance question and it is answered before any new number is
produced, so that the answer cannot be shaped by what a rerun happens to show.

## 1. The two candidate sources

| source | what it is | status |
|---|---|---|
| **P4X** | historical Route A + Route B, per-cell disposition against the *same* frozen gate | 88/96 PASS, 0 FAIL, 8 `PRECONDITION_NOT_MET`; obligation C2 `INCOMPLETE`, C1/C3/C4/C5/C6/C7 `PASS` |
| **P4Z** | RB-SCORE + RB-MAP, full 200 blocks, one producer hash, one runtime hash | 44 PASS, 0 FAIL, 52 INCONCLUSIVE; independent adjudication 44/44 |

## 2. The composition rule, stated before it is applied

> **Rule C.**  Historical evidence for a cell may serve as that cell's
> authoritative governed disposition if and only if all six hold:
>
> **C1 — identical claim.**  Same estimand `Gamma_{D,m,f}`, same detector and
> threshold, same window convention, same `m`, same residual convention.
>
> **C2 — identical gate.**  Same acceptance criterion and the same numerical
> thresholds, neither relaxed nor reinterpreted.
>
> **C3 — the producing campaign's governance defects are individually
> inapplicable to that cell**, shown cell by cell from the producing campaign's
> own ledger — not argued in aggregate.
>
> **C4 — the producing estimator's known validity limits do not bind for that
> cell's family**, shown from the frozen theorem rather than from agreement of
> results.
>
> **C5 — the cell's own precision precondition was met** in the producing
> campaign, on its own recorded terms.
>
> **C6 — no later campaign produced evidence that contradicts it.**
>
> Failing any of these, the cell needs new evidence.  A cell is never upgraded
> from `INCONCLUSIVE` to `PASS` by argument alone.

Rule C is deliberately strict on C3 and C4: "P4X passed it" is not a reason,
because the whole point of the P4Y and P4Z campaigns was that P4X's
architecture had real defects.  What matters is whether *those specific
defects* can touch *this specific cell*.

## 3. Applying C3 — the historical defects, cell by cell

The defects on record against the historical architecture, from P4Z's own
`FAILURE_TAXONOMY.md` and P4Y's Pilot-4 regression:

| defect | mechanism | does it touch the 52? |
|---|---|---|
| `F-01`/`F-03` infinite second moment of the Route-A summand; batch SE estimates a quantity that does not exist | requires `E[eps^2] = infinity` | **No.** All 52 cells are `gaussian`, `laplace`, `logistic`, `skewnormal4`. Every one has all polynomial moments finite. The defect is specific to `t1p5`. |
| `F-02` Route B as a rare-event estimator of a heavy-tailed jump | same heavy-tail requirement | **No**, same reason. |
| `F-04` the unadjudicable top-up state | requires a stage-2 top-up | **No.** Audited from P4X's own ledger: **0 of 52** cells took a stage-2 top-up. |
| `F-05` `N_req` targets an expectation, so top-ups are undersized | requires a top-up | **No**, same audit. |
| P4Y Pilot-4 sharding defect (8 805 vs 8 801 blocks) | requires sharding | **No.** Audited: **0 of 52** cells were sharded. The only sharded configuration in the whole P4X campaign is `frozen/cusum@5/t1p5`, which is a *residue* configuration and has since been independently re-qualified by P4Z. |
| `F-06` single-error `z` statistic | a P4 gate defect, already repaired by P4X's own C5 | not applicable to C2 cell dispositions |

Every one of the 52 cells is stage-1 only, single shard, with **both routes
recording `meets_r_star = True`** — which is also C5.

## 4. Applying C4 — is the historical estimator valid on these families?

P4Z's `OLD_ESTIMATOR_DIAGNOSIS.md` §1 is explicit: *"The old estimator is
correct.  It is only unusable."*  Unbiasedness was never in question; what P4Z
rejected was the **uncertainty**, because for an infinite-variance summand the
reported standard error estimates something that does not exist.

For the four families in the 52, the frozen `families.py` records
`finite_abs_moment_order = inf`, and the bounded-survival lemma plus discharge
lemma L1 give the historical summand every moment.  So on these cells the
historical batch standard error estimates a quantity that exists, and the
historical routes are valid estimators with valid uncertainty.

**A caveat recorded rather than argued away.**  P4Z's frozen checkpoint lists
"historical Route A" and "historical Route B" under `REJECTED_ESTIMATORS`
without a family qualification, even though the *stated cause* for each is
family specific (`F-01`, `F-02`).  P4ZA does not reinterpret that list.  It
takes the conservative reading: **a P4Z rejection stands**, and Rule C is
therefore *not* used to import P4X evidence as the sole authority for any cell.
See §6.

## 5. The K7 cells need no import at all

For the 20 `K7` cells this turns out to be moot, and that is the cleanest fact
in this document.

P4Z ran **both** routes to the full frozen 200 blocks on every one of them.
Setting aside K7 — which is a precondition P4Z invented, not a gate the frozen
P4 protocol contains — P4Z's own in-house evidence satisfies the frozen gate:

```text
relative discrepancy <= 0.03   20 / 20   (worst 0.0022)
|z| on Monte Carlo error <= 4  20 / 20   (worst 0.846)
both routes meet r*            20 / 20
```

and P4Z's RB-SCORE agrees with P4X's Route A to a worst two-sample `z` of
**1.256** across all twenty.

So the K7 cells are not a question of importing history.  They are a question
about the *uncertainty treatment* P4Z added on top of the frozen gate, which
`K7_DIAGNOSIS.md` shows was computed from non-adjacent ladder pairs without the
factor of 15 the Richardson relation requires.  That is a P4ZA question with a
P4ZA answer, and it is answered with new frozen evidence, not with composition.

## 6. The ruling

```text
COMPOSITION_USED_AS_SOLE_AUTHORITY = NO

K7 cells (20): new P4ZA evidence, from a re-derived and re-calibrated ladder
               and a corrected truncation-residual rule.  P4X and the existing
               P4Z 200-block data are recorded as CORROBORATION only.

K3 cells (32): new P4ZA evidence, from full 200-block runs under a properly
               derived regime envelope.  P4Z only ever ran 20 blocks on these,
               so there is no P4Z full-precision evidence to compose, and P4X
               is corroboration only.
```

Rule C is satisfied by the 52 cells on C1, C2, C3, C4 and C5.  P4ZA declines to
rely on it anyway, because of the caveat in §4 and because the cost of *not*
relying on it is small: the recomputation these cells need is roughly one
CPU-hour, against a campaign that has already spent 2.38.

That is the whole justification.  When honest evidence is cheap, buy it rather
than argue for it.  Rule C is documented in full because the reasoning must be
on the record whether or not it is leaned on, and because a future campaign
facing an expensive recomputation may legitimately need it.

**Corroboration is not disposition.**  P4X and the existing P4Z data appear in
the coverage graph as `corroborating_evidence`, and no cell's disposition is
derived from them.
