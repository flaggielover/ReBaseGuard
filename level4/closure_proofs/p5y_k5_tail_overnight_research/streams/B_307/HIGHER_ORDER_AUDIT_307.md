# HIGHER_ORDER_AUDIT_307 — every inequality behind the higher-order part of the TC-T radius and the K5-B clause

Stream B_307, overnight campaign (research only). Written 2026-09-27/28 UTC.

**Quarantine statement.** Nothing in this document was computed for CUSUM m = 5 cells 305–309 or at any drift in
[6/5, 13/5] (or its mirror). Every tail number is **quoted** from a committed file with file:line. Every new number
comes from a script in `code/` run on one of three sets:
* synthetic fixtures;
* the declared Gaussian drifts {0, 1/4, 1/2, 1, 3};
* the 34 committed lower-front TC cells (CUSUM cells 11–44, e ≈ 0.006–0.025).

No I1 constant is combined with an I2 constant. No committed per-cell "x-eff" factor is used to rank anything.
The validation sets were declared first, in `VALIDATION_DECLARATION_B307.json`.

Paths are relative to `level4/closure_proofs/`, with two abbreviations:
* `NS/` = `p5y_k5_tail_overnight_research/`;
* `code/` = `NS/streams/B_307/code/`.

## 0. History: committed facts this audit starts from (quoted, not recomputed; no route factor attached)

| fact | source |
|---|---|
| At 307 the C3/C4 knockout A1 = A2 = 0 closes with the certified A0 (Γ −0.021906 at A1 = A2 = 0; certified A0 5.5980). So (A1, A2), not A0, is 307's blocker **under that clause** | `p5y_k5_tail_c3_closure/evidence/adjudication/C3_ADJUDICATION.md:346-348`; `p5y_k5_tail_c4_exhaustion/phase_1/C4_TARGET_RECONSTRUCTION.md:72-76, 103-105`; `p5y_k5_tail_c3_closure/OPEN_NOTES_DISPOSITION_C3.md:27-28` |
| C5 decomposition of the radius sum S = (1/5)Σ_r rad_r, cells 307 / 308 / 309: A0·p2 81.56 / 81.66 / 81.95 %; 2A1·p1 16.77 / 16.73 / 16.51 %; A2·p0 1.67 / 1.61 / 1.54 % | `p5y_k5_tail_c5_exhaustion/phase_1/C5_BLOCKER_DECOMPOSITION.md:43-47` |
| … of which A0·ρ·f_G 61.59 / 60.04 / 58.80 %; A0·ρ²·Env4/2 19.86 / 21.52 / 23.06 %; A0·f_H 0.11 / 0.10 / 0.09 % | same file, :48-50 |
| C2 elasticities of the magnitude response: A0 0.63, A1 0.165, A2 0.022 | `p5y_k5_tail_c2_closure/phase_d/D_STAGE_DECISION.md:47-49` |
| At r ≥ 1, σ3 is 42–48 % of f_G at the tail | `p5y_k5_tail_c5_exhaustion/phase_1/C5_BLOCKER_DECOMPOSITION.md:59-62` |
| Measured midpoint residuals on the tail: δ_mid(F) ≈ 1e-7…4e-5, δ_mid(dF) ≈ 4e-7…1.5e-4, δ_mid(H) ≈ 5e-6…4e-4 | `p5y_k5_m5_tail_closure/phase_a/TAIL_BLOCKER_AUDIT.md:41` |
| Lemma Dv′ r2: A0 = Ā_eff, A1 = Ā_eff(κ₁C_T + δ₁), A2 = Ā_eff(2κ₁²C_T² + κ₂C_T + 2κ₁C_Tδ₁ + 2δ₁² + δ₂) | `p5y_k5_perron_deflated_resolvent/theorem/THEOREM_AD.md:81-89` |
| Lemma G: A0 = C, A1 = k₁C², A2 = k₂C² + 2k₁²C³ | `p5y_k5_m5_tail_closure/theorem/THEOREM_TCT.md:22-33` |
| Accepted route audit: real order-3 (R4) has scientific risk HIGH for 307. Review N3 corrects r1's rating of MEDIUM | `p5y_k5_tail_route_audit/review/ROUTE_AUDIT_R1_REVIEW.md:105-124`; `p5y_k5_tail_route_audit/ROUTE_AUDIT_R1.md:382-393` |

These figures are **history only**. No route factor, fixture ratio or ranking in this document is combined with
them (see the incident-01 note in §5).

## 1. The chain under audit

    (P1) analyticity ─┐
    (P2) f_F,f_D,f_H  ├─ Taylor with integral remainder (TC §4.1) ─> ‖φ^(j)(e)‖ ≤ p_j          [HO-7]
    (P2′) f_G surrogate [HO-8] ┤
    (P3) Env4 [HO-9], (P3′) σ3/σ4 towers [HO-10] ┘
    (I−K_e)E = φ  [HO-1]  ─>  E'' = Rφ'' + 2(∂R)φ' + (∂²R)φ   [HO-2]
    atom evaluation with A0, A1, A2 (Lemma G / Dv′)  [HO-3 … HO-6]  ─>  |E''(e)(a)| ≤ rad_r = A0p2 + 2A1p1 + A2p0
    centre motion  half_r = ρ|Ĝ(a)| + rad_r   [HO-11, HO-12]
    assembly  𝓗_m = Σ_r (1/m)[Ĥ_r(a) ± half_r] + Σ c(m)·𝒲   [HO-13]
    H_k ∩ 𝓗_m,  M_k = mag   [HO-14]  ─>  K5-B direct clause / C5-T   [HO-15];  chain (ℓ_k, γ_k, L_k)  [HO-16]

**Exact bookkeeping.** This is an identity, implemented in `code/b307_lib.py` `radius_terms`. With the three A's and
the five premise quantities,

    rad = A0·f_H + A0ρ·f_G + A0ρ²·Env4/2
        + 2A1·f_D + 2A1ρ·f_H + A1ρ²·f_G + A1ρ³·Env4/3
        + A2·f_F + A2ρ·f_D + A2ρ²·f_H/2 + A2ρ³·f_G/6 + A2ρ⁴·Env4/24.

* The "higher-order contribution" is every monomial that contains f_G or Env4: seven of the twelve.
* 307's (A1, A2) blocker is itself mostly higher-order. The measured residuals f_F, f_D, f_H are at the 10⁻⁴ scale
  (row above). So inside 2A1·p1 = 2A1f_D + 2A1ρf_H + A1ρ²f_G + A1ρ³Env4/3, the f_G and Env4 monomials carry the
  weight.
* Consequently, **every** term that blocks 307 under the committed clause is a product of an atom constant with one
  of the two higher-order quantities f_G and Env4. Neither of those is a measurement: f_G is the zero-candidate
  surrogate and Env4 the (P3) envelope.

## 2. Inequality-by-inequality reconstruction

Column key:
* **exact?** — whether the step is an identity or an inequality;
* **relaxation** — the worst case the inequality assumes;
* **discarded** — independence, symmetry or sign-cancellation information thrown away;
* **collapse** — whether operator information is reduced to a scalar;
* **order** — the looseness, expressed in Λ = E_a[τ], C (≥ ‖R_e‖), C_T, ρ and κ where possible.

"Fixture evidence" points to §4, and every number there is produced by `code/b307_run_fixtures.py`.

### HO-1  (I − K_e)E(e) = φ(e),  E := F − F̃   (THEOREM_TC.md:76-77)

* **exact?** Yes. It is the definition of φ together with (I − K_e)F = S.
* **relaxation / discarded / collapse:** none.
* **evidence:**
  * exact on every fixture grid point (identity counter `idfail`, `code/b307_cellpipe.py` `run_cell`);
  * the P1 negative control (factor 2 dropped) is detected.

### HO-2  E'' = Rφ'' + 2(∂R)φ' + (∂²R)φ,  ∂R = RK₁R,  ∂²R = 2RK₁RK₁R + RK₂R   (THEOREM_TC.md:77-79; THEOREM_AD.md:65)

* **exact?** Yes. It follows from differentiating E = R_eφ(e) twice.
* **evaluation at the atom.** E''(e)(a) = [R_eφ''(e)](a) + 2[∂R_eφ'(e)](a) + [∂²R_eφ(e)](a) is still exact.
* **evidence:**
  * exact at all 17 grid points of all 64 fixture cells × 5 objects × 4 routes;
  * class-(a) plant through the same identity check: ∂²R with the RK₂R term removed fires on 5439/5439 eligible
    grid points (those where [RK₂Rφ](a) ≠ 0);
  * the five-way split P_H + P_G + P_4 + P_1 + P_0 = E''(e)(a) (§4 T3) holds **by construction** (P_4 is defined as
    a remainder). It is bookkeeping, class (c), and **not evidence** (review C-9).

### HO-3  |E''(e)(a)| ≤ A0‖φ''(e)‖ + 2A1‖φ'(e)‖ + A2‖φ(e)‖   (THEOREM_TC.md:80)

* **exact?** No. It is two relaxations stacked:
  * (i) the triangle inequality over the three atom terms;
  * (ii) |δ_a T f| ≤ ‖δ_a T‖₁·‖f‖∞ on each term, with A_j ≥ ‖δ_a∂^jR_e‖ uniformly on the cell.
* **discarded:**
  * any cancellation among [Rφ''](a), 2[∂Rφ'](a) and [∂²Rφ](a);
  * the **shape** of the residual vectors. Step (ii) is sharp only when the residual is aligned with the sign
    pattern of the row δ_a∂^jR. For R ≥ 0 that pattern is f ≡ const: Lemma SM(d), THEOREM_AD.md:51-56;
  * the e-dependence of the three functionals (a cell supremum is used).
* **collapse:** yes. Three atom functionals, each a vector in ℓ¹(X), are reduced to three scalars.
* **order:** residual-specific. The factor A0‖f‖/|[Rf](a)| has no a-priori bound, since ν_e(f) can vanish while
  ‖f‖ does not. This is the "residual-specific order-0" escape of C4 §7 item 1
  (`p5y_k5_tail_c4_exhaustion/evidence/adjudication/C4_ADJUDICATION.md:254-269`).
* **evidence:** §4 T3, per-term bound/truth.

### HO-4  A0 ≥ sup_{e∈C} ‖δ_aR_e‖ = sup_{e∈C} Λ(e)

* **exact?** No.
* **Lemma G** uses A0 = C_upper ≥ sup_e‖R_e‖ = sup_{e,x}E_x[τ] ≥ Λ (THEOREM_TCT.md:26). It discards:
  * the start state: sup_x E_x[τ] is used instead of E_a[τ];
  * the drift: C_upper is the one-sided carried left-end bound (`p5y_k1_cover_ledger_successor/CHECKPOINT.md:86-90`).
* **Lemma Dv′** uses A0 = min(Ā, τ/D_lo). This is sharp as a norm-only constant (SM(d)); its slack is certificate
  slack only.
* **collapse:** none beyond HO-3.
* **order:** O(1). The ratio C/Λ is bounded by the ratio of worst-start ARL to atom-start ARL, and does not grow
  with Λ.
* **307:** A0 is **not** 307's blocker under the committed clause (§0).
* **evidence:** §4 T2, A0.G / true.

### HO-5  A1 ≥ sup_{e∈C} ‖δ_a R K₁ R‖

The ladder of successively looser bounds is implemented in `code/b307_lib.py` `Point.ladders`:

    ‖δ_aRK₁R‖₁                     (true functional norm)
      ≤ (R|K₁|R1)(a)                (PM: drops the sign cancellation of K₁)
      ≤ Λ·k₁·C                      (collapse: ‖|K₁|R1‖ ≤ k₁‖R1‖ = k₁C)
      ≤ k₁·C²                       (Lemma G: Λ → C)

Lemma Dv′ takes a separate route, Λ_eff(κ₁C_T + δ₁). It uses the taboo form ν' = δ_aĜK̂'Ĝ with the bound
|ν'| ≤ τκ₁C_T, plus the quotient rule with the triangle inequality between ν'/D and νD'/D².

* **exact?** No.
* **discarded:**
  * the **sign cancellation of K₁**. The score has mean zero, so K₁ annihilates constants up to the alarm and
    boundary terms. See REAL_ORDER3_THEORY §2 for the Hermite form K₁g = E[g(T(x,Z))·S];
  * in Dv′, the cancellation between the two quotient-rule terms;
  * the post-atom state: sup over x of (R1)(x) = C, or of (Ĝ1)(x) = C_T.
* **collapse:** yes, at two levels: K₁ → k₁ or κ₁, and R1 → C or C_T.
* **order:**
  * Lemma G is O(k₁C²);
  * Dv′ is O(Λ(κ₁C_T + δ₁));
  * the true functional norm is measured on FX_B (§4 T2b, log-log slopes in Λ at zero drift);
  * the heuristic LR scale is O(Λ^{3/2}). Its certification belongs to the C_308 LR stream
    (`NS/streams/C_308/IDEA_LR_SCORE_CONSTANTS.md`).

### HO-6  A2 ≥ sup_{e∈C} ‖δ_a(2RK₁RK₁R + RK₂R)‖

The same ladder applies:

    true  ≤  PM = 2(R|K₁|R|K₁|R1)(a) + (R|K₂|R1)(a)  ≤  Λ(2k₁²C² + k₂C)  ≤  k₂C² + 2k₁²C³   (Lemma G)

Lemma Dv′ uses Λ_eff(2κ₁²C_T² + κ₂C_T + 2κ₁C_Tδ₁ + 2δ₁² + δ₂). The discarded information is as in HO-5, plus the
cancellation between the two operator words (RK₁RK₁R against RK₂R).

* **order:**
  * Lemma G is O(C³);
  * Dv′ is O(Λ·C_T²);
  * the heuristic LR scale is O(Λ²), reading E_a Σ_{n<τ}|M_n² − n| as ~E[τ²].
* So both certified supplies are **asymptotically loose by a factor of order C_T²/Λ (Dv′) or C³/Λ² (G)** relative to
  the heuristic truth. §4 T2b checks this with exact fixture slopes.

### HO-7  Taylor remainders p0, p1, p2   (THEOREM_TC.md:55-57, 74-75)

The starting identity is exact:

    φ^(j)(e) = Σ_{i<4−j} t^i/i!·φ^(j+i)(e0) + ∫_{e0}^{e} (e−u)^{3−j}/(3−j)!·φ⁗(u) du.

The bound is ‖φ^(j)(e)‖ ≤ Σ_i |t|^i/i!·f_{j+i} + |t|^{4−j}/(4−j)!·Env4, followed by the substitution |t| → ρ.

* **exact?** The expansion is exact; the bound is not.
* **discarded:**
  * the relative direction of the vectors φ^(j+i)(e0) (triangle inequality across Taylor orders);
  * the **sign of t**: the odd monomials change sign across the cell, but a whole-cell interval charges |t|;
  * the **profile**: the value at |t| = ρ is charged at every t. This belongs to stream E / TPT
    (`NS/streams/E_assembly/THEOREM_TPT.md` §2).
* **collapse:** norms throughout.
* **order:** the powers ρ^i are weighted by 1/i!. Under the frozen cover rule ρ ≤ 1/(4 a_up C_use), a_up ≥ κ₁ ≥ k₁
  (`p5y_k1_cover_ledger_successor/CHECKPOINT.md:91-97`), the following products are bounded by cell-independent
  constants:
  * k₁ρC ≤ 1/4;
  * the ratio (A1ρ)/A0 = k₁Cρ under Lemma G, and likewise under Dv′ ≈ κ₁C_Tρ.

  **Hence the A1 and A2 monomials are not asymptotically suppressed relative to the A0 monomials at any cell.**
  They form a geometric-type series in k₁ρC. The lower-front evidence measures 2k₁ρC_upper = 0.49992–0.499999
  on all 170 objects (§4 T5).

### HO-8  f_G (P2′): ‖φ'''(e0)‖ ≤ f_G := σ3 + 3k₁s_H + 3k₂s_D + k₃s_F (+ ε_src[3])   (THEOREM_TCT.md:46-61)

The identity φ'''(e0) = S''' + 3K₁Ĥ + 3K₂D̂ + K₃F̂ (at Ĝ = 0) is exact, and was checked by exact polynomial
differentiation (P1).

* **exact?** No. Four relaxations are stacked:
  * (i) the triangle inequality over four vectors that **nearly cancel**. Their sum equals
    (I − K)F''' − [3K₁(F''−Ĥ) + 3K₂(F'−D̂) + K₃(F−F̂)], i.e. (I − K)F''' up to candidate errors;
  * (ii) ‖K_iX̂‖ ≤ k_i‖X̂‖. This discards the fact that on a smooth X̂ the operator K_i acts like an i-th
    derivative: by integration by parts against the score, K₁X̂ = −K(∂_z X̂∘T) plus alarm-boundary and clip-kink
    terms;
  * (iii) ‖X̂‖ ≤ s_X, the certified Bernstein supremum;
  * (iv) σ3 ≥ ‖S_r'''(e0)‖ from the (P3′) midpoint tower or Aux3.
* **pure slack by construction.** ε_src[3] is added on top, although the identity already carries the **true**
  source (THEOREM_TCT.md:59-61). This part is tiny.
* **collapse:** yes. Three operators and three candidate functions become six scalars.
* **order:**
  * f_G/‖φ'''(e0)‖ is the split-and-collapse factor (§4 T3 `fG_split_over_exact_zero_residual`);
  * f_G itself is O(1) in Λ at fixed source scale, because it consists of sup norms of F-derivatives and sources,
    not of an atom functional.

### HO-9  Env4 (P3): sup_{e∈C}‖φ⁗(e)‖ ≤ σ4 + 4k₁s_G + 6k₂(s_H + ρs_G) + 4k₃(s_D + ρs_H + ρ²s_G/2) + k₄(…)   (THEOREM_TC.md:37-47)

The identity φ⁗ = S⁗ + Σ_{i≥1} C(4,i)K_iF̃^(4−i) (F̃⁗ = 0) is exact.

* **exact?** No. The relaxations are those of HO-8 at order 4, plus two more:
  * a cell supremum in e, of S⁗ via σ4 and of K_i via k_i;
  * the triangle inequality over |t| ≤ ρ inside F̃^(j).
* **true object.** For Ĝ ≈ F''' it is ≈ (I − K)F⁗. For Ĝ = 0 it is ≈ (I − K)F⁗ − 4K₁F''' + O(ρ).
* **collapse:** yes.
* **evidence:** §4 T3 `env4_over_max_phi4`.

### HO-10  (P3′) towers for σ3 (midpoint) and σ4 (cell)   (THEOREM_TCT.md:74-117)

The recursion is ‖h_j^(n)‖ ≤ Σ_i C(n,i)k_i‖h_{j−1}^(n−i)‖ and σ_n(r) = Σ_i C(n,i)j_i‖h_r^(n−i)‖. The cell tower adds
the mean-value correction ρ·tower[j,4].

* **exact?** No. The recursion applies the triangle inequality and the collapse at every step j.
* **discarded:** the Gaussian-location structure of path probabilities. The n-th e-derivative of
  P_x(τ = j) is E_x[1{τ=j}·j^{n/2}He_n(M_j/√j)] (REAL_ORDER3_THEORY §3, identity checked in
  `NS/validation/B307_HERMITE_IDENTITY.json`).
* **order:** the tower grows like (k₁j)^n in j. The Hermite bound κ_n j^{n/2} grows like j^{n/2}. So the tower is
  **asymptotically loose in j by j^{n/2}**. For m = 5 we have j ≤ 5, so the gain is bounded.
* **already-adopted repair.** The adopted Aux3 midpoint values already replace the tower at order 3 where they bind
  (THEOREM_TCT.md:114-117). At order 4, the cell tower is the only supply.

### HO-11  the ρ-linear monomial A0·ρ·f_G bounds P_G = t·[R_eφ'''(e0)](a)

* **exact?** No. This is the composition HO-3(ii) ∘ HO-8.
* **true object.** At Ĝ = 0,

      [R_{e0}φ'''_0(e0)](a) = F'''(e0)(a) − [R(3K₁E_H + 3K₂E_D + K₃E_F)](a).

  So the monomial bounds **ρ·|F_r'''(e0)(a)| up to candidate errors**, which is a pointwise and signed scalar.
* **the bound.** It uses ρ·A0·(σ3 + 3k₁s_H + 3k₂s_D + k₃s_F).
* **two independent slack factors:**
  * the norm-only factor A0‖φ'''‖/|[Rφ'''](a)|;
  * the split factor f_G/‖φ'''‖.
* **structural position.** It is the first-order Taylor monomial multiplied by the order-0 atom constant. The
  committed history of its size is in §0 only.

### HO-12  the centre-motion floor  half_r = ρ|Ĝ(a)| + rad_r

* **exact?** It is valid, and it is intrinsic to a **whole-cell interval**.
* **floor.** Proposition RO3-F (REAL_ORDER3_THEORY §4) proves that every choice of Ĝ pays at least
  ρ·|[R_{e0}φ'''_0(e0)](a)| ≈ ρ|F'''(e0)(a)| in the A0-level ρ-group. The whole-cell interval must contain the true
  motion of F''_r(e)(a) across the cell.
* **discarded:** the **sign** of F'''(e0)(a). Only a sign- or profile-aware consumer can use it: TPT (stream E), or
  the K5-B chain with L_k (HO-16).

### HO-13  assembly 𝓗_m = Σ_r (1/m)[Ĥ_r(a) ± half_r] + Σ c(m)·𝒲   (THEOREM_TC.md:63-69)

* **exact?** The Minkowski sum of valid intervals is valid. The per-object radii, however, are separate worst cases.
* **discarded:** correlation among the five errors E_r. A joint residual φ_Σ = (1/m)Σ_rφ_r can cancel.
* **evidence:** §4 T4 (`perr_over_joint`).
* **not audited:** the W enclosures (frozen finite-power whole-cell enclosures).

### HO-14  H_k ∩ 𝓗_m, M_k = mag   (THEOREM_TCT.md:129-130)

* **exact?** Yes: an intersection of valid enclosures is valid.
* **discarded:** the magnitude discards the sign. On all four open cells the **lower** endpoint binds, so
  M = |C_lo| + S exactly (`p5y_k5_tail_c5_exhaustion/phase_1/C5_BLOCKER_DECOMPOSITION.md:33-37`). The clause is
  therefore affine in S.

### HO-15  K5-B direct clause Γ = g_hi + ρ·x_hi·M, and C5-T   (K5_GLOBAL_BRIDGE.md:27, 44)

* **exact?** No. The mean value theorem is applied with sup|tR''| ≤ x_hi·M.
* **discarded:**
  * the sign of R'';
  * the weight t;
  * the profile.
* **known refinements.** C5-T restores the exact weight
  (`p5y_k5_tail_c5_exhaustion/evidence/adjudication/C5_ADJUDICATION.md:13-44`). TPT restores the profile and is
  optimal within the three-input family (`NS/streams/E_assembly/THEOREM_TPT.md` §1).
* **scope here.** This step is not higher-order. It is recorded because S enters Γ through ρ·x_hi.

### HO-16  K5-B chain (ℓ_k, γ_k with L_k ≤ inf R''')   (K5_GLOBAL_BRIDGE.md:11, 23-27)

* **status.** Not used at the tail: it needs a certified, whole-cell, **signed** lower bound on R'''_m and an
  unbroken chain from cell 0. The readiness audit calls the tail "a chain problem, not a local one", and TC does not
  feed the chain (`p5y_k5_order3_readiness_audit/README.md:79-81, 109-113`).
* **what TC-T discards.** The sign information of HO-12 is exactly what the chain would need.

## 3. Looseness as orders in Λ, C, C_T, ρ, κ

| inequality | certified form | true object | order of the certified form | order of the truth | avoidable order |
|---|---|---|---|---|---|
| HO-4 A0 | C (G) / min(Ā, τ/D_lo) (Dv′) | ‖δ_aR‖ = Λ | C ≥ Λ | Λ | O(1): no asymptotic slack |
| HO-5 A1 | k₁C² (G), Λ(κ₁C_T + δ₁) (Dv′) | ‖δ_a∂R‖ | Λ² (G, C ~ Λ), Λ·C_T (Dv′) | **Λ^{3/2}** at zero drift (FX_B, measured) | **Λ^{1/2}** (drift 0); Λ^{0.63–0.77} at drift 1/4 and 1/2 |
| HO-6 A2 | k₂C² + 2k₁²C³ (G), Λ(2κ₁²C_T² + …) (Dv′) | ‖δ_a∂²R‖ | Λ³ (G), Λ·C_T² (Dv′) | **Λ²** at zero drift (FX_B) | **Λ¹** (drift 0); Λ^{1.1–1.4} at drift 1/4 and 1/2 |
| (A3, used by ADLR) | 6k₁³C⁴ + 6k₁k₂C³ + k₃C² | ‖δ_a∂³R‖ | Λ⁴ | **Λ^{5/2}** (FX_B) | Λ^{3/2} |
| HO-8 f_G | σ3 + 3k₁s_H + 3k₂s_D + k₃s_F | ‖φ'''(e0)‖ ≈ ‖(I−K)F'''‖ | O(1)·(sup norms) | same scale, cancelled | constant factor (fixtures: median 2.1–2.2 on FX_A, 8.8 on FX_B, §4 T3) |
| HO-11 A0·ρ·f_G | ρ·C·f_G | ρ·\|F'''(e0)(a)\| | ρ·Λ·(sup norms) | ρ·(pointwise value) | **unbounded ratio** (FX_B: the true value vanishes identically on 56/80 objects while the bound does not); lower front: 37–110× (§4 T5) |
| HO-9 Env4 | σ4 + Σ C(4,i)k_i s_{4−i} | sup‖φ⁗‖ | O(1) | same scale | constant (fixtures: 1.1–10, median 1.9–7) |
| HO-10 tower | (k₁j)^n growth | ‖h_j^(n)‖ | j^n | j^{n/2} (Hermite) | **j^{n/2}**; fixtures: h_4''' 24–38×, S_4''' 47–77× |
| HO-7 p_j and time | ρ^i/i! weights at \|t\| = ρ | \|t\|^i | — | — | profile factor 1/2, 1/3 (TPT, stream E) |
| HO-13 assembly | Σ_r rad_r / m | joint | — | — | constant (fixtures: 1.2–3.4) |

**How to read the Λ-exponents.** The measured exponents come from `code/b307_scaling.py`, which fits log-log slopes
over N = 4…24 on the FX_B score walk (`NS/validation/B307_SCALING.json`).
* **At zero drift**, the true atom functionals scale as Λ^{1+j/2}:
  * measured slopes 1.499 (j = 1), 2.005 (j = 2), 2.494 (j = 3);
  * this is exactly the likelihood-ratio heuristic (M_n ~ √n summed over τ ~ Λ steps).
* **Every certified rung** — and also the positive majorant, which already drops the sign cancellation — scales as
  Λ^{1+j}:
  * PM slopes 2.008, 3.006, 4.004;
  * Lemma G slopes 2.0, 2.99, 3.98;
  * Dv′ slopes 1.91 and 2.83.
* **Structural conclusion: the entire asymptotic slack of A1, A2 (and A3) is sign cancellation.** The collapse steps
  (K₁ → k₁, R1 → C, Λ → C) change only constants: the PM → collapse → G rungs share the exponent. This is the
  cancellation of the zero-mean score, carried by the path martingale M_n.
* **At drift 1/4 and 1/2** (the drift-dominated regime):
  * the true exponents fall to 1.37 / 1.23 (A1) and 1.85 / 1.57 (A2);
  * C_T grows faster than Λ (slope 1.35), so Dv′ is asymptotically **worse** than Lemma G there (A2 slope 3.37–3.42
    against 2.98).

**Caveat.** FX_B is a one-sided discrete walk. It shares CUSUM's score structure (Σ_z p_z^(i) = 0), its reflection
atom and its alarm killing, but it is not the CUSUM kernel. The exponents are evidence of **structure**, not
estimates for any CUSUM cell.

**Cover-rule consequence (all cells, no tail evaluation).** Under ρ ≤ 1/(4 a_up C_use) and k₁ ≤ a_up
(`p5y_k1_cover_ledger_successor/CHECKPOINT.md:91-97`), the ratios A1ρ/A0 = k₁ρC (G) and A2ρ²/A0 = (k₂Cρ² + 2k₁²C²ρ²)
(G) are bounded by cell-independent constants. The A1 and A2 monomials of §1 are therefore **fixed fractions of the
A0 monomials at every cell of the cover**, never asymptotically small.
* On the 34 lower-front cells: 2k₁ρC_upper = 0.49992–0.499999 (`NS/validation/B307_LOWER_FRONT_ORDER3.json`
  `summary_all.cover_factor_2k1rhoC`).

## 4. Exact fixture demonstrations (controls classified (a)–(d) as in `NS/reviews/REVIEW_GLOBAL_INTEGRITY_R1.md` §1)

**Control-class correction (review F6, C-7…C-9).** A pre-repair version counted three controls as evidence that
cannot fail: "A0 := τ_a" (class (d), guaranteed by Lemma SM(d)), the linear slope plant (class (c)) and the five-way
split (class (c), true by construction). They are relabelled NON-EVIDENCE below and replaced by class-(a) plants
through the code under test. The fixture run was repeated with the repaired code (run 3, 368 s).

**Producers and outputs.**
* `code/b307_run_fixtures.py` (run 3, 368 s, ledger entry "B307 exact-fixture audit") writes
  `NS/validation/B307_AUDIT_FIXTURES.json` and `NS/validation/B307_ORDER3_FIXTURES.json`.
* `code/b307_scaling.py` writes `B307_SCALING.json`.
* `code/b307_tower_fixture.py` writes `B307_TOWER_FIXTURE.json`.
* `code/b307_lower_front.py` writes `B307_LOWER_FRONT_ORDER3.json`.

**Coverage.**
* 64 fixture cells: FX_A 48, FX_B 16.
* 320 objects, 4 routes each: surrogate; zero candidate with the exact residual; real Ĝ with η = 10⁻³; real Ĝ with
  η = 10⁻².
* 17 exact grid points per cell.
* 42 ladder points.
* Ranges are min–max, with the median in parentheses.

### T1 — identities (P1): all exact; class-(a) controls fire

| identity | result | planted-invalid control | detected |
|---|---|---|---|
| F^(n) = Σ C(n,i)∂^iR S^(n−i), n = 1, 2, 3 (4 cases) | exact | ∂³R without 3RK₂RK₁R | 4/4 |
| E'' = Rφ'' + 2∂Rφ' + ∂²Rφ at a | exact (also at every one of 64 × 17 grid points × 5 × 4) | factor 2 dropped | yes |
| (P2′)/(P2) φ'''(e0) identity by exact polynomial differentiation, Ĝ = 0 and Ĝ = F''' | exact | 2K₁Ĥ in place of 3K₁Ĥ | 2/2 |
| Lemma SM(d): τ_a/D = Λ, and D = ν(h₁) (42 points) | exact | "A0 := τ_a" claimed ≥ Λ — **class (d), NON-EVIDENCE** (guaranteed by SM(d) since D < 1) | 42/42 (not counted) |
| E'' identity, all grid points | exact | class (a): ∂²R without RK₂R, through the identity check | 5439/5439 eligible |
| ladder soundness check `ladder_checks` (42 points) | 0 rung failures | class (a): Lemma-G A1 rung := true·(1 − 2⁻²⁰); class (a): PM ↔ collapse of A2 swapped | 42/42 and 42/42 |
| five-way split P_H + P_G + P_4 + P_1 + P_0 = E''(e)(a) | holds by construction | **class (c), NON-EVIDENCE** (review C-9) | — |

### T2 — atom-constant ladders (ratio of each rung to the true functional norm; every rung sound, 0 failures)

| class | constant | PM | collapse | Lemma G | Lemma Dv′ r2 |
|---|---|---|---|---|---|
| FX_A (24 points) | A0 | — | — | 1–1.24 (1.03) | 1 (exact at a point) |
| FX_A | A1 | 3.4–191 (29) | 5.5–224 (38) | 6.3–224 (46) | 2.4–33 (13) |
| FX_A | A2 | 5.0–403 (137) | 7.1–701 (205) | 7.7–711 (205) | 4.2–67 (18) |
| FX_B (18 points) | A1 | 5.1–32 (11.5) | 7.4–38 (16.6) | 7.4–38 (16.6) | 3.0–25 (7.6) |
| FX_B | A2 | 34–1320 (141) | 78–1950 (323) | 78–1950 (323) | 11–680 (67) |

`code/b307_lib.py:303-333` (`Point.ladders`).
* The biggest single step is **true → PM**: dropping the sign cancellation of K₁ and K₂ costs 3–400×.
* The collapse and the Λ → C steps cost factors 1–2.
* Dv′ sits well below Lemma G but remains 2.4–680× above the truth.

### T2b — Λ-scaling (FX_B)

See §3. Slopes vs Λ at drift 0: true 1.50 / 2.00 / 2.49; PM 2.01 / 3.01 / 4.00; Lemma G 2.00 / 2.99 / 3.98;
Dv′ 1.91 / 2.83.

Controls:
* The planted rung "true × Λ^{1/2}" (slope exactly +1/2) is **class (c), NON-EVIDENCE**: the least-squares slope is
  linear, so it holds for any data (review C-8).
* Class (a): the documented claim "|slope(true A_j) − (1 + j/2)| ≤ 0.05, j = 1, 2, 3, at drift 0" is checked on
  functionals recomputed through `b307_lib.Point`. It holds (1.499, 2.005, 2.494). The same check on a mutant with
  |K_i| in place of K_i (sign cancellation removed, same code path) **fires** (2.008, 3.006, 4.004)
  (`NS/validation/B307_SCALING.json` `exponent_claim_check`).

### T3 — per-term looseness of the TC radius on fixture cells

Each bound monomial is compared with its own exact truth, the maximum over the grid of the matching piece of E''.
Source: `code/b307_cellpipe.py:168-172` for the split, `code/b307_run_fixtures.py` `summarize_cell` for the ratios.

| class, regime | route | P_H | P_G (ρ f_G) | P_4 (Env4) | P_1 (2A1p1) | P_0 (A2p0) | rad / max\|E''\| |
|---|---|---|---|---|---|---|---|
| FX_A, cover rule | surrogate | 19 | **18** | 19 | 627 | 2770 | 3.5–375 (22) |
| FX_A, cover rule | real Ĝ (η = 10⁻³) | 19 | 29 | 23 | 918 | 5250 | 3.7–363 (26) |
| FX_A, ρ/16 | surrogate | 16 | 14 | 16 | 554 | 821 | 2.9–353 (14) |
| FX_B, cover rule | surrogate | 19 | 3.8·10⁴ | 58 | 3870 | 1.8·10⁴ | 311–4.8·10⁷ |
| FX_B, cover rule | real Ĝ (η = 10⁻³) | 19 | 140 | 330 | 531 | 1.8·10⁴ | 352–9.7·10⁶ |

(Values are medians of bound/truth per term.)

**Share of rad** (medians) under the cover rule, FX_A, surrogate route:
* P_G 0.77; P_4 0.096; P_1 0.17; P_0 0.014 (synthetic; not compared with any tail cell).

**Decomposition of the P_G slack** (FX_A, cover rule, medians):
* norm-only factor A0‖φ'''_0‖/|[Rφ'''_0](a)| = 5.8, of which Λ-only (Λ in place of A0) = 4.9;
* split factor f_G/‖φ'''_0‖ = 2.2 (range 1.3–15);
* Env4 / max‖φ⁗‖ = 1.9 (range 1.2–9.5).

**FX_B degeneracy.** On FX_B the norm-only factor is up to 10⁷, because F_r'''(e0)(a) vanishes identically on 56/80
objects: F_0(a) ≡ 1 and F_1(a) = 1 − p₀(e), and every r vanishes at e0 = 0. The bound does not vanish. This is the
**residual-specific unboundedness** of HO-3 in its purest form. It is a property of this toy; FX_A is the
representative class.

**Soundness.** Every monomial is individually sound, and |E''| ≤ rad on all 320 × 4 × 17 points. The premise checks
‖φ^(j)(e)‖ ≤ p_j(|t|) and ‖φ⁗‖ ≤ Env4 hold everywhere.

**Controls of the soundness check |E''| ≤ rad** (class (b): through the code, not guaranteed; fire rates given).
* The sign-flipped centre motion is detected on 328/640 real-route objects.
* "f_G := 0 as a certificate" (E10 misuse) is detected on 146/320 surrogate objects.
* Both controls fire only where the linear motion exceeds the remaining slack.

(The JSON verdict key `E2_identity_and_split_failures` now counts identity failures only. Split mismatches are
reported separately, as NON-EVIDENCE.)

### T4 — assembly per-r triangle (HO-13)

Σ_r rad_r / m over the joint-residual radius:
* FX_A: 1.42–3.22 (median 2.4);
* FX_B: 1.19–3.39 (median 1.5–2.1).

The joint radius is sound on all 64 cells (`code/b307_cellpipe.py:138`).

### T5 — lower-front historical cells (real order-3 data), 34 cells × 5 objects

Reproduction gate:
* My independent TC arithmetic reproduces the committed TC_CONSUMPTION H_TC exactly: 136/136 (cell, m).
* A planted 2⁻⁶⁰ perturbation of one committed δ_G is detected.

| quantity | min–max (median) |
|---|---|
| f_G^surr (pure-tower σ3 + ε_src[3]) | 118–256 (160) |
| f_G^real = δ_G + ε_src[3] | 0.0044–0.0079 (0.0051) |
| σ3 share of f_G^surr | 0.004–0.53 (0.15) |
| s_G/s_H | 34.8–80.5 (52.8) — matches the committed 34.8–80.5 (`p5y_k5_m5_tail_closure/phase_c/EXECUTION_DECISION.md:53-55`) |
| \|Ĝ(a)\|/s_G | 0.6799–0.6811 — matches the committed 0.680–0.681 |
| α := \|Ĝ(a)\| / (A0·f_G^surr) | **0.0091–0.027 (0.017)** |
| β := ρ·s_G·(4k₁ + 6k₂ρ + 2k₃ρ² + k₄ρ³/6) / (2 f_G^surr) | 0.0033–0.0084 (0.0057) |
| Q_real / Q_surr (A0-level order-3/4 group) | **0.012–0.035 (0.023)** |
| half_real / half_surr (per object) | 0.107–0.294 (0.185) |
| s_G / (C_upper·f_G^surr) ("Perron index") | 0.0065–0.017 |
| 2k₁ρC_upper | 0.49992–0.499999 |
| m-enclosure width, real/surrogate | m = 1: 0.107–0.160; m = 5: 0.157–0.217 |

On real non-target cells, the zero-candidate surrogate's ρ-linear monomial therefore overstates the certified true
centre motion ρ|Ĝ(a)| by a factor of 1/α = 37–110.
* **Scope.** This is a lower-front measurement (e ≈ 0.01, C ≈ 1000). It is **not** transferred to any other cell.
* The σ3 used here is the pure tower. The (P3′) refinement needs Aux3 fields that these cell files do not carry, so
  f_G^surr may be loose on that account as well.

## 5. RANKED LOOSENESS INVENTORY (structural and asymptotic criteria only)

**Ranking key.** Items are ranked by the **slack class** of the inequality:
* **P**: the certified form has a strictly larger asymptotic order than the true object;
* **U**: a norm-only bound on a pointwise, signed object, with no a-priori bound on the ratio (residual-specific);
* **C**: a bounded constant factor.

Compound classes rank above their parts. Ties are broken by how many independent slack sources compose in the item.
**No tail-cell share, factor or margin is used** (see the correction note at the end of this section).

The fixture slack figures are medians on FX_A under the cover rule (T3), unless the row says otherwise. They are
synthetic or lower-front measurements, and are not estimates for any tail cell.

| rank | inequality (§2 id) | slack class | what is discarded | fixture / real non-target evidence | owner / route |
|---|---|---|---|---|---|
| **1** | atom functionals of ∂R and ∂²R in the radius: 2A1·p1 and A2·p0 (HO-5, HO-6, composed with HO-3 and HO-7) | **P × U × C** | the sign cancellation of K₁ and K₂ (zero-mean score; path martingale M_n), the residual shape, the post-atom state | true A_j ∝ Λ^{1+j/2} against every certified rung ∝ Λ^{1+j} (T2b); rung ratios A1 2.4–224, A2 4–1950 (T2); per-term bound/truth P_1 627, P_0 2770 (T3) | LR constants: C_308 (`IDEA_LR_SCORE_CONSTANTS.md`), not implemented here |
| **2** | norm-only atom evaluation of the ρ-linear order-3 term A0·ρ·f_G (HO-11 = HO-3 ∘ HO-8) | **U × C** | the pointwise value and sign of F_r'''(e0)(a); the four-term cancellation (≈ (I−K)F'''); K_i acting as a derivative on smooth candidates | P_G bound/truth 18 (FX_A); split factor 2.2 and norm-only factor 5.8 (T3); unbounded on FX_B (true value ≡ 0); real lower-front cells: 1/α = 37–110 (T5) | real order-3 candidate (R4), ADLR or direct atom bound (REAL_ORDER3_THEORY) |
| **3** | norm-only atom evaluation of the order-4 remainder A0·ρ²·Env4/2 (HO-3 ∘ HO-9) | **U × C** | the pointwise F⁗(a); cancellation among five terms; the cell supremum in e | P_4 bound/truth 19 (FX_A); Env4/‖φ⁗‖ 1.9 (T3). On FX_A this is the dominant monomial of the real-Ĝ route (T3) | needs an order-4 pointwise object or a sharper s_G-free envelope; no route yet |
| 4 | (P3′) J/h Leibniz tower for σ3 (midpoint) and σ4 (cell) (HO-10) | **P in j** (j^{n/2}; bounded for j ≤ 5) | the Gaussian-location structure (Hermite in the summed score) | tower/true at n = 3: h_2 3.1–3.8, h_3 9–12, h_4 24–38, S_4 47–77 (`B307_TOWER_FIXTURE.json`) | Hermite h-tower bound κ_n j^{n/2} (REAL_ORDER3_THEORY §2e); THEORY_ONLY |
| 5 | split and collapse inside f_G and Env4 (HO-8 (i)–(iii), HO-9) | C | four- or five-term cancellation; ‖K_iX̂‖ ≤ k_i s_X | f_G/‖φ'''‖ 1.3–15 (2.2); Env4/‖φ⁗‖ 1.2–9.5 (1.9) | joint residual certificate: needs the candidate payloads (C6) |
| 6 | assembly: per-object radii summed (HO-13) | C | cross-object cancellation of the errors | per-r / joint 1.4–3.2 (2.4) (T4) | joint residual: data-blocked (C6) |
| 7 | whole-cell time substitution \|t\| → ρ (HO-7) | C | the profile | bounded constant | TPT (stream E) |
| 8 | A0 (HO-4) | C (≤ 1.24 on fixtures; Dv′ exact at a point) | the start state and drift; SM(d)-sharp | T2 | A0X / C_308 |
| 9 | clause: magnitude, weight, profile (HO-14, HO-15) | C | the sign of R'', the weight t, the profile | bounded constant; TPT optimal within its three-input family | stream E |
| — | HO-1, HO-2, the (P2)/(P2′) identities, SM(d), D = ν(h₁) | **exact** | nothing | T1 | — |

**Remarks.**
* **Ranks 1–3 are all norm-only evaluations of pointwise objects.** The higher-order chain is loose for one
  structural reason: every order ≥ 3 object is represented by **norms of candidates and sources times a norm-only
  atom constant**, while the quantity bounded is a single signed point value at the atom.
* **Rank 1 is the only item with a proven growing gap.** Its growth comes entirely from discarded sign
  cancellation: the PM rung already has the certified exponent (T2b). That makes it the most structurally avoidable
  item, independently of any cell.
* **Rank 3 is the item no current route addresses.** On fixtures it becomes dominant once rank 2 is improved (T3,
  real route).

**Correction note (incident 01).** A pre-correction version of this section and of §2–§4 placed route or synthetic
gain factors (for example TPT-G's profile factors, and fixture share patterns) next to committed tail-cell shares
of S. That adjacency is a target-equivalent proxy. It was corrected on coordinator instruction (incident 01). The
committed decomposition now appears only in the history section §0, with no route factor attached.

## 6. What the audit says about cell 307 (structural statements only; no new 307 number)

1. **The (A1, A2) blocker is a product.** The committed knockout (§0, history) names (A1, A2) as 307's blocker under
   the committed clause. In the radius, A1 and A2 multiply p1 and p0, whose content is ρ²f_G/2 + ρ³Env4/6 and
   ρ³f_G/6 + ρ⁴Env4/24 up to measured-residual terms (§1). So that blocker is structurally **rank 1 × (ranks 2–3
   quantities)**, and two independent structural levers act on it multiplicatively:
   * sharper atom functionals of ∂R and ∂²R. This is the C_308 LR stream; the asymptotic slack is pure sign
     cancellation (§3);
   * sharper order-3/4 quantities. This is REAL_ORDER3_THEORY: a real Ĝ, ADLR, or a direct atom bound.
2. **The cover rule makes the A1/A2 monomials structural.** k₁ρC ≤ 1/4 at every cell of the cover (§3), so they are
   never asymptotically small relative to the A0 monomials at any cell.
3. **Improving order 3 moves the problem to order 4.** On fixtures, a route that improves only the ρ-linear order-3
   term hands the dominant share of the radius to the order-4 envelope (rank 3; §4 T3). Rank 3 has no owner yet.
4. **Nothing here is a 307 forecast.** No quantity was evaluated at 307 or in its drift band. No fixture or
   lower-front ratio is combined with any committed tail-cell figure. None is to be transferred to the tail as an
   estimate (`p5y_k5_tail_route_audit/ROUTE_AUDIT_R1.md` §8 logic; quarantine rule on calibration).

## 7. Reproduction

    cd NS/streams/B_307/code
    nice python3 b307_run_fixtures.py      # T1–T4, ORDER3 fixtures  (≈ 6 min, exact)
    nice python3 b307_scaling.py           # T2b slopes (post-processing)
    nice python3 b307_tower_fixture.py     # HO-10 tower evidence
    nice python3 b307_lower_front.py       # T5 (34 committed lower-front cells, exact reproduction gate 136/136)
    nice python3 b307_hermite_check.py     # Hermite / LR identity at the declared drifts (float)
    python3 ../../../code/ov_quarantine.py --scan    # B_307 files: 0 findings, planted control detected

Each run appends one line to `NS/ledger/ZERO_TARGET_LEDGER.jsonl`, with class SYNTHETIC_VALIDATION,
NONTARGET_DRIFT_VALIDATION or NONTARGET_REAL_VALIDATION and no target cells touched.
