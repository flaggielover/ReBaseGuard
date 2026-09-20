# Independent fresh-context review r1 — Campaign B (CUSUM K5, m = 5 tail), commit `ae153a69`

**VERDICT: PASS_WITH_NOTES** — the stop decision and all five claims hold, but premise (P3′)'s order-4 re-seeding is
unsound as written and as implemented (N1), the refutation of T2 scores T2 on a weaker premise supply than TCT0 (N4),
and three published data tables are wrong (N14); these must be repaired before publication.

Reviewer method: I wrote my own exact-rational implementation of theorem TC-T from `theorem/THEOREM_TCT.md` and
`p5y_k5_lower_front_order3/theorem/THEOREM_TC.md` **before** reading `code/tct_rule.py`, `code/tail_forecast_r2.py`,
`tc_rule.py` or `tc_crosscheck.py`, and reproduced every published number from it. Local stack: CPython 3.14.5,
stdlib only (`fractions.Fraction`); python-flint, numpy and scipy are **absent** locally. No remote host was contacted.

## Checklist

| # | check | verdict | evidence |
|---|---|---|---|
| **A** | **Lemma G, (P2′), (P3′)** | | |
| 1 | ∂R = R K₁ R and ∂²R = 2 R K₁ R K₁ R + R K₂ R are the correct e-derivatives of R_e | PASS | re-derived: ∂(RK₁R) = RK₁RK₁R + RK₂R + RK₁RK₁R; identical to `THEOREM_AD.md` §4 |
| 2 | A0 = C, A1 = k₁C², A2 = k₂C² + 2k₁²C³ follow by submultiplicativity and \|g(a)\| ≤ ‖g‖ | PASS | ‖∂R‖ ≤ C·k₁·C; ‖∂²R‖ ≤ 2C k₁ C k₁ C + C k₂ C |
| 3 | Lemma G asserts nothing new: these are the frozen generic K1 DAG constants | PASS | `p5y_k5_perron_deflated_resolvent/theorem/OPERATOR_AUDIT.md` §3 lines 45–51: eps(F)=C(λ_F+σ₀), eps(D)=C(λ_D+k₁eps(F)+σ₁), eps(H)=C(λ_H+k₂eps(F)+2k₁eps(D)+σ₂) expands to A0 f_H + 2A1 f_D + A2 f_F |
| 4 | C_upper is a **cell-uniform** operator-norm bound on (I−K_e)⁻¹ | NOT_CHECKABLE_LOCALLY | ‖(I−K)⁻¹‖ = ‖(I−K)⁻¹1‖ for positive operators is established in `OPERATOR_AUDIT.md` §4; cell-uniformity is an inherited frozen-K1 property, not re-derivable here (N2) |
| 5 | theorem TC uses (P4) at exactly one place — §4 step 3 | PASS | A0/A1/A2 occur only in step 3's `\|E''(e)(a)\| ≤ A0‖φ''‖+2A1‖φ'‖+A2‖φ‖`; steps 1/2/4 are premise-free of A |
| 6 | Lemma G's constants reproduce the recorded A0/A1/A2 | PASS | all 15 values exact to double precision on cells 305–309 |
| 7 | (P2′) identity φ‴(e₀) = S‴(e₀) + 3K₁Ĥ + 3K₂D̂ + K₃F̂ with Ĝ := 0 | PASS | derived independently from φ = S − (I−K)F̃ and F̃‴(e₀) = Ĝ = 0 |
| 8 | f_G = 3k₁s_H + 3k₂s_D + k₃s_F + σ₃ is a correct bound on ‖φ‴(e₀)‖ | PASS | term-by-term from item 7 with ‖K_iX̂‖ ≤ k_i s_X and σ₃ ≥ ‖S_r‴(e₀)‖ |
| 9 | s_G = 0 and \|Ĝ(a)\| = 0 are legitimate | PASS | theorem TC §1 lets Ĝ be any *fixed* function; ‖0‖ = 0 and 0(a) = 0 exactly |
| 10 | adding eps_src[3] on top of f_G is a sound over-estimate, honestly stated | PASS | f_G enters p0/p1/p2 with positive coefficients; stated in `THEOREM_TCT.md` §2 and `tct_rule.fG_zero_candidate` (N6) |
| 11 | `candidate_suprema['S:r:3']` bounds the **candidate** Ŝ_r‴ and `midpoint_eps['S:r:3']` its certified midpoint error | PASS | `qualify5._aux_record` filters `cert.sup[(f,i,o)]` on `o == AUX_ORDER == 3`; `aux_certifier.midpoint_order3_eps` builds `out["S:r:3"] = tight_upper(δ_mid(S_r:3) + Σ C(3,i) j_i eps("h:r:3−i"))` |
| 12 | no index-vs-order confusion in the `S:r:3` / `h:j:3` keys | PASS | three-component ids are `family:index:order`; the order slot is filtered to 3. `eps_cell_refined["H:r"]` (two components) is used with r as index in `derived_identity_gate` — correct |
| 13 | σ₃'s use is confined to e₀, where a midpoint bound is the right object | PASS | σ₃ appears only in f_G, i.e. in theorem TC premise (P2), a midpoint premise |
| 14 | the refined h-tower re-seeding of order 4 is a valid upper bound | **FAIL** | `tct_rule.h_tower` replaces t[(j,3)] by a **midpoint** bound (cand + midpoint_eps) and then computes t[(j,4)] = Σ C(4,i) k_i t[(j−1,4−i)], which (P3) requires to hold for **every e in the cell** — see N1 |
| 15 | whether N1 overturns Claim 3 | PASS | it does not: under both repairs I tested cell 305 still closes (mag 4.2456 and 4.5146 vs the 4.8916 needed) — see N1 |
| 16 | (P3′) is applied at r = 0 although the same adopted evidence exists there | INFO | `sigma_source` returns `sup_S0[n]` unconditionally for r = 0; `candidate_suprema['S:0:3']` and `midpoint_eps['S:0:3']` both exist — see N7 |
| **B** | **Independent reproduction of Claim 3** | | |
| 17 | my own TC-T reproduces `H_tail_exact` for m = 5 on all five cells | PASS | worst endpoint disagreement 1.6·10⁻¹⁷ relative (my float-rounded σ is the only source of the gap) |
| 18 | …as **exact** rationals | NOT_CHECKABLE_LOCALLY | the (P3′) inputs are not in the repository — see N2 |
| 19 | my implementation is capable of failing | PASS | 14 perturbations (ρ, sup.H, sup.D, sup.F, k[3], j[2], sup_S0[3], sup_S0[4], H_at_a, W2 lo and hi endpoints, A0, A1, A2) each move the output; d(lo) from −5.1·10⁻⁶ to −2.7·10⁻⁹ |
| 20 | magnitudes 4.2031 / 4.0906 / 3.9692 / 3.9232 / 3.8719 | PASS | mine 4.2031390273 / 4.0905694518 / 3.9692261592 / 3.9231586597 / 3.8719127425 |
| 21 | margins 1.164 / 0.955 / 0.775 / 0.620 / 0.509 (M_needed / M_after) | PASS | mine 1.1638 / 0.9546 / 0.7750 / 0.6200 / 0.5087 |
| 22 | Γ_after negative at 305, positive at 306–309, from the frozen cover geometry | PASS | Γ = (R.hi − e₀D.lo) + ρ·x_hi·M with x_lo/x_hi/ρ/e₀ read from `p5y_k1_cover_ledger_successor/config/cells.json`; −0.047476860996 / +0.014379 / +0.078863 / +0.150091 / +0.215646, matching `Gamma_exact` to ≤ 6·10⁻¹⁶ relative; x_hi = cover `right` confirmed against the blocker map's own ρ·x_hi·M |
| 23 | the frozen K5-B predicate self-verifies | PASS | `python3 -B p5y_k5b_independent_countersignature/code/k5b_check.py run` → `"verification": "PASS"`, `"adversarial": "PASS"`, 7229 cells fuzzed, 0 soundness violations, 0 invariant violations, 4/4 mutation families caught |
| 24 | `k5b_literal`'s direct test is exactly (R.hi − e₀·D.lo) + ρ·x_hi·M < 0 | PASS | `k5b_check.py:166,175,188` — `Gamma = (c["R"][1] - c["e0"]*c["D"][0]) + c["rho"]*c["x_hi"]*c["M"]`, `via = "direct" if lt(Gamma, 0)` |
| 25 | the chain route cannot rescue 306–309 | PASS | with μ = H.lo after TCT0 (−4.20 … −3.87) and (x_hi²−x_lo²)/2 = 0.135…0.221, U = γ − μ·dx²/2 = +0.53, +0.57, +0.70, +0.85, +1.01 — every cell needs μ ≥ −0.29 or better |
| 26 | without (P3′) the route closes nothing | INFO | pure-(P3)-tower magnitudes are 13.82 / 13.65 / 13.54 / 13.46 / 13.36, i.e. worse than the adopted 5.27–5.50 — (P3′) is the single most load-bearing premise of Claim 3 (N2) |
| **C** | **Claim 1 — is the refutation of T2 fair?** | | |
| 27 | `classify()` is a faithful transcription of the frozen classes | PASS | STRONG ⇔ cons == 5; USEFUL ⇔ cons ≥ 3 or nom == 5; MARGINAL ⇔ nom ≥ 1; else INFEASIBLE — matches `FEASIBILITY_GATES_B.json` verbatim, including the "not STRONG"/"not USEFUL" ordering |
| 28 | T2_AUDIT closes 3/5 NOMINAL and 1/5 CONSERVATIVE | PASS | reproduced from my own T2 implementation: [305,306,307] and [305] |
| 29 | T2_AUDIT_MEAS closes 3/5 and 1/5 | PASS | reproduced: [305,306,307] and [305]; cell 308 misses by 0.004 out of 2.432 |
| 30 | T2_EVIDENCE closes 0/5, and the critical ratios 60.18/43.23/27.13/14.24/5.47 | PASS | reproduced exactly by my own bisection: 60.1841, 43.2334, 27.1269, 14.2392, 5.4747 |
| 31 | the adopted order-3 evidence the scoring rests on | PASS | recomputed from the 34 committed `TC_CELL_*.json`: sup.G/sup.H 34.786–80.500, \|Ĝ(a)\|/sup.G 0.67986–0.68110, δ_mid(G_r) 2.763·10⁻³–7.860·10⁻³; per-r maxima identical to `adopted_order3_evidence` |
| 32 | s_F = 1, s_D = 2 are defensible and not load-bearing | PASS | T2_AUDIT_MEAS, with every supremum measured, gives the same 3/5 and 1/5 (N8: s_F = 1 is *below* the measured candidate supremum for two objects) |
| 33 | CONSERVATIVE is applied as the frozen gates define it | INFO | s_H = 5 is a not-yet-measured input and is **not** ×4-scaled; the route comparison's own text says "×4 on the unmeasured sG, sH, δ_G". Scaling it gives 0/5 instead of 1/5, so the omission favours the route being refuted — see N3 |
| 34 | TCT0 and the T2 routes are scored on the same premise supply | **FAIL** | TCT0 gets the (P3′)-refined σ₄; the T2 routes go through the frozen `tc_rule.cell_enclosure`, which recomputes σ₄ from the **unrefined** tower. (P3′) is route-independent — see N4 |
| 35 | is there ANY reading of the comparison's stated inputs under which T2 reaches USEFUL? | PASS | only with \|Ĝ(a)\| = 0 **and** the refined σ₄ (then NOMINAL 5/5). With \|Ĝ(a)\| = 10 (= s_G, the comparison's own "≤ sup of the G candidate") or 0.681·s_G, NOMINAL never exceeds 4/5 and CONSERVATIVE never exceeds 1/5 — see N4 |
| **D** | **Identity and provenance of the measured inputs** | | |
| 36 | the 262-field producer identity gate | NOT_CHECKABLE_LOCALLY | ran on `rebaseguard-vultr-02` against sealed K1 records that are not in the repository and needs python-flint; I can confirm only that all five records carry `identical: true`, `fields_compared: 262`, `order3_fields_present: false` |
| 37 | the derived identity gate, reproduced from the measurements and the record endpoints | PASS | I rebuilt Σ_{r<m}(1/m)[Ĥ_r(a) ± eps_cell_refined(H:r)] + Σc·W for m = 1,2,3,5 on all five cells: 20/20 **contained**, worst relative endpoint gaps 3.628, 3.221, 2.903, 3.160, 2.722 ·10⁻⁸ — matching the recorded `worst_relative_gap` to 4 significant figures |
| 38 | the containment-with-tolerance framing is honest and the inclusion direction is safe | PASS | rebuilt ⊆ record, and the gate *also* enforces two-sided endpoint agreement ≤ 10⁻⁶ (`ok = contained and worst <= tol`), so both endpoints are pinned; a wrong Ĥ_r(a) or W moves an endpoint by O(10⁻²–1) ≫ 10⁻⁶. N9 notes that the `max(1,\|w\|)` normalisation makes "relative" an absolute 10⁻⁶ when \|w\| < 1 |
| 39 | the measurement writes no order-3 field of F | PASS | `tct_inputs.measure` emits a hardcoded per-r literal with keys delta_F/delta_D/delta_H/eps_src/sup{F,D,H}/H_at_a only; `certify_real_cell`, `rung3_engine.certify_order3` and `rung3_residual.g_residual` are never called (N10: the G-key refusal loop iterates that same literal and can never fire) |
| 40 | "not a new real scientific evaluation" is defensible | PASS | see N5 — defensible under the programme's own definition ("new real *address*/value"), and the namespace states the distinction explicitly |
| 41 | every replayed field is covered by an identity gate | INFO | `norms.k/j`, `sup_S0` and `sup.{F,D,H}` (order 0) are covered only *indirectly* — the 262-field gate covers midpoint/cell eps nodes, Aux3 residuals and Aux3 **order-3** candidate suprema; the derived gate covers Ĥ_r(a) and W2 — see N5 |
| **E** | **Claim 5 and sequencing discipline** | | |
| 42 | Campaign A byte-unchanged since its freeze `3f540a33` outside `evidence/tc_r1/` | PASS | `git diff --name-only 3f540a33 HEAD -- .../p5y_k5_lower_front_order3` → 64 files, all under `evidence/tc_r1/`, 54858 insertions and **0 deletions** |
| 43 | every adopted predecessor namespace byte-unchanged since `7cb01e38` | PASS | `git diff --name-only 7cb01e38 HEAD -- level4/` touches exactly two namespaces: `p5y_k5_lower_front_order3` and `p5y_k5_m5_tail_closure` |
| 44 | coverage map r4 untouched, sha256 `a3bddd83…`, and no r5 exists anywhere | PASS | `shasum` → `a3bddd83234f33983e07b005b4686a5f3971264bb6bdd64d2c639339de210a35`; last touched at `f2ac1eb3` (Campaign A); `find -iname '*COVERAGE_MAP*'` returns r3, r4 and the older `p5y_k5_remaining_cell_closure` map only |
| 45 | `config/FEASIBILITY_GATES_B.json` byte-identical to its version at `7ee92476`, and `phase_a/`, `phase_b/` unchanged | PASS | empty `git diff --stat 7ee92476 HEAD` for all three paths; sha256 `392101dd03b45ddf8feec5d4b986556ee474e77b5d0ec78488761ffb2cfafd94` as the README claims |
| 46 | `main` and the start frontier untouched | PASS | `origin/main` = `1cb45382…`, `origin/p5y-postk1-frontier` = `3c1c6b9c…`, and `3c1c6b9c` is an ancestor of `ae153a69` with 0 merges |
| 47 | no coverage map was produced and this review was not pre-empted | PASS | `review/` is empty; no file in the namespace asserts a review verdict (the README's "see `REVIEW_R1.md`" is a forward reference to this file) |
| 48 | working tree has no uncommitted change outside the Campaign B namespace | PASS | one modified path, `phase_c/EXECUTION_DECISION.md`, inside the namespace — see N11 |
| **F** | **What the work missed** | | |
| 49 | `ATOM_CONSTANT_REQUIREMENT.json` reproduced by my own bisection | PASS | uniform 1.000000 / 1.053453 / 1.335046 / 1.731144 / 2.194881 and A0-only 1.000000 / 1.068452 / 1.462443 / 2.131985 / 3.153419 — identical to the file for both series |
| 50 | "the binding term is A0·ρ·f_G" | INFO | true for r = 0,1,2 (74 %, 72 %, 65 % of the radius) but **not** for r = 3,4, where A0·ρ²·Env4/2 is comparable or larger (at cell 309 r = 4 it is 1.76 of the 3.32 A0p2, and A0ρf_G is only 38 %) — see N12 |
| 51 | f_G is irreducible with Ĝ := 0 | PASS | setting σ₃ ≡ 0 for every r — a gift far larger than any legitimate refinement — gives 3.0893 / 2.9705 / 2.9102 / 2.8759 / 2.8183 against needs 4.8916 / 3.9051 / 3.0761 / 2.4324 / 1.9698, i.e. still only 3/5. No tightening of f_G alone can close the tail |
| 52 | any cheap legitimate tightening inside TC-T that closes more than cell 305 | PASS | none found. The r = 0 (P3′) gap (N7) moves cell 306 from 4.0906 to at best 4.0347 against 3.9051; the W contribution to the binding endpoint is only −0.08…−0.12 of the ≈ 3.9; a sharper Env4 needs order-4 certified evidence, which Aux3 (AUX_ORDER = 3) does not provide |
| 53 | theorem AD §8's six certificates are genuinely operator-only, so C1 needs no new real address | PASS | `THEOREM_AD.md` §8 states it explicitly for Ā, τ, C, D_lo, D1, D2: "All of these are operator-only (no source S_r, no candidate of F, no R value)"; each is a polynomial supersolution / Bernstein bound. This is argued in the source theorem, not merely asserted by Campaign B |
| 54 | the *size* of the C1 reduction is argued | INFO | asserted, not argued, and the "uniform A0/A1/A2 reduction" framing does not match Lemma Dv′'s structure — see N13 |
| 55 | the measured-range tables in `MEASUREMENT_NOTE.md` and `EXECUTION_DECISION.md` §3 | **FAIL** | three wrong entries and one overstated comparison — see N14 |
| 56 | the "two independent rule paths" cross-check covers the new (P3′) mathematics | **FAIL** | both paths call `tct_rule.h_tower` and `tct_rule.sigma_source`; the 20/20 agreement therefore cannot detect N1 — see N15 |

## Notes

**N1 (must repair; blocking for publication). Premise (P3′)'s order-4 re-seeding uses a midpoint bound where a
whole-cell bound is required.**
`THEOREM_TCT.md` §3 writes «‖h_j‴‖ ≤ min(tower, candidate_suprema['h:j:3'] + midpoint_eps['h:j:3']) and the order-4
recursion is then seeded with the refined lower orders», and `code/tct_rule.py::h_tower` implements exactly that:
`t[(j,3)] = min(v, h3[j])` followed by `t[(j,4)] = Σ_i C(4,i) k_i t[(j−1,4−i)]`.
But `candidate_suprema['h:j:3'] + midpoint_eps['h:j:3']` bounds ‖h_j‴(**e₀**)‖ only — the candidate is a fixed
state-only polynomial for e₀ and `aux_certifier.midpoint_order3_eps` is, by name and by construction, the *midpoint*
error node (the frozen stack keeps a separate `RefinedCellValues`/`delta_cell` path for whole-cell quantities).
Theorem TC premise (P3) needs σ₄ ≥ sup_{e∈C} ‖S_r⁗(e)‖, and σ₄(r) = Σ_i C(4,i) j_i t[(r,4−i)] consumes both
t[(r,4)] and the refined t[(r,3)]. Feeding a midpoint bound into a whole-cell recursion is not valid.
σ₃ is **not** affected: it is only ever used at e₀ (item 13), so the `S:r:3` half of (P3′) is sound as written.

How big is it? I backed the implementation's refined ‖h_j‴‖ out of the recorded σ₄ (it reproduces σ₄ exactly, which
also confirms my reading of the code) and compared it with the omitted correction ρ·sup_C‖h_j⁗‖:

| cell | j = 2 refined / ρ·tower₄ | j = 3 | j = 4 |
|---|---|---|---|
| 305 | 1.4643 / 0.3977 | 3.1206 / 1.8173 | 3.6611 / **5.4023** |
| 309 | 1.9675 / 0.4989 | 3.5020 / 2.3173 | 2.8543 / **6.9627** |

i.e. at j = 4 the omitted term is larger than the refined value itself. Two repairs, both of which I computed:

* **conservative repair** ‖h_j‴(e)‖ ≤ ‖h_j‴(e₀)‖ + ρ·sup_C‖h_j⁗‖ (order 4 from the unrefined tower):
  σ₄(4) at 309 goes 201.1 → 228.3; magnitudes become 4.2456 / 4.1397 / 4.0271 / 3.9909 / 3.9487;
  **cell 305 still closes**, Γ = −0.044545, margin 1.152×.
* **maximal repair** (drop the h-refinement from σ₄ entirely, keep the σ₃ refinement): magnitudes
  4.5146 / 4.4159 / 4.3166 / 4.2936 / 4.2617; **cell 305 still closes**, Γ = −0.026000, margin 1.084×.

So Claim 3's *conclusion* is invariant, but its *published numbers* (4.2031, Γ = −0.047477, the margins
0.96×/0.78×/0.62×/0.51×) are not valid bounds and must be restated. `ATOM_CONSTANT_REQUIREMENT.json` moves too.

**N2 (must repair). The namespace cannot be re-derived from its own evidence.**
`tail_forecast_r2.main` takes (P3′)'s inputs from `record["auxiliary_evidence"]` — the adopted K1 records, which live
only on the compute host. `evidence/measurement_r1/*.json` does **not** carry `candidate_suprema['S:r:3']` or
`['h:j:3']`, and `MEASUREMENT_NOTE.md`'s list of replayed fields does not mention them. σ₃/σ₄ survive in the
repository only as rounded floats in `TAIL_FORECAST_R2.json` `detail.per_r`. Since the pure-(P3)-tower enclosure is
13.36–13.82 and closes nothing (item 26), these unrecorded numbers are the most load-bearing inputs of the whole
campaign. Emitting the ten `S:r:3` / `h:j:3` pairs per cell into the measurement record — they are already inside the
262-field identity gate, so nothing new is trusted — would make the result independently reproducible at zero cost.
Consequence for this review: I reproduced `H_tail_exact` to 1.6·10⁻¹⁷ relative using the recorded σ floats, not as
exact rationals.

**N3 (informational). The CONSERVATIVE scenario is not applied as the frozen gates define it, in the safe direction.**
`SCEN = {"CONSERVATIVE": F(4)}` multiplies only s_G, |Ĝ(a)| and δ_G in `T2_AUDIT`; s_H = 5 is equally
"not-yet-measured" and the route comparison's own parenthesis says "×4 on the unmeasured sG, **sH**, δ_G". Scaling
s_H as well gives **0/5** rather than 1/5, so the deviation makes the refuted route look *better* than the frozen
definition requires and Claim 1 holds a fortiori. Worth stating explicitly rather than leaving for a reader to find.

**N4 (must repair). The refutation scores T2 on a weaker premise supply than TCT0, and this is not disclosed.**
`tail_enclosures` hands TCT0 the (P3′)-refined σ₄ through `T.tail_enclosure`, but hands the three T2 routes to the
frozen `tc_rule.cell_enclosure`, which recomputes σ₄ from the unrefined tower (`tc_rule.sigma4_source`, no `aux`
argument). (P3′) is a statement about the *source*, independent of the choice of Ĝ, so T2 is entitled to it.
Giving T2 the same σ₄ (my own implementation):

| route | as published | with the same σ₄ as TCT0 |
|---|---|---|
| T2_AUDIT NOMINAL | 3/5 | **4/5** (305–308) |
| T2_AUDIT CONSERVATIVE | 1/5 | 1/5 |
| T2_AUDIT_MEAS NOMINAL | 3/5 | **4/5** |
| T2_AUDIT_MEAS CONSERVATIVE | 1/5 | 1/5 |

The class is still MARGINAL (USEFUL needs CONSERVATIVE ≥ 3 or NOMINAL = 5), so **Claim 1 survives** — but by one
cell, not by the comfortable margin the record implies. On the question "is there any reading under which T2 reaches
USEFUL": only if one additionally reads |Ĝ(a)| as 0, which contradicts both the comparison's own "abs_G_at_a ≤ sup of
the G candidate" (whose natural NOMINAL value is s_G) and the adopted ratio 0.681 measured on all 170 objects. With
|Ĝ(a)| ∈ {0.681·s_G, s_G} the best I could reach is 4/5 NOMINAL and 1/5 CONSERVATIVE. The load-bearing half of
Claim 1 — that the comparison's "CONSERVATIVE … 3/5" is wrong — is true under **every** reading I tried.

**N5 (informational). "Not a new real scientific evaluation": both sides.**
*Against*: the replay is a genuine 256-bit numerical evaluation of the frozen model at five real cells, ≈ 1350 CPU-s
each, and it computes quantities (`cert.norms`, `sup_S0`, `cert.sup[F|D|H,r,0]`, `Ĥ_r(a)`, the W enclosures) that the
adopted record does not store; its outputs are load-bearing for a published enclosure. *For*: the programme's line is
drawn at a new real *address* — a quantity with no adopted predecessor — and no such quantity is produced: no order-3
candidate of F is proposed, the gated order-3 entry points are never reached, the guard stays DENY, and every emitted
field is either compared field-by-field against the sealed record (262 of them) or pinned by the derived identity
gate. **Verdict: defensible**, and stated openly in `MEASUREMENT_NOTE.md`. The caveat worth adding to the record is
item 41: `norms.k/j`, `sup_S0` and the order-0 `sup.{F,D,H}` are covered by *neither* gate directly. They are covered
indirectly (they feed the gated residual and Aux3-eps computations, so an error in them perturbs gated fields), but
"identity-gated 5/5" in the README overstates the directness of the coverage for exactly the three families that
dominate f_G.

**N6 (cosmetic).** The forecast field named `delta_G` in `TCT0.detail.per_r` is f_G **without** `eps_src[3]`
(`tail_object` returns `delta_G = dG` and `fG = dG + eps_src[3]`). I confirmed this by reproducing both. Reusing the
frozen field name for a quantity that is not a residual invites misreading; the difference is 0–5.7·10⁻³.

**N7 (informational). (P3′) is not applied at r = 0.** `sigma_source(n, 0, …)` returns `sup_S0[n]` unconditionally,
although `candidate_suprema['S:0:3']` and `midpoint_eps['S:0:3']` are written by the same `_aux_record` /
`midpoint_order3_eps` as the r ≥ 1 entries. σ₃(0) is 0.694–0.700, i.e. 12–14 % of f_G(0). I bounded the missed gain
by setting σ₃(0) = 0 outright: cell 306 improves only from 4.0906 to 4.0347 against the 3.9051 it needs, so **no
further cell closes**. Immaterial, but the asymmetry should be either fixed or explained.

**N8 (informational).** In `T2_AUDIT` the assumed s_F = 1 is *below* the measured candidate supremum for two objects
(cell 305 r = 0: 1.0789; cell 306 r = 0: 1.0389), so those rows are not valid bounds. Harmless here because
`T2_AUDIT` is a forecast at the comparison's stated inputs and `T2_AUDIT_MEAS` gives the same 3/5 and 1/5, but the
record should not describe `T2_AUDIT` as a bound.

**N9 (cosmetic).** `derived_identity_gate` computes `rel = max(|lo−w₀|/max(1,|w₀|), |hi−w₁|/max(1,|w₁|))`. The
`max(1,·)` normalisation turns the "relative" tolerance into an absolute 10⁻⁶ whenever |w| < 1. At the tail |w| ≥ 1.33
so every comparison is genuinely relative; the field name is nonetheless inaccurate in general.

**N10 (cosmetic).** `tct_inputs.measure`'s post-hoc refusal — `if any(key.startswith("G") … for key in
out["r"][str(r)])` — iterates a dict literal written twelve lines above with a fixed key set, and
`order3_fields_present` is a hardcoded `False`. The claim they assert is true by construction; the guard cannot fire
and should not be presented as a check.

**N11 (must repair before publication).** `phase_c/EXECUTION_DECISION.md` carries an **uncommitted** eight-line
addition ("C1 is not route T1") absent from the reviewed commit `ae153a69`. Its substance is fine — T1 was refused for
feeding the registry constants the ρ-dominated *whole-cell* residuals, whereas C1 feeds them TC-T's *Taylor*
residuals, which is a real distinction — but the paragraph's "radius is 2.08–4.07 per r" quotes the r = 0 and r = 4
halves rather than the range: at cell 309 the halves are 2.077, 3.157, 3.767, **4.396**, 4.073. Commit it (corrected)
or drop it; a headline verdict document should not differ between the reviewed commit and the working tree.

**N12 (informational).** "The binding term is A0·ρ·f_G" holds for r = 0,1,2 (74 %, 72 %, 65 % of the radius) but not
for r = 3,4, where A0·ρ²·Env4/2 is comparable or larger (cell 309 r = 4: A0ρf_G = 1.55 of a 4.07 radius, 38 %).
This *strengthens* the stop decision — a route that only removes f_G, which is precisely what T2 does, cannot recover
more than about two thirds of the radius — but the record's framing implies f_G is the whole story.

**N13 (informational). The size of C1's reduction is asserted, not argued.** Lemma Dv′ gives A0 = Ā_eff ≥ sup E_a[τ].
At tail drift e ≈ 1.6–2.1 with the frozen CUSUM (h, k) = (5, ½) the mean increment is e − ½ ≈ 1.1–1.6, so E_a[τ] is of
order h/(e−k) ≈ 3.1–4.5 against C_upper = 5.78–7.73 — a ratio near 1.7, **short of the 2.195× cell 309 needs**. The
document's own risk paragraph concedes this outcome, but "Expected outcome: 5/5" is not supported by anything in the
namespace. Separately, Lemma Dv′ does not scale A0, A1, A2 uniformly: A1 = Ā_eff(κ₁C + δ₁) and
A2 = Ā_eff(2κ₁²C² + κ₂C + 2κ₁Cδ₁ + 2δ₁² + δ₂), where C = sup‖Ĝ_e‖ is the taboo-resolvent bound, a different constant
from C_upper. The `uniform_A_reduction_needed` series is therefore a modelling convenience; the
`A0_only_reduction_needed` series (up to 3.153× at cell 309) is the pessimistic bracket and should lead.

**N14 (must repair). Three published data tables are wrong.** Recomputed from the 25 committed measurement objects:

| claim | where | actual |
|---|---|---|
| `sup.F` 0.258 – 1.079 | `MEASUREMENT_NOTE.md`; `EXECUTION_DECISION.md` §2 ("0.26 – 1.08") | **0.184** – 1.079 (cell 309 r = 4) |
| `sup.D` 0.298 – 0.782 | `MEASUREMENT_NOTE.md` | 0.298 – **0.695** (§2 of `EXECUTION_DECISION.md` has the correct 0.30 – 0.70) |
| `H_at_a` −0.817 – −0.032 | `MEASUREMENT_NOTE.md` | −0.817 – **+0.090**; **four** of the 25 centres are positive, so the stated all-negative range misrepresents the sign structure |
| "per-order growth ≈ 1.1× (H/D) and ≈ 0.6× (D/F) … nothing like the front's 2–4 and ≈ 20" | `EXECUTION_DECISION.md` §3 | those are the r = 0 objects only. Over all 25: H/D = **1.11 – 4.46**, D/F = 0.53 – 1.80; the front is H/D 2.01 – 4.33 and D/F 16.9 – 144.4. The H/D ranges **overlap**, so only D/F is genuinely different |

The `norms.k` row quotes cell 305's values as if tail-wide (cell 309 is [0.99978, 0.79706, 0.96498, 1.50064, 2.77345]).
The front column of the same table is accurate (sup.F 0.060–1.222, sup.D 8.281–21.635, sup.H 18.526–80.436,
H_at_a +6.103–+53.885, C_upper 1011.2–1177.0). None of this is load-bearing — the rule reads the JSON, not the table —
but the last row is the evidential basis for the §3 argument that the tail's order-3 ratio *could* be 10× smaller than
the front's, and on a like-for-like basis that argument is weaker than stated. The §3 conclusion ("that is possible …
but it is **not evidence**") remains correct.

**N15 (must repair). The double-path cross-check does not cover the new mathematics.**
`THEOREM_TCT.md` §5 and `CAMPAIGN_A_OPEN_NOTES_DISPOSITION.md` present "two independent rule paths … agree as exact
rationals on every cell and every m, 20/20" as the structural safeguard for this successor. But
`tail_enclosure_crosscheck` calls `tct_rule.h_tower` and `tct_rule.sigma_source` — the (P3′) supply, which is the new
and load-bearing part — and is handed the same `A` dict from `atom_constants_generic`. It re-derives the Taylor sums,
the Env4 envelope and the assembly table only. The 20/20 agreement is therefore silent on N1, which is exactly the
defect it was meant to catch. The claim "importing no `tc_rule`" is literally true and the claim "two independent rule
paths" is not.

**N16 (informational, in the work's favour).** Several things I expected to find wrong are right: the assembly table
c(m,t) = 1/t − 1/m over the ten W_(r,j) with r + j ≤ 3 matches the measurement records' key set exactly; the TCT0
enclosure is applied to m = 1,2,3 as well and `regressed = []` is genuine (intersection can only narrow H and lower M,
so Γ is monotone); cells 305–309 lie outside `ADOPTED_DOMAIN` (0,148), `TEXT_CHANNEL` (1–40) and `A_CELLS` (11–44), so
their pre-route H really is the record's `R2_interval` and L is None — which is why my blocker-map-based Γ
reproduction agrees with `Gamma_exact` to 6·10⁻¹⁶; and `critical_ratio`'s bisection, the classification, the stop
verdict and `ATOM_CONSTANT_REQUIREMENT.json` all reproduce exactly.

## What I did not check

* Anything on a remote host. The 262-field producer identity gate, the ≈ 6740 CPU-s replay itself, the sealed K1
  records, `auxiliary_evidence`, and the full `tail_forecast_r2.py` run (which needs `--records` and the pinned
  adapter/loader/Perron/T-EXT chain) are all off-host artefacts I could not re-execute.
* The exact-rational values of σ₃ and σ₄ for r ≥ 1, and the underlying Aux3 `candidate_suprema` / `midpoint_eps`
  (N2). I verified their *semantics* by reading `aux_certifier.py` and `qualify5.py`, the pure tower exactly, and the
  downstream arithmetic given the recorded floats.
* Whether C_upper is genuinely cell-uniform and whether k_i, j_i genuinely bound ‖K_i(e)‖, ‖J_i(e)‖ over the cell
  (inherited frozen-K1 premises, item 4).
* The four adopted-state channels' composition (Perron deflation on [0,148], T-EXT C1/C2 on cells 1–40, the sealed
  Campaign-A enclosures on 11–44) and the replay gate against `1fa8d8de…` — I checked only that the tail cells are
  outside all of them, which is what makes my Γ reproduction valid.
* `code/b0_state_verify.py`'s eight gates were not re-executed; I independently re-derived G5 (immutability), G6
  (gates and blocker map sha) and the r4 sha by hand, and they agree.
* python-flint / numpy / scipy are absent locally, so no Arb-precision quantity was recomputed.
* Campaign A's own adjudication (`27 PASS / 7 INFO / 3 NOT_CHECKABLE_LOCALLY / 0 FAIL`) was taken as given; this
  review re-derived only the Campaign-A order-3 ratios that Campaign B's scoring depends on (item 31).

## Counts

| verdict | count |
|---|---|
| PASS | 43 |
| INFO | 6 |
| NOT_CHECKABLE_LOCALLY | 3 |
| FAIL | 4 |
| **total checks** | **56** |

INFO items: 16, 26, 33, 41, 50, 54. NOT_CHECKABLE_LOCALLY items: 4, 18, 36.

FAIL items: 14 (P3′ order-4 re-seeding, N1), 34 (asymmetric premise supply in the route scoring, N4),
55 (wrong measured-range tables, N14), 56 (cross-check does not cover the new premise supply, N15).

**FINAL VERDICT: PASS_WITH_NOTES.** The stop decision is correct and mechanically applied; Claims 1, 2, 4 and 5 are
established, and Claim 3's conclusion — cell 305 closes with zero new real addresses, cells 306–309 do not — survives
every repair I could construct. Notes N1, N2, N4, N11, N14 and N15 must be repaired before this is published as the
campaign record; N1 in particular means the published magnitude 4.2031 and Γ = −0.047477 are not valid bounds and
must be restated (≥ 4.2456 / −0.044545 under the conservative repair, 4.5146 / −0.026000 if the h-tower refinement is
withdrawn from σ₄ altogether).
