# P5Y K1 final-completion — status

    OVERALL                = K1_INCOMPLETE_IMPLEMENTATION
    P5Y_PRODUCTION_ALLOWED = NO        production_launched = false
    COST_CAP               = NOT_ESTABLISHED     cap 1126 CPU-h (unchanged)
    K1 = CLOSED            NOT claimed; reserved for independent adjudication

--------------------------------------------------------------------------
## Status table

### CUSUM

| item | state |
|---|---|
| compact cover | **NOT CERTIFIED** — 7 of 16 certified cells fail |
| M_R2 | implemented; sharpened (up to 37x tighter at high drift) |
| all-m assembly | implemented, unchanged, verified |
| far field | **NOT_ESTABLISHED at the frozen splice**; PASS at `e_far = 12` |
| **cell 325** | **CERTIFIED_PASS** (worst utilization 22.7% of .050) |

### SR

| item | state |
|---|---|
| raw DAG | **ABSENT** |
| compact cover | not attempted (blocked by the DAG) |
| M_R2 | **ABSENT** |
| all-m | **ABSENT** |
| far field | **NOT_ESTABLISHED at the frozen splice**; PASS at `e_far = 12` |

### Governance

| item | state |
|---|---|
| producer binding | PASS (Repair2, byte-preserved) |
| source-certificate binding | PASS (Repair2, byte-preserved) |
| resume universe | 17,978 unchanged; shards exact at 1/8/16/32/64 |
| precision | 256 bits, unchanged, no escalation |
| Taylor degree | unchanged |
| budgets / thresholds | unchanged | cover geometry unchanged |
| cap | 1126 CPU-h, not increased |
| production | OFF |

--------------------------------------------------------------------------
## Cell 325: CERTIFIED_PASS

The one task with a clean positive outcome. Drift-aware operator norms
(`sharp_norms.py`) replaced the whole-line moments with exact integrals over the
actual shifted window. At cell 325 that tightened the raw-kernel norms 13-29x:

```text
j_0  11.798 -> 0.406     j_1  10.777 -> 0.559
j_2  13.380 -> 0.777     j_3  21.963 -> 1.624
```

and hence `M_R2`:

```text
m    M_R2 before   M_R2 after   factor   cover util before -> after
1      1.842         1.240       1.5x      23.6%  ->  18.0%   PASS
2     14.057         1.505       9.3x     133.6%  ->  17.2%   FAIL -> PASS
3     29.874         1.745      17.1x     280.3%  ->  19.6%   FAIL -> PASS
5     77.437         2.086      37.1x     721.0%  ->  22.7%   FAIL -> PASS
```

Every enclosure is identical or strictly tighter than the reviewed run; none
loosened. Provenance chain 28/28, S0 charged exactly once, 0 duplicate edges.

--------------------------------------------------------------------------
## The finding this surfaced: cell 325 was not the binding constraint

Certifying 16 cells shows the real constraint is the block of largest-radius
cells, and **cell 325 is not in it** (its radius is 0.096; cells 318-324 run to
0.156).

| cell | rho | C | util % (m=1,2,3,5) | status |
|---:|---|---|---|---|
| 0 | 0.000254 | 1232.8 | 11.1, 12.7, 12.0, 11.0 | PASS x4 |
| 50 | 0.000319 | 981.4 | 12.1, 12.8, 11.9, 10.7 | PASS x4 |
| 136 | 0.000551 | 568.7 | 11.7, 10.6, 9.5, 8.2 | PASS x4 |
| 150 | 0.000621 | 505.0 | 10.7, 9.5, 8.4, 7.3 | PASS x4 |
| 221 | 0.001506 | 208.1 | 2.3, 2.6, 2.9, 3.0 | PASS x4 |
| 293 | 0.018019 | 17.39 | 24.2, 24.1, 23.3, 22.1 | PASS x4 |
| 300 | 0.028413 | 11.03 | 32.7, 30.6, 28.8, 27.3 | PASS x4 |
| 310 | 0.058938 | 5.316 | 46.6, 42.8, 46.6, 64.2 | PASS x4 |
| **318** | 0.10732 | 2.920 | 79.1, 85.0, **104.8**, **182.6** | FAIL m=3,5 |
| **319** | 0.12280 | 2.552 | 86.1, 99.9, **124.6**, **218.4** | FAIL m=3,5 |
| **320** | 0.13650 | 2.295 | 75.3, **102.9**, **140.4**, **239.7** | FAIL m=2,3,5 |
| **321** | 0.14657 | 2.138 | 86.2, **110.9**, **155.3**, **245.1** | FAIL m=2,3,5 |
| **322** | 0.15250 | 2.055 | **104.0**, **114.9**, **149.8**, **218.9** | FAIL x4 |
| **323** | 0.15525 | 2.018 | **105.5**, **108.9**, **134.6**, **181.4** | FAIL x4 |
| **324** | 0.15627 | 2.005 | 88.2, 92.2, **108.8**, **135.4** | FAIL m=3,5 |
| 325 | 0.096242 | 2.001 | 18.0, 17.2, 19.6, 22.7 | PASS x4 |

**Classification: CERTIFICATE_TOO_LOOSE, for every failure.** At each failing
cell the curvature enclosure straddles zero and is near-symmetric about it, so
its magnitude is certificate radius and it demonstrates nothing about the true
`R''`:

```text
cell 318 m=5  R2 = [-15.14, +15.03]  centre/halfwidth = 0.0034
cell 320 m=5  R2 = [-12.59, +12.27]  centre/halfwidth = 0.0127
cell 324 m=5  R2 = [ -4.46,  +4.75]  centre/halfwidth = 0.0325
```

This is **not** a scientific counterexample and is not reported as one. The
remaining looseness is the order-2 source/finite-power chain, which still uses
the plain mean-value envelope; the Taylor-in-`e` refinement was applied only to
the resolvent chain (F, D, H) and would need order-3 jets to extend.

--------------------------------------------------------------------------
## Far field (P5X-T3), both detectors

Derivation in `far_field.py`: `E[raw_1] = 0` and `Rbar = raw_1` exactly on
`{tau = 1}`, so `R = E[(Rbar - raw_1) 1{tau>1}]`; Cauchy-Schwarz with the
pathwise `E[Rbar^2] <= m` gives the decreasing majorant

```text
|R_(D,m)(e)|  <=  B(e) = sqrt(2m+2) * sqrt(Phi(c_D - e))
```

| | CUSUM (`c_D = 5.5`) | SR (`c_D = 6.7555`) |
|---|---|---|
| at `e_0 = c_D` | m=1,2 PASS; m=3 marginal; **m=5 FAIL** | m=1,2 PASS; **m=3,5 FAIL** |
| at `e_0 = 12` | **PASS all m** (B ≈ 1.3e-5) | **PASS all m** (B ≈ 5.6e-4) |
| closes all m from | `e_0 >= 5.9307` | `e_0 >= 7.1863` |
| uncovered | **(5.5, 5.9307]** | **(6.7555, 7.1863]** |

```text
CUSUM_FAR_FIELD = NOT_ESTABLISHED at the frozen K1 splice   (PASS at e_far = 12)
SR_FAR_FIELD    = NOT_ESTABLISHED at the frozen K1 splice   (PASS at e_far = 12)
failure class   = CERTIFICATE_TOO_LOOSE
```

### A governance conflict worth the adjudicator's attention

P5X `FROZEN_SCOPE.md` section 3 fixes the certified compact cover as
`[0, e_far]` with **`e_far = 12`**, and leaves `[e_far, infinity)` to P5X-T3.
The frozen K1 cover instead ends at `c_D` — and the provenance confirms the
truncation: the parent records the CUSUM cover as *"334 over [0,12], 323 over
[0, e_star] = [0, 5.5]"*.

So `[0, c_D]` plus P5X-T3 does not compose to the real line for m=3,5 under this
majorant. Closing it needs either a sharper far-field majorant or cover cells
beyond `c_D` — and extending the cover would change frozen cover geometry, which
this campaign may not do. Reported, not worked around.

--------------------------------------------------------------------------
## SR: ABSENT

```text
SR_IMPLEMENTATION = ABSENT     SR_M_R2 = ABSENT     SR_ALL_M = ABSENT
failure class     = IMPLEMENTATION_INCOMPLETE   (not a scientific failure)
```

Measured evidence, not assertion. Task1R certifies, with a PASS verdict:

```text
object    F_0 only        (1 of 19 required object classes)
patch     (17, 11)        (1 of 3,994 live patches)
drift     e = 1/4         (1 of 316 frozen cells)
cost      12.72 CPU-s, 48.6 MiB peak
```

Missing: `h_1..h_4`, `S_1..S_4`, `F_1..F_4`, `dF_0..dF_4`, the entire order-2
chain and finite powers, whole-cell uniform-in-`e` envelopes (without which no
`M_R2` exists), the all-m assembly, and generalisation to all patches and all
drifts. **8,849 of 17,978 obligations (49.2%) are undischarged.**

The validated CUSUM path is hard-wired to the CUSUM state square and a recentred
Hermite expansion; SR is a softplus/Taylor-model formulation on two charts with
panel Gaussian moments. They share the Arb backend and the frozen error algebra
and little else — which is why the frozen CHECKPOINT lists `complete_SR_raw_DAG`
first among its implementation dependencies.

--------------------------------------------------------------------------
## Cost / memory

Model anchored on the frozen optimized-backend primitives; it reproduces the
frozen `base_raw_sr_cpu_h = 380.1558` exactly, so it is the frozen model.

```text
MEASURED (this host, 8 vCPU / 30.8 GiB)
  CUSUM complete            103.0 CPU-h central, 128.6 conservative
  per cell                  ~947 CPU-s        peak RSS 202 MiB/worker
  safe worker count         8                 RSS at 8 workers ~1.6 GiB

STRUCTURAL (from the frozen obligation list)
  certified function objects per cell: 19 base + 22 bundle + 21 curvature = 62
  complete/base = 3.26x     (CUSUM measured independently: 3.33x)

EXTRAPOLATION (SR is unimplemented; NOT a cost result)
  SR complete               1234.1 CPU-h central, 1577.3 conservative
  campaign                  1337.1 central, 1680.3 conservative   > 1126

LOWER BOUNDS
  assumption-free (SR base objects only)    435.8 CPU-h   does NOT exceed cap
  assumption-dependent (complete set)      1188.9 CPU-h   exceeds cap
```

```text
COST_CAP_STATUS = NOT_ESTABLISHED
```

COST_CAP_FAIL is **not** claimed: the assumption-free lower bound does not
exceed the cap. COST_CAP_PASS is not claimed either: both the complete
extrapolation and the assumption-dependent lower bound do exceed it. The
assumption — that order-1/2 objects cost comparably per function to order-0 —
is plausible (71% of the measured panel cost is the per-function Taylor
contraction) but unproved for an implementation that does not exist.

Wall-time note: the historical 64-worker projections do **not** apply. This host
has 8 cores; at 8 workers the extrapolated campaign is ~167 h wall.

--------------------------------------------------------------------------
## Production gate (Phase 7)

```text
1 implementation complete .................. NO   (SR absent)
2 no implementation defect ................. yes
3 cell 325 certified ....................... YES
3b all re-certified CUSUM cells pass ....... NO   (318-324)
4 CUSUM far field PASS ..................... NO   (at the frozen splice)
5 SR far field PASS ........................ NO   (at the frozen splice)
6 SR representative certificates PASS ...... NO   (nothing to certify)
7 provenance / resume PASS ................. yes
8 within the 1126 CPU-h cap ................ NOT_ESTABLISHED
9 memory safe on host ...................... yes
```

Five conditions fail, so `P5Y_PRODUCTION_ALLOWED = NO`. Production was not
enabled and not launched. Phase 8 was not entered.

--------------------------------------------------------------------------
## Unresolved blockers

```text
1  SR raw DAG absent (8,849 / 17,978 obligations)
2  SR M_R2 absent
3  SR all-m assembly absent
4  CUSUM cells 318-324 fail: CERTIFICATE_TOO_LOOSE, order-2 chain envelope
5  far field does not close m=3,5 at the frozen K1 splice, both detectors;
   the frozen K1 cover ends at c_D while P5X FROZEN_SCOPE requires e_far = 12
6  cost cap NOT_ESTABLISHED
```

Recommended next work, in order of value: extend the Taylor-in-`e` refinement to
the order-2 source/finite-power chain (would likely clear 318-324, as it cleared
325); sharpen the far-field majorant or obtain governance for cover cells beyond
`c_D`; then the SR raw DAG, which is the dominant remaining effort.
