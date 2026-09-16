# R2 repair successor: qualification result

**Run.**
- The protocol, gates, feasibility criterion, registries and bound code were frozen in `a1dcf1e8` (fast-forward on
  `p5y-postk1-frontier` over `84aaa6a5`).
- All 93 parts ran afterwards on `rebaseguard-vultr-02` (venv `/root/work/rbg-cusum-aux5-venv`), each in a fresh
  process, from a clean checkout of exactly `a1dcf1e8`. `RUN_PROVENANCE.json` records 0 porcelain lines and no DEV
  override. There were 0 runner failures.
- `qualify_r2.py check` passed on the host and again locally (`problems: []`). It re-verifies the R2 bound code, all
  87 R1 files byte-for-byte, the protocol hash and every part hash, and recomputes all verdicts.

`QUALIFICATION_RESULT_R2.json` sha256 is `cbb24407e6496538…`; protocol sha256 is `4960e7eb7da8ed8a…`.

## R1 retained, R05 repaired

| | Verdict |
|---|---|
| G01–G16 | **16/16 PASS** |
| QS manufactured soundness (25 fixtures incl. T25) | PASS: 0 violations |
| QC residual consistency | PASS |
| **QM mutation sensitivity** | **21/21**. R05 is now detected by **T25**; the 20 other mutations are detected by their R1 trials |
| **R05 isolating fixture** | **PASS**: fixture 0 violations unmutated vs **5** for R05; `ABL_ZERO_OFFSET` 0 / 0; `ABL_RESOLVE_CLOSED` 0 / 0 (all six frozen invariants) |
| QR reference-kernel differential | PASS (15/15) |
| QX independent cross-check | PASS |
| QO real-operator integration (synthetic) | PASS |
| QP R1-producer precision | STAGNATING: the whole-cell width floor is mathematical, and the exact-candidate midpoint and constant-R''' fixtures contract, as in R1 |

## Graded method (selected)

| | Verdict |
|---|---|
| QG1 soundness, 16 σ-fixtures, both modes | PASS: 0 violations of every (e, o, t) node bound at e0 and 17 grid points, and of the export |
| QG2 graded never looser than scalar | PASS (every node component and radius) |
| QG3 graded mutation sensitivity | PASS: **11/11** (all required, fixed from the seed-disjoint DEV run) |
| QG4 real CUSUM Arb kernels at e = 0, synthetic polynomials | PASS: 272/272 operator-parity checks `K_i(f∘σ)(x) = (−1)^i K_i(f)(σx)`, and the graded residual ranges dominate float quadrature |
| QG5 graded determinism | PASS |
| QG6 graded fail-closed (10 controls, including real front-end refusals and empty pinned registries) | PASS |

**Conditioning on manufactured stress fixtures** (certified exact `C_e0`, `C_o0`; m = 1 radius; scalar = the R1
generic enclosure on the same inputs):

| fixture | C_e0 / C_o0 | scalar mid → graded mid | scalar cell → graded cell | category (mid / cell) |
|---|---|---|---|---|
| S02 CUSUM cell-0 analogue, noise 10⁻⁶ | 1232 / 3.33 | 6.61·10⁶ → 22.8 (×2.9·10⁵) | 6.28·10⁹ → 3.21·10⁴ (×1.95·10⁵) | ORDERS / ORDERS |
| S03 same, noise 10⁻⁹ | 1232 / 3.33 | 2.29·10³ → 0.0131 (×1.7·10⁵) | 6.42·10⁹ → 3.70·10⁴ (×1.7·10⁵) | ORDERS / ORDERS |
| S13 C = 100, odd 1.98 | 99.9 / 1.98 | 0.773 → 2.4·10⁻³ (×325) | 2.96·10⁵ → 653 (×453) | MATERIAL / MATERIAL |
| S01 C = 4 | 4.0 / 2.1 | ×3.3 | ×3.1 | MODEST / MODEST |

Method 3, residual correction (emulated by 10× smaller candidate error), only divides the scalar radius by 10. The C⁴
structure stays.

**Graded precision.** S02 and S03 are STAGNATING at 128–512 bits: the radii are identical, set by a mathematical floor.
There is no sign flip and no instability.

## Cell 0 (committed magnitudes only; no R''' value)

**Autopsy.** The scalar mode reproduces the committed `eps_mid` of F:0, D:0 and H:0 exactly.
- `ε_F = 4.55·10⁻³`, `ε_D = 4.57`, `ε_H = 9.00·10³`, `ε_G ≥ 2.66·10⁷`.
- Each level is ≥ 97.9 % the propagated lower level: `C⁴·6k₁³·δ_F` with `δ_F = 3.69·10⁻⁶`.

**Forecast.** Binding row: `C_e0` = certified `C_upper`; `C_o0` = **non-certified** float estimate 4.68; G-residual
factor 1. The factors 10 and 100 give 3.45·10³ and 3.47·10³, so this assumption is not load-bearing.

| m = 1 | R1 | R2 | contraction | category |
|---|---:|---:|---:|---|
| midpoint `R'''(e0)` | 2.66·10⁷ | **3.45·10³** | 7.7·10³ | ORDERS_OF_MAGNITUDE_IMPROVEMENT |
| whole cell 0 | 2.27·10⁹ | **2.80·10⁵** | 8.1·10³ | ORDERS_OF_MAGNITUDE_IMPROVEMENT |
| point `R'''(0)`, conservative proxy | — | 1.91·10⁵ | — | — |

Sweep over `C_o0`:

| `C_o0` | midpoint radius | category |
|---|---:|---|
| 10 | 8.8·10³ | ORDERS |
| 50 | 1.1·10⁵ | MATERIAL |
| 466 | 8.5·10⁶ | MODEST |
| `C_upper` | 2.66·10⁷ | NO |

Further levers (not selected): a certified even bound of 466 would give a midpoint radius of 449 (cell 3.2·10⁴); a
Perron-deflated even component (hypothetical 11.2) would give 0.26 (cell 17).

## Verdict

Frozen rule (`PRE_RESULT_GATES_R2.json`):
- QUALIFIED_FOR_GOVERNED_REAL_CELL_QUALIFICATION needs a registered certified `C_o0` and the graded real wiring.
- Both are absent. The operator-certificate registry is frozen empty, and `certify_real_cell_r2` refuses with
  `GRADED_REAL_WIRING_NOT_BUILT`.
- All gates and questions pass, so the rule gives **PARTIALLY_QUALIFIED**.

Next-step rule: the cell-0 midpoint forecast is ORDERS_OF_MAGNITUDE_IMPROVEMENT at the float estimate, but a
certified input and the real wiring are missing, so the next step is **REPAIR_CELL0_CONDITIONING_AGAIN**.

No real-cell qualification proposal is prepared, because R2 is not QUALIFIED.

```text
R1_PRESERVED                        = YES   (87 files byte-identical; e69a0224 / 4a1b20a8 untouched)
R05_ISOLATING_FIXTURE               = PASS
QM                                  = 21/21
CELL0_R1_RADIUS_FORECAST            = midpoint >= 2.66e7, whole cell 2.27e9 (m = 1)
CELL0_R2_RADIUS_FORECAST            = midpoint 3.45e3, whole cell 2.80e5 (m = 1; C_o0 = non-certified 4.68)
CONTRACTION_FACTOR                  = 7.7e3 midpoint, 8.1e3 whole cell (ORDERS_OF_MAGNITUDE_IMPROVEMENT, conditional on certified C_o0 <= ~5)
PRIMARY_R1_WIDTH_SOURCE             = resolvent conditioning compounded by dependency inflation (parity-blind global C at all four levels)
SELECTED_R2_NUMERICAL_METHOD        = sigma-graded parity-block certified error propagation with Neumann parity perturbation over the cell
E0_PARITY_REDUCTION                 = USED
POINT_R3_AT_ZERO_CERTIFICATION      = POSSIBLE
WHOLE_CELL_FIRST_CELL_CERTIFICATION = NOT_DEMONSTRATED
PRECISION_BEHAVIOR                  = STAGNATING
REAL_ORDER3_PRODUCER_R2             = PARTIALLY_QUALIFIED
B1_NO_CERTIFIED_ORDER3_PRODUCER     = OPEN
REAL_CELL_QUALIFICATION             = NOT_AUTHORIZED
SCIENTIFIC_K5_PROBE_RUN             = NO
NEXT_STEP                           = REPAIR_CELL0_CONDITIONING_AGAIN
```
