# P4X-R0 pilot report

```text
CLASSIFICATION      = PRE_FREEZE_COST_AND_PRECISION_PILOT
BINDING             = NO
P4_ORIGINAL_VERDICT = PARTIAL   (immutable)
CPU BUDGET          = 4.000 h
CPU SPENT           = 0.545 h   (0.572 h including one superseded policy re-run)
WALL SPENT          = 0.549 h
PEAK RSS            = 452 MB
```

## 1. Isolation

Worktree `/Users/suzhe/ReBaseGuard-p4x`, branch `p4x-feasibility-audit`,
starting HEAD `997cef599a5d6562d32650399eaffd83869d8c7f`, tree clean at entry.
Every protected tree byte-identical to `c123b9b` by git object.  Zero writes
outside `level4/closure_proofs/p4x_generalization_boundary/`.

## 2. The four cost-driving configurations

Named by the feasibility audit's `DRAFT_SUCCESSOR_SCOPE.md` §8, and reconstructed
here from the frozen Priority-4 `results/correspondence.json`, not guessed.
All four are **Route B** configurations; Route A is not the binding constraint
anywhere.

| # | layer | detector | family | route | historical paths | historical estimate (m=1) | SE | rel SE | m=1 status | why it drives cost |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | frozen | `sr@520.886` | `t1p5` | B | 960 000 | 3.0694 | 0.7160 | **23.33 %** | FAIL | the worst relative SE in the campaign; the single largest correspondence discrepancy (25.64 %) |
| 2 | frozen | `cusum@5` | `t1p5` | B | 960 000 | 3.5959 | 0.2914 | 8.10 % | FAIL | second-worst precision at the frozen layer |
| 3 | reduced | `sr@20` | `t1p5` | B | 3 200 000 | 2.8311 | 0.1053 | 3.72 % | FAIL | four failing cells, and the cheapest place to characterise the `t1p5` estimator |
| 4 | frozen | `sr@520.886` | `skewnormal4` | B | 960 000 | 8.1256 | 0.0366 | 0.45 % | PASS (m=2 FAILS) | the only statistically inconsistent cell in the campaign (`m=2`, \|z\| = 4.29) |

**`frozen / SR@520.886 / t1p5` is confirmed among them, and is the campaign's
cost driver.**

### 2.1 The four do not share one pathology

This is the pilot's first finding and it reorganises everything after it.

* Configurations 1-3 (`t1p5`) are **variance-limited**: relative SE 3.7 %-23.3 %,
  all statistically consistent (\|z\| ≤ 1.49).
* Configuration 4 (`skewnormal4`) is **bias-limited**: relative SE 0.41 %-0.45 %
  — twenty to fifty times more precise — while Route B sits systematically
  **above** Route A at every window (2.02 %-2.57 %, one-signed).

Variance reduction is the right tool for the first three and the wrong tool for
the fourth.  Measurements below confirm this: every variance-reducing step on
configuration 4 makes its bias worse.

## 3. Candidate methods and why each was chosen

Only methods preserving unbiasedness, or whose bias is independently
quantifiable, were admitted.  No new estimator framework was invented; no
importance sampling was used.

| method | idea | why admissible a priori |
|---|---|---|
| `baseline_h0.05` | the frozen Route-B estimator, fresh seed namespace | the reference for every ratio |
| `reflection_h0.05` | reflection-antithetic: for a symmetric family under a reflection-equivariant detector the `-h` run is the exact mirror of the `+h` run, so it need not be simulated | exactness verified numerically, not assumed |
| `coarse_h0.10`, `coarse_h0.20` | the identical estimator at a larger finite-difference step; central-difference variance scales as `1/h^2` | the `O(h^2)` term is removed by the same Richardson combination; the residual is measured by the step ladder |
| `fine_h0.025` | the identical estimator at a smaller step | bias/variance control in the other direction |
| `g2_control` | control variate from Corollary G2: the window mean at a *deterministic* horizon has expectation exactly 1 | the only analytically known quantity available on these paths |

**Common random numbers are not a candidate**: the frozen Route B already uses
exact CRN coupling between the `+h` and `-h` runs.  It is the baseline, not an
improvement.

## 4. Pilot design

* 48 blocks x 20 000 paths for the two frozen `t1p5` configurations, 32 x 100 000
  for the reduced one, 24 x 20 000 for `skewnormal4`;
* fresh seed namespace `411xxxx` (the frozen campaign used `401xxxx`), so no
  pilot block can coincide with a frozen block;
* RNG addressing unchanged from the frozen simulator: counter-based Philox keyed
  on `(seed, batch, step)` with a `2^64` stride per stream;
* block means are the unit of inference, matching the frozen convention, so
  within-block Monte Carlo noise and between-block variation are never mixed;
* variance-reduction factors carry F-distribution 95 % confidence intervals;
* scaling ladders over four block sizes per configuration;
* the tail sweep and the cost calibration use **separate** seeds from the method
  comparison, so no method is scored on the block that tuned it.

## 5. Measured results

### 5.1 Per-method, m = 1, against the baseline

VRF > 1 means variance reduced.  "shift" is the point-estimate move in units of
the baseline standard error — the bias indicator.

| configuration | method | estimate ± SE | rel SE | VRF (95 % CI) | CPU mult | VRF/CPU | shift |
|---|---|---|---|---|---|---|---|
| frozen/sr/t1p5 | baseline `h=.05` | 3.9040 ± 0.2104 | 5.39 % | — | 1.00 | — | — |
| | `reflection` | 14.1448 ± 7.4211 | 52.46 % | **0.001** (0.000-0.001) | 0.91 | 0.001 | +48.7 |
| | `coarse h=.10` | 3.8938 ± 0.2289 | 5.88 % | 0.845 (0.474-1.507) | 1.12 | 0.756 | −0.05 |
| | `coarse h=.20` | 3.8523 ± 0.1558 | 4.04 % | 1.825 (1.023-3.255) | 1.12 | 1.626 | −0.25 |
| | `fine h=.025` | 4.1796 ± 0.3518 | 8.42 % | 0.358 (0.201-0.638) | 1.12 | 0.319 | +1.31 |
| frozen/cusum/t1p5 | baseline | 3.7732 ± 0.1984 | 5.26 % | — | 1.00 | — | — |
| | `reflection` | 4.0974 ± 3.7914 | 92.53 % | **0.003** (0.002-0.005) | 0.89 | 0.003 | +1.63 |
| | `coarse h=.10` | 3.6573 ± 0.1731 | 4.73 % | 1.314 (0.736-2.343) | 1.01 | 1.302 | −0.58 |
| | `coarse h=.20` | 3.6099 ± 0.1284 | 3.56 % | 2.388 (1.339-4.260) | 1.01 | 2.363 | −0.82 |
| | `fine h=.025` | 3.7675 ± 0.3533 | 9.38 % | 0.315 (0.177-0.562) | 0.99 | 0.317 | −0.03 |
| reduced/sr/t1p5 | baseline | 2.8320 ± 0.1142 | 4.03 % | — | 1.00 | — | — |
| | `reflection` | 8.0749 ± 2.2830 | 28.27 % | **0.003** (0.001-0.005) | 0.85 | 0.003 | +45.9 |
| | `coarse h=.10` | 2.8327 ± 0.0639 | 2.26 % | 3.198 (1.561-6.550) | 1.01 | 3.166 | +0.01 |
| | `coarse h=.20` | 2.8940 ± 0.0762 | 2.63 % | 2.250 (1.098-4.609) | 1.01 | 2.225 | +0.54 |
| | `fine h=.025` | 2.7220 ± 0.1542 | 5.67 % | 0.548 (0.268-1.124) | 1.00 | 0.547 | −0.96 |
| frozen/sr/skewnormal4 | baseline | 8.0736 ± 0.0420 | 0.52 % | — | 1.00 | — | — |
| | `reflection` | — | — | SKIPPED (asymmetric family) | — | — | — |
| | `coarse h=.10` | 8.2812 ± 0.0274 | 0.33 % | 2.347 (1.015-5.426) | 0.92 | 2.539 | **+4.94** |
| | `coarse h=.20` | 9.4614 ± 0.0206 | 0.22 % | 4.162 (1.800-9.621) | 0.68 | 6.133 | **+33.01** |
| | `fine h=.025` | 8.1485 ± 0.0698 | 0.86 % | 0.363 (0.157-0.839) | 1.01 | 0.358 | +1.78 |

### 5.2 The structural fact behind all of it

Under CRN, on any path where the `+h` and `-h` runs stop at the same time with
the same window, `Z^+ - Z^- = -2h` identically, so the per-path contribution is
**exactly 1**.  Measured fraction of exactly-one paths:

| configuration | exactly-one fraction | largest \|contribution − 1\| |
|---|---|---|
| frozen/sr/t1p5 | 85.5 % | 7 062 |
| frozen/cusum/t1p5 | 87.5 % | 23 438 |
| reduced/sr/t1p5 | 87.4 % | 50 996 |
| frozen/sr/skewnormal4 | 28.9 % | 89 |

All of Route B's variance lives on the decoupling set.  This is the numerical
shadow of Corollary G2: `Gamma − 1` is exactly the stopping-selection effect.
It also explains `skewnormal4`: at ARL ≈ 396 a shift of `h = 0.05` decouples
71 % of paths, which is why its estimator is well-behaved but step-sensitive.

### 5.3 Tail index — the decisive measurement

Hill estimator on the per-path summand, both routes, all 24 configurations.
`alpha >= 2` means finite variance and the classical `n^{-1/2}` rate;
`alpha < 2` means neither.

| family | Route B `alpha` (range over 4 layer/detector combos) | Route A `alpha` | finite variance? |
|---|---|---|---|
| gaussian | 13.3 – 16.2 | 5.00 – 5.60 | yes |
| laplace | 9.3 – 12.1 | 4.30 – 4.90 | yes |
| logistic | 10.9 – 11.3 | 4.19 – 5.00 | yes |
| skewnormal4 | 10.9 – 14.0 | 4.37 – 5.09 | yes |
| t3 | 2.96 – 3.50 | 2.70 – 2.96 | yes |
| **t1p5** | **1.47 – 1.53** | **1.50 – 1.52** | **NO** |

`t1p5` is the **only** family whose estimator summand has infinite variance, on
**both** routes, at **every** layer and detector.  The measured index matches
the model exactly: Student-`t` with `nu = 1.5` has tail index 1.5, and the frozen
Priority-4 protocol already labels this family *"finite mean, INFINITE
variance"*.  The precision limit is therefore a property of the model, not of
the implementation — and it was already known before any P4X data existed.

### 5.4 Scaling ladders

Block standard deviation against block size, log-log slope (classical would be
−0.5):

| configuration | n rungs | block SD | fitted slope | last-rung local slope |
|---|---|---|---|---|
| frozen/sr/t1p5 | 5k, 20k, 80k, 320k | 32.25, 8.11, 2.10, 1.00 | −0.849 | **−0.54** |
| frozen/cusum/t1p5 | 5k, 20k, 80k, 320k | 3.20, 4.14, 1.33, 0.62 | −0.438 | −0.55 |
| reduced/sr/t1p5 | 25k, 100k, 400k, 1.6M | 2.24, 0.88, 0.31, 0.19 | −0.604 | −0.34 |
| frozen/sr/skewnormal4 | 5k, 10k, 20k, 40k | 0.516, 0.399, 0.169, 0.172 | −0.599 | +0.01 |

Two readings, and both matter.

1. **Block size, not path count, is what broke the historical `t1p5` cells.**
   At `n = 20 000` the block mean for frozen/sr/`t1p5` is 2.106 with a block SD
   of 8.11; at `n = 320 000` it is 4.095 with a block SD of 1.00.  The frozen
   campaign used 20 000 paths per block for that cell — inside the regime where
   both the estimate and its error bar are unreliable.
2. **The standard error is itself an unreliable statistic here.**  At an
   *identical* design (48 blocks x 20 000 paths) the frozen campaign measured a
   23.33 % relative SE and this pilot measured 5.39 % — a factor of 4.3 apart.
   That spread is expected when `alpha < 2` and is the reason the cost
   projection carries a worst-case tier rather than a single number.

At the largest ladder rung the frozen/sr/`t1p5` Route-B pilot estimate is
`4.0946 ± 0.1770`, against the frozen Route-A value `4.1276 ± 0.0956`:
combined \|z\| = **0.16**.  That is what a precision limitation predicts and a
theorem contradiction does not.  It is a pilot observation about estimator
behaviour, **not** a prediction that any production cell will pass — P4X's
production run must be able to return either outcome.

## 6. Method verdicts

| method | verdict | evidence |
|---|---|---|
| `reflection` | **REJECTED — exact but variance-catastrophic** | Pathwise mirror exact to `0.000e+00`; negated stream distributionally valid for `t1p5` (KS p = 0.49) and `gaussian` (p = 0.35), correctly invalid for `skewnormal4` (p = 0, skew +0.78).  But VRF 0.001-0.003, a **300-1000x variance increase**: substituting the mirror for the `-h` run destroys the CRN cancellation that makes 85-90 % of paths contribute exactly 1.  The CRN pairing is worth far more than the 2x compute saving. |
| `g2_control` | **REJECTED — degenerate** | Measured per-path variance `6e-29` to `9e-31`, i.e. exactly zero.  Under CRN at a deterministic horizon the control equals exactly 1 on **every** path — which is precisely Corollary G2's content.  It carries no information about the stopped estimator.  This is the only analytically known quantity available on these paths, so **no usable control variate exists for Route B.** |
| `coarse_h` | **REJECTED for `skewnormal4`; NOT ADOPTED for `t1p5`** | For `skewnormal4` the point estimate moves **+4.94** and **+33.01** baseline SEs — inadmissible bias.  For `t1p5` the VRF is a real 1.3-3.2 and shifts are ≤ 0.82 baseline SE, but the pilot's own SEs are too large to resolve an `O(h^4)` bias, and the step ladder is not sign-consistent across configurations (−0.05, −0.25 / −0.58, −0.82 / +0.01, +0.54).  Adopting it on inconclusive bias evidence would trade a measured problem for an unmeasured one. |
| `fine_h0.025` | **NOT ADOPTED as default** | Variance increases (VRF 0.32-0.55) everywhere.  Retained as the diagnostic ladder rung it already is. |

**No candidate variance-reduction method is adopted.**  The frozen Route-B
estimator at `h = 0.05 / 0.025` is retained unchanged.  Precision is bought
with paths and block size only.

That is a real result rather than a null one: the pilot's job was to find out
whether cheap variance reduction exists, and the answer — with the reason — is
that the frozen estimator is already the right one, because its CRN structure
has already extracted the exact-cancellation gain that any antithetic or
control-variate scheme would be competing for.

## 7. Route Q's admissible role

The feasibility audit's draft gate `X6` proposed declaring a cell `ARBITRATED`
when Route Q reproduces the identity for that family and window.  **The pilot
finds that clause inadmissible and it must be removed.**

Route Q evaluates the memoryless detector `tau = inf{t : |Z_t| >= c}` at
`c = 2.0`.  The frozen Priority-4 `EVIDENCE_BOUNDARY.md` §3 states it plainly:

> Route Q's detector is **not** the frozen ReBaseGuard detector.  Nothing in
> Route Q is evidence about `h = 5` or `A = 520.886133602749`.

Route Q therefore cannot arbitrate a disagreement at a frozen operating point:
it is evidence about the **identity**, on its own detector, not about the
frozen cell.  Nor can it serve as a control variate — its paths belong to a
different detector, so there is no coupling to exploit.

```text
ROUTE_Q_ADMISSIBLE_ROLE = C  (independent cross-check of the identity only)
  NOT A: it is not a zero-sampling-error arbiter for frozen-detector cells
  NOT B: it is not a control variate for Route B
```

Removing the arbitration clause makes CUT-1 strictly harder, and the cost
projection below is computed without it.

## 8. CUT-2 and CUT-3

Both were determined from artifacts that already exist.  **No new simulation.**

**CUT-3 = NEGLIGIBLE.**  The closed Gaussian gains already publish their own
standard errors (`gamma_tilde_se`, frozen Priority-3 stability map) and
Priority 4 already publishes `route_a` standard errors, so the correctly
specified two-sample statistic is arithmetic on numbers that exist.  Recomputed
here: worst historical-gate statistic **12.91**, worst two-sample statistic
**2.98**, against the same limit of 4 — all eight Gaussian frozen cells pass.
Marginal production cost is zero, because `gaussian` is already one of the six
theorem-supported families in the grid.

**CUT-2 = NONE.**  The A3 half is already satisfied and over-determined: 16/16
uniform cells confirmed at \|z\| 514-680 against a gate demanding 10, plus a
Route-Q exact defect and an exact rational Arb certificate.  The first-moment
half is a **non-existence** claim (`PROOF.md` §10 proves `E|A_1| = infinity`),
which a two-route discrepancy statistic structurally cannot express: measured
\|z\| across all 16 Cauchy cells is 0.026-1.616 against a gate demanding ≥ 10.
Encoding CUT-2 on the existing exact and analytic evidence is legitimate and
costs nothing.  An optional confirmatory divergence diagnostic — a truncated
moment `E[|A_1| 1{|A_1| <= K}]` growing without bound in `K`, and a standard
error failing to shrink at `n^{-1/2}` — is priced at **0.008 CPU-hours** and is
explicitly not load-bearing.

## 9. Budget

| stage | CPU (s) | wall (s) |
|---|---|---|
| sizing | 0.5 | 0.5 |
| five-method comparison + ladders | 1 784.0 | 1 799.4 |
| tail sweep (24 configurations, both routes) | 74.5 | 74.5 |
| cost calibration + precision policy | 96.4 | 96.4 |
| bias checks | 5.0 | 5.0 |
| CUT-2 / CUT-3 (no simulation) | < 1 | < 1 |
| **recorded total** | **1 960.3 (0.545 h)** | **1 975.7 (0.549 h)** |
| including one superseded policy re-run | 2 060 (0.572 h) | — |

Cap 4.000 CPU-hours.  **Spent 14 %.**  Peak RSS 452 MB.
