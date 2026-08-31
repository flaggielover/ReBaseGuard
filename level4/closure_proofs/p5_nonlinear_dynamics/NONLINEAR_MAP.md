# The nonlinear conditional-mean map

Tier: **NUMERICAL EVIDENCE** for the measured function `R`; the structural
statements built on it are the CONDITIONAL THEOREMS T8–T10 of `THEOREM.md`.

## 1. What is measured, and why one function suffices

By T2 the conditional-mean map factorises,

```
M_{D,m,rho}(e) = rho * R_{D,m}(e) ,      R_{D,m}(e) = E[Rbar | e] ,
V_{D,m,rho}(e) = rho^2 S_{D,m}(e) + (1-rho)^2/m ,   S_{D,m}(e) = Var(Rbar | e) .
```

So a single pass over `e` determines the map for **every** `rho`. P5 measures
`R`, `S` and the response `A(e) = E[tau|e]` on a 49-point grid
`|e| in {0, 0.005, ..., 5}` (`experiments/run_nonlinear_map.py`) plus a 20-point
far-tail grid `|e| in {5.5, ..., 24}` (`run_map_tail.py`), for both detectors and
`m in {1,2,3,5}`, with `4e5`–`3.2e6` cycles per point in 8 independent batches.
The statistical unit is the batch; all intervals are batch standard errors.

Everything is reproduced on a second, independent seed family (`20261119`
against `20260501`). Across 392 paired grid cells the standardised differences
have `mean z = +0.016`, `sd z = 1.044`, `max|z| = 3.12` — an exact Monte Carlo
signature with no systematic offset.

## 2. The shape of `R`

`R` is an odd, bounded, saturating function with a very steep slope at the
origin and a decaying, sign-preserving tail:

| det | m | `R'(0)` measured | P3 `1 - GammaTilde` | rel. err | `rho_c` (P3) | `sup|R|` | at `|e| =` | `S(0)` | `A(0)` |
|---|---|---|---|---|---|---|---|---|---|
| CUSUM | 1 | -14.937 | -14.917 | 0.14% | 0.0670 | 1.564 | 0.30 | 4.036 | 465.2 |
| CUSUM | 2 | -12.203 | -12.265 | 0.51% | 0.0815 | 1.252 | 0.20 | 2.811 | 465.2 |
| CUSUM | 3 | -10.875 | -10.957 | 0.75% | 0.0913 | 1.100 | 0.20 | 2.274 | 465.2 |
| CUSUM | 5 |  -9.120 |  -9.226 | 1.15% | 0.1084 | 0.908 | 0.20 | 1.591 | 465.2 |
| SR | 1 | -16.266 | -16.454 | 1.14% | 0.0608 | 1.585 | 0.20 | 4.032 | 464.4 |
| SR | 2 | -13.336 | -13.501 | 1.22% | 0.0741 | 1.271 | 0.20 | 2.770 | 464.4 |
| SR | 3 | -11.786 | -11.973 | 1.56% | 0.0835 | 1.108 | 0.20 | 2.207 | 464.4 |
| SR | 5 |  -9.902 | -10.049 | 1.46% | 0.0995 | 0.909 | 0.20 | 1.563 | 464.4 |

A representative slice (CUSUM, `m=1`, `e > 0`; `R` in reference-error units,
batch s.e. `<= 0.0035`):

```
 e      0.005   0.02    0.05    0.10    0.20    0.30    0.50    1.00    2.00    3.00    4.00
 R     -0.077  -0.297  -0.699  -1.197  -1.555  -1.564  -1.413  -1.059  -0.562  -0.387  -0.235
 s=-R/e 15.32   14.85   13.98   11.97    7.78    5.21    2.83    1.06    0.26    0.13    0.06
 S       4.05    3.95    3.48    2.36    0.94    0.57    0.48    0.53    0.74    0.82    1.03
```

**Three regimes.**

1. **Linear / repulsive core, `|e| <~ 0.05`.** `R(e) ~ (1-GammaTilde) e` with a
   slope of `-9` to `-16`. This is exactly the P1/P2/P3 derivative, recovered to
   within `0.14%–1.6%` by a completely independent estimator. `r_lin ~ 0.05`
   (P7's grid-defined radius) is confirmed: the `10%` departure point.
2. **Saturation, `0.2 <~ |e| <~ 1`.** `|R|` peaks at `0.91–1.59` near
   `|e| = 0.2–0.3` and then *falls*. The map cannot amplify beyond
   `rho * sup|R| <= 1.59` no matter how large `e` is.
3. **Total forgetting, `|e| >~ 8`.** `A(e) -> 1`: the cycle ends on its first
   observation. Then `w = min(m,1) = 1` and `Rbar = raw_1`, whose selection
   constraint `raw_1 >= e + c_D` (or `<= e - c_D`) becomes vacuous. Measured:
   at `|e| >= 10`, `|R| <= 0.0021` (s.e. `0.0008`) and `S = 1.000` to three
   decimals for every measured `m`. The chain's one-step law is empirically
   indistinguishable from `N(0, rho^2 + (1-rho)^2/m)` there and converges to
   that reset law in the far-field limit. At finite `e`, Gaussian tails leave a
   nonzero probability of `tau>1`.

The tail is not monotone: `|R|` has a secondary lobe near `|e| ~ 5.5-7`
(CUSUM `|R| = 0.399` at `5.5`; SR `|R| = 0.388` at `6.5-7.0`), because there
the one-step alarm condition `raw_1 <= e - c_D` still bites. It decays to zero
beyond it. This is a real, reproducible feature (both seed families), not noise,
and it is why hypothesis (H3) is stated on `(0, E]` with `E = 2` plus the
`sup|R| < E` tail bound rather than globally.

## 3. The mechanism, stated plainly

By T1 the next reference error is `rho x (mean of at most m N(0,1) draws)` plus
independent `N(0,1/m)` noise. `e` acts **only** by biasing which draws land in
the terminal window. That bias is:

* maximal *per unit of `e`* at `e = 0`, where the alarm is rare and therefore
  extremely selective — one unit of reference error changes the terminal-window
  mean by 9–16 units, which is the entire content of `GammaTilde`;
* *bounded in absolute terms* everywhere, because a mean of `m` standard normals
  cannot be large in expectation however it is selected (T5 makes this a
  theorem);
* *vanishing* once `|e|` is large enough that the alarm is immediate, because a
  certain event selects nothing.

> **Local repulsion at `0` and global boundedness are not in tension: they are
> the same selection channel evaluated at two ends of its dynamic range.**
> The chain is locally repelling and globally *forgetting*. There is no
> "restoring drift" in the Lyapunov sense — the far field is not pushed back
> towards `0`, it is *erased* and redrawn from a fixed law.

## 4. Hypothesis audit for T8–T10

`experiments/audit_hypotheses.py`, pooling both seed families:

| det | m | (H1) oddness, max abs residual | (H2) `R<0` on `e>0` | (H3a) `s` strictly decreasing on `(0,2]` | (H3b) `sup|R| < 2` | `|R|` beyond `|e|=10` |
|---|---|---|---|---|---|---|
| CUSUM | 1 | 0.0093 (1.80 x 95% CI, 7/34 pairs) | holds | 1 violation, `z = 0.2` | 1.563 | 0.0012 (s.e. 0.0007) |
| CUSUM | 2 | 0.0071 (1.80 x) | holds | none | 1.252 | 0.0012 |
| CUSUM | 3 | 0.0061 (1.80 x) | holds | none | 1.099 | 0.0012 |
| CUSUM | 5 | 0.0065 (1.80 x) | holds | none | 0.908 | 0.0012 |
| SR | 1 | 0.0051 (1.91 x) | holds | none | 1.583 | 0.0021 |
| SR | 2 | 0.0034 (1.62 x) | holds | none | 1.271 | 0.0010 |
| SR | 3 | 0.0036 (1.35 x) | holds | none | 1.107 | 0.0010 |
| SR | 5 | 0.0033 (1.68 x) | holds | none | 0.908 | 0.0010 |

* **(H1)** is T3, an *exact theorem*, so this row is a falsification test of the
  simulator, not a hypothesis. The absolute residual never exceeds `0.011` in
  `R` units against `|R|` up to `1.59` (`<0.7%`). Residuals reach `1.35–1.91`
  times a `z`-based 95% batch interval and `3–7` of 34 pairs fall outside it;
  with only 8 batches a `z`-interval understates a `t_7` interval by 21%, and
  on the `t_7` scale the worst residual is `1.6 x` CI. This is logged as an
  open, non-material discrepancy in `ADVERSARIAL_REVIEW.md` A5, not as evidence
  against T3.
* **(H2)/(H3a)/(H3b)** hold in all eight cells within Monte Carlo error. The one
  nominal `s`-monotonicity violation (CUSUM `m=1`) has `z = 0.2`.

## 5. The bifurcating branch (T9) on the measured map

Solving `s(e*) = 1/rho` on the measured `s` (CUSUM `m=1`; SR `m=1` agrees to
`<0.003` everywhere):

| `rho` | `rho/rho_c` | `e*` | 2-cycle multiplier | noise s.d. at `e*` | `SNR` |
|---|---|---|---|---|---|
| 0.050 | 0.75 | — (no 2-cycle) | — | — | — |
| 0.067 | 1.00 | 0.0098 | 0.969 | 0.943 | **0.010** |
| 0.0815| 1.22 | 0.0929 | 0.264 | 0.928 | 0.100 |
| 0.15  | 2.24 | 0.2433 | 0.002 | 0.860 | 0.283 |
| 0.30  | 4.48 | 0.4439 | 0.056 | 0.731 | 0.608 |
| 0.50  | 7.46 | 0.6487 | 0.142 | 0.610 | 1.064 |
| 0.70  | 10.4 | 0.8262 | 0.178 | 0.581 | 1.422 |
| 0.80  | 11.9 | 0.9101 | 0.233 | 0.609 | **1.494** |
| 0.90  | 13.4 | 0.9754 | 0.295 | 0.661 | 1.476 |
| 1.00  | 14.9 | 1.0434 | 0.267 | 0.733 | 1.424 |

Read this table as the whole P3-to-P7 story:

* the 2-cycle **does** appear exactly at `rho_c` — the branch amplitude at
  `rho = rho_c` is `0.0065`–`0.0099` where the `0.005` map grid can resolve it
  at all (CUSUM `m=1,2,3,5` and SR `m=1,2`), with multiplier `0.93`–`0.98`,
  i.e. critical slowing down as a supercritical flip requires. In SR `m=3` and
  `m=5` the measured `s` at the innermost grid point `e = 0.005` falls a
  fraction of one standard error *below* `1/rho_c` (`11.924` vs `11.973`;
  `9.985` vs `10.049`), so the root lies below the grid and is reported as
  unresolved rather than absent: the exact amplitude at `rho_c` is `0`;
* it is attracting at every measured branch point on the finite `rho` grid —
  the multiplier never approaches `1` again in that scan. This is numerical
  evidence, not a proof over the full interval or a proof excluding a cascade;
* the **signal-to-noise ratio never exceeds `1.5` for `m=1`** (`2.1` for
  `m=5`) and is `~0.01` at the boundary itself. The orbit is buried in the
  chain's own noise floor over the entire admissible range.

`SNR` is *non-monotone*, peaking near `rho ~ 0.8` and falling slightly at
`rho = 1`, because the noise floor `rho^2 S(e*) + (1-rho)^2/m` is itself
non-monotone: reducing the fresh-noise term also increases `rho^2 S`.

## 6. Independent skeleton scan (no algebra used)

`experiments/run_skeleton.py` iterates the *measured, PCHIP-interpolated,
symmetrised* map `f_rho = rho R` from 84 initial conditions spanning `[-8, 8]`
plus `0` and `+/-1e-6`, for 199 values of `rho` in `[0.01, 1]`, discarding 4000
transient iterates and classifying the period of the last 256.

Result, in all eight `(D, m)` cells:

* **only periods 1 and 2 ever occur**; no period 4, no period 8, no aperiodic
  orbit, on the whole admissible range;
* the period-2 regime begins at `rho = 0.065–0.11` per cell, matching the
  frozen P3 `rho_c = 0.0608–0.1084` to within `0.0055` — one scan step in seven
  of eight cells and `1.1` scan steps in the eighth (SR `m=5`: onset `0.105`
  against `rho_c = 0.0995`, where the `1e-7` convergence tolerance rejects the
  `rho = 0.100` orbit whose amplitude is still below it);
* every initial condition except the exact fixed point `0` converges to the
  **same** orbit: `{0}` for `rho <= rho_c`, `{+e*, -e*}` for `rho > rho_c`.
  The reported "2 distinct signatures" per `rho` are the attractor plus the
  invariant point `e = 0` itself, reached only from `e_0 = 0` exactly. Orbits
  from `e_0 = +/-1e-6` leave `0` and land on the 2-cycle, i.e. `0` is repelling
  as T9 says;
* one cell (SR `m=2`, `rho = 0.075`, i.e. `1.01 x rho_c`) failed to converge to
  `1e-7` within 4000 iterations, with orbit amplitude `0.017`. That is critical
  slowing down at the bifurcation point (multiplier `-> 1`), not a third
  attractor;
* **no asymmetric 2-cycle was found anywhere.** T9's symmetric-branch algebra is
  therefore not merely a sufficient description: on the measured map it is the
  complete one.

## 7. Detector and window comparison

* **Detector.** CUSUM and SR have closely matching measured nonlinear summaries
  once ARL-matched: `e*(1) = 1.0434` (CUSUM) vs `1.0418` (SR) at `m=1`;
  `sup|R|` agrees to `<1.4%`; `SNR` agrees to 3 decimals at every `rho`. The
  clearest systematic detector difference is at the origin — SR's `GammaTilde` is
  ~9% larger, so SR's `rho_c` is ~9% smaller. These are finite-grid,
  ARL-matched comparisons and do not establish detector identity or universal
  transfer.
* **Window `m`.** Increasing `m` flattens the map (`|R'(0)|` falls `14.9 -> 9.1`
  for CUSUM), shrinks the orbit (`e*(1) = 1.043 -> 0.604`) and *raises* `rho_c`.
  It also raises the SNR (`1.42 -> 2.08`), because the noise floor falls faster
  (`S(0) = 4.04 -> 1.59`, fresh variance `1/m`) than the orbit does. Larger `m`
  is therefore *better* on dispersion and *marginally more visible* on
  structure — the two effects that P7 reported separately are here a single
  statement about the map.
