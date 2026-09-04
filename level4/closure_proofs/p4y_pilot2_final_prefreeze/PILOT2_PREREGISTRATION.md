# P4Y FINAL PRE-FREEZE PILOT (PILOT-2) — preregistration

```text
STATUS   = PRE-RESULT, FROZEN
BINDING  = NO
THIS IS NOT P4Y PRODUCTION
THIS IS NOT A P4Y CHECKPOINT A
THIS IS NOT PERMISSION TO RE-RUN THE 96-CELL SCIENTIFIC CAMPAIGN

P4_ORIGINAL_VERDICT      = PARTIAL   immutable
P4X_ADJUDICATION         = OVERRIDE_FAIL
P4X_SUCCESSOR_VERDICT    = FAIL      immutable
P4X_SCIENTIFIC_FAILURES  = NONE      immutable
P4Y_PILOT1_VERDICT       = NEEDS_ONE_MORE_PRE-FREEZE_PILOT   immutable
```

Frozen **before any result-bearing Pilot-2 design, calibration or validation
output exists**.  At the moment this document is committed, `results/` is
empty.

The only Pilot-2 numbers observed before this freeze are the outputs of the
**pre-freeze feasibility probe** recorded in §5.3, which measured nothing but
CPU-per-block and the Hill index of block means at candidate block sizes.  No
allocation rule was evaluated, no target was computed, no endpoint quantity
was formed, and the probe uses its own seed namespace that no result-bearing
phase reuses.

---

## 1. Why Pilot-1 was insufficient

Pilot-1 (branch `p4y-prefreeze-pilot`, commit `cefc03d`) is immutable and its
verdict stands at `NEEDS_ONE_MORE_PRE-FREEZE_PILOT`.  It is **not** relabelled
`READY` by this document or by anything Pilot-2 finds.

Two defects, and only these two:

**D1 — the endpoint was ambiguous and was amended after design results were
visible.**  Pilot-1 §6 defined `p_attain = P(realised relSE <= r*)` without
saying what to do with a replicate the cap refused to fund.  Read literally,
that ranked *more* careful rules *below* less careful ones and selected
nothing.  `AMENDMENT 1` fixed the reading — correctly, in our judgement — but
after design data existed.  A governance successor to a campaign that failed
on governance cannot rest on an endpoint re-defined once results were in view.

**D2 — the production cap was not measured.**  Pilot-1 ran at `B1 = 24`
blocks.  Production runs at 48–1784.  At pilot scale a 16× cap still left
about 12 % of routes `PRECISION_LIMITED`, and the entire cost tail was sizing
noise amplified by `1/kappa`.  There was a strong quantitative argument that
production would be one to two orders of magnitude tighter, but expectation is
not measurement.

Pilot-2 removes exactly these two, and nothing else.

## 2. What Pilot-2 inherits and will not revisit

Inherited unchanged, and mechanically checked in `tests/`: the P4 theorem;
A1–A7; the detector recursions; the six theorem-supported families and the two
outside-assumption families; the `m` grid `{1,2,3,5}`; the Route-A score
estimator; the Route-B Richardson CRN central difference at
`h = (0.05, 0.025)`; the Richardson combination formed per block; the Route-Q
role; the Gaussian consistency statistic; the correspondence gate
`relative <= 0.03 AND |z| <= 4`; `r*`; Lean; Arb.

```text
NEW THEOREM = NO      NEW LEAN = NO      NEW ARB = NO      NEW SCIENTIFIC CLAIM = NO
```

Inherited from Pilot-1 as settled and **not re-litigated**: the staged rule
`C_staged_safety_1.00` is the candidate; safety-factor inflation and
chi-square/quantile inflation are **not** resurrected.  Pilot-2 carries no
safety factor and no reserve factor.

Inherited from P4X as the frozen stage-1 rule: `kappa_stage1 = 0.5`, which
every one of P4X's 96 `production_plan` rows carries.  Pilot-2's kappa
question concerns the **staged growth** exponent only.

## 3. Frozen endpoint

The future production state space after the staged rule terminates is exactly

```text
ATTAINED   |   PRECISION_LIMITED
```

and there is no third state.  The **primary endpoint** is the probability of a
**valid governance disposition**, audited per replicate by
`src/p4y_pilot2/audit.py` from the recorded trajectory and the frozen cap,
without asking the rule what it thinks:

```text
valid governance disposition
  = ATTAINED
        with achieved relSE <= target
        and blocks executed <= cap_blocks
  or PRECISION_LIMITED
        with achieved relSE > target
        and the NEXT predeclared stage > cap_blocks
        and blocks executed <= cap_blocks
  and, in both branches, no scientific-outcome field reachable from the
      stopping decision
```

**A validly `PRECISION_LIMITED` route is a valid GOVERNANCE DISPOSITION and is
NOT a scientific success.**  The two are reported separately throughout and
are never added together into a single "success" number.

This endpoint can fail.  An implementation that executed past the cap,
mislabelled a terminal state, stopped without the cap actually refusing the
next stage, or let a forbidden field reach the allocation, is caught by the
auditor and counts against the endpoint.  Tests inject each of those
violations and assert the auditor rejects them.

## 4. Frozen statistical target

```text
r*                                    = 0.010823
  (inherited operative value; checkpoint_a.json records
   r_star_exact = 0.010823062977345114, carried for provenance only)

P4Y_GOVERNANCE_DISPOSITION_TARGET     delta = 0.95
P4Y_VALIDATION_CONFIDENCE             beta  = 0.05, one-sided
method                                exact Clopper-Pearson lower bound
```

At zero failures the Clopper–Pearson bound is computed mechanically as
`beta ** (1/R)`; it is never inferred qualitatively.  The method is fixed here
and is not changed after results.

**Secondary, reported separately and never merged into the primary:**

```text
P(ATTAINED)            with its own Clopper-Pearson lower bound
P(PRECISION_LIMITED)   with its own rate
```

Acceptability of the recommended `(kappa, cap)` requires **both** a valid
disposition bound at target **and** an acceptable split between the two
branches.  A rule that terminates correctly but routes an unacceptable share
into `PRECISION_LIMITED` is not acceptable:

```text
ATTAINMENT_FLOOR_POOLED     >= 0.95   pooled attainment rate
ATTAINMENT_FLOOR_STRATUM    >= 0.90   per (cell, stratum)
PRECISION_LIMITED_CEILING   <= 0.05   pooled, on validation
```

## 5. Production block-count reconstruction and strata

### 5.1 Reconstruction (allocation and cost metadata only)

From the immutable P4X artifacts `checkpoint_a/results/checkpoint_a.json`
(`production_plan`) and `production/results/c2_cell_ledger.json`, over all 48
`(configuration, route)` strata:

```text
stage-1 block counts    48 .. 1784     median 160
final   block counts    48 .. 9021     median 160
B_ref / B1              median 1.000,  minimum 0.0022
reference block counts  4, 13, 24, 48, 160, 300
kappa_stage1            0.5 on all 96 rows
```

The heavy-tail configurations do **not** differ by having a deficit; they
differ by having a *tiny reference* — 3.8 blocks of 250 000 paths, whose
relative-SE estimate carries a ~41 % standard deviation that the stage-1 law
then squares.

No P4X correspondence outcome, discrepancy, `z`, sign or pass/fail was read.

### 5.2 Frozen strata — every one an actual P4X stage-1 allocation

| id | `B_ref` | `B1` | regime | provenance |
|---|---|---|---|---|
| `T1` | 48 | 48 | low | the modal P4X stage-1 allocation, 10 of 48 strata |
| `T2` | 160 | 160 | middle | the median P4X stage-1 allocation |
| `T3` | 300 | 300 | high | the upper mode of the `B_ref/B1 == 1` group, 11 of 48 |
| `T4` | 4 | 215 | heavy-tail high-cost | `frozen/cusum@5/t1p5` Route B — the single configuration that consumed 18.60 of P4X's 24.75 CPU-hours |
| `T5` | 4 | 1784 | extreme | `frozen/sr@520.886/t1p5` Route B — the maximum P4X stage-1 allocation |

**There is deliberately no deficit axis.**  A precision deficit is not a
separate regime: stage 1 is sized from the reference, so a route a factor `D`
short of target simply receives a stage-1 allocation `D^(1/kappa_stage1)`
larger and is then at target in expectation at its own `B1`.  The deficit is
absorbed into `B1`, and `B1` is exactly what the strata span.

### 5.3 Cells, and the pre-freeze feasibility probe that fixed their block sizes

The probe measured only cost per block and the Hill index of the **block
means**.  Block sizes are the smallest probed size whose block means are
comfortably finite-variance, because that is what makes the block-**count**
regime faithful.

| probe: `reduced/cusum@2`, route, family | block size | Hill alpha of block means | s/block |
|---|---|---|---|
| Route A, `t1p5` | 1 000 | 2.50 | 0.00068 |
| Route A, `t1p5` | **5 000** | **5.45** | **0.00228** |
| Route A, `t1p5` | 250 000 | 13.18 | 0.098 |
| Route B, `t1p5` | 2 000 | 2.05 | 0.00988 |
| Route B, `t1p5` | **10 000** | **5.99** | **0.041** |
| Route A, `gaussian` | **1 000** | **85.67** | **0.00206** |

| cell | configuration | route | block size | strata | role |
|---|---|---|---|---|---|
| `H` | `reduced/cusum@2/t1p5` | A | 5 000 | `T1 T2 T3 T4 T5` | primary heavy-tail cell |
| `L` | `reduced/cusum@2/gaussian` | A | 1 000 | `T1 T2 T3` | finite-variance control |
| `RB` | `reduced/cusum@2/t1p5` | B | 10 000 | `T1` | Route-B robustness, **reported separately, excluded from the primary endpoint** |

**STOP rule:** if calibration measures a block-mean Hill alpha `<= 2.5` on any
cell, Pilot-2 stops — the block-count regime would not be faithful.

### 5.4 Target

`r*_pilot(cell, stratum)` is frozen **procedurally**, not as a number, because
no calibration output may exist before this document:

```text
r*_pilot(cell, stratum)
  := round_to_4_significant_figures(
         max over m in {1,2,3,5} of
             block_sd(cell, m) / ( sqrt(B1_nominal) * |block_mean(cell, m)| ) )

computed from CALIBRATION_BLOCKS = 2000 blocks drawn in the `calibration`
seed namespace, which no other phase reuses.
```

This places the nominal rule exactly on its target at the stratum's nominal
`B1`, which is the production situation.  `r* = 0.010823` itself is untouched
and is what P4Y production uses.

## 6. Frozen staged rule

```text
stage 1     B1_realised = max(8, ceil(B_ref * (relSE_ref / target)
                                       ** (1 / kappa_stage1)))
            with kappa_stage1 = 0.5, inherited from P4X unchanged,
            computed from a FRESH reference of B_ref blocks

loop        observe the route's own achieved relative SE at the worst m
            if achieved <= target                     -> ATTAINED
            next = ceil(B * (achieved/target) ** (1/kappa_blockcount))
            if next > cap_blocks                      -> PRECISION_LIMITED
            else execute exactly the next stage and repeat
```

No "at most one top-up".  The cap is the only terminator, so the terminal
state space is `{ATTAINED, PRECISION_LIMITED}` as a property of the control
flow.  No safety factor.  No reserve factor.

**Section 14 enforcement.**  `rule.trace` takes `(measure, b1, target, kappa,
pool_limit)` and nothing else; `measure` returns a float.  There is no
parameter, attribute or closure through which a discrepancy, sign, `z`,
Route-Q value, Gaussian consistency result, historical pass/fail or desired
verdict could enter.  Tests pin the signature, pin `Precision.__slots__` to
`(blocks, relative_se)`, and assert the auditor rejects a run that saw any
named forbidden field.

## 7. Frozen kappa candidates

```text
kappa_blockcount_A = 0.3197278911564626    (1 - 1/alpha at the frozen floor 1.47)
kappa_blockcount_B = 0.5                   (the finite-variance block-count rate)
```

Exactly two.  **No third fitted exponent is admissible**, before or after
results.  If neither satisfies the frozen criterion, Pilot-2 returns
`NEEDS_ONE_MORE_PRE_FREEZE_PILOT` or `DO_NOT_OPEN_P4Y` and fits nothing.

## 8. Frozen cap grid and cap semantics

```text
CAP_MULTIPLIERS = (1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0)
cap_blocks(stratum, M) = ceil(M * B1_nominal)        an INTEGER, per stratum
```

The cap is expressed against the stratum's frozen **nominal** `B1`, not
against whatever stage 1 realises, because in production a checkpoint freezes
the cap before the run.  A route whose realised stage-1 requirement already
exceeds the cap is `PRECISION_LIMITED` **from projected cost alone, before a
single block executes** — the inherited P4X semantics verbatim.

The cap grid is evaluated exactly, with no extra simulation: the stage
*sequence* does not depend on the cap, so one recorded trajectory per
`(replicate, kappa)` yields the outcome under every cap. `tests/` asserts that
this derivation equals an independent re-run under each cap.

## 9. Frozen selection criteria — design side only

**Cap selection**, per kappa, on `design` pooled over the primary cells and
all their strata: the **smallest** `M` in the grid such that

```text
(a) valid-disposition rate == 1.000                     exactly
(b) pooled attainment rate >= 0.95
(c) per (cell, stratum) attainment rate >= 0.90
```

If no `M` qualifies for a kappa, that kappa has no selectable cap.

**Kappa selection**: among kappas with a selectable cap, the one whose
`(kappa, cap)` pair has the smaller **design mean block multiplier**
`blocks used / B1_nominal`.  Ties: smaller `M`; then the inherited
`kappa_A = 0.3197278911564626`.

Validation never influences selection.  The full `kappa × cap` curve is
computed on validation and reported, but only the selected pair is decisive.

## 10. Frozen replication and seeds

```text
R_DESIGN            = 20   per (primary cell, stratum)
R_VALIDATION        = 59   per (primary cell, stratum)
R_DESIGN_ROBUSTNESS = 12   RB only
R_VALIDATION_ROBUST = 29   RB only

design replicate ids     0 ..
validation replicate ids 50 000 ..            disjoint by construction
```

`R = 59` is the smallest `R` with `delta**R <= beta` at
`delta = 0.95, beta = 0.05`, so a clean validation certifies the target.

Addressing is an **injective positional code** keyed by logical scientific
identity — campaign base, cell, stratum, namespace, replicate — with the
Philox `batch` carrying the logical block id and the internal counter carrying
the step.  Worker id, process id, shard index and scheduling order are **not
arguments** of the seed function and cannot be added without changing a
signature that a test pins.  **No modulo compression**; a test asserts `%`
does not appear in the seed path.  Campaign base `6 310 000 000`, a clean
`1e9` above Pilot-1's theoretical ceiling.

**Section 20 audit:** the complete frozen reachable address domain is
enumerated and `#addresses == #unique seeds` is asserted, both in `tests/` and
again at the start of every result-bearing phase, which refuses to execute on
any collision.

## 11. Frozen shard partition

Inherited from Pilot-1 unchanged:

```text
q, r = divmod(B, K)
shard_i = q + 1 for i < r, else q

require   sum(shard_blocks) == B
          max(shard_blocks) - min(shard_blocks) <= 1
          actual_executed_blocks == frozen_requested_blocks
          actual_executed_paths  == frozen_requested_blocks * frozen_block_size
```

No independent per-shard rounding.  The historical regression `B = 8801,
K = 5` must yield exactly 8 801 blocks and 2 200 250 000 paths, never 8 805
and 2 201 250 000, and the test fails on a discrepancy of one block.

## 12. Frozen budget and STOP rules

```text
PILOT2_CPU_CAP_HOURS = 3.0
```

Larger than Pilot-1's 2.0 only because reaching production-representative
block counts requires it (§22 of the brief permits this when predeclared); the
frozen design's worst case is 2.12 CPU-hours, computed before execution.  The
cap is never silently extended.

STOP rules, checked live:

1. cumulative CPU reaching 3.0 hours;
2. any replicate requesting more than `pool_limit = B_ref + 12 * B1_nominal`;
3. any calibration cell with block-mean Hill alpha `<= 2.5`;
4. any address collision in the frozen domain;
5. any shard partition whose executed total differs from the frozen total;
6. estimator drift — the non-drift or frozen-anchor tests failing.

A STOP is reported as a STOP and `PILOT-2 = INCOMPLETE`.  An auditor failure
is **not** a STOP: it counts against the primary endpoint, which is the point
of having an auditor.

## 13. Frozen cost-acceptance criterion

P4X's measured execution is the cost basis and nothing more:

```text
P4X total       = 24.749349116539157 CPU-hours
P4X max config  = 18.59941603055556  CPU-hours   (frozen/cusum@5/t1p5)
future caps     = 60 total, 40 per configuration   (inherited)

REQUIRED_RESERVE = 0.25
accept if   conservative projected total      <= 45.0 CPU-hours
      and   conservative projected max config <= 30.0 CPU-hours
```

The future cap is **not** set equal to the observed projection; the projection
must sit a quarter below it.

## 14. Frozen pass criteria

`READY_FOR_BINDING_CHECKPOINT` requires **all** of:

| | criterion |
|---|---|
| A | the frozen endpoint survives unchanged — zero post-result amendments |
| B | valid-disposition Clopper–Pearson lower bound `>= 0.95` |
| C | pooled attainment `>= 0.95`, its lower bound `>= 0.90`, and `PRECISION_LIMITED <= 0.05` |
| D | a kappa from the frozen pair is selected mechanically |
| E | `cap_blocks` is empirically supported at production-representative block counts |
| F | conservative projected total CPU `<= 45.0` h |
| G | conservative projected max-config CPU `<= 30.0` h |
| H | exact shard-sum invariant PASS |
| I | RNG collision-free addressing PASS |
| J | shard-invariant logical block identity PASS |
| K | no STOP fired |
| L | no post-result amendment occurred |

If any load-bearing item is unresolved the verdict is
`NEEDS_ONE_MORE_PRE_FREEZE_PILOT` or `DO_NOT_OPEN_P4Y`.  **An unresolved item
is never rounded into PASS.**

## 15. Anti-overfitting commitments

No tuning to the historical eight P4X cells; no cap chosen from their
shortfalls; no P4X correspondence outcome read; `r*` unmodified; the 3 % / `z`
gate unmodified; no post-result heavy-tail exception; no kappa outside the
frozen pair; no stage multiplier added after validation; `PRECISION_LIMITED`
not redefined; the endpoint not amended.

Pilot-1 and Pilot-2 samples are **governance-design evidence only** and may
never be used as scientific correspondence evidence.

## 16. Temporal integrity

```text
T0  this preregistration frozen and committed          results/ empty
T1  code and config hash frozen                        same commit
T2  first result-bearing execution                     run_phase.py calibration
T3  validation complete
T4  final report
```

No scientific or governance rule may be modified after T2.  An implementation
bug discovered after T2 is classified explicitly; if fixing it could alter
result-bearing semantics, Pilot-2 stops and restarts under a new pre-freeze
pilot rather than patching and continuing.
