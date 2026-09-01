# P6 results

```text
SEED FAMILY      = EVAL (reported); TUNE used only for calibration and screening; REPLAY reproduces
PRIMARY CELL     = CUSUM, m = 3, Delta = 1.0        (preregistered)
PRIMARY OBJECTIVE= Dtail(100)                        (preregistered)
BAR              = B2*, the best fixed rho in the frozen grid AT MATCHED FRESH  (never B3)
```

All numbers are per-replicate summaries; the unit is the independent replicate.
In-control cells: `n_rep = 8000`, `n_cycles = 100`, `burn_in = 15`. Delay cells:
`n_rep = 60000`, shift injected at cycle 15, one delay observation per
replicate. Intervals are paired bootstraps over replicate pairs, `B = 4000`.

---

## 0. Foundation (Stage 1) — the numbers are believable

| check | result |
|---|---|
| `X1` bit-identity vs `rebaseguard_p7.chain.simulate_chain` | **24/24 cells** `tau` identical; `max |e_start difference| = 0.0` exactly |
| `X2` convention A | `e_{j+1} = e_j + zbar_j` at `rho = 1` to `0.0` residual; truncated-window fraction `0.09%`-`5.3%` |
| `X3` reproduction of P7's published `Arl0` | **40/40** cells' 95% intervals overlap P7's bootstrap intervals; `max |z| = 2.53` over 40 comparisons |
| `X4` detector identity | the CUSUM step is the imported frozen `cusum_update`; the SR step is the verbatim Stage-D recursion |
| `X5` observability | 93 focused tests pass, including field-set and no-reaction-to-latent-fields assertions |
| `c_beta` | re-derived from P7's closed response curve: `c_{0.25} = 0.2816` (CUSUM), `0.2656` (SR), interpolation bracket `0.05` |
| burn-in | R3 curves flat from cycle 5-8 for every policy; `burn_in = 15` used, above the requirement |

## 1. Calibration (TUNE, `Delta = 0` only) — the sensor is real

| cell | `g0` | `g1` | `s0` | `s1` | `R^2` | `E[V]` | `sd(V)` | `rho_flat` |
|---|---|---|---|---|---|---|---|---|
| CUSUM m=1 | 0.9663 | -1.0189 | 0.1234 | 0.1234 | **0.951** | 2.519 | 1.913 | 0.284 |
| CUSUM m=2 | 0.9480 | -1.0615 | 0.0809 | 22.77 | 0.951 | 1.663 | 1.130 | 0.231 |
| CUSUM m=3 | 0.9384 | -1.0667 | 0.0626 | 2.560 | 0.952 | 1.324 | 0.814 | 0.201 |
| CUSUM m=5 | 0.9201 | -1.0321 | 0.0433 | 0.498 | 0.951 | 0.949 | 0.450 | 0.174 |
| SR m=1 | 0.9904 | -1.1679 | 0.1173 | 0.1173 | 0.953 | 2.501 | 1.924 | 0.286 |
| SR m=2 | 0.9703 | -1.2167 | 0.0750 | 0.0750 | 0.954 | 1.634 | 1.119 | 0.234 |
| SR m=3 | 0.9601 | -1.2386 | 0.0582 | 5.176 | 0.954 | 1.281 | 0.796 | 0.207 |
| SR m=5 | 0.9457 | -1.2530 | 0.0410 | 0.712 | 0.954 | 0.910 | 0.456 | 0.180 |

Three things to read off this table.

1. **`R^2 = 0.95` in every cell.** The observable readout explains 95% of the
   variance of the latent raw window mean. The selection effect really is a
   sensor.
2. **`E[V] = 0.91` to `2.52` against the unselected `1/m` = `0.20` to `1.00`**:
   the alarm-selected window mean carries **2.5x to 4.7x** the second moment of
   an unselected mean of the same length. That inflation, fed back cycle after
   cycle, is the distortion mechanism.
3. **`rho_flat = nu/(E[V]+nu)`** — the reuse weight the *derivation* recommends
   if the sensor is switched off — is `0.174` to `0.286`. This was computed from
   the frozen model with no grid search at all, and it lands inside the interval
   where P7's `S12` independently measured the in-control ARL optimum. That is a
   consistency check on the derivation, not a novelty claim.

`s1` (the truncated-window variance) is estimated from a group holding 0%-5% of
cycles; at CUSUM `m=2` and SR `m=3` that group holds under a hundred
observations and the estimate is correspondingly noisy. Its effect is confined
to those cycles and is always conservative (less reuse on an anomalous cycle).

## 2. Headline: SAW vs the best fixed reuse weight, at matched cost, in all 8 families

`B2*` is re-selected on `EVAL` per cell as the grid member minimising the
primary objective. **`Fresh` is identical for SAW and `B2*` in every cell**
(`3.00` vs `3.00` at `m = 3`, etc.), so the comparison is exactly cost-matched
under the approved primary cost model.

| cell | `B2*` | `Arl0` `B2*` -> SAW | rel | `Rms` `B2*` -> SAW | rel | `Dtail100` `B2*` -> SAW | rel | `Dq95` | `Rdelta` `B2*` -> SAW | `Coll` `B2*` -> SAW |
|---|---|---|---|---|---|---|---|---|---|---|
| CUSUM m=1 | 0.15 | 92.7 -> 106.0 | **+14.4%** | 0.8782 -> 0.7780 | **-11.4%** | 0.1125 -> 0.1057 | -6.0% | 261 -> 252 | 0.566 -> 0.473 | 0.195 -> 0.200 |
| CUSUM m=2 | 0.25 | 123.9 -> 132.8 | +7.2% | 0.6161 -> 0.5818 | -5.6% | 0.0923 -> 0.0830 | -10.1% | 210 -> 187 | 0.361 -> 0.313 | 0.231 -> 0.251 |
| **CUSUM m=3** | 0.15 | 144.1 -> 151.5 | +5.1% | 0.5177 -> 0.4909 | -5.2% | 0.0677 -> 0.0607 | **-10.4%** | 144 -> 125 | 0.251 -> 0.219 | 0.293 -> 0.301 |
| CUSUM m=5 | 0.15 | 174.7 -> 178.9 | +2.4% | 0.4059 -> 0.3932 | -3.1% | 0.0382 -> 0.0341 | -10.9% | 76 -> 68 | 0.141 -> 0.131 | 0.375 -> 0.366 |
| SR m=1 | 0.20 | 90.5 -> 101.3 | +12.0% | 0.8545 -> 0.7779 | -9.0% | 0.1062 -> 0.1013 | -4.7% | 252 -> 235 | 0.562 -> 0.480 | 0.187 -> 0.189 |
| SR m=2 | 0.20 | 119.5 -> 127.2 | +6.5% | 0.6178 -> 0.5822 | -5.8% | 0.0863 -> 0.0766 | -11.3% | 199 -> 169 | 0.367 -> 0.313 | 0.245 -> 0.243 |
| SR m=3 | 0.20 | 138.6 -> 145.5 | +5.0% | 0.5110 -> 0.4886 | -4.4% | 0.0634 -> 0.0579 | -8.6% | 133 -> 119 | 0.254 -> 0.221 | 0.290 -> 0.283 |
| SR m=5 | 0.25 | 162.8 -> 172.0 | +5.6% | 0.4088 -> 0.3915 | -4.3% | 0.0349 -> 0.0316 | -9.6% | 72 -> 65 | 0.148 -> 0.133 | 0.319 -> 0.348 |

**8 of 8 families improve on every one of `Arl0`, `Rms`, `Dtail(100)`, `Dq95`
and `Rdelta`, at identical fresh-sample cost.** The `Arl0` and `Rms` differences
are resolved (paired interval excludes zero) in all 8; `Arl0` exceeds the 10%
materiality threshold in the two `m = 1` cells and is resolved-but-below-10%
elsewhere.

## 3. The primary cell in full — CUSUM, `m = 3`, `Delta = 1.0`

Absolute values (`Fresh` in observations per alarm):

| policy | `Arl0` | `Fap100` | `Rms` | `Mad` | `OutCal(.25)` | `Fresh` | `Wbar` | `FreshProp` | `Coll` | `Dmean` | `Dmed` | `Dq95` | `Dtail50` | `Dtail100` | `Rdelta` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `B3` full reuse | 69.31 | 0.849 | 0.9235 | 0.7819 | 0.8236 | **0.00** | 1.000 | 0.00 | **0.016** | 64.65 | 9 | 341 | 0.2108 | **0.1429** | 0.933 |
| `B0` fresh-only | 132.48 | 0.692 | 0.5751 | 0.4603 | 0.6254 | 3.00 | 0.000 | 3.00 | 0.289 | 41.53 | 9 | 184 | 0.1339 | 0.0819 | 0.313 |
| `B2*` = `rho=0.15` | 144.10 | 0.664 | 0.5177 | 0.4145 | 0.5881 | 3.00 | 0.150 | 2.55 | 0.293 | 36.13 | 9 | 144 | 0.1162 | 0.0677 | 0.251 |
| `B6` two-level `|zbar|` | 137.52 | 0.679 | 0.5175 | 0.4208 | 0.6115 | 3.00 | 0.277 | 2.17 | 0.235 | 37.06 | 9 | 149 | 0.1192 | 0.0700 | 0.269 |
| `B11` confidence gate | 135.69 | 0.683 | 0.5294 | 0.4291 | 0.6163 | 3.00 | 0.251 | 2.25 | 0.227 | 36.73 | 9 | 152 | 0.1215 | 0.0709 | 0.271 |
| `SAW_A_flat` (sensor off) | 144.67 | 0.662 | 0.5132 | 0.4115 | 0.5867 | 3.00 | 0.201 | 2.40 | 0.280 | 36.31 | 9 | 146 | 0.1183 | 0.0686 | 0.251 |
| **`SAW_M`** | **151.52** | **0.646** | **0.4909** | **0.3917** | **0.5651** | 3.00 | 0.247 | 2.26 | 0.301 | **33.24** | 9 | **125** | **0.1066** | **0.0607** | **0.219** |
| `SAW_T` | 150.96 | 0.648 | 0.4950 | 0.3947 | 0.5667 | 3.00 | 0.214 | 2.36 | 0.308 | 33.36 | 9 | 128 | 0.1076 | 0.0611 | 0.221 |
| `Z1` oracle SAW | 156.53 | 0.632 | 0.4776 | 0.3790 | 0.5457 | 3.00 | 0.310 | 2.07 | 0.307 | 31.71 | 9 | 117 | 0.1017 | 0.0572 | 0.203 |
| `B9` `k = 2m` | 172.10 | 0.594 | 0.4041 | 0.3261 | **6.00** | 6.00 | 0.200 | 4.80 | 0.333 | 23.70 | 9 | 75 | 0.0747 | 0.0368 | 0.138 |
| `B9` `k = 4m` | 190.59 | 0.546 | 0.3372 | 0.2766 | **12.00** | 12.00 | 0.200 | 9.60 | 0.361 | 17.01 | 9 | 49 | 0.0471 | 0.0170 | 0.089 |

Paired effects of `SAW_M` against `B2*`, with 95% bootstrap intervals and P7's
verdict labels (materiality `10%` relative):

| metric | relative effect | 95% interval | verdict |
|---|---|---|---|
| **`Dtail(100)`** (primary) | **-10.4%** | `[-14.3%, -6.4%]` | **PRACTICALLY_MATERIAL** |
| `Dtail(50)` | -8.3% | `[-11.1%, -5.4%]` | STATISTICALLY_RESOLVED |
| `Dq95` | -13.2% | `[-18.6%, -7.8%]` | PRACTICALLY_MATERIAL |
| `Dmean` | -8.0% | `[-11.3%, -4.5%]` | STATISTICALLY_RESOLVED |
| `Dmed` | 0.0% | `[0.0%, 0.0%]` | INCONCLUSIVE (both `9`) |
| `Arl0` | +5.1% | `[+4.5%, +5.7%]` | STATISTICALLY_RESOLVED |
| `Fap(100)` | -2.7% | `[-3.0%, -2.5%]` | STATISTICALLY_RESOLVED |
| `Rms` | -5.2% | `[-5.4%, -5.0%]` | STATISTICALLY_RESOLVED |
| `Mad` | -5.5% | `[-5.7%, -5.3%]` | STATISTICALLY_RESOLVED |
| `Q95e` | -4.9% | `[-5.2%, -4.6%]` | STATISTICALLY_RESOLVED |
| `Tail(0.5)` | -8.5% | `[-8.9%, -8.1%]` | STATISTICALLY_RESOLVED |
| `Tail(1.0)` | -20.4% | `[-21.5%, -19.2%]` | PRACTICALLY_MATERIAL |
| `OutCal(0.25)` | -3.9% | `[-4.2%, -3.6%]` | STATISTICALLY_RESOLVED |
| `Coll` | +0.8% | `[-4.7%, +6.4%]` | INCONCLUSIVE (0.301 vs 0.293) |
| **`Fresh`** | **0.0%** | `[0.0%, 0.0%]` | matched exactly |
| `Wbar` | **+64.8%** | `[+64.6%, +64.9%]` | 0.247 vs 0.150 |
| `FreshProp` (sensitivity) | **-11.4%** | `[-11.5%, -11.4%]` | cheaper under the proportional model too |

Three readings.

* **`Dmed` does not move.** Both medians are `9`, against a nominal `10.35`.
  This is `S9` reproduced exactly: the damage and the repair are both in the
  right tail, and a campaign reporting mean delay alone would have seen a small
  effect and missed the shape of it.
* **SAW reuses *more* and distorts *less*, at the same sample cost.** Its mean
  algebraic reuse weight is 65% above `B2*`'s while its reference RMS is 5.2%
  lower and its `Arl0` is 5.1% higher. It is not buying safety by reusing less;
  it is buying it by reusing *selectively*.
* **Pair correlations are `~0.00`** in every comparison. The pre-design's
  warning holds exactly: common random numbers in this chain are seed alignment,
  not path coupling. Sizing used the unpaired variance, as preregistered, and
  the pairing delivered no variance reduction at all.

Against `B3` (full reuse, the sanity check, not the bar):
`Dtail(100)` **-57.6%** `[-59.1%, -56.0%]`, `Dq95` **-63.4%**, `Dmean` -48.6%.

## 4. Shift sensitivity — where the advantage exists, and where it does not

CUSUM `m = 3`:

| policy | `Delta=0.5` `Dtail100` | `Rdelta` | `Delta=1` `Dtail100` | `Rdelta` | `Delta=2` `Dq95` | `Rdelta` |
|---|---|---|---|---|---|---|
| `B3` full reuse | **0.1639** | **1.074** | 0.1429 | 0.933 | 30 | 0.187 |
| `B0` fresh-only | 0.2224 | 0.742 | 0.0819 | 0.313 | 11 | 0.041 |
| `B2*` | 0.2289 | 0.697 | 0.0677 | 0.251 | 10 | 0.034 |
| `SAW_M` | 0.2277 | **0.654** | **0.0607** | **0.219** | **9** | **0.030** |
| `Z1` oracle | 0.2266 | 0.649 | 0.0572 | 0.203 | 9 | 0.031 |

**`Dtail(100)` is not reported at `Delta = 2`**: the preregistered tail-event
floor is 200 events per arm and the `Delta = 2` cells deliver between `0` and
`170` for most arms (12 for `SAW_M` at CUSUM `m=3`, 2 at `m=5`). Those estimates
are labelled **`INSUFFICIENT_TAIL_EVENTS`**, never `INCONCLUSIVE` — the two mean
different things and conflating them would hide a design failure. `Dq95`, which
needs far fewer events, is reported instead, and it is the preregistered
fallback. All `Delta = 1` cells clear the floor comfortably (`269` to `8,576`
events per arm), as do all `Delta = 0.5` cells (`6,278` upward).

**At `Delta = 0.5` SAW's advantage disappears** (`0.2277` vs `B2*`'s `0.2289`),
and full reuse has the *smallest* delay tail of any policy. That is not a point
in full reuse's favour and the campaign must not present it as one: at
`Delta = 0.5` its discrimination ratio is `Rdelta = 1.074 > 1`, i.e. **the
shifted cycle is longer than the in-control cycle** — the pathological regime
`S6` names. Its short delays are false alarms arriving at a rate of one per 69
in-control observations, not detections. On `Rdelta`, the metric that is not
confounded by the in-control alarm rate, `SAW_M` is best at **every** measured
shift including `0.5`.

The honest statement is therefore: *SAW's delay-tail advantage over the best
fixed reuse weight is material at `Delta = 1`, present but not resolvable at the
available tail-event budget at `Delta = 2`, and absent at `Delta = 0.5`; its
discrimination-ratio advantage holds at all three.*

## 5. Cost, and the shape of the frontier

Under the approved primary cost model `C_fresh = k_j 1{rho_j < 1}`:

* `B3` (full reuse) is the **unique zero-cost policy** and the monitoring-worst
  one (`Arl0 = 69.3` against a nominal `465`, `Coll = 0.016`, i.e. P7's `S8`
  98% collapse reproduced).
* **every** policy that draws any fresh baseline pays exactly `k` per alarm, so
  at `k = m` all of `B0`, the whole `B2` grid, `B6`, `B11`, `SAW_M`, `SAW_T` and
  `Z1` sit at *the same cost point*, and the comparison between them is exactly
  matched.
* `Fresh` therefore separates policies only through `k`. `B9` at `k = 2m` and
  `k = 4m` dominates everything at `k = m` — buying safety with data always
  works — which is precisely why the bar is `B2*` at matched cost and not `B3`.
* Under the declared *proportional* sensitivity `(1-rho_j) k_j`, `SAW_M` is
  **11.4% cheaper** than `B2*` as well as safer, because it reuses more on
  average.

The `k`-indexed frontier is in `ROBUSTNESS.md` section 1.

## 6. Mechanism confirmation — the theory's own quantitative prediction

`THEORY.md` T6-C(iii) says the adaptive rule beats the best fixed one **iff**
the plug-in error is below the Jensen gap, and both sides are measurable
without running the policy. Measured on `EVAL`:

| cell | `E[V]` | `sd(V)` | Jensen gap (rel) | plug-in error | margin | **predicted** one-step `E[e^2]` gain | **measured** stationary `E[e^2]` gain | calibration `corr` |
|---|---|---|---|---|---|---|---|---|
| CUSUM m=1 | 2.517 | 2.318 | 15.91% | 0.0084 | 0.1055 | **14.7%** | 21.5% | 0.997 |
| CUSUM m=2 | 1.660 | 1.388 | 12.17% | 0.0039 | 0.0429 | **11.2%** | 10.8% | 0.998 |
| CUSUM m=3 | 1.325 | 1.024 | 10.19% | 0.0029 | 0.0243 | **9.1%** | 10.1% | 0.999 |
| CUSUM m=5 | 0.948 | 0.584 | 6.94% | 0.0016 | 0.0099 | **6.0%** | 6.1% | 0.999 |
| SR m=1 | 2.504 | 2.307 | 16.28% | 0.0091 | 0.1073 | **15.0%** | 17.2% | 0.997 |
| SR m=2 | 1.633 | 1.356 | 12.58% | 0.0044 | 0.0437 | **11.4%** | 11.2% | 0.998 |
| SR m=3 | 1.278 | 0.976 | 10.24% | 0.0027 | 0.0244 | **9.2%** | 8.6% | 0.999 |
| SR m=5 | 0.911 | 0.573 | 7.09% | 0.0014 | 0.0102 | **6.2%** | 8.4% | 0.999 |

* The criterion is satisfied in **8/8** cells, with the plug-in error at
  **7.4%-13.9%** of the gap — a comfortable margin, and one that widens as `m`
  falls (7.4% at `m=1`, 13.9% at `m=5`), i.e. the plug-in is relatively most
  accurate exactly where the gap is largest.
* **What `V` means here, precisely, because it is easy to overstate.** The
  reference quantity is estimated by binning on `V_hat` itself (200 equal-count
  bins, taking the realised `U^2` mean inside each), so what is measured is
  `E[U^2 | V_hat]` — the **calibration** of the plug-in — and not `E[U^2 | F_j]`
  against the full observable sigma-field. The last column is therefore a
  calibration correlation and should not be read as "the plug-in is 99.9%
  accurate". Two consequences, both in P6's *disfavour* and stated for that
  reason: the Jensen gap reported here is the one available on
  `sigma(V_hat) subset F_j`, i.e. a **lower bound** on what a better plug-in
  could reach; and the plug-in error reported here is likewise the
  `sigma(V_hat)`-restricted one. The honest measure of how much of the latent
  quantity the observables carry is the calibration regression's
  `R^2 = 0.951`-`0.954` (section 1), which is a genuinely out-of-sample-shaped
  statistic and is not computed by binning on the fit.
* The prediction is **quantitative, and it holds**: for `m >= 2` the measured
  stationary reduction in `E[e^2]` matches the one-step prediction to within
  about 2 percentage points, and the ordering across `m` (largest gain at
  `m = 1`, smallest at `m = 5`) is reproduced exactly.
* At `m = 1` the measured stationary gain (`21.5%`, `17.2%`) **exceeds** the
  one-step prediction (`14.7%`, `15.0%`). That is the expected direction — the
  improvement recurses — and it is also the honest limit of the theory: T6-C is
  a one-step statement from a common entering law and does not predict the
  stationary magnitude.

The SAW-T Gaussian approximation of `THEORY.md` T6-D(c) was measured against a
Monte Carlo evaluation of the realised tail: overall predicted vs empirical
exceedance agree to `0.0005`-`0.003`, with a worst decile-bin gap of `0.013` to
`0.020`.

## 7. Two P5 questions P6 was asked to re-verify

* **`P8` (RMS/ARL co-optimality) does NOT reproduce at P5's strength.** On P6's
  own `EVAL` grid, `argmax_rho Arl0` and `argmin_rho Rms` over the frozen `B2`
  grid coincide in only **2 of 8** cells (CUSUM `m=3`, SR `m=3`) and are
  **adjacent grid points in the other 6** — never further apart than one grid
  step, and always with `Rms`'s optimum at the *larger* `rho`:

  | cell | `argmax Arl0` | `argmin Rms` | | cell | `argmax Arl0` | `argmin Rms` |
  |---|---|---|---|---|---|---|
  | CUSUM m=1 | 0.25 | 0.30 | | SR m=1 | 0.25 | 0.30 |
  | CUSUM m=2 | 0.20 | 0.25 | | SR m=2 | 0.20 | 0.25 |
  | CUSUM m=3 | 0.20 | **0.20** | | SR m=3 | 0.20 | **0.20** |
  | CUSUM m=5 | 0.15 | 0.20 | | SR m=5 | 0.15 | 0.20 |

  P5 measured 7-of-8 exact coincidence on its grid; P6 measures 2-of-8 with a
  systematic one-step offset on a different (coarser in this region) grid. The
  two are compatible — both say "co-located, within grid resolution" — but P6's
  result is *weaker*, and the systematic direction of the offset suggests the
  two optima are genuinely distinct points that a coarse grid cannot separate.
  **This is a reproduction failure of the strong reading of `P8`**, and it
  matters: it removes any remaining licence to treat `Rms` as a surrogate for
  `Arl0`. P6 does not: both are measured everywhere, as `S18`/`X6` require.
* **`P9` (`m` monotonicity).** Increasing `m` raises `Arl0` and lowers `Rms` for
  every policy measured here, over `m in {1,2,3,5}` — the same direction P5
  measured, with the same scope limit. It also *shrinks* SAW's advantage
  (`Arl0` gain `+14.4%` at `m=1` down to `+2.4%` at `m=5`), which the theory
  predicts: the Jensen gap falls with `m` because averaging more observations
  reduces the dispersion of the selection intensity. `X8`'s resolution applies:
  `S14`'s reuse-attributable ARL loss growing with `m` is a *ratio against the
  same-`m` fresh control*, while this is an absolute level; the two are
  measured against different controls and do not conflict.

## 8. Screening drops (Stage 2, TUNE) — reported, not hidden

| policy | rule | reason and numbers (CUSUM `m=3`, TUNE) |
|---|---|---|
| `B7_overshoot` | `ES2` strict domination | `Arl0 = 133.1`, `Rms = 0.5408` against `B2_rho0.2`'s `145.2` / `0.5120` at identical `Fresh`; worse on both coordinates in all 8 families |
| `B8_window_disp` | `ES2` strict domination | `Arl0 = 134.2`, `Rms = 0.5404`; and its sensor, the terminal-window sample variance, estimates the *innovation* variance, which is `1` by construction. This was predicted in the pre-design as "expected to be near-useless, and that is a useful negative" |
| `B10_capped` | `ES2` strict domination | `Arl0 = 113.9`, `Rms = 0.5991`; the consecutive-reuse cap forces periodic full refreshes that cost `Arl0` without buying `Rms`, and it carries internal state, so `T6-B` would not apply to it |

No policy was dropped by `ES1`, `ES3`, `ES4` or `ES5`. In particular **no policy
became cost-degenerate** (`ES3`/`F3`): under the step-shaped cost model that
failure mode cannot occur at fixed `k`, which is itself a finding about the cost
model rather than about the policies.
