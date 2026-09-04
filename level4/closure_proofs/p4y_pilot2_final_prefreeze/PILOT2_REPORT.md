# P4Y FINAL PRE-FREEZE PILOT (PILOT-2) — report

```text
STATUS = PILOT-2 COMPLETE, NON-BINDING
P4Y_BINDING_CHECKPOINT_CREATED = NO
P4Y_PRODUCTION_RUN             = NO

P4_ORIGINAL_VERDICT      = PARTIAL   immutable
P4X_ADJUDICATION         = OVERRIDE_FAIL
P4X_SUCCESSOR_VERDICT    = FAIL      immutable
P4X_SCIENTIFIC_FAILURES  = NONE      immutable
P4Y_PILOT1_VERDICT       = NEEDS_ONE_MORE_PRE-FREEZE_PILOT   immutable,
                           and NOT relabelled READY by this pilot
```

**Headline.** The governance machinery is sound and the frozen endpoint holds
perfectly: every replicate, at every cap, under both kappa candidates,
terminated in a *valid* governance disposition — 1.0000, with no third state
anywhere. But the frozen **attainment** criterion is **not met by any
`(kappa, cap)` pair in the frozen grid**, and Pilot-2 diagnoses why, at
production-representative block counts, with a cause that is neither the cap
nor the staged rule: **stage-1 sizing from a tiny heavy-tail reference is
severely and systematically optimistic.** At the actual P4X heavy-tail
reference of 4 blocks, the reference relative-SE estimate falls below its true
value in 95–100 % of fresh draws, with a median of 34–41 % of the truth; the
stage-1 law squares that, so stage 1 buys a median of 11–17 % of what the
route needs.

`P4Y_PILOT2_VERDICT = NEEDS_ONE_MORE_PRE_FREEZE_PILOT`, and the item that is
unresolved is named rather than rounded into PASS.

---

## 1. Immutable historical state

| | |
|---|---|
| `P4_ORIGINAL_VERDICT` | `PARTIAL` |
| `P4X_CHECKPOINT_A` | `756bf687cfe8e7d08f3fadea3daac504ea0330ac` |
| `P4X_FINAL_COMMIT` | `19b006456be7efc8254b1a72b6e0eb764b127753` |
| `P4X_ADJUDICATION` | `OVERRIDE_FAIL` |
| `P4X_SUCCESSOR_VERDICT` | `FAIL` |
| `P4X_SCIENTIFIC_FAILURES` | `NONE` |
| P4X scientific ledger | 88/96 binding PASS, 0 scientific FAIL, 8 `PRECONDITION_NOT_MET`, 0 `PRECISION_LIMITED` |
| `P4Y_PILOT1_VERDICT` | `NEEDS_ONE_MORE_PRE-FREEZE_PILOT` |

P4X failed on governance and sampling integrity, not on a scientific
contradiction. Nothing in this pilot alters, repairs, relabels or overwrites
it: the P4X namespace is not present on this branch. Pilot-1's namespace is
present, imported read-only, and unmodified.

## 2. Pilot-1 findings inherited

Inherited as settled and **not re-litigated**:

* the staged rule removes the third state — 0 `UNRESOLVED` in 354 validation
  replicates against 9 for the P4X-shaped rule, with the Gaussian control
  showing 5/59 abandoned by the baseline where the cap never bound at all;
* the repair is nearly free — identical spend on 97.2 % of routes, mean cost
  ratio 1.0105;
* **safety-factor inflation is unnecessary**, and chi-square / quantile
  inflation did not improve attainment enough to justify 24–60 % extra cost.
  Pilot-2 carries **no safety factor and no reserve factor**, and produced no
  contradiction that would justify resurrecting them.

## 3. Exactly why Pilot-1 was insufficient

**D1 — endpoint amended after design results were visible.** Pilot-1's
`p_attain` did not say what to do with a replicate the cap refused to fund;
read literally it ranked careful rules below careless ones. `AMENDMENT 1`
fixed the reading correctly but after design data existed.

**D2 — the cap was never measured.** Pilot-1 ran at `B1 = 24`; production runs
at 48–1784.

Pilot-2 removes exactly these two and introduces no others.

## 4. Preregistration hash and temporal ordering

```text
P4Y_PILOT2_PREREGISTRATION = ff688eccf6d4d8de025b10cfade967e70a0694fa
```

That commit contains `PILOT2_PREREGISTRATION.md`, all source, all tests — and
**no file under `results/`**. Verified by `git ls-tree`: sixteen files, none
of them a result.

| | event | evidence |
|---|---|---|
| `T0` | preregistration frozen | `ff688ec`, `results/` empty |
| `T1` | code and config frozen | same commit |
| `T2` | first result-bearing execution | 2026-09-04T05:32:56Z, `run_phase.py calibration` |
| `T2'` | re-run from scratch after the classified harness bug | commit `924f839` |
| `T3` | validation complete | see `results/TEMPORAL_LEDGER.txt` |
| `T4` | this report | |

**No governance rule was modified after T2.** One implementation bug was found
after T2; §29 classifies it and records what was done.

## 5. Frozen endpoint

```text
valid governance disposition
  = ATTAINED             achieved relSE <= target, blocks executed <= cap
  or PRECISION_LIMITED   achieved relSE > target
                         AND the NEXT predeclared stage > cap
                         AND blocks executed <= cap
  and in both branches no scientific-outcome field reachable from the
      stopping decision
```

Audited per replicate by `src/p4y_pilot2/audit.py`, which re-derives validity
from the recorded trajectory and the frozen cap and never asks the rule what
it thinks. The endpoint can fail, and tests prove it does when it should:
execution past the cap, a mislabelled attainment, a premature
`PRECISION_LIMITED`, a foreign trajectory, and each of the nineteen named
forbidden fields are each injected and each rejected.

**A validly `PRECISION_LIMITED` route is a valid governance disposition and is
never counted as a scientific success.** `P(ATTAINED)` and
`P(PRECISION_LIMITED)` are reported separately throughout, with their own
bounds and their own frozen acceptability floors.

## 6. Frozen statistical target

```text
r*                    = 0.010823        inherited operative value
                        (r_star_exact = 0.010823062977345114, provenance only)
delta                 = 0.95            governance-disposition target
beta                  = 0.05            one-sided
method                = exact Clopper-Pearson lower bound
R_validation          = 59              smallest R with delta**R <= beta

attainment floor, pooled     >= 0.95
attainment floor, per cell/stratum >= 0.90
PRECISION_LIMITED ceiling, pooled  <= 0.05
```

## 7. Production block-count reconstruction

From the immutable P4X `checkpoint_a.json` `production_plan` and
`c2_cell_ledger.json`, over all 48 `(configuration, route)` strata — allocation
and cost metadata only, no correspondence outcome read:

```text
stage-1 block counts   48 .. 1784      median 160
final   block counts   48 .. 9021      median 160
reference block counts 4, 13, 24, 48, 160, 300
B_ref / B1             median 1.000    minimum 0.0022
kappa_stage1           0.5 on all 96 rows
```

Pilot-1's reported 48–9021 range is **confirmed** as the range of *final*
block counts; the *stage-1* range, which is what a rule actually starts from,
is 48–1784.

## 8. Selected strata — every one an actual P4X stage-1 allocation

| id | `B_ref` | `B1` | regime | provenance |
|---|---|---|---|---|
| `T1` | 48 | 48 | low | the modal P4X stage-1 allocation, 10 of 48 strata |
| `T2` | 160 | 160 | middle | the median P4X stage-1 allocation |
| `T3` | 300 | 300 | high | the upper mode of the `B_ref/B1 == 1` group, 11 of 48 |
| `T4` | 4 | 215 | heavy-tail high-cost | `frozen/cusum@5/t1p5` Route B — consumed 18.60 of P4X's 24.75 CPU-hours |
| `T5` | 4 | 1784 | extreme | `frozen/sr@520.886/t1p5` Route B — the maximum stage-1 allocation |

**No deficit axis, by design.** Stage 1 is sized from the reference, so a route
a factor `D` short of target receives an allocation `D^(1/kappa_stage1)` larger
and is then at target in expectation at its own `B1`. The deficit is absorbed
into `B1`, and `B1` is what the strata span. What the heavy-tail
configurations actually had was not a deficit but a four-block reference —
which §11 shows is the whole problem.

Cells: `H` `reduced/cusum@2/t1p5` Route A at 5 000 paths/block (all five
strata); `L` `reduced/cusum@2/gaussian` Route A at 1 000 (T1–T3, the
finite-variance control); `RB` `reduced/cusum@2/t1p5` Route B at 10 000 (T1,
Route-B robustness, reported separately and excluded from the primary
endpoint). Block sizes come from the pre-freeze probe and are the smallest
whose block means are comfortably finite-variance; calibration re-measured
them at Hill alpha 5.59 / 68.13 / 3.69, all above the frozen 2.5 STOP floor.

## 9. Frozen kappa candidates and staged rule

```text
kappa_blockcount_A = 0.3197278911564626      1 - 1/alpha at the frozen floor 1.47
kappa_blockcount_B = 0.5                     the finite-variance block-count rate

stage 1   B1_realised = max(8, ceil(B_ref * (relSE_ref/target) ** (1/0.5)))
loop      achieved <= target            -> ATTAINED
          next = ceil(B * (achieved/target) ** (1/kappa_blockcount))
          next > cap_blocks             -> PRECISION_LIMITED
          else execute exactly the next stage and repeat
```

`kappa_stage1 = 0.5` is inherited from P4X unchanged. No safety factor, no
reserve factor, no "at most one top-up". Exactly two kappa candidates; no
third fitted exponent was introduced, before or after results.

Cap grid: `M ∈ {1.5, 2, 3, 4, 6, 8, 12} × B1_nominal`, each an integer.

## 10. Cap candidates

```text
CAP_MULTIPLIERS = (1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0)
cap_blocks(stratum, M) = ceil(M * B1_nominal)          an INTEGER per stratum
```

The cap is frozen against the stratum's **nominal** `B1`, as a checkpoint
would freeze it before a run. A route whose realised stage-1 requirement
already exceeds the cap is `PRECISION_LIMITED` from projected cost alone,
before a single block executes — the inherited P4X semantics verbatim.

The grid is evaluated exactly with no extra simulation: the stage sequence is
cap-independent, so one recorded trajectory per `(replicate, kappa)` yields
every cap's outcome, and a test asserts that this derivation equals an
independent re-run under each cap.

## 11. Design results — and the finding that decides this pilot

### 11.1 The governance endpoint is perfect everywhere

```text
valid-disposition rate = 1.0000
```

at every cap, under both kappa candidates, on every stratum, on both cells.
No third state, no execution past a cap, no mislabelled terminal state, no
forbidden field. The auditor — which is built to fail and demonstrably does
when fed a violation — found nothing to reject.

### 11.2 The attainment criterion is not met by any frozen pair

Pooled over the primary cells and all strata, `R_design = 20` per
(cell, stratum):

| cap | `kappa_A` attain | `kappa_B` attain | `kappa_A` mean × | `kappa_B` mean × | eligible? |
|---|---|---|---|---|---|
| 1.5× | 0.6500 | 0.7250 | 0.726 | 0.771 | no |
| 2× | 0.7000 | 0.7688 | 0.826 | 0.819 | no |
| 3× | 0.7438 | 0.7937 | 0.961 | 0.870 | no |
| 4× | 0.7875 | 0.8313 | 1.097 | 1.014 | no |
| 6× | 0.8313 | 0.8812 | 1.319 | 1.199 | no |
| 8× | 0.8500 | 0.9062 | 1.437 | 1.369 | no |
| 12× | 0.8750 | **0.9313** | 1.655 | 1.591 | no |

The frozen criterion requires pooled attainment `>= 0.95` and per-stratum
`>= 0.90`. The best pair in the grid reaches 0.9313 pooled and 0.85 on its
worst stratum. **`NO KAPPA HAS A SELECTABLE CAP`**, and per §12 of the brief
no third exponent was fitted and no threshold was moved.

### 11.3 Which population is failing — and it is not the light tail

Attainment by `(cell, stratum)` at `kappa_B`, design:

| cell / stratum | `B1` | `B_ref` | 1.5× | 2× | 3× | 4× | 6× | 8× | 12× |
|---|---|---|---|---|---|---|---|---|---|
| `L/T1` gaussian | 48 | 48 | **1.00** | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| `L/T2` gaussian | 160 | 160 | **1.00** | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| `L/T3` gaussian | 300 | 300 | **1.00** | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| `H/T1` t1p5 | 48 | 48 | 0.55 | 0.60 | 0.70 | 0.80 | 0.80 | 0.80 | 0.85 |
| `H/T2` t1p5 | 160 | 160 | 0.60 | 0.70 | 0.70 | 0.75 | 0.85 | 0.90 | 0.90 |
| `H/T3` t1p5 | 300 | 300 | 0.45 | 0.55 | 0.65 | 0.70 | 0.75 | 0.80 | 0.90 |
| `H/T4` t1p5 | 215 | **4** | 0.70 | 0.75 | 0.75 | 0.75 | 0.85 | 0.95 | 0.95 |
| `H/T5` t1p5 | 1784 | **4** | 0.50 | 0.55 | 0.55 | 0.65 | 0.80 | 0.80 | 0.85 |

**The finite-variance control attains 100 % at the smallest cap in the grid, on
every stratum.** Five of the six theorem-supported families are
finite-variance. The failure is entirely `t1p5`.

### 11.4 The cause is stage-1 sizing from a tiny heavy-tail reference

The reference relative-SE estimate against its true value at `B_ref` blocks,
the truth taken from 2 000 calibration blocks:

| cell / stratum | `B_ref` | true `relSE(B_ref)` | median estimate | ratio | fraction of draws **below** truth |
|---|---|---|---|---|---|
| `L/T1` | 48 | 0.00459 | 0.00450 | 0.981 | 0.65 |
| `L/T2` | 160 | 0.00251 | 0.00249 | 0.992 | 0.55 |
| `L/T3` | 300 | 0.00183 | 0.00182 | 0.991 | 0.60 |
| `H/T1` | 48 | 0.06171 | 0.03871 | 0.627 | 0.75 |
| `H/T2` | 160 | 0.03380 | 0.03012 | 0.891 | 0.60 |
| `H/T3` | 300 | 0.02468 | 0.02192 | 0.888 | 0.60 |
| `H/T4` | **4** | 0.21376 | 0.08811 | **0.412** | **1.00** |
| `H/T5` | **4** | 0.21376 | 0.07292 | **0.341** | **0.95** |

At the **actual P4X heavy-tail reference of 3.8 → 4 blocks**, the estimate is
below its true value in 95–100 % of fresh draws, with a median of 34–41 % of
the truth. The stage-1 law squares the ratio, so the allocation it buys is
correspondingly tiny:

`B1_realised / B1_nominal`, design:

| cell / stratum | `B_ref` | q05 | median | q95 | max |
|---|---|---|---|---|---|
| `L/T1` | 48 | 0.62 | 0.98 | 1.40 | 1.40 |
| `L/T2` | 160 | 0.88 | 0.98 | 1.18 | 1.19 |
| `L/T3` | 300 | 0.85 | 0.98 | 1.14 | 1.18 |
| `H/T1` | 48 | 0.19 | 0.40 | 49.04 | 56.44 |
| `H/T2` | 160 | 0.24 | 0.71 | 7.47 | 95.92 |
| `H/T3` | 300 | 0.24 | 0.72 | 5.77 | 8.84 |
| `H/T4` | **4** | 0.04 | **0.17** | 0.69 | 0.80 |
| `H/T5` | **4** | 0.02 | **0.11** | 0.93 | **3645.13** |

For the light-tail control the stage-1 allocation is tight and unbiased —
median 0.98 of nominal, spread 0.62–1.40. For `t1p5` it is catastrophically
dispersed and **systematically low**: a median of 11–17 % of what the route
needs at the four-block reference, with a tail reaching 3 645× at the other
extreme.

**This is not a cap problem and not a staged-rule problem.** No cap can rescue
a route whose stage 1 starts at a ninth of the required size and whose every
subsequent size estimate is drawn from the same median-low distribution: the
rule creeps upward, each step under-sized, and meets whatever cap it is given.
Raising the cap raises attainment monotonically — 0.725 → 0.931 from 1.5× to
12× — but never fast enough, and by 12× the mean spend has already doubled.

This is the same right-skew Pilot-1 documented in its §12.1 (realised ≤ true on
75 % of draws pooled, 100 % on the heaviest cell). Pilot-1 saw it as a
diagnostic; Pilot-2, at production-representative references, shows it is the
binding constraint.

### 11.5 Answer to Q3 — kappa

`kappa_B = 0.5` **dominates** `kappa_A = 0.3197278911564626` at every cap from
2× upward, on **both** axes simultaneously: strictly higher attainment and
strictly lower mean cost. At 1.5× it still attains more (0.725 vs 0.650) at a
slightly higher mean spend.

That is a clean, mechanical, design-side answer, and it is what the block-mean
evidence predicts: the Hill index of the block means is 5.59 (`H`), 68.13
(`L`) and 3.69 (`RB`) — all comfortably above 2 — so block **counts** compose
at the finite-variance rate `B^{-1/2}`, i.e. `kappa = 0.5`. Applying
`1 - 1/alpha = 0.3197` to block-count growth raises the noise-amplifying
exponent from 2 to 3.128 and buys nothing.

**However**: the frozen selection rule ranks only among kappas that have a
*selectable* cap, and neither has one. So **no kappa is selected**, formally.
The dominance is reported as design-side evidence for the next pilot, not as a
selection.

## 12. Validation results — fresh seeds, 472 replicates per point

Validation replicate ids start at 50 000 and are disjoint from design by
construction. `R = 59` per (primary cell, stratum) × 8 cell-strata = **472
replicates per `(kappa, cap)` point**. Selection was already closed on the
design side; validation influenced nothing.

| cap | `kA` valid | `kA` attain | `kA` PL | `kB` valid | `kB` lower | `kB` attain | `kB` attain LB | `kB` PL | `kB` mean × |
|---|---|---|---|---|---|---|---|---|---|
| 1.5× | 1.0000 | 0.7246 | 0.2754 | 1.0000 | 0.9937 | 0.7881 | 0.7548 | 0.2119 | 0.739 |
| 2× | 1.0000 | 0.7797 | 0.2203 | 1.0000 | 0.9937 | 0.8242 | 0.7928 | 0.1758 | 0.804 |
| 3× | 1.0000 | 0.8199 | 0.1801 | 1.0000 | 0.9937 | 0.8581 | 0.8289 | 0.1419 | 0.875 |
| 4× | 1.0000 | 0.8305 | 0.1695 | 1.0000 | 0.9937 | 0.8835 | 0.8563 | 0.1165 | 0.961 |
| 6× | 1.0000 | 0.8559 | 0.1441 | 1.0000 | 0.9937 | 0.8983 | 0.8725 | 0.1017 | 1.050 |
| 8× | 1.0000 | 0.8686 | 0.1314 | 1.0000 | 0.9937 | 0.9153 | 0.8911 | 0.0847 | 1.189 |
| 12× | 1.0000 | 0.8898 | 0.1102 | 1.0000 | 0.9937 | **0.9301** | 0.9076 | 0.0699 | 1.319 |

### 12.1 Valid governance disposition — the primary endpoint

```text
P4Y_VALID_DISPOSITION_RATE        = 1.0000    at every (kappa, cap) point
P4Y_VALID_DISPOSITION_LOWER_BOUND = 0.9937    exact Clopper-Pearson, 472/472
target                              0.95      MET
invalid dispositions observed       0
```

Zero invalid dispositions anywhere: no third state, no execution past a cap,
no mislabelled terminal state, no forbidden field. The endpoint the auditor
was built to be able to fail did not fail. **Criterion B is met.**

### 12.2 Attainment and `PRECISION_LIMITED` — reported separately

```text
best pair in the frozen grid (kappa_B_0.5, 12x), REPORTED not selected
  P4Y_ATTAINMENT_RATE          = 0.9301   floor 0.95     NOT MET
  attainment lower bound       = 0.9076   floor 0.90     met
  P4Y_PRECISION_LIMITED_RATE   = 0.0699   ceiling 0.05   NOT MET
```

**Criterion C is not met.** It is not rounded into PASS.

### 12.3 Per stratum, `kappa_B` — where the failure lives

| cell / stratum | `B1` | `B_ref` | 1.5× | 3× | 6× | 12× |
|---|---|---|---|---|---|---|
| `L/T1` gaussian | 48 | 48 | **1.000** | 1.000 | 1.000 | 1.000 |
| `L/T2` gaussian | 160 | 160 | **1.000** | 1.000 | 1.000 | 1.000 |
| `L/T3` gaussian | 300 | 300 | **1.000** | 1.000 | 1.000 | 1.000 |
| `H/T1` t1p5 | 48 | 48 | 0.814 | 0.881 | 0.898 | 0.949 |
| `H/T2` t1p5 | 160 | 160 | 0.729 | 0.814 | 0.881 | 0.932 |
| `H/T3` t1p5 | 300 | 300 | 0.559 | 0.780 | 0.847 | 0.898 |
| `H/T4` t1p5 | 215 | **4** | 0.763 | 0.847 | 0.881 | 0.898 |
| `H/T5` t1p5 | 1784 | **4** | **0.441** | 0.542 | 0.678 | **0.763** |

The per-stratum floor of 0.90 fails on `H/T3`, `H/T4` and `H/T5` even at the
largest frozen cap, and `H/T5` — the extreme regime, a four-block reference
driving a 1 784-block allocation — reaches only 0.763.

**This matters for how the verdict should be read.** The frozen design weights
the heavy-tail cell 5 strata to the control's 3, whereas P4X's own structure is
8 `(configuration, route)` strata needing stage-1 sizing against 40 whose
reference already met `r*` — and those 8 are *exactly* the eight `t1p5`
strata. So the pooled rate above over-weights the hard subpopulation relative
to a real campaign. **That observation does not rescue the verdict**, because
the frozen criterion also imposes a per-stratum floor, and three heavy strata
fail it on their own, independent of any pooling weight.

### 12.4 Route-B robustness (`RB/T1`, 29 replicates, excluded from the primary)

| cap | valid | attain | PL | mean × |
|---|---|---|---|---|
| 1.5× | 1.0000 | 0.7931 | 0.2069 | 0.536 |
| 3× | 1.0000 | 0.8966 | 0.1034 | 0.716 |
| 8× | 1.0000 | 0.9310 | 0.0690 | 0.960 |
| 12× | 1.0000 | 0.9310 | 0.0690 | 0.960 |

Route B behaves like Route A on the same family, at lower cost. Consistent
with Pilot-1's Route-A/Route-B equivalence for governance.

## 13. Kappa comparison — Q3

`kappa_B = 0.5` **dominates** `kappa_A = 0.3197278911564626` on validation at
**every** cap, on **both** axes: higher attainment, lower `PRECISION_LIMITED`,
lower mean spend. At 12× it attains 0.9301 against 0.8898 while spending 1.319
against `kappa_A`'s 1.655 (design-side, same ordering).

This is what the block-mean evidence predicts. Calibration measured the Hill
index of the **block means** at 5.59 (`H`), 68.13 (`L`) and 3.69 (`RB`) — all
above 2 — so block **counts** compose at the finite-variance rate `B^{-1/2}`.
Applying `1 - 1/alpha = 0.3197` to block-count growth raises the
noise-amplifying exponent from 2 to 3.128 and buys nothing: it is the
*within-block* tail index, and block-count growth is not a within-block
operation. P4X's frozen policy conflated the two by writing the law in terms
of `N`.

**Formally, no kappa is selected**, because the frozen rule ranks only among
kappas that have a selectable cap and neither does. The dominance is recorded
as design- and validation-side evidence for the next pilot, not as a
selection. `P4Y_SELECTED_KAPPA_BLOCKCOUNT = NONE_SELECTED`.

## 14. Measured production-regime cost tail, and cost feasibility

At the best pair in the grid (`kappa_B`, 12×), validation, 472 replicates:

```text
mean block multiplier   1.319
q95 block multiplier    4.374
max block multiplier   11.646
```

Projected against the immutable P4X cost basis (24.749 CPU-hours total, 18.599
on `frozen/cusum@5/t1p5`):

| | central | conservative (q95) | frozen accept limit | |
|---|---|---|---|---|
| total CPU | 32.65 h | **108.25 h** | 45.0 h | **FAIL** |
| max-configuration CPU | 24.54 h | **81.35 h** | 30.0 h | **FAIL** |

Criteria F and G are **not met**, and they fail for the *same* reason as
criterion C: a route that starts at a ninth of its required size has to climb
a long way, and the climb is what produces a q95 spend of 4.37×.

```text
P4Y_TOTAL_CAP_FEASIBILITY      = FAIL
P4Y_PER_CONFIG_CAP_FEASIBILITY = FAIL
```

## 15. Shard, RNG and identity results

```text
P4Y_EXACT_SHARD_SUM_INVARIANT        = PASS
P4Y_HISTORICAL_8801_BLOCK_REGRESSION = PASS
P4Y_RNG_COLLISION_AUDIT              = PASS
P4Y_SHARD_INVARIANT_BLOCK_IDENTITY   = PASS
```

* **Shard sum.** `sum == B` and `max - min <= 1` for every `B` in
  `{0, 1, 7, 48, 215, 300, 1784, 8801, 100000, 2200168765}` × every `K` in
  `{1,2,5,7,13,64}`; executed blocks and executed paths equal the frozen
  request exactly, `delta == 0`. A dedicated test asserts no independent
  per-shard rounding occurs.
* **8801 regression.** `partition(8801, 5) = [1761, 1760, 1760, 1760, 1760]`,
  summing to **8 801** blocks and **2 200 250 000** paths. The defective
  historical implementation is reproduced in-tree and pinned at 8 805 blocks /
  2 201 250 000 paths — `+4` blocks, `+1 000 000` paths. The test fails on a
  discrepancy of one block in either direction.
* **RNG collision audit.** The complete frozen reachable domain — **1 355
  addresses**, enumerated exactly from the frozen cells × their strata ×
  namespaces × their replicate ranges — gives **1 355 unique seeds**, and a
  margin audit at 200 replicates per point gives 15 000 / 15 000. Seeds span
  `6 310 000 000 .. 6 513 050 028`, a clean `1e9` above Pilot-1's *theoretical*
  ceiling. A test asserts `%` does not appear in the seed path, so no modulo
  compression can creep back. Every result-bearing phase re-runs the audit at
  start-up and refuses to execute on any collision.
* **Shard-invariant identity.** For `K ∈ {1,2,5,7,13,64}` the union of shard
  ranges is exactly `range(B)`, no block is scheduled twice, block outputs are
  **bit-identical** across `K`, and pooled summaries equal the unsharded
  formula exactly.
* **Scientific-outcome isolation.** `rule.trace` takes
  `(measure, b1, target, kappa, max_cap)` and nothing else; `Precision` carries
  `(blocks, relative_se)` and nothing else; all nineteen named forbidden fields
  are injected into the auditor and each is rejected; and the runner's
  `replicate` body is scanned for those names.

206 tests pass: 10 addressing, 22 rule/auditor, 23 leakage, 122
shard/identity, 8 non-drift and frozen-anchor, 21 bug-fix equivalence.

## 16. Estimator non-drift

Per-block evaluation reproduces the frozen `route_a` and `route_b` **bit for
bit** on all three Pilot-2 cells; the frozen `P4_PROTOCOL.json` still hashes to
the `protocol_sha256` recorded in `correspondence.json`; all frozen Route-Q
quadrature anchors reproduce; `r*` is re-derived from the unchanged 0.03
criterion rather than read. `NEW THEOREM = NO`, `NEW LEAN = NO`,
`NEW ARB = NO`, `NEW SCIENTIFIC CLAIM = NO`.

## 17. STOP ledger

```text
P4Y_PILOT2_STOP_FIRED = NO
```

| STOP rule | fired? |
|---|---|
| cumulative CPU reaching 3.0 hours | no — **0.5768 CPU-hours** used |
| a replicate requesting more than `pool_limit` | no — see §18 for the harness bug that mis-reported this once, before any result existed |
| calibration block-mean Hill alpha `<= 2.5` | no — measured 5.59, 68.13, 3.69 |
| address collision in the frozen domain | no — 1 355 / 1 355 unique |
| shard partition executing a wrong total | no |
| estimator drift | no |

CPU: calibration 109.7 s, design 543.3 s, validation 1 423.4 s → **0.5768 of
the 3.0 CPU-hour cap**, never silently extended. The frozen design's
pre-computed worst case was 2.12 hours; the realised cost is well under it
because most replicates terminate in one or two stages.

## 18. Amendment ledger

```text
P4Y_PILOT2_POST_RESULT_AMENDMENTS = 0 governance amendments / 2 implementation fixes
```

**Zero** changes to any governance rule after T2: the endpoint, `delta`,
`beta`, the statistical method, the attainment floors, the
`PRECISION_LIMITED` ceiling, the kappa pair, the cap grid, the staged rule,
the selection criteria, the cost-acceptance criterion, the budget and the STOP
rules are exactly as frozen at `ff688ec`. Nothing was re-interpreted and
nothing was repaired to fit a result. This is the defect Pilot-1 carried, and
Pilot-2 does not carry it.

Two implementation fixes, both classified per §23 of the brief:

**(1) Harness abort bug — semantics-preserving, results discarded and re-run.**
`trace` bounded its loop by `pool_limit = B_ref + largest frozen cap` and, when
the sizing law *computed* a next stage beyond that bound, flagged
`pool_exhausted`, which the runner raised on. A computed next stage is a
number, not a draw: the replicate that triggered it had drawn 48 blocks against
a pool limit of 624, so frozen STOP rule 2 never fired in substance.
`terminate` never reads the flag. `tests/test_bugfix_equivalence.py` keeps the
pre-fix implementation verbatim and proves, over randomised trajectories on all
five strata and both kappas, that the new stage list is a **prefix** of the old
and that **every frozen cap yields an identical `Outcome`**; wherever the lists
differ, the old code had drawn one extra stage already larger than the largest
frozen cap — simulation no cap could consume. The frozen `strata.pool_limit`
docstring, committed at T0, already stated the intent: *"the rule can always
run to the point where the largest cap would refuse it, and never one block
further."* The code contradicted the frozen text; the fix restored it.
**Everything computed under the buggy harness was discarded** — design,
console, and calibration, even though calibration never calls `trace` and
reproduces bit for bit — and every result-bearing phase was re-run from
scratch. Commit `924f839`. A follow-on `NameError` in the same edit was caught
before it produced any output.

**(2) Reporting gap — no decision affected.** `build_report` emitted the
validation `kappa × cap` curve only when a pair had been selected. §9 of the
frozen preregistration requires the curve to be reported regardless: *"The full
`kappa × cap` curve is computed on validation and reported, but only the
selected pair is decisive."* The fix emits it unconditionally. No threshold,
criterion, selection or outcome is touched by it.

Neither fix could alter result-bearing semantics, so neither triggered the
"stop and restart under a new pre-freeze pilot" clause; and neither was patched
silently.

## 19. Pass criteria — item by item

| | criterion | outcome |
|---|---|---|
| A | frozen endpoint survives unchanged | **PASS** — zero governance amendments |
| B | valid-disposition CP lower bound `>= 0.95` | **PASS** — 0.9937, 472/472 |
| C | attainment `>= 0.95`, LB `>= 0.90`, PL `<= 0.05` | **FAIL** — 0.9301 / 0.9076 / 0.0699 |
| D | a kappa selected mechanically from the frozen pair | **FAIL** — no kappa has a selectable cap |
| E | `cap_blocks` empirically supported at production block counts | **FAIL** — no cap in `{1.5…12}×` qualifies |
| F | conservative projected total CPU `<= 45.0` h | **FAIL** — 108.25 h |
| G | conservative projected max-config CPU `<= 30.0` h | **FAIL** — 81.35 h |
| H | exact shard-sum invariant | **PASS** |
| I | RNG collision-free addressing | **PASS** |
| J | shard-invariant logical block identity | **PASS** |
| K | no STOP fired | **PASS** |
| L | no post-result amendment | **PASS** — 0 governance, 2 classified implementation fixes |

Five load-bearing items are unresolved. None is rounded into PASS.

## 20. Verdict

```text
P4Y_PILOT2_VERDICT = NEEDS_ONE_MORE_PRE_FREEZE_PILOT
```

**Not `READY_FOR_BINDING_CHECKPOINT`**, because C, D, E, F and G fail.

**Not `DO_NOT_OPEN_P4Y`**, because the failure is diagnosed, localised and
fixable, and because the governance machinery this line of pilots was built to
repair now demonstrably works:

* the valid-disposition endpoint is 1.0000 with a 0.9937 lower bound over 472
  fresh replicates at every cap and both kappas — the third state is gone and
  stays gone;
* the finite-variance control attains **1.000 at the smallest cap on every
  stratum**, and 40 of P4X's 48 `(configuration, route)` strata are of exactly
  that kind;
* the eight strata that needed stage-1 sizing in P4X are *precisely* the eight
  `t1p5` strata, which is exactly where Pilot-2's failure lives — so the pilot
  has found the real production boundary rather than an artifact;
* the cause is not the cap and not the staged rule. It is **stage-1 sizing
  from a tiny heavy-tail reference**: at `B_ref = 4` the reference relative-SE
  estimate is below its true value in 95–100 % of draws with a median of
  34–41 % of the truth, and the stage-1 law squares that, buying a median 11–17 %
  of what the route needs;
* that is a governance parameter — the size and treatment of the reference —
  not a scientific fact, and fixing it needs no new theorem, no new Lean, no
  new Arb and no change to `r*` or the correspondence gate.

## 21. May a P4Y binding checkpoint be frozen now?

**No.** Freezing a checkpoint now would freeze a `cap_blocks` that the evidence
says cannot deliver the attainment target on the heavy-tailed family, and a
projected cost that exceeds the acceptance limit by a factor of two. That is
the shape of the mistake that ended P4X, made a second time.

**What Pilot-3 must do**, in scope order — and it must freeze all of this
before any result-bearing byte, as Pilot-2 did:

1. **Repair stage-1 sizing for the heavy-tail configurations.** Predeclare a
   pair of candidates: (i) a minimum heavy-tail reference block count large
   enough that its relative-SE estimate is not median-low — the reference is
   cheap, it is not production; and (ii) sizing from a one-sided **upper**
   confidence bound on `relSE_ref` rather than its point estimate. This is the
   binding constraint and everything else is downstream of it.
2. **Carry `kappa_blockcount = 0.5` as the leading candidate**, with 0.3197
   retained as the control. Pilot-2's evidence is unambiguous on both axes,
   but it was not a formal selection and Pilot-3 should re-establish it under a
   criterion that can actually select.
3. **Extend the cap grid upward** and, more importantly, express the cap
   against the *projected* requirement rather than a nominal `B1`, so that the
   cap and the sizing repair are consistent.
4. **Predeclare the population mixture.** P4X's real structure is 8 strata
   needing sizing against 40 that do not. A pooled attainment criterion should
   be applied to a production-representative mixture, with the per-stratum
   floor retained so the hard strata cannot be averaged away.
5. Re-run the same governance battery — shard sum, 8801 regression, collision
   audit, shard-invariant identity, non-drift — which Pilot-2 passes and which
   should keep passing unchanged.

Pilot-3 is small: it needs no new estimator, no new science, and Pilot-2 spent
0.58 CPU-hours.

## 22. Draft future P4Y Checkpoint-A architecture — designed, NOT activated

Recorded for completeness. **It is not created, and on Pilot-2's evidence it
must not be activated until Pilot-3 resolves items C–G.** There is no
`checkpoint_a/` directory, no `checkpoint_a.json`, no anchor commit.

**Inherited unchanged:** the P4 theorem and A1–A7; the 96-cell scope and the 32
outside-assumption rows; the six theorem-supported families; both detectors at
both layers; the `m` grid `{1,2,3,5}`; the Route-A and Route-B estimators with
their frozen finite-difference steps and per-block Richardson combination; the
Route-Q role; the Gaussian consistency rule; `r* = 0.010823`; the
correspondence criteria `relative <= 0.03 AND |z| <= 4`; and the `C1`, `C3`,
`C4`, `C5`, `C6`, `C7` obligations. `NEW LEAN = NO`, `NEW ARB = NO`.

**The only substantive successor changes:**

| # | change | status after Pilot-2 |
|---|---|---|
| 1 | staged precision governance: the cap is the only terminator, terminal states `{ATTAINED, PRECISION_LIMITED}` exhaustive by control flow | **ready** — 1.0000 valid disposition, LB 0.9937 |
| 2 | `PRECISION_LIMITED` frozen to the mechanical definition, audited independently of the rule | **ready** |
| 3 | exact shard partition with an execution ledger asserting `delta_blocks == 0` | **ready** |
| 4 | collision-free logical RNG addressing, no modulo compression, worker-free | **ready** |
| 5 | stage-1 sizing for heavy-tail configurations | **NOT READY — Pilot-3** |
| 6 | `cap_blocks` per configuration as a frozen integer | **NOT READY — Pilot-3** |
| 7 | `kappa_blockcount` | **evidence favours 0.5; not formally selected** |

**Production scope, when it happens:** fresh full-scope production of all 96
theorem-supported cells and both routes, in a fresh seed namespace. It may not
reuse P4X samples as binding P4Y evidence, may not run only the historical
eight cells, and may not inherit the P4X 88 PASS cells as P4Y PASS. Pilot-1
and Pilot-2 samples are **governance-design evidence only** and are never
scientific correspondence evidence.

---

## Repository safety

```text
branch                        p4y-pilot2-final, off p4y-prefreeze-pilot, NOT merged
worktree                      /Users/suzhe/ReBaseGuard-p4y2
writes outside this directory none
P4X namespace on this branch  absent
Pilot-1 namespace             present, imported read-only, unmodified
main                          untouched
binding checkpoint            none created
production run                none executed
tests                         206 passed
pilot CPU                     0.5768 of the 3.0 CPU-hour cap; no STOP fired
```
