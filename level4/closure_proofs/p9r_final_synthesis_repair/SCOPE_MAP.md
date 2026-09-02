# P9R model-scope map

Rebuilt from source. Allowed statuses: `PROVED`, `CONDITIONAL`, `CERTIFIED`,
`EMPIRICAL`, `NEGATIVE`, `UNKNOWN`, `OUT_OF_SCOPE`. Nothing that P8 or P8R
measured empirically is written as `PROVED`.

## 1. Dimensions of the scope

| dimension | values inside P9R scope | outside |
|---|---|---|
| detector | frozen two-sided CUSUM (`k=1/2, h=5`); frozen symmetric two-chart SR (`A=520.886133602749`, no headstart) | every other detector; adaptive or state-reading kernels |
| window `m` | `1, 2, 3, 5` for reproduction; **all** `m >= 1` for `P9R-T2a`/`T2b` (no `m` enters their proofs beyond `F ~ N(0,1/m)`) | — |
| innovation family | Gaussian `N(0,1)` | every non-Gaussian family |
| convention | convention A (no minimum dwell, `w=min(m,tau)`, denominator `w`) | convention B; the Stage-A minimum-dwell process for `m>1`; the Track-1B random-window convention |
| reuse fraction `rho` | `rho = 0` exactly (theorems); `rho in {0,1}` (reproduction) | `0 < rho < 1` beyond P7's own results |
| drift | in-control only (`Delta = 0`) | out-of-control delay; shift regimes |

## 2. Per-cell status

### The `rho = 0` core

| detector | `m` | claim | status |
|---|---|---|---|
| CUSUM | any `>= 1` | invariant law is exactly `N(0,1/m)`; `ARL_0 = E[A(e)]`; multiplier `0` | `PROVED` (`P9R-T2a`) |
| SR | any `>= 1` | same | `PROVED` (`P9R-T2a`) |
| CUSUM | any `>= 1` | `E[A(e)] < A(0)` strictly | `CONDITIONAL` on `ASM-DOM` (`P9R-T2b`) |
| SR | any `>= 1` | same | `CONDITIONAL` on `ASM-DOM` (`P9R-T2b`) |
| CUSUM, SR | `1,2,3,5` | the mixture is far below `A(0)` numerically | `EMPIRICAL` (`P9R-E3`; deficits `311–390` cycles) |
| CUSUM, SR | any | `A` even; `sup A < inf`; `A(0)>1`; `A(e)->1` | `PROVED` (`L1`-`L4`) |
| CUSUM, SR | any | `A` globally non-increasing in `\|e\|` | `UNKNOWN` — empirically supported, not proved |

### Operational behaviour

| detector | `m` | `rho` | quantity | status |
|---|---|---|---|---|
| CUSUM | `1,2,3,5` | `0` | ARL `83.70–164.07` | `EMPIRICAL` (`MC_CONSISTENT` with P7) |
| CUSUM | `1,2,3,5` | `1` | ARL `50.11–80.55` | `EMPIRICAL` |
| SR | `1,2,3,5` | `0` | ARL `79.18–155.42` | `EMPIRICAL` |
| SR | `1,2,3,5` | `1` | ARL `48.31–77.68` | `EMPIRICAL` |
| both | `1,2,3,5` | `1` | cycle-2 collapse to `5.8–9.4` | `EMPIRICAL` |
| both | `1,2,3,5` | — | `rho < rho_c` guarantees nominal-ARL preservation | `NEGATIVE` (`P9R-T3`, `P7-R1`) |
| both | `1,2,3,5` | — | `rho_c = 1/\|1-Gamma\|` as a *local deterministic* boundary | `PROVED` (`P3-T1`) |
| both | `1,2,3,5` | — | Gaussian `rho_c` numerical values | `EMPIRICAL` (`P3-N1`: exact formula, Monte Carlo gains) |
| SR | `1` | — | `Gamma_SR in [5.800391799508442, 28.781285803081492]` | `CERTIFIED` (`P2-C1`, Arb) |
| both | witness rows | — | exact rational `rho_c` witnesses | `CERTIFIED` (`P3-X1`; **not** formally verified) |

### Model-class generalisation

| dimension | status | source |
|---|---|---|
| non-Gaussian innovation families | `UNKNOWN` for every P9R theorem | none of `L1`-`L4`, `T2a`, `T2b` is claimed beyond Gaussian |
| general location families | `CONDITIONAL` under (A1)-(A7), at P4's `PARTIAL` strength | `P4-T1` |
| cross-family window law | `NEGATIVE` | `P8-F1`, `P8R-F1` |
| detector transfer | `NEGATIVE` (measured absent) | `P8-F1`, `P8R-F1` |
| P8R magnitude gate `S15` | `EMPIRICAL` only, adjudicated statistically fragile | `P8R-S15` |
| Level-4 global closure | `UNKNOWN` (`D-09` open) | `GLOBAL-CLOSURE` |
| novelty | `UNKNOWN` — `NOT_ESTABLISHED` | `P9R-N1` |

### Out of scope for P9R

Convention B, the Stage-A minimum-dwell process, Track-1B random windows,
out-of-control delay, adaptive/state-reading kernels, P6's policy kernel, and
production validation are `OUT_OF_SCOPE`. None of them appears in a P9R claim.

## 3. What must not be read out of this table

* `P9R-T2a` holds for **all** `m >= 1`, but only for the two frozen Gaussian
  detectors under convention A. It is not a general theorem about re-baselining.
* The `EMPIRICAL` rows are Monte Carlo at the stated `n_rep`; they are
  consistent with P7, not identical to it.
* `CERTIFIED` never means `PROVED` and never means `FORMALLY_VERIFIED`.
* A `CLOSED` priority status does not add a row to this table.
