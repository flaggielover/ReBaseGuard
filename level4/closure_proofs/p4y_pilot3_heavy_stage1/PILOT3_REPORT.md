# P4Y PILOT-3 — heavy-tail Stage-1 sizing closure pilot — report

```text
STATUS = PILOT-3 COMPLETE, NON-BINDING
P4Y_BINDING_CHECKPOINT_CREATED = NO
P4Y_PRODUCTION_RUN             = NO

P4_ORIGINAL_VERDICT     = PARTIAL   immutable
P4X_SUCCESSOR_VERDICT   = FAIL      immutable
P4X_SCIENTIFIC_FAILURES = NONE      immutable
P4Y_PILOT1_VERDICT      = NEEDS_ONE_MORE_PRE-FREEZE_PILOT   immutable
P4Y_PILOT2_VERDICT      = NEEDS_ONE_MORE_PRE_FREEZE_PILOT   immutable
```

---

## 1. Immutable history

| | |
|---|---|
| `P4_ORIGINAL_VERDICT` | `PARTIAL` |
| `P4X_SUCCESSOR_VERDICT` | `FAIL` — governance and sampling integrity, not a scientific contradiction |
| `P4X_SCIENTIFIC_FAILURES` | `NONE` — 88/96 binding PASS, 0 scientific FAIL, 8 `PRECONDITION_NOT_MET` |
| `P4Y_PILOT1_VERDICT` | `NEEDS_ONE_MORE_PRE-FREEZE_PILOT` |
| `P4Y_PILOT2_VERDICT` | `NEEDS_ONE_MORE_PRE_FREEZE_PILOT` |

Neither earlier pilot is relabelled by this one. P4X is absent from this
branch; Pilot-1's and Pilot-2's namespaces are present, imported read-only,
and unmodified.

## 2. The exact Pilot-2 blocker

Pilot-2 closed every governance question but one. Its endpoint held perfectly
— valid disposition 1.0000 at every cap under both kappas, Clopper–Pearson
lower bound 0.9937 over 472 fresh replicates per point, zero invalid
dispositions, shard sum / 8801-regression / collision audit / shard-invariant
identity all PASS, no third state, no scientific leakage — and yet **no
cap/kappa pair was selectable**. Its best pair (`kappa = 0.5`, `12x` nominal
`B1`) gave attainment 0.9301 against a 0.95 floor, `PRECISION_LIMITED` 0.0699
against a 0.05 ceiling, and a conservative projection of 108.25 CPU-hours
against a 45 h limit.

Pilot-2 localised the cause and it was neither the cap nor the staged rule:

> at the historical heavy-tail reference of ~4 blocks, `relSE_ref` fell below
> its true value in 95–100 % of fresh draws with a median of 34–41 % of truth;
> Stage-1 raises that estimate to the power `1/kappa`, so it bought a median
> 11–17 % of the true requirement.

A sample standard deviation of a heavy-tailed scale is right-skewed: its
**median sits below** the quantity it estimates. Feeding that median-low
statistic into a law that squares it is the whole defect.

## 3. Preregistration hash and temporal ledger

```text
P4Y_PILOT3_PREREGISTRATION = 8dbb7d2ea5dbe6eaad2cfff0d89e44cc6fbdc3af
```

That commit contains the preregistration, all source and all tests, and
**zero files under `results/`** — verified by `git ls-tree --full-tree`.

| | event | evidence |
|---|---|---|
| `T0` | preregistration frozen | `8dbb7d2`, `results/` empty |
| `T1` | code and config frozen | same commit |
| `T2` | first result-bearing execution | 2026-09-04T07:15:32Z, benchmark |
| `T3` | design complete | `results/TEMPORAL_LEDGER.txt` |
| `T4` | validation complete | " |
| `T5` | report complete | " |

## 4. Production mixture — verified mechanically before freezing

From `checkpoint_a.json`, over all `(configuration, route)` strata:

```text
48 strata total
 8 with frozen heavy_tailed = True   -- every one of them t1p5
40 ordinary
the heavy set EQUALS the set that needed stage-1 sizing
```

The frozen mixture is **8 : 40**, and it — not any pilot cell count — weights
the primary rates. Pilot-2's pooled figures over-weighted the hard
subpopulation 5:3; Pilot-3 does not repeat that.

## 5. Heavy-tail class — from pre-existing metadata, not from failure

P4X's frozen `heavy_tail_policy` records
`only_family_requiring_alpha_below_2 = "t1p5"`, with measured per-path tail
index 1.471–1.528 for `t1p5` against a minimum of **2.695** for every other
family. The class is therefore decided by a tail index measured before P4X
ran, and `t1p5` is the only family receiving the treatment. No route was
classified heavy after observing a Pilot-3 precision failure, and a test
asserts the classification against the frozen artifact.

Consequently the heavy-tail reference inflation applies **only** to those 8
strata. The 40 ordinary strata keep their historical reference and the point
estimate — brief §18: do not penalise all 48 to fix 8.

## 6. Strata, cells and the high-quality benchmark

| id | `B_req` | weight | provenance |
|---|---|---|---|
| `S59` | 59 | 2 | `frozen/sr@520.886/t1p5` A — the minimum heavy allocation |
| `S151` | 151 | 2 | `reduced/sr@20/t1p5` B |
| `S215` | 215 | 2 | `frozen/cusum@5/t1p5` B — **18.60 of P4X's 24.75 CPU-hours** |
| `S1784` | 1784 | 2 | `frozen/sr@520.886/t1p5` B — the maximum |
| `ORD` | 160 | **40** | the median ordinary allocation; finite-variance control |

**The high-quality reference benchmark** (brief §8): 8 000 fresh blocks per
primary cell in a `benchmark` namespace no other phase reuses, giving the
block standard deviation a relative uncertainty of
`1/sqrt(2*(8000-1)) = 0.79 %` — small against the 25–60 % effects this pilot
resolves, and **documented rather than assumed**. The Route-B robustness cell
uses 3 000 blocks (1.29 %).

Measured at T2:

| cell | configuration | route | block size | benchmark blocks | block-mean Hill alpha | `sd(s)/s` |
|---|---|---|---|---|---|---|
| `H` | `reduced/cusum@2/t1p5` | A | 5 000 | 8 000 | 4.83 | 0.79 % |
| `O` | `reduced/cusum@2/gaussian` | A | 1 000 | 8 000 | 69.74 | 0.79 % |
| `HB` | `reduced/cusum@2/t1p5` | B | 10 000 | 3 000 | 3.55 | 1.29 % |

All above the frozen 2.5 STOP floor. These indices are secondary diagnostics
and do not redefine the family class or select `kappa`.

## 7. Frozen candidate grids

```text
Bmin       (4 baseline control, 16, 32, 64, 128)   selectable: 16, 32, 64, 128
UCB        point_baseline (control), chi2, t_squared, bootstrap
UCB level  0.95 one-sided, frozen;  bootstrap resamples 2000, frozen
kappa      K1 = 0.5 (leading), K2 = 0.3197278911564626 (control)
caps       (1.25, 1.5, 2.0, 3.0) x the PROJECTED requirement B1
```

## 8. Stage-1 sizing formula

```text
U  = UCB(reference block means at B_ref)        one-sided, level 0.95
B1 = max(8, ceil( B_ref * (U / r*) ** (1/kappa) ))
```

Rounding happens **exactly once, at the logical total-block level** — never
per shard. `B_ref = Bmin` for heavy strata, the historical value for ordinary
strata. The point-estimate allocation is recorded alongside on every
replicate so the two can be compared draw by draw.

## 9. Cap definition

```text
cap_blocks = ceil( multiplier * B1 )
```

anchored to the projected requirement the UCB rule produces, not to a nominal
`B1` that may itself be badly underestimated — the flaw Pilot-2 exposed. It is
fixed before any Stage-1 block executes, so a route whose projection already
exceeds it is `PRECISION_LIMITED` from projected cost alone. An absolute
ceiling of `40 * B_req` bounds pilot cost; an allocation above it is refused
and recorded **INVALID**, counting against the candidate.

## 10. STOP — a result-bearing defect in the frozen design, found after T2

```text
P4Y_PILOT3_STOP_FIRED = YES
validation = NOT RUN
```

Brief §23: *"If a result-bearing semantic bug is discovered: STOP; classify;
do not silently fix-and-continue."* Brief §3: *"If the design fails, report
failure. Do not rescue it."* Both apply. Pilot-3 stopped after design, did not
run validation, and repaired nothing.

### 10.1 What went wrong

`PILOT3_PREREGISTRATION.md` §6 froze the high-quality benchmark's uncertainty
as

```text
relative uncertainty of sd = 1/sqrt(2*(8000-1)) = 0.79 %
```

**That formula assumes normal block means, and for this block-mean law it is
wrong by orders of magnitude.** Measured on the 8 000 benchmark blocks
actually drawn (cell `H`, `m = 1`, the window that governs every heavy
stratum):

| | |
|---|---|
| block-mean sd over 8 000 blocks | 1.56549, on a mean of 2.50174 |
| largest single block mean | 78.24, against a median of 2.49 |
| **share of total squared deviation from the single largest block** | **29.3 %** |
| from the top 5 blocks | 60.2 % |
| from the top 20 blocks | 78.3 % |
| sd across 8 disjoint sub-samples of 1 000 | 0.834 … 2.672, a **3.2× spread** |
| sd over nested prefixes 250→8 000 | 1.25, 1.04, 1.46, 1.48, 1.28, 1.57 — no convergence |

A quantity where one observation in eight thousand carries three tenths of the
variance is not pinned to 0.79 % by eight thousand observations. **The pilot's
"truth" was not a truth.**

### 10.2 Why that is result-bearing, not a reporting bug

The benchmark defines `target(stratum)` and `relSE_true(B_ref)`. Those in turn
define what `ATTAINED` means, what "the requirement" is, and every coverage
and ratio-to-truth figure. The primary comparison — does a UCB remove
systematic under-allocation? — is measured entirely against them. So this is
load-bearing, and brief §23's reporting-bug exemption does not apply.

Concretely, the design phase reports Stage-1 requirement coverage of **0.11 –
0.16** for the UCB rules against **0.06 – 0.15** for the point estimate, and a
point-estimate median ratio to "truth" of **0.29 – 0.51 that barely improves
with `Bmin`** (0.429 at 16 → 0.478 at 128 on `S59`). A consistent estimator
measured against a stable truth does not behave that way. The numbers are
arithmetically correct and governance-wise meaningless: they are a noisy
statistic compared against another draw of the same noisy statistic.

**No selection was made.** Under the frozen criteria, 96 candidates were
evaluated and **0 qualified**; the closest — `Bmin = 16`, `chi2`, `kappa =
0.5`, cap `2×` — failed criterion 4, the per-heavy-stratum floor. That result
stands as recorded, and it is *not* used to conclude anything about the UCB,
because the instrument it was measured with is invalid.

### 10.3 The defect is not merely a pilot-scale artefact

The obvious hope is that this is an artefact of the pilot's 5 000-path blocks
and that production's frozen 250 000-path blocks are well behaved. A
post-STOP diagnostic in a fresh `probe` namespace — **not** an endpoint, and
disclosed as such — says otherwise:

| block size | n | CV | top-1 block's share of squared deviation | top-5 | sd ratio between halves |
|---|---|---|---|---|---|
| 5 000 | 1 200 | 0.446 | 37.8 % | 66.2 % | 1.34 |
| 50 000 | 600 | 0.123 | 8.8 % | 30.6 % | 1.01 |
| **250 000** | 400 | 0.144 | **32.2 %** | **78.2 %** | **2.79** |

At the **production** block size one block in four hundred still carries a
third of the variance, and the sd differs by 2.8× between halves of the
sample. (The benign 50 000 row is a 600-block sample that happened to contain
no extreme block; with rare heavy events, absence is not evidence.)

This has a consequence beyond Stage-1 sizing, and it is the most important
thing Pilot-3 found: **the inherited `MINIMUM_BLOCK_SIZE = 250 000` rule does
not deliver a well-behaved block-mean law for `t1p5` at `m = 1`.** The staged
rule's own stopping test is `achieved relSE <= r*`, computed from the same
block-mean standard deviation. If that statistic is unstable, then `ATTAINED`
is unstable — not just the initial allocation. Pilot-2's governance
architecture is unaffected in form, but the precision quantity it adjudicates
needs a firmer footing for this one family.

### 10.4 Second frozen-design error, disclosed

The pre-freeze synthetic probe in §9.1 of the preregistration calibrated the
UCB constructions on normal and `t(5.6)` laws at CV 0.40. The real law is CV
0.63 at `m = 1` with one-block-in-eight-thousand dominance — far outside what
that probe explored. The candidate set was therefore chosen against a model of
the problem that was too benign. This did not bias any recorded number, but it
is why the frozen grid looked adequate and was not.

## 11. Design results as recorded

96 candidates (`Bmin` 4 selectable values × 3 UCB constructions × 2 kappa × 4
caps), 20 replicates per (primary cell, stratum). **0 qualified.**

The closest, `Bmin = 16`, `chi2`, `kappa = 0.5`, cap `2×`:

| stratum | heavy | weight | n | attainment | `PRECISION_LIMITED` | valid | Stage-1 coverage |
|---|---|---|---|---|---|---|---|
| `H/S59` | yes | 2 | 20 | 0.850 | 0.150 | 1.000 | 0.20 |
| `H/S151` | yes | 2 | 20 | 0.950 | 0.050 | 1.000 | 0.10 |
| `H/S215` | yes | 2 | 20 | 0.600 | 0.400 | 1.000 | 0.10 |
| `H/S1784` | yes | 2 | 20 | **0.500** | **0.500** | 1.000 | 0.05 |
| `O/ORD` | no | **40** | 20 | **1.000** | 0.000 | 1.000 | 0.50 |
| **mixture (8:40)** | | | | **0.9542** | **0.0458** | | |

**Criterion 4 excludes all 96 of 96 candidates** — not merely the closest.
Every combination of `Bmin`, UCB construction, kappa and cap leaves at least
one heavy stratum below the 0.90 attainment floor or above the 0.10 PL
ceiling.

**The per-heavy-stratum floor did exactly the job it was frozen to do.** The
production-mixture-weighted numbers *pass* criteria 2 and 3 — attainment
0.9542 against a 0.95 floor, `PRECISION_LIMITED` 0.0458 against a 0.05 ceiling
— while three of the four heavy strata fail on their own, one of them at
0.500. Weighted by the real 8 : 40 mixture, forty easy strata very nearly
averaged away a heavy stratum that attained half the time. Criterion 4 caught
it. Had Pilot-3 reported only the mixture figures it would have declared
success on a rule that abandons half of its hardest routes.

### 11.1 Kappa comparison — the one design conclusion that survives

Cost is the discriminator, and the requirement itself differs by 2.33×:

| kappa | heavy blocks required | mean × | q95 × | total central | total conservative | max-config conservative | verdict |
|---|---|---|---|---|---|---|---|
| `K1 = 0.5` | **5 725** | 0.69 | 2.31 | 8.01 h | **21.40 h** | 11.38 h | PASS / PASS |
| `K2 = 0.3197` | 13 363 | 1.32 | 5.70 | 32.03 h | **130.59 h** | 106.05 h | FAIL / FAIL |

`K2` misses the frozen 45 h and 30 h acceptance limits by factors of about 2.9
and 3.5. This comparison is a ratio driven by the exponent and by P4X's own
recorded Stage-1 precision, so it is the least benchmark-dependent quantity
Pilot-3 produced — but it is a *design-side observation*, and since no
candidate qualified, **no kappa was selected**.

### 11.2 The ordinary strata were not penalised

Brief §18 required that fixing the 8 heavy strata must not tax the 40 ordinary
ones. The heavy-tail reference inflation applies only to the frozen tail
class, a test asserts it, and the ordinary control attains **1.000 with zero
`PRECISION_LIMITED`** at cap `2×`. The reference expansion itself is cheap:
0.05 h at `Bmin = 16` rising to only 0.64 h at `Bmin = 128`, against a 45 h
budget. Whatever Pilot-4 concludes, **`Bmin` can be generous without a cost
problem** — that part of the design space is settled.

### 11.3 Disposition audit

Across all 96 candidates, 14 880 dispositions were audited: **498 invalid
(3.35 %)**, every one attributable to the frozen absolute ceiling — 496
Stage-1 allocations above `40 × B_req` (overwhelmingly `kappa = 0.3197` at
`S1784`) and 2 `POOL_EXHAUSTED`. Both are the ceiling mechanism behaving as
frozen, and both count **against** their candidates. No third state, no cap
overrun, no mislabelled terminal state, no scientific leakage was found
anywhere.

## 12. Shard, RNG and leakage regression — all PASS

```text
P4Y_EXACT_SHARD_SUM_INVARIANT        = PASS
P4Y_HISTORICAL_8801_BLOCK_REGRESSION = PASS
P4Y_RNG_COLLISION_AUDIT              = PASS
P4Y_SHARD_INVARIANT_BLOCK_IDENTITY   = PASS
P4Y_SCIENTIFIC_LEAKAGE_GUARD         = PASS
```

Nothing was redesigned; these are regression checks, as brief §21 requires.
109 tests pass. `partition(8801, 5) = [1761, 1760, 1760, 1760, 1760]` summing
to **8 801** blocks and **2 200 250 000** paths, with the defective historical
implementation pinned at 8 805 / 2 201 250 000. The frozen reachable address
domain is **878 addresses, 878 unique**, campaign base `9 310 000 000`, no
modulo compression, no worker/pid/shard/schedule argument in the seed.

## 13. STOP ledger

| | |
|---|---|
| CPU cap | 3.0 CPU-hours, frozen before T2, never extended |
| used | benchmark 186.8 s + design 2 412.9 s + post-STOP diagnostic 56.8 s = **0.7379 CPU-h** |
| cumulative-CPU STOP | did not fire |
| absolute-ceiling STOP | did not fire as a phase abort; ceiling refusals were recorded as INVALID, as frozen |
| Hill-alpha `<= 2.5` STOP | did not fire — 4.83 / 69.74 / 3.55 |
| address-collision STOP | did not fire |
| shard-sum STOP | did not fire |
| estimator-drift STOP | did not fire |
| **§23 classify-and-stop** | **FIRED** — result-bearing semantic defect in the frozen benchmark |

`P4Y_PILOT3_STOP_FIRED = YES`. Validation was **not run**: the primary
endpoint is measured against the benchmark, and the benchmark is invalid, so
2 CPU-hours of validation would have produced precise numbers about nothing.

## 14. Amendment ledger

```text
P4Y_PILOT3_POST_RESULT_AMENDMENTS = 0
```

**Zero.** No endpoint amendment, no new candidate, no new safety factor, no
changed kappa, no changed cap grid, no changed block minimum, no changed
statistical method, no re-interpretation. When the frozen design turned out to
be wrong, Pilot-3 stopped and said so. That is the discipline Pilot-2 could
not claim and Pilot-3 can.

The post-STOP diagnostic in §10.3 is disclosed, ran in a fresh `probe`
namespace, is not an endpoint, and changed no recorded result.

## 15. Frozen criteria — item by item

| | criterion | outcome |
|---|---|---|
| 1 | valid-disposition lower bound `>= 0.95` | **PASS** for the examined candidates; 1.0000 per stratum |
| 2 | mixture attainment `>= 0.95` | passes at the closest candidate (0.9542) — **but on an invalid instrument** |
| 3 | mixture `PRECISION_LIMITED` `<= 0.05` | passes at the closest candidate (0.0458) — same caveat |
| 4 | **every heavy stratum** `>= 0.90` attainment, `<= 0.10` PL | **FAIL for all 96 of 96 candidates** — 0.500 on `S1784` at the closest |
| 5 | no invalid disposition | **FAIL** for 498 of 14 880 across the grid; PASS for the closest candidate |
| 8 | conservative total CPU `<= 45 h` | PASS at `kappa = 0.5`, FAIL at `kappa = 0.3197` |
| 9 | conservative max-config CPU `<= 30 h` | PASS at `kappa = 0.5`, FAIL at `kappa = 0.3197` |
| 10 | governance regression tests | **PASS** |

**0 of 96 candidates satisfied all frozen criteria.** No `Bmin`, no UCB
method, no kappa, no cap was selected. Nothing is rounded into PASS, and
criteria 2 and 3 are explicitly *not* claimed as evidence, because the
quantity they are computed from is not trustworthy.

## 16. Verdict

```text
P4Y_PILOT3_VERDICT = NEEDS_ONE_MORE_PRE_FREEZE_PILOT
```

**Not `READY_FOR_BINDING_CHECKPOINT`**: nothing qualified, and no rule was
selected.

**Not `DO_NOT_FREEZE_P4Y`**: none of the frozen kill criteria is *established*.
"No UCB/min-reference design prevents systematic under-allocation" cannot be
concluded from measurements taken against an invalid truth. "Reliable sizing
requires implausible reference computation" is now a live question but is not
answered: §11.2 shows the reference expansion is cheap, so a much larger
`Bmin` is affordable and untested. Governance simplicity is intact, the
scientific scope is untouched, and at `kappa = 0.5` the projected campaign
sits comfortably inside both caps.

**Why this is not "more optimisation".** Pilot-3 did not fail to tune a
parameter. It discovered that a quantity all three pilots have implicitly
relied on — the reference relative standard error for `t1p5` at `m = 1` — is
not reliably estimable by the means assumed, at the pilot's block size *or at
the frozen production block size*. That is one specific, measurable question,
it is prior to every allocation rule, and it also governs the staged rule's
own stopping test. It has never been measured. It should be, once, on its own.

## 17. What Pilot-4 must be — and when it must return DO_NOT_FREEZE_P4Y

Pilot-4 is a **measurement pilot with no allocation rule in it at all**.
Frozen before any result-bearing byte, as Pilot-3 was:

1. **Measure the sampling distribution of the `t1p5` reference relative SE
   directly.** Draw a large pool of blocks for one heavy configuration at each
   of several block sizes — `250 000` (the frozen production value) and at
   least one substantially larger, e.g. `10^6` and `4×10^6` — and characterise
   `s_B / s_pool` by subsampling, with the pool's own stability established by
   disjoint-split and growing-prefix checks rather than by a normal-theory
   formula. **Never again assert a benchmark uncertainty from
   `1/sqrt(2(n-1))`.**
2. **Determine the smallest `(block size, B_ref)` pair at which the reference
   relative SE is estimable to within a predeclared factor with predeclared
   probability** — for example, within `[0.8, 1.25]` of the pool value with
   probability `>= 0.9`. This is the single number Pilot-3 lacked.
3. **Re-examine the inherited `MINIMUM_BLOCK_SIZE = 250 000` for `t1p5`.** It
   is a governance parameter, not science, and Pilot-3's diagnostic indicates
   it does not deliver a well-behaved block-mean law at `m = 1`. Raising it is
   in scope; changing `r*`, the gate, the estimators or the theorem is not.
4. Only if (2) succeeds, re-run Pilot-3's frozen candidate comparison against
   the now-trustworthy benchmark, with `kappa = 0.5` leading on Pilot-3's cost
   evidence and `0.3197` retained as the control.

**Pilot-4 must return `DO_NOT_FREEZE_P4Y` if** no `(block size, B_ref)` pair
within the affordable envelope — a reference budget that keeps the projected
campaign under the frozen 45 h / 30 h limits — estimates the reference
relative SE to the predeclared accuracy. In that case the `t1p5` precision
estimand is not governable at attainable cost, and P4Y should not be frozen on
it. That condition must be preregistered so Pilot-4 can fail cleanly.

## 18. Draft future P4Y Checkpoint A — NOT drafted

Brief §29 asks for a draft **only if READY**. Pilot-3 is not READY, so no
Checkpoint-A architecture is drafted here and none is activated. The four
governance components Pilot-1 and Pilot-2 established — staged termination
with the cap as sole terminator, mechanical `PRECISION_LIMITED` semantics
audited independently of the rule, the exact shard partition with a
`delta_blocks == 0` ledger, and collision-free worker-free logical RNG
addressing — remain validated and ready to be inherited. The Stage-1 sizing
rule, the `cap` formula, `Bmin`, the UCB construction and `kappa` remain
**open**.

## 19. Full-scope freshness — unchanged

A future P4Y must re-run all 96 scientific cells fresh. It may not inherit the
P4X 88 PASS cells, run only `t1p5`, run only the historical eight, or use
Pilot-1, Pilot-2 or Pilot-3 samples as scientific correspondence evidence.
All three pilots are **governance evidence only**.

---

## Repository safety

```text
branch                        p4y-pilot3-heavy-stage1, off p4y-pilot2-final, NOT merged
writes outside this directory none
P4X namespace on this branch  absent
Pilot-1 and Pilot-2 namespaces present, imported read-only, unmodified
main                          untouched
binding checkpoint            none created
production run                none executed
tests                         109 passed
pilot CPU                     0.7379 of the 3.0 CPU-hour cap
```
