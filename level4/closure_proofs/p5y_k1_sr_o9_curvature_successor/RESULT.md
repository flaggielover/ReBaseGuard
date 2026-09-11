# P5Y K1 SR O9 curvature certification successor: CURVATURE_SUCCESSOR_NUMERICALLY_NOT_CLOSING

**CURVATURE_CERTIFICATION_SUCCESSOR only. This is a negative result, committed as immutable evidence.** It is not K1
closure, not P5Y closure, and not production readiness. The parent is `8b8a242` (tag
`p5y-k1-sr-o9-t5-one-cell-28-of-28`), which is unchanged.

The authoritative record is `config/CURVATURE_SUCCESSOR_RECORD.json` (sha256 `bd5f582d9c8aa88c4db39d66aefb5e672d19f6723d635eedafe95610d35b0a27`).

## A. Doctrine ruling: CURVATURE_LOCALIZATION_DOCTRINE_PERMITS_SUCCESSOR

- **Q10_cell_313_target_gate.** Does NOT survive independently: with zero curvature error, the m=1..5 enclosures lie inside (-2,2) (phase2_decomposition.json: target_gate_with_zero_curvature_error = PASS).
- **Q1_quantity.** M_R2 >= sup_{e in parent cell} |R''_{D,m}(e)| at x0, assembled with the frozen positive all-m coefficients from uniform-cell H_r = F_r'' and W''_(r,j) enclosures (ERROR_ALGEBRA 3; checkpoint enclosure.curvature).
- **Q2_one_uniform_enclosure_binding.** NO as a representation. What binds is a certified bound UNIFORM over the parent cell. ERROR_ALGEBRA 1 permits any proved, dependency-preserving enclosure of the same expression, and the frozen CUSUM implementation itself does NOT substitute an interval e: it uses delta_cell = delta_mid + rho*Env (cusum_layer2).
- **Q3_uniform_or_cover.** A rigorous bound for every e in the parent cell. The Taylor cover itself is single and parent-level: R(cell) in R_interval + (cell-e0) D_interval +- rho^2 M_R2/2 with the EXACT midpoint e0 and the parent rho.
- **Q4_sr_refine_subintervals.** NO. sr_refine (like frozen refine.py) refines whole-cell ERROR bounds around the parent midpoint with the parent rho; it has no subinterval concept and neither authorises nor uses one.
- **Q5_union_of_subinterval_certificates.** YES for M_R2 only: max_j over certified sup_{E_j}|R''| on a cover of the cell bounds sup_cell|R''|, with parent e0, rho, D_interval and STYLE_1 unchanged. NO for local Taylor covers with local rho_j: that is cell splitting (ERROR_ALGEBRA 7; checkpoint adaptive_splitting=false; exactly one Taylor representation, no_interpolation).
- **Q6_subdivision_geometry.** No frozen subdivision rule exists. Any subdivision must be predeclared and deterministic before results. The successor chosen here uses none (N = 1).
- **Q7_scientific_vs_representation.** SCIENTIFIC: theorem target sup|R|<2; B_cover<=1/20 with the parent-rho STYLE_1 cover; M_R2 >= sup_cell|R''|; the twice-differentiated resolvent H equation, C_upper, the candidates, contracts and obligations. REPRESENTATION: how sup_cell of the residuals (and of R'') is enclosed: interval-e ball, mean-value extension, or max over subintervals.
- **Q8_obligation_identity.** Unchanged. The same 28 units per cell; the new enclosure is nested evidence inside the existing curvature/assembly obligations, as CUSUM Aux3 did (no new work ID).
- **Q9_cell_315.** Its right endpoint is exactly c_SR (affine [0,1]). The mean-value successor needs only rho (Arb enclosure) and the operator window [-c_SR+e_lo, c_SR+e_hi], so no decimal endpoint enters. A piecewise subdivision would need exact affine sub-endpoints; not used.

Scope: PERMITTED: tighter proved enclosures of the SAME parent-cell quantity, meaning the frozen mean-value whole-cell residual extension, or max over a predeclared subinterval cover, with the parent e0/rho/STYLE_1 unchanged. FORBIDDEN: local-rho Taylor covers (cell splitting), new candidates, any threshold/degree/precision change.

## B/C. Nominal-vs-certified decomposition and the idealized cover (diagnostic only)

| cell | m | certified B_cover / (1/20) | idealized (diagnostic) | M_R2 / nominal R'' | target gate now / with zero curvature error |
|---|---|---|---|---|---|
| 150 | 1 | 0.07585 | 0.0664 | 17x | PASS / PASS |
| 150 | 2 | 0.06011 | 0.0515 | 18.7x | PASS / PASS |
| 150 | 3 | 0.05204 | 0.0437 | 20x | PASS / PASS |
| 150 | 5 | 0.04257 | 0.0346 | 22.5x | PASS / PASS |
| 250 | 1 | 0.2127 | 0.0882 | 1.28e+03x | PASS / PASS |
| 250 | 2 | 0.3111 | 0.0962 | 1.31e+03x | PASS / PASS |
| 250 | 3 | 0.4073 | 0.0988 | 1.46e+03x | PASS / PASS |
| 250 | 5 | 0.6495 | 0.099 | 2.1e+03x | PASS / PASS |
| 275 | 1 | 0.9513 | 0.212 | 624x | PASS / PASS |
| 275 | 2 | 2.063 | 0.204 | 1.1e+03x | PASS / PASS |
| 275 | 3 | 3.165 | 0.189 | 1.5e+03x | PASS / PASS |
| 275 | 5 | 5.898 | 0.161 | 2.42e+03x | PASS / PASS |
| 313 | 1 | 33.42 | 0.621 | 537x | FAIL / PASS |
| 313 | 2 | 1084 | 0.31 | 3.54e+04x | FAIL / PASS |
| 313 | 3 | 1595 | 0.311 | 5.16e+04x | FAIL / PASS |
| 313 | 5 | 2174 | 0.311 | 7.03e+04x | FAIL / PASS |
| 315 | 1 | 0.3006 | 0.00612 | 145x | PASS / PASS |
| 315 | 2 | 9.528 | 0.00306 | 9.29e+03x | PASS / PASS |
| 315 | 3 | 13.25 | 0.00307 | 1.29e+04x | PASS / PASS |
| 315 | 5 | 16.43 | 0.00307 | 1.6e+04x | PASS / PASS |

**Answer: B: certified curvature grossly inflated relative to nominal (idealized cover passes in every cell; cell 313's target-gate failure does not survive a zero-error curvature term).**

## D/E. Successor architecture and subdivision rule

The successor applies the frozen CUSUM layer-2 construction to the SR DAG: delta_cell = delta_mid + rho*Env. Env is
the e-uniform bound on the e-derivative of each node residual, built as closed-form cell-uniform operator norms times
candidate sup norms. The per-node minimum with the T3 interval-e delta_cell is taken; both are valid bounds.

The frozen ErrorDAG, `sr_refine`, assembly, ledger and T5 obligations then run unchanged. Parent e0, rho, STYLE_1
and every threshold are unchanged.

Subdivision rule, predeclared 2026-09-11T02:33:37+00:00 (sha256 `1c0cdc8b9e68e61a...`):
NONE: N = 1 for every cell. No subinterval geometry. A max-over-subintervals enclosure (parent rho) is doctrinally permitted but is not part of this successor, and would need its own predeclared dyadic ladder.

## F/G. Kill micropilot, with cell 150 as control (subdivision level N = 1)

| cell | m | B_cover / (1/20): old -> new | M_R2: old -> new | curvature obligation | assembly obligation | target gate |
|---|---|---|---|---|---|---|
| 275 | 1 | 0.9513 -> 0.2304 | 242.3 -> 6.375 | PASS | PASS | PASS -> PASS |
| 275 | 2 | 2.063 -> 0.2475 | 608.8 -> 14.82 | PASS | PASS | PASS -> PASS |
| 275 | 3 | 3.165 -> 0.2507 | 974.5 -> 20.76 | PASS | PASS | PASS -> PASS |
| 275 | 5 | 5.898 -> 0.2648 | 1878 -> 34.75 | PASS | PASS | PASS -> PASS |
| 313 | 1 | 33.42 -> 0.9897 | 134 -> 1.753 | FAIL | FAIL | FAIL -> PASS |
| 313 | 2 | 1084 -> 4.238 | 4419 -> 16.14 | FAIL | FAIL | FAIL -> PASS |
| 313 | 3 | 1595 -> 6.281 | 6502 -> 24.46 | FAIL | FAIL | FAIL -> PASS |
| 313 | 5 | 2174 -> 9.82 | 8863 -> 38.89 | FAIL | FAIL | FAIL -> PASS |
| 315 | 1 | 0.3006 -> 0.006763 | 57.54 -> 0.5227 | PASS | PASS | PASS -> PASS |
| 315 | 2 | 9.528 -> 0.009273 | 1849 -> 1.403 | PASS | PASS | PASS -> PASS |
| 315 | 3 | 13.25 -> 0.01202 | 2571 -> 1.934 | PASS | PASS | PASS -> PASS |
| 315 | 5 | 16.43 -> 0.01545 | 3188 -> 2.599 | PASS | PASS | PASS -> PASS |
| 150 | 1 | 0.07585 -> 0.07106 | 1423 -> 516.1 | PASS | PASS | PASS -> PASS |
| 150 | 2 | 0.06011 -> 0.05554 | 1309 -> 444.3 | PASS | PASS | PASS -> PASS |
| 150 | 3 | 0.05204 -> 0.04761 | 1256 -> 416.8 | PASS | PASS | PASS -> PASS |
| 150 | 5 | 0.04257 -> 0.03818 | 1212 -> 380.1 | PASS | PASS | PASS -> PASS |

Critical kill cases (B_cover / (1/20)): {'275/m2': 0.24748867114507106, '313/m2': 4.2384665358148395, '313/m5': 9.820491512207859, '315/m2': 0.009273167173054082}. Cell 313 still fails m = 2, 3, 5.

What still binds cell 313, from the H closure after the successor:
- H_0: eps_H 1.504 = C*deltaH 0.747 + C*k2*eps_F 0.114 + C*2k1*eps_D 0.643 + C*eps_S2 0
- H_1: eps_H 29.04 = C*deltaH 14.2 + C*k2*eps_F 1.41 + C*2k1*eps_D 9.33 + C*eps_S2 4.14
- H_2: eps_H 34.25 = C*deltaH 9.87 + C*k2*eps_F 0.856 + C*2k1*eps_D 10.3 + C*eps_S2 13.2
- H_3: eps_H 38.09 = C*deltaH 4.98 + C*k2*eps_F 0.925 + C*2k1*eps_D 11.4 + C*eps_S2 20.7
- H_4: eps_H 41.04 = C*deltaH 4.97 + C*k2*eps_F 0.979 + C*2k1*eps_D 12.3 + C*eps_S2 22.8

Control cell 150: every m passes and every ratio is tighter or equal ({'T5': [28, 'T5_28_OF_28_PASS'], 'all_pass': True, 'tighter_or_equal': True}).

## H. Six-cell validation
NOT REACHED: the predeclared condition (every kill case passes) failed at 313 m = 2, 3, 5

## I. Determinism
12 fresh-process replay files, all byte-identical: True; zero scientific leaves moved: True.

## Predecessor disclosure
frozen sr_operators kz2 cites a pointwise-false inequality; the values used by 8b8a242 are nevertheless valid upper bounds on all six cells (slack 1.07-1.58x); committed T4/T5 stand

## J. Cost
{
 "T2_T3_evidence_reuse": "100% (T3 midpoint-mode deltas and x0 values; no patch recomputation)",
 "curvature_layer_cpu_s_per_cell": {
  "150": 0.854874586,
  "275": 0.842538249,
  "313": 0.840684756,
  "315": 0.839376591
 },
 "peak_rss_kib": 61192,
 "projection_note": "the curvature layer is about 1 CPU-s per cell. The mean-value construction removes the need for the T3 interval-e mode; the T3 midpoint mode alone is ~18 CPU-s per patch at 30-way load (T2 closure runs), i.e. ~20 CPU-h per cell, ~6,300 CPU-h for 316 cells. Estimate only; no cap qualification."
}

## Next options (not taken; each needs its own predeclaration or governance)
- drift-aware sharper operator norms (final_completion sharp_norms precedent)
- predeclared dyadic max-over-subinterval ladder for the residual enclosure (parent rho)
- Aux3-style nested third-derivative evidence (needs auxiliary candidates: governance required)

## L. Production firewall
PASS: True. The production worktrees are unchanged ({'ReBaseGuard-sr-lifecycle': {'dirty': False, 'head': 'bcec064'}, 'ReBaseGuard-sr-parallel': {'dirty': False, 'head': 'bd7cf26'}}), with no active rbg units and no production processes. prodctl was not run;
no production ledger, retry or worker was touched.

