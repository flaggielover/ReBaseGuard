# P7 experiment design and analysis pre-commitment

Written after the runtime/variance pilot (`results/_pilot_notes.md`) and
**before** any production cell was analysed. The pilot fixed sizes and grids; it
did not fix verdicts. Where a pilot signal motivated a confirmatory claim, that
is said so explicitly, so nothing here can be read as a post-hoc discovery.

---

## 1. What P7 may and may not conclude

P7 asks a single question: *does the P1--P3 recursive re-baselining structure
produce a measurable, practically meaningful sequential-monitoring consequence?*

Owned elsewhere and deliberately out of scope:

| topic | owner |
|---|---|
| period-2 orbits, attractors, basins, hysteresis, bifurcation, global nonlinear dynamics | P5 |
| the safe re-baselining algorithm | P6 |
| detector-family / distribution-family / drift-pattern robustness matrix | P8 |

If P7 observes P5-type phenomena it records them as handoff observations only.

## 2. Factors

| factor | levels | why |
|---|---|---|
| detector | frozen CUSUM (`k=1/2, h=5`), frozen SR (`A=520.886133602749`) | the only two families P1/P2 close; ARL-matched at ~465.5 |
| window `m` | 1, 2, 3, 5 | exactly the windows P3 supports; no extrapolation |
| reuse `rho` | `{0.25, 0.5, 0.8, 1.0, 1.25, 1.5, 2, 4} x rho_c(D,m)`, plus absolute anchors `{0, 0.25, 0.5, 0.75, 1}` | ladder straddling the P3 boundary, plus the operating points a practitioner would actually pick |
| reference condition | in control; frozen alternatives `Delta in {0.5, 1.0}` | A/B/C outcomes |

`rho_c(D,m)` is **read at run time** from P3's `results/boundary_table.json`.
The `2x rho_c` and `4x rho_c` rungs exist so that "clearly repulsive" is
represented at a value not confounded with the practitioner anchors.

Full grid: 2 detectors x 4 windows x 13 reuse fractions = 104 cells.

## 3. Controls (both reported, never merged)

* **nominal** -- `A(0)`, the calibrated frozen `ARL_0` of a reference that is
  never updated. This is the calibration promise.
* **fresh** -- `rho = 0` at the same `m`: the reference is re-estimated from `m`
  fresh observations after every alarm. This is the matched-information control
  and is the denominator for every *reuse-attributable* claim.

Reporting an absolute ARL loss as a reuse effect would double count the fresh
control's own loss. It is not done anywhere in P7.

## 4. Designs

**E2/E6 chain sweep** (`experiments/run_chain_sweep.py`). Every cell starts at
`e_0 = 0` exactly, so one run gives the finite-cycle curve (`j = 0..49`) and the
quasi-stationary metrics (`j >= 12`). `n_rep = 5000`, `n_cycles = 50`,
`burn_in = 12`. Statistical unit = replicate.

**E3/E4 response curves** (`experiments/run_response_curves.py`). `A(x)` and
`g_m(x)` on a shared innovation stream per grid point, `x` from 0 to 3,
`n = 4x10^5` for `|x| <= 0.15`. Three negative `x` values are simulated purely
as a symmetry check.

**E5 delay.** The shift is applied at a re-baselining instant, the D2.5
convention. Because the detector resets and the innovations are iid, the delay
obeys the *exact* identity `E[tau | shift Delta] = E_pi[A(e - Delta)]`
(`THEORY_BRIDGE.md` §1). The grid is therefore evaluated through that identity
from the measured `pi` and `A`, and the identity itself is validated against
direct shifted-chain simulation at four cells. Any disagreement beyond Monte
Carlo error invalidates the identity route and it is abandoned, not patched.

**E7 boundary ladder.** The `rho/rho_c` rungs at higher precision for the
detector/window combinations retained after the sweep.

## 5. Common random numbers

CRN is used **only** where the coupling is exact and stated:

* within a response-curve grid point, `A(x)` and every `g_m(x)` share one
  innovation stream (perfect pairing across `m`);
* the delay identity reuses one measured `pi` across all `Delta`.

CRN is **not** used across `rho` in the chain sweep. Two chains at different
`rho` decouple after the first alarm because their alarm times differ, so a CRN
claim there would be false. Cells at different `rho` are independent.

## 6. Uncertainty

* Statistical unit is the replicate; every standard error is across replicates,
  which absorbs serial dependence inside a replicate rather than ignoring it.
* Cycle run lengths are heavy tailed (approximately geometric, `sd ~ mean`), but
  the *per-replicate mean over 38 cycles* is not. Both a normal-theory interval
  and a 10,000-resample replicate bootstrap percentile interval are computed for
  every ARL, and a disagreement greater than 20% of the interval width is
  reported as an estimator-stability warning rather than silently averaged.
* Right-censoring: none. Every cycle is run to its alarm; `max_steps` is a
  hard error, never a truncation. This is asserted by a test.

## 7. Pre-committed verdict language

| label | criterion |
|---|---|
| `STATISTICALLY RESOLVED` | the 95% CI of the effect excludes 0 |
| `PRACTICALLY MATERIAL` | resolved **and** the relative effect exceeds 10% with the CI excluding 5% |
| `INCONCLUSIVE` | otherwise |

## 8. Pre-committed boundary criterion (the highest-priority test)

Adapted deliberately from Stage-D D2.5 so that the two verdicts are comparable.

For each cell family `(D, m)` and each pre-specified metric `M`, compute the
local rate `|Delta M / Delta log(rho/rho_c)|` on every adjacent pair of the
`rho/rho_c` ladder. The boundary has an **observable statistical consequence**
only if the rate across the bracket containing `rho/rho_c = 1` is the maximum
over all brackets, in at least half of the eight `(D, m)` families, for at
least one pre-specified metric.

**Committed in advance:** smooth variation -- monotone or not -- with no
localised feature at `rho/rho_c = 1` will be reported as *the P3 boundary is
local-mathematical, not operational*, extending D2.5's verdict from the `m`
direction to the `rho` direction. No phase-transition narrative will be built
from a smooth curve, and no metric will be selected after the fact for showing
the sharpest change. Pre-specified metrics: chain `ARL_0`; reference MSE;
`FAP(100)`; `ACF1(e)`; delay `R_Delta` at `Delta = 1`.

## 9. Pre-committed confirmatory claims

Three, fixed now; everything else in `STATISTICAL_CONSEQUENCES.md` is labelled
exploratory. Each was suggested by the pilot and is being *confirmed*, not
discovered, at production size.

* **C1.** At `rho = 1`, chain `ARL_0` is materially below the `rho = 0` fresh
  control at the same `m`, for every `(D, m)`.
* **C2.** No pre-specified metric shows a localised rate feature at
  `rho/rho_c = 1` (§8).
* **C3.** The effective-multiplier identity `ACF1(e) = rho(1 - Gamma_eff)` with
  `Gamma_eff = -E_pi[e g(e)]/E_pi[e^2]` holds to Monte Carlo error, and
  `Gamma_eff` is far below `GammaTilde` whenever the reference dispersion
  exceeds the linearisation radius of `g`.

Multiplicity: three confirmatory claims, each read at 95%; no correction is
applied and none is needed for three pre-specified tests, but the count is
stated so that the exploratory results are not read at the same strength.

## 10. Linearisation radius

`r_lin(D, m)` is the largest `r > 0` such that
`|g_m(x)/x + GammaTilde_{D,m}| <= 0.10 * GammaTilde_{D,m}` for every grid
`0 < |x| <= r`. It is the radius inside which the P3 classification is the
correct description of the reference map, and it is reported next to the
measured reference dispersion in every cell.
