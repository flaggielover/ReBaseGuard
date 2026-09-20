# Independent fresh-context review r2 — Campaign B (CUSUM K5, m = 5 tail), commit `5ed8f059`

**VERDICT: PASS_WITH_NOTES** — all four round-1 FAILs (N1, N4, N14, N15) are REPAIRED, the (P3′) r2 mathematics is
sound, and every repaired headline number reproduces **exactly, as exact rationals**, from an implementation I wrote
from the theorem alone; four prose claims in `phase_c/EXECUTION_DECISION.md` §4/§5,
`CAMPAIGN_A_OPEN_NOTES_DISPOSITION.md` and `theorem/THEOREM_TCT.md` §2/§3 carry wrong numbers and must be corrected
before publication (M1–M4). Nothing found moves a headline number, a theorem step, the stop decision or cell 305's
closure.

Reviewer method: I wrote my own exact-rational implementation of theorem TC-T from `theorem/THEOREM_TCT.md` and
`p5y_k5_lower_front_order3/theorem/THEOREM_TC.md` **before** opening `code/tct_rule.py`, `code/tail_forecast_r2.py`,
`tc_rule.py` or `tc_crosscheck.py`, driving it **only** from committed files:
`evidence/measurement_r1/TCT_INPUTS_30{5..9}.json`, `evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json` and
`p5y_k1_cover_ledger_successor/config/cells.json`. Round 1 could only work in floats because the Aux3 inputs were not
published; with the r2 extract everything below is exact `fractions.Fraction`. Local stack: CPython 3.14.5, stdlib
only; python-flint, numpy and scipy absent. No remote host was contacted; no file but this one was written.

One methodological note on my own code: my first run disagreed with every published Γ. The cause was mine —
`cells.json` holds 642 entries, 326 CUSUM and 316 SR, with **duplicate `index` values across detectors**; keying on
`index` without filtering `detector == "CUSUM"` silently loads the SR cell. That is a real trap for any third party
reproducing this namespace and is worth a sentence in the record (M6). After filtering, agreement is exact.

## Checklist

| # | check | verdict | evidence |
|---|---|---|---|
| **A** | **Is the N1 repair sound?** | | |
| 1 | the mean-value step ‖h_j‴(e)‖ ≤ ‖h_j‴(e₀)‖ + ρ·sup_C‖h_j⁗‖ is valid for every e in the cell | PASS | h_j = K_e^{j−1}h_1 is analytic on C by (P1), so h_j‴(e) = h_j‴(e₀) + ∫_{e₀}^{e} h_j⁗(s)ds in B(X); ‖·‖ and \|e − e₀\| ≤ ρ give the bound. The three ingredients are (a) ‖h_j‴(e₀)‖ ≤ adoptedh(j), which is what the Aux3 midpoint evidence asserts, (b) a cell-uniform order-4 bound, item 3, (c) analyticity |
| 2 | ρ is the right radius: the cell really is [e₀ − ρ, e₀ + ρ] | PASS | exact on all five cells: `e0 − rho == left`, `e0 + rho == right`, `right − left == 2·rho` as Fractions, in both the frozen cover and the measurement records; and the measurement's `e0/rho/left/right` equal the cover's exactly |
| 3 | `pure[j,4]` is a legitimate **cell-uniform** bound on ‖h_j⁗‖ | PASS | re-derived from theorem TC (P3) myself: `pure[1,n] = sup_C‖S_0^{(n−1)}‖` (h_1′ = −S_0 exactly), `pure[j,n] = Σ_{i=0..n} C(n,i) k_i pure[j−1,n−i]` from h_j = K_e h_{j−1} pointwise in e with ‖K_i(e)‖ ≤ k_i on C. Every input (k_i, sup_S0) is cell-uniform, so every output is |
| 4 | the cell tower's order-4 re-derivation from the corrected lower orders is valid | PASS | the Leibniz identity h_j^{(4)}(e) = Σ_i C(4,i)K_i(e)h_{j−1}^{(4−i)}(e) holds **pointwise in e**; t_cell[j−1,n] is cell-uniform for n = 0,1,2 (= pure), n = 3 (item 1) and n = 4 (induction, base t_cell[1,4] = pure[1,4]). So the sum is cell-uniform. This is exactly what theorem TC (P3) needs, and exactly the defect N1 named |
| 5 | no circularity | PASS | `pure_tower` is computed in full, from frozen inputs only, before any correction; the order-3 correction at level j reads `pure[(j,4)]`, never `cell[(j,4)]`; `cell[(j,4)]` reads only `cell[(j−1,·)]`. The dependency graph is a DAG |
| 6 | no ordering bug | PASS | `h_towers` sets **all** order-3 slots in one loop j = 1..4, then computes `cell[(j,4)]` in a second loop with j ascending, so `cell[(j−1,4)]` exists before `cell[(j,4)]`. My own implementation uses the same order and agrees exactly |
| 7 | the order-4 clamp `min(recursion, pure[j,4])` is sound and monotone | PASS (INFO) | the minimum of two valid upper bounds is valid. It is in fact **never binding**: t_cell ≤ pure componentwise, so the recursion is automatically ≤ pure[j,4]. I verified 0 firings over all 5 cells × j = 2,3,4. Defensive only — see M7 |
| 8 | σ₃ may use the midpoint tower: every consumer traced | PASS | σ₃ reaches exactly one place, `fG_zero_candidate` → `f_G`, and f_G reaches exactly `taylor_bounds` as the coefficient of ρ³/6, ρ²/2, ρ in p0/p1/p2 — i.e. the Taylor coefficient of φ‴(**e₀**), theorem TC premise (P2), a midpoint premise. f_G does **not** enter `env4` |
| 9 | σ₄ reaches only Env4 (premise (P3), whole cell) | PASS | `tc_rule.env4(sF,sD,sH,sG,k,sigma4,rho)` is the only consumer; σ₄ appears there additively and nowhere else. `tc_rule.taylor_bounds` takes `e4` as an opaque scalar |
| 10 | the r = 0 pair of keys `candidate_suprema['Sclosed:0:3']` + `midpoint_eps['Sclosed:3']` is right | PASS | theorem TC (P2) defines src(0,k) = `Sclosed:k`, so the eps key has two components and the candidate key three (`family:index:order`); both exist in the extract for all five cells |
| 11 | the r = 0 source is the closed form, so `sup_S0[3]` and `Sclosed:0:3` should agree | PASS (INFO) | they agree to **8.7·10⁻¹⁷ relative** on all five cells, with `sup_S0[3]` marginally the smaller. Consequence: `min(sup_S0[3], Sclosed:0:3 + eps)` always selects `sup_S0[3]`, so the r = 0 refinement is **inert** — round 1's N7 is answered by construction rather than by a numerical gain. My downward perturbation of the adopted r = 0 value moves nothing; the upward one moves nothing either (M5) |
| 12 | `eps_src[0..3]` are midpoint DAG values and (P2) is a midpoint premise for all four | PASS | theorem TC (P2) states all four of ‖φ(e₀)‖, ‖φ′(e₀)‖, ‖φ″(e₀)‖, ‖φ‴(e₀)‖ at e₀, and the Taylor step (§4 step 1) is the only consumer of f_F/f_D/f_H/f_G. A midpoint ε is the right object in each |
| 13 | s_F, s_D, s_H, s_G in Env4 raise no midpoint-vs-cell question | PASS | they bound ‖F̂‖, ‖D̂‖, ‖Ĥ‖, ‖Ĝ‖ — sup norms of **fixed, e-independent** state-only functions (theorem TC §1). There is no e to be uniform over |
| 14 | any other place where a midpoint quantity stands in for a whole-cell one, or vice versa | PASS | I traced every input of `tail_object`/`tail_enclosure`: f_F/f_D/f_H/f_G/σ₃ midpoint→(P2); σ₄/s_X/k_i→(P3) whole-cell; C_upper, k_i, j_i frozen cell-uniform (inherited, item 15); `H_at_a`/`W2` are the adopted centre and the frozen **whole-cell** W enclosures, used in the assembly only; `eps_cell_refined` is used only by `derived_identity_gate`, never by the enclosure. No further inversion found |
| 15 | C_upper, k_i, j_i are genuinely cell-uniform | NOT_CHECKABLE_LOCALLY | inherited frozen-K1 premises, as round 1 item 4 found. I could confirm only that the extract's `C_upper`, `e0` and `rho` equal the frozen cover ledger's (`cells.json`, sha `341eb5e9…`) exactly |
| 16 | the `h:1:3` adopted bound is not binding | INFO | `pure[1,3] = sup_S0[2] = 0.5462 < adoptedh(1) = 0.6787`, so the min selects the tower and the j = 1 adopted evidence never enters. Harmless; noted so a reader is not misled about how much of (P3′) is live (M5) |
| **B** | **Independent reproduction, exact rationals** | | |
| 17 | the five m = 5 `H_tail_exact` (both endpoints), `M_after_exact` and `Gamma_exact` strings | PASS | **exact Fraction equality**, 20/20 strings, all five cells. Not "to 10⁻¹⁷" — byte-equal after rational normalisation |
| 18 | m = 1, 2, 3 (no exact strings are published there) | PASS | all floats reproduce with delta 0.0: `H_tail`, `mag_tail`, `M_after`, `Gamma`, 15 cells × 4 fields. Note the published `H_tail` is the **route** enclosure before intersection, while `M_after` is min(M_R2, mag(H ∩ H_adopted)) — the two differ at m = 1, 2 and I reproduce both |
| 19 | magnitudes 4.257155 / 4.151682 / 4.040057 / 4.005124 / 3.964274 | PASS | mine 4.2571547291 / 4.1516820791 / 4.0400566570 / 4.0051240513 / 3.9642743261 |
| 20 | Γ −0.043752 / +0.019116 / +0.085118 / +0.158343 / +0.226117 | PASS | mine −0.043751780433 / +0.019115585049 / +0.085117769892 / +0.158342964745 / +0.226117166471, from Γ = (R.hi − e₀·D.lo) + ρ·x_hi·M with x_hi = cover `right` |
| 21 | margins 1.149 / 0.941 / 0.761 / 0.607 / 0.497 and M_needed 4.8916 / 3.9051 / 3.0761 / 2.4324 / 1.9698 | PASS | mine 1.1490 / 0.9406 / 0.7614 / 0.6073 / 0.4969 and 4.891579 / 3.905056 / 3.076148 / 2.432398 / 1.969828 |
| 22 | the full `detail.per_r` block and A0/A1/A2 | PASS | `sigma3`, `sigma4`, `env4`, `f_G_incl_eps_src3`, `order3_residual_bound`, `rad`, `half`, `sup_G`, `abs_G_at_a` and A0/A1/A2: **worst absolute delta 0.0** over all 25 (cell, r) objects |
| 23 | my implementation is capable of failing | PASS | **53** independent +0.1 % perturbations, each applied to all five cells: ρ; each drift-aware norm `k_0..k_4` and `j_0..j_4`; each `sup_S0[0..4]`; each `sup.F/D/H` at each r; each adopted `h:j:3`; each adopted `S:r:3` and `Sclosed:0:3`; A0, A1, A2; each `H_at_a`; five W2 endpoints. **49 move the output**; d(mag) at 305 ranges from +5.4·10⁻³ (ρ) and +2.3·10⁻³ (k₁) down to +6.5·10⁻⁶. All ten norms move it (k₄ smallest at +3.6·10⁻⁵, j₄ at +3.5·10⁻⁵), so the (P3)/(P3′) tower is genuinely live in my path. The four that do not move it are **explained, not excused**: `h:1:3` (item 16), `Sclosed:0:3` upward (item 11), and two W2 **hi** endpoints (the magnitude binds on the negative endpoint — they do move `H_tail[1]`, by 2.0–4.5·10⁻⁵). A downward perturbation of `Sclosed:0:3` does move it (−5.6·10⁻⁵), confirming the `min` is live in one direction |
| 24 | `atom_constant_requirement`, both series | PASS | my own bisection: A0-alone 1.000000 / 1.091314 / 1.501903 / 2.205575 / 3.294279; uniform 1.000000 / 1.071062 / 1.361618 / 1.771344 / 2.252903 — identical to the file and to `ATOM_CONSTANT_REQUIREMENT.json`, whose `cells` section is byte-equal to the forecast's |
| 25 | `critical_sup_G_over_sup_H_ratio` 64.72 / 47.99 / 32.03 / 19.20 / 10.55 | PASS | my own bisection reproduces all five to every published digit, under exactly one definition out of the twelve I tried: s_G = ratio·(measured s_H), \|Ĝ(a)\| = ag_max(r)·s_G, δ_G = dg_max(r), criterion "the frozen direct test still passes". The label attached to it in `THEOREM_TCT.md` §2 is wrong — see M4 |
| 26 | `ADOPTED_TAIL_INPUTS.json` is internally consistent with what `detail.per_r` implies | PASS | the extract's Aux3 values are the **only** non-frozen input to σ₃/σ₄, and they reproduce all 25 recorded σ₃/σ₄ floats with delta 0.0 (item 22). The extract's `R_interval`/`D_interval`/`R2_interval`/`M_R2` reproduce all five Γ and M_after exactly (items 17, 20); `M_R2 == mag(R2_interval)` on all 20 (cell, m) |
| 27 | the frozen assembly table c(m) I derived is the frozen one | PASS | independent confirmation: `p5y_k1_cover_ledger_successor/config/checkpoint.json` `assembly["5"]` lists F_r 1/5 and W(0,0) 4/5, W(0,1)=W(1,0) 3/10, W(0,2)=W(1,1)=W(2,0) 2/15, W(0,3)…W(3,0) 1/20 — exactly 1/t − 1/m with t = r + j + 1 |
| 28 | the adopted M, Γ-before and phase-A blocker ratios | PASS | adopted M 5.4983 / 5.4270 / 5.3352 / 5.2961 / 5.2699; Γ before +0.041841 / +0.117964 / +0.199484 / +0.288317 / +0.374145; M must fall by 1.1240× (305) … 2.6754× (309), matching `phase_a` 1.12×/2.67× |
| **C** | **Did the N4 repair introduce a new problem?** | | |
| 29 | the refinement touches only the σ₄ term of Env4 | PASS | `tc_rule.env4` returns `sigma4 + 4k₁s_G + 6k₂(s_H+ρs_G) + 4k₃(s_D+ρs_H+ρ²s_G/2) + k₄(s_F+ρs_D+ρ²s_H/2+ρ³s_G/6)`; σ₄ enters additively and the s_G/s_H/s_D/s_F terms are untouched by (P3′) |
| 30 | the σ₄ handed to `env4` is still valid when s_G ≠ 0 | PASS | σ₄ bounds sup_C‖S_r⁗(e)‖ — a property of the **true source**, which does not mention F̂, D̂, Ĥ, Ĝ at all. The (P3) proof splits φ⁗ = S⁗ + Σ C(4,i)K_i F̃^{(4−i)}; changing Ĝ changes only the second sum. So (P3′) is route-independent, which is what N4 asked for |
| 31 | every route now goes through one premise supply | PASS | `tail_enclosures` calls `T.tail_enclosure(R, mk, ak, A, m, o3)` for all four modes with the same `aux`; `tc_rule.cell_enclosure` now appears only in `compose()` for the **sealed Campaign-A** cells 11–44, which is correct |
| 32 | `order3_inputs` for T2_AUDIT scales s_F, s_D, s_H by the scenario factor | PASS | `{"sup_F": 1·scen, "sup_D": 2·scen, "sup_H": 5·scen, "sup_G": 10·scen, "abs_G_at_a": 10·scen, "delta_G": 10⁻³·scen}`. This matches the frozen comparison's own parenthesis "×4 on the unmeasured sG, **sH**, δ_G" (`phase_b/TAIL_ROUTE_COMPARISON.md` line 11), so round 1's N3 is answered |
| 33 | larger s_F/s_D/s_H is the unfavourable direction | PASS | ∂Env4/∂s_F = k₄ > 0, ∂Env4/∂s_D = 4k₃ + k₄ρ > 0, ∂Env4/∂s_H = 6k₂ + 4k₃ρ + k₄ρ²/2 > 0; p0, p1, p2 are increasing in Env4 with positive coefficients and rad = A0p2 + 2A1p1 + A2p0 with A > 0. So the radius is strictly increasing in each. Confirmed numerically: T2_AUDIT CONSERVATIVE falls from 1/5 (order-3 inputs only) to 0/5 |
| 34 | `classify()` still matches `config/FEASIBILITY_GATES_B.json` | PASS | STRONG ⇔ cons == 5; else USEFUL ⇔ cons ≥ 3 or nom == 5; else MARGINAL ⇔ nom ≥ 1; else INFEASIBLE — verbatim, including the "not STRONG"/"not USEFUL" ordering. The gates file is byte-unchanged since `7ee92476` (empty `git diff`), sha256 `392101dd…` |
| 35 | the per-route NOMINAL/CONSERVATIVE counts follow from the per-cell `pass` flags | PASS | I reproduced **all 40** per-cell pass flags (4 routes × 2 scenarios × 5 cells) and all 40 Γ floats with delta 0.0 from my own implementation: TCT0 1/1, T2_AUDIT 3/0 (NOMINAL 305–307), T2_AUDIT_MEAS 4/1 (305–308), T2_EVIDENCE 0/0. My mechanical `classify` gives MARGINAL / MARGINAL / MARGINAL / INFEASIBLE, as published |
| 36 | the chain route rescues nothing | PASS | my direct test alone (`Γ < 0`) reproduces all 40 recorded `pass` flags, so at m = 5 on cells 305–309 the chain route adds no closure for any route or scenario |
| 37 | is there now any route or reading that reaches USEFUL? | INFO | not at any defensible \|Ĝ(a)\|. With \|Ĝ(a)\| = s_G (the comparison's own input) the best is 3/5; with \|Ĝ(a)\| = 0.681·s_G (the adopted ratio on all 170 objects) the best is 4/5 NOMINAL and 1/5 CONSERVATIVE. Only \|Ĝ(a)\| ≡ **0** reaches 5/5 NOMINAL ⇒ USEFUL, and nothing supports a candidate that vanishes exactly at the atom. Same finding as round 1 item 35; still the one hinge of the refutation, and worth one explicit sentence in the record (M8) |
| **D** | **The self-containment claim** | | |
| 38 | `manifest_sha256` is checkable against a committed file | PASS | `29ad1f9bb8630a5f3f9aab74d400d552516f0774a05e2b219d66f38b2da0d334` is exactly `shasum -a 256` of the committed `p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/COMPOSITE_EXPORT_MANIFEST.json` (35 312 bytes, 326 file entries) |
| 39 | the per-cell `record_sha256` match that manifest's `k4_records/aux5_CUSUM_<k>_256.json` entries | PASS | 5/5: `585f56c2…`, `9c9da15b…`, `28bacf0a…`, `e8d7a412…`, `95be4c65…` |
| 40 | …and match each measurement record's `k1_record_sha256` | PASS | 5/5, so extract, measurement and manifest are bound to the same record triple-wise, locally |
| 41 | the extract's **field values** are the record's field values | NOT_CHECKABLE_LOCALLY | the 90 MB export tree is not in the repository, so the hash chain stops at the manifest. `tail_forecast_r2.main` does re-verify every emitted field (`candidate_suprema`, `midpoint_eps`, `eps_cell_refined`, per-m intervals, `M_R2`, `C_upper`) against the live record and exits on any difference — but that check runs only where the records live |
| 42 | partial local corroboration of the extract | PASS | the extract's `C_upper`, `e0` and `rho` are exactly the frozen cover ledger's (`cells.json`, sha `341eb5e9…`) on all five cells; `M_R2 == mag(R2_interval)` on all 20 (cell, m); and the Aux3 values reproduce every published σ₃/σ₄ |
| 43 | `derived_identity_gate` rebuilt locally from committed files only | PASS | I rebuilt it myself from the measurement `H_at_a`/`W2` and the extract's `eps_cell_refined`/`R2_interval`: **20/20 contained**, and my `rebuilt`/`record` rational strings and `endpoint_gap_normalised` floats are byte-identical to the recorded ones. Worst gaps 3.628 / 3.221 / 2.903 / 3.160 / 2.722 ·10⁻⁸ |
| 44 | can item B be run from committed files alone? | PASS | yes — this entire review's arithmetic used no file outside the repository. N2 is substantively discharged: every number the enclosure depends on is now published |
| 45 | can the shipped tool be run from committed files alone? | INFO | no. `tail_forecast_r2.py` still requires `--records DIR`, and it takes `aux`, `C_upper` and the per-m intervals from the **live record**, using the extract only as a checker. A third party can re-derive the mathematics (item 44) but cannot re-execute the generator (M9) |
| **E** | **Prose accuracy** | | |
| 46 | `README.md` | PASS | 1.12×/2.67×; 3/5, 0/5, 4/5, 1/5, 0/5; 4.257155 vs 4.8916; Γ +0.041841 → −0.043752; margin 1.149×; 0.94×/0.76×/0.61×/0.50×; both atom-constant series; the N1 before/after magnitudes 4.2031/4.0906/3.9692/3.9232/3.8719 → 4.2572/4.1517/4.0401/4.0051/3.9643 — all confirmed |
| 47 | `EXECUTION_DECISION.md` §1–§3 | PASS | the §3 route table, the critical-ratio row, "3.3–7.6× smaller" (34.79/10.546 = 3.30, 80.50/10.546 = 7.63), the quotations from `phase_b` line 11, and the §2 comparison table (s_H 0.5723–1.3345, s_D 0.2981–0.6952, s_F 0.1843–1.0789, s_G/s_H 34.8–80.5 ⇒ 20–107 on the tail, \|Ĝ(a)\|/s_G 0.680–0.681, δ_mid(G_r) 2.8–7.9·10⁻³ over all 170 objects) |
| 48 | round 1's N14 tables, corrected | PASS | recomputed from the 25 committed objects: sup.F **0.1843–1.0789**, sup.D **0.2981–0.6952**, sup.H 0.5723–1.3345, H_at_a **−0.8171…+0.0897 with exactly 4 of 25 positive**, sup.H/sup.D **1.1127–4.4643**, sup.D/sup.F **0.5318–1.8047** — every corrected entry is right, and the overlap claim for sup.H/sup.D is correctly stated |
| 49 | the front column and the remaining `MEASUREMENT_NOTE.md` rows | PASS | front (34 cells, 170 objects) sup.F 0.0603–1.2222, sup.D 8.281–21.635, sup.H 18.526–80.436, H_at_a +6.103–+53.885, H/D 2.006–4.326, D/F 16.92–144.40, C_upper 1011.2–1177.0, norms.k [1, 0.79788, 0.96788, 1.51001, 2.80057], sup_S0 [0.7042, 0.4839, 0.5283, 1.101, 1.48]; tail norms.k and sup_S0 rows also exact; CPU 1359.6+1351.3+1350.2+1357.5 = 5418.6, +≈1320 ⇒ ≈6740 s ≈ 1.87 CPU-h |
| 50 | the per-r radii at cell 309: 2.077 / 3.157 / 3.786 / 4.498 / 4.414 | PASS | mine 2.0772 / 3.1569 / 3.7861 / 4.4978 / 4.4136. (Round 1's N11 figure 4.396 at r = 3 was the pre-repair value; the repaired 4.498 is correct) |
| 51 | §4 "A0·ρ·f_G is ≈ 74 %, 72 %, 65 % of the radius at r = 0, 1, 2" | PASS | cell 309: 73.9 %, 71.7 %, 65.0 %; cell 305: 74.5 %, 72.1 %, 68.2 % |
| 52 | §4 "…but **not** at r = 3, 4, where A0·ρ²·Env4/2 is comparable or larger", and "cannot recover more than about two thirds of the radius" | **FAIL** | both halves are wrong — see **M1** |
| 53 | §5 the CUSUM parameters (h, k) = (5, ½) | PASS | `p5y_k1_cover_ledger_successor/config/checkpoint.json` → `scope.detectors.CUSUM = {"h": 5, "k": 0.5, "two_sided": true, …}` — reachable and checked locally |
| 54 | §5 "E_a[τ] ~ h/(e − k) ≈ 3.1–4.5 against C_upper = 5.78–7.73" | PASS | e ∈ [1.6209, 2.0923] on the five cells, e − ½ ∈ [1.1209, 1.5923], 5/1.5923 = 3.14 and 5/1.1209 = 4.46; C_upper 5.7824–7.7326. The derived "ratio near 1.7" (per cell 1.73–1.84) and hence "clears 306 (1.091) and 307 (1.502), short of 308 (2.206) and 309 (3.294)" are correct |
| 55 | §5 "at e = 0 the adopted registry bought 469.8 against C_upper = 1233, a 2.6× reduction" | **FAIL** | the registry's own block for e ∈ [0, 5.083·10⁻⁴] gives A0 = Ā_eff = **500.409**, against C_upper = 1232.836, i.e. **2.464×** — see **M2** |
| 56 | `THEOREM_TCT.md` §1, §4, §6 | PASS | A0 5.782–7.733, A1 26.65–47.69, A2 277.9–646.2; f_G ≈ 4.9–8.9 (mine 4.901–8.872); ρ 4.05–5.42·10⁻² on the tail against 2.66–3.10·10⁻⁴ at the front; e ∈ [1.6209, 2.0923]; "0.94×, 0.76×, 0.61×, 0.50×" and "margin 1.149×" |
| 57 | `THEOREM_TCT.md` §3 "σ₄ from ≈ 355 to ≈ 235 at r = 4" (and its repeat in the disposition) | **FAIL** | the pure-tower σ₄(4) at **cell 309** is 345.10, not ≈355; 355.35 is **cell 305**'s. The refined 235.12 and the magnitudes 4.2617 → 3.9643 are cell 309's and are correct — see **M3** |
| 58 | `THEOREM_TCT.md` §3's other numbers | PASS | pure σ₃ at cell 309 for r = 1…4 = 5.876 / 16.889 / 36.523 / 67.196 ("5.9, 16.9, 36.5, 67.2") against refined 3.043 / 3.412 / 3.805 / 2.250 ("3.04, 3.41, 3.81, 2.25"); "σ₃ to 0.69–3.81" is cell 309's range (0.6942–3.8053) and is correct **as a cell-309 statement**, which the surrounding sentences scope; over all five cells it is 0.6942–4.3910 |
| 59 | `THEOREM_TCT.md` §2 "the trade reverses unless the order-3 candidate's certified supremum is below ≈ 10.5–64.7 × s_H" | **FAIL** | 10.5–64.7 is the *closure* threshold, not the break-even between the two enclosures — see **M4** |
| 60 | `FORECAST_R2.md` | PASS | every number checks: the route table, the N8 sentence about s_F = 1 (true at cells 305 and 306, r = 0: sup.F = 1.0789 and 1.0389), the N3 sentence ("1/5 instead of 0/5" — I reproduce both), the critical ratios, both atom-constant series, and `TAIL_FORECAST_R2.json` sha256 `0903715d…` |
| 61 | the recorded output hashes | PASS | `shasum -a 256` of the five committed measurement records equals both `MEASUREMENT_NOTE.md`'s table and the forecast's `derived_identity_gate[*].measurement_sha256`; `adopted_inputs_sha256 = 485fb125…` is the committed extract's hash |
| 62 | `CAMPAIGN_A_OPEN_NOTES_DISPOSITION.md`, apart from the two sentences already failed at 52 and 57 | PASS | "the two disagree by 2–30×" is right (cell 309: 1.93×–29.9×); the N1/C7 obligation is carried forward, not discharged; N5's argument that the enclosure depends on no un-gated order-3 quantity is correct (s_G = \|Ĝ(a)\| = 0, δ_G a closed form of gated quantities, `eps_src[3]` adopted). Its "dominant at r = 3, 4" sentence and its "σ4 up to 355 … at cell 309" are the same two defects as rows 52 and 57 and are failed there, not twice — M1, M3 |
| **F** | **Structure, invariants, and what round 1 missed** | | |
| 63 | N15: the second path shares no function with the first | PASS | `tail_enclosure_crosscheck` re-derives the pure tower, both towers' order-3 slots, the order-4 recursion, both σ's, the Taylor sums, the (P3) envelope and the assembly table in-line; the string "tc_rule" occurs only in its docstring; it calls none of `pure_tower`, `h_towers`, `sigmas`, `sigma_source`, `tail_object` or any `R.*`. I re-derived its algebra by hand and it is equivalent to the theorem |
| 64 | the two namespace paths agree, and agree with a genuinely third implementation | PASS | 20/20 exact-rational agreement between `tail_enclosure` and `tail_enclosure_crosscheck`, and **20/20 with my own** — three independent paths, one of which was written before any of the code was read |
| 65 | the stop decision still follows mechanically | PASS | classes MARGINAL / MARGINAL / MARGINAL / INFEASIBLE ⇒ no route in {STRONG, USEFUL} ⇒ `verdict = STOP_AND_WRITE_COSTED_CONTINUATION_PLAN` by the frozen `stop_rule`, with the gate file byte-unchanged since before any forecast |
| 66 | cell 305's closure is sound under my own implementation, and robust | PASS | Γ(305) = −0.043751780433 < 0, margin 1.149×. Robustness: withdrawing the h-refinement from σ₄ **altogether** (round 1's "maximal repair") gives mag 4.5146 against the 4.8916 needed — 305 still closes. It also survives every +0.1 % perturbation I applied |
| 67 | "setting σ₃ ≡ 0 still closes only 3/5" (§5 "Not recommended") | PASS | under the repaired arithmetic: mags 3.1434 / 3.0316 / 2.9810 / 2.9578 / 2.9107 against needs 4.8916 / 3.9051 / 3.0761 / 2.4324 / 1.9698 ⇒ 3/5 (305–307), as claimed |
| 68 | git invariants | PASS | working tree **clean** (round 1's N11 is resolved: the eight-line §4 addition is committed, and its "2.08–4.07 per r" quote is replaced by the correct 2.077–4.498); `origin/main` = `1cb45382…`; `origin/p5y-postk1-frontier` = `3c1c6b9c…`, an ancestor of HEAD with 0 merges; `git diff 7cb01e38 HEAD -- level4/` touches exactly two namespaces; Campaign A touched only under `evidence/tc_r1/`; coverage map r4 sha256 `a3bddd83…`, **no r5 anywhere**; `config/`, `phase_a/`, `phase_b/` byte-unchanged since `7ee92476` |
| 69 | the frozen module pins | PASS | `tc_rule.py` `8d402d11…` and `tc_crosscheck.py` `1c72117f…` match `tct_rule.FROZEN`; `load_frozen` verified the pin when I executed it |
| 70 | `review/REVIEW_R1.md` was committed together with its repairs | INFO | both live in `46655b31`, not in a commit of its own. Harmless here — the r1 text is unmodified between `46655b31` and HEAD — but a review and the repairs it forces reaching the history in one commit is not ideal provenance (M10) |
| 71 | `evidence/b0_r1/B0_STATE_VERIFICATION.json` was re-run after the repairs | INFO | its only change since `ae153a69` is `head: 006a1260… → 46655b31…`; `ALL_PASS: true`, r4 regenerated byte-identically, `dirty_paths: 9` at the time of the run. Not re-executed by me (M11) |

## Notes

**M1 (must repair). `EXECUTION_DECISION.md` §4 "Where the radius goes" is wrong in both of its quantitative claims,
and `CAMPAIGN_A_OPEN_NOTES_DISPOSITION.md` N3 repeats the first in a stronger form.**
Exact decomposition of rad_r = A0·p2 + 2A1·p1 + A2·p0 into its eight terms (my own implementation):

| cell | r | rad | A0·ρ·f_G | A0·ρ²·Env4/2 | next largest |
|---|---|---|---|---|---|
| 309 | 3 | 4.4978 | **2.463 (55 %)** | 1.139 (25 %) | 2A1ρ²f_G/2 = 0.615 (14 %) |
| 309 | 4 | 4.4136 | 1.552 (35 %) | **2.049 (46 %)** | 2A1ρ²f_G/2 = 0.388 (9 %) |
| 305 | 3 | 4.5217 | **2.741 (61 %)** | 0.852 (19 %) | 0.685 (15 %) |
| 305 | 4 | 5.0786 | **2.535 (50 %)** | 1.546 (30 %) | 0.633 (12 %) |

* "**not** [dominant] at r = 3, **4**, where A0·ρ²·Env4/2 is comparable or larger" is **false at r = 3 on all five
  cells** — there A0·ρ·f_G is 55–61 % of the radius and 2.2–3.2× the Env4 term — and **false at r = 4 on cells 305,
  306 and 307**, where A0·ρ·f_G is still the larger of the two (2.535 vs 1.546; 2.308 vs 1.650; 1.891 vs 1.774). The
  Env4 term overtakes it only at cells 308 and 309, r = 4. The disposition's stronger wording — "the (P3) remainder
  A0·ρ²·Env4/2 is the **dominant** term of the radius at r = 3, 4" — is false at r = 3 everywhere and at r = 4 on
  three of the five cells.
* "a route that only removes f_G … cannot recover more than **about two thirds** of the radius" understates it. Summing
  *all* f_G-bearing terms (A0·ρ·f_G + 2A1·ρ²·f_G/2) over r and dividing by Σ_r rad_r gives **78.7 / 77.1 / 75.0 / 73.2
  / 71.6 %** on cells 305…309. Setting f_G to its `eps_src[3]` floor drops the magnitude to 1.22–1.35, i.e. below
  *every* M_needed — so removing f_G alone would close all five cells.

This matters because §4's conclusion is what orders C1 ahead of C2 in the continuation plan. That ordering is still
right, but for the reason §3 already gives and not for the reason §4 gives: a *real* Ĝ does not remove f_G for free —
it pays s_G through Env4 and \|Ĝ(a)\| through the centre motion, which is precisely why `T2_EVIDENCE` closes 0/5 and
why the critical ratio at cell 309 is 10.55. I recommend replacing §4's paragraph with the term table above plus that
sentence; the argument gets stronger, not weaker.

**M2 (must repair). `EXECUTION_DECISION.md` §5: the registry's gain at e = 0 is 500.4 against 1233, a 2.46×
reduction, not "469.8 … a 2.6× reduction."**
`p5y_k5_perron_deflated_resolvent/evidence/registry_r1/REGISTRY.json` block 0 covers e ∈ [0, 5083/10⁷] and carries
`Abar = 281705050073289555/562949953421312 = 500.40869…`; feeding it and the block's `tau`, `C_T`, `D_lo`, `D1`, `D2`
to the frozen `deflated_consume.atom_constants_r2` gives A0 = 500.40869, A1 = 9146.27, A2 = 466617.4, against
`cells.json` cell 0 `C_upper = 1232.8359`. The ratio is 1232.836/500.409 = **2.4637**. (469.8 is roughly the `Abar` of
blocks 84–85, i.e. e ≈ 0.04, not e = 0.) The error is 6 % and in the direction that flatters C1, which is the option
the document recommends — so it should be corrected even though it changes no verdict. Everything else in that
paragraph (item 54) is right, and the paragraph's honest conclusion "3/5 securely, 4–5/5 only if the taboo constants
are also favourable" survives: with the correct 2.46× historical precedent the argument is if anything slightly
stronger, since 2.46 clears cell 308's 2.206× as well.

**M3 (must repair, minor). "σ₄ ≈ 355 at cell 309" mixes two cells.**
The pure-tower σ₄(r = 4) is 355.35 / 352.81 / 350.28 / 347.72 / **345.10** on cells 305…309. `THEOREM_TCT.md` §3
writes "reduces … σ₄ from ≈ 355 to ≈ 235 at r = 4" inside a paragraph whose other numbers (σ₃ 5.9/16.9/36.5/67.2 →
3.04/3.41/3.81/2.25, magnitude 4.2617 → 3.9643) are all cell 309's, and
`CAMPAIGN_A_OPEN_NOTES_DISPOSITION.md` N3 says "σ4 up to 355 from the pure tower at cell 309" outright. The honest
cell-309 pair is **345 → 235**; 355 is cell 305. The refined value ≈235 is right (232.75–235.12 across the five
cells), and so is 4.2617 — I reproduced it by replacing the cell tower with the pure tower, which is exactly round 1's
"maximal repair" and matches its 4.2617 / 4.2936 / 4.3166 / 4.4159 / 4.5146 series.

**M4 (must repair, minor). `THEOREM_TCT.md` §2 attaches `critical_sup_G_over_sup_H_ratio` to the wrong statement.**
§2 says "the trade reverses unless the order-3 candidate's certified supremum is below ≈ 10.5–64.7 × s_H", i.e. it
reads the number as the break-even between the Ĝ := 0 and the real-Ĝ enclosure. It is not. Under the very evidence
model the generator uses (\|Ĝ(a)\| = ag_max·s_G, δ_G = dg_max), my own bisection gives:

| cell | 305 | 306 | 307 | 308 | 309 |
|---|---|---|---|---|---|
| ratio at which the real-Ĝ **magnitude** equals TCT0's (the actual "trade reverses") | 53.53 | 52.42 | 49.13 | 46.21 | 44.55 |
| ratio at which the real-Ĝ route still **closes** the cell (the published number) | 64.72 | 47.99 | 32.03 | 19.20 | 10.55 |

The two coincide only by accident near cell 305. At cell 309, a real candidate with s_G = 20·s_H gives a *smaller*
enclosure than TCT0 and still fails to close; at cell 305, s_G = 60·s_H gives a *larger* enclosure than TCT0 and still
closes, because TCT0 closes there with margin. `EXECUTION_DECISION.md` §3 and `FORECAST_R2.md` both describe the
quantity correctly ("at which T2 still closes each cell"); only the theorem's §2 sentence mislabels it. The number
itself is right — I reproduce all five digits by independent bisection (item 25).

**M5 (informational). Two of the ten (P3′) adopted inputs per cell are inert, in the safe direction.**
`h:1:3` never binds (`pure[1,3] = sup_S0[2] = 0.5462 < adoptedh(1) = 0.6787`), and the r = 0 source refinement never
binds either, because `sup_S0[3]` and `Sclosed:0:3` are the *same closed-form quantity computed twice* and agree to
8.7·10⁻¹⁷, with `sup_S0[3]` fractionally smaller, so `min` always selects it. Round 1's N7 ("(P3′) is not applied at
r = 0") is therefore answered structurally rather than numerically: it *is* applied now, and it changes nothing. Both
facts are worth one line in `THEOREM_TCT.md` §3 so a reader does not over-weight the adopted evidence: at the tail the
live half of (P3′) is `S:r:3` for r = 1…4 and `h:j:3` for j = 2, 3, 4.

**M6 (informational, for reproducibility). `cells.json` indices are not unique.**
The frozen cover holds 642 entries, 326 CUSUM and 316 SR, and **`index` collides across detectors**: entry `index =
305` exists for both, with completely different `e0`, `rho`, `left`, `right` and `C_upper` (SR cell 305 is e ≈ 3.965,
ρ = 0.1033, C_upper = 3033). Any reproducer that keys on `index` alone silently loads the SR cell and gets a Γ that is
wrong by ≈ 0.41 while every other quantity still matches — a failure mode that looks like a subtle arithmetic bug. The
namespace itself is safe (`A.read_records` filters on `A.DETECTOR` and asserts the CUSUM universe is exactly
`range(310)`), but `MEASUREMENT_NOTE.md` or `THEOREM_TCT.md` §4 should say "filter `detector == "CUSUM"`" in one
clause, since the extract now invites third-party reproduction.

**M7 (cosmetic).** The order-4 clamp in `h_towers` (`if cell[(j,4)] > pure[(j,4)]: cell[(j,4)] = pure[(j,4)]`) can
never fire: `t_cell ≤ pure` componentwise, and the recursion is monotone in its inputs, so the re-derived value is
automatically ≤ `pure[j,4]`. I measured 0 firings over all 5 cells × j = 2, 3, 4. It is harmless and defensive, but
`THEOREM_TCT.md` §3's "and clamped to the pure tower" presents it as load-bearing when it is not — the soundness comes
entirely from the mean-value correction and the pointwise Leibniz recursion (items 1, 4).

**M8 (informational, in the work's favour but worth stating).** The refutation of T2 has exactly one hinge:
\|Ĝ(a)\| > 0. I probed it directly. With measured suprema, s_G = 10, δ_G = 10⁻³ and \|Ĝ(a)\| = 0 the route closes
**5/5** NOMINAL ⇒ **USEFUL**; with \|Ĝ(a)\| = 0.681·s_G it closes 4/5; with \|Ĝ(a)\| = s_G it closes 3/5. The record's
"no reading reaches USEFUL" is therefore true for every reading in which the order-3 candidate does not vanish exactly
at the atom — which is justified twice over (the frozen comparison's own "\|Ĝ(a)\| ≤ sup of the G candidate", and the
adopted 0.680–0.681 ratio on all 170 objects, both quoted in §2). §3 should say so in one clause rather than leaving a
reader to discover that the whole refutation turns on one input.

**M9 (informational). "Self-contained" is true of the mathematics, not of the tool.**
I re-derived every published number from committed files alone, so round 1's N2 is discharged in substance. But
`tail_forecast_r2.main` reads `aux`, `C_upper` and the per-m intervals from `st["records"]` — the live sealed records —
and uses `ADOPTED_TAIL_INPUTS.json` only as a field-by-field checker; `critical_ratio` and `atom_constant_requirement`
likewise read `st["records"][k]["m"][m]`. So the generator still cannot be re-executed off-host. That is a reasonable
design (the checker direction is the safe one), but `MEASUREMENT_NOTE.md`'s "with it the namespace can be re-derived
from its own committed evidence" should say *re-derived*, not *re-run*.

**M10 (cosmetic).** `review/REVIEW_R1.md` and the repairs it forced arrive in the same commit `46655b31`. The r1 text
is byte-unchanged between `46655b31` and HEAD, and its verdict and counts match what `README.md` reports
(43/6/3/4), so nothing is wrong — but a reviewer's output landing in the same commit as the author's response to it
is the sequencing pattern Campaign A's own `SEQUENCING_DEFECT_NOTE.md` is about, and this review's own file should be
committed on its own.

**M11 (not checked).** I did not re-execute `code/b0_state_verify.py`. I re-derived its G2/G5/G6 claims by hand
(coverage map r4 sha `a3bddd83…`, gates sha `392101dd…`, the two-namespace diff since `7cb01e38`, 0 merges since the
frontier, no r5) and they agree. Its only change since `ae153a69` is the recorded HEAD.

## Round 1's four FAILs

Explicitly, one line each:

* **N1 (round-1 item 14) — REPAIRED.**
* **N4 (round-1 item 34) — REPAIRED.**
* **N14 (round-1 item 55) — REPAIRED.**
* **N15 (round-1 item 56) — REPAIRED.**

None is PARTIALLY_REPAIRED and none is NOT_REPAIRED. The evidence for each:

| round-1 FAIL | disposition | evidence |
|---|---|---|
| **N1** — (P3′)'s order-4 re-seeding fed a midpoint bound into a whole-cell recursion | **REPAIRED** | The two-tower construction is sound as written and as implemented. I verified the four things that could break it: the mean-value step is a correct Banach-space estimate with ρ the true half-width (items 1, 2); `pure[j,4]` is cell-uniform, re-derived by me from (P3) (item 3); the order-4 recursion from corrected lower orders is valid because Leibniz holds pointwise in e (item 4); and there is neither circularity nor an ordering bug (items 5, 6). σ₃ (midpoint tower) reaches only premise (P2) at e₀ and σ₄ (cell tower) reaches only Env4 — I traced every consumer (items 8, 9). The repaired magnitudes 4.2572/4.1517/4.0401/4.0051/3.9643 and Γ = −0.043752 reproduce **exactly** from my own implementation; they sit, as they must, between round 1's unsound 4.2031 and its conservative repair 4.2456, and below its maximal repair 4.5146 — which I also reproduced (4.2617 at cell 309) |
| **N4** — T2 was scored on a weaker premise supply than TCT0 | **REPAIRED** | all four routes now call `tct_rule.tail_enclosure` with the same `aux`; `tc_rule.cell_enclosure` survives only for the sealed Campaign-A cells 11–44 (item 31). The refinement is legitimate for a route with s_G ≠ 0 because σ₄ is a statement about the true source alone and enters Env4 purely additively (items 29, 30). The effect is exactly what N4 predicted for the measured route: T2_AUDIT_MEAS NOMINAL 3/5 → **4/5**. T2_AUDIT NOMINAL stays 3/5 because the r2 σ₄ is *larger* than the r1 σ₄ that N4's table was computed against. I reproduced all 40 per-cell flags independently (item 35), and N3's CONSERVATIVE point is also repaired (s_F, s_D, s_H now scaled; 1/5 → 0/5, the direction that does **not** flatter the refuted route) |
| **N14** — three published data tables were wrong | **REPAIRED** | every corrected entry recomputed from the 25 committed objects and confirmed: sup.F 0.1843–1.0789, sup.D 0.2981–0.6952, sup.H 0.5723–1.3345, H_at_a −0.8171…+0.0897 with 4 of 25 positive, sup.H/sup.D 1.1127–4.4643 vs the front's 2.006–4.326 (correctly described as overlapping), sup.D/sup.F 0.5318–1.8047 vs 16.92–144.40, and the per-cell `norms.k` row now given as a range rather than cell 305's values. The front column, `sup_S0`, `C_upper` and the CPU accounting also check out (items 48, 49) |
| **N15** — the "two independent rule paths" shared the (P3′) functions | **REPAIRED** | `tail_enclosure_crosscheck` now re-derives the pure tower, both order-3 slots, the order-4 recursion, both σ's, the Taylor sums, the (P3) envelope and the assembly table in-line, calls none of `pure_tower`/`h_towers`/`sigmas`/`sigma_source`/`tail_object`/`R.*`, and mentions `tc_rule` only in its docstring (item 63). It would now catch an N1-class defect. The strongest evidence is item 64: the two namespace paths and **my own third implementation, written from the theorem before any code was read, agree on all 20 (cell, m) pairs as exact rationals**. The one residue is that both namespace paths still receive the same `A` dict from `atom_constants_generic` — Lemma G is three lines and I re-derived it independently, so this is immaterial |

## What I did not check

* Anything on a remote host. The 262-field producer identity gate, the ≈ 6 740 CPU-s replay, the sealed K1 records and
  `auxiliary_evidence` as stored, and a real run of `tail_forecast_r2.py` (which needs `--records` plus the pinned
  adapter/loader/Perron/T-EXT chain and the sealed Campaign-A cells) are all off-host.
* Whether `ADOPTED_TAIL_INPUTS.json`'s field *values* are the sealed records' values (item 41). The hash chain is
  locally verifiable only as far as the manifest; the field copy is verified by `tail_forecast_r2.main` where the
  records live. I corroborated `C_upper`, `e0`, `rho` against the frozen cover and everything else against the
  published arithmetic.
* Whether C_upper is genuinely cell-uniform and whether k_i, j_i genuinely bound ‖K_i(e)‖, ‖J_i(e)‖ on the cell —
  inherited frozen-K1 premises (item 15), as in round 1.
* The frozen K5-B predicate itself. I used only its direct test, which reproduces all 40 recorded `pass` flags
  (item 36); round 1 ran `k5b_check.py` and it self-verified.
* `code/b0_state_verify.py` was not re-executed (M11); `code/tct_inputs.py` and `code/tail_blocker_map.py` were read
  but not run.
* Round 1's own adjudication of Campaign A (27 PASS / 7 INFO / 3 NOT_CHECKABLE / 0 FAIL) and the composition of the
  four adopted state channels were taken as given; I re-derived only the Campaign-A order-3 ratios the scoring uses
  (170 objects: sup.G/sup.H 34.7857–80.5004, \|Ĝ(a)\|/sup.G 0.67986–0.68110, δ_mid(G_r) 2.763–7.860·10⁻³).
* python-flint / numpy / scipy are absent locally, so no Arb-precision quantity was recomputed. Everything above is
  exact `fractions.Fraction`, which is *stronger* than round 1's float reproduction, not weaker.
* The T1 comparison numbers in §5 ("δ_cell = 0.05–0.09 per object", "radius ≈ 45 per r") — these describe a route that
  was never implemented here and I had no committed δ_cell to check them against.

## Counts

| verdict | count |
|---|---|
| PASS | 60 |
| INFO | 5 |
| NOT_CHECKABLE_LOCALLY | 2 |
| FAIL | 4 |
| **total checks** | **71** |

Each row carries exactly one verdict and the four columns sum to 71.
INFO items: 16, 37, 45, 70, 71. NOT_CHECKABLE_LOCALLY items: 15, 41.
FAIL items: 52 (M1), 55 (M2), 57 (M3), 59 (M4).
Rows 7, 11 and 62 are PASS and carry an additional informational remark in their evidence cell; they are counted once,
as PASS.

Coverage against the brief: task A = rows 1–16, task B = rows 17–28, task C = rows 29–37, task D = rows 38–45,
task E = rows 46–62, task F = rows 63–71.

All four FAILs are prose. None of them touches the theorem, the implementation, any published enclosure, any margin,
the route classification or the stop verdict; all four are numbers or characterisations in narrative paragraphs, and
three of the four (M1, M2, M3) are in text that round 1 did not have to look at because it was rewritten by the
repairs.

**FINAL VERDICT: PASS_WITH_NOTES.** The N1 repair is mathematically sound, and I could not construct a reading of
premise (P3′) r2 that is not a valid whole-cell bound. Every repaired headline number — the five magnitudes, the five
Γ, the five margins, the four route classes, the twenty exact-rational enclosure strings, the per-r σ₃/σ₄/Env4/f_G/rad
detail, both atom-constant series, all five critical ratios and the derived identity gate — reproduces **exactly** from
an implementation written from the theorem before any of this namespace's code was read, driven only by committed
files. The stop decision follows mechanically from an unmodified gate file, cell 305's closure survives every
perturbation and even the complete withdrawal of the h-refinement from σ₄, and no route or defensible reading reaches
USEFUL. Notes M1–M4 must be repaired before this is published as the campaign record; M5–M10 are improvements to the
record's accuracy that cost nothing.
