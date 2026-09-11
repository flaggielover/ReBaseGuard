# P5Y K1 SR O9 — cell 313 operator-norm / source-chain successor

**Classification: `OPERATOR_NORM_TIGHTENING_INSUFFICIENT`.** Parent `804e387`. Diagnostic only; nothing certified; no production; K1/P5Y not closed; not production ready.

## Phase 1 — doctrine

Ruling `OPERATOR_NORM_TIGHTENING_PERMITTED`; all bound fragments present.

- **Q1_requirement**: YES: every propagation edge needs a certified UPPER bound ||T_i|| of the same operator (depgraph edge rule; ERROR_ALGEBRA 2 'certified operator norm bounds ... over the whole cell'). Sampled norms are forbidden.
- **Q2_historical_formula_binding**: NO: whole-line moments are 'admissible', not mandatory. The frozen final-completion campaign replaced them by drift-aware closed forms, min(drift-aware, whole-line, Cauchy-Schwarz), recorded as 'not a relaxation of anything'.
- **Q3_tighter_proved_norm**: YES, provided it bounds the SAME operator (K^(i), K_z^(i) with the frozen e-free continuation limits), sup over the SAME reachable state set and every e of the SAME parent cell, on the same edges and owners (ERROR_ALGEBRA 1: a tighter proved enclosure of the same expression).
- **Q4_cell_dependence**: C_upper is frozen per-cell input and not replaceable (B_resolvent = 0, multiplicative only). k_j >= sup_cell ||K_j|| may depend on the frozen parent cell's drift interval. Midpoint-DAG norms may be evaluated at e0 (R and D intervals are midpoint quantities); cell-DAG, mean-value and refinement norms must be uniform over the parent cell. No sub-cell dependence.
- **Q5_derivative_specific**: YES: each edge carries its own norm (k_i, kz_i per derivative index), so no shared envelope is required; each can be certified separately.
- **Q6_obligation_identity**: NO change: norms are nested certificate inputs; the 28 units per cell are unchanged.
- **known_defect**: The frozen sr_operators kz2 cites a pointwise-false inequality; its values were proved valid for the six cells (curvature successor evidence). It must not be copied: any successor norm needs an independent derivation.

## Phase 3 — oracle-tight norms (NON-CERTIFYING)

| variant | m1 | m2 | m3 | m5 | M_R2 m5 |
|---|---:|---:|---:|---:|---:|
| base | 0.9897 | 4.238 | 6.281 | 9.82 | 38.89 |
| K_all | 0.9872 | 4.222 | 6.255 | 9.732 | 38.53 |
| Kz_all | 0.9897 | 3.432 | 4.952 | 7.812 | 30.7 |
| ALL_NORMS | 0.9872 | 3.417 | 4.93 | 7.74 | 30.41 |
| CANDSUP_only__beyond_norm_scope | 0.9154 | 3.616 | 5.458 | 8.545 | 33.69 |
| ALL_NORMS_plus_CANDSUP__beyond_norm_scope | 0.9136 | 2.958 | 4.344 | 6.816 | 26.64 |

| norm | old cell (env) | oracle cell sup | old/oracle | removable share of M_R2 m5 |
|---|---:|---:|---:|---:|
| K^(0) | 0.7492 | 0.7492 | 1.000 | 0.4% |
| K^(1) | 0.4796 | 0.4796 | 1.000 | -0.0% |
| K^(2) | 0.6978 | 0.6978 | 1.000 | 0.5% |
| K^(3) | 0.9794 | 0.9794 | 1.000 | -0.0% |
| K_z^(0) | 5.272 | 4.239 | 1.244 | 6.2% |
| K_z^(1) | 3.719 | 2.453 | 1.516 | 6.2% |
| K_z^(2) | 6.402 | 3.74 | 1.712 | 4.5% |
| K_z^(3) | 10.3 | 5.13 | 2.009 | 4.1% |

Even with every operator norm replaced by its exact value, m=2,3,5 stay at 3.42, 4.93, 7.74. Stop rule 2 holds: no rigorous norm successor is built; Phases 4–7 are not run.

## Next blocker

NORM_ONLY_UNIFORM_CELL_H_CASCADE: the cell-uniform eps_H of F_1..F_4 is carried by the mean-value residual (F_1), the parent-rho derivative feedback C*2k1*(epsD_mid+rho*supH) and the source cascade C*epsS2 (F_2..F_4), while sup|H_hat| of F_2..F_4 is 1e-2..1e-12.

| F_r (oracle norms) | eps_H_cell | C·deltaH | C·k2·nF | C·2k1·nD | C·epsS2 | sup|H_hat| |
|---|---:|---:|---:|---:|---:|---:|
| F_0 | 1.494 | 0.64 | 0.747 | 0 | 0.107 | 0.636 |
| F_1 | 22.35 | 7.33 | 10.9 | 2.94 | 1.21 | 2.03 |
| F_2 | 25.56 | 7.68 | 7.65 | 9.56 | 0.657 | 0.00976 |
| F_3 | 29.82 | 8.96 | 4.97 | 15.2 | 0.729 | 2.34e-08 |
| F_4 | 32.13 | 9.66 | 4.97 | 16.7 | 0.769 | 1.47e-12 |

| m | M_R2 certified | M_R2 oracle | M_R2 max for ratio 1 | reduction still needed |
|---|---:|---:|---:|---:|
| 1 | 1.753 | 1.744 | 1.796 | 0.971x |
| 2 | 16.14 | 12.79 | 2.935 | 4.36x |
| 3 | 24.46 | 18.95 | 2.932 | 6.46x |
| 5 | 38.89 | 30.41 | 2.932 | 10.4x |

## Escalation

Requires `CUSUM_AUX3_STYLE_THIRD_DERIVATIVE_EVIDENCE`: the frozen sr_refine already applies the aux3 Taylor alternative at orders 0 and 1 (nF, nD); order 2 (H) has no Taylor alternative because it needs X'''(e0), which no frozen candidate provides. Norms (even exact), D/Z/degree/precision, splitting and local rho are all excluded, so the only remaining frozen-compatible lever on eps_H_cell is eps_cell(X^(2)) <= eps_mid(X^(2)) + rho*||X^(3)(e0)|| + (rho^2/2)*T[X,4], min with the cascade (CUSUM aux3, Part 3).

whether it closes 313 depends on the uncomputed |X'''(e0)| and T[X,4]; aux3 measured norm-only towers 500x-53000x above certified candidate sups at CUSUM cell 321, which is the same structure seen here (sup|H_hat| of F_3, F_4 ~ 1e-8..1e-12 against eps_H ~ 30..41).

- m=2: rho*|R'''(e0)| + (rho^2/2)*T[R,4] <= 2.81, i.e. |R'''(e0)| + 0.0783*T[R,4] <= 17.94
- m=3: rho*|R'''(e0)| + (rho^2/2)*T[R,4] <= 2.806, i.e. |R'''(e0)| + 0.0783*T[R,4] <= 17.92
- m=5: rho*|R'''(e0)| + (rho^2/2)*T[R,4] <= 2.806, i.e. |R'''(e0)| + 0.0783*T[R,4] <= 17.92

Estimated: 15 order-3 auxiliary candidates per cell, midpoint certification only. New contracts:

- order-3 SR equations: K_e''' by differentiating SR_DERIVATION K_e'' = K_z2,e + 2e K_z,e + (e^2-1) K_e once more, and the Leibniz order-3 recursions for F, W, S (as aux3 code/aux_certifier.py)
- order-3 collocation operator continuing phi^(i)/phi = (-1)^i He_i at i=3 on the frozen grid/degree/quadrature/basis
- per-patch T2 certification of the 15 order-3 objects at e0 (midpoint residual, B_int/endpoint strips as frozen)
- order-4 norm-only tower T[X,4]: new certified K^(4), K_z^(4) bounds (A_5 moments) with an independent derivation (the sr_operators kz2 justification must not be reused)
- governed successor contract: auxiliary evidence nested in the existing units, bound as auxiliary_evidence_hash; 28 obligations per cell unchanged; candidates/contracts change requires explicit authorization

Not implemented in this round.

## Determinism

- `phase23_oracle_c313.json IDENTICAL 9cffaac07ceb80f290ce5bc35b8c73140b17d7dbd498c8eb3303dc6c95672b29`
- `phase3_next_blocker_c313.json IDENTICAL e53a9522e66ceb8e600fbc7cf9807a4a81b5c335f13680ecf33fbc7db36bfa5f`
- `DONE`
