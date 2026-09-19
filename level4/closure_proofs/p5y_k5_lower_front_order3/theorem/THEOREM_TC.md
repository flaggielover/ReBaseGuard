# Theorem TC — Taylor-cell, atom-deflated whole-cell enclosure of R''_m

Status: written before any certified or real computation of this campaign. It uses no value of R or of any derivative
of R. Notation: `THEOREM_AD.md` of `p5y_k5_perron_deflated_resolvent` (adopted at 7cb01e38): X the reachable closure,
B(X) with the sup norm, a = x0 = (0,0), K_e the frozen CUSUM kernel, R_e = (I − K_e)⁻¹, K_i(e) = ∂_e^i K_e.

## 1. Setting

Fix a frozen K1 cell C = [e0 − ρ, e0 + ρ] and r ∈ {0,…,4}. Let S(e) := S_r(e) be the TRUE source (S_0 the closed form
φ(u+e) − φ(l+e); S_r = J_e h_r for r ≥ 1) and F(e) := F_r(e) = R_e S(e). Let F̂, D̂, Ĥ, Ĝ ∈ B(X) be four FIXED functions
(state-only polynomials: the frozen K1 candidates for F_r, F_r', F_r'' at e0 and the frozen order-3 producer's candidate
G_r for F_r''' at e0). Define the Taylor candidate, t := e − e0,

    F̃(e) := F̂ + t D̂ + (t²/2) Ĥ + (t³/6) Ĝ,          φ(e) := S(e) − (I − K_e) F̃(e).

## 2. Premises (each is an adopted/frozen certificate or a frozen rule)

- **(P1) regularity.** e ↦ K_e is real-analytic into bounded operators on B(X) with ‖K_i(e)‖ ≤ k_i on C (Lemma K of
  theorem AD; the frozen drift-aware norms `cert.norms["k"]`, valid on the cell — the same bounds the frozen K1 and
  order-3 residual envelopes use). e ↦ S(e) is real-analytic into B(X) (closed form for r = 0; S_r = J_e h_r,
  h_r = K_e^{r−1} h_1 for r ≥ 1).
- **(P2) midpoint residuals.** With the frozen DAG residual equations at e0 (the exact premises of the frozen error
  algebra and of the order-3 producer's `rung3_residual.g_residual`):

      ‖φ(e0)‖    ≤ f_F := δ_mid(F_r)  + ε_mid(src(r,0))
      ‖φ'(e0)‖   ≤ f_D := δ_mid(dF_r) + ε_mid(src(r,1))
      ‖φ''(e0)‖  ≤ f_H := δ_mid(H_r)  + ε_mid(src(r,2))
      ‖φ'''(e0)‖ ≤ f_G := δ_mid(G_r)  + ε_mid(src(r,3))

  where src(0,k) = Sclosed:k, src(r,k) = S:r:k (r ≥ 1), δ_mid are the certified midpoint residual bounds
  (reachable-set Bernstein range + frozen truncation allowances) and ε_mid(src) the certified midpoint source-node errors
  (frozen midpoint DAG for k ≤ 2, Aux3 `midpoint_order3_eps` for k = 3).
  *Why these are φ⁽ʲ⁾(e0):* φ(e0) = −[(I−K)F̂ − Ŝ] + (S − Ŝ); φ'(e0) = −[(I−K)D̂ − K_1F̂ − Ŝ'] + (S' − Ŝ');
  φ''(e0) = −[(I−K)Ĥ − K_2F̂ − 2K_1D̂ − Ŝ''] + (S'' − Ŝ''); φ'''(e0) = −[(I−K)Ĝ − K_3F̂ − 3K_2D̂ − 3K_1Ĥ − Ŝ'''] + (S''' − Ŝ''')
  (all operators at e0; Leibniz, candidates fixed). The bracketed terms are exactly the certified residuals of the frozen
  F_r, dF_r, H_r and G_r equations.
- **(P3) fourth-derivative envelope.** For every e ∈ C,

      ‖φ⁗(e)‖ ≤ Env4 := σ4 + 4k_1 s_G + 6k_2 (s_H + ρ s_G) + 4k_3 (s_D + ρ s_H + ρ² s_G/2)
                        + k_4 (s_F + ρ s_D + ρ² s_H/2 + ρ³ s_G/6),

  where s_X ≥ ‖X̂‖ are certified candidate suprema on X and σ4 ≥ sup_C ‖S⁗(e)‖.
  *Proof:* (I − K_e)F̃(e) differentiated four times, F̃⁗ = 0, gives φ⁗ = S⁗ + Σ_{i=1..4} C(4,i) K_i(e) F̃⁽⁴⁻ⁱ⁾(e) with
  F̃''' = Ĝ, F̃'' = Ĥ + tĜ, F̃' = D̂ + tĤ + t²Ĝ/2, F̃ = F̂ + tD̂ + t²Ĥ/2 + t³Ĝ/6 and |t| ≤ ρ.
  σ4: r = 0: the frozen drift-aware closed-form bound `order2.sup_source_derivative_on(4, left, right)`. r ≥ 1:
  S_r⁗ = Σ_{i=0..4} C(4,i) J_i(e) h_r⁽⁴⁻ⁱ⁾(e) with ‖J_i(e)‖ ≤ j_i (frozen `cert.norms["j"]`), and the true-object
  tower ‖h_1‖ ≤ 1, ‖h_1⁽ⁿ⁾‖ ≤ sup_C‖S_0⁽ⁿ⁻¹⁾‖ (h_1' = −S_0 exactly), ‖h_j‖ ≤ 1, ‖h_j⁽ⁿ⁾‖ ≤ Σ_i C(n,i) k_i ‖h_{j−1}⁽ⁿ⁻ⁱ⁾‖.
- **(P4) atom constants.** A0, A1, A2 of theorem AD (Lemma Dv'), from the adopted certified registry r1 (sha 1b7f5da7…)
  with the adopted block rule (`deflated_consume.block_for`, r2 rule) and `atom_constants_r2`, valid at every e ∈ C.

## 3. Statement

For every e ∈ C:

    ‖φ(e)‖   ≤ p0 := f_F + ρ f_D + ρ² f_H/2 + ρ³ f_G/6 + ρ⁴ Env4/24
    ‖φ'(e)‖  ≤ p1 := f_D + ρ f_H + ρ² f_G/2 + ρ³ Env4/6
    ‖φ''(e)‖ ≤ p2 := f_H + ρ f_G + ρ² Env4/2

and

    |F_r''(e)(a) − Ĥ(a) − (e − e0) Ĝ(a)|  ≤  rad_r := A0·p2 + 2·A1·p1 + A2·p0.

Consequently, with the frozen assembly coefficients c(m) (F_r: 1/m, r < m; W_(r,t−r−1): 1/t − 1/m, 1 ≤ t < m) and the
frozen whole-cell W-enclosures W_(r,j)''(C)(a) ∈ 𝒲_(r,j) (origin ± cellwise node, exactly as the frozen
`propagate.enclosures` builds them),

    R''_m(e) ∈ 𝓗_m := Σ_{r<m} (1/m)·[Ĥ_r(a) − ρ|Ĝ_r(a)| − rad_r ,  Ĥ_r(a) + ρ|Ĝ_r(a)| + rad_r]  +  Σ c·𝒲_(r,j)

for every e ∈ C, and 𝓗_m ∩ H_adopted (the adopted Perron-deflated whole-cell enclosure) is a valid K5-B input.

## 4. Proof

1. φ is C⁴ (indeed analytic) from (P1). Taylor's theorem with integral remainder in the Banach space B(X), expanded at
   e0 to order 3 for φ, to order 2 for φ', to order 1 for φ'', with |t| ≤ ρ and (P2), (P3), gives p0, p1, p2
   (e.g. φ''(e) = φ''(e0) + tφ'''(e0) + ∫_{e0}^{e}(e − s)φ⁗(s)ds).
2. Put E(e) := F(e) − F̃(e). Since (I − K_e)F(e) = S(e), (I − K_e)E(e) = φ(e) for every e. Differentiating (K_e, E
   analytic): (I − K)E' = φ' + K_1E; (I − K)E'' = φ'' + 2K_1E' + K_2E. Hence E = Rφ, E' = Rφ' + (∂R)φ,
   E'' = Rφ'' + 2(∂R)φ' + (∂²R)φ with ∂R = RK_1R, ∂²R = 2RK_1RK_1R + RK_2R — exactly the identities of theorem AD §5
   with (φ_F, φ_D, φ_H) replaced by (φ, φ', φ'').
3. Evaluate at a with Lemma SM(c) and Lemma Dv/Dv' (theorem AD): |E''(e)(a)| ≤ A0‖φ''(e)‖ + 2A1‖φ'(e)‖ + A2‖φ(e)‖ ≤ rad_r.
   E''(e) = F''(e) − Ĥ − tĜ. This is the second claim.
4. |t| ≤ ρ gives the interval for F_r''(e)(a). R''_m is the frozen linear combination (IMPLEMENTATION_MAP assembly) of
   the F_r''(e)(a) and W''(e)(a) with nonnegative coefficients; interval sums of valid enclosures are valid. The
   intersection of two valid enclosures of the same set of values is valid (and a nonempty check is enforced). ∎

## 5. What is new and what is reused

- New: the Taylor candidate F̃ (the adopted AD bound used the e-constant candidate, whose whole-cell residual is
  δ_mid + ρ·Env and dominated the radius), and one order-3 candidate Ĝ per (cell, r) with its certified midpoint residual.
- Reused unchanged: theorem AD's error identities and A-constants; the frozen K1 candidates/residuals/norms; Aux3's
  order-3 source evidence; the order-3 producer's G_r candidate and residual rule; the frozen W enclosures and assembly.
- Not claimed: nothing about R, R' or R''' values beyond this enclosure; no whole-function sup norm is improved.

## 6. Consumption rule (pre-registered)

For each pre-registered cell k and each m: H_k ← H_k ∩ 𝓗_m(k) (refuse if empty), M_k ← min(M_k, mag(H_k)). Every other
input is the adopted Perron-deflated state (records, theorem-AD tightening with registry r1, T-EXT C1/C2 channel) composed
exactly as the adopted consumer does. Then the frozen `k5b_literal` for each m on cells 0..309; a cell passes iff the
frozen theorem says so. The empty-TC composition must reproduce the adopted consumption byte-identically (rows sha and
pass ranges), otherwise refuse.
