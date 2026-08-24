# D4 phase-map closure — final report

## A. D4 verdict

`D4-PHASE-MAP-CLOSED`

## B. Exact derivative formula used

`F'_{rho,m}(0) = rho(1-GammaTilde_m)`

## C. Exact Gamma definition

`GammaTilde_m = E_0[A_m T_tau], A_m=(1/min(m,tau))*sum_{r<min(m,tau)} Z_{tau-r}`

## D. Gamma table

| m | GammaTilde_m | SE | 95% CI | C_m | P(tau<m) |
|---:|---:|---:|---:|---:|---:|
| 1 | 15.846431 | 0.034288 | [15.779227, 15.913635] | 0.000000 | 0.000000 |
| 2 | 13.230470 | 0.030026 | [13.171619, 13.289320] | 0.000000 | 0.000000 |
| 5 | 10.171536 | 0.022229 | [10.127968, 10.215104] | 0.002706 | 0.000699 |
| 10 | 7.079662 | 0.013621 | [7.052965, 7.106359] | 0.023078 | 0.007496 |
| 20 | 4.244327 | 0.007867 | [4.228908, 4.259747] | 0.078725 | 0.027922 |
| 35 | 2.885820 | 0.005100 | [2.875825, 2.895814] | 0.148534 | 0.058972 |
| 50 | 2.356567 | 0.003906 | [2.348913, 2.364222] | 0.202767 | 0.089230 |
| 60 | 2.157178 | 0.003553 | [2.150214, 2.164142] | 0.233234 | 0.108566 |
| 65 | 2.081690 | 0.003339 | [2.075145, 2.088235] | 0.247192 | 0.118286 |
| 70 | 2.016702 | 0.003227 | [2.010379, 2.023026] | 0.260452 | 0.127834 |
| 72 | 1.993263 | 0.003158 | [1.987074, 1.999452] | 0.265576 | 0.131559 |
| 75 | 1.960645 | 0.003106 | [1.954557, 1.966733] | 0.273092 | 0.137314 |
| 80 | 1.912931 | 0.002993 | [1.907066, 1.918797] | 0.285185 | 0.146630 |
| 90 | 1.834449 | 0.002863 | [1.828838, 1.840061] | 0.307970 | 0.165119 |
| 100 | 1.774206 | 0.002727 | [1.768861, 1.779550] | 0.329149 | 0.183179 |
| 150 | 1.600817 | 0.002284 | [1.596340, 1.605293] | 0.417955 | 0.267831 |
| 250 | 1.481870 | 0.002025 | [1.477901, 1.485840] | 0.548145 | 0.410783 |

## E. rho_c table

| m | Gamma regime | rho_c | SE | 95% CI | accessible in [0,1]? |
|---:|---|---:|---:|---:|---|
| 1 | GAMMA_GT_2 | 0.067356 | 0.000156 | [0.067053, 0.067663] | yes |
| 2 | GAMMA_GT_2 | 0.081763 | 0.000201 | [0.081371, 0.082158] | yes |
| 5 | GAMMA_GT_2 | 0.109033 | 0.000264 | [0.108517, 0.109553] | yes |
| 10 | GAMMA_GT_2 | 0.164483 | 0.000369 | [0.163764, 0.165208] | yes |
| 20 | GAMMA_GT_2 | 0.308230 | 0.000747 | [0.306772, 0.309702] | yes |
| 35 | GAMMA_GT_2 | 0.530273 | 0.001434 | [0.527478, 0.533099] | yes |
| 50 | GAMMA_GT_2 | 0.737155 | 0.002122 | [0.733019, 0.741338] | yes |
| 60 | GAMMA_GT_2 | 0.864171 | 0.002653 | [0.859002, 0.869404] | yes |
| 65 | GAMMA_GT_2 | 0.924479 | 0.002854 | [0.918919, 0.930107] | yes |
| 70 | GAMMA_GT_2 | 0.983572 | 0.003121 | [0.977492, 0.989728] | yes |
| 72 | ONE_LT_GAMMA_LT_2 | 1.006783 | 0.003201 | [1.000548, 1.013095] | no |
| 75 | ONE_LT_GAMMA_LT_2 | 1.040967 | 0.003366 | [1.034411, 1.047606] | no |
| 80 | ONE_LT_GAMMA_LT_2 | 1.095372 | 0.003591 | [1.088379, 1.102456] | no |
| 90 | ONE_LT_GAMMA_LT_2 | 1.198395 | 0.004112 | [1.190390, 1.206509] | no |
| 100 | ONE_LT_GAMMA_LT_2 | 1.291646 | 0.004549 | [1.282791, 1.300625] | no |
| 150 | ONE_LT_GAMMA_LT_2 | 1.664400 | 0.006327 | [1.652091, 1.676895] | no |
| 250 | ONE_LT_GAMMA_LT_2 | 2.075247 | 0.008722 | [2.058292, 2.092483] | no |

## F. Gamma=2 / rho_c=1 crossing

Bracket `[70, 72]`; frozen log-linear estimate
`71.419386`.

## G. Direct-map correspondence

| Cell | m | rho | theorem lambda | direct derivative | SE | abs z | relative gap | result |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| V1 | 1 | 0.20 | -2.969286 | -2.914392 | 0.068411 | 0.798 | 1.85% | PASS |
| V2 | 20 | 0.20 | -0.648865 | -0.654774 | 0.017564 | 0.335 | 0.91% | PASS |
| V3 | 20 | 0.40 | -1.297731 | -1.262012 | 0.038644 | 0.921 | 2.75% | PASS |
| V4 | 50 | 0.70 | -0.949597 | -0.992447 | 0.038677 | 1.105 | 4.51% | PASS |
| V5 | 50 | 0.80 | -1.085254 | -1.054968 | 0.043666 | 0.692 | 2.79% | PASS |
| V6 | 100 | 1.00 | -0.774206 | -0.793719 | 0.040803 | 0.477 | 2.52% | PASS |

Result: 6/6 frozen cells passed.

## H. Operational overlay

| m | rho | theorem class | lambda | cycle ARL | reference MSE | e ACF1 | direction ACF1 |
|---:|---:|---|---:|---:|---:|---:|---:|
| 20 | 0.20 | LOCALLY-STABLE | -0.6489 | 279.78 | 0.0393 | -0.240 | -0.295 |
| 20 | 0.40 | LOCALLY-UNSTABLE | -1.2977 | 261.76 | 0.0458 | -0.440 | -0.575 |
| 50 | 0.60 | LOCALLY-STABLE | -0.8139 | 323.71 | 0.0269 | -0.369 | -0.515 |
| 50 | 0.90 | LOCALLY-UNSTABLE | -1.2209 | 277.11 | 0.0545 | -0.405 | -0.604 |
| 100 | 1.00 | LOCALLY-STABLE | -0.7742 | 322.39 | 0.0494 | -0.300 | -0.457 |

The overlay shows metric differences with reuse, but does not establish an
abrupt stochastic-chain change at the theorem boundary.

## I. Stage-D operational conclusion

Still `MATHEMATICAL, NOT OPERATIONAL`, unchanged.

## J. Figures

- `figures/d4_local_stability_map.png`
- `figures/d4_gamma_and_boundary.png`
- `figures/d4_operational_overlay.png`

## K. Tests

Focused D4 tests: `18` passed.
Current distinct check accounting: `965 / 965`.

## L. Adversarial result

`14 / 14` passed.

## M. Reproduction

`bash level4/closure_proofs/d4_phase_map/reproduce.sh`

## N. Historical statuses

Stage D remains `STAGE-D-PARTIAL`; D2.3 remains `FAILED`; D2.5 remains its
negative result; Track 1A remains failed; Track 1B remains closed; Stage F and
the current post-closure global verdict remain `LEVEL-4-PARTIAL`.

## O. Git

See repository history for the freeze, phase-map, and final closure commits.
All pushes are fast-forward and history is not rewritten.

## P. Original global D4 mandatory requirement

`CLOSED` in this later scoped campaign.
No global re-audit is performed here.

## Q. Next blocker

`PRIOR-ART/NOVELTY VERIFICATION`

## Frozen closure criteria

- D4.1: PASS
- D4.2: PASS
- D4.3: PASS
- D4.4: PASS
- D4.5: PASS
- D4.6: PASS
- D4.7: PASS
- D4.8: PASS
- D4.9: PASS
- D4.10: PASS

## Remaining global blockers after scoped D4 closure

- Semi-real external validation — SCIENTIFIC
- Prior-art and novelty verification — DOCUMENTATION_PROVENANCE
