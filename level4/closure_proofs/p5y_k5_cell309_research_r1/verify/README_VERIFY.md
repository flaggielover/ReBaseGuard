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

    python3 verify/srk_verify_indep.py CERT.json [--index I] [--max-depth 14] [--order 8] [--procs 1] [--json OUT]
    python3 verify/run_verify_all.py      # all decoy files + section 5 mutants -> verify/VERIFY_RESULTS.json
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
   * A failing cell is bisected along its widest dimension, down to `--max-depth` (default 14).
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
* A REJECT that is not a disproof can be a method limitation. The limits are the depth (default 14) and the Taylor
  order (8).
* The disproof is only attempted at a few points per failing cell.
* Polynomial degree is limited to ≤ 24 by the parser; the decoys use 8–12.
* The verifier checks the certificate claims only. It does not re-derive Lemma SV′ or the use of Γ in
  `srk_assemble.py`.

## Results

(See the tables below, generated from `verify/VERIFY_RESULTS.json` by `verify/results_table.py`.)
