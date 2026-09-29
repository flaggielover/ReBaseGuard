# Independent SRK certificate verifier

`verify/srk_verify_indep.py` is the second, independent implementation of the SRK certificate check. It decides
claims (C1)–(C4) and the sha256 check of `impl/SRK_CERT_SPEC.md` §3 for `SRK_CERT/1` certificates.

**Independence.** The verifier was written from the specification documents only:
* `impl/SRK_CERT_SPEC.md`, including the later additions `weight_block`, `kernel: taboo` and erratum SE-1;
* `theory/THEOREM_SRK.md` §§1, 2, 9;
* `p5y_k5_perron_deflated_resolvent/theorem/OPERATOR_AUDIT.md` §1.

No producer module (`impl/srk_*.py`, the overnight `c1b_*` / `d309_*` modules) and no other certifier code was opened,
imported or copied. The only other inputs it reads are the decoy certificate files, and it never modifies them. It
uses the Python standard library only (integers and `fractions`), with no numpy, mpmath or flint.

For the frozen geometry (h, k) = (5, 1/2), a certificate whose block or weight block meets [6/5, 13/5] or
[−13/5, −6/5] is **REFUSED** before anything is evaluated. None of the decoys does.

## Usage

    python3 verify/srk_verify_indep.py CERT.json [--index I] [--max-depth 24] [--order 8] [--procs 1] [--json OUT]
    python3 verify/run_verify_all.py      # all decoy files + section 5 mutants -> verify/VERIFY_RESULTS.json
    python3 verify/run_verify_all.py --remutate --jobs 4   # keep recorded genuine verdicts, re-run mutant batteries
    python3 verify/results_table.py       # markdown tables of VERIFY_RESULTS.json
    python3 tests/test_verify_selftests.py

The verdicts are:
* **ACCEPT**: every claim is proved.
* **REJECT**: carries a reason and the failing cell. The reason says one of two things:
  * `FALSE at (p, m, e)`: a rigorous point *upper* bound < 0, so the claim is disproved.
  * `UNPROVEN at depth limit`: a method limitation; the claim is not disproved.
* **REFUSE**: the input is malformed or falls in the quarantine band.

## Method

1. **Kernel closed form (re-derived).** Write σ = p − e, τ = m + e, t = e − e_c and u = z + e.
   * The images of the clipping pieces are (0, τ−u−k), (σ+u−k, τ−u−k) and (σ+u−k, 0), plus the atom when p + m ≤ 2k.
   * The window limits are L1 = τ−c, L2 = k−σ, L3 = τ−k and L4 = c−σ.
   * From ∫_A^B u^n φ = c_n(Φ(B)−Φ(A)) + H_n(A)φ(A) − H_n(B)φ(B), where c_n = (n−1)!! for even n (0 for odd n),
     H_0 = 0, H_1 = 1 and H_n = u^{n−1} + (n−1)H_{n−2}, one gets
     (K_e P)(x) = Σ_L α_L(σ,τ,t) Φ(L) + β_L(σ,τ,t) φ(L).
   * The polynomials α_L and β_L are exact rationals, computed once per certificate, with one set for case A
     (p+m ≥ 2k) and one for case B (p+m ≤ 2k).
   * Taboo mode drops the atom piece.
   * The formula is cross-checked against quadrature of the *defining* integral: whole and taboo kernel, geometries
     (5,1/2), (3,1/2), (4,1/3), random polynomials. Agreement is 1e-14 relative.
2. **Cover.** X is the triangle p, m ≥ 0, p+m ≤ h−2k, plus the two axis segments.
   * X × E is covered by prisms (polygon × e-interval). The polygons are axis boxes clipped exactly (Fractions) by
     p+m ≤ h−2k and by the case line p+m = 2k.
   * The initial cells have width 1/4 and span the full block.
   * A failing cell is bisected along its widest dimension, down to `--max-depth` (default 24).
3. **Taylor models (order N = 8).** Each cell gets a frame (σ,τ,t) = centre + (r0 x0, r1 x1, r2 x2), with x ∈ [−1,1]³
   containing the prism.
   * **Polynomials** are shifted into the frame *exactly*, with integer arithmetic after clearing denominators.
     They are then rounded to a 2^-128 grid. Every rounding error (≤ 1 ulp per coefficient) and every truncated term
     of degree > N goes into an interval remainder.
   * **Φ(L) and φ(L)** are expanded around the rational centre. The derivatives come from Hermite polynomials, and
     the remainder is the Lagrange remainder sup|He_N φ|·s^{N+1}/(N+1)!. Products carry the standard Taylor-model
     remainder.
   * **Cancellation.** The large cancellation between P and K_eP therefore happens exactly, inside the polynomial
     part.
4. **Lower bound of a model over a prism.** It is the sum of four parts:
   * the constant term;
   * the exact minimum of the linear part over the prism's vertices (exact rationals);
   * Σ_{|a|≥2} of min(0, c) when all exponents are even, else −|c|;
   * minus the remainder.

   On axis cells the prism is 2-dimensional: x1 ≡ x2 on m = 0 and x0 ≡ −x2 on p = 0. These identities are
   substituted before bounding, which is exact on the feasible set.
5. **Gaussian enclosures.**
   * **π** from Machin's formula; the alternating partial sums bracket π, with width < 2^-500.
   * **1/√(2π)** by directed integer square roots.
   * **exp(z)** by argument halving, a Taylor series with directed rounding and a tail bound, then repeated squaring.
   * **φ** = exp(−x²/2)/√(2π).
   * **Φ(x)** = ½ + φ(x)Σ x^{2n+1}/(2n+1)!! for 0 ≤ x ≤ 8 (a positive series with a geometric tail bound). For x > 8
     the Mills bracket [1 − φ(x)/x, 1] is used, and Φ(−x) = 1 − Φ(x).
   * **Ranges of |He_n|φ** use a centred form for He_n on pieces of width ≤ 1/4, together with the monotonicity of φ
     on each side of 0.
6. **The weight κ̄_i over the weight block E_w.** Here k_i(x;e') = G(c−p+e') − G(m−c+e') with G = ∫_{−∞}^u |He_i|φ.
   * **Closed form of G.** G(u) = C_J − s_J He_{i−1}(u)φ(u) on the piece J between consecutive roots of He_i.
     * The roots are isolated by n exact sign changes and bisected to width 2^-200.
     * C_0 = 0 and C_{J+1} = C_J + 2 s_{J+1} He_{i−1}(r_J) φ(r_J).
     * Near a root, G_{J+1} − G_J = 2 s_{J+1}(H(r_J) − H(u)) ≥ 0, which gives one-sided rules. Where a root line
       p = c + e' − r (or m = r + c − e') crosses a cell, the cell is clipped into two sub-polygons, and each uses the
       analytic piece formula with those rules, plus an error term ≤ 2·(bracket width)·sup|He_i φ|.
   * **Sup over e'.** On a sub-interval I = [a, b] of E_w, suppose ∂_{e'}k = g(c−p+e') − g(m−c+e') (with g = |He_i|φ)
     has a certified sign over cell × I. Then the sup is attained at an endpoint.
     * Otherwise, sup_I k ≤ max(k(a), k(b)) + (b−a)²/8 · M2, where M2 ≥ sup|∂²k| ≤ sup|He_{i+1}φ|(c−p+e') +
       sup|He_{i+1}φ|(m−c+e'). This is the interpolation error bound for a C^{1,1} function.
     * Hence κ̄ ≤ max_j k(·;e'_j) + δ on the cell, and (C3) follows from min_j LB(D − k_j) − δ ≥ 0.
     * Points whose k-range is dominated by another point's are dropped. The tolerance for δ starts at 2^-12 and is
       refined only when δ decides a cell.
7. **Disproof.** For every failing cell at depth ≥ 2, the claimed quantity gets a rigorous point *upper* bound at the
   cell centre; at the depth limit, also at the vertices × e-endpoints. For (C3) this uses κ̄(x) ≥ k(x;e') for 17
   sample points e' ∈ E_w. A negative bound is reported as **FALSE**.

## Soundness argument and assumptions

**Why an ACCEPT is a proof.** ACCEPT is returned only if every cell of a cover of X × E has a certified lower bound
≥ 0 for each of (C1), (C2), (C3), (C4) holds as an exact rational comparison, and the sha256 matches. Each lower
bound rests on four facts:
1. the case formulas equal K_eP on their closed regions;
2. the Taylor models enclose the analytic formulas on the frame box, which contains the prism;
3. the κ̄ bound κ̄ ≤ max_j k_j + δ, together with the one-sided root rules;
4. the vertex/abs-sum bound.

All rounding is directed or swept into the remainders. Internal exceptions produce REJECT, never ACCEPT. A run is
accepted only if every cover task completed.

**Assumptions.** Correctness of Python's integer and Fraction arithmetic, and of the following classical results:
* Machin's formula and alternating-series bracketing;
* Taylor's theorem with the Lagrange remainder;
* Mills' inequality 1 − Φ(x) ≤ φ(x)/x (x > 0);
* simplicity of the real roots of He_n (n roots found by n sign changes);
* the C^{1,1} interpolation bound;
* the model of SRK_CERT_SPEC §1 (window, update map, reachable closure X), which was re-derived here, including the
  piece ordering m−c ≤ k−p ≤ m−k ≤ c−p for p+m ≥ 2k (valid because p+m ≤ h+2k on X).

**Limitations.**
* A REJECT that is not a disproof can be a method limitation. The limits are the depth (default 24) and the Taylor
  order (8).
* The disproof is only attempted at a few points per failing cell.
* Polynomial degree is limited to ≤ 24 by the parser; the decoys use 8–12.
* The verifier checks the certificate claims only. It does not re-derive Lemma SV′ or the use of Γ in
  `srk_assemble.py`.

## Results

These results are from `verify/VERIFY_RESULTS.json`; `python3 verify/results_table.py` regenerates the tables.
* **Settings:** Taylor order 8, initial cell width 1/4, depth limit 24 (6 for the item-7 probes), one process per
  verification.
* **Hashes:**
  * verifier `srk_verify_indep.py`: sha256 `a32d5d397893a1fc698d3609f59cb65aab3bc4fe1445c51c676fd9ad54652333` (unchanged throughout);
  * harness v2 `run_verify_all.py`: `3455c1414464290a306384770a056c2e4a7e3c2210965eac49500809f9a7ce05`;
  * harness v1: `54840bf4d364f7b4853b542d74f81f9c5cdbd9ad97e5b447a1a2b808e2a8d2be`;
  * `results_table.py`: `389a87d7cc1be83aab18884686a1825bced2a8bc32010c98574109bff269e2fe`.

### Inputs

| directory | certificates | classes | genuine verdicts | mutant batteries |
|---|---|---|---|---|
| `evidence/srk_decoys/` (producer rerun) | 55 | whole h3 15, h4 15, h5 25 | recorded by a harness-v1 run of this verifier | harness **v2** |
| `evidence/srk_decoys_cell/` | 32 | cell h3 16, h5 16 | recorded by a harness-v1 run of this verifier | harness **v2** |
| `evidence/srk_decoys_prelim/` (preliminary) | 20 | prelim h3 5, h5 15 | this verifier | harness **v1**, kept as history |

The genuine verdicts were produced with the same verifier file (sha above). `--remutate` reused each of them only when
the certificate sha256 matched.

### Genuine certificates

**107 of 107 are ACCEPTED**, with 0 REJECT and 0 REFUSE.

The "min certified LB" columns give the smallest certified cell lower bound over the accepted cover for (C2) and (C3).
They are conservative.

| file | idx | i | verdict | cells | max depth | sec | min certified LB (C2) | min certified LB (C3) |
|---|---|---|---|---|---|---|---|---|
| h3_k1_2_E1_2_17_32.json | 0 | 0 | ACCEPT | 132 | 0 | 0.7 | 2.34e-03 | 6.01e-03 |
| h3_k1_2_E1_2_17_32.json | 1 | 1 | ACCEPT | 132 | 0 | 0.8 | 2.34e-03 | 3.02e-04 |
| h3_k1_2_E1_2_17_32.json | 2 | 2 | ACCEPT | 159 | 4 | 2.3 | 2.63e-03 | 2.18e-04 |
| h3_k1_2_E1_2_17_32.json | 3 | 3 | ACCEPT | 183 | 4 | 1.7 | 2.63e-03 | 5.57e-04 |
| h3_k1_2_E1_2_17_32.json | 4 | 4 | ACCEPT | 195 | 4 | 2.5 | 2.63e-03 | 6.89e-04 |
| h3_k1_2_E1_33_32.json | 0 | 0 | ACCEPT | 132 | 0 | 2.1 | 1.62e-04 | 6.17e-03 |
| h3_k1_2_E1_33_32.json | 1 | 1 | ACCEPT | 150 | 3 | 1.5 | 1.59e-04 | 4.15e-04 |
| h3_k1_2_E1_33_32.json | 2 | 2 | ACCEPT | 231 | 7 | 3.6 | 1.62e-04 | 6.03e-05 |
| h3_k1_2_E1_33_32.json | 3 | 3 | ACCEPT | 196 | 6 | 2.1 | 1.59e-04 | 8.89e-05 |
| h3_k1_2_E1_33_32.json | 4 | 4 | ACCEPT | 253 | 7 | 4.3 | 1.62e-04 | 2.73e-04 |
| h3_k1_2_E1_4_9_32.json | 0 | 0 | ACCEPT | 132 | 0 | 0.7 | 7.70e-03 | 1.22e-02 |
| h3_k1_2_E1_4_9_32.json | 1 | 1 | ACCEPT | 132 | 0 | 0.7 | 7.70e-03 | 9.78e-03 |
| h3_k1_2_E1_4_9_32.json | 2 | 2 | ACCEPT | 134 | 1 | 0.9 | 7.70e-03 | 1.31e-03 |
| h3_k1_2_E1_4_9_32.json | 3 | 3 | ACCEPT | 167 | 4 | 2.6 | 8.25e-03 | 1.12e-04 |
| h3_k1_2_E1_4_9_32.json | 4 | 4 | ACCEPT | 175 | 4 | 3.1 | 8.25e-03 | 5.49e-04 |
| h4_k1_2_E1_2_17_32.json | 0 | 0 | ACCEPT | 258 | 0 | 1.1 | 4.18e-03 | 7.59e-03 |
| h4_k1_2_E1_2_17_32.json | 1 | 1 | ACCEPT | 258 | 0 | 1.3 | 4.18e-03 | 4.60e-03 |
| h4_k1_2_E1_2_17_32.json | 2 | 2 | ACCEPT | 276 | 3 | 2.0 | 5.07e-03 | 1.30e-03 |
| h4_k1_2_E1_2_17_32.json | 3 | 3 | ACCEPT | 291 | 5 | 3.1 | 5.18e-03 | 3.54e-04 |
| h4_k1_2_E1_2_17_32.json | 4 | 4 | ACCEPT | 300 | 5 | 3.4 | 5.18e-03 | 2.09e-04 |
| h4_k1_2_E1_33_32.json | 0 | 0 | ACCEPT | 258 | 0 | 1.7 | 2.68e-04 | 5.80e-03 |
| h4_k1_2_E1_33_32.json | 1 | 1 | ACCEPT | 269 | 3 | 2.5 | 3.06e-04 | 2.50e-05 |
| h4_k1_2_E1_33_32.json | 2 | 2 | ACCEPT | 319 | 5 | 3.7 | 3.06e-04 | 3.69e-05 |
| h4_k1_2_E1_33_32.json | 3 | 3 | ACCEPT | 296 | 4 | 2.3 | 2.68e-04 | 2.80e-04 |
| h4_k1_2_E1_33_32.json | 4 | 4 | ACCEPT | 362 | 7 | 4.7 | 3.06e-04 | 1.18e-04 |
| h4_k1_2_E1_4_9_32.json | 0 | 0 | ACCEPT | 258 | 0 | 1.2 | 2.06e-02 | 2.47e-02 |
| h4_k1_2_E1_4_9_32.json | 1 | 1 | ACCEPT | 258 | 0 | 1.1 | 2.06e-02 | 1.98e-02 |
| h4_k1_2_E1_4_9_32.json | 2 | 2 | ACCEPT | 258 | 0 | 1.6 | 2.46e-02 | 1.48e-02 |
| h4_k1_2_E1_4_9_32.json | 3 | 3 | ACCEPT | 260 | 2 | 1.6 | 2.46e-02 | 3.11e-02 |
| h4_k1_2_E1_4_9_32.json | 4 | 4 | ACCEPT | 266 | 3 | 2.9 | 2.46e-02 | 7.94e-03 |
| h5_k1_2_E0_1_32.json | 0 | 0 | ACCEPT | 432 | 0 | 2.7 | 6.76e-03 | 8.70e-03 |
| h5_k1_2_E0_1_32.json | 1 | 1 | ACCEPT | 432 | 0 | 2.5 | 6.76e-03 | 8.40e-03 |
| h5_k1_2_E0_1_32.json | 2 | 2 | ACCEPT | 432 | 0 | 2.4 | 6.76e-03 | 5.84e-03 |
| h5_k1_2_E0_1_32.json | 3 | 3 | ACCEPT | 432 | 0 | 3.8 | 3.91e-02 | 2.06e-02 |
| h5_k1_2_E0_1_32.json | 4 | 4 | ACCEPT | 434 | 2 | 4.3 | 3.91e-02 | 7.63e-03 |
| h5_k1_2_E1_2_17_32.json | 0 | 0 | ACCEPT | 432 | 0 | 2.4 | 7.68e-03 | 1.12e-02 |
| h5_k1_2_E1_2_17_32.json | 1 | 1 | ACCEPT | 432 | 0 | 2.7 | 7.68e-03 | 9.72e-03 |
| h5_k1_2_E1_2_17_32.json | 2 | 2 | ACCEPT | 433 | 1 | 3.1 | 7.68e-03 | 4.64e-03 |
| h5_k1_2_E1_2_17_32.json | 3 | 3 | ACCEPT | 442 | 3 | 4.1 | 8.80e-03 | 2.16e-03 |
| h5_k1_2_E1_2_17_32.json | 4 | 4 | ACCEPT | 448 | 3 | 3.0 | 7.68e-03 | 3.16e-03 |
| h5_k1_2_E1_33_32.json | 0 | 0 | ACCEPT | 432 | 0 | 3.7 | 4.36e-04 | 5.59e-03 |
| h5_k1_2_E1_33_32.json | 1 | 1 | ACCEPT | 451 | 3 | 4.0 | 4.36e-04 | 2.65e-05 |
| h5_k1_2_E1_33_32.json | 2 | 2 | ACCEPT | 502 | 6 | 4.8 | 4.36e-04 | 3.85e-05 |
| h5_k1_2_E1_33_32.json | 3 | 3 | ACCEPT | 481 | 5 | 4.3 | 4.36e-04 | 8.12e-05 |
| h5_k1_2_E1_33_32.json | 4 | 4 | ACCEPT | 513 | 8 | 5.4 | 4.36e-04 | 1.81e-04 |
| h5_k1_2_E1_4_9_32.json | 0 | 0 | ACCEPT | 432 | 0 | 1.9 | 5.41e-02 | 5.81e-02 |
| h5_k1_2_E1_4_9_32.json | 1 | 1 | ACCEPT | 432 | 0 | 1.8 | 5.41e-02 | 4.66e-02 |
| h5_k1_2_E1_4_9_32.json | 2 | 2 | ACCEPT | 432 | 0 | 2.5 | 6.08e-02 | 5.79e-02 |
| h5_k1_2_E1_4_9_32.json | 3 | 3 | ACCEPT | 432 | 0 | 2.6 | 6.08e-02 | 8.58e-02 |
| h5_k1_2_E1_4_9_32.json | 4 | 4 | ACCEPT | 432 | 0 | 2.6 | 6.08e-02 | 1.54e-01 |
| h5_k1_2_E1_8_5_32.json | 0 | 0 | ACCEPT | 432 | 0 | 2.5 | 1.68e-01 | 1.74e-01 |
| h5_k1_2_E1_8_5_32.json | 1 | 1 | ACCEPT | 432 | 0 | 2.8 | 1.68e-01 | 1.38e-01 |
| h5_k1_2_E1_8_5_32.json | 2 | 2 | ACCEPT | 432 | 0 | 2.4 | 1.68e-01 | 1.68e-01 |
| h5_k1_2_E1_8_5_32.json | 3 | 3 | ACCEPT | 432 | 0 | 2.6 | 1.68e-01 | 2.48e-01 |
| h5_k1_2_E1_8_5_32.json | 4 | 4 | ACCEPT | 432 | 0 | 4.1 | 1.72e-01 | 4.46e-01 |
| cell_h3_k1_2_C1_3_20_51_S0.json | 1 | 1 | ACCEPT | 132 | 0 | 2.0 | 1.39e-03 | 5.35e-03 |
| cell_h3_k1_2_C1_3_20_51_S0.json | 2 | 2 | ACCEPT | 155 | 4 | 1.5 | 1.38e-03 | 1.88e-04 |
| cell_h3_k1_2_C1_3_20_51_S0.json | 3 | 3 | ACCEPT | 174 | 5 | 2.0 | 1.38e-03 | 2.92e-04 |
| cell_h3_k1_2_C1_3_20_51_S0.json | 4 | 4 | ACCEPT | 198 | 5 | 4.1 | 1.39e-03 | 1.06e-03 |
| cell_h3_k1_2_C1_3_20_51_S1.json | 1 | 1 | ACCEPT | 132 | 0 | 2.5 | 1.30e-03 | 5.28e-03 |
| cell_h3_k1_2_C1_3_20_51_S1.json | 2 | 2 | ACCEPT | 155 | 4 | 1.7 | 1.30e-03 | 2.76e-04 |
| cell_h3_k1_2_C1_3_20_51_S1.json | 3 | 3 | ACCEPT | 174 | 5 | 2.0 | 1.30e-03 | 1.56e-05 |
| cell_h3_k1_2_C1_3_20_51_S1.json | 4 | 4 | ACCEPT | 198 | 5 | 4.1 | 1.30e-03 | 9.99e-04 |
| cell_h3_k1_2_C1_3_20_51_S2.json | 1 | 1 | ACCEPT | 132 | 0 | 1.9 | 1.21e-03 | 5.21e-03 |
| cell_h3_k1_2_C1_3_20_51_S2.json | 2 | 2 | ACCEPT | 155 | 4 | 1.4 | 1.21e-03 | 3.62e-04 |
| cell_h3_k1_2_C1_3_20_51_S2.json | 3 | 3 | ACCEPT | 175 | 5 | 1.8 | 1.21e-03 | 8.31e-05 |
| cell_h3_k1_2_C1_3_20_51_S2.json | 4 | 4 | ACCEPT | 198 | 5 | 3.8 | 1.21e-03 | 9.89e-04 |
| cell_h3_k1_2_C1_3_20_51_S3.json | 1 | 1 | ACCEPT | 132 | 0 | 1.9 | 1.13e-03 | 5.15e-03 |
| cell_h3_k1_2_C1_3_20_51_S3.json | 2 | 2 | ACCEPT | 155 | 4 | 1.7 | 1.13e-03 | 4.45e-04 |
| cell_h3_k1_2_C1_3_20_51_S3.json | 3 | 3 | ACCEPT | 175 | 5 | 2.0 | 1.13e-03 | 2.87e-05 |
| cell_h3_k1_2_C1_3_20_51_S3.json | 4 | 4 | ACCEPT | 198 | 5 | 4.3 | 1.13e-03 | 9.85e-04 |
| cell_h5_k1_2_C1_2_37_72_S0.json | 1 | 1 | ACCEPT | 434 | 1 | 4.2 | 5.41e-05 | 2.38e-03 |
| cell_h5_k1_2_C1_2_37_72_S0.json | 2 | 2 | ACCEPT | 450 | 3 | 4.3 | 5.41e-05 | 4.22e-04 |
| cell_h5_k1_2_C1_2_37_72_S0.json | 3 | 3 | ACCEPT | 459 | 4 | 4.2 | 5.41e-05 | 3.19e-04 |
| cell_h5_k1_2_C1_2_37_72_S0.json | 4 | 4 | ACCEPT | 462 | 3 | 4.0 | 5.41e-05 | 5.46e-04 |
| cell_h5_k1_2_C1_2_37_72_S1.json | 1 | 1 | ACCEPT | 434 | 1 | 3.8 | 5.02e-05 | 2.37e-03 |
| cell_h5_k1_2_C1_2_37_72_S1.json | 2 | 2 | ACCEPT | 450 | 3 | 4.1 | 5.02e-05 | 4.22e-04 |
| cell_h5_k1_2_C1_2_37_72_S1.json | 3 | 3 | ACCEPT | 459 | 4 | 4.0 | 5.02e-05 | 3.09e-04 |
| cell_h5_k1_2_C1_2_37_72_S1.json | 4 | 4 | ACCEPT | 462 | 3 | 4.4 | 5.02e-05 | 5.37e-04 |
| cell_h5_k1_2_C1_2_37_72_S2.json | 1 | 1 | ACCEPT | 434 | 1 | 3.9 | 4.64e-05 | 2.37e-03 |
| cell_h5_k1_2_C1_2_37_72_S2.json | 2 | 2 | ACCEPT | 450 | 3 | 4.0 | 4.64e-05 | 4.22e-04 |
| cell_h5_k1_2_C1_2_37_72_S2.json | 3 | 3 | ACCEPT | 459 | 4 | 4.1 | 4.64e-05 | 2.98e-04 |
| cell_h5_k1_2_C1_2_37_72_S2.json | 4 | 4 | ACCEPT | 462 | 3 | 4.0 | 4.64e-05 | 5.28e-04 |
| cell_h5_k1_2_C1_2_37_72_S3.json | 1 | 1 | ACCEPT | 434 | 1 | 3.7 | 4.27e-05 | 2.36e-03 |
| cell_h5_k1_2_C1_2_37_72_S3.json | 2 | 2 | ACCEPT | 450 | 3 | 4.0 | 4.27e-05 | 4.22e-04 |
| cell_h5_k1_2_C1_2_37_72_S3.json | 3 | 3 | ACCEPT | 459 | 4 | 4.2 | 4.27e-05 | 2.87e-04 |
| cell_h5_k1_2_C1_2_37_72_S3.json | 4 | 4 | ACCEPT | 462 | 3 | 4.2 | 4.27e-05 | 5.19e-04 |
| h3_k1_2_E1_4_9_32.json | 0 | 0 | ACCEPT | 132 | 0 | 0.8 | 7.70e-03 | 1.22e-02 |
| h3_k1_2_E1_4_9_32.json | 1 | 1 | ACCEPT | 132 | 0 | 0.7 | 7.70e-03 | 9.78e-03 |
| h3_k1_2_E1_4_9_32.json | 2 | 2 | ACCEPT | 134 | 1 | 0.8 | 7.70e-03 | 1.31e-03 |
| h3_k1_2_E1_4_9_32.json | 3 | 3 | ACCEPT | 167 | 4 | 2.7 | 8.25e-03 | 1.12e-04 |
| h3_k1_2_E1_4_9_32.json | 4 | 4 | ACCEPT | 175 | 4 | 2.8 | 8.25e-03 | 5.49e-04 |
| h5_k1_2_E1_2_17_32.json | 0 | 0 | ACCEPT | 432 | 0 | 2.6 | 7.68e-03 | 1.12e-02 |
| h5_k1_2_E1_2_17_32.json | 1 | 1 | ACCEPT | 432 | 0 | 2.6 | 7.68e-03 | 9.72e-03 |
| h5_k1_2_E1_2_17_32.json | 2 | 2 | ACCEPT | 433 | 1 | 2.6 | 7.68e-03 | 4.64e-03 |
| h5_k1_2_E1_2_17_32.json | 3 | 3 | ACCEPT | 442 | 3 | 4.1 | 8.80e-03 | 2.16e-03 |
| h5_k1_2_E1_2_17_32.json | 4 | 4 | ACCEPT | 448 | 3 | 2.8 | 7.68e-03 | 3.16e-03 |
| h5_k1_2_E1_4_9_32.json | 0 | 0 | ACCEPT | 432 | 0 | 1.9 | 5.41e-02 | 5.81e-02 |
| h5_k1_2_E1_4_9_32.json | 1 | 1 | ACCEPT | 432 | 0 | 1.6 | 5.41e-02 | 4.66e-02 |
| h5_k1_2_E1_4_9_32.json | 2 | 2 | ACCEPT | 432 | 0 | 2.5 | 6.08e-02 | 5.79e-02 |
| h5_k1_2_E1_4_9_32.json | 3 | 3 | ACCEPT | 432 | 0 | 2.4 | 6.08e-02 | 8.58e-02 |
| h5_k1_2_E1_4_9_32.json | 4 | 4 | ACCEPT | 432 | 0 | 2.5 | 6.08e-02 | 1.54e-01 |
| h5_k1_2_E1_8_5_32.json | 0 | 0 | ACCEPT | 432 | 0 | 2.5 | 1.68e-01 | 1.74e-01 |
| h5_k1_2_E1_8_5_32.json | 1 | 1 | ACCEPT | 432 | 0 | 2.7 | 1.68e-01 | 1.38e-01 |
| h5_k1_2_E1_8_5_32.json | 2 | 2 | ACCEPT | 432 | 0 | 2.6 | 1.68e-01 | 1.68e-01 |
| h5_k1_2_E1_8_5_32.json | 3 | 3 | ACCEPT | 432 | 0 | 2.5 | 1.68e-01 | 2.48e-01 |
| h5_k1_2_E1_8_5_32.json | 4 | 4 | ACCEPT | 432 | 0 | 3.7 | 1.72e-01 | 4.46e-01 |

### Harness v2: review R2 condition C3 (reason-specific, single-defect mutants)

**Finding (R2 C3, confirmed).** Harness v1 checked mutant expectations by verdict only. On the rerun certificates,
which carry an explicit `weight_block` and a file-level `kernel` key, three item-7 probes were refused for a reason
other than their own defect. The verifier itself was not implicated.

| probe | v1 result on the 87 rerun certificates | cause |
|---|---|---|
| **7q** quarantine band | REFUSE "weight_block does not contain block" (all 41 real-kernel h5: 25 whole, 16 cell) | `block` was moved into the band, `weight_block` was not |
| **7f** unknown kernel | REFUSE "kernel key conflicts with the file-level kernel key" (all 87) | the file-level `kernel` key triggered the conflict check first |
| **7h** non-dyadic drift | REFUSE "weight_block does not contain block" (all 87) | the block was shifted, `weight_block` was not |

The v1 probes 1–6, 7a–7e and 7g had the correct reason in every class. Only the 20 preliminary certificates, which
have no `weight_block` or file-level `kernel`, exercised 7q, 7f and 7h as intended under v1.

**Fix (v2, in `run_verify_all.py` only; `srk_verify_indep.py` is untouched):**
* Every mutant has exactly one defect:
  * **7q** moves `weight_block` together with `block`, so the band is the only defect;
  * **7h** shifts both by −1/3 (or +1/3), chosen by exact rational comparison so as never to enter a quarantine band;
  * **7f** runs as a bare certificate;
  * a new probe **7i** tests the kernel conflict on its own.
* Every expectation is reason-specific:
  * (C4), sha256 and each REFUSE message are matched exactly;
  * "claim" rejections must be a (C1)–(C3) FALSE or UNPROVEN;
  * "proved or claim" allows an ACCEPT, which is a completed proof of a true mutated claim.
* Every mutant result records `harness_version`, `harness_sha256` and `verifier_sha256`.
* v1 results carry `harness_version: v1` and the v1 sha.

The 7q probe is a **parse-time refusal**: the verifier refuses it before any evaluation, so nothing is evaluated at
band drifts. No real-kernel run anywhere in these batteries used drifts in [6/5, 13/5] or its mirror.

**Outcomes of the item-7 probes that were masked (v2 on the rerun certificates; v1 preliminary rows for comparison):**

| probe | harness | class | n | outcome | expectation met |
|---|---|---|---|---|---|
| 7f | v1 | prelim h3 | 5 | REFUSE (unknown kernel) | yes |
| 7f | v1 | prelim h5 | 15 | REFUSE (unknown kernel) | yes |
| 7f | v2 | cell h3 | 16 | REFUSE (unknown kernel) | yes |
| 7f | v2 | cell h5 | 16 | REFUSE (unknown kernel) | yes |
| 7f | v2 | whole h3 | 15 | REFUSE (unknown kernel) | yes |
| 7f | v2 | whole h4 | 15 | REFUSE (unknown kernel) | yes |
| 7f | v2 | whole h5 | 25 | REFUSE (unknown kernel) | yes |
| 7h | v1 | prelim h3 | 5 | processed: REJECT (disproved) | yes |
| 7h | v1 | prelim h5 | 15 | processed: REJECT (disproved) | yes |
| 7h | v2 | cell h3 | 16 | processed: REJECT (disproved) | yes |
| 7h | v2 | cell h5 | 16 | processed: REJECT (disproved) | yes |
| 7h | v2 | whole h3 | 15 | processed: REJECT (disproved) | yes |
| 7h | v2 | whole h4 | 15 | processed: REJECT (disproved) | yes |
| 7h | v2 | whole h5 | 20 | processed: REJECT (disproved) | yes |
| 7h | v2 | whole h5 | 5 | processed: REJECT (unproven at depth 6) | yes |
| 7i | v2 | cell h3 | 16 | REFUSE (kernel conflicts with file key) | yes |
| 7i | v2 | cell h5 | 16 | REFUSE (kernel conflicts with file key) | yes |
| 7i | v2 | whole h3 | 15 | REFUSE (kernel conflicts with file key) | yes |
| 7i | v2 | whole h4 | 15 | REFUSE (kernel conflicts with file key) | yes |
| 7i | v2 | whole h5 | 25 | REFUSE (kernel conflicts with file key) | yes |
| 7q | v1 | prelim h5 | 15 | REFUSE (quarantine band) | yes |
| 7q | v2 | cell h5 | 16 | REFUSE (quarantine band) | yes |
| 7q | v2 | whole h5 | 25 | REFUSE (quarantine band) | yes |

The 7q probe exists only for the frozen real geometry (h, k) = (5, 1/2), which is the only one the quarantine band
applies to. The h3 and h4 classes therefore have no 7q probe.

### Mutant summary

* **Harness v2** (all 87 rerun certificates, `srk_decoys` + `srk_decoys_cell`):
  * 1868 mutant runs, **1868 expectations met, 0 unmet**;
  * 98 mutated claims PROVED TRUE (mutant 2 under SE-1; mutant 4 with Gamma recomputed where the widened claim is
    true; mutant 5 where the weight gets smaller);
  * 7 claim rejections ended UNPROVEN rather than disproved (allowed by the expectation, reported as undetermined):
    * `h5_k1_2_E0_1_32.json` #0 7h_non_dyadic_drift (processed, no crash): C2 UNPROVEN at depth limit: certified lower bound -4.087856e-03 ()
    * `h5_k1_2_E0_1_32.json` #1 7h_non_dyadic_drift (processed, no crash): C2 UNPROVEN at depth limit: certified lower bound -4.087856e-03 ()
    * `h5_k1_2_E0_1_32.json` #2 7h_non_dyadic_drift (processed, no crash): C2 UNPROVEN at depth limit: certified lower bound -4.087856e-03 ()
    * `h5_k1_2_E0_1_32.json` #3 7h_non_dyadic_drift (processed, no crash): C2 UNPROVEN at depth limit: certified lower bound -5.269901e-03 ()
    * `h5_k1_2_E0_1_32.json` #4 7h_non_dyadic_drift (processed, no crash): C2 UNPROVEN at depth limit: certified lower bound -5.269901e-03 ()
    * `h5_k1_2_E1_33_32.json` #4 2_V0_scaled_1-2^-8: C3 UNPROVEN at depth limit: certified lower bound -2.162263e-07 (pts=1 delta=0.00e+00)
    * `cell_h3_k1_2_C1_3_20_51_S2.json` #4 3_V0_minus_lam_W0: C3 UNPROVEN at depth limit: certified lower bound -6.371945e-08 (pts=1 delta=0.00e+00)
    * The 7h cases are intentional: item-7 probes run with depth limit 6, and 7h only checks that a non-dyadic drift
      is processed.
    * The other two are near-tight mutated claims, with lower bound about −1e-7 at depth 24.
* **Harness v1** (the 20 preliminary certificates, kept as history): 415 runs, 415 met. Their 7q, 7f and 7h probes had
  the correct reasons (table above).

### Mutant outcome table (all certificates, by harness version)

| mutant | harness | runs | expectation met | ACCEPT(proved true) | REJECT(disproved) | REJECT(C4/sha) | REJECT(unproven) | REFUSE | other |
|---|---|---|---|---|---|---|---|---|---|
| 1_gamma_minus_1e-6 | v1 | 20 | 20 | 0 | 0 | 20 | 0 | 0 | 0 |
| 2_V0_scaled_1-2^-8 | v1 | 20 | 20 | 20 | 0 | 0 | 0 | 0 | 0 |
| 2x_V0_scaled_3/4 (SE-1 mandatory) | v1 | 20 | 20 | 0 | 20 | 0 | 0 | 0 | 0 |
| 3_V0_minus_lam_W0 | v1 | 20 | 20 | 0 | 20 | 0 | 0 | 0 | 0 |
| 4B_block_widened_1/8 | v1 | 20 | 20 | 0 | 0 | 20 | 0 | 0 | 0 |
| 4B_block_widened_1/8+Gamma_recomputed | v1 | 20 | 20 | 0 | 20 | 0 | 0 | 0 | 0 |
| 4L_block_widened_1/8 | v1 | 20 | 20 | 0 | 0 | 20 | 0 | 0 | 0 |
| 4L_block_widened_1/8+Gamma_recomputed | v1 | 20 | 20 | 0 | 20 | 0 | 0 | 0 | 0 |
| 4R_block_widened_1/8 | v1 | 20 | 20 | 0 | 0 | 20 | 0 | 0 | 0 |
| 4R_block_widened_1/8+Gamma_recomputed | v1 | 20 | 20 | 0 | 20 | 0 | 0 | 0 | 0 |
| 5_hermite_index_plus_1 | v1 | 20 | 20 | 4 | 16 | 0 | 0 | 0 | 0 |
| 6_sha256_altered | v1 | 20 | 20 | 0 | 0 | 20 | 0 | 0 | 0 |
| 7a_missing_key_W1 | v1 | 20 | 20 | 0 | 0 | 0 | 0 | 20 | 0 |
| 7b_non_rational_string | v1 | 20 | 20 | 0 | 0 | 0 | 0 | 20 | 0 |
| 7c_e_lo_gt_e_hi | v1 | 20 | 20 | 0 | 0 | 0 | 0 | 20 | 0 |
| 7d_garbage_block | v1 | 20 | 20 | 0 | 0 | 0 | 0 | 20 | 0 |
| 7e_weight_block_not_containing_block | v1 | 20 | 20 | 0 | 0 | 0 | 0 | 20 | 0 |
| 7f_unknown_kernel | v1 | 20 | 20 | 0 | 0 | 0 | 0 | 20 | 0 |
| 7g_e_c_not_midpoint | v1 | 20 | 20 | 0 | 0 | 0 | 0 | 20 | 0 |
| 7h_non_dyadic_drift (processed, no crash) | v1 | 20 | 20 | 0 | 20 | 0 | 0 | 0 | 0 |
| 7q_quarantine_band_refused | v1 | 15 | 15 | 0 | 0 | 0 | 0 | 15 | 0 |
| 1_gamma_minus_1e-6 | v2 | 87 | 87 | 0 | 0 | 87 | 0 | 0 | 0 |
| 2_V0_scaled_1-2^-8 | v2 | 87 | 87 | 86 | 0 | 0 | 1 | 0 | 0 |
| 2x_V0_scaled_3/4 (SE-1 mandatory) | v2 | 87 | 87 | 0 | 87 | 0 | 0 | 0 | 0 |
| 3_V0_minus_lam_W0 | v2 | 87 | 87 | 0 | 86 | 0 | 1 | 0 | 0 |
| 4B_block_widened_1/8 | v2 | 87 | 87 | 0 | 0 | 87 | 0 | 0 | 0 |
| 4B_block_widened_1/8+Gamma_recomputed | v2 | 87 | 87 | 0 | 87 | 0 | 0 | 0 | 0 |
| 4L_block_widened_1/8 | v2 | 87 | 87 | 0 | 0 | 87 | 0 | 0 | 0 |
| 4L_block_widened_1/8+Gamma_recomputed | v2 | 87 | 87 | 0 | 87 | 0 | 0 | 0 | 0 |
| 4R_block_widened_1/8 | v2 | 87 | 87 | 0 | 0 | 87 | 0 | 0 | 0 |
| 4R_block_widened_1/8+Gamma_recomputed | v2 | 87 | 87 | 4 | 83 | 0 | 0 | 0 | 0 |
| 5_hermite_index_plus_1 | v2 | 87 | 87 | 8 | 79 | 0 | 0 | 0 | 0 |
| 6_sha256_altered | v2 | 87 | 87 | 0 | 0 | 87 | 0 | 0 | 0 |
| 7a_missing_key_W1 | v2 | 87 | 87 | 0 | 0 | 0 | 0 | 87 | 0 |
| 7b_non_rational_string | v2 | 87 | 87 | 0 | 0 | 0 | 0 | 87 | 0 |
| 7c_e_lo_gt_e_hi | v2 | 87 | 87 | 0 | 0 | 0 | 0 | 87 | 0 |
| 7d_garbage_block | v2 | 87 | 87 | 0 | 0 | 0 | 0 | 87 | 0 |
| 7e_weight_block_not_containing_block | v2 | 87 | 87 | 0 | 0 | 0 | 0 | 87 | 0 |
| 7f_unknown_kernel (bare certificate) | v2 | 87 | 87 | 0 | 0 | 0 | 0 | 87 | 0 |
| 7g_e_c_not_midpoint | v2 | 87 | 87 | 0 | 0 | 0 | 0 | 87 | 0 |
| 7h_non_dyadic_drift (processed, no crash) | v2 | 87 | 87 | 0 | 82 | 0 | 5 | 0 | 0 |
| 7i_kernel_conflicts_with_file_kernel | v2 | 87 | 87 | 0 | 0 | 0 | 0 | 87 | 0 |
| 7q_quarantine_band_refused | v2 | 41 | 41 | 0 | 0 | 0 | 0 | 41 | 0 |

### Unit self-tests

`tests/test_verify_selftests.py` (sha256 `8357be8539ed408b449c486387907b9dd3e0df03ccf0c846fec18ccfae48e2c3`) was run on the **current inputs** at 2026-09-29T23:45Z: **21 tests, all OK** (40 s). It was
recorded with `python3 verify/run_verify_all.py --unit-tests --no-mutants` in `VERIFY_RESULTS.json` (`unit_selftests`).
`TestRequiredRejections` uses `evidence/srk_decoys/h5_k1_2_E0_1_32.json` #1, which has an explicit `weight_block` and a
certificate-level `kernel`.

Per-test outcome:
* `TestGaussianEnclosures.test_G_value_vs_quadrature`: ok
* `TestGaussianEnclosures.test_Phi_monotone_consistent`: ok
* `TestGaussianEnclosures.test_absHephi_bounds_contain_samples`: ok
* `TestGaussianEnclosures.test_he_roots`: ok
* `TestGaussianEnclosures.test_phi_Phi_contain_math`: ok
* `TestGaussianEnclosures.test_pi`: ok
* `TestKernelClosedForm.test_closed_form_vs_quadrature`: ok
* `TestRequiredRejections.test_0_genuine_accepted`: ok
* `TestRequiredRejections.test_0b_taboo_positive_control`: ok
* `TestRequiredRejections.test_1_gamma`: ok
* `TestRequiredRejections.test_2_scaled_V0`: ok
* `TestRequiredRejections.test_3_drop_lambda`: ok
* `TestRequiredRejections.test_4_widened_block`: ok
* `TestRequiredRejections.test_5_hermite_plus_one`: ok
* `TestRequiredRejections.test_6_sha`: ok
* `TestRequiredRejections.test_7_malformed`: ok
* `TestRequiredRejections.test_7_non_dyadic_drift_no_crash`: ok
* `TestRequiredRejections.test_quarantine_refused`: ok
* `TestRequiredRejections.test_weight_block_is_used`: ok
* `TestTaylorModels.test_containment`: ok
* `TestTaylorModels.test_lower_bound_below_samples`: ok

**Revision for review R2 condition C3.** The fix is the same as harness v2: each probe has a single defect, and every
assertion is reason-specific.
* **The two tests that failed on the rerun inputs:**
  * `test_quarantine_refused` now moves `weight_block` together with `block`. It must be refused with a reason starting
    `quarantine:` and containing "nothing evaluated". It is a parse-time refusal.
  * `test_7_non_dyadic_drift_no_crash` shifts `block` and `weight_block` together by −1/3 (or +1/3, chosen by exact
    rational comparison so as never to meet a quarantine band). It must be *processed*: ACCEPT, or REJECT with a
    (C1)–(C3) reason, not refused. It also checks that the shifted block is the one verified.
* **Two more tests that would have failed loudly on the rerun inputs:**
  * `test_4_widened_block` now keeps `weight_block` containing the widened block.
  * `test_0b_taboo_positive_control` sets `kernel: taboo` in the certificate and runs it as a bare certificate. Before,
    a file-level `taboo` conflicted with the certificate's `kernel: whole`.
* **Tests that passed but checked only the verdict now check the reason:**
  * `test_1_gamma`: (C4);
  * `test_2_scaled_V0` and `test_3_drop_lambda`: a (C1)–(C3) claim failure;
  * `test_5_hermite_plus_one`: a claim failure, when rejected;
  * `test_6_sha`: exactly "sha256 mismatch";
  * `test_7_malformed`: each of its 7 probes against its own message; the unknown-kernel probe runs bare;
  * `test_weight_block_is_used`: a C3 claim failure, with the weight-block hull built to stay out of the band.

### Taboo-kernel certificates

The `kernel: taboo` path (certificate- or file-level key) is implemented and tested: closed form against quadrature,
plus a positive control. No taboo decoy file existed at the time of this run.
