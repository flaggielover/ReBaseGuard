# Theorem TC-T — theorem TC at the CUSUM m = 5 tail: registry-free atom constants and a zero order-3 candidate

Status: written from the measured adopted inputs of cells 305–309 and **no** new real scientific value. Theorem TC
(`p5y_k5_lower_front_order3/theorem/THEOREM_TC.md`, adopted at `3c1c6b9c`, module pin `tc_rule.py`
`8d402d11…`) is reused **verbatim**: its setting §1, premises (P1)–(P3), statement §3 and proof §4 are unchanged.
This successor replaces exactly two of its *premise supplies*, because the tail domain e ∈ [1.6209, 2.0923] admits
neither of the ones the lower front used, and it sharpens a third from adopted evidence.

## 0. What the tail needs and the lower front did not

| theorem-TC premise | lower front (cells 11–44, e ∈ [0.0089, 0.0252]) | m = 5 tail (cells 305–309, e ∈ [1.6209, 2.0923]) |
|---|---|---|
| (P4) atom constants A0, A1, A2 | adopted certified operator registry r1 (`1b7f5da7…`) via Lemma Dv′ | **registry r1 certifies only e ∈ [0, 0.1147]** — no coverage. Replaced by **Lemma G** |
| Ĝ (the order-3 candidate of F) | the frozen order-3 producer's degree-12 candidate, one certified real evaluation per (cell, r) | **Ĝ := 0**, a legal fixed function; no real evaluation. Premise **(P2′)** |
| σ3, σ4 (true source derivative sups) | the frozen J/h Leibniz tower | the tower **intersected with the adopted Aux3 order-3 source and h evidence**. Premise **(P3′)** |

Everything else — the frozen K1 candidates, residuals and drift-aware norms, the frozen W enclosures, the assembly
table, the K5-B consumption rule — is the adopted machinery, unchanged.

## 1. Lemma G (registry-free atom constants)

Let C := `cells.json[cell].C_upper`, the frozen K1 one-sided block bound, so C ≥ sup_{e ∈ C} ‖(I − K_e)⁻¹‖ on the
cell, and let k_i := `cert.norms["k"][i]` ≥ sup_{e ∈ C} ‖K_i(e)‖ be the frozen drift-aware norms (theorem TC (P1)).
Then for every e ∈ C and every f ∈ B(X),

    |[R_e f](a)|    ≤ A0 ‖f‖,   A0 := C
    |[∂R_e f](a)|   ≤ A1 ‖f‖,   A1 := k₁ C²
    |[∂²R_e f](a)|  ≤ A2 ‖f‖,   A2 := k₂ C² + 2 k₁² C³

*Proof.* |[R f](a)| ≤ ‖R f‖ ≤ ‖R‖ ‖f‖ ≤ C‖f‖. With ∂R = R K₁ R and ∂²R = 2 R K₁ R K₁ R + R K₂ R (theorem AD §4, the
e-derivatives of e ↦ R_e; R_e exists and is analytic on C by (P1) and the invertibility the frozen K1 stack asserts
for every cell through C_upper), submultiplicativity gives ‖∂R‖ ≤ C k₁ C and ‖∂²R‖ ≤ 2 C k₁ C k₁ C + C k₂ C, and
evaluation at a is bounded by the sup norm. ∎

These are **exactly** the constants of the frozen generic K1 DAG rules
`eps(F) = C f_F`, `eps(D) = C(f_D + k₁ eps(F))`, `eps(H) = C(f_H + k₂ eps(F) + 2 k₁ eps(D))` rewritten in the form
A0 f_H + 2 A1 f_D + A2 f_F, so Lemma G asserts nothing the adopted K1 stack does not already assert. Lemma Dv′ of
theorem AD is strictly sharper where a certified operator registry exists; Lemma G needs none, which is why it is the
tail's supply. Numerically A0 = 5.782–7.733, A1 = 26.65–47.69, A2 = 277.9–646.2 on cells 309…305.

Theorem TC's proof uses (P4) at exactly one place — §4 step 3, `|E''(e)(a)| ≤ A0‖φ''(e)‖ + 2A1‖φ'(e)‖ + A2‖φ(e)‖`.
Lemma G supplies that inequality, so §3's conclusion holds verbatim with these A.

## 2. Premise (P2′) — the zero order-3 candidate

Theorem TC §1 lets F̂, D̂, Ĥ, Ĝ be **four fixed functions**; nothing requires Ĝ to approximate F_r'''. Take Ĝ := 0,
so the Taylor candidate is the quadratic F̃(e) = F̂ + tD̂ + (t²/2)Ĥ. Theorem TC's own (P2) identity then reads, at e0,

    φ'''(e0) = −[(I − K)·0 − K₃F̂ − 3K₂D̂ − 3K₁Ĥ − Ŝ'''] + (S''' − Ŝ''') = S'''(e0) + 3K₁Ĥ + 3K₂D̂ + K₃F̂

so with σ3 ≥ ‖S_r'''(e0)‖,

    f_G := 3 k₁ s_H + 3 k₂ s_D + k₃ s_F + σ3      satisfies  ‖φ'''(e0)‖ ≤ f_G,

and the two other order-3 inputs of theorem TC vanish exactly: **s_G = 0** (Ĝ = 0 so ‖Ĝ‖ = 0, and (P3)'s envelope
loses every s_G term) and **|Ĝ(a)| = 0** (the centre-motion half-width ρ|Ĝ(a)| of §3 is zero, i.e. the enclosure
stays centred on the adopted order-2 candidate Ĥ_r(a) with no motion term).

The implementation adds the adopted `eps_src[3]` = ε_mid(src(r,3)) on top of f_G. That is a valid extra allowance —
the identity above already carries the **true** source — and it keeps the field semantics of the frozen `tc_rule`
(`fG = delta_G + eps_src[3]`) intact, so the frozen arithmetic is used with no reinterpretation.

**What is traded.** A real Ĝ makes f_G ≈ 10⁻³ but pays ‖Ĝ‖ and |Ĝ(a)|; Ĝ := 0 makes those zero but pays
f_G ≈ 4.9–8.9. On the lower front, where ρ ≈ 2.7·10⁻⁴, the ρ·f_G term is negligible and the real candidate is
strictly better. On the tail, where ρ ≈ 4.1–5.4·10⁻², the trade reverses unless the order-3 candidate's certified
supremum is below ≈ 10.5–64.7 × s_H (per cell; `evidence/forecast_r2/TAIL_FORECAST_R2.json`
`critical_sup_G_over_sup_H_ratio`). Both choices are valid enclosures, so a campaign may compute both and intersect.

## 3. Premise (P3′) — σ3 and σ4 from adopted Aux3 evidence

Theorem TC (P3) bounds the true source derivatives by the frozen J/h Leibniz tower
‖h_1‖ ≤ 1, ‖h_1^{(n)}‖ ≤ sup‖S_0^{(n−1)}‖ (h_1' = −S_0 exactly), ‖h_j‖ ≤ 1,
‖h_j^{(n)}‖ ≤ Σ_i C(n,i) k_i ‖h_{j−1}^{(n−i)}‖, and σ_n(r) = Σ_i C(n,i) j_i ‖h_r^{(n−i)}‖ for r ≥ 1.
On the tail that tower is loose at order 3: σ3 = 5.9, 16.9, 36.5, 67.2 for r = 1…4 at cell 309, against
adopted values of 3.04, 3.41, 3.81, 2.25.

The adopted Aux3 evidence already carries certified order-3 quantities for the **same** objects
(`auxiliary_evidence.candidate_suprema['S:r:3'], ['Sclosed:0:3'], ['h:j:3']` and the matching
`auxiliary_evidence.midpoint_eps` entries, all inside the frozen producer's identity gate). Since
‖S_r'''(e0)‖ ≤ ‖Ŝ_r'''(e0)‖ + ‖S_r'''(e0) − Ŝ_r'''(e0)‖ and likewise for h_j,

    adopted3(r) := candidate_suprema['S:r:3'] + midpoint_eps['S:r:3']      bounds ‖S_r'''(e0)‖
    adoptedh(j) := candidate_suprema['h:j:3'] + midpoint_eps['h:j:3']      bounds ‖h_j'''(e0)‖

**Those are MIDPOINT bounds, and the two premises they feed are not both midpoint premises.** σ3 enters only f_G,
i.e. theorem TC premise (P2), which is stated at e0 — a midpoint bound is exactly the right object there. σ4 enters
Env4, i.e. premise (P3), which must hold for **every** e in the cell. Review r1 note N1 found that (P3′) r1
substituted the midpoint bound into the order-3 slot of the tower and then ran the order-4 recursion on it, which is
unsound. (P3′) r2 therefore keeps **two** towers:

    midpoint tower   t_mid[j,3] = min( tower[j,3], adoptedh(j) )                 -> sigma3 only
    cell tower       t_cell[j,3] = min( tower[j,3], adoptedh(j) + rho * tower[j,4] )
                     t_cell[j,4] = min( sum_i C(4,i) k_i t_cell[j-1,4-i] , tower[j,4] )    -> sigma4 only

The cell tower's order-3 slot carries the mean-value correction ‖h_j'''(e)‖ ≤ ‖h_j'''(e0)‖ + ρ·sup_C‖h_j⁗‖ (h_j is
analytic on the cell), with sup_C‖h_j⁗‖ taken from the **unrefined** tower, which is cell-uniform by (P3); the
order-4 entries are then re-derived from the corrected lower orders, which is valid because the Leibniz recursion
holds pointwise in e, so cell-uniform inputs give a cell-uniform output. The minimum of two valid upper bounds is a
valid upper bound, so (P3′) r2 is sound by construction. It reduces σ3 to 0.69–3.81 and σ4 from ≈ 355 to ≈ 235 at
r = 4, and the resulting whole-cell magnitude from 4.2617 to 3.9643 at cell 309.

## 4. Statement and consumption

With A from Lemma G, f_G from (P2′), σ3/σ4 from (P3′) and every other input the adopted K1/Aux3 value, theorem TC §3
holds unchanged: for every e in the cell

    p0 = f_F + ρ f_D + ρ² f_H/2 + ρ³ f_G/6 + ρ⁴ Env4/24,  p1 = f_D + ρ f_H + ρ² f_G/2 + ρ³ Env4/6,
    p2 = f_H + ρ f_G + ρ² Env4/2,   rad_r = A0 p2 + 2 A1 p1 + A2 p0,   half_r = rad_r   (|Ĝ(a)| = 0)
    R''_m(e) ∈ 𝓗_m := Σ_{r<m} (1/m)·[Ĥ_r(a) − half_r, Ĥ_r(a) + half_r] + Σ c(m)·𝒲_{(r,j)}

with Env4 = σ4 + 6k₂ s_H + 4k₃(s_D + ρ s_H) + k₄(s_F + ρ s_D + ρ² s_H/2) (the (P3) envelope at s_G = 0).
Consumption is theorem TC §6 unchanged: H_k ← H_k ∩ 𝓗_m(k) (refuse if empty), M_k ← min(M_k, mag(H_k)), then the
frozen `k5b_literal`.

## 5. Identity of the replayed inputs

`cert.norms`, `cert.sup[F|D|H, r, 0]`, `sup_S0`, `Ĥ_r(a)` and the W enclosures are not stored in the adopted K1
record; they are recomputed by the frozen chain in replay mode (`code/tct_inputs.py`), where the frozen producer's
identity gate compares 262 dependent fields (every object `delta_mid`, every `eps_mid` and `eps_cell` node, the Aux3
midpoint eps, Aux3 object residuals and Aux3 candidate suprema) against the sealed record exactly. Two further gates
cover the fields that one does not reach:

- **derived identity gate** (`tct_rule.derived_identity_gate`): the adopted record's `R2_interval` is rebuilt for
  every m from the replayed Ĥ_r(a) and W enclosures and the record's own `eps_cell_refined`, exactly as the frozen
  propagate/assembly composes it, and must be *contained* in the record interval with relative endpoint agreement
  ≤ 10⁻⁶. Measured worst gap: 2.7–3.6 · 10⁻⁸ (the record's enclosure adds its eps as an outward-rounded Arb radius,
  so it is very slightly wider). A wrong Ĥ_r(a) or W moves an endpoint by O(10⁻²–1).
- **two independent rule paths**: `tct_rule.tail_enclosure` (through the frozen `tc_rule` functions) and
  `tct_rule.tail_enclosure_crosscheck` (re-derived from this document in generic form) must agree as exact rationals
  on every cell and every m. They do, on all 20 pairs. Since review r1 note N15 the second path shares **no function**
  with the first — it imports no `tc_rule` and re-derives both towers, both σ's, the Taylor sums, the (P3) envelope
  and the assembly table itself — because in r1 both paths called the same `h_tower`/`sigma_source` and the 20/20
  agreement was therefore silent on exactly the (P3′) defect that note N1 found.

## 6. What is not claimed

Nothing about R, R′ or R‴ values beyond this enclosure; no whole-function sup norm is improved; no order-3 candidate
of F is proposed, computed or recorded, so the guard stays DENY and Campaign A's note N5 trust surface is not entered.
The enclosure is **not** by itself sufficient for cells 306–309: it reaches 0.94×, 0.76×, 0.61× and 0.50× of what
the frozen K5-B needs there, and closes cell 305 with a margin of 1.149× — see `phase_c/EXECUTION_DECISION.md`.

`tail_object` also accepts a **non-zero** order-3 supply, so a route that proposes a real Ĝ is scored on the same
(P3′) premise supply; (P3′) is a statement about the source and is independent of the choice of Ĝ (review r1 note N4).
