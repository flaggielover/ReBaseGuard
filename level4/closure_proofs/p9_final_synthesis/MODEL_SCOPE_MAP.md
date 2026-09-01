# Model-scope map — what is established where

Cells: `PROVED` · `CERTIFIED` · `EMPIRICAL` · `NEGATIVE` · `UNKNOWN` ·
`OUT_OF_SCOPE`.

**Blank/`UNKNOWN` cells are not extrapolated.** `UNKNOWN` means the repository
has no authoritative statement, not that the answer is presumed favourable.

**P8 is authoritatively `FAIL`.** Its surviving evidence is citable only as a
failed-campaign evidence set within its exact tested scope, so **it fills no
cell here**. Every non-Gaussian column is `UNKNOWN` except where P4's
location-family theorem or Stage-D's calibration already speaks. This is the
single largest honest gap in the project, and it is now known to be durable
rather than merely pending.

Three cells are *worse* than `UNKNOWN` after P8: detector transfer is **measured
absent**, P7-boundary transfer **fails literally**, and the cross-family
window-separability law is **rejected**. Those are marked `NEGATIVE`.

---

## 1. Distribution family × conclusion

| conclusion | Gaussian | non-Gaussian regular location families | heavy-tailed (`t5`,`t3`) | contaminated | Cauchy |
|---|---|---|---|---|---|
| derivative identity `F' = rho(1-Gamma)` | **PROVED** (`P1-T1`,`P2-T1`) | **PROVED**, conditional on (A1)–(A7) (`P4-T1`, priority is `PARTIAL`) | `UNKNOWN` — inside (A1)–(A7) only if the moment conditions hold; nine `t1p5` cells are frozen failures (`P4-F1`) | `UNKNOWN` | **NEGATIVE** — excluded, `E\|A_m\|` diverges already on `tau=1` (`P4-C1`) |
| `Gamma > 2` (local repulsion at `rho=1`) | **CERTIFIED** (`CORE-C1`, `CORE-C2`) | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | `OUT_OF_SCOPE` |
| `rho_c = 1/\|1-Gamma\|` | **PROVED** (`P3-T1`) | **PROVED** given `P4-T1`'s conditions | `UNKNOWN` | `UNKNOWN` | `OUT_OF_SCOPE` |
| raw-mean identity | **PROVED** (`P5-T1`) | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` |
| unique invariant law + uniform ergodicity | **PROVED** (`P5-T7`) | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` |
| operational degradation | **EMPIRICAL**, reproduced (`P7-E1`) | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` |
| `rho_c` is **not** an operational boundary | **PROVED** at `rho=0` (`P9-T2`); **NEGATIVE** empirically (`P7-R1`) | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` |
| ARL_0 calibration to `465.50394` | **CERTIFIED** by Stage D | Stage-D D3 supplies **CUSUM** thresholds for six families (`STAGE-D-PARTIAL`, frozen convention only) | as left | as left | `OUT_OF_SCOPE` |

## 2. Detector family

| conclusion | frozen two-sided CUSUM | frozen symmetric two-chart SR | EWMA / any third family |
|---|---|---|---|
| derivative theorem | **PROVED** (`P1-T1`) | **PROVED** (`P2-T1`) | `UNKNOWN` — no closed derivative theorem exists |
| `Gamma` interval certificate | **CERTIFIED** (`CORE-C1`) | **CERTIFIED** (`CORE-C2`) | `UNKNOWN` |
| exact witnesses | **CERTIFIED** (`P3-X1`) | **CERTIFIED** (`P3-X1`) | `UNKNOWN` |
| `P9-T2` separation | **PROVED** | **PROVED** | `UNKNOWN` |
| non-Gaussian threshold calibration | Stage-D D3, six families | **does not exist** — the frozen `A` is Gaussian-only | `OUT_OF_SCOPE` |
| detector transfer | — | — | **`NEGATIVE`** — measured **absent** by P8 (`P8-S4`), inside a `FAIL` campaign; previously only `UNKNOWN` (`PROJ-SCOPE`) |

The SR row is worth stating plainly: `A = 520.886133602749` is a **Gaussian-only**
threshold. Any SR result outside Gaussian innovations requires a new
calibration, which does not exist at the anchor commit.

## 3. Window `m` and reuse fraction `rho`

| conclusion | `m=1` | `m in {2,3,5}` | `m > 5` | `m in {10,20}` |
|---|---|---|---|---|
| derivative theorem | **PROVED** | **PROVED** | **PROVED** (theorem is for all `m>=1`) | **PROVED** |
| numerical `GammaTilde` | **EMPIRICAL** | **EMPIRICAL** | `UNKNOWN` | `UNKNOWN` |
| `rho_c` values | **EMPIRICAL** | **EMPIRICAL** | `UNKNOWN` | `UNKNOWN` |
| `m` monotonicity of RMS/ARL | — | **EMPIRICAL** (`P5-N4`) | `UNKNOWN` — no saturation observed, direction not a theorem | `UNKNOWN` |

The theorem holds for all `m >= 1`; only the *numbers* stop at `m = 5`.
`P5-N4` (the premise the P5 ledger confusingly labels `P9`) must not be
extrapolated past `m=5`, and it does not improve every metric — measured SNR
*increases* with `m`.

| conclusion | `rho = 0` | `0 < rho < rho_c` | `rho = rho_c` | `rho > rho_c` | `rho = 1` |
|---|---|---|---|---|---|
| local classification | **PROVED** attracting | **PROVED** attracting | **PROVED** boundary (1 cell `INCONCLUSIVE`, `P3-U1`) | **PROVED** repelling | **PROVED** repelling |
| stationary law exists | **PROVED** (`N(0,1/m)`) | **PROVED** (`P5-T7`) | **PROVED** | **PROVED** | **PROVED** |
| operational safety | **NEGATIVE** — degraded already (`P9-T2`) | **UNKNOWN**, and *not* safe by inference | `UNKNOWN` | **EMPIRICAL**: the measured ARL optimum sits here | **EMPIRICAL** worst (`P7-E1`) |

The bottom row is the operational headline and it reads oddly on purpose: the
measured ARL optimum sits `1.25x`–`4.1x` **above** `rho_c`, i.e. **inside the
locally repelling region** (P6 pre-design `X1`, from P5 premises `S11`/`S12`,
`EMPIRICAL_ONLY`). Local stability and operational quality do not merely fail to
coincide — over the measured grid they point in *opposite* directions.

## 4. Convention, initialization, horizon, policy

| axis | value | status |
|---|---|---|
| convention | A (`w=min(m,tau)`, random denominator) | **PROVED** / **EMPIRICAL** — the primary convention throughout |
| convention | B (fixed-`m` denominator) | `UNKNOWN` for most results; must be reported side by side, never merged |
| convention | Stage-A minimum-dwell | **NEGATIVE** for `m>1` — a different object (`P1` definition audit); D2.3/Track-1A remain failed |
| initialization | canonical `e_0 = 0` | **PROVED** / **EMPIRICAL** — all P7/P9 runs |
| initialization | finite-reference / stationary start | `UNKNOWN` — and materially different: cycle 1 is `~465`, stationary is `~48` |
| horizon | stationary | **PROVED** (`P5-T7`), **EMPIRICAL** (`P7`) |
| horizon | finite (few cycles) | **EMPIRICAL** and **convention-sensitive** (`P9-N1`, `X-08`); the transient is oscillatory over ~10 cycles |
| policy | fixed `rho` | **PROVED** (`P5-T7`), **EMPIRICAL** (`P7`) |
| policy | memoryless adaptive, `rho_max < 1` | **PROVED** well-posed (`P6-T6B`); effectiveness **EMPIRICAL** under `P6 = PARTIAL` |
| policy | detector-state-reading adaptive | **`OUT_OF_SCOPE`** — outside T6-B's hypothesis class entirely |
| data | simulation | all of the above |
| data | semi-real streams | **EMPIRICAL**, regime-scoped (P6); not production validation |
| data | production | **`UNKNOWN`** — never claimed |

## 5. Count

| status | cells |
|---|---:|
| `PROVED` | 28 |
| `CERTIFIED` | 6 |
| `EMPIRICAL` | 14 |
| `NEGATIVE` | 5 |
| `UNKNOWN` | **31** |
| `OUT_OF_SCOPE` | 5 |

`UNKNOWN` is the largest single category after `PROVED`. Most of it is one
question — behaviour outside the two frozen Gaussian specialisations — and that
question is P8's, unadjudicated at the anchor commit.
