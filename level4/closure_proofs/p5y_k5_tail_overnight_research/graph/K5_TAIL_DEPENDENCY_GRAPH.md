# K5 tail dependency graph — CUSUM m = 5, cells 306–309

This graph runs from the primitive certified quantities to the adoption quantity Γ. It is the Phase-1 deliverable of
the overnight campaign. The machine-readable companion is `K5_TAIL_DEPENDENCY_GRAPH.json`.

**Provenance.** The graph synthesizes three read-only reconstructions, done under quarantine. Each reconstructor
computed no number for cells 305–309 and quoted everything with file:line:
* `sources/graph_A_consumer.md`: the consumer chain, nodes N1–N34 with Def/Impl/Src/Val/Bound/→Γ/Scope/Dom/Impr/Sci/Frozen;
* `sources/graph_B_operators.md`: the operator constants, and I1 vs I2 at 306;
* `sources/graph_C_inputs.md`: K1 inputs, order-3, sup-norm, cover, 308, and R(e).

Every row below points to the node entry holding the full citations. **No quantity in this document was computed for
any target cell.** The only numbers present are committed values, quoted.

## 0. The object

* **Target proposition H3a** (`p5y_postk1_precompute_resolution/K5_TARGET_AND_THIRD_ORDER.md`): `s(e) = −R(e)/e` is
  strictly decreasing on (0, 2].
  * R = R_{CUSUM,m}(e) is the expected mean of the last `min(m, τ)` raw N(0,1) draws at alarm, given entering error e
    (graph C §6).
  * In operator form, `R_m(e) = (1/m) Σ_{r<m} F_r(e)(a) + Σ_{1≤t<m} Σ_{r<t} (1/t − 1/m) W_(r,t−r−1)(e)(a)`, where:
    * `F_r = (I − K_e)⁻¹ S_r` and `W = K^j S_r`;
    * K_e is the killed two-sided CUSUM kernel (H = 5, K = 1/2, state (p, m), atom a = (0,0));
    * the increment satisfies z + e ~ N(0,1);
    * the alarm is on the unclipped update.
* **K5-B direct clause** (`p5y_k5_feasibility/K5_GLOBAL_BRIDGE.md`): a cell passes if
  `Γ_k = hi(R_k − e0 D_k) + ρ_k x_k M_k < 0`, where `M_k ≥ sup_cell |R''_m|`. The proof takes the mean value of
  `g = R − eR'` about e0.
* **Adoption quantity** (floor r2, FLR:76): Γ is computed by the frozen C2 consumer path (`c2_d5_forecast.py` blob
  18403dbe + `deflated_consume.py` a0a836fa + `tct_rule.py` 98f6eee4 + the k5b_literal direct clause), with only the
  atom constants S substituted.
  * This is the direct clause, **not** C5-T (graph A §2).
  * C5-T is authoritative for scientific statements, and the C8/C9 factors are C5-T numbers.
  * Floor r2's base-clause wording ("the campaign's own frozen closure rule") is ambiguous against its pinned
    adoption quantity (graph A §5).

### Binding-regime closed form (committed facts, graph A §0.2)

On all four cells three committed facts hold:
* 𝓗 ⊆ R2_interval;
* the lower endpoint binds;
* C_lo < 0.

So, symbolically:

    Γ(S) = [R.hi − e0·D.lo]  +  ρ·x_hi·|C_lo|  +  ρ·x_hi·( A0·P̄2 + 2·A1·P̄1 + A2·P̄0 ),   P̄j = (1/5) Σ_r p_j(r).

Γ is affine in (A0, A1, A2). Under Lemma Dv′, all three are proportional to `eff = min(Ā, τ/D_lo)`.

## 1. Nodes

Abbreviations for the columns:
* **Frozen:** on the floor-r2 consumer path;
* **Impr:** theoretically improvable;
* **NS:** improvement needs new science (T), new real compute (R), new data or toolchain (D), or governance only (G);
* **Dom:** dominance per committed evidence, quoted.

| id | node | definition (short) | bound type | enters Γ via | scope | Dom (committed) | Impr | NS | Frozen | detail |
|---|---|---|---|---|---|---|---|---|---|---|
| N1 | e0, ρ, x_lo, x_hi | cover cell `[e0−ρ, e0+ρ]` | exact rational | transport factor ρ·x_hi, and the Taylor radius inside TC-T | per cell | halving ρ closes 307–309 (C5 oracle, **diagnostic**; it scales only the Taylor ρ, graph A §5) | yes (refine) | R + G | yes | A:N1 |
| N2/N3 | R_k ∋ R(e0), D_k ∋ R′(e0) | K1 midpoint Arb balls; generic eps: eps(F)=C f_F, eps(D)=C(f_D+k1 eps(F)) | two-sided certified | g_hi only | per cell | g_hi "59–60 % of the closure deficit" (C6 adj :606) | **yes**: AD Corollary T (atom-functional eps) is adopted but applied only on cells 0–148 | T-light (existing theorem) + G | yes | A:N2 |
| N4 | H = R2_interval, M_R2 | K1 whole-cell enclosure of R″ | two-sided | intersection ∩ 𝓗, M cap | per cell | not binding (mag 𝓗/M_R2 ≈ 0.65) | irrelevant | — | yes | A:N4 |
| N5 | C = C_upper | ≥ sup ‖(I−K_e)⁻¹‖ | upper | Lemma G A0 | per cell | never selected on the tail | — | R | yes | A:N5 |
| N6 | k_i, j_i | ≥ sup ‖K_i(e)‖, ‖J_i‖ | upper | Lemma G; f_G; Env4; towers | per cell | — | frozen | R | yes | A:N6 |
| N7 | δ_{F,D,H}, ε_src | midpoint residuals and source errors | upper | f_F, f_D, f_H | cell × r | negligible (f_F, f_D, f_H ≈ 0.15–0.6 % of the radius) | pointless | — | yes | A:N7 |
| N8 | s_F, s_D, s_H | ≥ ‖F̂‖, ‖D̂‖, ‖Ĥ‖ (candidate sups) | upper | f_G, Env4 | cell × r | candidate-sup part of f_G, quoted at A:N8 | yes (A1/R5; composite-sup theorem, stream D) | D (payloads never serialized) + T | yes | A:N8, C §2 |
| N9 | sup_S0[n] | drift-aware closed-form bounds | upper | towers, σ4 (r = 0) | per cell | — | — | — | yes | A:N9 |
| N10 | Aux3 order-3 evidence | S:r:3, h:j:3 candidate sups + midpoint eps | upper | σ3/σ4 via (P3′) | per cell | the live half is S:r:3 (r = 1…4) and h:j:3 (j = 2…4) | yes | R | yes | A:N10 |
| N11 | Ĥ_r(a) | centre values at the atom | point interval | centre C_lo/C_hi | cell × r | — | no (centres) | — | yes | A:N11 |
| N12 | W2 enclosures | "origin ± cellwise node" | two-sided | centre C_lo/C_hi | cell | \|C_lo\| is small vs S̄ (C5 phase 1 :36) | yes (C4 :263) | R | yes | A:N12 |
| N13 | C_T, τ, Ā, D_lo, D1, D2 | operator constants (taboo resolvent, ARL, escape probability and its e-derivatives) | upper / lower, block-uniform | Dv′ → A | per cell (sub-block max/min) | "D_lo and τ are the only operator levers that matter … D2 is irrelevant" (D1 diagnosis :98-103) | yes (E1/R3; LR route, stream C1) | T or computation; host-free for stdlib certifiers | I1 yes; I2 is the r2 substitute | A:N13, B §a |
| N14 | κ1, κ2 | E\|He_n(Y)\| rational upper bounds | upper | Dv′ A1, A2 | shared | negligible slack | — | — | yes | A:N14 |
| N15 | g_hi | R.hi − e0·D.lo | upper | additive | per cell | 59–60 % of the deficit | via N2/N3 | T-light + G | yes | A:N15 |
| N16 | A_G | Lemma G: C, k1C², k2C²+2k1²C³ | upper | min supply | per cell | never selected | — | — | yes | A:N16, B §a.2 |
| N17 | eff, δ1, δ2, A_Dv′ | Dv′ r2: A0=eff, A1=eff(κ1C_T+δ1), A2=eff(2κ1²C_T²+κ2C_T+2κ1C_Tδ1+2δ1²+δ2) | upper | rad_r | per cell | A0·p2 ≈ 81.5–81.9 % of S̄ | yes (N13); floored by Λ (N34) | T | yes | A:N17 |
| N18 | chosen supply S | componentwise min over valid supplies | upper | rad_r | per cell | S_I1 = C2 on all fields | D′ operator-mixed is tighter but not admissible under r2 | G | yes | A:N18 |
| N19 | towers | Leibniz J/h recursions | upper | σ3, σ4 | per cell | pure tower loose at order 3 (TCT:79-80) | yes | T | yes | A:N19 |
| N20 | σ3 | ≥ ‖S_r‴(e0)‖ (midpoint tower) | upper | f_G | cell × r | 42–48 % of f_G at r ≥ 1 | yes | R (evidence) or T | yes | A:N20 |
| N21 | σ4 | ≥ sup ‖S_r⁗‖ (cell tower) | upper | Env4 | cell × r | ≈235 at r = 4 via the tower | yes | R or T | yes | A:N21 |
| N22 | f_F, f_D, f_H | δ + ε (midpoint) | upper | p0, p1, p2 | cell × r | negligible | — | — | yes | A:N22 |
| N23 | f_G | 3k1 s_H + 3k2 s_D + k3 s_F + σ3 + ε_src[3] (Ĝ := 0) | upper (norm-only) | p2 (ρ f_G), p1, p0 | cell × r | **dominant**: A0·ρ·f_G ≈ 60–63 % of S̄ | yes: real Ĝ (R), composite sup (T + D), cancellation (T) | R / T / D | yes | A:N23, C §3 |
| N24 | Env4 | (P3) envelope at s_G = 0 | upper | p2 (ρ² Env4/2) … | cell × r | A0·ρ²·Env4/2 ≈ 18–23 % of S̄ | yes | T / R | yes | A:N24 |
| N25 | p0, p1, p2 | Taylor bounds at \|t−e0\| ≤ ρ | upper | rad_r | cell × r | — | **yes: the profile p_j(s) (TPT)** | T (done tonight) | yes | A:N25 |
| N26 | rad_r | A0 p2 + 2A1 p1 + A2 p0 | upper | 𝓗 | cell × r | — | via A, p, TPT, LR | T | yes | A:N26 |
| N27 | c(5), [C_lo, C_hi] | assembly coefficients and centres | exact / interval | 𝓗 | cell | small | — | — | yes | A:N27 |
| N28 | 𝓗_5 | [C_lo − S̄, C_hi + S̄] | two-sided | M | cell | lower end binds | via S̄ | — | yes | A:N28 |
| N29 | M | min(M_R2, mag(H ∩ 𝓗)) | upper | transport | cell | = \|lo\| on 306–309 | — | — | yes | A:N29 |
| N30 | Γ (direct clause) | g_hi + ρ x_hi M | upper on max g | **adoption quantity** | cell | — | TPT / C5-T replace the transport step | T + **G (floor extension)** | yes | A:N30 |
| N31 | Γ_C5T | g_hi + max((−H_lo)⁺ w_R, (H_hi)⁺ w_L) | upper | scientific clause | cell | 1.21–1.30 % of the penalty | superseded in strength by TPT (TPT-D) | — | **no** | A:N31 |
| N32 | chain clause | μ_k, ℓ_k, γ_k, U_k | upper | not in the adoption quantity | adjacent cells | — | — | — | no | A:N32 |
| N33 | adoption predicates | floor r2 base + (F1′ or F2) | governance | — | cell | 306: F1′(d) fails | — | G | yes | A:N33, B §b.4 |
| N34 | Λ_k floor | Λ_k = sup E_a[τ]; any admissible A0 ≥ Λ_k | constraint | never enters Γ | cell | 309: Λ ≥ 3.586306 > the C5-T critical A0 3.266416 | — | — | no | A:N34, C §5 |

## 2. Edges (primitive → derived)

    N1 → N15, N25, N30        N2,N3 → N15         N4 → N29         N5,N6 → N16
    N13,N14 → N17             N16,N17 → N18       N6,N9,N10 → N19   N19,N10 → N20, N21
    N7 → N22                  N6,N8,N20,N7 → N23  N6,N8,N21 → N24
    N22,N23,N24,N1 → N25      N18,N25 → N26       N11,N12 → N27    N26,N27 → N28
    N4,N28 → N29              N15,N29,N1 → N30    N15,N28,N1 → N31  N30 → N33   N13 → N34 (floor on N18.A0)

## 3. Which inequality carries the largest avoidable looseness (structural, target-independent)

Graph A §3 lists 18 inequality steps. They are grouped here by **structural reason**, not by any closure estimate.
The weights quoted are committed historical shares of the radius sum S̄. They are used only to say which inequality
the structure makes large, never to forecast a cell.

| rank | inequality (graph A §3 item) | structural looseness | new-route owner |
|---|---|---|---|
| 1 | whole-cell radius charged at every t in the transport (items 4, 5, 12) | the Taylor remainder terms linear and quadratic in \|t−e0\| (≈ 60 % + ≈ 20 % of S̄ historically) are charged at their edge value over the whole cell. The exact profile charges ≈ 1/2 and ≈ 1/3 (TPT-G) | **TPT** (E_assembly): theorem, implementation, V1/V3 done |
| 2 | order-3 surrogate `‖S‴ + 3K1Ĥ + 3K2D̂ + K3F̂‖ ≤ σ3 + 3k1 s_H + …` (item 14) plus atom functional × sup norm (item 8) | triangle inequality plus submultiplicativity; ‖·‖ over the whole state space where only an atom functional is needed; no cancellation | B_307 (order-3), D_309 (composite sup, RSO) |
| 3 | A1, A2 via submultiplicativity / quotient rule (item 9) | discards the sign cancellation of K₁, K₂ (synthetic: true functional norm 3–10× / 10–20× below even the positive majorant); asymptotically Dv′ A2 ~ Λ·C_T² vs A2^LR ~ E[τ²] | **LR** (C_308/LR) |
| 4 | order-0 channel `A0‖φ″‖` (item 8) | sharp only at f ≡ 1 (C4 :256-259); the floor A0 ≥ Λ binds the whole family | RSO (D_309) |
| 5 | generic midpoint eps in g_hi (item 3) | C_upper·f instead of the atom functional (AD Corollary T), not applied on the tail | assembly (E): inventory only |
| 6 | Env4 / σ4 towers (items 13, 15) | Leibniz triangle recursion; order-4 source measured nowhere | B_307 / D_309 |
| 7 | independent R/D in g_hi, independent r-sum, W hull (items 1, 7) | no joint information exists (C6: never existed) | — (data never existed) |
| 8 | κ rationalization, outward rounding (items 2, 10) | negligible | — |

## 4. What is target-free, what is data-blocked, what is governance-blocked

* **Target-free and computable locally** (stdlib only, from committed inputs or operator-only):
  * TPT (assembly);
  * AD Corollary T for g_hi (existing theorem);
  * LR atom constants (operator-only; exact rational certifiers run on this Mac, as I2 did);
  * tight Ā/τ supersolutions (C_308/A0X).
* **Data-blocked:**
  * composite sup norms, RSO and cancellation in f_G need the K1 candidate payloads. These were never serialized, and
    replay needs a numpy/flint host (C6).
  * A real order-3 Ĝ needs new real addresses (N1/N3/N5/N7 open; guard DENY).
* **Governance:**
  * every route that changes the consumer or non-constant inputs, or supplies non-Lemma-G/Dv′ constants, is
    **closure-only under floor r2**;
  * adoption needs a user-decided floor extension frozen before any evaluation (C2 Condition 1; route audit U3).
