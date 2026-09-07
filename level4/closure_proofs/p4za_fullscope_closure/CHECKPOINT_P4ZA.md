# P4ZA pre-run checkpoint — frozen before any result-bearing byte

```text
CHECKPOINT              P4ZA_CHECKPOINT_1
STATUS                  FROZEN.  Binding on the P4ZA run.  Binding on nothing historical.
P4ZA_NUMERICAL_HOST     LOCAL_MAC
AWS_CPU_USED_BY_P4ZA    0
```

## 1. Parent evidence, bound by hash

```text
P4Z branch   p4z-location-family-feasibility
P4Z head     298d916c75e7eaa3ef28d6957116ed76569dd708
P4Z verdict  P4Z_NUMERICAL_PASS_AWAITING_FORMAL_OR_GOVERNANCE
P4 theorem tree  eede90383da44c250871b1bb97d12045c897c8d9   (unchanged)
```

Content hashes of every parent artifact P4ZA reads are recorded in
`results/p4za_starting_audit.json` and `production/p4za_campaign_plan.json`.
P4ZA writes into none of them.

## 2. What is being recomputed, and what is not

```text
recomputed      13 configurations, 52 cells   (32 K3 + 20 K7)
NOT recomputed  44 cells already PASS on full P4Z evidence
```

P4ZA does not rerun a successful campaign.  It also does **not** use historical
evidence as any cell's authoritative disposition — see
`EVIDENCE_COMPOSITION_RULING.md`.  P4X and the existing P4Z data are recorded
as corroboration only.

## 3. Estimators — unchanged, inherited by content hash

```text
PRIMARY    RB-SCORE   p4z .../rbscore.py    981f4f09ed17c7afac59e81680128e882a9ee392e93254504d0227660351d975
COMPANION  RB-MAP     p4z .../rbmap.py      8166946145d82d5049665d78a80ff43d705d4e40f6b0d326af9d8de1e1648ec3
CONTRACT              p4z .../analytic.py   71e576e2ad218801dbee80ebfbf0108e10b0128549e6500404ac813ac1ffc111
```

Same estimand `Gamma_{D,m,f}`, same code, no modification.

## 4. The new FD ladder, frozen after calibration and before execution

```text
rungs                    0.1, 0.05, 0.025
frozen scientific pair   (0.05, 0.025)     UNCHANGED
dropped                  h = 0.2
ladder blocks            40
```

`h = 0.2` is dropped because the Phase-5 calibration measured an implied order
of `0.88 – 1.39` between `h = 0.2` and `h = 0.1`, against the `O(h^2)`
prediction of `2`.  No rung below `0.025` is added because the measured order
collapses to `-1.67 … 0.82` there: the CRN difference is swamped by Monte Carlo
noise, so a finer rung would add noise to `T_B` rather than information.

```text
T_B = | R(0.1, 0.05) - R(0.05, 0.025) |     rounded outward
```

This is the standard Richardson error estimate — the difference between
successive extrapolations on **adjacent** pairs.  The idealised `h^4` relation
would divide it by 15; P4ZA does not, which is a declared conservative factor
of 15.

**The P4Z defect this corrects.**  P4Z differenced *non-adjacent* pairs,
`(0.2, 0.1)` against `(0.05, 0.025)` — a factor of 4 apart in `h` — and omitted
the divisor.  That quantity measures how bad `h = 0.2` is, not how wrong
`R(0.05, 0.025)` is, and `K7`'s limit was applied to it as though it were the
latter.  See `K7_DIAGNOSIS.md`.

## 5. The K3 envelope, redesigned

The P4Z light envelope was fitted on **one** cell whose RB-MAP leg had four
batches, then applied across two layers and two detectors; on that very cell it
read 1.110 against a measured 2.293.

P4ZA replaces it with a **per-configuration** calibration taken from P4Z's
Stage-0 measured per-path relative standard deviation.  That is a *precision
statistic*, which is exactly the class of information the frozen K3 trigger
discipline permits a sizing rule to read.  No discrepancy, no `z`, no gate
outcome enters the sizing.

```text
N = 4.0 * ( measured_relative_sd / r* )^2       r* = 0.010823063
blocks = 200, fixed;  block_paths = ceil(N / 200)
expected achieved relative SE = r* / 2 = 0.005412
```

**Why the target is `r*` and not P4Z's 0.0025.**  `r*` *is* the frozen
precondition; 0.0025 was a self-imposed extra.  For these 13 configurations a
0.0025 target costs **67.9 CPU-hours**; targeting `r*` with a x4 variance
safety factor costs **3.62** and still lands at half the frozen limit.

**A fairness note, recorded because it cuts against P4ZA.**  A coarser
precision target makes the `z` gate *easier*, since `z` divides by the combined
standard error.  That is a real effect and the choice here is cost-driven.  For
the 20 K7 cells it is also demonstrably not what carries them: on P4Z's own
data at roughly 3x tighter precision the correspondence already passes 20/20
with worst `z` on Monte Carlo error of 0.846.

## 6. Skewnormal4

```text
SKEWNORMAL4_ROUTE = RB_SCORE_EXTENDABLE_BY_INTEGRABILITY_PROOF
```

Its score grows exactly linearly (`psi/z -> sd` right, `-> sd(1+alpha^2)` left,
matching the Mills ratio), which is hypothesis **L4** of the frozen
`THEOREM.md` §8 — whose Coverage line already names the skew-normal.  The
bounded-survival lemma then means only the score's values on `|z| < c_D` enter,
giving an effective bound of 29.38 (`cusum@5`) and 37.88 (`sr@520.886`).
RB-SCORE's moment argument applies with `M_eff` in place of `M`.  No new
estimator, no invented scope exclusion.  See `K3_AND_SKEWNORMAL_AUDIT.md`.

## 7. Seeds, budget, stopping

```text
seeds        rb_score 4190001, rb_map 4190002, fd_ladder 4190003, stride 100
             checked disjoint from every P4Z seed and every historical P4 seed
blocks       200 per route, 40 for the ladder; FIXED
stopping     NON-ADAPTIVE.  No top-up, no second stage, no precision trigger.
budget       TOTAL_CPU_CAP 6.0 h, PER_CONFIGURATION_CPU_CAP 2.0 h
             projected 3.62 h.  P4ZA does NOT borrow P4Z's unused cap.
workers      1, BLAS threads 1
runtime      P4Z Mac contract REUSED -- verified to still match this host
             exactly.  runtime_hash fb9ec8f26ce46c4a7e566dc58683d2a3d3da866cae475aeca9ba35ff729f7410
```

## 8. Gate — every threshold inherited unchanged

```text
relative <= 0.03        z <= 4.0        r* = 0.010823063
K5 top-1 <= 0.10, top-5 <= 0.30, evaluated only at the full 200 blocks
K7 relative drift <= 0.02   (the SAME limit as P4Z, applied to the corrected quantity)

SE_A = batch SE over 200 RB-SCORE block means
SE_B = hypot(batch SE over 200 RB-MAP block means, T_B)
PASS  rel <= 0.03 AND z <= 4.0 AND all preconditions met
FAIL  rel > 0.03 OR z > 4.0 with preconditions met
INCONCLUSIVE  any precondition unmet
"almost pass" does not exist
```

**Declared risk.**  On the Phase-5 calibration the corrected `T_B` reaches
`0.01940` relative on `frozen/sr@520.886/gaussian`, against the unchanged
`0.02` limit — a margin of 3 %.  Production uses different seeds and a
different block count, so some cells may exceed it and become `INCONCLUSIVE`.
That limit is **not** being widened to prevent it.

## 9. Stage-A

Exercises only the new mechanisms, on the cheapest representative of each:
`reduced/sr@20/gaussian` (K7-style ladder on a light tail),
`reduced/sr@20/logistic` (bounded-score K3), `reduced/sr@20/skewnormal4`
(the unbounded-score route).  20 blocks per route.

```text
P4ZA_STAGE_A_KILLED       a TCB or producer gate fired
P4ZA_STAGE_A_INCONCLUSIVE a Stage-A configuration hit its cost cap
P4ZA_STAGE_A_PASS         otherwise; the full run proceeds automatically
```

## 10. No-result-change governance statement

P4ZA produces new evidence only.  Historical P4 remains `PARTIAL`.  P4X, P4Y
and P4Z artifacts are unmodified.  No `INCONCLUSIVE` is reinterpreted as
`PASS`; the 52 cells receive a disposition only from new P4ZA measurement under
the unchanged frozen gate.  No scientific threshold is altered.
