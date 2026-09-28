# A0 dependency graph for CUSUM m = 5 tail cells (r0)

**Target-free.** No number of any cell 305–309 appears here (committed values live in `history/HISTORY_308.md`).
Node ids N* refer to the overnight graph `p5y_k5_tail_overnight_research/graph/K5_TAIL_DEPENDENCY_GRAPH.md`, which
covers the whole chain from primitives to Γ. This file expands the order-0 constant A0 and everything it touches.

## 1. Definition and sharp value

* **A0 is admissible on a drift set E** iff |[R_e f](a)| ≤ A0‖f‖ for all e ∈ E, f ∈ B(R) (THEOREM_TCT (P4), j = 0).
* **Sharp value** (THEOREM_AD Lemma SM(d)): at one drift, sup_{‖f‖≤1} |[R_e f](a)| = τ_a(e)/D_e = Λ(e) = E_a[τ](e),
  attained at f ≡ 1. So the smallest admissible uniform A0 on E is sup_{e∈E} Λ(e).
* **Where the sup lies** (Theorem M): for E = [x_lo, x_hi] with x_lo ≥ 0, sup_E Λ = Λ(x_lo).

## 2. How the committed supply S_I1 provides A0 (C2)

    A0^I1 = min( A0^G , A0^{Dv′, C1} , A0^{Dv′, C2} )         (componentwise min over supplies, C2 combination rule)
    A0^G   = C_upper ≥ sup_e ‖R_e‖  = sup_e sup_x E_x[τ]       (Lemma G; sup over ALL starting states)
    A0^Dv′ = Ā_eff = min( Ā , τ/D_lo )                          (Lemma Dv′ r2; per registry, worst sub-block of the cell)
    Ā     = W(a), W ≥ 1 + K_e W uniformly on a registry block   (whole-kernel polynomial supersolution)
    τ     = w_T(a), w_T ≥ 1 + K̂_e w_T uniformly on the block    (taboo supersolution)
    D_lo  ≤ inf_block D_e                                        (tame-error chain / SM bound)

The binding branch at the tail cells is recorded in committed history (C3 §K; `history/`), not repeated here.

## 3. Where A0 is consumed

| consumer site | form | note |
|---|---|---|
| TC-T radius (N26) | rad_r(s) = **A0**·p2(s) + 2A1·p1(s) + A2·p0(s), p2(s) = f_H + s f_G + s²Env4/2 | the only place (P4) is used (TC §4 step 3), pointwise in t |
| frozen direct clause (N30) | radius at s = ρ for every t; ρ x_hi M | whole-cell charge |
| A1, A2 under Dv′ / D14 (N17) | A1 = Ā_eff(κ₁C_T + δ₁), A2 = Ā_eff(…), RLR: c_j = min(Ā_eff ρ_j, L_j/D_lo, Ā_eff ρ_j^Dv) | **the same Ā_eff multiplies all three constants** |
| g_hi (N15) | generic midpoint eps C·f (not A0) | AD Corollary T not applied on the tail |
| Λ floor (N34) | A0 ≥ sup_E Λ | constraint only; never enters Γ |

## 4. Slack inventory for the A0 channel (classification per brief §6)

| # | where | what is lost | class | route that addresses it | needs |
|---|---|---|---|---|---|
| S1 | SM(d) | nothing: A0 = Λ(e) is sharp for a norm-only order-0 bound | STRUCTURAL (floor) | none within norm-only bounds; RSO (residual-specific) leaves the family | data (pointwise residuals) |
| S2 | uniform A0 over the cell | Λ(x_lo) charged at every t although Λ decreases across the cell (Theorem M) | STRUCTURAL (consumer uniformization) | block-resolved constants in TC-P + TPT-B (Theorem MB) | nothing new (theory + certificates) |
| S3 | Ā block-uniform supersolution | a single supersolution valid on a whole block pays Λ*(E) ≥ sup_E Λ (C2b A0_TIGHTNESS §1) | CERTIFICATE_SLACK | Theorem M: certify pointwise at the block's left endpoint (Lemma M-U) | a pointwise certifier |
| S4 | Ā polynomial/PL family and discretisation | supersolution family cannot follow E_x[τ] exactly | NUMERICAL / CERTIFICATE_SLACK | tighter families (C2b PL, higher degree), ladder min | CPU |
| S5 | τ/D_lo branch | two certificates (taboo upper, escape lower) compound; D_lo tame error | CERTIFICATE_SLACK | superseded by S3 route when U < τ/D_lo | — |
| S6 | Lemma G C_upper | sup over all starting states, not the atom | STRUCTURAL (wrong functional) | not used when Dv′ is available | — |
| S7 | worst sub-block per registry | cell constant = worst block, used on every block | COVER_SLACK | block-resolved constants (Theorem MB) | nothing new |
| S8 | outward dyadic hulls, rational rounding | tiny | NUMERICAL (negligible) | — | — |
| S9 | first certifying rung (C2 rule) vs min over a ladder | the first rung that certifies is used, not the best | IMPLEMENTATION_SLACK | ladder minimum (Lemma Lad) | CPU |
| S10 | A0 × p2(ρ) in the direct clause | the Taylor profile terms linear and quadratic in s are charged at s = ρ over the whole transport | STRUCTURAL (assembly) | TPT / TPT-B (THEOREM_TPT) | nothing new; **incident-01 liability** |
| S11 | A0 × ρ f_G | f_G is a norm-only surrogate for an order-3 signed point value | STRUCTURAL (surrogate) | SC composite sup; real order-3 Ĝ | data (payloads) / governed real compute |
| S12 | A0 × Env4 | order-4 source never measured; Leibniz tower | STRUCTURAL | Hermite tower (theory only) | theory |
| S13 | Ā_eff shared by A1, A2 | any excess in Ā_eff is multiplied into both derivative constants | STRUCTURAL propagation | Lemma Dv′-M / D14-M (one tighter Ā′ tightens all three) | a pointwise certifier |

Dependencies of A0 on other quantities, as asked in brief §6:
* **D_lo, τ:** through the τ/D_lo branch (S5) and, for A1/A2, through δ_j = D_j/D_lo and C_T (not through A0 once
  U binds).
* **Ā:** replaced by Ā′ = min(Ā, U) (Lemmas Dv′-M, D14-M).
* **uniformization:** S2 and S7.
* **cover:** the cell width ρ multiplies the s-dependent profile terms (S10); real refinement needs new K1 records.

## 5. Consequence for route design (target-free)

The committed C3 knockout (history H1.3) shows that the A1/A2 channel alone cannot close cell 308 under the frozen
consumer. The slack classes that remain host-free and data-free are **S2, S3, S4, S7, S9, S10, S13**. They act on
different inequalities and compose (Theorem MB): one tighter certified Ā′ (S3/S4/S9) propagates to A0, A1 and A2
(S13); block resolution (S2/S7) and the Taylor-profile transport (S10) change how the constants are charged.
S1, S11 and S12 need data, governed real computation or new theory. No selection among S2–S13 is made by estimated
effect on any tail cell: every sound, reviewed component is included (charter rule 5).
