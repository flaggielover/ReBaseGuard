# P4Z Phases 9–10 — feasibility model and micro-pilots

```text
RESULT_BEARING = NO
These runs are falsification probes.  No verdict, historical or future, may
cite a number in this document as scientific evidence.
```

## 1. Resource discipline

The CUSUM Aux4 full-cover campaign owns the 4 physical cores of the
authoritative AWS worktree.  Every P4Z pilot ran **on the local host**, in a
scratch virtual environment, strictly single threaded
(`OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`, enforced by the
driver, which refuses to start otherwise).

```text
micropilot          ~100 CPU-s   (run twice; scientific fields bit identical)
fd ladder            ~33 CPU-s
exploratory probes   ~50 CPU-s
TOTAL               ~280 CPU-s   on a host the CUSUM campaign does not use
AWS CPU consumed by P4Z             0
```

## 2. Cells

The brief's tiny representative set, mapped onto the actual unresolved residue:

| label | cell | why |
|---|---|---|
| easy | `gaussian/cusum@2` | the light-tailed control; a method that helps here is doing something other than what was diagnosed |
| difficult | `t1p5/cusum@5` | unresolved cells 4 and 5 |
| difficult | `t1p5/sr@520.886` | unresolved cells 6, 7, 8 — the worst historical concentration |
| near-threshold | `t1p5/sr@20` | unresolved cells 1 and 2, the only ones where *Route B* missed `r*` |
| near-threshold | `t3/cusum@5` | unresolved cell 3, the only non-`t1p5` cell |

8 batches x 40 000 paths = 320 000 paths per cell for RB-SCORE; 4 x 40 000 =
160 000 for RB-MAP; 40 000 for the historical comparison.  Full `m` grid.

## 3. What the pilots falsify

The pilots were run to kill the candidates.  They did not.

### 3.1 The diagnosis is confirmed, directly

The historical Route-A per-path summand on the three `t1p5` cells has a
measured Hill index of `1.5–1.6` — the theoretical `alpha` of Student-`t` with
`nu = 1.5` — and a top-1 share of squared deviation of `0.297`, `0.436` and
`0.975`.  On `t1p5/sr@520.886` a single path in 200 000 carries **97.5 %** of
the sample variance.  Finding F-01 is not an inference; it is visible.

### 3.2 Point estimates agree with the historical record

Two-sample statistic `z = |e_new - e_hist| / sqrt(SE_new^2 + SE_hist^2)`, the
statistic P4X established as correct for comparing two Monte Carlo estimates:

| cell | m | RB-SCORE vs P4X Route A | RB-MAP vs P4X Route B |
|---|---|---|---|
| `gaussian/cusum@2` | 1 | 0.19 | 2.05 |
| `t1p5/cusum@5` | 1, 2 | 0.06, 0.08 | 0.27, 1.24 |
| `t1p5/sr@520.886` | 1, 2, 5 | 1.02, 1.16, 1.40 | 1.87, 2.61, 2.26 |
| `t1p5/sr@20` | 1, 2 | 0.55, 0.51 | 1.32, 1.56 |
| `t3/cusum@5` | 1 | 0.83 | 0.11 |

Every value is under 4.  The redesigned estimators reproduce the historical
numbers; they do not move them.

### 3.3 The moment class changes, which is the point

| cell | route-A per-path rel. sd | RB-SCORE rel. sd | VRF | Hill | top-1 |
|---|---|---|---|---|---|
| `gaussian/cusum@2` | 1.00 | 0.973 | 1.1 | 6.4 → 3.8 | 0.003 → 0.005 |
| `t3/cusum@5` | 19.93 | 2.298 | 75 | 3.1 → 3.3 | 0.010 → 0.012 |
| `t1p5/sr@20` | 12.06 | 0.940 | 165 | 1.6 → 4.0 | 0.436 → 0.005 |
| `t1p5/cusum@5` | 29.69 | 1.216 | 596 | 1.6 → 3.5 | 0.297 → 0.012 |
| `t1p5/sr@520.886` | 128.27 | 1.242 | **10 668** | 1.5 → 4.1 | 0.975 → 0.006 |

Every RB-SCORE top-1 share is below `0.012`, against P4Y Pilot-4's
admissibility threshold of `0.10` and its finite-variance control's `0.006`.
The heavy strata now sit where a well-aggregated law sits.

### 3.4 Achieved precision, against the frozen `r*`

`r* = 0.010823063`, unchanged.  RB-SCORE at 320 000 paths:

| cell | relSE range over m |
|---|---|
| `gaussian/cusum@2` | 0.00146 – 0.00165 |
| `t1p5/cusum@5` | 0.00153 – 0.00208 |
| `t1p5/sr@520.886` | 0.00136 – 0.00176 |
| `t1p5/sr@20` | 0.00082 – 0.00122 |
| `t3/cusum@5` | 0.00319 – 0.00425 |

For comparison, `frozen/cusum@5/t1p5` Route A reached `0.01658` — and missed
`r*` — after **93 500 000** paths and 198 CPU-seconds.  RB-SCORE reaches
`0.00153` after 320 000 paths and 1.8 CPU-seconds.

### 3.5 Predicted vs measured variance

The model's only prediction is that the block-mean relSE follows
`per-path rel. sd / sqrt(N)`, which is a claim that the summand has finite
variance.  Checked on `t1p5/sr@520.886`, `m=1`: per-path rel. sd `1.242`, so
the predicted relSE at 320 000 paths is `1.242/sqrt(320000) = 0.00220`; the
measured value is `0.00157`.  The same check on `t3/cusum@5`, `m=1`: predicted
`2.298/sqrt(320000) = 0.00406`, measured `0.00319`.  Measured is *tighter* than
predicted in both cases, which is why the cost model carries a x4 safety factor
on variance rather than a x1.

### 3.6 Bias diagnostic

RB-SCORE is exactly unbiased by construction, so the bias diagnostic is applied
to RB-MAP, where a finite-difference truncation term exists.  The FD ladder
(`diagnostics/fd_ladder.json`) on `t1p5/sr@520.886`, `m=1`, against RB-SCORE:

| `h` | central difference | offset |
|---|---|---|
| 0.2 | 3.96019 | −0.09184 |
| 0.1 | 4.03096 | −0.02108 |
| 0.05 | 4.05448 | +0.00245 |
| 0.025 | 4.05340 | +0.00136 |
| 0.0125 | 4.09315 | +0.04111 |

The offset ratio from `h=0.2` to `h=0.1` is **4.36**, against the `O(h^2)`
prediction of 4.  The frozen pair `(0.05, 0.025)` sits where truncation is
already below Monte Carlo noise, and the Richardson combination there recovers
RB-SCORE to `+0.0010`.  Meanwhile the standard error roughly **doubles** from
`h=0.05` to `h=0.0125` — the CRN blow-up P4X's R0 pilot measured independently.

**The frozen finite-difference convention is validated and kept unchanged.**

### 3.7 The one thing the pilots did surface

Applying the frozen gate to the pilot's own RB-SCORE vs RB-MAP pair, all 20
`(cell, m)` combinations satisfy `rel <= 0.03` — the worst is `0.0170` — but
**two** exceed `|z| <= 4`: `t1p5/sr@520.886` at `m=1` (`z = 4.12`) and `m=2`
(`z = 4.77`).

This is not an estimator defect, and the FD ladder shows why.  RB-MAP was run
with only **4 batches**, so its standard error is the spread of four block
means, and the four `m` of a configuration share paths and are therefore
perfectly correlated — one unlucky set of four blocks shifts all four `m`
together.  The same cell, run with 6 batches in the FD ladder, gives a
Richardson-vs-RB-SCORE offset of `+0.0010` (0.02 %) rather than the pilot's
1.2–1.7 %.

It is, however, a real warning about the *governance*, and it is the reason
`CAMPAIGN_GOVERNANCE.md` fixes **200 blocks per route** rather than sizing
blocks adaptively, and the reason Route B's uncertainty must carry its
truncation residual.  At the precision RB makes affordable, `|z| <= 4` — not
the 3 % relative gate — becomes the binding constraint, and a standard error
computed from too few blocks fails it for reasons that have nothing to do with
the science.  P4X's 8 unadjudicable cells came from too few blocks of a
badly concentrated law; the same mistake at 400x better precision would be
invisible in `rel` and glaring in `z`.

## 4. Cost model

`results/estimator_feasibility.json`, built from the pilot by pure arithmetic.

```text
target relative SE per route     0.0025          (r* / 4.33)
safety factor on variance        x4
safety factor on CPU             x3
blocks per route                 200             (fixed, non-adaptive)

route A                          0.9389 CPU-h
route B                          5.2183 CPU-h
TOTAL                            6.1573 CPU-h
cap                             12.0    CPU-h
worst configuration              1.339  CPU-h  against a 2.0 cap
P4X actual                      24.7493 CPU-h, leaving 8 cells unadjudicated
```

The `t3` configurations carry 87 % of the projected cost — not because the
estimator is expensive there but because `t3` is standardised to unit variance
and so has a long ARL at `h=5`, and because the CRN "aligned" mode of the
frozen simulator draws a full `n_paths` vector at every step regardless of how
many paths are still alive.  That is an inherited cost property of Route B's
coupling requirement, not something P4Z introduces, and the frozen convention
is kept.

**Falsifiable.**  The model predicts a per-path relative sd per regime.  Stage 0
of the campaign measures it on 20 blocks and kills any configuration exceeding
the prediction by more than the x4 safety factor (kill gate `K3`).
