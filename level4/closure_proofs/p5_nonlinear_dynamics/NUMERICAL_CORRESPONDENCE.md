# P5 numerical correspondence

What P5 must agree with, and by how much it does. Every number here is produced
by a script in `experiments/` and stored in `results/`.

## 1. Semantic correspondence with the frozen chain — EXACT

`tests/test_correspondence.py` compares the P5 raw-mean chain against the frozen
`rebaseguard_p7.chain.simulate_chain` (which is itself bit-identical to
`level4/stage_d/src/chain.py` for CUSUM) under an identical RNG stream.

| check | configurations | result |
|---|---|---|
| `tau` arrays identical | `{cusum,sr} x m in {1,3,5} x rho in {0.5,1}`, 200 replicates x 60 cycles | **bit-identical, 12/12** |
| `e_start` agreement | same | `max abs difference = 8.9e-16` (a few ULP of a reordered floating-point sum) |
| `Rbar == e + zbar_m` path-by-path on the frozen `p7.cycles` object | `{cusum,sr} x e in {0, 0.4, -1.3}`, `m in {1,2,3,5}`, 4000 paths | `max abs difference < 1e-12`, `tau` identical |
| truncated-denominator convention (`tau=1` gives the same `Rbar` for every `m`) | both detectors | holds to `1e-12` |

## 2. The slope at the origin vs the frozen P1/P2/P3 gain — 0.14%–1.6%

P5's `R'(0)` is estimated from the map grid only (a five-point fit on
`e in {0, +/-0.005, +/-0.01}`); P3's `1 - GammaTilde` is read from the CLOSED
`m_rho_stability_priority3/results/boundary_table.json` and never recomputed.

| det | m | P5 `R'(0)` | P3 `1 - GammaTilde` | rel. err | P5 `1/|R'(0)|` | P3 `rho_c` |
|---|---|---|---|---|---|---|
| CUSUM | 1 | -14.937 | -14.917 | 0.14% | 0.0670 | 0.0670 |
| CUSUM | 2 | -12.203 | -12.265 | 0.51% | 0.0819 | 0.0815 |
| CUSUM | 3 | -10.875 | -10.957 | 0.75% | 0.0920 | 0.0913 |
| CUSUM | 5 |  -9.120 |  -9.226 | 1.15% | 0.1096 | 0.1084 |
| SR | 1 | -16.266 | -16.454 | 1.14% | 0.0615 | 0.0608 |
| SR | 2 | -13.336 | -13.501 | 1.22% | 0.0750 | 0.0741 |
| SR | 3 | -11.786 | -11.973 | 1.56% | 0.0848 | 0.0835 |
| SR | 5 |  -9.902 | -10.049 | 1.46% | 0.1010 | 0.0995 |

The residual is systematic (P5 slightly under-estimates `|R'(0)|` in every
cell) and is a finite-difference bias: `R` is concave towards the origin, so a
five-point fit over `|e| <= 0.01` sits marginally below the tangent. The
independent seed family reproduces the same values (`0.0001`–`1.1%` deviation
from P3), so it is not a seed effect. It is logged in `ADVERSARIAL_REVIEW.md`
A3 and is immaterial: it shifts `rho_c` by at most `0.0012`, far below the
`rho`-grid resolution, and none of T8–T11 depends on the exact value.

## 3. The in-control ARL and response function vs P7 — <0.2%

| quantity | P5 | frozen reference |
|---|---|---|
| `A(0)` CUSUM | 465.2 | 465 (P7 nominal single-cycle ARL) |
| `A(0)` SR | 464.4 | ~465 (ARL-matched calibration, `A = 520.886133602749`) |
| `sup_e A(e)` | attained at `e = 0` in both detectors | consistent with T3 symmetry |
| `r_lin` (10% departure from the tangent) | `~0.05` for every `(D,m)` | P7's grid-defined `r_lin = 0.05` |

## 4. P7's `ACF1 = rho(1 - Gamma_eff)` — identified, not merely fitted

T11 makes this an identity with `Gamma_eff = 1 + E_pi[e^2 s(e)]/E_pi[e^2]`. P5
tests it *across campaigns*: `s` comes from the **map** experiment, `pi` from the
**chain** experiment, and the prediction is compared against the chain's directly
measured `ACF1`. See `results/chain_analysis.json` (`t11`) and
`STATIONARY_DYNAMICS.md` §3.

The comparison of `Gamma_eff` with the tangent gain `GammaTilde` reproduces
P7's reported 5x–25x overshoot of `lambda` over the measured `ACF1`, now with a
mechanism rather than an observation.

## 5. Theorem constants vs measured quantities

| constant | rigorous bound used in the proof | measured value |
|---|---|---|
| `C_CUSUM = sup_e E[tau|e]` | `10/Phi(-1)^10 = 9.8959e8` | `465.2` |
| `C_SR = sup_e E[tau|e]` | `1/Phi(-(log A + 1/2)) = 1.4054e11` | `464.4` |
| `sup_e E[e_{j+1}^2|e]` | `rho^2 C_D + (1-rho)^2/m` | `<= 4.04` (`= S(0)` at `rho=1`) |
| Doeblin `delta'` | positive but astronomically small | measured mixing: IACT of 1–3 cycles |

The proofs are correct with the rigorous constants and vacuous-in-practice as
rate statements; the measured constants are reported separately and are *not*
used inside any proof. Substituting the measured `sup_e A(e)` converts T5/T7
into CONDITIONAL THEOREMS with realistic constants — that substitution is
offered in `LIMITATIONS.md` §3 and is not claimed as proved.

## 6. Independent seed-family replication

The entire map experiment was re-run under seed family `20261119` (primary:
`20260501`). Over 392 paired `(detector, m, e)` cells:

```
mean z = +0.016 ,  sd z = 1.044 ,  max |z| = 3.12 ,
fraction |z| > 2 = 5.6% (nominal 4.6%) ,  |z| > 3 = 1.0% (nominal 0.27%) .
```

Derived quantities agree far more tightly than their inputs: `e*(rho=1)` to
4 decimal places, the 2-cycle multiplier to `<0.006`, `SNR` to 3 decimals, in
all 8 cells.

## 7. Protected-tree integrity

`results/protected_hashes_before.txt` / `protected_hashes_after.txt`:
SHA-256 of all 294 files under `m_gt_1_priority1`, `sr_derivative_priority2`,
`m_rho_stability_priority3`, `p4_theory_generalization`,
`p7_statistical_consequences`, `stage_d` and `level4/src`. Verified byte-identical
before and after the campaign (`tests/test_protected_tree.py`).
