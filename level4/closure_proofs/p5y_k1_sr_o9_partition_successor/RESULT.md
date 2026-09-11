# PS1 - P5Y K1 SR predeclared partition successor: round result

**Classification: `PARTITION_SUCCESSOR_313_REGION_28_OF_28_PASS`.** Not K1 closure; not P5Y closure; not production ready; the old 316-cell campaign is NOT claimed to pass.

## A. Governance ruling

`PARTITION_SUCCESSOR_PERMITTED_AS_NEW_PREDECLARED_ADDITIVE_CAMPAIGN`.

- **1_B_permitted**: YES, as a new additive K1 successor campaign. The s7 prohibition binds the frozen campaign ('after freeze'); it does not bind a new campaign declared before its own results.
- **2_temporal_anchor**: A git commit (P8R Checkpoint-A standard) that contains the protocol, the deterministic partition generator, the generated cell table and its hash, every threshold, and the executable surface, and NO successor scientific result; checked from git (ls-tree of the anchor, anchor ancestor of HEAD, every result recorded against a descendant commit).
- **3_global_partition**: The successor must declare the WHOLE SR partition (all of [0, c_SR]) as one canonical table. A globally predeclared nonuniform partition is allowed: the frozen cover is already nonuniform (its step depends on C at each left endpoint). Every cell must be defined; none may be left to the old table.
- **4_high_rho_only**: YES, if the refinement is a deterministic function of frozen geometry (parent rho, C_upper, a_up, norms) applied uniformly to every parent cell, never of observed pass/fail. The frozen cover's own rule is exactly such a geometry rule.
- **5_inputs_frozen_only**: YES: the generator may read only the frozen cell table and frozen constants plus constants fixed in the protocol; it may not read any T2-T5 record, verdict or ratio.
- **6_new_identities**: YES: T1 refuses any record differing from the frozen cell, and resume identity includes cells_sha256 and cell_index; children need new identities (successor schema, parent index, child index, N) and a new cells_sha256.
- **7_old_obligations**: YES: the old 316-cell obligations and every result (cell 313 m2/m3/m5 FAIL included) stay immutable historical evidence; the successor does not claim them.
- **8_theorem_unchanged**: YES: same target sup_e |R_D,m(e)| < 2 over the same SR drift domain [0, c_SR] (negative drift by the inherited oddness), same m scope, same B_cover = 1/20 per cell, same D/Z/precision/degree.
- **9_new_successor**: YES: a new K1 SR cover successor with its own work universe (28 obligations per NEW cell), not a repair of the 316-cell campaign.
- **A_vs_B**: A (silently subdividing frozen cell 313 after its failure and counting it for the frozen campaign) is ILLEGAL: ERROR_ALGEBRA s7 forbids cell-splitting relaxation after freeze, checkpoint sets adaptive_splitting = false and forbids result-dependent cell changes, and T1 refuses any cell record not byte-identical to its frozen entry. B is the pattern the frozen record itself used: the cover-ledger successor replaced the old 323/322 executable cover by a newly declared 326/316 table under a new governed campaign (new_governed_campaign = true, historical_manifest_reinterpreted_in_place = false, old universe SUPERSEDED_BY_SUCCESSOR, old facts byte-identical, 'does not recolor old results'). P8R/P9R repaired failed campaigns in new namespaces behind a pre-result temporal anchor without rewriting history.
- **caveat**: The need for a finer partition is known because cell 313 failed. This is disclosed, not hidden. It is admissible under the P8R standard (a successor is designed from known failures) provided the rule is global and geometry-only, frozen before any successor result, and never tuned on successor results.

## B. Old vs new campaign semantics

The frozen 316-cell campaign and every result of it (cell 313 m1 PASS, m2/m3/m5 FAIL) remain immutable history. PS1 is a new additive K1 SR successor with its own predeclared 369-cell table, its own identities (PS1-SR-P<parent>-N<n>-K<k>) and its own work universe (28 obligations per successor cell); the theorem target, domain, thresholds and science are unchanged. Union of successor cells = [0, c_SR] exactly.

## C. Legal partition rules evaluated

| rule | successor cells | refined parents | old 313 -> | max child rho | CPU-h (midpoint T3) |
|---|---:|---:|---:|---:|---:|
| GLOBAL_x16 | 5056 | 316 | 16 | 0.0098 | 101373 |
| GLOBAL_x2 | 632 | 316 | 2 | 0.0783 | 12672 |
| GLOBAL_x4 | 1264 | 316 | 4 | 0.0392 | 25343 |
| GLOBAL_x8 | 2528 | 316 | 8 | 0.0196 | 50686 |
| Q_CAP_0.05 | 5009 | 315 | 8 | 0.0227 | 100430 |
| Q_CAP_0.08 | 2513 | 315 | 4 | 0.0392 | 50386 |
| Q_CAP_0.1 | 2505 | 315 | 4 | 0.0392 | 50225 |
| RHO_CAP_1/25 | 369 | 25 | 4 | 0.0396 | 7398 |
| RHO_CAP_1/32 | 413 | 29 | 8 | 0.0311 | 8281 |
| RHO_CAP_1/50 | 460 | 38 | 8 | 0.0198 | 9223 |

## D/E. rho-scaling and child-location diagnostic (NON-CERTIFYING, pre-anchor)

| N | child rho | worst-child ratio m2/m3/m5 (certified inputs, B) | oracle (A) | worst child |
|---:|---:|---|---|---|
| 1 | 0.15663 | 4.24 / 6.28 / 9.82 | 2.96 / 4.34 / 6.82 | k0 (leftmost) |
| 16 | 0.00979 | 0.0213 / 0.0217 / 0.0224 | 0.021 / 0.0214 / 0.0219 | k0 (leftmost) |
| 2 | 0.07831 | 0.557 / 0.77 / 1.16 | 0.43 / 0.579 / 0.858 | k0 (leftmost) |
| 32 | 0.00489 | 0.0104 / 0.0105 / 0.0106 | 0.0104 / 0.0104 / 0.0105 | k0 (leftmost) |
| 4 | 0.03916 | 0.127 / 0.152 / 0.198 | 0.112 / 0.13 / 0.164 | k0 (leftmost) |
| 8 | 0.01958 | 0.0465 / 0.0496 / 0.0553 | 0.0448 / 0.047 / 0.0512 | k0 (leftmost) |

## G/H. Chosen pre-result rule and anchor

RULE RHO_CAP, r_max = 1/25 (dyadic, equal exact-rational children, C_upper inherited); 369 cells; table sha256 `dfaced89653bd71a0bab4a61729407694768456b1e841f042df84c4544bfe349`; protocol sha256 `600a74023470ddac8e4025a031bbd0e7b869fbb524aae5598f11d4caa60cd741`; temporal anchor commit `9bfe3a71dd1884c933aa237896c21d59f9775c0e` (2026-09-11T05:26:43Z), containing no successor result.

## I. Temporal integrity

{'pre_execution': 'TEMPORAL_INTEGRITY_PASS', 'post_execution': 'TEMPORAL_INTEGRITY_PASS'}

## J/K. Certified successor cells

| successor cell | T3 | T5 | B_cover/limit m1 | m2 | m3 | m5 | M_R2 m5 | contraction | T3 CPU-h | peak RSS MiB |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| PS1-SR-P313-N4-K0 | True | 28/28 | 0.167 | 0.1267 | 0.1518 | 0.1981 | 7.679 | 0.076 | 27.3 | 107 |
| PS1-SR-P313-N4-K1 | True | 28/28 | 0.1548 | 0.1188 | 0.1422 | 0.1836 | 7.155 | 0.074 | 20.9 | 107 |
| PS1-SR-P313-N4-K2 | True | 28/28 | 0.14 | 0.1096 | 0.1315 | 0.1683 | 6.664 | 0.071 | 20.5 | 107 |
| PS1-SR-P313-N4-K3 | True | 28/28 | 0.1228 | 0.09927 | 0.1196 | 0.1523 | 6.199 | 0.069 | 20.1 | 107 |
| PS1-SR-P150-N1-K0 | True | 28/28 | 0.07106 | 0.05554 | 0.04761 | 0.03818 | 380.1 | 0.500 | 29.5 | 101 |
| PS1-SR-P275-N1-K0 | True | 28/28 | 0.2304 | 0.2475 | 0.2507 | 0.2648 | 34.75 | 0.503 | 30.0 | 102 |
| PS1-SR-P315-N1-K0 | True | 28/28 | 0.006763 | 0.009273 | 0.01202 | 0.01545 | 2.599 | 0.037 | 24.0 | 102 |

Determinism replay (fresh process, 6 patches of successor cell 360): True.

## F. Cost

Measured T3 midpoint CPU per successor cell: 24.6 CPU-h (30-way load, 32 vCPU); 369-cell projection 9073 CPU-h. Estimate only; the 1,126 CPU-h cap is not requalified and is far exceeded.

## L. Production firewall

No production process, no prodctl, no AWS/Vultr production worker, no production ledger touched; every predecessor namespace byte-identical (temporal-integrity I3).

## M. Next step

A governed full PS1 SR campaign over all 369 successor cells under this frozen protocol (and a matching governed decision on the CPU cap), followed by independent adjudication. Not started.
