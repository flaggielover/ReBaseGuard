# P4Y PILOT-4 — heavy-tail precision measurement feasibility gate — preregistration

```text
STATUS  = PRE-RESULT, FROZEN
BINDING = NO
NOT P4Y PRODUCTION.  NOT A BINDING CHECKPOINT.  NOT AN ALLOCATION-RULE PILOT.
NOT A CAP-SELECTION PILOT.  NOT A 96-CELL CAMPAIGN.

P4_ORIGINAL_VERDICT     = PARTIAL   immutable
P4X_SUCCESSOR_VERDICT   = FAIL      immutable
P4X_SCIENTIFIC_FAILURES = NONE      immutable
P4Y_PILOT1_VERDICT      = NEEDS_ONE_MORE_PRE-FREEZE_PILOT   immutable
P4Y_PILOT2_VERDICT      = NEEDS_ONE_MORE_PRE_FREEZE_PILOT   immutable
P4Y_PILOT3_VERDICT      = NEEDS_ONE_MORE_PRE_FREEZE_PILOT   immutable
```

Frozen **before any result-bearing Pilot-4 byte exists**. `results/` is empty
at this commit.

The only Pilot-4 numbers observed beforehand are a pre-freeze probe of (a) the
block-aggregation identity, (b) cost per path, and (c) memory — recorded in
§4.1. No precision-stability quantity was computed.

---

## 1. The single question

> Does there exist an affordable pair `(logical block size, reference block
> count)` under which the `t1p5` precision scale can be estimated with a
> predeclared multiplicative accuracy and probability guarantee?

If no: **`DO_NOT_FREEZE_P4Y`.** A properly executed negative result is that
verdict, not `INCOMPLETE`, and not an invitation to a Pilot-5 research
campaign.

## 2. Why — the exact Pilot-3 defect

Pilot-3 froze its benchmark uncertainty as `1/sqrt(2(n-1)) = 0.79 %` at
`n = 8000`. That is normal theory. Measured on the blocks it actually drew,
one block in 8 000 carried **29.3 %** of the total squared deviation, the top
five carried 60.2 %, eight disjoint 1 000-block sub-samples gave standard
deviations spanning **0.834–2.672**, and nested prefixes did not converge.
Even at the frozen production block size of 250 000 paths, one block in 400
carried ~32 % and two half-samples differed by ~2.79×.

Pilot-3's "truth" was another draw of the same noisy statistic. Pilot-4
therefore uses **no normal-theory SD-uncertainty formula anywhere**, and its
benchmark is admissible only if it passes empirical stability criteria frozen
below.

## 3. Scope

No Stage-1 sizing, no staged top-up, no cap design, no kappa selection, no
production cost optimisation, no correspondence adjudication. A test asserts
that the tokens `cap_blocks`, `stage1`, `top_up`, `PRECISION_LIMITED` and
`kappa` do not occur in Pilot-4's executable code.

Inherited and untouched: the P4 theorem, A1–A7, detector semantics, the six
families, the `m` grid, the Route-A/B estimators, the finite-difference steps,
Richardson, `r*`, the correspondence gates, the Gaussian consistency
statistic, Route-Q, Lean, Arb.

```text
NEW SCIENCE = NO   NEW THEOREM = NO   NEW LEAN = NO   NEW ARB = NO
```

## 4. The measurement object — brief §9

For a frozen `(configuration, route, window m)` and a logical block size `b`
paths, let `X^(b)` be the per-block value the frozen Priority-4 estimator
returns for one block of `b` independent paths.

```text
ESTIMAND     theta(b) = sd( X^(b) ) / | E X^(b) |
ESTIMATOR    theta_hat = s / |xbar|   over B_ref logical blocks, ddof = 1
IDENTITY     relSE(B) = theta(b) / sqrt(B)     exactly
```

`theta` is the coefficient of variation of the block-mean law. Future
governance compares `relSE(B) = sd/(sqrt(B)|mean|)` against `r*`, and the
identity above makes estimating `relSE` to within a multiplicative factor the
*same problem* as estimating `theta` to within that factor — with `B` divided
out, so the question is about the block law and not about any allocation.

* **Random object**: the per-block value, a plain average of `b` i.i.d.
  per-path contributions.
* **Finite variance**: **not assumed.** `theta` exists only if `X^(b)` has
  finite variance, and Pilot-3's evidence puts exactly that in doubt.
  Pilot-4 treats it as empirical: a block size is usable only if its benchmark
  passes §6. A Hill index above 2 is never accepted as a substitute (brief
  §19); tail diagnostics are reported as secondary and explain stability
  rather than establish it.
* **Shard invariance**: `X^(b)` is a function of logical block ids and their
  Philox streams, never of worker assignment or scheduling order.
* **No robust substitute.** A trimmed or median-based scale would estimate a
  different functional and would change the meaning of the inherited standard
  error. Out of scope.

### 4.1 Pre-freeze probe (disclosed)

**The aggregation identity.** Every frozen per-block statistic is a plain
average of per-path contributions — Route A directly, Route B because the
Richardson combination is linear in the two path averages. So a block value
over `k*n` paths equals the mean of `k` independent block values over `n`
paths, **exactly**. Verified bit-for-bit by splitting a simulated block's own
paths (`|diff| = 0.000e+00` on both routes), and pinned by
`tests/test_aggregation_identity.py`.

Two consequences, both load-bearing: a single 1 000 000-path block was
measured at **318 MB** peak RSS, so 4 000 000 would be ~1.2 GB and the direct
route does not scale; and one base pool can serve **every** block size in the
grid, which is what makes a three-block-size sweep affordable. Analyses at
different block sizes therefore share paths — disclosed, and it makes the
comparison across block sizes a common-random-number comparison.

Measured cost at the base block size of 50 000 paths, s per 1e6 paths:
`t1p5 cusum@2 A` 0.330, `t1p5 sr@20 A` 0.506, `t1p5 cusum@2 B` 4.141,
`gaussian cusum@2 A` 0.714.

## 5. Frozen grids

```text
BASE_BLOCK_PATHS = 50 000        every logical block size is a multiple

BLOCK_SIZES      = (250 000, 1 000 000, 4 000 000)

BREF_GRID          250 000 : (32, 64, 128, 256)
                 1 000 000 : (32, 64, 128)
                 4 000 000 : (16, 32, 64)
```

The `B_ref` grids shrink as `b` grows because a reference costs `B_ref * b`
paths per stratum and eight production heavy strata must fit well inside the
inherited 45 CPU-hour envelope. Projected reference overhead for all eight, at
the measured P4X heavy rate of 12 s/1e6:

| | 250 000 | 1 000 000 | 4 000 000 |
|---|---|---|---|
| smallest `B_ref` | 0.21 h | 0.85 h | 1.71 h |
| largest `B_ref` | 1.71 h | 3.41 h | 6.83 h |

```text
MAX_PRODUCTION_REFERENCE_HOURS = 10.0     one fifth of the 45 h envelope
```

Every grid point is affordable, so **affordability is not the binding
constraint — stability is.** No larger block size may be added after seeing
instability.

## 6. Benchmark construction and admissibility

Two **independent master pools** per `(stratum, block size)`, each of
`8 × max(B_ref at that b)` logical blocks capped at 2048 / 1024 / 512. The
benchmark `theta_bench` is computed on the two pools combined, and is
**admissible only if all four checks pass**:

```text
A  disjoint split     max(theta_pool0, theta_pool1) / min(...)  <= C_SPLIT = 1.25
B  growing prefix     theta(full) / theta(first half)  in [1/1.15, 1.15]
                      over prefixes 1/8, 1/4, 1/2, full
C  extreme top-1      largest block's share of total squared deviation <= 0.10
D  extreme top-5      top five blocks' share <= 0.30
```

Quarter-level splits and the full prefix curve are reported; `C_SPLIT` is the
decisive split criterion. Thresholds are frozen here and are not chosen from
observed variability. `top-1 <= 0.10` is generous by construction: for a
well-aggregated law at these pool sizes it should sit near 1–2 %.

**If no block size yields an admissible benchmark, Pilot-4 fails the gate.**
An unstable large pool is never called truth.

## 7. Accuracy target, replication and confidence

```text
ACCURACY_FACTOR     c = 1.25      success is  1/c <= theta_hat/theta_bench <= c
TARGET_PROBABILITY  p = 0.90
BETA                0.05          one-sided, exact Clopper-Pearson
R_REFERENCE_DRAWS   29            smallest R with p**R <= beta; 29/29 gives 0.9019
SECONDARY_FACTOR    1.50          reported, never decisive
```

`c = 1.25` on `relSE` corresponds to a factor `1.25^2 = 1.56` on a sample size
at the classical rate — strict enough to support production precision
governance, and not absurdly stronger. **`c` is not set from observed
variability.**

The 29 reference draws are fresh, mutually disjoint, and drawn in a namespace
disjoint from both master pools.

## 8. Strata

| id | configuration | route | block sizes | `B_ref` cap | role |
|---|---|---|---|---|---|
| `H` | `reduced/cusum@2/t1p5` | A | all three | 256 | primary heavy — the full sweep |
| `HSR` | `reduced/sr@20/t1p5` | A | 250 000 | 256 | is the phenomenon detector-generic? |
| `HB` | `reduced/cusum@2/t1p5` | B | 250 000 | 64 | is it route-generic? |
| `O` | `reduced/cusum@2/gaussian` | A | 250 000 | 128 | **ordinary finite-variance control** |

Primary window `m = 1`, which Pilot-3 identified as the dominant instability.
The control must show the framework finds a stable regime where one exists; if
the control fails, the framework itself is classified suspect (brief §20).

## 9. Feasibility criterion

A pair `(b, B_ref)` is selectable only if **all** hold:

```text
A  the benchmark at b is admissible on EVERY heavy stratum measured at b
B  growing-prefix stability passes at b
C  extreme concentration passes at b
D  Clopper-Pearson lower bound on P(inside the band) >= 0.90, on every heavy
   stratum measured at b
E  production reference overhead <= 10 CPU-hours
F  the ordinary control passes its own criteria
G  shard / RNG regressions pass
H  no STOP fired
I  no post-result amendment
```

Among selectable pairs, prefer the smallest reference path cost `B_ref * b`;
ties to the smaller `b`. Frozen before results.

## 10. Kill gate — binding

Return **`DO_NOT_FREEZE_P4Y`** if, under the entire frozen grid and CPU
envelope: no block size achieves an admissible benchmark; or no affordable
`B_ref` achieves the frozen multiplicative accuracy at the target probability;
or independent master pools remain materially inconsistent; or extreme blocks
continue to dominate beyond the frozen tolerance.

`PILOT4_INCOMPLETE` is reserved for an external, non-scientific interruption.
**A properly executed negative result is `DO_NOT_FREEZE_P4Y`, not
`INCOMPLETE`.**

## 11. Budget, STOP rules, temporal integrity

```text
PILOT4_CPU_CAP_HOURS = 5.0     frozen before T2, never extended
frozen design's computed cost  = 2.57 CPU-hours
```

STOP on: cumulative CPU reaching 5.0 h; an address collision; a shard-sum
breach; estimator drift. A STOP is reported as a STOP.

```text
T0 preregistration frozen      results/ empty
T1 code and config frozen      same commit
T2 first result-bearing execution
T3 measurement pools complete
T4 diagnostics complete
T5 report complete
```

No load-bearing amendment after T2. If a result-bearing semantic defect is
found after T2, Pilot-4 **STOPs and classifies** — it does not patch and
continue as the same pilot. A pure reporting bug may be repaired only if it
provably cannot alter any result or selection, and must be disclosed.

Addressing is the inherited injective positional code with campaign base
`12 310 000 000`, a clean `1e9` above Pilot-3's theoretical ceiling; keyed by
logical identity only, no modulo compression. The reachable domain is
enumerated and checked collision-free before execution.
