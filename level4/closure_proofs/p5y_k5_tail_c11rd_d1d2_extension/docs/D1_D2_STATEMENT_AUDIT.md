# C11RD — exact reconstruction of the original D1 / D2 statements (cell 306)

Scope. This audit reconstructs, from the ORIGINAL producer chain's source code and committed
artifacts, exactly what the two constants D1 and D2 of N9 mean for K5 tail cell 306. It is written
BEFORE any C11RD target computation. Nothing here is inferred from the constants' names.

Every claim is linked to a file and line range at the C11R final head
`7375b9cdb1d770ba836335164f205e26b445035e` (= the C11RD branch point). File hashes (sha256):

| # | file | sha256 |
|---|---|---|
| S1 | `level4/closure_proofs/p5y_k5_perron_deflated_resolvent/code/taboo_certify.py` (the original certifier) | `ced9422ca07981a9ad053acd79b72ef0d5007e93e49c16f2501f31c593fd0daa` |
| S2 | `level4/closure_proofs/p5y_k5_tail_c2_closure/code/c2_refined_registry.py` (the producer of the cell-306 registry row) | `0d1d8021a3780e13c567f583c1e490025ea2ca43dbfa7082f7dd5905e965b623` |
| S3 | `level4/closure_proofs/p5y_k1_cover_ledger_implementation/code/opnorms.py` (kernel norms, source-derivative sups) | `f195439876fe99bc6bfd5e1b7d35790c23a68f753c2ba1206508a27a11b9f67e` |
| S4 | `level4/closure_proofs/p5y_k1_cover_ledger_implementation/code/cusum_layer1.py` (frozen H, quadrature, dyadic candidates) | `efcc0f36632632577a24c4ddf1a7c2c3579d471cdba5a752dd72c708667cdc79` |
| S5 | `level4/closure_proofs/p5y_k1_cover_ledger_implementation/code/cusum_layer2.py` (Z_RANGE, REWARD_RADIUS) | `42c3d98394a6a8536e05d50626b21c7c71c309f5f98e286bdf2a3f7b5badf5a7` |
| S6 | `level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/registry_c2/REGISTRY_C2.json` (the committed registry) | `1b2b834939fcd80a81ddc8f029f46705b53cefeb46c0cc925a99c2b8e856fdd6` |
| S7 | `level4/closure_proofs/p5y_k5_tail_c11r_n9_statement_alignment/evidence/table/C11R_N9_STATEMENTS.json` (C11R's frozen statement table; git blob `58b4066f…`) | — |
| S8 | `level4/closure_proofs/p5y_k5_tail_c11_n9_independent_certifier/code/c11_certifier.py` (C11's independent re-derivation of the model) | `fc88fb0dcc0f757d9ed42b08ecdd9e7ca2c65320181320f009390d67e3155741` |

The original values D1 and D2 of cell 306 were disclosed in C11R Phase 15 (comparison commit
`2c24a989`). They are NOT used anywhere in this audit, the derivation, the design, the validation or
the calibration of C11RD; they enter only the frozen comparison step, after a sealed C11RD run.

## 1. Producer chain (implementation path and certificate path)

1. **Cell partition** — S2 lines 81–86 (`sub_blocks`): the cell's drift interval is split into
   `N = ceil((x_hi - x_lo) / SUB_BLOCK_MAX_WIDTH)` equal sub-blocks, `SUB_BLOCK_MAX_WIDTH = 1/100`.
   For cell 306 the interval is `[680769/400000, 17885921/10000000]` (width `108337/1250000`), so
   **N = 9**; the nine exact bounds are recorded in S7 `drift_domain.sub_block_bounds` and in S6
   `blocks[1].sub_rows[i].e_lo/e_hi`.
2. **Per sub-block, the premise** — S2 lines 94–107 (`_sub`): `TC.block_artifact(lo, hi, alpha,
   F(0), 2, DEGREE_TABOO = 20, False)` (S1 lines 242–249 → `certify_block`, lines 200–239, with
   `full=False`): a degree-20 polynomial Khat supersolution `w >= 1 + Khat_e w` uniformly on the
   sub-block (Lemma T), giving `C_T = sup w` (over the reachable cover) and `tau = w(a)`.
3. **Per sub-block, D_lo / D1 / D2** — S2 lines 108–113: `TC.cell_artifact(mid, half, tau, C_T,
   degree = 20)` with `mid`, `half` the sub-block's centre and half-width (S1 lines 352–356 →
   `certify_cell`, lines 284–349). The artifact is the "denominator artifact" of the sub-row
   (`denominator_artifact_sha256` in S6; the nine hashes are S7's D1/D2 `aggregation.artifacts`).
4. **Cell aggregation** — S2 lines 161–165: `D1 = max(sub-row D1)`, `D2 = max(sub-row D2)`
   (and `D_lo = min`, `C_T = max`, `tau = max`). Registry rule "r2", `degree_taboo = 20`.

## 2. The model (state, dynamics, atom, reachable set)

* Constants: `K_ = 0.5`, `C_ = 5.5` (S1 line 55); frozen state bound `H_FROZEN = 5.0` (S4 line 40).
  C11 re-derived the same `K = 1/2, H = 5, C = K + H = 11/2` from the frozen model text (S8 lines
  60–63).
* Transition from `x = (p, m)` with drift `e`: increment `z` with density `phi(z + e)`
  (S1 lines 103–104: `y = z + drift`, weight `phi(y)`); alarm-free window `z in [ell, up] =
  [m - C, C - p]` (S1 line 94); next state `x'(z) = (max(0, p + z - K), max(0, m - z - K))`
  (S1 lines 105–106, `wp`, `wm`; S8 docstring).
* The atom `a = (0, 0)` is reached exactly for `z in [beta, alpha] = [m - K, K - p]` (non-empty iff
  `p + m < 1`) (S1 lines 95, 99–100: `beta, alpha = m - K_, K_ - p`; `continue` skips that window).
* State set: `R = {(p, m) in [0, 5]^2 : p + m <= 4 or p = 0 or m = 0}` (S7 `state_set`; S8
  `box_meets_R`). The original bounds residuals on a reachable cover (`max_abs_on_reachable_fast`,
  S1 lines 296–298), a superset of R.

## 3. The operators

* `K_e f(x) = int_{ell}^{up} f(x'(z)) phi(z + e) dz` (full kernel; used for Abar only).
* **`Khat_e = K_e` with the atom window removed** (S1 docstring lines 3–4: `K_e = Khat_e +
  k_a (x) delta_a`; `Ops.khat`, lines 148–155: the "origin" piece is subtracted from the low branch;
  float proposal lines 99–100 skip `[beta, alpha]`). **D1 and D2 use Khat_e only** (S1 lines 300–314;
  S7 D1/D2 `kernel: Khat_e`, `convention: atom_removed`).
* **Derivative kernels** `Khat_e^(i) f(x) = int_{window \ atom} f(x'(z)) phi^(i)(z + e) dz`: the
  derivative is taken in the DRIFT `e` and acts only on the density, because every window endpoint
  (`m - C`, `C - p`, `m - K`, `K - p`) is independent of `e` in the `z` variable (S1 `Ops.__init__`
  lines 136–140: `b[i]` = successive derivative coefficient series of phi; float line 108:
  `phi^(o)(y) = (-1)^o He_o(y) phi(y)` with `He_1 = y`, `He_2 = y^2 - 1`).
* **Source** `h_1 = 1 - K_e 1 = 1 - Phi(C - p + e) + Phi(m - C + e)` (one-step alarm probability),
  `h_1' = -S_0 = -phi(C - p + e) + phi(m - C + e)`, `h_1'' = -S_1 = (C - p + e) phi(C - p + e) -
  (m - C + e) phi(m - C + e)` (S1 `closed_h1` lines 261–271; `float_h1` lines 115–128).

## 4. The objects d, d', d'' and the constants

(S1 docstring lines 6–10, `taboo_proposals` lines 274–281, `certify_cell` residuals lines 300–314.)

    d    = Ghat_e h_1                         Ghat_e = (I - Khat_e)^(-1) = sum_n Khat_e^n
    d'   = Ghat_e (Khat'_e d + h_1')
    d''  = Ghat_e (Khat''_e d + 2 Khat'_e d' + h_1'')

`d(x) = P_x(alarm before reaching the atom)`; `D_e := d_e(a)`. `d'` and `d''` are the first and
second derivatives of `e -> d_e` (derivative variable: the drift `e`; orders 1 and 2), evaluated
state-wise; `D_e' = d'_e(a)`, `D_e'' = d''_e(a)`.

**D1** is an upper bound of `|D_e'| = |d'_e(a)|` and **D2** an upper bound of `|D_e''| =
|d''_e(a)|`, **for every e** in the sub-block (S1 line 348, statement:
*"for every e in [e0 - rho, e0 + rho]: D_e >= D_lo, |D_e'| <= D1, |D_e''| <= D2 (given ||Ghat_e|| <=
C_T and (Ghat_e 1)(a) <= tau on the same set)"*). Direction: **UPPER bounds of absolute values**.
Norm: the supremum norm on R for the operator bounds; the constants are values at the atom.

## 5. How the original bounds them (the proof route, not the statement)

S1 `certify_cell`, lines 284–349:

* Candidates `d~0, d~1, d~2`: degree-20 (in the registry run) tensor-Chebyshev polynomials on
  `[0, H]^2` from a float solve at the sub-block centre `e0` (lines 274–281), made exact-dyadic
  (S4 `dyadic_candidate`).
* Residuals at `e0`: `r0 = d~0 - Khat d~0 - h_1`, `r1 = d~1 - Khat d~1 - Khat' d~0 - h_1'`,
  `r2 = d~2 - Khat d~2 - 2 Khat' d~1 - Khat'' d~0 - h_1''`, bounded on the reachable cover by
  `max_abs_on_reachable_fast` (Bernstein-type range bound) plus truncation allowances
  `x_k` (`Ops.trunc`: `2 Z_RANGE sup (N+1)^i eps_z`, the order-120 phi Taylor series; `closed_h1`
  allowances) → `lambda_mid[k]`.
* Extension to the sub-block (fixed candidates): `lambda_cell[k] = lambda_mid[k] + rho env_k`,
  `env0 = kappa1 S0 + sup|h_1'|`, `env1 = kappa1 S1 + kappa2 S0 + sup|h_1''|`,
  `env2 = kappa1 S2 + 2 kappa2 S1 + kappa3 S0 + sup|h_1'''|` (lines 303–317), with
  `kappa_i = kernel_norm(i)` (S3 lines 82–98: whole-line `int |phi^(i)|`: `kappa1 = 2 phi(0)`,
  `kappa2 = 4 phi(1)`, `kappa3 = 2 phi(0) + 8 phi(sqrt 3)`) and `sup_h[k] =
  sup_source_derivative(k - 1)` (S3 lines 136–141: `2 sup|phi^(n)|`).
* Propagation (lines 321–327): `n0 = C lam0`, `p0 = tau lam0`, `n1 = C (lam1 + kappa1 n0)`,
  `p1 = tau (lam1 + kappa1 n0)`, `p2 = tau (lam2 + 2 kappa1 n1 + kappa2 n0)`.
* **D2** `= |d~2(a)| + p2(cell)` (line 333). **D1** `= min(|d~1(a)| + p1(cell),
  D1_mid + rho D2)` with `D1_mid = |d~1(a)| + p1(mid)` (lines 332–336; a mean-value alternative).
* Dependencies: the sub-block's OWN `C_T` and `tau` (item 2 above). C11R's frozen table records
  that a block-uniform `(C_T, tau)` pair is also sound because the propagation is increasing in both
  (S7 D1/D2 `dependency_granularity`).
* No denominator enters D1 or D2 (D_lo is the "denominator" of the ARL ratio downstream).

## 6. Kinks, boundaries and conventions (what any re-derivation must respect)

* `max(0, ·)` kinks of the state update at `z = K - p` and `z = m - K`; the atom window between
  them when `p + m < 1`; the alarm window `[m - C, C - p]` (S1 lines 94–106; S8 `kernel_apply`).
  The original resolves them with cut points in the Pair kernel (`_kernel_polynomials`, two
  polynomial branches) and its float proposal (lines 94–109).
* A mechanical consequence (derived in `theory/D1_D2_DERIVATION.md`, Lemma 1, not taken from the
  original): the images of the two single-arm z-ranges lie on the AXES and the image of the
  both-positive range lies on the line `p' + m' = p + m - 1`, so `d, d', d''` are analytic on each
  band `k <= p + m <= k + 1` and have derivative jumps across the lines `p + m = 1, 2, 3, 4`. The
  original used one global polynomial per object and absorbs these kinks in its residual bound.

## 7. The exact C11RD targets (what "the same statement" means here)

For cell 306, with `E = [680769/400000, 17885921/10000000]`, `R`, `a = (0, 0)` and `Khat_e` as above:

* **D1\***: *for every e in E: |d'_e(a)| <= D1\**, where `d_e = Ghat_e h_1`.
* **D2\***: *for every e in E: |d''_e(a)| <= D2\**.

Statement fields to match the original record (S7 `original_statements.D1/D2`): constant `D1`/`D2`;
quantity *"|d'(atom)|, the first drift derivative of d"* / *"|d''(atom)|, the second drift
derivative of d"*; kernel `Khat_e`; convention `atom_removed`; direction `UPPER_BOUND`; state set R;
drift domain exactly E (EQUAL); aggregation `max_over_sub_blocks` over a partition that tiles E
exactly (the maximum preserves "for every e"); dependencies `C_T_independent`, `tau_independent`
— C11R's ACCEPTED independent F_H certificate (a block-uniform pair on all of E), never an original
constant. Under C11R's frozen statement-equivalence rule (`c11r_equiv._premises`: `_independent`
suffix normalised; SAME premises; domain EQUAL), such a record compares as **EQUIVALENT** to the
original, and the frozen factor-2 numerical rule (S7 `comparison_semantics_frozen_before_results`)
then applies unchanged.

## 8. What the audit does NOT establish

It does not certify anything, reproduce any original value, or read any original D1/D2 value; it
fixes the statements the independent certifier must prove.
