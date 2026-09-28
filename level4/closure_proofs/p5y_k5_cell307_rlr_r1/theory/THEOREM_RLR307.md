# Theorem RLR-307: a block-uniform regenerative-LR supply of the atom constants on one cover cell

**Status.** Formal statement for the cell-307 RLR campaign (r1). It restates, and assembles into one theorem, results
proved in:
* THEOREM_LR (overnight C1a, blob `6f4f1fbe6b99`);
* THEOREM_AD (`p5y_k5_perron_deflated_resolvent/theorem/THEOREM_AD.md`);
* THEOREM_TCT (`p5y_k5_m5_tail_closure/theorem/THEOREM_TCT.md`).

It adds:
* Lemma S (reflection);
* Lemma H (hull and cover);
* Lemma Lad (ladder composition);
* the explicit min / max composition up to the consumed supply.

It states **what the certificate proves and nothing about the value of any consumer output.**

## 0. Objects

**Kernel** (THEOREM_AD Lemma K; C1B §1).
* State x = (p, m), with p, m ≥ 0. Parameters K = 1/2, C = 11/2.
* Increment Z with Z + e ~ N(0, 1); e is the drift.
* Update T(x, z) = ((p + z − K)⁺, (m − z − K)⁺).
* Alarm-free window A(x) = [m − C, C − p]. It does not depend on e.
* Sub-Markov kernel (K_e f)(x) = ∫_{A(x)} f(T(x, z)) φ(z + e) dz.
* Atom a = (0, 0). The atom window is [m − K, K − p].
* Taboo kernel K̂_e is K_e restricted to the survival set A(x) minus the atom window.
* R = {0 ≤ p, m ≤ 5 : p = 0 or m = 0 or p + m ≤ 4}, the reachable set from a. Every operator acts on B(R) with the
  sup norm.

**Resolvents and derived quantities.**
* R_e = (I − K_e)⁻¹ and Ĝ_e = (I − K̂_e)⁻¹.
* σ is the first time of alarm or of return to a at a time ≥ 1.
* τ_a(e) = E_a[σ] = (Ĝ_e 1)(a).
* D_e = 1 − (Ĝ_e k_{a,e})(a) > 0.
* Λ(e) = E_a[τ] = τ_a/D (Lemma SM(d)).
* Score S_k = −(Z_k + e), which is i.i.d. N(0, 1) under P^e. M_n = Σ_{k≤n} S_k.
* L1(e) = E_a[Σ_{n<σ} |M_n|] and L2(e) = E_a[Σ_{n<σ} |M_n² − n|].

**Atom constants (the consumer's interface; THEOREM_TCT §1 (P4) and THEOREM_AD §4).** For a drift set E, a triple
(A0, A1, A2) is *admissible on E* if, for every e ∈ E, every f ∈ B(R) and j ∈ {0, 1, 2},

    |[∂_e^j R_e f](a)| ≤ A_j ‖f‖.                                                    (P4)

Theorem TC-T uses (P4) at exactly one place: |E''(e)(a)| ≤ A0‖φ''‖ + 2A1‖φ'‖ + A2‖φ‖ (THEOREM_TCT §1). **Any
admissible triple can therefore replace the supply in TC-T, and the frozen C2 consumer is valid with it.**

## 1. Statement

Let E = [x_lo, x_hi] be the drift cover interval of one cover cell (for this campaign, cell 307 of `cells.json`).

**Blocks.**
* Partition E by the C2 rule: N = max(1, ⌈(x_hi − x_lo)/(1/100)⌉) equal sub-blocks E_i.
* Let B_i ⊇ E_i be the outward 2^-20 dyadic hull of E_i (protocol P1, P2).

**Certified inputs.** For each B_i, let a set of certified rungs d ∈ {4, 6, 8} of the pinned certifier
(`c1b_certpw.certify_degree`, status CERTIFIED) give exact rationals. Each satisfies, **uniformly for e ∈ B_i**:

| input | inequality | certified by |
|---|---|---|
| τ | ≥ sup τ_a(e) | S1: taboo supersolution w_T = w_T(a) (Lemma T) |
| C_T | ≥ sup ‖Ĝ_e‖ | S1: sup_R w_T |
| Ā | ≥ sup Λ(e) | S2: whole-kernel supersolution W(a) (THEOREM_AD §4) |
| C_R | ≥ sup ‖R_e‖ | S2: sup_R W |
| τ_a,lo | ∈ (0, inf τ_a(e)] | S3 |
| D_lo | ∈ (0, inf D_e] | S3 |
| D1 | ≥ sup \|∂_e D_e\| | S3 |
| D2 | ≥ sup \|∂²_e D_e\| | S3 |
| L1_up | ≥ sup L1(e) | S3/S4 |
| L2_up | ≥ sup L2(e) | S3/S4 |

The constants are κ1 = 7978845609/10¹⁰ ≥ √(2/π) and κ2 = 4·φ(1)⁺ ≥ 4φ(1), where φ(1)⁺ is a rigorous upper
endpoint. Neither depends on e.

**Ladder composition (Lemma Lad).**
* Upper bounds are composed by the minimum over certified rungs: C_R, τ, C_T, Ā, τ_a,up, Ŝ2_up, T_N,up, D1, D2,
  L1_up, L2_up.
* Lower bounds are composed by the maximum: τ_a,lo, D_lo, Λ_lo.

**Block supply (declaration D14).** On each block, put

    Ā_eff = min(Ā, τ/D_lo),   δ_j = D_j/D_lo,   ρ_j = L_j,up/τ_a,lo,
    ρ1^Dv = κ1 C_T,   ρ2^Dv = 2κ1²C_T² + κ2 C_T,
    c_j = min( Ā_eff ρ_j ,  L_j,up/D_lo ,  Ā_eff ρ_j^Dv )                              (j = 1, 2)
    A1^B = min( c1 + Ā_eff δ1 ,                    κ1 C_R² )
    A2^B = min( c2 + 2 c1 δ1 + Ā_eff (2δ1² + δ2) ,  κ2 C_R² + 2κ1² C_R³ ).

**Cell supply.** A_j^cell = max_i A_j^{B_i} for j = 1, 2.

**Consumed supply.** Let S_I1 = (A0^I1, A1^I1, A2^I1) be C2's adopted componentwise-minimum supply for the cell:
{Lemma G, Dv′(REGISTRY_C1), Dv′(REGISTRY_C2)}, recomputed by the frozen consumer and reproducing C2's committed
record. Put

    S_RLR = ( A0^I1 ,  min(A1^I1, A1^cell) ,  min(A2^I1, A2^cell) ).

**Theorem RLR-307.**
1. If every block B_i has at least one certified rung, then S_RLR is admissible (P4) on E.
2. Consequently the frozen C2 consumer (TC-T and the K5-B direct clause) is valid with S_RLR. Its output Γ(5, k; S_RLR)
   is a certified upper quantity of the same type as C2's Γ(5, k; S_I1).
3. The consumer's own rule "`pass` ⇔ Γ < 0 (exact rationals)" then certifies the K5-B inequality for the cell,
   exactly as for any admissible supply.
4. If some block has no certified rung, the theorem asserts nothing: there is no RLR cell supply.

## 2. Proof

**Lemma S (reflection).** Let r(p, m) = (m, p). Then K_{−e} = r K_e r, K̂_{−e} = r K̂_e r and r(a) = a, and R is
r-invariant.
* *Proof.* Replacing (x, Z) by (r x, −Z) maps the update, both windows and the law of Z + e to those at −e. ∎
* Consequence: every quantity above is even in e, as a functional norm at the fixed point a or a supremum over R:
  τ_a, ‖Ĝ‖, Λ, ‖R‖, D, |D′|, |D″|, L1, L2, and the functional norms of ∂^j R at a.
* So the constants do not depend on whether a code base writes its drift as Z + e ~ N(0,1) or as Z − e ~ N(0,1).
  Certificates on B are certificates on −B.

**Step 1 (Sherman–Morrison, THEOREM_AD Lemma SM).** (R_e f)(a) = ν_e(f)/D_e, with ν_e(f) = (Ĝ_e f)(a) and
|ν_e(f)| ≤ τ_a‖f‖, because Ĝ ≥ 0.

**Step 2 (score representation, THEOREM_LR LR-1 on the taboo chain).**
* Hypotheses:
  * (H1) is the certified taboo supersolution w_T (Lemma TL: geometric tail of σ).
  * (H2) is Lemma K: e ↦ K̂_e is C^∞ in operator norm, and the survival set is e-free.
  * (H3) holds: the score is N(0, 1), and t ≡ −1.
* Conclusion: ν′(f) = E_a[Σ_{n<σ} f(X_n) M_n] and ν″(f) = E_a[Σ_{n<σ} f(X_n)(M_n² − n)], so |ν′(f)| ≤ L1‖f‖ and
  |ν″(f)| ≤ L2‖f‖.
* The same derivatives are also bounded by THEOREM_AD §4:
  * |ν′(f)| ≤ τ_a κ1 C_T ‖f‖;
  * |ν″(f)| ≤ τ_a(2κ1²C_T² + κ2 C_T)‖f‖.
  * These use ∂Ĝ = ĜK̂′Ĝ, ∂²Ĝ = 2ĜK̂′ĜK̂′Ĝ + ĜK̂″Ĝ and ‖K̂^(n)‖ ≤ E|He_n(Y)| ≤ κ_n.

**Step 3 (three bounds on each of |ν′/D| and |ν″/D|).** For e ∈ B:
* Λ(e) ≤ Ā.
* Λ(e) = τ_a/D ≤ τ/D_lo.
* Hence Λ ≤ Ā_eff.

Therefore

    |ν′/D| ≤ L1/D ≤ L1,up/D_lo,
    |ν′/D| = (L1/τ_a)(τ_a/D) ≤ ρ1 Ā_eff,        since ρ1 ≥ sup L1 / inf τ_a ≥ L1(e)/τ_a(e),
    |ν′/D| ≤ (τ_a/D) κ1 C_T ≤ Ā_eff ρ1^Dv,

so |ν′(f)/D| ≤ c1‖f‖. The same argument gives |ν″(f)/D| ≤ c2‖f‖.

**Step 4 (quotient rule; THEOREM_LR LR-3 and THEOREM_AD Lemma Dv′).**

    ∂(ν/D) = ν′/D − νD′/D²,    ∂²(ν/D) = ν″/D − 2ν′D′/D² + ν(2D′²/D³ − D″/D²).

With |ν| ≤ τ_a‖f‖, |D′|/D ≤ δ1 and |D″|/D ≤ δ2:
* |νD′/D²| ≤ Ā_eff δ1‖f‖;
* |2ν′D′/D²| ≤ 2c1δ1‖f‖;
* |ν(2D′²/D³ − D″/D²)| ≤ Ā_eff(2δ1² + δ2)‖f‖.

Hence the first entries of A1^B and A2^B bound |[∂R f](a)| and |[∂²R f](a)|.

**Step 5 (Lemma G, LR-4 form).**
* ∂R = R K′ R and ∂²R = 2RK′RK′R + RK″R.
* ‖K^(n)‖ ≤ κ_n (Lemma K, whole kernel).
* ‖R_e‖ = sup_R R_e 1 ≤ sup_R W ≤ C_R (Lemma T with K).
* Hence |[∂R f](a)| ≤ κ1C_R²‖f‖ and |[∂²R f](a)| ≤ (κ2C_R² + 2κ1²C_R³)‖f‖.
* A minimum of valid bounds is a valid bound, so A^B is admissible on B.

**Step 6 (Lemma Lad).**
* Every tabulated inequality concerns a rung-independent quantity, for example sup_B τ_a or inf_B D.
* The minimum of upper bounds of one quantity is an upper bound of it; the maximum of lower bounds is a lower bound.
* The combinations used in Steps 3–5 need only each input to bound its own quantity. For example, τ from rung 4 and
  D_lo from rung 8 still give Λ ≤ τ/D_lo.

**Step 7 (Lemma H, hull and cover).**
* A certificate valid for every e ∈ B_i is valid on E_i ⊆ B_i.
* ∪E_i = E. So for every e ∈ E, some i has e ∈ B_i and |[∂^j R_e f](a)| ≤ A_j^{B_i}‖f‖ ≤ A_j^cell‖f‖.

**Step 8 (consumed supply).**
* S_I1 is admissible on E: C2 adopted it, and each of its three members is Lemma G or Lemma Dv′.
* Componentwise minima of admissible triples are admissible, because (P4) is componentwise.
* So S_RLR is admissible, and A0 is S_I1's. ∎

*Remark (not used in the proof).* In the consumer (`c2_d5_forecast.direct`) the radius
rad = A0 p2 + 2A1 p1 + A2 p0 has p_j ≥ 0. So a componentwise smaller supply gives a nested, smaller enclosure
[lo, hi], and M = min(M0, max(|a|, |b|)) is monotone in it, provided [lo, hi] meets the recorded interval H.
* With admissible supplies both [lo, hi] and H contain the true value, so they meet.
* When they do not meet, the consumer falls back to M0 (M = M0 if a > b). Monotonicity is then not claimed.

**How each certified inequality is established (certification semantics, pinned code).**

* **S1 / S2 (supersolutions).** w − 1 − K̂_e w ≥ 0 and w ≥ 0 on R × B.
  * The residual is an exact G-form: a polynomial times φ and Φ at affine boundaries.
  * It is enclosed by integer Taylor models of order 10 on a box cover of R × B, adaptive, with every rounding
    outward (`c1b_kernel.gf_box_int`).
  * Lemma T then gives τ ≥ w(a) ≥ τ_a and ‖Ĝ‖ ≤ sup_R w.
* **S3 (linear functionals by tame error; D1).** For X = Ĝ(F), with a candidate X̃ and residual r:
  * |X(a) − X̃(a)| ≤ τ‖r‖ and ‖X − X̃‖ ≤ C_T‖r‖;
  * for triangular systems the errors compose through ‖K̂^(j)‖ ≤ κ_j;
  * this gives two-sided enclosures of τ_a, Ŝ2 = E_a Σ M_n², T_N = E_a Σ n, D, D′ and D″;
  * lower bounds for τ_a and Λ also come from subsolutions (D7(c)).
* **S4 (one-sided certificates; THEOREM_LR §cert (i′) and Lemma C0(ii)).**
  * Ŝ2 ≤ a(a) for a quadratic certificate a + b1μ + b2μ² with forcing μ².
  * L1 ≤ a(a) with forcing c/2 + g2μ² and 2c·g2 ≥ 1, since |μ| ≤ c/2 + μ²/(2c) ≤ c/2 + g2μ².
  * The checker requires A_lo > 0, C_lo ≥ 0 and B² ≤ 4A_loC_lo on every box of R × B and every owning x-region
    (D13 ownership).
  * T_N is bounded by a linear certificate. Then L1 ≤ min(certificate, √(τ_a,up Ŝ2_up)) (Cauchy–Schwarz).
  * L2 ≤ Ŝ2 + T_N, because |M² − n| ≤ M² + n.

## 3. Soundness claim

Suppose the pinned certifier implements S1–S4 as stated. Its correctness was reviewed in REVIEW_RLR_R2 and
REVIEW_RLR_R3_VERIFY, and it is re-qualified in this campaign (Q2, Q5, Q6). Then every triple produced by this
theorem's composition is admissible (P4) on its drift set, and the consumer's Γ with it is a valid K5-B quantity.

Soundness does **not** depend on:
* the float candidate generator (`c1b_float`, untrusted);
* any Monte Carlo.

Both only affect how tight the bounds are.

## 4. Limits of applicability

* Only the two-sided CUSUM kernel of Lemma K with K = 1/2, C = 11/2, the reachable set R, and atom a = (0, 0).
* Only dyadic blocks: the hull rule supplies them. Statements are block-uniform. A block's statement says nothing
  about a drift outside its hull.
* Only A1 and A2 are changed. A0 is the committed I1 value, so RLR cannot move the A0 term of the radius.
* With certified ρ, raw RLR is **not** guaranteed ≤ Dv′: LR-3 dominance holds for exact ρ only. Only the D14
  combination is guaranteed ≤ Dv′ and ≤ Lemma G, on the same certified inputs.
* The certifier is a single implementation. The independent reconstruction in this campaign covers:
  * the composition layers (assembly, ladder, cell max, final minimum);
  * the κ bounds;
  * the pins.

  It does not re-certify S1–S4 (protocol §6).
* Governance: the theorem is closure-only under floor r2. An RLR-bearing supply is neither a Lemma G nor a Lemma Dv′ r2
  supply, and it mixes certifiers. Nothing here adopts a cell, creates r6 or modifies floor r2.
