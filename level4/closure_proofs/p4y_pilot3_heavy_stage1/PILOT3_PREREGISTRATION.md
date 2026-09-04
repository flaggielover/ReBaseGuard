# P4Y PILOT-3 — heavy-tail Stage-1 sizing closure pilot — preregistration

```text
STATUS  = PRE-RESULT, FROZEN
BINDING = NO
NOT P4Y PRODUCTION.  NOT A BINDING CHECKPOINT.
NOT PERMISSION TO RUN THE 96-CELL SCIENTIFIC CAMPAIGN.

P4_ORIGINAL_VERDICT     = PARTIAL   immutable
P4X_SUCCESSOR_VERDICT   = FAIL      immutable
P4X_SCIENTIFIC_FAILURES = NONE      immutable
P4Y_PILOT1_VERDICT      = NEEDS_ONE_MORE_PRE-FREEZE_PILOT   immutable
P4Y_PILOT2_VERDICT      = NEEDS_ONE_MORE_PRE_FREEZE_PILOT   immutable
```

Frozen **before any result-bearing execution**. At this commit `results/` is
empty.

The only Pilot-3 numbers observed before this freeze are a pre-freeze
feasibility probe of the UCB constructions on **synthetic** normal and
Student-t laws (§9.1) and cost-per-block figures inherited from Pilot-2. No
ReBaseGuard block was drawn for any candidate, no target was computed, and no
endpoint quantity was formed.

---

## 1. The single unresolved question

Pilot-2 closed everything except one thing. Its governance endpoint held
perfectly — valid disposition 1.0000, CP lower bound 0.9937, shard sum, the
8801/5 regression, the collision audit and shard-invariant identity all PASS,
staged termination sound, no third state, no scientific leakage — but **no
cap/kappa pair was selectable**, and it localised the cause precisely:

> at the historical heavy-tail reference of ~4 blocks, `relSE_ref` fell below
> its true value in 95–100 % of fresh draws with a median of 34–41 % of truth;
> Stage-1 raises that to the power `1/kappa`, so it bought a median 11–17 % of
> the true requirement.

Pilot-3 answers only:

> how to size the INITIAL production allocation for heavy-tail strata without
> systematically underestimating the precision requirement.

## 2. Scope boundary

Inherited unchanged and imported read-only: the P4 theorem and A1–A7; the
scientific correspondence meaning; the detectors; the `m` grid `{1,2,3,5}`;
the six theorem-supported families; the Route-A and Route-B estimators; the
finite-difference steps; the Richardson combination; the Route-Q role; the
Gaussian consistency statistic; the scientific thresholds; `r*`; Lean; Arb;
**the staged termination semantics**; **the exact sharding algorithm**; and
**the logical RNG addressing architecture**.

```text
NEW SCIENCE = NO    NEW THEOREM = NO    NEW LEAN = NO    NEW ARB = NO
```

Pilot-3 changes exactly one thing: **how Stage 1 is sized for the frozen
heavy-tail class.** Everything after Stage 1 is Pilot-2's staged rule,
imported from `p4y_pilot2.rule` and audited by `p4y_pilot2.audit`, both
untouched.

## 3. Production population — verified mechanically before freezing

From `checkpoint_a.json`:

```text
48 (configuration, route) strata
 8 with frozen heavy_tailed = True   -- all eight are t1p5
40 ordinary
the heavy set EQUALS the set that needed stage-1 sizing
```

The heavy class comes from **pre-existing frozen family metadata**, not from
any observed Pilot-3 failure: `heavy_tail_policy` records
`only_family_requiring_alpha_below_2 = "t1p5"`, with measured `alpha`
1.471–1.528 for t1p5 against a minimum of **2.695** for every other family.
`t1p5` is therefore the only family receiving the special treatment, and that
is decided by tail index measured before P4X ran.

**The frozen production mixture is 8 : 40**, and it — not any pilot cell count
— weights the primary rates. A per-heavy-stratum requirement is retained so
the 40 easy strata cannot average away failure on the 8 hard ones.

## 4. Strata, cells and weights

Four of P4X's eight actual heavy Stage-1 allocations, spanning the range and
including both cost-dominant configurations. Each stands for two production
heavy strata.

| id | `B_req` | weight | provenance |
|---|---|---|---|
| `S59` | 59 | 2 | `frozen/sr@520.886/t1p5` A, `B1 = 58.7` — the minimum |
| `S151` | 151 | 2 | `reduced/sr@20/t1p5` B, `B1 = 151.1` |
| `S215` | 215 | 2 | `frozen/cusum@5/t1p5` B, `B1 = 215.2` — **18.60 of P4X's 24.75 CPU-hours** |
| `S1784` | 1784 | 2 | `frozen/sr@520.886/t1p5` B, `B1 = 1783.6` — the maximum |
| `ORD` | 160, `B_ref = 160` | **40** | the median ordinary allocation; finite-variance control |

Cells: `H` `reduced/cusum@2/t1p5` Route A at 5 000 paths/block (all four heavy
strata); `O` `reduced/cusum@2/gaussian` Route A at 1 000 (the ordinary
control); `HB` `reduced/cusum@2/t1p5` Route B at 10 000 on `S59` (Route-B
robustness, reported separately, excluded from the primary endpoint).

## 5. Precision target

`r* = 0.010823`, inherited, unchanged. The Stage-1 objective is **not**
scientific PASS: it is a sufficiently reliable initial allocation that the
staged rule can reach `ATTAINED` or valid `PRECISION_LIMITED` within
affordable caps.

`target(stratum)` is frozen **procedurally**: the high-quality benchmark's
`block_sd / (sqrt(B_req) * |mean|)` at the worst `m`, so the stratum's true
requirement is exactly `B_req` blocks.

## 6. High-quality benchmark for the true reference precision

```text
BENCHMARK_BLOCKS             = 8000   (3000 for the Route-B robustness cell)
namespace                    = "benchmark", fresh, never reused by any other phase
relative uncertainty of sd   = 1/sqrt(2*(8000-1)) = 0.79 %
```

0.79 % is small against the 25–60 % effects this pilot must resolve, and it is
**documented rather than assumed**. A noisy estimate is never called truth.

## 7. Minimum reference block count — frozen grid

```text
BMIN_CANDIDATES = (4, 16, 32, 64, 128)
BMIN_BASELINE   = 4        the HISTORICAL value: baseline control only,
                           never a selectable production rule
BMIN_SELECTABLE = (16, 32, 64, 128)
```

Measured per candidate: downward-bias frequency, `relSE_hat / relSE_true`,
the spread of the estimate, the resulting Stage-1 allocation fraction, and CPU
overhead.

## 8. Kappa candidates — frozen pair, no third

```text
K1 = 0.5                    LEADING candidate on Pilot-2 evidence
K2 = 0.3197278911564626     CONTROL
```

0.5 is **not** declared selected before this pilot. No third exponent is
admissible, before or after results. Selection is mechanical under §12.

## 9. UCB constructions — frozen, three candidates plus a baseline

```text
UCB_LEVEL           = 0.95      one-sided, frozen
BOOTSTRAP_RESAMPLES = 2000      frozen
```

| id | construction | selectable |
|---|---|---|
| `point_baseline` | the Pilot-2 rule: no bound at all | **no** — control |
| `chi2` | normal-theory: `U = relSE_hat * sqrt((B-1)/chi2_{0.05}(B-1))` | yes |
| `t_squared` | one-sided Student-t upper bound on `sigma^2 = E[(X-mu)^2]`, built from the sample variance of the squared deviations | yes |
| `bootstrap` | nonparametric block bootstrap percentile upper bound on relSE | yes |

Three serious candidates, not a method zoo. `t_squared` is included because
`sigma^2` is a *mean* and so admits a t-bound without a normality assumption;
`bootstrap` because it assumes nothing about the block-mean law; `chi2`
because it is closed-form and cheap enough for production.

### 9.1 Pre-freeze synthetic probe (disclosed)

On synthetic laws only — no ReBaseGuard block drawn — coverage of the true
relSE at CV 0.40, the realistic scale:

| law | `B` | `point` | `chi2` | `t_squared` | `bootstrap` |
|---|---|---|---|---|---|
| normal | 32 | 0.483 | 0.937 | 0.850 | 0.875 |
| normal | 128 | 0.507 | 0.932 | 0.893 | 0.920 |
| t(5.6) | 32 | 0.425 | 0.856 | 0.781 | 0.798 |
| t(5.6) | 128 | 0.439 | 0.845 | 0.841 | 0.864 |

The point estimate covers the truth 42–51 % of the time — the Pilot-2
mechanism, reproduced from first principles. This probe informs nothing that
is frozen beyond the candidate set itself; the pilot measures the real thing.

## 10. Stage-1 sizing formula

```text
U   = UCB(reference block means at B_ref)          one-sided, level 0.95
B1  = max(8, ceil( B_ref * (U / r*) ** (1/kappa) ))
```

Rounding happens **exactly once, at the logical total-block level**. Never per
shard. `B_ref = Bmin` for heavy strata and the historical value for ordinary
strata — brief §18: the heavy-tail reference inflation applies **only** to the
frozen tail class, so the 40 ordinary strata are not penalised to fix the 8.

The point-estimate allocation `B1_point` is recorded alongside on every
replicate, so the two can be compared draw by draw.

## 11. Cap definition and grid

```text
cap_blocks = ceil( multiplier * B1 )
CAP_MULTIPLIERS = (1.25, 1.5, 2.0, 3.0)
```

The cap is anchored to the **projected requirement** the frozen UCB rule
produces, not to a nominal `B1` that may itself be badly underestimated —
which is exactly what Pilot-2 exposed. It is computed before any Stage-1 block
executes, so a route whose projection already exceeds it is
`PRECISION_LIMITED` from projected cost alone.

An absolute ceiling of `40 * B_req` bounds pilot cost. A Stage-1 allocation
above it is **refused and recorded INVALID**, counting against the candidate,
never in its favour.

## 12. Frozen criteria — a candidate is selectable only if ALL hold

| | criterion | threshold |
|---|---|---|
| 1 | valid-disposition Clopper–Pearson lower bound | `>= 0.95` |
| 2 | production-mixture-weighted attainment | `>= 0.95` |
| 3 | production-mixture-weighted `PRECISION_LIMITED` | `<= 0.05` |
| 4 | **every** heavy stratum: attainment `>= 0.90` and PL `<= 0.10` | per stratum |
| 5 | no invalid disposition — covers third state, cap overrun and leakage | `0` |
| 8 | conservative projected total CPU | `<= 45.0 h` |
| 9 | conservative projected max-configuration CPU | `<= 30.0 h` |
| 10 | all execution-governance regression tests | PASS |

Criteria 6 and 7 of the brief (no cap overrun, no scientific leakage) are
enforced by the auditor and are therefore subsumed in criterion 5, which the
auditor makes falsifiable.

**A failed heavy stratum is never averaged away**: criterion 4 is per stratum
and independent of the mixture weights.

### 12.1 Frozen tie-break, applied to DESIGN only

```text
1. lowest conservative total CPU
2. lowest conservative max-configuration CPU
3. lowest PRECISION_LIMITED rate
4. simpler rule            chi2 (closed form) < t_squared < bootstrap
5. smaller Bmin
```

Validation never selects. It reports the full candidate curve and the selected
candidate's independent numbers.

## 13. Cost thresholds and projection

```text
inherited campaign caps   60 h total, 40 h per configuration
REQUIRED_RESERVE          0.25
accept if   conservative total      <= 45.0 h
      and   conservative max config <= 30.0 h
```

The future cap is **not** set equal to the projection; the projection must sit
a quarter below it.

**Projection basis.** P4X's measured `cost_ledger.json` (24.749 CPU-hours,
18.599 on `frozen/cusum@5/t1p5`), apportioned to routes within each
configuration in proportion to `blocks * block_size * rate` — apportionment
never changes a configuration total, so the max-configuration figure is exact.
Each production heavy stratum's requirement is derived from P4X's Stage-1
**achieved relative SE** under the candidate kappa. That is precision and cost
metadata: no discrepancy, no `z`, no pass/fail is read, and it is used only
for the projection §17 demands — never to select a rule, kappa, cap or Bmin.

Sanity check computed before freezing: at `kappa = 0.3197` this basis sums to
13 363 blocks against the 13 367 P4X actually executed. The four-block gap is
exactly the sharding over-execution defect Pilot-1 repaired.

Reported decomposition: heavy reference expansion; heavy Stage-1 and top-ups;
ordinary unchanged.

## 14. Replication, seeds, budget, STOP rules

```text
R_DESIGN     = 20   per (primary cell, stratum)      ids 0..
R_VALIDATION = 59   per (primary cell, stratum)      ids 50 000..
robustness   = 12 design / 29 validation, HB only, excluded from the primary
```

Addressing is Pilot-2's injective positional code with campaign base
`9 310 000 000`, a clean `1e9` above Pilot-2's theoretical ceiling. Keyed by
logical identity only; no worker, pid, shard or schedule argument; no modulo
compression. The complete frozen reachable domain is enumerated and checked
collision-free, again at the start of every result-bearing phase, which
refuses to execute on any collision.

```text
PILOT3_CPU_CAP_HOURS = 3.0        stated before T2, never extended
```

STOP rules: cumulative CPU reaching 3.0 h; a trace exceeding the absolute
ceiling; a benchmark cell with block-mean Hill alpha `<= 2.5`; an address
collision; a shard-sum breach; estimator drift. A STOP is reported as a STOP.
An auditor failure is **not** a STOP — it counts against the endpoint.

## 15. Temporal integrity and the no-repair rule

```text
T0 preregistration frozen      results/ empty
T1 code and config frozen      same commit
T2 first result-bearing execution
T3 design complete
T4 validation complete
T5 report complete
```

After T2: **no** endpoint amendment, no new candidate, no new safety factor,
no changed kappa, no changed cap grid, no changed block minimum, no changed
statistical method. If a result-bearing semantic bug is found, Pilot-3 STOPs
and classifies it rather than fixing and continuing. A pure reporting bug may
be repaired only if it provably cannot alter results or selection, and must be
disclosed.

**If the design fails, Pilot-3 reports failure. It does not rescue it.**

## 16. Kill criteria

`DO_NOT_FREEZE_P4Y` if: no UCB/minimum-reference design prevents systematic
under-allocation; no candidate clears the heavy-tail attainment floor;
reliable sizing needs implausible reference computation; conservative
production stays above cap feasibility; governance simplicity is lost; or
scientific scope would have to change.

`NEEDS_ONE_MORE_PILOT` only for one genuinely narrow unresolved design
quantity — never merely because further optimisation is conceivable.

If at least one candidate satisfies every frozen criterion, the verdict is
`READY_FOR_BINDING_CHECKPOINT` and **piloting stops**.
