# Long-run reference-state behaviour

Tier: the *existence, uniqueness, ergodicity and moment* statements are EXACT
THEOREMS (T7). Everything measured below — the shape of `pi`, the dispersion
law, mixing rates, mode structure — is NUMERICAL EVIDENCE about a law whose
existence is proved, not assumed.

## 1. Experimental design

`experiments/run_chain.py`: 8 `(detector, m)` cells x 21–22 reuse fractions
(`rho in {0, 0.02, ..., 1}` union `{0.5, 0.8, 1, 1.25, 1.5, 2} x rho_c`),
240 replicate chains per cell x 2000 cycles, first 400 discarded.

* **Statistical unit is the replicate chain.** Every reported interval is a
  replicate standard error. No time step is ever treated as an independent draw.
* **Three initial-condition groups** run inside every cell (`e_0 = 0, +6, -6`,
  80 replicates each), so initial-condition dependence is measured, not assumed
  away.
* `experiments/run_density.py` re-runs four cells at 4000 cycles x 240
  replicates for the mode analysis, with per-replicate histograms.
* `experiments/run_stress.py` is the deliberate runaway hunt.

## 2. The dispersion law

Stationary `RMS(e)` against `rho` is **smooth, non-monotone, and has an interior
minimum far above `rho_c`** — in every one of the eight cells:

| det | m | `rho_c` | `argmin_rho RMS` | min RMS | RMS at `rho_c` | RMS at `rho=1` | `argmax_rho ARL` | max ARL | ARL at `rho=1` |
|---|---|---|---|---|---|---|---|---|---|
| CUSUM | 1 | 0.0670 | **0.300** | 0.8412 | 0.9390 | 1.3713 | 0.300 | 95.3 | 49.9 |
| CUSUM | 2 | 0.0815 | **0.200** | 0.6191 | 0.6578 | 1.0664 | 0.200 | 124.8 | 61.6 |
| CUSUM | 3 | 0.0913 | **0.200** | 0.5150 | 0.5346 | 0.9250 | 0.200 | 145.0 | 69.4 |
| CUSUM | 5 | 0.1084 | **0.163** | 0.4053 | 0.4117 | 0.7613 | 0.163 | 175.6 | 80.1 |
| SR | 1 | 0.0608 | **0.300** | 0.8398 | 0.9437 | 1.3667 | 0.300 | 90.8 | 48.4 |
| SR | 2 | 0.0741 | **0.200** | 0.6179 | 0.6622 | 1.0579 | 0.200 | 119.4 | 59.4 |
| SR | 3 | 0.0835 | **0.200** | 0.5133 | 0.5367 | 0.9098 | 0.200 | 138.7 | 66.6 |
| SR | 5 | 0.0995 | **0.199** | 0.4049 | 0.4128 | 0.7426 | 0.150 | 167.8 | 78.6 |

Replicate 95% intervals on `RMS` are `+/-0.003` to `+/-0.004`, so the interior
minimum is many standard errors deep.

**Three readings.**

1. **The measured dispersion-optimal reuse fraction is `1.5x` to `4.9x`
   `rho_c`.** The
   locally-stable region `rho < rho_c` is *not* the low-dispersion region.
   Operating exactly at `rho_c` is `1.5%–11.6%` worse than the optimum, and
   `rho -> 0` (fresh reference) is worse still. This is the sharpest form of
   P7's "not an operational boundary": at `rho_c` the dispersion curve is still
   *descending*.
2. **The in-control ARL is maximised at the same `rho`**, to within one grid
   point in 7 of 8 cells (SR `m=5`: 0.150 vs 0.199, adjacent grid points that
   differ by 0.5% in ARL). Low reference dispersion and long in-control cycles
   are the same objective here, which is what makes a dispersion-based control
   target credible for P6.
3. The mechanism of the optimum is visible in T2: `V_{rho}(e) = rho^2 S(e) +
   (1-rho)^2/m`. Increasing `rho` trades *fresh-reference noise* `(1-rho)^2/m`
   (falling) against *reused stopped-window noise* `rho^2 S(e)` and the
   increasingly strong anti-correlated dynamics (rising). Neither term alone
   explains the shape; the minimum is where their derivatives balance.

Tail measures move with `RMS`: for CUSUM `m=1`, `P(|e|>2)` falls from `0.045`
(`rho=0`) to `0.016` (`rho=0.3`) and rises to `0.139` (`rho=1`); `q95(|e|)`
follows the same U.

## 3. The 2-cycle is present — in time, not in the marginal law

The flip bifurcation of T9 leaves an unmistakable *temporal* signature and
almost none in the marginal distribution.

CUSUM `m=1`, selected `rho` (replicate 95% intervals on `ACF1` are `+/-0.004`):

| `rho` | `rho/rho_c` | `ACF1` | sign-alternation rate | excess kurtosis | RMS |
|---|---|---|---|---|---|
| 0.00 | 0.0 | -0.001 | 0.500 | -0.01 | 0.999 |
| 0.067 | **1.0** | -0.060 | 0.534 | +0.00 | 0.939 |
| 0.20 | 3.0 | -0.196 | 0.613 | -0.02 | 0.859 |
| 0.50 | 7.5 | -0.471 | 0.814 | -0.44 | 0.908 |
| 0.80 | 11.9 | -0.536 | **0.892** | -0.70 | 1.152 |
| 1.00 | 14.9 | -0.497 | 0.879 | -0.64 | 1.371 |

* The alternation rate rises from the coin-flip value `0.500` to `0.89`: nearly
  nine cycles in ten re-baseline to the *opposite* side. That is the period-2
  orbit, executed stochastically.
* The distribution stays **platykurtic** (excess kurtosis `-0.70`, never
  positive in this slice), but the dedicated density experiment below finds it
  bimodal by this `rho`. The reference law is not heavy-tailed in the measured
  regime.
  P7's heavy detection-delay tail therefore comes from the response function
  `A(e - Delta)` acting on an `O(1)`-dispersed reference error, **not** from a
  heavy-tailed reference law. See `LIMITATIONS.md` §5.
* Nothing localises at `rho_c`. `ACF1` and the alternation rate grow *smoothly*
  from `rho = 0`, with no kink, and pass `rho_c` at `-0.060` and `0.534` —
  ordinary values. A pre-registered curvature probe (second difference at
  `rho_c` in units of its own standard error, ranked against every other
  interior grid point) puts `rho_c` **first in 0 of 40** detector x window x
  metric combinations, and its best rank is 4th of 21. **P7's C2 is
  independently reconfirmed with a different criterion, on a different
  statistic, from a different campaign.**

## 4. Mixing and ergodicity evidence

* **Lag-1 autocorrelation is negative everywhere `rho > 0`**, so the chain is
  *better mixed than iid* for mean-type functionals; the initial-positive-
  sequence integrated autocorrelation time is at its floor (`<= 1.0` cycles) in
  every one of the 176 cells. Practically, the chain forgets its state in one
  cycle for the measured mean-type summaries. The estimator is floored at one,
  so this is not evidence that every functional mixes faster than iid.
* **Initial-condition independence.** Comparing the `e_0 = 0`, `+6` and `-6`
  groups after burn-in over `RMS`, `ACF1` and `ARL` in all 176 cells: 552
  max-of-three-pairs `z` values with median `1.11`, only `2` above `3`, maximum
  `3.88`. The null distribution of that maximum has median `3.53` and 95th
  percentile `4.17`, so this is noise.
  This is the empirical face of the uniform ergodicity proved in T7.

## 5. Runaway hunt (deliberate)

`experiments/run_stress.py`: `e_0 in {0, 5, 20, 100, 1000, -1000, 10^6}`,
`rho in {0.9, 0.99, 1.0}`, both detectors, `m in {1,5}`, 200 replicates x 400
cycles each.

| `e_0` | max over cells of mean `|e_1|` (one cycle) | max over cells of max `|e_1|` | max tail RMS (cycles 100+) |
|---|---|---|---|
| 0 | 1.934 | 4.357 | 1.373 |
| 5 | 0.877 | 3.600 | 1.369 |
| 20 | 0.848 | 3.790 | 1.371 |
| 100 | 0.857 | 3.423 | 1.371 |
| 1000 | 0.851 | 3.297 | 1.372 |
| **10^6** | **0.825** | **3.226** | **1.373** |

**One cycle after starting at `e_0 = 10^6`, the mean absolute reference error is
`0.83`.** The largest absolute reference error ever observed at any cycle after
the initial one, across every stress configuration, is `5.43`. No observed
stress trajectory left the ordinary stationary range after its initial state.

Direct measurement of the forgetting: at `|e| >= 100`, `P(tau = 1) = 1.000000`,
`R(e) = -0.0006 +/- 0.0008` and `S(e) = 1.000` for **every measured** `m`, for
both detectors. The one-step law is empirically indistinguishable from
`N(0, rho^2 + (1-rho)^2/m)` there. It is not exactly normal at finite `e`
because a Gaussian tail leaves nonzero probability of `tau>1`.

## 6. Mode structure: a stochastic period-2 orbit, not metastability

`experiments/run_density.py` (`results/density.json`, `density_crossover.json`):
per-replicate histograms over 240 replicates x 3600 post-burn-in cycles
(864000 samples per cell), skeleton orbit `+/-e*(rho)` overlaid. The
pre-registered statistic is the per-replicate contrast

```
C(rho) := [ dens(+e*) + dens(-e*) ] / 2  -  dens(0) ,
```

negative = mass at the origin (unimodal), positive = mass on the orbit
(bimodal), with a replicate standard error.

| `rho` | CUSUM m=1 `C` | CUSUM m=3 `C` | SR m=1 `C` | mean residence (cycles) | alternation | excess kurtosis (CUSUM m=1) |
|---|---|---|---|---|---|---|
| 0.30 | -0.057 +/-0.008 | -0.121 +/-0.010 | -0.051 +/-0.008 | 1.46 | 0.68 | -0.10 |
| 0.40 | -0.078 +/-0.007 | -0.059 +/-0.009 | -0.072 +/-0.007 | 1.33 | 0.75 | -0.25 |
| 0.50 | -0.030 +/-0.006 | **+0.030** +/-0.008 | -0.033 +/-0.007 | 1.23 | 0.81 | -0.44 |
| 0.60 | **+0.012** +/-0.007 | +0.108 +/-0.008 | **+0.004** +/-0.007 | 1.17 | 0.86 | -0.59 |
| 0.70 | +0.043 +/-0.006 | +0.148 +/-0.007 | +0.040 +/-0.006 | 1.13 | 0.88 | -0.67 |
| 0.80 | +0.044 +/-0.006 | +0.140 +/-0.008 | +0.046 +/-0.006 | 1.12 | 0.89 | -0.69 |
| 1.00 | +0.026 +/-0.006 | +0.057 +/-0.007 | +0.025 +/-0.006 | 1.14 | 0.88 | -0.63 |

**Bimodality onset** (linear interpolation of the `C = 0` crossing;
`results/bimodality_onset.json`):

| det | m | onset `rho` | in units of `rho_c` |
|---|---|---|---|
| CUSUM | 1 | 0.579 | **8.6 x** |
| CUSUM | 3 | 0.472 | **5.2 x** |
| SR | 1 | 0.593 | **9.8 x** |
| SR | 5 | 0.411 | **4.1 x** |

Three conclusions.

1. **The stationary law does become genuinely bimodal**, with modes at the
   skeleton 2-cycle `+/-e*(rho)`. The flip bifurcation is not merely a property
   of a deterministic caricature — it eventually reshapes the invariant law.
2. **It does so only at `4x`–`10x rho_c`.** Near the boundary the law is
   unambiguously unimodal (`C` is negative and many standard errors from zero at
   `rho = 0.3`, which is already `3x`–`4x rho_c`). This is T10 made visible: the
   orbit needs `SNR` of order `1` before it can dent the marginal law, and
   `SNR(rho_c) ~ 0.01`.
3. **This is not metastability, and there are not two regimes.** Mean residence
   on one side is `1.08`–`1.46` cycles and *falls* as `rho` rises, while the
   alternation rate rises to `0.93`. The chain does not dwell in a mode; it
   flips almost every cycle. Combined with T7 (the invariant law is **unique**),
   the correct description is a *single* invariant law whose mass has moved onto
   a stochastically executed period-2 orbit. Multiple attractors, coexisting
   invariant measures and metastable regimes are all **rejected**.

The law also stays platykurtic throughout (excess kurtosis `-0.09` to `-1.02`,
never positive): bimodal and light-tailed, not heavy-tailed.
