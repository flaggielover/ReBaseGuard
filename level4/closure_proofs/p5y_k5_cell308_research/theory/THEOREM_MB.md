# Theorem MB — Theorem-M block atom constants and their block-resolved transport (draft r0)

**Status: THEORY_ONLY (coordinator draft r0, 2026-09-28). Needs an independent proof review before any freeze.**
It states what the certificates prove and **nothing about the value of any consumer output** at any cell.
No number of any CUSUM m = 5 tail cell appears in this file.

It assembles, and adds three short lemmas to, results proved and reviewed elsewhere:

| source | what is used | status there |
|---|---|---|
| THEOREM_AD (`p5y_k5_perron_deflated_resolvent/theorem/THEOREM_AD.md`) | Lemma K, Lemma T, Lemma SM (a)–(d), Lemma Dv, Lemma Dv′ r2, whole-kernel supersolution | adopted |
| THEOREM_TCT (`p5y_k5_m5_tail_closure/theorem/THEOREM_TCT.md`) | premises (P1), (P2′), (P3′), (P4); Lemma G; §4 step 3 is the only use of (P4) | adopted |
| Theorem M (`p5y_k5_tail_overnight_research/streams/C_308/A0X/EXCLUSION_308.md` §c) | P_e(τ > n) even and nonincreasing in \|e\| from the atom | REVIEW_THEOREM_M_R1 ACCEPTED_WITH_CORRECTIONS (applied) |
| THEOREM_LR / THEOREM_RLR307 (`p5y_k5_cell307_rlr_r1/theory/THEOREM_RLR307.md`) | declaration D14, Lemma S, Lemma H, Lemma Lad | QUALIFICATION_ACCEPTED, EXECUTION_ACCEPTED, ADJUDICATION_ACCEPTED (cell 307) |
| THEOREM_TPT (`p5y_k5_tail_overnight_research/streams/E_assembly/THEOREM_TPT.md`) | Theorem TPT, Lemma TC-P, Theorem TPT-B, Proposition TPT-D | REVIEW_TPT_R1: mathematics sound; implementation r2 VALIDATED_NON_TARGET |

## 0. Objects

As THEOREM_RLR307 §0. State x = (p, m) ∈ R = {0 ≤ p, m ≤ 5 : p = 0 or m = 0 or p + m ≤ 4}; K = 1/2, H = 5,
C = H + K = 11/2; increment Z with Z + e ~ N(0, 1); T(x, z) = ((p + z − K)⁺, (m − z − K)⁺); alarm-free window
A(x) = [m − C, C − p]; (K_e f)(x) = ∫_{A(x)} f(T(x, z)) φ(z + e) dz; atom a = (0, 0); R_e = (I − K_e)⁻¹;
Λ(e) := E_a[τ](e) = (R_e 1)(a) = τ_a(e)/D_e (Lemma SM(d)).

A triple (A0, A1, A2) is **admissible on a drift set E** if |[∂_e^j R_e f](a)| ≤ A_j‖f‖ for every e ∈ E, every
f ∈ B(R) and j ∈ {0, 1, 2} (THEOREM_RLR307 (P4) = THEOREM_TCT (P4)).

## 1. Theorem M (restated; proved and reviewed elsewhere)

For the chain started at the atom, every n ≥ 0 and 0 ≤ e ≤ e′: P_e(τ > n) = P_{−e}(τ > n) ≥ P_{e′}(τ > n). Hence Λ
is even and nonincreasing on [0, ∞).

*Proof outline* (EXCLUSION_308 §c.2–c.6). From the atom, {τ > n} = {|S_t − S_s| ≤ H + K(t − s), 0 ≤ s < t ≤ n}
(V-mask; the alarm fires on the unclipped update), a closed, convex, centrally symmetric set A_n in the partial-sum
coordinates; S = R_n − e(1, …, n) with R_n Gaussian, symmetric and unimodal; Anderson's inequality (or Prékopa)
gives the monotonicity; the tail-sum formula gives Λ. **Scope:** atom start (and diagonal starts); nothing about
off-diagonal starts, taboo quantities τ_a, D, C_T, or the size of Λ′.

*Consistency with the kernel.* The unclipped p-update exceeds H iff z > C − p and the m-update iff z < m − C, i.e.
alarm iff z ∉ A(x) — the same window as in K_e. The V-mask identity is the Lindley recursion unrolled from p₀ = m₀ = 0.

## 2. Lemma M-U (one drift controls a block)

Let b ≥ 0 and let U be a certified upper bound U ≥ Λ(b). Then for every block B ⊆ [b, ∞):

    sup_{e ∈ B} Λ(e) ≤ U.

By evenness the same holds for B ⊆ (−∞, −b]. *Proof.* Theorem M. ∎

**Monotone envelope.** If b₀ < b₁ < … < b_k are left endpoints of consecutive blocks (all ≥ 0) with certified
U_i ≥ Λ(b_i), then Ū_j := min_{i ≤ j} U_i ≥ sup_{e ≥ b_j} Λ(e), so Ū_j is valid on block j. This rule is
result-free (it takes a minimum of valid bounds).

**Only Λ transfers.** A certificate computed at the single drift b may also produce τ, C_T, D_lo, D1, D2, L1, L2
*at b*. **None of these is valid on B**: Theorem M does not cover taboo quantities or derivatives (EXCLUSION_308
§c.8). Only the whole-kernel value U = W(a) of a supersolution W ≥ 1 + K_b W, W ≥ 0 (THEOREM_AD §4) transfers.

## 3. Lemma A0-M (order-0 channel)

With B, U as in Lemma M-U: A0 := U satisfies |[R_e f](a)| ≤ A0‖f‖ for all e ∈ B, f ∈ B(R).

*Proof.* Lemma SM(c)–(d): |[R_e f](a)| ≤ Λ(e)‖f‖ ≤ U‖f‖. ∎

## 4. Lemma Dv′-M (Lemma Dv′ with a Theorem-M Ā)

Lemma Dv′ r2 (THEOREM_AD §4) holds under the hypothesis "Ā ≥ sup_E E_a[τ]" with **any** certified Ā; its proof bounds
every term by (τ_a/D)(e) × (a tame factor) and uses τ_a/D = Λ(e) ≤ Ā. Hence on a block B with certified τ, C = C_T,
D_lo, D1, D2 (valid uniformly on B) and U as in Lemma M-U,

    Ā′ := min(Ā_B, U),   Ā′_eff := min(Ā′, τ/D_lo),
    A0 = Ā′_eff,   A1 = Ā′_eff (κ₁C_T + δ₁),   A2 = Ā′_eff (2κ₁²C_T² + κ₂C_T + 2κ₁C_Tδ₁ + 2δ₁² + δ₂)

is admissible on B (δ_j = D_j/D_lo; Ā_B any block-uniform whole-kernel certificate, or +∞ if none). ∎

## 5. Lemma D14-M (the RLR block supply with a Theorem-M Ā)

In THEOREM_RLR307 §1 (declaration D14) and its proof §2, the drift-uniform whole-kernel bound Ā enters only through
Step 3, "Λ(e) ≤ Ā for e ∈ B", and through Ā_eff = min(Ā, τ/D_lo). Replacing Ā by Ā′ = min(Ā, U) with U as in
Lemma M-U keeps Step 3 true. Hence the D14 block supply computed with Ā′ in place of Ā is admissible on B. ∎

(Every other D14 input — τ, C_T, C_R, τ_a,lo, D_lo, D1, D2, L1_up, L2_up — must still come from a **block-uniform**
certificate on B, exactly as in THEOREM_RLR307.)

## 6. Block supply

Let the cover cell E = [x_lo, x_hi] (x_lo > 0) be partitioned by a rule fixed in advance into sub-intervals E_i with
outward dyadic hulls B_i ⊇ E_i, all with left endpoint b_i ≥ 0. For each i let S_i be the componentwise minimum of
every triple that is admissible on B_i and available from a certificate, among:

1. the committed cell-level supply S_I1 (admissible on all of E, hence on B_i);
2. Lemma Dv′-M on B_i, when block-uniform τ, C_T, D_lo, D1, D2 are certified on B_i;
3. Lemma D14-M on B_i (the RLR block supply with Ā′), when the RLR block certificate exists;
4. Lemma G on B_i (C_R from a block-uniform whole-kernel certificate).

A componentwise minimum of admissible triples is admissible (each inequality in (P4) is separate).

## 7. Theorem MB (composition with the block-resolved transport)

Assume the frozen TC-T premises (P1), (P2′), (P3′) for the cover cell E, with midpoint e0, half-width ρ, x_lo > 0,
and the block triples S_i admissible on B_i. Let H_final be any valid whole-cell enclosure of R″_m on E (for example
the committed consumed enclosure). Then:

1. (Lemma TC-P, pointwise in t.) For t ∈ E ∩ B_i, s = |t − e0|:
   |F_r″(t)(a) − Ĥ_r(a)| ≤ rad_r^{(i)}(s) := A0^{(i)} p2(s) + 2A1^{(i)} p1(s) + A2^{(i)} p0(s), with the profile
   polynomials p_j(s) of THEOREM_TPT §2 (Ĝ ≡ 0 on the TC-T path). TC's proof uses (P4) only pointwise in t
   (TC §4 step 3), so the triple of any block containing t may be used.
2. (Profile enclosure.) L(t) := max(H_final.lo, lo_i(s)) ≤ R″_m(t) ≤ min(H_final.hi, hi_i(s)) =: U(t).
3. (Theorem TPT-B.) For every e ∈ E, g_m(e) ≤ g_hi + P*_B, where P*_B is the maximum of 0 and of the running
   transport integrals at the piece ends (pieces = the partition of [x_lo, e0] and [e0, x_hi] by block ends).
4. Hence **Γ_MB := g_hi + P*_B is a certified upper bound on sup_{e ∈ E} g_m(e)**, the same quantity that the K5-B
   direct clause bounds by g_hi + ρ x_hi M. If Γ_MB < 0 (exact rationals), then g_m < 0 on E, which is the K5-B
   inequality on that cell.

*Proof.* (1) is Lemma TC-P with (P4) applied at each t with the constants of a block containing t. (2) intersects two
valid enclosures. (3) is Theorem TPT-B (THEOREM_TPT §2b): within one piece the integrand is monotone in s, the
running integral is quasi-convex on each piece, and its supremum over the cell is attained at a piece end. (4)
follows from (3). ∎

**Dominance (Proposition TPT-D plus monotonicity).** P*_B is nondecreasing in every block constant. If S_i ≤ S_I1
componentwise for all i (true by construction, item 1 of §6), then
Γ_MB ≤ Γ_TPT(S_I1) ≤ Γ_C5T(S_I1) ≤ Γ_frozen(S_I1), with the same g_hi and the same enclosure inputs.

## 8. What changes, and the governance class

| item | change |
|---|---|
| K1 records, TC-T inputs (f_*, Env4, W terms, Ĥ_r(a), g_hi, H_final, cover) | **unchanged** |
| atom constants | block-resolved, each a minimum including the committed S_I1 |
| consumer | the direct clause is replaced by the TPT-B transport (a different certified bound on the same quantity sup g_m) |
| closure criterion | **unchanged**: a certified upper bound on sup_cell g_m that is < 0 (strict) |
| floor r2 | **closure-only**: floor r2 binds adoption to C2's consumer path with only S substituted; MB changes the consumer and the constants' certifiers. No adoption, no r6. |

## 9. Open obligations before this can be FREEZE_READY

* O1. Independent proof review of Lemmas M-U, A0-M, Dv′-M, D14-M and Theorem MB (including the claim that TC-T uses
  (P4) only pointwise in t, and the cap/intersection step 2 with a block-resolved profile).
* O2. A pointwise Λ certifier that is deterministic, persisted and independently re-verifiable (streams A0, VERIFY).
* O3. The TC-T input extraction and the TPT-B consumer on the frozen path, with reproduction gates (stream ASSEMBLY).
* O4. An independent reconstruction of the composition layers (block supply, envelope, ladder, TPT-B integral).
* O5. Incident-independence review (incident 01 applies to any profile transport; COORDINATOR_EXPOSURE_DISCLOSURE).
