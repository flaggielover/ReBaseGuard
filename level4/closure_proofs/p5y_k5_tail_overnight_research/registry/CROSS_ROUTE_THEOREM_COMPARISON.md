# Cross-route theorem comparison: a partial order of the candidate theorems (brief §22)

**Scope.** Theorems are compared by **logical strength, assumptions, scope and cost**. Nothing is ranked by any
guessed chance of closing a target cell. No target-cell number appears in this document (rule S8, amendment 2).

## 1. Which inequality each theorem acts on

The adoption quantity (graph N30) is

    Γ = g_hi + transport( enclosure of R''_m ),   enclosure radius = Σ_r (1/m)(A0 p2 + 2A1 p1 + A2 p0).

| theorem | inequality replaced | inputs it needs |
|---|---|---|
| TPT, TPT-B | the whole-cell transport step (N30/N31) | the committed TC/TC-T inputs; nothing new |
| RLR, LR | the atom constants A1, A2 (N17) | operator certificates only |
| C2b strategy | A0, τ, C_T certificates (N13) | operator certificates only |
| Theorem M | none. It locates sup Λ over a cell (N34). | none |
| SC (composite sup) | the order-3 surrogate f_G (N23) | candidate payloads |
| RSO | the order-0 channel A0‖φ‖ (graph §3 item 8) | pointwise residual majorants |
| real refinement | the cover ρ (N1) | new K1 records |
| real order-3 (R1) | f_G, via a real Ĝ (N23) | new real addresses |
| ADLR | the s-dependent radius | certified Λ₃, Λ₄ |
| Theorem CV | the trust relation between implementations | none (a verification structure) |

**Theorems that act on different inequalities compose.** TPT consumes any radius profile. It therefore stacks on top
of LR/RLR constants, SC's f_G and RSO's order-0 term. None of these excludes another.

## 2. Dominance relations that are proved

| relation | status | source |
|---|---|---|
| TPT ≤ C5-T < frozen clause, for the same enclosure inputs | proved (TPT-D); validated on synthetic and real non-target data | THEOREM_TPT §1, V1–V3 |
| TPT-B ≤ TPT when every block constant ≤ the cell constant | proved | THEOREM_TPT §2b |
| TPT is sharp among bounds built from (g_hi, L, U) | proved (TPT-O, as a supremum) | §1 |
| true A1 ≤ A1^LR ≤ positive majorant ≤ Lemma G, and likewise for A2 | proved (LR-4, with a caveat on the score level) | THEOREM_LR |
| RLR ≤ Dv′ on the same inputs | **proved for exact ρ only** (LR-3). With certified ρ (the Cauchy–Schwarz L1 bound) RLR can exceed Dv′ (REVIEW_RLR_R2: 6/9 exact fixtures). The guaranteed object is **min(RLR, Dv′, Lemma G)**. | THEOREM_LR; REVIEW_RLR_R2 §1.3 |
| plain LR vs Dv′ | **incomparable** | THEOREM_LR E1/E2; stream B scaling |
| SC composite sup ≤ the order-3 surrogate, with strict slack (the Leibniz gap) for continuous candidates | proved | SUPNORM_THEOREM |
| RSO ≤ A0·‖φ‖; equality for constant ψ, where it collapses to the refuted uniform-A0 family | proved | RESIDUAL_SPECIFIC_309 |
| a refinement without new records ≡ TPT **within the fixed-(g_hi, L, U) family** | an implementation identity, not validation evidence (review D B3); re-certifying constants on sub-segments (B2c) is a separate lever, THEORY_ONLY (review D B2) | COVER_REFINEMENT_309, D_309_ROUTE_SUMMARY §7 |
| real refinement vs TPT | **incomparable**: refinement removes order-1 slack that TPT cannot touch; TPT is free | COVER_REFINEMENT_309 |
| ADLR vs TC-T | **incomparable** | REAL_ORDER3_THEORY |
| a block-uniform Ā ≥ Λ*(E) ≥ sup_E Λ, for **any** single-supersolution certifier (I1, I2 and C2b alike) | proved | C2b A0_TIGHTNESS §1 |

**Asymptotic regimes.** The streams' statements are reconciled here.
* Dv′'s A1 is of order Λ·C_T, and its A2 of order Λ·C_T².
* How C_T, the taboo excursion scale, grows relative to Λ is a property of the chain:
  * in C1a's examples C_T is bounded; there Dv′ is essentially exact and plain LR is worse (Λ^{3/2} against Λ);
  * in B's zero- and low-drift fixtures C_T grows faster than Λ (slope about 1.35); there Dv′ is asymptotically
    loose and the true orders are Λ^{1+j/2}.
* With exact ρ, RLR dominates Dv′ in both regimes (LR-3). With certified ρ only the min with Dv′ is guaranteed (REVIEW_RLR_R2). Plain LR does not dominate.

## 3. Assumptions and scope

| theorem | assumptions | scope |
|---|---|---|
| TPT | x_lo > 0; profile coefficients ≥ 0 (TPT-M), else P₊ (not implemented); cap = consumed H_final | every cell with x_lo > 0, any detector, any m |
| RLR | an atom with regeneration; certified geometric tail of τ; block-uniformity via a drift-free certificate | any atom-regenerative killed kernel with a differentiable density |
| Theorem M | start at the atom or a diagonal state; Gaussian increments; V-mask form | the CUSUM model as frozen |
| C2b strategy | the reachable-set triangulation; second-derivative bounds (§5.3, single-author) | any block; A0, τ, C_T only (no D-constants) |
| SC | continuous candidates; composite-sup certification | needs candidate payloads |
| RSO | a declared majorant class; supersolution with source ψ | needs pointwise residuals |
| Theorem CV | two independent verifiers; certified brackets | general |

## 4. Cost (local stdlib, measured where available)

| theorem | cost |
|---|---|
| TPT | milliseconds per cell |
| C2b | 2–300 CPU-s per drift or block (exact part); float proposal ≤ 190 s |
| RLR on the real kernel | see stream C1b (`streams/C_308/LR/cusum/`) |
| SC / RSO | a host replay of the candidates, about 1350 CPU-s per cell historically (E07a), plus certification |
| real refinement | new K1 records: multi-hour to a CPU-day, unmeasured |

## 5. Resulting partial order (strength, holding all else fixed)

    frozen clause  <  C5-T  <=  TPT  <=  TPT-B                    (transport)
    Lemma G  >=  positive majorant  >=  LR  >=  true;   Dv' >= min(RLR, Dv', G)  (atom constants; RLR <= Dv' for exact rho only; LR vs Dv' incomparable)
    surrogate f_G  >=  SC composite                                 (order-3 term)
    A0*||phi||  >=  RSO                                             (order-0 term)
    TPT  ~  refinement-without-records (fixed-input family only; B2c open);   TPT  <>  real refinement   (incomparable)

Here `≥` means the left side is the looser bound. The chains act on different inequalities, so the strongest combined
theorem available **without new real objects** is **TPT ∘ (min(RLR, Dv′, Lemma G) constants) ∘ (C2b-certified A0)**. That combination
has three blockers:
* TPT's tail use is blocked in this campaign (incident 01);
* each component is closure-only (U3);
* RLR's real-kernel certification must be completed and reviewed.

Adding SC and RSO needs the candidate payloads (U1, U2). Real refinement and real order-3 need new real records under
separate governance.
