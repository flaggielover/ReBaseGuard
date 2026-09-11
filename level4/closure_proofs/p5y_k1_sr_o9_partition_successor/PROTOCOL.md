# PS1 - P5Y K1 SR predeclared partition successor: PRE-RESULT PROTOCOL

Frozen before any successor certified result. Machine-readable source: `config/PARTITION_PROTOCOL.json`;
frozen file set: `config/PROTOCOL_DIGEST.json`; temporal anchor: `TEMPORAL_ANCHOR.md` (checked against git).

## Purpose

Prove the SAME K1 SR target over the SAME SR drift domain with the SAME frozen science, on a NEW predeclared partition whose cells are small enough for the frozen STYLE_1 Taylor/curvature architecture. A new additive successor campaign; the 316-cell campaign and all its results (including cell 313 m2/m3/m5 FAIL) stay immutable history and are not claimed.

## Domain and theorem

SR drift e in [0, c_SR], c_SR = log(4581762885148045/8796093022208) + 1/2 (exact, symbolic); negative drift by the inherited exact oddness; far-field theorem P5X-T3 and splice obligations inherited unchanged. The CUSUM cover is outside this successor (its own governed campaign).

Target: sup_e |R_D,m(e)| < 2; K1 only; m = 1,2,3,5 (unchanged).

## Partition (RULE RHO_CAP, r_max = 1/25)

For every frozen SR parent (in order) N = smallest of 1, 2, 4, 8, ... with rho/N <= 1/25; equal exact-rational
children; C_upper inherited; terminal parent not split. Generator: `code/partition_generator.py` (reads only the
frozen cell table). Result: 369 cells, parents split {'1': 291, '2': 11, '4': 14}, table sha256
`dfaced89653bd71a0bab4a61729407694768456b1e841f042df84c4544bfe349`. Old cell 313 -> successor cells [360, 361, 362, 363].

## Unchanged science

- **B_cover**: 1/20 per cell, STYLE_1, all budgets and nested gates unchanged
- **D**: 11
- **Z**: 20
- **precision_bits**: 256
- **candidate_degree**: 16
- **candidates_contracts**: 46 candidates / 102 contracts per cell (frozen O9 census)
- **T2**: T2-closed per-patch certifier (O9 core, endpoint-strip successor, B_int, P1 softplus Lagrange factor), all 3,994 frozen live patches
- **curvature**: governed mean-value successor: delta_cell = delta_mid + rho*Env over the successor cell (interval-e cell mode not run)
- **T4_T5**: frozen ErrorDAG, sr_refine, assembly, ledger and T5 gates, generated verbatim (code/make_successor_stages.py)
- **obligations**: 28 per successor cell, same unit structure as the frozen parent; SR successor universe = 28 x 369 = 10332 (+ far field)

## Why this rule

- **doctrine**: geometry-only rule over the whole domain, the same kind as the frozen s-rule; no pass/fail input
- **a_priori**: the STYLE_1 charge W = rho|D| + rho^2 M_R2/2 is in absolute units and its uniform-cell inflation scales with rho; an absolute radius cap is the direct control
- **diagnostic_margin_worst_old313_child**: {'1': 9.820491512834474, '16': 0.022413992748831525, '2': 1.1586943031659933, '32': 0.010574932105246017, '4': 0.1980632883444213, '8': 0.05528471012313246}
- **cost_projection_cpu_h_midpoint_only**: {'GLOBAL_x16': 101372.8, 'GLOBAL_x2': 12671.6, 'GLOBAL_x4': 25343.2, 'GLOBAL_x8': 50686.4, 'Q_CAP_0.05': 100430.45, 'Q_CAP_0.08': 50385.65, 'Q_CAP_0.1': 50225.25, 'RHO_CAP_1/25': 7398.45, 'RHO_CAP_1/32': 8280.65, 'RHO_CAP_1/50': 9223.0}
- **rejected**: {'GLOBAL_x2': 'fails the diagnostic at the old-313 region (1.16)', 'GLOBAL_x4_x8': 'robust but 3.4x-6.8x the cost of RHO_CAP_1/25', 'Q_CAP': 'the a-priori sr_refine contraction q is ~0.5 across almost the whole table by the frozen step rule, so it cannot single out the failing region (it would split ~311 cells)', 'RHO_CAP_1/32, 1/50': 'more cells for no diagnostic need'}

## Disclosure

The need for a finer partition is known from the historical cell-313 failure. r_max = 1/25 was chosen from NON-CERTIFYING diagnostics of the historical geometry (evidence/phase34_*), before and independent of any successor result, and is frozen here.

## Micropilot and controls

Phase 8: children of old cell 313 [360, 361, 362, 363]; every child must be 28/28 PASS. Phase 9 controls: {150: [150], 275: [275], 315: [368]}.

## Prohibitions

- no change of partition, thresholds or scientific settings after any successor result
- no per-cell tuning, no removal or truncation of any region, no redefinition of K1
- implementation-defect fixes only if they change no partition, threshold or scientific setting; each fix committed and recorded; results produced before a fix are rerun
- no claim that the old 316-cell campaign passed
- no production
