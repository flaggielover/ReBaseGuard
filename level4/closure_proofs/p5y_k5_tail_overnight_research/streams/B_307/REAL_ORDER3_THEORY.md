# REAL_ORDER3_THEORY — the true order-3 objects, their representations, bounds, and what they can and cannot buy

Stream B_307, overnight campaign (research only). Written 2026-09-27/28 UTC.
Code: `NS/streams/B_307/code/` (`b307_order3.py`, `b307_cellpipe.py`, `b307_lib.py`, `b307_run_fixtures.py`,
`b307_lower_front.py`, `b307_hermite_check.py`, `b307_tower_fixture.py`).

**Correction note (incident 01).** A pre-correction version of §4c set a committed tail break-even figure next to
this document's structural ratios (α, β). That adjacency is a target-equivalent proxy. It was removed on coordinator
instruction (incident 01).

**Scope and quarantine.**
* Nothing here is evaluated on CUSUM m = 5 cells 305–309 or at any drift in [6/5, 13/5] (or its mirror).
* **No order-3 result of this document is applied to 305–309.** Tail facts are quoted with file:line.
* The accepted route audit rates the real order-3 route R4 at **HIGH** scientific risk for 307
  (`p5y_k5_tail_route_audit/review/ROUTE_AUDIT_R1_REVIEW.md:105-124`). This document neither lowers nor uses that
  rating. It asks what the real order-3 objects contain, structurally.

Notation follows THEOREM_TC / THEOREM_AD:
* a = (0,0), the atom;
* R_e = (I − K_e)⁻¹, and K_i = ∂_e^iK_e;
* F_r = R_eS_r;
* Λ(e) = E_a[τ] = ‖δ_aR_e‖;
* ∂^jR is the j-th e-derivative of e ↦ R_e.

## 1. The true order-3 objects, and who needs what

| object | definition | exists? |
|---|---|---|
| F_r'''(e) ∈ B(X) | third e-derivative of F_r = R_eS_r(e) | yes, by (P1) (§3) |
| F_r'''(e)(a) | its value at the atom: one signed real number per (r, e) | yes |
| R'''_m(e) | (1/m)Σ_{r<m}F_r'''(e)(a) + Σ_t c(m,t)Σ_{r<t}W'''_(r,t−r−1)(e)(a), with the same coefficients at every order (`p5y_k1_cover_ledger_successor/ERROR_ALGEBRA.md` §4) | yes |

**What theorem TC needs from order 3** (THEOREM_TC.md:9-15, 53-69):
* a **fixed function** Ĝ, the third Taylor coefficient of the candidate. Any Ĝ is admissible; the choice only
  changes the width;
* Ĝ enters through exactly three scalars, all at the **midpoint** e0:
  * f_G ≥ ‖φ'''_Ĝ(e0)‖, where φ'''_Ĝ(e0) = S''' + 3K₁Ĥ + 3K₂D̂ + K₃F̂ − (I − K)Ĝ is the residual of Ĝ;
  * |Ĝ(a)|, which gives the centre motion ρ|Ĝ(a)|;
  * s_G ≥ ‖Ĝ‖, which enters Env4.
* The "real order-3" route is Ĝ ≈ F_r'''(e0). TC-T takes Ĝ := 0.
* TC is **local** (one cell) and **midpoint-only** at order 3.

**What K5-B's chain needs from order 3** (K5_GLOBAL_BRIDGE.md:11, 23-27):
* a certified **whole-cell, signed** lower bound L_k ≤ inf_{e∈C_k} R'''_m(e);
* an **unbroken** run of such cells from cell 0, because the chain is contiguity-dependent
  (`p5y_k5_order3_readiness_audit/README.md:79-81, 109-113`).

So the chain needs strictly more than TC:
* the sign;
* uniformity over the cell, which requires a pointwise **order-4** bound at the atom: F'''(e)(a) ≥ F'''(e0)(a) − ρ·sup|F⁗(u)(a)|;
* contiguity.

TC-T's whole-cell interval **discards the sign**: half_r = ρ|Ĝ(a)| + rad_r. This is HO-12 of HIGHER_ORDER_AUDIT_307.

## 2. Rigorous computable representations

### 2a. Resolvent identity (exact)

Differentiate (I − K_e)F_r(e) = S_r(e) three times (Leibniz). This gives

    F''' = R_e·[S''' + 3K₁F'' + 3K₂F' + K₃F],

equivalently

    F''' = Σ_{j=0..3} C(3,j)·∂^jR·S^(3−j).

The operator derivatives expand over compositions. For every n,

    ∂^nR = Σ_{compositions (i_1,…,i_p) of n}  n!/(i_1!…i_p!) · R K_{i_1} R K_{i_2} R … K_{i_p} R,

and for n = 3 this is

    ∂³R = 6RK₁RK₁RK₁R + 3RK₂RK₁R + 3RK₁RK₂R + RK₃R.

* Implementation: `b307_lib.Point.atom_rows`, `generic_dnR_bound`, and `Point.__init__` (d3R).
* Verification: exact on 4 P1 cases. The atom identity F'''(e0)(a) = [RS'''](a) + 3[∂RS''](a) + 3[∂²RS'](a) +
  [∂³RS](a) holds exactly on all 320 fixture objects (`B307_ORDER3_FIXTURES.json` `F3_atom_identity_all_exact`).
* Negative control: ∂³R without the 3RK₂RK₁R term is detected (4/4).

### 2b. Likelihood-ratio / Hermite form of the kernel derivatives (CUSUM)

The CUSUM kernel is (K_eg)(x) = ∫_{m−c}^{c−p} g(T(x,z))·φ(z+e) dz. Its window and its map T do not depend on e
(`p5y_k5_perron_deflated_resolvent/theorem/OPERATOR_AUDIT.md:10-15`). Since ∂_e^iφ(z+e) = He_i(−(z+e))·φ(z+e),

    (K_i g)(x) = E[ g(T(x,Z))·1{no alarm}·He_i(S) ],     S := −(Z + e) ~ N(0,1) under P_e.

* Check: float identity check at the declared drifts e ∈ {0, 1/4, 1/2, 1, 3}, 6 states, g ∈ {1, post-state p'},
  i = 1..4. There are 240 cases with worst relative error 1.6·10⁻¹⁵ (`NS/validation/B307_HERMITE_IDENTITY.json`).
* Negative control: dropping the (−1)^i sign is detected in 112/120 odd-order cases. The 8 undetected cases have a
  derivative that vanishes by symmetry.
* κ_n = E|He_n(Y)| = 0.797885, 0.967883, 1.510013, 2.800600 (n = 1..4), matching the whole-line norms quoted in
  `p5y_k5_m5_tail_closure/evidence/measurement_r1/MEASUREMENT_NOTE.md:60`.

### 2c. Path (likelihood-ratio) form of the atom functionals

Let M_n := Σ_{k≤n} S_k. Under P_e, M_n is a sum of n i.i.d. N(0,1) scores.

**Gaussian-location lemma.** For u_k = z_k + e and M = −Σu_k,

    ∂_e^j Π_{k≤n} φ(u_k) = H_j(M, n)·Π_{k≤n} φ(u_k),     H_j(M, n) := n^{j/2}·He_j(M/√n).

Written out: H_0 = 1, H_1 = M, H_2 = M² − n, H_3 = M³ − 3nM, H_4 = M⁴ − 6nM² + 3n².
* Proof. Πφ(u_k) depends on e only through Σu_k, with variance n. Differentiate
  exp(−(Σu_k)²/(2n)) j times and use He_j(−x) = (−1)^jHe_j(x).
* Check: jets at 100 random points, j = 1..4 steps and orders 1..4; worst error 4.4·10⁻¹³.
* Negative control: dropping the variance rescaling is detected in 225/300 cases. The 75 undetected cases are
  order 1, where H_1 = M needs no rescaling.

**Theorem RO3-LR (path representation).**
* Premises:
  * P_x(τ > n) ≤ Ā·θ^n uniformly for e in a drift set E. This follows from a whole-kernel supersolution
    W ≥ 1 + K_eW on E, with θ = 1 − 1/‖W‖ (THEOREM_AD.md:91-93).
  * g ∈ B(X) is fixed.
* Claim: for every e ∈ E and every j ≥ 0,

      (∂^jR g)(a) = E_a[ Σ_{n<τ} g(X_n)·H_j(M_n, n) ].

* Proof sketch:
  * R g(a) = Σ_n E_a[g(X_n); τ > n], and {τ > n} and X_n are functions of Z_1..Z_n alone.
  * Differentiate each summand under the integral (the Gaussian-location lemma).
  * The interchange of Σ_n and ∂_e^j is justified by E|H_j(M_n,n)|² = j!·n^j together with Cauchy–Schwarz:

        Σ_n E|g(X_n)H_j(M_n,n)|·1{τ>n} ≤ ‖g‖·√(j!)·Σ_n n^{j/2}·√(Āθ^n) < ∞,

    uniformly on E. Each summand is entire in e.
* Consequence:

      Λ_j(e) := E_a[Σ_{n<τ}|H_j(M_n,n)|]  ≥  ‖δ_a∂^jR_e‖,   Λ_0 = Λ.

**Caveat.** The Cauchy–Schwarz bound above proves finiteness only. It is asymptotically weak: of order
√Ā·(2C)^{1+j/2}, no better than Dv′ in Λ. Sharp certification of Λ_j needs augmented-state supersolutions in
(x, M). That is the C_308 LR program (`NS/streams/C_308/IDEA_LR_SCORE_CONSTANTS.md`), which owns Λ_1 and Λ_2 and is
not implemented here.

### 2d. The sources depend on e: F_r^(k)(e)(a) with the explicit e-dependence

S_r(x; e) is a deterministic function of (x, e). By Leibniz over the product "source × path likelihood",

    F_r^(k)(e)(a) = Σ_{j=0..k} C(k,j)·E_a[ Σ_{n<τ} S_r^(k−j)(X_n; e)·H_j(M_n, n) ],

where S_r^(i) is the partial e-derivative at a fixed state. This gives the **atom-direct LR (ADLR)** bound

    |F_r^(k)(e)(a)| ≤ Σ_{j=0..k} C(k,j)·Λ_j(e)·σ_{k−j}(e),     σ_i(e) ≥ ‖S_r^(i)(e)‖.

(Coordinator suggestion; ADLR is evaluated in §4d.) The same holds with any A_j ≥ ‖δ_a∂^jR‖ in place of Λ_j; for
example the true functional norm, the positive majorant, or the Lemma-G-type generic_dnR_bound.

### 2e. The sources themselves, and an h-tower without the Leibniz recursion

The raw-variable objects have path forms:
* h_j(x) = P_x(τ = j);
* S_r(x) = E_x[raw_1·1{τ = r+1}], with raw_1 = Z_1 + e (`p5y_k1_cusum_kernel/IMPLEMENTATION_MAP.md:28-33`;
  S_r = J_eh_r).

By §2c:

    h_j^(n)(x) = E_x[1{τ=j}·H_n(M_j, j)]
        ⇒  ‖h_j^(n)‖ ≤ κ_n·j^{n/2}     (also ≤ √(n!·j^n·P_x(τ=j)))

    S_r^(n)(x) = E_x[1{τ=r+1}·(raw_1·H_n(M_{r+1}, r+1) + n·H_{n−1}(M_{r+1}, r+1))]
        ⇒  ‖S_r^(n)‖ ≤ √(n!·(r+1)^n) + n·κ_{n−1}·(r+1)^{(n−1)/2}

These are universal constants, valid at every drift and every cell. They grow like j^{n/2}, whereas the frozen J/h
tower grows like (k₁j)^n.
* On the exact FX_B score walks the tower overstates the truth by 3–4× at j = 2, 9–12× at j = 3, 24–38× at j = 4,
  and 47–77× on S_4''' (`NS/validation/B307_TOWER_FIXTURE.json`, all sound).
* Negative control: dropping the binomial weights is detected in 6/54 cases. It is weak because the tower is loose.

This is a **valid alternative supply** for σ3 and σ4. The minimum of it and the frozen tower is valid.
* At j = 1, keep the frozen h_1^(n) = −S_0^(n−1) bound: it is a closed form. The Hermite bound is meant for j ≥ 2.
* Status: THEORY_ONLY. It was not evaluated on any CUSUM cell.
* Its use would be a closure-only change under floor r2.

## 3. Existence and finiteness (analyticity premise P1)

1. **Kernel.** e ↦ K_e is real-analytic into bounded operators on B(X), with ‖K_i(e)‖ ≤ κ_i (Lemma K,
   THEOREM_AD.md:19-30), or with the drift-aware k_i on a cell (THEOREM_TC.md:18-20).
2. **Resolvent.** If ‖R_e‖ ≤ C on the cell (C_upper, THEOREM_TCT.md:22-23), then e ↦ R_e is analytic there, as a
   Neumann series around each point with radius ≥ 1/(C·Σ_i κ_iρ^{i−1}/i!). Every ∂^nR is given by §2a, and
   ‖∂^nR‖ ≤ generic_dnR_bound(n, k, C) < ∞ (`b307_lib.generic_dnR_bound`).
3. **Sources.** S_0 is a closed form in φ, so it is entire. S_r = J_eh_r with h_r = K_e^{r−1}h_1 is analytic
   (THEOREM_TC.md:20-21). Therefore F_r = R_eS_r is analytic on the cell, and F_r''' and F_r⁗ exist in B(X) with

       ‖F_r^(k)(e)‖ ≤ Σ_j C(k,j)·‖∂^jR_e‖·‖S_r^(k−j)(e)‖ < ∞.

4. **Atom values.** F_r'''(e)(a) is a finite, continuous and analytic function of e on the cell. R'''_m is a finite
   linear combination of such functions and of the W''' terms (the latter are finite powers).
5. **LR form.** Finite under a uniform geometric tail (§2c). The rigorous but weak constant is
   Λ_j ≤ √(j!·Ā)·Σ_n n^{j/2}θ^{n/2}.

**Premise status on the tail (read only).**
* A whole-kernel supersolution Ā exists on the tail blocks: the committed I1 registry
  (`p5y_k5_tail_operator_registry/evidence/registry_c1/REGISTRY_C1.json:12-109`) supplies the geometric-tail premise
  of §2c there.
* No new tail quantity is computed here.

## 4. Usable deterministic bounds and their structural comparison

### 4a. The surrogate is the norm-only resolvent bound on the true point value (Proposition RO3-S)

**Statement.** With Ĝ = 0, write φ'''_0 := S''' + 3K₁Ĥ + 3K₂D̂ + K₃F̂ (at e0) and
E_X := X(e0) − X̂ for the candidate errors. Then

    [R_{e0}φ'''_0](a) = F'''(e0)(a) − [R(3K₁E_H + 3K₂E_D + K₃E_F)](a),

and TC-T's monomial A0·f_G satisfies

    A0·f_G ≥ A0·‖φ'''_0‖ ≥ |[R_{e0}φ'''_0](a)|.

**Proof.** Subtract the exact identity of §2a from φ'''_0. ∎

**Reading.** The dominant TC-T monomial A0·ρ·f_G is **exactly** a norm-only bound of ρ·|F'''(e0)(a)|, up to
candidate-error terms. It is built from the resolvent identity by a triangle split into four norms.

### 4b. The centre-motion floor (Proposition RO3-F)

**Statement.** Let Ĝ be any fixed function, f_G(Ĝ) ≥ ‖φ'''_Ĝ(e0)‖, and A0 ≥ ‖δ_aR_{e0}‖. Then

    ρ|Ĝ(a)| + A0ρ·f_G(Ĝ)  ≥  ρ·|[R_{e0}φ'''_0(e0)](a)|  (≈ ρ|F'''(e0)(a)|).

**Proof.** φ'''_Ĝ = φ'''_0 − (I − K)Ĝ, so [R φ'''_Ĝ](a) = [Rφ'''_0](a) − Ĝ(a). Apply the triangle inequality. ∎

**Reading.** Whatever order-3 candidate is used, the A0-level ρ-group of a **whole-cell** TC enclosure cannot fall
below the true centre motion. What a real Ĝ can remove is only the **excess** of the norm-only bound over that floor.

**Check.** Holds on all 320 objects × 3 routes (`floor_ok`, `b307_order3.route_groups`).

### 4c. The price of a real candidate: the order-4 envelope penalty (Proposition RO3-E)

**Setting.** A real Ĝ puts s_G into Env4. The A0-level cost is A0·(ρ²/2)·s_G·(4k₁ + 6k₂ρ + 2k₃ρ² + k₄ρ³/6).
Relative to the surrogate's A0ρf_G^surr this is

    β := ρ·s_G·(4k₁ + 6k₂ρ + 2k₃ρ² + k₄ρ³/6) / (2 f_G^surr).

Since ‖F'''‖ = ‖R(I − K)F'''‖ ≤ C‖(I − K)F'''‖ ≤ C(f_G^surr + ε3), where
ε3 := 3k₁‖E_H‖ + 3k₂‖E_D‖ + k₃‖E_F‖ (§4a), and s_G ≤ ‖F'''‖ + ‖Ĝ − F'''‖ (for an exact sup):

    β ≤ ρ(4k₁ + 6k₂ρ + 2k₃ρ² + k₄ρ³/6)·(C(f_G^surr + ε3) + ‖Ĝ − F'''‖) / (2 f_G^surr).

**Under the frozen cover rule** ρ ≤ 1/(4 a_up C_use), with k₁ ≤ κ₁ ≤ a_up
(`p5y_k1_cover_ledger_successor/CHECKPOINT.md:91-97`), the leading factor is 2k₁ρC ≤ 1/2. So for an accurate
candidate

    β ≤ (1/2)·(1 + O(ρ) + ε3/f_G^surr + ‖Ĝ−F'''‖/(C f_G^surr)).

**Evidence.**
* The envelope holds on all 640 real-route objects (`envelope_ok`).
* On FX_A under the cover rule, β = 0.0025–0.09 against an envelope of 0.05–0.62.
* On the lower front, β = 0.0033–0.0084 with 2k₁ρC_upper = 0.49992–0.499999.

**Consequence (ideal candidate).** Write α := |F'''(e0)(a)|/(A0 f_G^surr) (pointwise against norm-only). Then

    Q_real/Q_surr  ≈  α + β  ≤  α + 1/2 (+ small).

* **Never much worse.** A real Ĝ is never much worse than Ĝ = 0 at the A0 level: at most ≈ 1.5×.
* **Capped gain.** Its gain is capped by 1/(α + β).
* **When it is large.** The gain is large iff two conditions hold:
  * the true point value is small relative to its norm-only bound (α ≪ 1);
  * F''' is **not Perron-amplified**, i.e. ‖F'''‖ ≪ C‖(I − K)F'''‖. The "Perron index" s_G/(C f_G^surr) measures
    this.
* No committed tail-cell figure is placed next to α, β or any ratio of this section (incident-01 rule).

### 4d. ADLR — the atom-direct likelihood-ratio Taylor enclosure (coordinator suggestion), evaluated

**Enclosure.** For every e in the cell, with s = |e − e0|:

    F_r''(e)(a) ∈ Ĥ_r(a) ± [ rad0 + s·B3 + (s²/2)·B4 ]

with the three terms defined as follows:
* rad0 = A0f_H + 2A1f_D + A2f_F at e0. This is theorem AD's midpoint form (THEOREM_AD.md:114-116), with the A's
  valid at e0.
* B3 ≥ |F_r'''(e0)(a)|, by §2d with k = 3: B3 = Σ_{j≤3} C(3,j)·A_j(e0)·σ_{3−j}(e0).
* B4 ≥ sup_{u∈C}|F_r⁗(u)(a)|, by §2d with k = 4: B4 = Σ_{j≤4} C(4,j)·sup_u A_j(u)·σ^cell_{4−j}.

**Validity conditions.**
* (i) the A_j bound the atom functionals ‖δ_a∂^jR‖ — **at e0** for rad0 and B3, and **uniformly on the cell** for
  B4. Examples: Λ_j of §2c, a positive majorant, or generic_dnR_bound;
* (ii) σ_i bound the **true** source derivatives, again at e0 and cell-uniformly respectively. The e-dependence of
  S_r is handled by §2d;
* (iii) Taylor's theorem with integral remainder, applied to the scalar function e ↦ F_r''(e)(a).

**Structural comparison.**
* The s-coefficient becomes B3 = Λσ3 + 3A1σ2 + 3A2σ1 + A3σ0, against TC-T's A0f_G = A0(σ3 + 3k₁s_H + 3k₂s_D + k₃s_F).
* ADLR has **no A1/A2 cross terms in the ρ-group**. It removes the whole ρ-dependent part of 2A1p1 + A2p0 (rank 1
  of the audit).
* In exchange it needs A3 (true order Λ^{5/2}; certified order Λ⁴) multiplying σ0, plus a cell-uniform A4.
* Each route discards a different piece of information:
  * ADLR splits by **source** order (Leibniz in S) and uses **pointwise** atom functionals;
  * TC-T splits by **kernel** order and uses the **actual** sup norms of the candidates, which carry the real size
    of F, F', F''.

**Exact fixture results.** From `B307_ORDER3_FIXTURES.json`, summary `adlr`; half-widths at s = ρ; medians, with
range in parentheses.

| variant (A_j supply) | certified? | FX_A: half / TC-T surrogate half | FX_A: half / real-Ĝ half | FX_B: half / surrogate | pointwise failures |
|---|---|---|---|---|---|
| G (generic_dnR_bound with cell k, C) | **yes** | 18.3 (1.5–150) | 125 | 2.2·10⁴ | 0 |
| PM (positive majorants at e0, grid max for B4) | no (proxy) | 2.67 (0.76–22) | 18.8 | 2.4·10³ | 0 |
| true (exact ‖δ_a∂^jR‖ at e0; grid max for B4) | best case of **any** A_j supply, incl. LR | **0.46 (0.06–0.79)** | 1.84 (0.50–5.3) | **2.9 (0.61–22)** | 0 |
| oracle (B3 = \|F'''(a)\|, B4 = grid max \|F⁗(a)\|) | no (shape floor) | 0.050 (0.004–0.29) | 0.32 | 0.0016 | 0 |

At the ρ/16 regime, FX_A gives 0.54 for the true variant and 8.9 for G.

Negative control ("oracle with B3 := 0"):
* detected on 240/240 FX_A objects;
* detected on only 7/80 FX_B objects. There F'''(e0)(a) ≡ 0 on 56/80 objects, so the linear term carries no motion.

**Verdict on ADLR.**
* **Valid.** 0 failures in every variant.
* **Incomparable with TC-T**, and regime-dependent:
  * with the best possible atom constants it is 2.2× tighter on FX_A (moderate Λ = 2.9–32);
  * it is 2.9× looser on FX_B (Λ = 30–273), where A3σ0 ∝ Λ^{5/2} dominates while TC-T's candidate sups stay small;
  * with the only certified supply available today (Lemma-G type), it is 18× (FX_A) to 2·10⁴× (FX_B) looser than
    the surrogate;
  * it is always looser than an accurate real-Ĝ route. At the median, even the best-case constants give ADLR 1.8×
    the real route's half-width on FX_A.
* **The shape is excellent.** The oracle row is 20× tighter than the surrogate on FX_A. The gap is entirely in the
  constants A3 and A4, which no stream certifies: C_308 owns Λ_1 and Λ_2 only.
* **Which regime the tail is in is not assessed** (quarantine).

## 5. Required inputs, and which are unavailable locally

| route | inputs | available here? | blocker (committed) |
|---|---|---|---|
| **real Ĝ in theorem TC (R4)** | K1 candidates F̂, D̂, Ĥ (degree-12 dyadic polynomials); a producer run of the order-3 solve (I − K)Ĝ = K₃F̂ + 3K₂D̂ + 3K₁Ĥ + Ŝ:3 with its certified residual δ_G, sup s_G, value Ĝ(a) | **no** | the candidates were **never serialized** (0/326 records; C6, `p5y_k5_tail_c6_evidence_recovery/README.md:41-50`). Replay needs numpy/python-flint on a host (none in scope, C6-N1). The order-3 producer registry is frozen empty and its guard is DENY. N1, N3, N5 and N7 are open (`p5y_k5_tail_c2_closure/OPEN_NOTES_DISPOSITION_C2.md:5-43, 72-75`) |
| **ADLR** | σ0..σ3 at e0 and σ0..σ4 cell-uniform for S_r (true source-derivative sups); A_0..A_3 at e0; A_0..A_4 uniform on the cell | partly | the σ's exist in committed form: the (P3′) midpoint Aux3 values, the pure tower, or the Hermite bound of §2e. A_0 = Ā_eff exists. A_1, A_2 exist as Lemma G / Dv′, with LR sharpening THEORY_ONLY (C_308). **A_3 and A_4 exist only as the generic (Lemma-G-type) bound, which is 18×–2·10⁴× too loose on fixtures (§4d). No stream owns a sharp A_3 or A_4** |
| **direct atom bound with Dv′-type constants** | a Lemma Dv″ (third derivative of ν_e/D_e by the quotient rule) with a new operator constant D3 ≥ \|D'''\| | **no** | D3 is certified nowhere. It would be a new operator constant, closure-only under floor r2 |
| **K5-B chain L_k** | a cell-uniform order-4 atom bound, and an unbroken run from cell 0 | **no** | readiness audit: "chain problem" (`p5y_k5_order3_readiness_audit/README.md:109-113`) |

**Governance** (`p5y_k5_tail_route_audit/ROUTE_AUDIT_R1.md:42`; floor r2). Every route above is **closure-only**:
each changes the consumer or its non-constant inputs, or supplies constants other than Lemma G / Lemma Dv′ r2.
Adoption would need a user-decided floor extension, frozen before any evaluation.

## 6. Non-target evidence

### 6a. Exact fixtures: the ladder of bounds on the true point value |F_r'''(e0)(a)|

Each bound is divided by the truth. Medians, with range in parentheses. From `B307_ORDER3_FIXTURES.json`
`summary.*.levels_over_truth`, computed in `code/b307_order3.py:29-63`. FX_B statistics use only the 24/80 objects
with F'''(e0)(a) ≠ 0.

| bound | FX_A (Λ 2.9–32) | FX_B (Λ 30–273) |
|---|---|---|
| L_res_norm = Λ·‖(I−K)F'''‖ (norm-only, exact joint residual) | 4.9 (1.6–101) | 77 (24–187) |
| L_split_true = Λ(σ3 + 3k₁‖F''‖ + 3k₂‖F'‖ + k₃‖F‖) (true sups, point norms) | 13.5 (2.4–434) | 538 |
| **L_surrogate = A0·f_G^surr (TC-T form: candidate sups, cell k, Lemma-G A0)** | **18 (3.1–555)** | **664** |
| L_atom_true = Σ C(3,j)·‖δ_a∂^jR‖·σ_{3−j} (ADLR, best-case constants) | 5.6 (1.8–110) | 2670 |
| L_atom_PM (positive majorants) | 95 | 7.2·10⁵ |
| L_atom_G (generic Lemma-G-type) | 203 | 2.2·10⁶ |
| **L_real = \|Ĝ(a)\| + Λ(f_G(Ĝ) + ε3), η = 10⁻³ / 10⁻²** | **1.02 / 1.19** | **1.10 / 2.1** |

All levels are sound, with 0 violations.

**The factorization on FX_A.** The TC-T surrogate is 18× the truth, and this splits into:
* ≈ 5× for norm-only (L_res_norm);
* ≈ 2.7× for the split into four norms (L_split_true / L_res_norm);
* ≈ 1.3× for candidate sups, cell norms and A0 ≥ Λ.

A real candidate collapses all of it to a factor of 1.02–1.2.

### 6b. Exact fixtures: surrogate vs real candidate vs ADLR (half-widths, whole cell)

Real-Ĝ route over the surrogate, medians (ranges):

| class, regime | Q ratio (A0-level ρ-group) | α | β | half-width ratio |
|---|---|---|---|---|
| FX_A, cover rule | 0.088 (0.006–0.36) | 0.058 (0.002–0.33) | 0.018 (0.0025–0.090) | 0.17 (0.075–0.44) |
| FX_A, ρ/16 | 0.075 (0.003–0.35) | 0.072 | 0.0009 | 0.081 (0.009–0.36) |
| FX_B, cover rule | 0.0020 (0.0004–0.008) | 0 (median; F''' ≡ 0 on 56/80) | 0.0010 | 0.24 (0.03–0.96) |
| FX_B, ρ/16 | 0.0010 | 0 | 0.00006 | 0.83 (0.14–0.996) |

* On FX_B the half-width gain is small although the Q gain is huge. With Ĝ fixed, the A2·p0 monomial dominates
  there: it is the rank-1 item of the audit, with P_0 share 0.51–0.995.
* **Improving order 3 alone cannot beat the atom-functional slack of rank 1.**
* Pointwise soundness of every route: 0 failures on 320 objects × 17 grid points.
* Negative controls:
  * the sign-flipped motion is detected on 328/640 objects;
  * "f_G := 0 as a certificate" is detected on 146/320.

### 6c. The safe historical cases: 34 committed lower-front TC cells with REAL order-3 data

The data are 170 objects, from `b307_lower_front.py` and `NS/validation/B307_LOWER_FRONT_ORDER3.json`.

* **Reproduction gate.** An independent implementation of the theorem-TC arithmetic reproduces all 136 committed
  (cell, m) enclosures H_TC exactly. A 2⁻⁶⁰ perturbation of one committed δ_G is detected.
* **Are the committed fields sufficient for the surrogate?** Yes, for f_G^surr with the **pure-tower** σ3 (the norms
  k, j, sup_S0 and the sup of F, D, H are all committed). The (P3′) Aux3 refinement of σ3 is **not** available from
  these files, so this surrogate is valid but possibly looser than a (P3′) surrogate would be. σ3 is 0.4–53 %
  (median 15 %) of f_G^surr here.

| quantity (lower front, all 170 objects) | min – max (median) |
|---|---|
| α = \|Ĝ(a)\|/(A0·f_G^surr): certified centre motion over its norm-only surrogate | 0.0091 – 0.027 (0.017) |
| β: order-4 s_G penalty over the surrogate's order-3 monomial | 0.0033 – 0.0084 (0.0057) |
| Q_real / Q_surr | 0.012 – 0.035 (0.023) |
| per-object half-width, real / surrogate | 0.107 – 0.294 (0.185) |
| m-enclosure width, real / surrogate | m = 1: 0.107–0.160; m = 2: 0.153–0.222; m = 3: 0.157–0.226; m = 5: 0.157–0.217 |
| Perron index s_G/(C_upper·f_G^surr) | 0.0065 – 0.017 |
| 2k₁ρC_upper (cover-rule factor) | 0.49992 – 0.499999 |

**Reading.** On real non-target CUSUM cells:
* the surrogate's order-3 monomial overstates the certified point motion by 37–110×;
* the real candidate's order-4 penalty is tiny (β < 0.01), because F''' is far from Perron-amplified (index ≈ 0.01);
* the real route narrows the whole enclosure by a factor of 5–9.

Proposition RO3-E predicts β ≤ ≈ 1/2 at every cell of the cover. The lower-front β sits far below that envelope.

**Transfer.** None of these ratios is transferred to any tail cell. The route audit's E09/§8 concern, that per-cell
ratios transfer only as estimates, applies with full force. Campaign B's T2 is the committed counter-example: a
tail forecast built on lower-front ratios was refuted (`p5y_k5_m5_tail_closure/README.md:22-26`).

## 7. Does the real order-3 object contain more structural information than the surrogate?

**Yes, in one precise sense, and with three rigorous limitations that must be preserved.**

1. **More information: the signed point value.**
   * F_r'''(e0)(a) is one signed number. The surrogate replaces it by A0·(σ3 + 3k₁s_H + 3k₂s_D + k₃s_F), a
     norm-only bound of the same quantity (Proposition RO3-S).
   * The excess is structural. It comes from the norm-only factor (SM(d) is sharp only for f ≡ 1) and from a
     four-term split that discards the near-cancellation to (I − K)F'''.
   * It is large on exact fixtures (FX_A median 18×) and on **real** non-target cells (37–110×). It is unbounded in
     general: on FX_B the truth is identically 0.
2. **Limitation A: the whole-cell floor** (Proposition RO3-F).
   * A whole-cell interval must still charge ρ|F'''(e0)(a)|, and it discards the sign.
   * The sign is usable only by a profile-aware or sign-aware consumer: TPT (stream E), or the K5-B chain (which
     needs L_k, a whole-cell signed object, §1).
3. **Limitation B: the norm-only cost moves to order 4** (Proposition RO3-E).
   * A real Ĝ re-enters the radius through s_G = ‖Ĝ‖ in Env4.
   * For an accurate candidate and under the frozen cover rule, this penalty is ≤ ≈ 1/2 of the surrogate's order-3
     monomial. So the gain is capped by 1/(α + β), and the real route is never worse than ≈ 1.5× the surrogate.
   * The penalty is small exactly when F''' is not Perron-amplified.
   * **Which regime the tail is in has never been measured** (committed: "The tail's own s_G/s_H has never been
     measured", `p5y_k5_tail_c2_closure/phase_r/R_STAGE_DESIGN.md:68-69`). It is not assessed here.
4. **Limitation C: order 4 and the atom functionals remain.**
   * Once order 3 is fixed, the order-4 envelope (rank 3 of the audit) dominates: 83–98.5 % of rad on FX_A.
   * With a fixed order-3 candidate, the A2·p0 monomial (rank 1) can dominate (FX_B).
   * Neither is touched by a real Ĝ. The order-4 point value has no representation in any current route.
   * ADLR (§4d) is the only candidate-free route. It is valid and has an excellent shape, but it is incomparable with
     TC-T and needs sharp A_3 and A_4, which nobody certifies.

**Negative results preserved.**
* (N-a) The Cauchy–Schwarz route to the LR constants (§2c) is not sharper than Dv′ in Λ. It proves finiteness only.
* (N-b) ADLR with the only certified constants available (Lemma-G type) is 18×–2·10⁴× looser than the TC-T
  surrogate on fixtures.
* (N-c) Even with best-case constants, ADLR is looser than the surrogate in the large-Λ fixture regime (FX_B, 2.9×)
  and looser than an accurate real Ĝ everywhere tested.
* (N-d) The Hermite h-tower (§2e) does not beat the frozen closed form at j = 1.
* (N-e) The FX_B toy has F'''(a) ≡ 0 on most objects (structural identities F_0(a) ≡ 1, F_1(a) = 1 − p₀(e)). Its α
  statistics are degenerate and are reported as such, not as evidence of a typical ratio.

**Final order-3 results are NOT applied to 305–309.** No tail number was produced by this document or its code.
