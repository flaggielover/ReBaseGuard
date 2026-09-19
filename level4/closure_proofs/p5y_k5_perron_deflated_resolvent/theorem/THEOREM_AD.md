# Theorem AD — atom-regenerative (rank-one) deflation of the CUSUM resolvent, and deflated K1 error propagation

Status: DRAFT r1, written before any front-cell forecast. It uses no value of R or of any derivative of R.
Notation follows `OPERATOR_AUDIT.md`. X is the reachable closure, B(X) the bounded functions with the sup norm,
a = (0,0) = x0 the evaluation point, e real.

## 0. Why not the spectral projection

The request was to decompose (I − K_e)⁻¹ into a Perron part and a stable complement. The natural spectral form
P_e = r_e ⊗ ℓ_e / ℓ_e(r_e), (I − K)⁻¹ = P/(1 − λ) + (I − K)⁻¹(I − P) is valid for a simple isolated eigenvalue, but
certifying it for this infinite-dimensional operator needs (i) an enclosed eigenpair with a certified gap and (ii) a
norm bound on a complement operator that is *not positive*, so no supersolution argument applies; and every e-derivative
brings P_e', λ_e', r_e', ℓ_e'. The kernel has a better structure: an atom at the evaluation point. Splitting the atom off
is an *exact rank-one* decomposition with a *positive* complement and an *e-independent* left functional. It is the
regenerative (Nummelin-splitting) form of Perron deflation. Everything below uses it; λ_e is never needed.

## 1. Lemma K (kernel structure)

For every e ∈ ℝ, exactly, K_e = K̂_e + k_{a,e} ⊗ δ_a with K̂_e ≥ 0, k_{a,e} ≥ 0 as in the audit, and

    k_{a,e} + h_{1,e} + K̂_e 1 = 1,     h_{1,e} = 1 − K_e 1 (one-step alarm probability) > 0.

e ↦ K̂_e, K_e, k_{a,e} are real-analytic into bounded operators / B(X), with
‖∂_e^n K̂_e‖ ≤ ‖∂_e^n K_e‖ ≤ κ_n := E|He_n(Y)|, Y ~ N(0,1); κ₁ = √(2/π) < 0.7978846, κ₂ = 4φ(1) < 0.9678830.

*Proof.* T(x, z) = a iff z ∈ [β, α] = [m − k, k − p]; on that set f(T(x,z)) = f(a), and [β, α] ⊂ (m − c, c − p). Mass
balance: integrate 1 over the window. The weight is φ(z+e); ∂_e^n φ(z+e) = (−1)^n He_n(z+e) φ(z+e), so
|(∂_e^n K̂_e f)(x)| ≤ ‖f‖ ∫ |He_n(y)| φ(y) dy (the window and the atom window are e-free). Analyticity: φ(·+e) is entire
and the L¹ norm of its Taylor remainder in e tends to 0 locally uniformly, which gives operator-norm convergence of the
series. E|Y| = √(2/π); E|Y² − 1| = 2 E[(1 − Y²); |Y| < 1] = 4φ(1). ∎

## 2. Lemma T (taboo resolvent by supersolution)

Let e ∈ E (a set of drifts). If w ∈ B(X) satisfies w ≥ 1 + K̂_e w on X for every e ∈ E, then for every e ∈ E:
Ĝ_e := (I − K̂_e)⁻¹ = Σ_j K̂_e^j exists in operator norm, Ĝ_e ≥ 0,

    ‖Ĝ_e‖ = ‖Ĝ_e 1‖ ≤ C_T := sup_X w,    τ_a(e) := (Ĝ_e 1)(a) ≤ w(a),    r(K̂_e) ≤ θ := 1 − 1/C_T.

*Proof.* w ≥ 1, so K̂w ≤ w − 1 ≤ θw; by positivity K̂^j 1 ≤ K̂^j w ≤ θ^j w, hence ‖K̂^j‖ = ‖K̂^j 1‖ ≤ θ^j C_T and the
series converges. Induction: Σ_{j<n} K̂^j 1 ≤ w (true for n = 0; Σ_{j<n+1} K̂^j 1 = 1 + K̂ Σ_{j<n} K̂^j 1 ≤ 1 + K̂w ≤ w). ∎

Probabilistically Ĝ_e 1(x) = E_x[τ ∧ T_a], T_a = inf{t ≥ 1 : X_t = a}. (Not used in any proof.)

## 3. Lemma SM (Sherman–Morrison at the atom)

Assume Ĝ_e exists. Put h_e := Ĝ_e k_{a,e}, ν_e(f) := (Ĝ_e f)(a), p_e := h_e(a), D_e := 1 − p_e. Then:

(a) D_e = ν_e(h_{1,e}) ≥ h_{1,e}(a) > 0 and 0 ≤ h_e ≤ 1;
(b) I − K_e is invertible on B(X) and (I − K_e)⁻¹ = Ĝ_e + h_e ⊗ ν_e / D_e;
(c) for every f ∈ B(X): [(I − K_e)⁻¹ f](a) = ν_e(f) / D_e, and |ν_e(f)| ≤ τ_a(e) ‖f‖;
(d) sharpness: sup_{‖f‖ ≤ 1} |[(I − K_e)⁻¹ f](a)| = τ_a / D_e = E_a[τ] (attained at f = 1).

*Proof.* (a) Ĝ(I − K̂)1 = 1 and (I − K̂)1 = k_a + h_1 give h + Ĝh_1 = 1; both terms are ≥ 0; Ĝ ≥ I on nonnegative
functions. (b) I − K = (I − K̂) − k_a ⊗ δ_a = (I − K̂)(I − h ⊗ δ_a); the rank-one factor has inverse I + h ⊗ δ_a / (1 − h(a))
because D ≠ 0; multiply. (c) Evaluate (b) at a: ν(f) + p ν(f)/D = ν(f)/D; |Ĝf(a)| ≤ (Ĝ|f|)(a) ≤ ‖f‖ τ_a.
(d) f = 1 gives τ_a/D, and (c) is an upper bound. ∎

**Consequence (what deflation cannot do).** (d) says the point value at x0 = a has an *intrinsic* sup-norm
amplification E_a[τ] ≈ 465 at e = 0. No decomposition improves the order-0 bound |E_F(a)| ≤ ARL(a)·‖residual‖ from a
residual *norm*; it only replaces the non-sharp one-sided C_upper (1233) by the sharp τ_a/D. The large gains below are in
the order-1 and order-2 cross terms, where the generic stack multiplies independent copies of C.

## 4. Lemma Dv (derivatives of the resolvent at the atom, argument fixed)

Let ∂R := R K' R and ∂²R := 2 R K' R K' R + R K'' R (R = (I − K_e)⁻¹, K' = ∂_e K_e); these are the e-derivatives of e ↦ R_e.
Assume on a drift set E: τ_a ≤ τ, ‖Ĝ‖ ≤ C, D ≥ D_lo > 0, |∂_e D| ≤ D1, |∂_e² D| ≤ D2, ‖∂_e^n K̂‖ ≤ κ_n. Then for fixed
f ∈ B(X) and every e ∈ E:

    |[∂R f](a)|  ≤ A1 ‖f‖,   A1 = τ κ₁ C / D_lo + τ D1 / D_lo²
    |[∂²R f](a)| ≤ A2 ‖f‖,   A2 = τ (2κ₁² C² + κ₂ C) / D_lo + 2 τ κ₁ C D1 / D_lo² + τ (2 D1² / D_lo³ + D2 / D_lo²)

and |[R f](a)| ≤ A0 ‖f‖ with A0 = τ / D_lo.

*Proof.* δ_a is e-independent and continuous, so [∂^j R_e f](a) = ∂_e^j (δ_a R_e f) = ∂_e^j (ν_e(f)/D_e) by Lemma SM(c)
(everything analytic by Lemma K). With ∂Ĝ = ĜK̂'Ĝ, ∂²Ĝ = 2ĜK̂'ĜK̂'Ĝ + ĜK̂''Ĝ and positivity of Ĝ:
|ν_e(f)| ≤ τ‖f‖, |∂ν_e(f)| = |δ_aĜK̂'Ĝf| ≤ τκ₁C‖f‖, |∂²ν_e(f)| ≤ τ(2κ₁²C² + κ₂C)‖f‖. Quotient rule:
(ν/D)' = ν'/D − νD'/D², (ν/D)'' = ν''/D − 2ν'D'/D² + ν(2D'²/D³ − D''/D²); bound term by term. ∎

(k_{a,e}' does not appear: it cancels. The direct computation ν(K'h) = −D' − Dν(k_a') reproduces the same A1.)

### Lemma Dv' (r2: the channel written as the ARL at the atom)

Every term above is (τ_a(e)/D_e)·(tame factor) with |ν_e(g)| ≤ τ_a(e)‖g‖, and τ_a/D = E_a[τ] (Lemma SM(d)). Hence, if in
addition Ā ≥ sup_E E_a[τ], and with δ₁ := D1/D_lo ≥ |D'|/D, δ₂ := D2/D_lo ≥ |D''|/D,

    A0 = Ā_eff,   A1 = Ā_eff (κ₁C + δ₁),   A2 = Ā_eff (2κ₁²C² + κ₂C + 2κ₁Cδ₁ + 2δ₁² + δ₂),   Ā_eff := min(Ā, τ/D_lo)

are also valid in Lemma Dv and Theorem AD. *Proof:* |ν'/D| ≤ (τ_a/D)κ₁C‖f‖, |νD'/D²| ≤ (τ_a/D)(|D'|/D)‖f‖,
|ν''/D| ≤ (τ_a/D)(2κ₁²C² + κ₂C)‖f‖, |2ν'D'/D²| ≤ 2(τ_a/D)κ₁C(|D'|/D)‖f‖, |ν(2D'²/D³ − D''/D²)| ≤ (τ_a/D)(2(D'/D)² + |D''|/D)‖f‖. ∎

**Whole-kernel supersolution (Lemma T with K in place of K̂).** If W ≥ 1 + K_e W on X for every e ∈ E, then
(I − K_e)⁻¹1 ≤ W on X, so E_a[τ] ≤ W(a) =: Ā. (Same proof: W ≥ 1, K W ≤ θW, positivity.) The whole-kernel ARL function has
no atom kink, so this bound is nearly sharp (the adopted R3 C_e0 is 469.8 against a float 466).

## 5. Theorem AD (deflated point errors of the frozen K1 DAG)

Fix a K1 cell with midpoint e0 and half-width ρ, and a drift set E ⊇ [e0 − ρ, e0 + ρ] on which the hypotheses of
Lemma Dv hold. For each r ∈ {0,…,4} let F̂_r, D̂_r, Ĥ_r be the frozen candidates (state-only polynomials, constant in e)
and let the frozen certificate give (record fields):

- λ_F, λ_D, λ_H: the local residuals (`objects[F_r|dF_r|H_r].delta_mid` at e0; `.delta_cell` uniformly on the cell);
- σ_0, σ_1, σ_2: the source errors of `S_r^(k)` (`eps_mid` / `eps_cell` of node `Sclosed:k` for r = 0, `S:r:k` otherwise).

Then, with f_F = λ_F + σ_0, f_D = λ_D + σ_1, f_H = λ_H + σ_2,

    |F_r(e0)(a) − F̂_r(a)|  ≤ A0 f_F^mid
    |D_r(e0)(a) − D̂_r(a)|  ≤ A0 f_D^mid + A1 f_F^mid
    |H_r(e)(a) − Ĥ_r(a)|   ≤ A0 f_H^cell + 2 A1 f_D^cell + A2 f_F^cell      for every e in the cell.

*Proof.* Errors E_F = F − F̂, E_D = D − D̂, E_H = H − Ĥ (true objects at e, candidates fixed). The frozen binding error
algebra (`p5y_k1_cover_ledger_successor/ERROR_ALGEBRA.md` §1 and §3, the premises of every frozen eps rule) states the exact
identities (I − K)E_F = φ_F, (I − K)E_D = φ_D + K'E_F, (I − K)E_H = φ_H + K''E_F + 2K'E_D (signs immaterial), where
φ_X = (complete equation residual of the candidate) + (candidate source − true source), with ‖φ_X‖ ≤ λ_X + σ_k at e0
(delta_mid, eps_mid) and uniformly on the cell (delta_cell = delta_mid + ρ·Env, eps_cell; §3 "uniform cell bounds").
Theorem AD uses these premises and nothing else from the stack; it changes only the resolvent inequality applied to them. Solving: E_F = Rφ_F, E_D = Rφ_D + (∂R)φ_F,
E_H = Rφ_H + 2(∂R)φ_D + (∂²R)φ_F. Evaluate at a and apply Lemma SM(c) and Lemma Dv (at e0 for F, D; at each e in the cell
for H). ∎

This replaces the frozen rules eps(F) = C f_F, eps(D) = C(f_D + k₁C f_F), eps(H) = C(f_H + k₂Cf_F + 2k₁C(f_D + k₁Cf_F)) at
the evaluation point only. Whole-function sup norms are *not* improved (they still carry h·(channel)); no rule of the
stack that consumes a sup norm is changed.

## 6. Corollary T (tightening a recorded enclosure)

A frozen record interval for R_m^(j) (j = 0, 1 at the midpoint; j = 2 on the whole cell) is the Arb ball

    Σ_{r<m} (1/m)·[origin_r ± eps_r] + (W terms),   eps_r = eps_mid[F:r], eps_mid[D:r], eps_cell_refined[H:r]

(`propagate.enclosures`, `assembly.assemble`, `enclose(c, ρ) = c + arb(0, ρ.abs_upper())`). Arb contains the exact
Minkowski sum, whose half-width is at least Σ(1/m)(rad origin_r + eps_r) + (W half-width). If eps'_r ≥ the true error
at a, the true value lies in [lo + Δ, hi − Δ] with Δ = Σ_{r<m}(1/m) max(0, eps_r − eps'_r).
The used radius arb(0, eps.abs_upper()) is ≥ the recorded eps (rounding up), so Δ computed from recorded eps is ≤ the
exact shrink. The consumer refuses a record whose half-width is below Σ(1/m)eps_r (that would violate the assumption).
M' := min(M_R2, mag(tightened R2 interval)) is again ≥ sup_cell |R_m''|.

## 7. Corollary C (consumption) — pre-registered consumer semantics

1. Load the adopted inputs exactly as T-EXT's consumer does (pinned E6 adapter `fbad7d33`, frozen loader `3a54f0fb`,
   frozen K5-B `ddd54dc4`, cells.json `341eb5e9`, manifest `29ad1f9b`, sealed slot-1 `cf90f1ea`, T-EXT result `cb97cabc`
   and its pinned channel derivation `text_consume.text_objects`, sha `657458ad`).
2. For every cell covered by a certified operator registry (§8), tighten R and R' (midpoint) and R'' (whole cell) by
   Corollary T with the Theorem AD radii. Cells not covered keep their record.
3. Apply the adopted T-EXT C2 channel unchanged: L_k = Λ(k) on cells 1..40, H ∩ [−M2, M2] and M = min(M, M2) on 0..40.
4. Run the frozen k5b_literal per m on cells 0..309. A cell passes iff the frozen theorem says so.
5. No other choice exists: no cell selection, no adaptive block choice after seeing records, no rerun.

Validity: K5-B is a theorem about *valid* enclosures; every enclosure fed to it is valid (records, Corollary T,
T-EXT C2 — intersection of valid enclosures is valid). So each pass certifies g_m < 0 on that cell exactly as in K5-B.

## 8. The certified operator constants the theorem needs (registry obligations)

Per e-block B (a finite list of blocks covering the domain; a cell uses the worst constants of the blocks it meets):

| constant | meaning | certificate |
|---|---|---|
| Ā ≥ sup_B E_a[τ] | Lemma Dv' | W(a) of a whole-kernel polynomial supersolution W ≥ 1 + K_eW, uniform on B (r2) |
| τ ≥ sup_B E_a[τ ∧ T_a] | Lemma T | w(a) of a polynomial supersolution w, uniform on B |
| C ≥ sup_B ‖Ĝ_e‖ | Lemma T | sup_X w (Bernstein on the frozen reachable cover) |
| D_lo ≤ inf_B D_e | Lemma SM | operator-only: candidate for d = Ĝ h_1 (d(a) = D) with tame error τ·residual, extended over B by \|D'\| |
| D1 ≥ sup_B \|D'\| | Lemma Dv | operator-only: candidate for d' with tame error; or D1 ≤ \|e\|·D2 by evenness (D'(0) = 0) |
| D2 ≥ sup_B \|D''\| | Lemma Dv | operator-only: candidate for d'' with tame whole-block error |

Uniformity of the supersolution over B uses Lemma T with E = B and the linear-in-e expansion
w − 1 − K̂_e w = [w − 1 − K̂_{ec} w] − (e − ec) ∂_eK̂_{ec} w − R₂, |R₂| ≤ (e − ec)²/2 · κ₂ · ‖w‖, checked at both ends of B
(affine in e − ec, so the endpoints are the worst case) with the frozen Pair kernel for K̂_{ec} and K̂'_{ec}.

All of these are operator-only (no source S_r, no candidate of F, no R value). h_1 = 1 − K_e 1 is part of the operator.

## 9. Answers to the campaign's structural questions

| question | answer |
|---|---|
| EXACT_DEFLATION_IDENTITY | (I − K_e)⁻¹ = Ĝ_e + (Ĝ_e k_{a,e}) ⊗ δ_aĜ_e / D_e, D_e = (Ĝ_e h_{1,e})(a) (Lemma SM); at a: R_e f(a) = ν_e(f)/D_e |
| complement invariance | not needed: the identity is algebraic (a rank-one factorisation), not a spectral splitting |
| SOURCE_PERRON_COMPONENT | NONZERO_BUT_CONTROLLED: the channel coefficient of a source is ν_e(S_r) (odd in e, 0 at e = 0 for σ-odd sources); for *errors* it is ν_e(residual), bounded by τ‖residual‖ and then divided once by D |
| MOVING_PROJECTION_DERIVATIVES_REQUIRED | AVOIDED_BY_FORMULATION: the left functional δ_a is e-independent; only the scalar D_e and the positive operator Ĝ_e move, with ∂Ĝ = ĜK̂'Ĝ |
| where the gain comes from | the frozen cross terms C²k₁ (order 1) and 2C³k₁² + C²k₂ (order 2) become A1 ≈ τκ₁C/D + τ\|D'\|/D² and A2: one channel division instead of a product of channel amplifications |
| where it does not | order-0 point values (Lemma SM(d)); whole-function sup norms; anything needing a *value* of R''' |
