# P5Y K1 SR O9 — aux3-style third-derivative evidence: feasibility + governance

**Classification: `AUX3_SR_FEASIBILITY_FAIL`.** Parent `d2981a5`. Diagnostic only; nothing certified; no production; K1/P5Y not closed; not production ready.

## Phase 1 — governance

Ruling `AUX3_SR_PERMITTED_ONLY_VIA_EXPLICITLY_GOVERNED_ADDITIVE_SUCCESSOR`.

- **Q1_additive_aux_candidates_preserve_28**: YES. Precedent CUSUM aux3/aux4: third-derivative candidates entered as an additive successor with no new top-level work id and no new frozen DAG node; universe 17,978 and the per-cell 19+1+4+4 = 28 SR obligations are untouched. The frozen SR T2 census (46 candidates / 102 contracts) stays immutable; order-3 objects form a separate auxiliary census.
- **Q2_evidence_only**: YES. They are nested internal support of the existing curvature (and hence assembly) obligations, bound into the parent certificate as an auxiliary-evidence hash with every leaf SCIENTIFIC by default (aux4 repair of the AUXILIARY_GOVERNANCE defect). They are not obligations.
- **Q3_same_quantity**: YES, as a min-with-cascade refinement: the certified quantity is unchanged (M_R2 = mag(R2_interval(cell)) >= sup_{e in parent cell}|R''_{D,m}(e)|, same all-m assembly, same H_r and W2 node intervals). The Taylor bound H_r(x0,e) in H_r(x0,e0) + [-1,1]*(rho*|F_r'''(x0,e0)| + (rho^2/2)*T[F_r,4]) (or aux3's node form eps_mid + rho*||X'''(e0)|| + (rho^2/2)*T[X,4]) is a proved enclosure of the same node quantity, and a node keeps the cascade whenever it is smaller. ERROR_ALGEBRA s3 fixes differentiation twice as the construction and requires a new governed disposition to replace it, so the successor must carry that disposition explicitly. The cascade is still computed and remains the fallback.
- **Q4_midpoint**: YES: EXACT_MIDPOINT e0 of the frozen parent cell (checkpoint geometry), the same e0 as T2/T3.
- **Q5_parent_rho**: YES: the frozen parent rho; no splitting (adaptive_splitting=false) and no local rho.
- **Q6_fourth_order_global**: YES: T[X,4] must bound sup over every state and every e in the whole parent cell. The norm tower does this by construction from cell-uniform operator norms and closed-form source suprema. No whole-cell order-3 candidate quantity is used; order 3 is used at e0 only.
- **Q7_census_change**: YES, an additive auxiliary census (order-3 candidates and their contracts) is required, and only through an explicitly governed successor: ERROR_ALGEBRA s3 (new governed disposition), aux4 AUXILIARY_GOVERNANCE. The historical 46/102 census and every predecessor stay byte-identical.

## Phase 2 — third-order equations

15 auxiliary candidates (`F:0:k3, F:1:k3, F:2:k3, F:3:k3, F:4:k3, S:0:k3, S:1:k3, S:2:k3, W:0,1:k3, W:0,2:k3, W:1,1:k3, h:1:k3, h:2:k3, h:3:k3, h:4:k3`), 5 image nodes (`S:3:k3, S:4:k3, W:0,3:k3, W:1,2:k3, W:2,1:k3`), 64 new contracts (46 on frozen candidates), new raw moment shift(s) [4]. All midpoint-only. DAG sha256 `7526883218b8afa2`.

## Phase 4 — feasibility oracle (cell 313)

| m | R''(e0) | R'''(e0) | true sup R'' | true sup R'''' |
|---|---:|---:|---:|---:|
| 1 | 0.2495 | 0.523 | 0.3225 | 0.9104 |
| 2 | 0.1249 | 0.2607 | 0.1614 | 0.4534 |
| 3 | 0.126 | 0.256 | 0.1619 | 0.4427 |
| 5 | 0.126 | 0.256 | 0.1619 | 0.4427 |

| B_cover / (1/20) | m2 | m3 | m5 |
|---|---:|---:|---:|
| ideal (true M_R4) | 0.322 | 0.323 | 0.323 |
| pure norm tower, order 4, exact norms | 6.81 | 9.22 | 12.4 |
| pure norm tower, order 4, cert-form norms | 8.18 | 11.3 | 15.4 |
| one-level hybrid (TRUE lower-order cell sups; not certifiable) | 0.476 | 0.493 | 0.53 |
| **self-consistent order-3 architecture, ideal midpoint, exact norms** | 1.42 | 1.87 | 2.49 |

| self-consistent variant | q_N | m2 | m3 | m5 |
|---|---:|---:|---:|---:|
| N4/cert_additive_midpoint/kz_certform | 0.709 | 2.25 | 3.04 | 4.02 |
| N4/cert_additive_midpoint/kz_exact | 0.709 | 1.78 | 2.3 | 3.07 |
| N4/true_midpoint/kz_certform | 0.709 | 1.76 | 2.42 | 3.21 |
| N4/true_midpoint/kz_exact | 0.709 | 1.42 | 1.87 | 2.49 |
| N5/cert_additive_midpoint/kz_certform | 0.936 | 1.58 | 2.08 | 2.74 |
| N5/cert_additive_midpoint/kz_exact | 0.936 | 1.25 | 1.55 | 2.04 |
| N5/true_midpoint/kz_certform | 0.936 | 1.22 | 1.62 | 2.14 |
| N5/true_midpoint/kz_exact | 0.936 | 0.993 | 1.25 | 1.63 |
| N6/cert_additive_midpoint/kz_certform | 1.185 | no bound | no bound | no bound |
| N6/cert_additive_midpoint/kz_exact | 1.185 | no bound | no bound | no bound |
| N6/true_midpoint/kz_certform | 1.185 | no bound | no bound | no bound |
| N6/true_midpoint/kz_exact | 1.185 | no bound | no bound | no bound |

The true R_m is benign on cell 313 (sup_cell|R''''| ~ 0.44-0.91; ideal third-order cover 0.32), but every certifiable whole-cell fourth-order bound is norm-based. Pure norm towers give M_R4 ~ 2e3-4e3; the best self-consistent Taylor tower fed by IDEAL midpoint evidence (orders <= 3) and EXACT norms still leaves m=2,3,5 above 1, because the resolvent self-consistency q_N = C sum C(N,i) k_i rho^i/i! (C ~ 2, parent rho ~ 0.157) amplifies the remainder; adding order-4/5 midpoint candidates raises q_N toward and past 1.

Kill rule: any m in (2,3,5) with best-case certified-architecture ratio > 1.1 -> AUX3_SR_FEASIBILITY_FAIL. Phases 5–7 not run.

## Cost / scaling (not measured)

15 candidates and 64 contracts per cell (+33% / +63% of the frozen T2 census), midpoint-only, reusable across m. Not measured because Phase 5 did not run.

## Determinism

- `phase1_doctrine.json IDENTICAL 97b46ea42d0c0864ea61364b2ea71af7a700ab574b59f409aa1d0a744050e327`
- `phase2_equations.json IDENTICAL fd965e4f1825fbb62301b4aa8bcbe7000b6de4ef7341f1f7d568d79b4c8b2271`
- `phase34_oracle_c313.json IDENTICAL 8ce54c177c8cc1ac724bfdbffedc47af1135795c32ca5c515b8fa14671a345f5`
- `phase34_tower_ext_c313.json IDENTICAL 358959a4d557a202b246fe8a8ff3b6b5b88c834452b9dc1116c58c4b0fda7e1f`
- `phase34_consistent_c313.json IDENTICAL 23bdbcc20c3a1dd518fdaf85184572dd8a45122d6bbac32093e5cc11986ee484`
- `phase34_consistent_v2_c313.json IDENTICAL 362aef3691f49750f6d60ec499847168047bd2702944234ed2771da39e2791f5`
- `DONE`
