# P4Y PILOT-4 — heavy-tail precision measurement feasibility gate — report

```text
STATUS = PILOT-4 COMPLETE, NON-BINDING
P4Y_BINDING_CHECKPOINT_CREATED = NO
P4Y_PRODUCTION_RUN             = NO

P4_ORIGINAL_VERDICT     = PARTIAL   immutable
P4X_SUCCESSOR_VERDICT   = FAIL      immutable
P4X_SCIENTIFIC_FAILURES = NONE      immutable
P4Y_PILOT1_VERDICT      = NEEDS_ONE_MORE_PRE-FREEZE_PILOT   immutable
P4Y_PILOT2_VERDICT      = NEEDS_ONE_MORE_PRE_FREEZE_PILOT   immutable
P4Y_PILOT3_VERDICT      = NEEDS_ONE_MORE_PRE_FREEZE_PILOT   immutable
```

---

## 1. Immutable history

| | |
|---|---|
| `P4_ORIGINAL_VERDICT` | `PARTIAL` |
| `P4X_SUCCESSOR_VERDICT` | `FAIL` — governance and sampling integrity, not a scientific contradiction |
| `P4X_SCIENTIFIC_FAILURES` | `NONE` — 88/96 binding PASS, 0 scientific FAIL |
| `P4Y_PILOT1_VERDICT` | `NEEDS_ONE_MORE_PRE-FREEZE_PILOT` |
| `P4Y_PILOT2_VERDICT` | `NEEDS_ONE_MORE_PRE_FREEZE_PILOT` |
| `P4Y_PILOT3_VERDICT` | `NEEDS_ONE_MORE_PRE_FREEZE_PILOT` |
| Pilot-3 preregistration | `8dbb7d2ea5dbe6eaad2cfff0d89e44cc6fbdc3af` |

No earlier pilot is repaired or relabelled. P4X is absent from this branch;
the Pilot-1, Pilot-2 and Pilot-3 namespaces are present, imported read-only,
and unmodified.

## 2. The exact Pilot-3 measurement defect

Pilot-3 froze its benchmark uncertainty as `1/sqrt(2(n-1)) = 0.79 %` at
`n = 8000` — normal theory, applied to a law that is not remotely normal.
Measured on the blocks it drew:

* one block in 8 000 carried **29.3 %** of the total squared deviation;
* the top five carried **60.2 %**;
* eight disjoint 1 000-block sub-samples gave standard deviations spanning
  **0.834 – 2.672**;
* nested prefixes showed no convergence;
* at the **production** block size of 250 000 paths, one block in 400 still
  carried ~32 %, and two half-samples differed by ~**2.79×**.

So Pilot-3's "truth" was another draw of the same noisy statistic, and every
coverage figure computed against it was meaningless. Pilot-4 uses **no
normal-theory SD-uncertainty formula anywhere.**

## 3. Preregistration hash and temporal ledger

```text
P4Y_PILOT4_PREREGISTRATION = 783151b5417c410d7aecc2e924cc62e2980463a9
```

That commit contains the preregistration, all source and all tests, and
**zero files under `results/`**, verified by `git ls-tree --full-tree`.

| | event | evidence |
|---|---|---|
| `T0` | preregistration frozen | `783151b`, `results/` empty |
| `T1` | code and config frozen | same commit |
| `T2` | first result-bearing execution | 2026-09-04T08:29:37Z, master phase |
| `T3` | measurement pools complete | `results/TEMPORAL_LEDGER.txt` |
| `T4` | diagnostics complete | " |
| `T5` | report complete | " |

## 4. The measurement object

For a frozen `(configuration, route, window m)` and a logical block size `b`
paths, `X^(b)` is the per-block value the frozen Priority-4 estimator returns
for one block of `b` independent paths.

```text
ESTIMAND     theta(b) = sd( X^(b) ) / | E X^(b) |
ESTIMATOR    theta_hat = s / |xbar|  over B_ref logical blocks, ddof = 1
IDENTITY     relSE(B) = theta(b) / sqrt(B)      exactly
```

Future governance compares `relSE(B)` against `r*`, so estimating `relSE` to
within a multiplicative factor is the *same problem* as estimating `theta` to
within that factor — with `B` divided out, making the question about the block
law rather than about any allocation.

**Finite variance is not assumed.** `theta` exists only if `X^(b)` has finite
variance, and that is precisely what Pilot-3 put in doubt. Pilot-4 treats it
as empirical: a block size is usable only if its benchmark passes the frozen
stability criteria. Hill indices are reported as secondary and never accepted
as a substitute. No robust or trimmed scale is substituted, because that would
estimate a different functional and change the meaning of the inherited
standard error.

### 4.1 The enabling identity — verified, not assumed

Every frozen per-block statistic is a **plain average of per-path
contributions**: Route A directly, Route B because the Richardson combination
`(4 D(h/2) − D(h))/3` is linear in the two path averages. Therefore a block
value over `k·n` paths equals the mean of `k` independent block values over
`n` paths — **exactly**.

Verified bit-for-bit by splitting a simulated block's own paths:
`|diff| = 0.000e+00` on both routes, pinned by
`tests/test_aggregation_identity.py`.

This is load-bearing twice. A single 1 000 000-path block measured **318 MB**
peak RSS, so 4 000 000 would be ~1.2 GB and the direct route does not scale to
the frozen grid. And one base pool of 50 000-path blocks serves **every** block
size, which is what makes a three-block-size sweep affordable. Analyses at
different block sizes therefore share paths — disclosed, and it makes the
across-block-size comparison a common-random-number one.

## 5. Frozen grids

```text
BASE_BLOCK_PATHS = 50 000
BLOCK_SIZES      = (250 000, 1 000 000, 4 000 000)
BREF_GRID          250 000 : (32, 64, 128, 256)
                 1 000 000 : (32, 64, 128)
                 4 000 000 : (16, 32, 64)
```

Projected production reference overhead for all eight heavy strata, at the
measured P4X heavy rate of 12 s/1e6 paths:

| `B_ref` | 250 000 | 1 000 000 | 4 000 000 |
|---|---|---|---|
| smallest | 0.21 h | 0.85 h | 1.71 h |
| largest | 1.71 h | 3.41 h | 6.83 h |

against a frozen affordability limit of 10 CPU-hours — one fifth of the
inherited 45 h envelope. **Every grid point is affordable, so affordability is
not the binding constraint. Stability is.**

## 6. Benchmark construction and frozen admissibility

Two **independent** master pools per `(stratum, block size)`; `theta_bench` on
the two combined; admissible only if all four frozen checks pass:

```text
A  disjoint split   max(theta_pool0, theta_pool1)/min(...)  <= 1.25
B  growing prefix   theta(full)/theta(half)  in [1/1.15, 1.15]
C  extreme top-1    largest block's share of squared deviation <= 0.10
D  extreme top-5    top five blocks' share <= 0.30
```

For a well-aggregated law at these pool sizes the top-1 share should sit near
1–2 %, so the 0.10 threshold is generous by construction.

## 7. Accuracy target, replication, confidence

```text
c = 1.25          success is  1/c <= theta_hat/theta_bench <= c
p_target = 0.90
beta = 0.05       one-sided exact Clopper-Pearson
R = 29            smallest R with p**R <= beta; 29/29 gives 0.9019
secondary band    1.50, reported, never decisive
```

`c = 1.25` on `relSE` is a factor `1.56` on a sample size at the classical
rate. It was **not** set from observed variability.

## 8. Benchmark results — the decisive finding

Two independent master pools per `(stratum, block size)`, combined; frozen
thresholds `split <= 1.25`, `prefix in [0.870, 1.150]`, `top-1 <= 0.10`,
`top-5 <= 0.30`.

| stratum | route | `b` | pool blocks (each) | `theta` | split | prefix | top-1 | top-5 | verdict |
|---|---|---|---|---|---|---|---|---|---|
| `H` `cusum@2/t1p5` | A | 250 000 | 2048 | 0.09197 | 1.105 | 1.054 | **0.086** | 0.269 | **ADMISSIBLE** |
| `H` | A | 1 000 000 | 1024 | 0.08158 | **1.793** | **1.450** | **0.573** | **0.694** | REJECTED |
| `H` | A | 4 000 000 | 512 | 0.03464 | **1.366** | **1.196** | **0.382** | **0.489** | REJECTED |
| `HSR` `sr@20/t1p5` | A | 250 000 | 2048 | 0.12210 | 1.041 | 0.980 | **0.250** | **0.512** | REJECTED |
| `HB` `cusum@2/t1p5` | B | 250 000 | 512 | 0.22319 | 1.025 | 1.013 | **0.206** | **0.558** | REJECTED |
| `O` `cusum@2/gaussian` | A | 250 000 | 1024 | 0.00198 | 1.048 | 0.977 | **0.006** | 0.027 | **ADMISSIBLE** |

```text
admissible benchmark across the heavy strata measured at that block size
  250 000    NO   (H passes; HSR and HB fail)
  1 000 000  NO   (H fails on all four checks)
  4 000 000  NO   (H fails on all four checks)
```

**No block size in the frozen grid yields an admissible benchmark.**

### 8.1 Agreement measures are fooled; the concentration measure is not

The single most useful thing Pilot-4 found is the *disagreement between the
criteria* at 250 000:

| stratum | split | prefix | top-1 |
|---|---|---|---|
| `H` | 1.105 | 1.054 | 0.086 |
| `HSR` | **1.041** | **0.980** | **0.250** |
| `HB` | **1.025** | **1.013** | **0.206** |

On `HSR` and `HB` the two *independent* master pools agree to within 4 % and
2 %, and the growing-prefix curve is flat to within 2 % — every agreement
measure says "stable" — while a **single block carries 21–25 % of the total
squared deviation** and the top five carry 51–56 %.

That is exactly the trap brief §13 asks to be distinguished: a law can look
beautifully converged in every consistency check and still be a handful of
rare extremes wearing a standard deviation. Two pools of 2048 blocks agree
because each contains a similar handful — not because the scale has
aggregated. Had Pilot-4 frozen only split and prefix criteria, it would have
declared these benchmarks admissible and been wrong in the same way Pilot-3
was.

### 8.2 The ordinary control passes, so the framework is not the problem

At the same block size, the finite-variance control gives `top-1 = 0.006` and
`top-5 = 0.027` — against `0.086`, `0.250` and `0.206` for the heavy strata.
Under normality the expected top-1 share at these pool sizes is about 0.4–1.4 %,
so the control sits essentially where a well-aggregated law should, and the
heavy strata sit **15× to 60×** above it.

The framework detects a stable regime when one exists (brief §20). The
negative result on the heavy strata is therefore a property of the block law,
not an artefact of the instrument.

### 8.3 Two honest caveats about these numbers

**The top-1 criterion is n-dependent, and pool sizes differ.** The share a
single block carries falls roughly as `1/n`; the combined pools are 4096
blocks at 250 000, 2048 at 1 000 000 and 1024 at 4 000 000 for `H`, and 1024
for `HB`. So the frozen absolute threshold of 0.10 bites harder at larger `b`
and on `HB`. This is a weakness of the frozen design and it is disclosed, not
repaired. It does **not** drive the conclusion: `H` at 1 000 000 and 4 000 000
also fail the *scale-free* split and prefix criteria (1.793 / 1.450 and
1.366 / 1.196), and `HSR` versus `H` at 250 000 is an exactly like-for-like
comparison — same pool size, same block size, same route — with top-1 of 0.250
against 0.086.

**Analyses at different block sizes share base paths.** That was frozen and
disclosed in advance: one base pool of 50 000-path blocks serves every block
size, which is what makes the sweep affordable. A consequence is that where an
extreme base block falls relative to an aggregation boundary affects the
larger-`b` results, which is part of why `H` at 1 000 000 looks worse than at
4 000 000. The 250 000 conclusions rest on **two independent pools**, which is
the stronger evidence and is not affected by this.

### 8.4 Aggregation is working; the tail is simply still there

A positive secondary observation. If the block-mean law had finite variance
and were aggregating normally, `theta` would fall as `1/sqrt(b)`. From
Pilot-3's measurement of `theta = 0.626` for `H` at 5 000 paths to Pilot-4's
`0.09197` at 250 000 is a factor of 6.8 for a 50× block-size increase, against
`sqrt(50) = 7.07`. So the scale *is* aggregating at close to the classical
rate — the problem is not that aggregation fails, but that at every affordable
block size a handful of blocks still carries most of the variance, so the
*estimate* of that scale from an affordable reference remains unreliable.

## 9. Reference accuracy — candidate by candidate

29 fresh disjoint reference draws per `(stratum, b, B_ref)`; success is
`theta_hat / theta_bench` inside `[1/1.25, 1.25]`; bound is exact
Clopper-Pearson at `beta = 0.05`; target `0.90`.

| stratum | `b` | `B_ref` | median ratio | q05 | q95 | under-estimation | inside band | lower bound | benchmark |
|---|---|---|---|---|---|---|---|---|---|
| `H` | 250 000 | 32 | 0.727 | | | 0.79 | 7 / 29 | 0.1192 | admissible |
| `H` | 250 000 | 64 | 0.797 | | | 0.66 | 6 / 29 | 0.0942 | admissible |
| `H` | 250 000 | 128 | 1.412 | | | 0.45 | 5 / 29 | 0.0705 | admissible |
| `H` | 250 000 | **256** | 1.302 | | | 0.28 | **10 / 29** | **0.2005** | admissible |
| `H` | 1 000 000 | 32 | 0.699 | | | 0.72 | 9 / 29 | 0.1725 | rejected |
| `H` | 1 000 000 | 64 | 0.716 | | | 0.79 | 6 / 29 | 0.0942 | rejected |
| `H` | 1 000 000 | 128 | 0.660 | | | 0.79 | 2 / 29 | 0.0124 | rejected |
| `H` | 4 000 000 | 16 | 0.822 | | | 0.76 | 9 / 29 | 0.1725 | rejected |
| `H` | 4 000 000 | 32 | 0.755 | | | 0.72 | 7 / 29 | 0.1192 | rejected |
| `H` | 4 000 000 | **64** | 0.872 | | | 0.59 | **11 / 29** | **0.2293** | rejected |
| `HSR` | 250 000 | 32 | **0.483** | | | **0.90** | 5 / 29 | 0.0705 | rejected |
| `HSR` | 250 000 | 64 | 0.559 | | | **0.93** | 5 / 29 | 0.0705 | rejected |
| `HSR` | 250 000 | 128 | 0.632 | | | 0.83 | 6 / 29 | 0.0942 | rejected |
| `HSR` | 250 000 | 256 | 0.722 | | | 0.76 | 8 / 29 | 0.1453 | rejected |
| `HB` | 250 000 | 32 | 0.790 | | | 0.69 | 9 / 29 | 0.1725 | rejected |
| `HB` | 250 000 | 64 | 0.842 | | | 0.66 | 9 / 29 | 0.1725 | rejected |
| **`O` control** | 250 000 | 32 | 1.034 | | | 0.45 | 25 / 29 | 0.7116 | admissible |
| **`O` control** | 250 000 | 64 | 0.995 | | | 0.55 | 28 / 29 | 0.8466 | admissible |
| **`O` control** | 250 000 | **128** | **1.015** | | | 0.41 | **29 / 29** | **0.9019** | admissible |

(The q05/q95 columns are recorded in `results/reference.json` and omitted here
for width; `verify_report4.py` re-derives every figure in this table.)

### 9.1 The control reaches the target; no heavy stratum comes close

```text
ordinary control, B_ref = 128 :  29/29 inside the band, lower bound 0.9019
                                 -- exactly the frozen target, met
heavy strata, best case       :  11/29, lower bound 0.2293
```

At the same block size and the same reference size, the finite-variance
control lands inside `±25 %` **every time** while the primary heavy stratum
lands inside 5 times in 29. The frozen apparatus is capable of certifying a
measurement pair; it certifies the control and refuses every heavy one.

### 9.2 Under-estimation, measured against a trustworthy benchmark

Pilot-3 could only observe that reference estimates fell below "truth"; it had
no trustworthy truth. On `H` at 250 000, where the benchmark **is** admissible,
under-estimation runs **0.28 – 0.79** and reaches **0.90 – 0.93** on `HSR` at
the smaller references. Pilot-3's mechanism is confirmed against a benchmark
that passed its own stability criteria — and it is not merely a bias that a
one-sided bound could absorb, because the *spread*, not just the location, is
too wide: the median ratio wanders between 0.48 and 1.41 across candidates
rather than converging on 1.

## 10. Frozen feasibility criterion, candidate by candidate

| `b` | `B_ref` | reference paths | production overhead | min heavy rate | min heavy LB | affordable | selectable |
|---|---|---|---|---|---|---|---|
| 250 000 | 32 | 8.0e6 | 0.21 h | 0.1724 | 0.0705 | yes | **no** |
| 250 000 | 64 | 1.6e7 | 0.43 h | 0.1724 | 0.0705 | yes | **no** |
| 250 000 | 128 | 3.2e7 | 0.85 h | 0.1724 | 0.0705 | yes | **no** |
| 250 000 | 256 | 6.4e7 | 1.71 h | 0.2759 | 0.1453 | yes | **no** |
| 1 000 000 | 32 | 3.2e7 | 0.85 h | 0.3103 | 0.1725 | yes | **no** |
| 1 000 000 | 64 | 6.4e7 | 1.71 h | 0.2069 | 0.0942 | yes | **no** |
| 1 000 000 | 128 | 1.28e8 | 3.41 h | 0.0690 | 0.0124 | yes | **no** |
| 4 000 000 | 16 | 6.4e7 | 1.71 h | 0.3103 | 0.1725 | yes | **no** |
| 4 000 000 | 32 | 1.28e8 | 3.41 h | 0.2414 | 0.1192 | yes | **no** |
| 4 000 000 | 64 | 2.56e8 | 6.83 h | 0.3793 | 0.2293 | yes | **no** |

```text
SELECTED MEASUREMENT PAIR = NONE
best min-heavy lower bound anywhere in the grid = 0.2293   target 0.90
```

**Every candidate is affordable and none is accurate.** The production
reference overhead ranges from 0.21 to 6.83 CPU-hours against a 10-hour
allowance, so cost never bound; the measurement did.

## 11. CPU cost

```text
master phase     4 519.8 CPU-s   two independent pools per stratum x block size
reference phase  8 248.0 CPU-s   29 fresh disjoint draws per stratum
TOTAL            3.5466 CPU-hours of the frozen 5.0 cap
```

Projected production measurement overhead, had a pair been selectable, is the
"production overhead" column of §10 — 0.21 to 6.83 CPU-hours for all eight
heavy strata. That figure is now moot.

## 12. Shard, RNG and leakage regression — all PASS

```text
P4Y_EXACT_SHARD_SUM_INVARIANT        = PASS
P4Y_HISTORICAL_8801_BLOCK_REGRESSION = PASS
P4Y_RNG_COLLISION_AUDIT              = PASS
P4Y_SHARD_INVARIANT_BLOCK_IDENTITY   = PASS
P4Y_SCIENTIFIC_LEAKAGE_GUARD         = PASS
```

Regression only; nothing was redesigned (brief §21).
`partition(8801, 5) = [1761, 1760, 1760, 1760, 1760]` summing to **8 801**
blocks and **2 200 250 000** paths, with the defective historical
implementation pinned at 8 805 / 2 201 250 000. Block outputs are
bit-identical across `K ∈ {1,2,5,7,13,64}` and pooled summaries equal the
unsharded formula exactly. The frozen address domain is collision-free,
campaign base `12 310 000 000`, no modulo compression, no worker / pid / shard
/ schedule argument in the seed.

**Leakage guard.** A test parses every source file, strips docstrings and
comments through the AST, and asserts with a word-boundary matcher that no
scientific-outcome identifier — discrepancy, `z`, gate, pass/fail, Route-Q,
Gaussian consistency, verdict, historically-failed — occurs in executable
code. A companion test asserts the matcher is not vacuous (it must fire on
`gate = 3` and must not fire on `aggregate(x, 5)`).

**No allocation rule.** A further test asserts that the tokens `cap_blocks`,
`stage1`, `size_stage1`, `top_up`, `PRECISION_LIMITED` and `kappa` do not
occur in Pilot-4's executable code at all (brief §2).

## 13. STOP ledger

| STOP rule | fired? |
|---|---|
| cumulative CPU reaching the frozen 5.0 h cap | no |
| address collision in the frozen domain | no |
| shard-sum breach | no |
| estimator drift | no |
| §11 classify-and-stop (result-bearing semantic defect after T2) | **no** |

```text
P4Y_PILOT4_STOP_FIRED = NO
```

Unlike Pilot-3, Pilot-4 executed its frozen experiment to completion. Its
result is negative, and a negative result executed as specified is a finding,
not an interruption.

## 14. Amendment ledger

```text
P4Y_PILOT4_POST_RESULT_AMENDMENTS = 0
```

Zero. No threshold, band, grid, block size, `B_ref`, criterion, confidence
level or budget was changed after T2. In particular the `top-1 <= 0.10`
threshold — the criterion that decides the verdict on two of three heavy
strata — was frozen at T0 and is applied exactly as written, including where
§8.3 notes it is `n`-dependent and therefore imperfect. The imperfection is
disclosed, not repaired.

## 15. Is benchmark stability established?

```text
P4Y_BENCHMARK_STABILITY = FAIL
```

Not for the heavy class. It is established for the finite-variance control
(`top-1 = 0.006`, split 1.048, prefix 0.977) and for exactly one heavy
stratum, `H` at 250 000 (`top-1 = 0.086`, split 1.105, prefix 1.054). It is
**not** established for the SR heavy stratum or the Route-B heavy stratum at
any tested block size, nor for `H` at 1 000 000 or 4 000 000.

Since a future P4Y must adjudicate all eight production heavy strata — four
configurations across both routes, SR included — an instrument that is
trustworthy on one of them is not an instrument.

## 16. Is precision measurement governable?

```text
P4Y_MEASUREMENT_FEASIBILITY = NOT_FEASIBLE   (under the frozen envelope)
```

No. Under the entire frozen grid — block sizes 250 000, 1 000 000 and
4 000 000, reference counts from 16 to 256, and a reference budget that every
grid point satisfies — no block size produces a benchmark admissible across
the heavy strata measured at it. Affordability was never the binding
constraint: the most expensive grid point costs 6.83 CPU-hours of production
reference against a 10-hour frozen allowance. **The constraint is the block
law itself.**

The mechanism is now precisely characterised, and it is not that aggregation
fails. §8.4 shows `theta` falling at very close to the classical `1/sqrt(b)`
rate from 5 000 to 250 000 paths per block. What persists is that at every
affordable block size a handful of blocks still carries most of the variance,
so an *estimate* of the scale from an affordable reference remains a lottery
over whether those blocks were drawn.

## 17. Verdict

```text
P4Y_PILOT4_VERDICT = DO_NOT_FREEZE_P4Y
```

The frozen kill gate (brief §25) fires on its first clause: **no block size
achieves a stable benchmark.** Under the entire frozen grid and CPU envelope,
no `(block size, B_ref)` pair is selectable, because criterion A — an
admissible benchmark on every heavy stratum measured at that block size —
fails at 250 000 (`HSR` and `HB` rejected), at 1 000 000 (`H` rejected on all
four checks) and at 4 000 000 (`H` rejected on all four checks).

**This is not `PILOT4_INCOMPLETE`.** Brief §26 reserves that for an external,
non-scientific interruption. Pilot-4 executed its frozen experiment to
completion, inside its frozen budget, with zero post-result amendments and no
STOP. A properly executed negative feasibility result is `DO_NOT_FREEZE_P4Y`.

**And no Pilot-5.** Brief §28 fixes the state machine: measurement FAIL →
`DO_NOT_FREEZE_P4Y`. Pilot-4 does not propose a successor pilot, and this
report does not treat the negative result as an invitation to keep
optimising. There is no `SIZING REPLAY`, because the measurement gate that
would have licensed one did not pass.

### 17.1 What is actually established

Positively, and worth preserving:

* The **governance architecture** developed across Pilots 1–3 is sound and has
  now been regression-checked a fourth time: exact shard sum, the 8801/5
  regression, collision-free worker-free logical addressing, shard-invariant
  block identity, and a scientific-leakage guard — all PASS.
* The **measurement framework works**: it certifies a stable regime for the
  finite-variance control (`top-1 = 0.006`) and for `H` at 250 000, and
  refuses the rest. It is not a blunt instrument that rejects everything.
* The **block-mean scale aggregates at close to the classical rate**
  (§8.4), so there is no pathology in the estimator's convergence.
* The failure is specific and named: for `t1p5` at `m = 1`, at every
  affordable block size, a handful of blocks carries most of the variance, so
  an affordable reference cannot pin the scale.

### 17.2 Why this closes the successor question rather than deferring it

Three successive pilots each localised the same object from a different
direction — Pilot-2 found the cap could not be chosen, Pilot-3 found the
Stage-1 reference was systematically optimistic, and Pilot-4 finds the
underlying scale is not reliably measurable at all. A fourth pilot would be
measuring the same estimand with the same estimator, and the frozen envelope
already spans a 16× range of block sizes and a 16× range of reference counts
at costs the campaign can afford.

The remaining moves are **not governance moves**. Making the `t1p5` precision
scale measurable would require changing the estimand or the estimator — a
variance-reduced Route-B construction for the heavy family, a different
precision functional, or a different stopping criterion — and every one of
those changes the scientific meaning that P4X, P4Y and this whole pilot line
were built to preserve. That is a research question about the P4 estimator,
not a pre-freeze governance pilot, and it is explicitly outside the frozen
scope of all four pilots.

`P4_SCIENTIFIC_LINE_STATUS = UNCHANGED_PARTIAL`. The P4 line stands where the
original adjudication left it, and P4X's `FAIL` stands as governance failure
with `P4X_SCIENTIFIC_FAILURES = NONE`. Nothing in four pilots contradicted a
single scientific result; what they established is that the *governance* of
heavy-tailed precision, on the inherited estimand, is not attainable at
attainable cost.

## 18. No Checkpoint-A draft

Brief §29 conditions a Checkpoint-A draft on the measurement gate passing. It
did not. No P4Y Checkpoint A architecture is drafted, and none is activated.

The four governance components validated across Pilots 1–3 — staged
termination with the cap as sole terminator, mechanically audited
`PRECISION_LIMITED` semantics, the exact shard partition with a
`delta_blocks == 0` ledger, and collision-free worker-free logical RNG
addressing — remain available to any future campaign that has a trustworthy
precision instrument. They are not the blocker and never were.

## 19. Next action

```text
NEXT_ACTION = none within governance.  Close the P4Y successor question.
```

Brief §28 fixes the state machine and Pilot-4 lands on its terminal branch:
measurement FAIL → `DO_NOT_FREEZE_P4Y`. There is no `SIZING REPLAY` and no
Pilot-5. Concretely:

* **Do not freeze a P4Y Checkpoint A.** The precision instrument a checkpoint
  would bind is not measurable to the frozen accuracy at any affordable
  reference, on two of three heavy strata at any block size, and on the third
  at the two larger block sizes.
* **Do not open a Pilot-5.** Nothing in the frozen envelope was left
  unexplored: three block sizes spanning 16×, reference counts spanning 16×,
  every point affordable, all executed, zero amendments, no STOP.
* **The P4 scientific line stands at `PARTIAL`**, exactly where its own
  adjudication left it, and `P4X_SCIENTIFIC_FAILURES = NONE` stands with it.
  Four pilots contradicted no scientific result.
* **What would reopen the question is scientific, not governance.** Making the
  `t1p5` precision scale measurable requires changing the estimand or the
  estimator — a variance-reduced Route-B construction for the heavy family, a
  different precision functional, or a different stopping criterion. Every one
  of those alters the scientific meaning the whole pilot line was built to
  preserve, and each is a research question about the P4 estimator rather than
  a pre-freeze governance pilot. It is out of scope for all four pilots and is
  **not** proposed here.

The governance machinery built across Pilots 1–3 is sound, tested and
available should such a research result ever arrive. It was never the blocker.

---

## Repository safety

```text
branch                        p4y-pilot4-measurement, off p4y-pilot3-heavy-stage1, NOT merged
writes outside this directory none
P4X namespace on this branch  absent
Pilot-1/2/3 namespaces        present, imported read-only, unmodified
main                          untouched
binding checkpoint            none created
production run                none executed
tests                         79 passed
pilot CPU                     3.5466 of the 5.0 CPU-hour cap; no STOP fired
post-result amendments        0
```
