# REVIEW_STREAM_D_R1 — independent adversarial review of Stream D (cell 309 routes)

**Reviewer:** independent fresh-context reviewer (wrote none of Stream D). **Date:** 2026-09-28.
**Scope:** `streams/D_309/{SCOPED_NEGATIVE_FAMILIES_309,SUPNORM_THEOREM,COVER_REFINEMENT_309,RESIDUAL_SPECIFIC_309,D_309_ROUTE_SUMMARY,PROGRESS}.md`, `streams/D_309/code/*.py`, `validation/D309_*.json`.
**Quarantine:** reviewer ran only Stream D functions and own stdlib scripts, at declared drifts {0, 1/4, 1/2, 1, 3} and synthetic FSM fixtures, with `ov_quarantine.LEDGER` redirected to the reviewer scratch dir. No main() of Stream D was run (they write into NS). No cell 305–309 quantity, no drift in [1.2, 2.6] or mirror, no git write, no remote host.

## 0. Verdict

ROUTE_REVIEW: ACCEPTED_WITH_CONDITIONS

* **Mathematics sound.** SC-3, SC-4w, TC⁺, SC-T, SC-S1, CR-1, the leading-order `1 − 1/N^j` statement, RSO-0,
  RSO-PM, RSO-LR (order 1) and RSO-P were re-derived by the reviewer. No error was found that breaks validity.
* **SC is genuinely stronger than the surrogate, not a relabelling.** It needs candidate functions, not scalars.
  It is C5 route A3 made precise, with the same DATA blocker.
* **Certificates sound.** Both certificates (naive and centred Taylor form) are sound by reading. In the reviewer's
  per-box attack (1280 exact point values, 0 violations) they contained every value. The Hermite closed form agrees
  with the reviewer's own independent quadrature in 2400/2400 cases (i = 0..5).
* **Evidence defects (B1–B3):**
  * several "negative controls" are arithmetic tautologies;
  * the B2 − TPT = 0 validation holds by construction;
  * route B2's REFUTED label is broader than CR-2 proves.
* **Repairs are local.** Conditions §6 repair labels, controls and guards only.
* **Quarantine clean.** Governance labels (closure-only; data-blocked by payloads + U1/U2; CR NEW_REAL) are correct.
  **No route is or could honestly be FREEZE_READY.**


## 1. Route SC — composite-sup premise supply (`SUPNORM_THEOREM.md`)

### 1.1 Mathematics (G2) — re-derived by the reviewer

* **SC-T identity (SUPNORM:100-109).** Differentiating `(I−K_e)F = S` three times gives
  `(I−K)F''' = S''' + 3K1F'' + 3K2F' + K3F`; with `Ĝ = 0`, `F̃''' = 0`, so
  `φ'''(e0) = S''' + 3K1Ĥ + 3K2D̂ + K3F̂ = (I−K)F''' + 3K1E_H + 3K2E_D + K3E_F`. **Correct.**
* **SC-3 (a)/(b), SC-4w.** Triangle inequality on a valid decomposition; min of valid premises is valid. **Correct.**
* **TC⁺ (SUPNORM:51-76).** Reviewer recomputed the remainder integrals: `∫_0^s (s−v)(f4+vE5)dv = f4 s²/2 + E5 s³/6`,
  `∫(s−v)²/2(·) = f4 s³/6 + E5 s⁴/24`, `∫(s−v)³/6(·) = f4 s⁴/24 + E5 s⁵/120`. `Env5` with `Ĝ = 0`:
  `C(5,3)K3Ĥ + C(5,4)K4(D̂+tĤ) + K5(F̂+tD̂+t²Ĥ/2)` → `10k3 s_H + 5k4(s_D+ρs_H) + k5(…)`. **Correct.**
  N1: SUPNORM:55 writes `s = |t − e0|` although `t = e − e0` was defined at :21 (should be `|e − e0|` or `|t|`).
* **Genuinely stronger, not a relabelling.** The ladder S0 ≥ S1 ≥ S2 ≥ S3 (SUPNORM:87-91) removes cell-uniformity,
  submultiplicativity and the cross-term triangle; S3 needs the candidate *functions*, not the scalars `s_X`, so it is
  not expressible from TC-T's inputs. It is C5 route A3 made precise, which Stream D itself discloses
  (SCOPED_NEGATIVE_FAMILIES_309.md:133; C5_ROUTE_SEARCH.md:45 "A3 … KILLED … DATA"). Novelty = rigour + certificate,
  not a new idea; the DATA blocker of A3 is unchanged. Accepted.
* **SC-S1 (SUPNORM:144-160).** Proof checked: windows `[m−C, C−p]` are nested in the atom's `[−C, C]`, so the true
  norm is the atom window integral; off-atom the window loses positive measure; at the atom equality needs the
  continuous `X̂∘n(a,·)` to equal `±‖X̂‖·sign He_i` a.e. across a simple root — impossible. **Correct** for
  continuous nonzero candidates. Notes:
  * N2: the root condition `|e| < C − √3` is stated for i ≤ 3; TC⁺/SC-4w also use i = 4, 5 (harmless: every He_i,
    i ≥ 1, has a root in [−1, 1], so `|e| < C − 1` suffices; state it).
  * **N3 (claim wording):** SC-S1 is strictness of the **exact** sup. The certified B3 carries overhead (TF 1.19–1.44×
    over a grid lower bound, `validation/D309_HERMITE_TF_NONTARGET.json` runs), so "strict" does not imply a
    certified gain. `D_309_ROUTE_SUMMARY.md:67` ("The gain is strict …") and the commit subject of 6d0f0615
    ("strictly positive") must say "strict for exact sups; certified gain not guaranteed".
* **N4 (FSM SC-4w/TC⁺ ratios are idealized).** `E3` / `Env5_comp` in the FSM run are sups of `phi_poly`, which
  contains the **exact** source `S(e)` (`d309_core.py:254-266`, used at `d309_supnorm_fsm.py:81-88`). Real SC-4w
  cannot see `S⁗(e)` as a function (only σ4 or a source candidate); the SUPNORM §7 ratios `E3/E0`, SC3_E3, SC4_E3,
  SC4_TCplus therefore include a source cancellation that real use cannot certify. Validity unaffected; label them.

### 1.2 Certificate (Lemma HC, Hermite closed form, centred Taylor form) — soundness attack

Reading (`d309_hermite.py:93-142, 245-279`; `d309_hermite_tf.py:32-96`): moment recursion
`M_j = (j−1)M_{j−2} + A^{j−1}φ(A) − B^{j−1}φ(B)` correct; `φ^{(i)}(u) = (−1)^i He_i(u)φ(u)` correct; image boxes of
`n(x,z)` monotone and correct (`tf:86-87`); weight × image-range × exact panel mass is a valid enclosure because
`φ ≥ 0`; partial-window panels hulled with 0 (`tf:93-94`) is valid; the box cover keeps a superset of R
(`c11_certifier.py:189-210`). **No unsoundness found by reading.**

Reviewer runs (own scripts in SCR/review_D, ledger redirected; drifts {1/4, 3}; declared in each script docstring):

| run | what | result |
|---|---|---|
| `rev_tf_attack.py` | every box of `C11.cover(2)` × 8 points, 3 function sets (w_bump; three random dense degree-7 polys, one per order; high-cancellation `(p−m)^6/4^6+(p+m−4)^5/4^5`), exact point value (Ki_apply) ⊂ box enclosure | TF 0/480 violations, naive 0/480 |
| `rev_tf_attack2.py` | depth-5 boxes (24 seeded + atom boxes), panel 1/16, planted defects through the same code path | see §1.3 table (filled from `rev_tf_attack2.json`) |
| `rev_quad.py` | Ki_apply vs reviewer's **own** float Gauss–Legendre quadrature (no Stream-D or C11 code), i = 0..5, 20 states × 4 functions × 5 declared drifts | see §1.3 |

### 1.3 Reviewer run results (SC certificate and closed form)

| run | cases | result | negative controls through the same code path |
|---|---|---|---|
| `rev_quad.py` (Ki_apply vs own Gauss–Legendre quadrature, i = 0..5, 5 declared drifts, 20 states, 4 functions) | 2400 | **2400/2400 agree**, max abs diff 9.1·10⁻¹³ | sign `(−1)^i` dropped: 1185/1185 detected; clipping/kinks removed: 783/783 detected |
| `rev_tf_attack.py` (cover(2), 16 boxes × 8 points × 3 sets × 2 drifts) | 480 | TF 0 violations, naive 0 | (too coarse: planted defects hidden, see next row) |
| `rev_tf_attack2.py` (depth 5, 25 boxes × 8 points × 2 sets × 2 drifts, panel 1/16) | 800 | **TF 0 violations, naive 0** | remainder zeroed: 632/800; Hermite sign dropped: 716/800; remainder halved: 0/800; window hull dropped: 0/800 |

Reading: Lemma HC is independently confirmed (including i = 4, 5, which Stream D did not test); both certificates
contained every exact point value. Point containment detects only gross defects (zeroed remainder, wrong sign): a
halved Taylor remainder or a dropped window hull stays hidden behind the `O(panel)` z–n decoupling overestimate. So
certificate soundness rests on the reading proof in §1.2, with the runs as a sanity layer — not on any Stream-D test.

### 1.4 SC test adequacy (S2) — findings

* **B1 (tautological negative controls claimed as evidence).** The "planted-too-small" certificate controls never
  touch the certificate:
  * `d309_hermite.py:350,357`: `planted = glo * 99/100` … `"nc_planted_upper_detected": bool(not (planted >= glo))`;
  * `d309_hermite_tf.py:130`: `"nc_planted_detected": bool(not (glo * F(99, 100) >= glo))`.

  Both are `True` for every `glo > 0` by arithmetic; they cannot fail. SUPNORM:294 ("the planted-too-small control
  is detected 6/6") and PROGRESS:12-13 present them as detections. The same pattern recurs in SC-FSM NC2
  (`d309_supnorm_fsm.py:103-104`: `rads = [max(devs)/2]` — a violation at the max-dev point is guaranteed) and NC1
  (`:67-68`, a hand-written alternative formula, detected whenever `K2D̂ ≠ 0`; it tests the identity comparator,
  not a premise supply). SUPNORM:268-269 "NC1 … detected 60/60; NC2 … detected 60/60" overstates them.
  **Repair:** relabel as harness/arithmetic checks, and add controls that feed a planted-invalid object through
  the real path (e.g. a planted-invalid premise supply through `tc_rad_poly` + `enclosure_check`; a planted defect
  in `box_upper_tf` checked by point containment — both done by the reviewer, §1.3).
* **N5 (weak soundness criterion).** The TF/H3 "soundness" check is `certified_upper ≥ max over a 121-point
  half-integer grid` (`tf:111-114,126`; `hermite:344-347`) — a necessary condition only. Per-box containment (the
  reviewer's §1.2 runs) is the adequate test.
* **N6 (H1 pass threshold loose for w_bump).** H1 tolerance reaches 9.6·10⁻⁴ absolute (`trunc_bound`, w_bump) against
  values ≤ 0.48; the observed gaps (≤ 5.8·10⁻⁸) are what carry the evidence, not the pass count.
* **N7 (shared primitive in the "independent" H1).** `d309_hermite.py:81-85` monkey-patches `c7_gaussian.Phi/phi/
  sqrt_two_pi` in-process, and `c11_certifier` uses the same module object, so the H1 comparator shares the patched
  Gaussian primitives. The `_memo_selftest` checks two arguments only. The reviewer's `rev_quad.py` (float
  quadrature, `math.exp`) closes this gap independently (§1.3).
* **N8 (Q5 defence in depth).** The certificate entry points `box_upper_tf(triple, box, e, panel)`
  (`d309_hermite_tf.py:64`) and `box_upper_composite` (`d309_hermite.py:245`) take a drift but do not call
  `Q.guard_drift`; only the drivers do (`tf:107`, `hermite:283`). The header claim "guard_drift at every entry
  point" (`tf:2`) is not true of the function a future real stage would call. Add the guard.

## 2. Route CR — cover refinement, and B2 (`COVER_REFINEMENT_309.md`)

### 2.1 Mathematics

* **CR-1 (COVER:42-56).** With `rad(s) = A0p2 + 2A1p1 + A2p0` and TC's `p_j`, the reviewer re-derived
  `r0 = A0f_H+2A1f_D+A2f_F`, `r1 = A0f_G+2A1f_H+A2f_D`, `r2 = A0Env4/2+A1f_G+A2f_H/2`, `r3 = A1Env4/3+A2f_G/6`,
  `r4 = A2Env4/24`, and `Γ_F − g_hi = ρ(e0+ρ)(|c_lo| + Σ r_jρ^j)` with the stated per-power coefficients. **Correct.**
* **"1 − 1/N^j" (COVER:112-118, table :81).** The order-j slack of a TPT record over half-width h is
  `≈ e_c r_{j−1} h^j / j`; with `h = ρ/N` and `e_J = e0 + O(ρ)` the retained fraction is `N^{−j}(1 + O(ρ/e0))`, so
  `1 − N^{−j}` is removed, and the frozen-relative charges `1/N, 1/(2N²), 1/(3N³)` follow. **Correct as a
  leading-order statement with premises held fixed**, which the text says; the FSM shows the premise change matters
  (prediction error up to +37 %, COVER:144-150). The `e_J/e0` factor is not shown; add it.
* N9: CR-3 (COVER:104) is a definitional identity; its bookkeeping is inconsistent with §2 — `S_TPT` there already
  contains `w_g` (COVER:65), yet CR-3 adds `[w_g(e0) − w_g(e_J)]` separately. Define `S_X` without `w_g` or drop the term.
* **CR-2 (COVER:87-91) is correct only for its stated input set, and its proof cites a withdrawn word.**
  * N10: the proof says `g_hi + P*` "is attained by an admissible witness"; TPT-O was corrected to a **supremum**
    (THEOREM_TPT.md:75-80, per REVIEW_TPT_R1 N1). The conclusion survives (any valid bound ≥ the sup); fix the wording.
  * **B2 (blocker for the route-B2 REFUTED label as worded).** COVER:95 "a record-free split can never gain anything"
    and D_309_ROUTE_SUMMARY:27 (B2 **REFUTED**) overreach. CR-2 covers only bounds built from the *fixed* triple
    `(g_hi, L, U)`. A split without new K1 records can still change the third input: re-certifying the operator
    constants (`k_i`, `A`, the Env4 k-terms) on shorter drift segments gives an `s`-dependent profile that is
    pointwise ≤ the cell-uniform one (Lemma TC-P needs constants only on `[e0, t]` and at `t`). That lever is not
    dominated by fixed-profile TPT and is neither NEW_REAL nor a new record. C5 killed B2 as **NEW_REAL**, not MATH
    (C5_ROUTE_SEARCH.md:50); upgrading it to REFUTED on Stream D's own formalization is the S4 pattern
    ("do not refute your own redefinition"). **Repair:** state "B2 is REFUTED within the fixed-(g_hi, L, U) family";
    record sub-segment constant re-certification as a separate, unevaluated lever.
* **B3 (validation by construction, S2/S7).** "B2 − TPT = 0 exactly in 30/30" (COVER:97, :267; summary :102) is not
  evidence for CR-2. `d309_cover.py:287-290` *implements* B2 as the parent record's own TPT integrals over
  sub-lengths from the same `e0`; the rightmost/leftmost subcells reproduce `I_R(ρ)`, `I_L(ρ)` exactly, so the max
  equals parent TPT whenever the integrands are nonnegative. The check verifies an implementation identity and
  cannot test the ∀-split claim, which rests on TPT-O alone. Relabel it (e.g. "consistency check of the B2
  transcription"), keep CR-2 as proved-by-TPT-O.

### 2.2 Policies — are they result-free?

* **DRP-0 (COVER:181-185)** is a priori and uses no Γ — result-free **provided** `ρ_k* = s_1/s_2` is computable from
  certified inputs. N11: `s_1` includes a "centre error" (COVER:69, :113) — the centre's deviation from the true
  `R''(e0)`, which is not an input. Define `s_1` with its certified bound (`W + r0` half-widths) instead.
* **DRP-1 (COVER:216-231) is result-adaptive, not result-free:** it splits on `Γ ≥ 0`, i.e. on the target outcome.
  The section discloses this (:230-231), but the commit subject of 6d0f0615 ("result-free policies DRP-0/1") and the
  PROGRESS/summary phrasing do not. Rigour is unaffected (every leaf bound is certified, so adaptivity cannot create
  a false PASS), but under S1 a branch-and-bound toward `Γ < 0` on a target cell is admissible only as a frozen,
  budget-capped stage authorized in advance. N12: fix the wording everywhere to "DRP-0 result-free; DRP-1
  outcome-adaptive, frozen-predicate".
* Cost bound `records ≤ 2^{D+1} − 2` (COVER:228) is correct for a full binary tree without the root.

### 2.3 CR test adequacy

* N13: `NC_half_transport` (`d309_cover.py:238-239`) is arithmetic (`g_hi + (gmax−g_hi)/2 < gmax` whenever
  `gmax > g_hi`) and cannot fail; `NC_g_hi_planted` (`:226-228`) shifts an interval off the truth by construction
  (harness check of `midpoint_check`, acceptable as such). The only code-path control, the flat profile, is caught in
  3/10 (disclosed, COVER:275-278). C2 soundness (`clause ≥ grid max of exact g`) is truth-relative and can fail — the
  real evidence. Label the two harness checks as such.
* The C5 "ρ halved" oracle diagnosis is confirmed: `p5y_k5_tail_c5_exhaustion/code/c5_common.py:85-86` scales
  `m2["rho"]` only.

## 3. Route RSO — residual-specific order-0 and derivative extensions (`RESIDUAL_SPECIFIC_309.md`)

### 3.1 Mathematics

* **RSO-0 (RSO:45-61).** Positivity + supersolution iteration; step 2 gives `v ≥ R_eψ` **pointwise on X**, not only
  at `a` — which RSO-PM needs. **Correct.**
* **RSO-PM (RSO:106-119).** `∂R = RK₁R`, `∂²R = 2RK₁RK₁R + RK₂R`; `R|f| ≤ Rψ ≤ v0` pointwise, then
  `R(|K₁|v0) ≤ v1` and `R(2|K₁|v1 + |K₂|v0) ≤ v2` by RSO-0. **Correct.** The implementation uses the entrywise
  cell-sup `|K_i|` (`d309_rso.py:62-64`), a valid stronger choice.
* **RSO-LR (RSO:126-153).** Score identities correct for the Gaussian location family (`∂_eS = −1` ⇒ `M_n² − n`).
  Certificate reduction re-derived: with `V = α + βμ²`, the RHS is `ψ|μ| + Kα + μ²Kβ + 2μK^Sβ + K^{S²}β`; the two AM–GM
  inequalities give exactly the two linear inequalities at RSO:146. `K^S = K₁` and `K^{S²} = K₂ + K`
  (`He₂ = u² − 1`). **Correct.** Implementation solves them with equality at one drift (`d309_rso.py:365-368`,
  exact `R`), nonnegativity automatic — consistent with "single drift" (G3).
* **RSO-P (RSO:158-175).** Pointwise-in-x Taylor profiles with integral remainders, then linearity of `R` and RSO-0/PM.
  **Correct.**
* **Collapse statement (RSO:81-86).** For `ψ ≡ c`, any admissible `v` is `c·W` with `W ≥ 1 + K_eW` on C, so
  `v(a) ≥ c·sup_C E_a[τ] = cΛ`: a uniform order-0 atom constant, i.e. an F1 supply. **Correct.** But:
  * **N14 (the "iff" is misstated).** RSO:86 and the G10 row (RSO:323) say "non-cosmetic iff ψ is non-constant on
    the support of μ". By RSO:78 the shape factor exceeds 1 iff `ψ < ‖ψ‖` on a μ-positive set — which also holds for
    ψ **constant on supp μ but larger off it**. Restate as "iff ψ ≠ ‖ψ‖ μ-a.e.".
  * N15: Corollary RSO-G (RSO:71-76) uses `μ(ψ)` without an e; the bound needs `sup_{e∈C} μ_{a,e}(ψ)`.
  * The derivative collapse (RSO:121) is correct in the sense stated: constant ψ yields a triple with a uniform
    `A0`, hence an F1 member regardless of `A1, A2`.
* **Original definition respected (S4).** RSO-C4 is kept exactly as C4 §7.1 / ROUTE_AUDIT_R1:418-431 defined it; the
  extensions are labelled as extensions. Good practice.

### 3.2 RSO tests

* Truth-relative checks that can fail (and did not): `N0 ≥ max_e (R_e a)(a)`, `N1/N2 ≥` PM and **signed** truths on a
  17-point drift grid (`d309_rso.py:130-154, 208-210`); TC assembly vs exact `F''(t)(a)` (`:289-296`) — the
  worst dev/rad reaches 0.98 for RSO-P-box1 (`D309_RSO_FSM.json` R4), so that check has real power; certificates
  verified twice (Taylor bisection and grid+Lipschitz, `:75-92`) — both rigorous as coded.
* **B1 (continued).** NC (a) (`d309_rso.py:201-204`: halves one entry of a copy of ψ and checks `psi_bad ≥ a`) and
  NC (c) (`:428`: `not (lower*9/10 ≥ lower)`) are arithmetic on constructed values and cannot fail. RSO:286-293
  lists them under "Negative controls (all detected)". NC (b) (`:198-199`, planted `0.9·v` through
  `check_cert_taylor`) and NC (d) (`:412`, wrong score through the kernel builder) are genuine.

## 4. Cross-cutting checks

### 4.1 Power of the FSM TC-enclosure soundness check (reviewer run `rev_fsm_power.py`)

Same 48 generic + 12 adversarial fixtures as Stream D's declared rule; planted-**invalid** premise supplies fed through
the real `tc_rad_poly` + `enclosure_check` path:

| planted invalid supply | cases where `enclosure_check` reports a violation |
|---|---|
| `f_G := 0` (order-3 premise dropped) | 30/60 |
| `Env4 := 0` | **0/60** |
| `f_G := TRUE/2`, `Env4 := (true sup)/2` (both below truth) | **1/60** |
| `A0` halved | **0/60** |

* **N16.** "0 violations in 9900 point checks" (SUPNORM:265-266) and "0 violations … 2376 checks" (RSO:247) are weak
  evidence of premise validity: the fixtures are loose (worst dev/rad ≤ 0.54 for every SC variant, from
  `D309_SUPNORM_FSM.json`), so even invalid supplies pass. The load-bearing SC evidence is the **premise-level**
  truth check `TRUE ≤ S3 ≤ S2 ≤ S1 ≤ S0`, `TRUE ≤ S4`, `E3 ≥ true sup` (`d309_supnorm_fsm.py:71`, `env_levels`),
  which is truth-relative and can fail. Say so, and report the enclosure check's power.

### 4.2 Quarantine, leakage (G8, S8), temporal integrity (G7)

* Static scan (`ov_quarantine._scan_file`, run in memory by the reviewer, no write into NS) on the 7 files of
  `streams/D_309/code`: **0 findings**; the reviewer's planted control (forbidden import, literal 309, TCT_INPUTS path)
  is detected with all three kinds.
* Ledger: 9 D_309 entries (`ledger/ZERO_TARGET_LEDGER.jsonl`), classes SYNTHETIC_VALIDATION / NONTARGET_DRIFT_VALIDATION,
  `cells_touched = []`, `new_target_evaluations = 0`, no LEAK_FLAG. Drifts used by the code: FSM e ≤ 3/8 and the CUSUM
  kernel at {0, 1/4, 1/2, 1, 3} ± 2·10⁻⁴ with `guard_drift` on the interval (`d309_hermite.py:185, 304`). No import of
  any forbidden module; only the allowed pure libraries `c7_gaussian`, `c11_certifier` (+ `c11_common`, whose git/ps
  helpers are defined but never called).
* Temporal: each code file's mtime precedes its ledger run and its JSON (e.g. `d309_rso.py` 03:49 local, last run
  18:50:53Z, JSON 03:50); all committed in 6d0f0615. `d309_rso.py` was run 3× (18:37, 18:41, 18:50Z); the declared
  rule is in the file, but whether it changed between runs cannot be established from one commit (N17: record re-run
  reasons).
* **S8.** Committed tail numbers appear only in history sections: SCOPED_NEGATIVE_FAMILIES_309.md §1 (:24-25, :51,
  :59-61, :73, :102) and COVER §9 (:283, replay CPU cost). No route factor, synthetic ratio or gain appears in those
  sections, and no route section carries a tail number (reviewer grep for the committed values 3.266, 3.586, 4.679,
  4.867, 2.2529, 2.1015, 6.716, 0.6076, 0.944, 9.793, 2.583, 1.067, 1.096, 1.37, 0.681). N18 (caution, not a
  violation): RSO:25-27 points to the C5 per-cell `A0·f_H` share (`C5_BLOCKER_DECOMPOSITION.md:49`) in the same
  document whose §6 reports the RSO-C4 synthetic radius ratio; a reader can combine the two. Drop the pointer or move
  it to a history appendix without the ratio.
* The ranking in D_309_ROUTE_SUMMARY §3 is structural (channels acted on, strictness, NEW_REAL); it states the
  wide-cell regime conditionally and uses no per-cell number. G1/G8 PASS.

### 4.3 Governance and data blockers

* **Closure-only** is correct for every row: SC and RSO change TC-T premise supplies / a consumer term, CR changes
  records and geometry; none is a Lemma G / Lemma Dv′ r2 supply.
* **Data-blocked** is correct: the K1 candidate payloads were never serialized (0/326;
  `p5y_k5_tail_c6_evidence_recovery/README.md:41-50`), the lower-front `TC_CELL_*.json` carry scalars only (reviewer
  confirms the SUPNORM §8 reading), so no real cell — target or not — can host an SC or RSO certificate; regeneration
  needs U1 (numpy/python-flint host) and the new quantity faces U2 (C6 Condition 10). CR additionally needs NEW_REAL
  addresses (guard DENY).
* **FREEZE_READY: no** for every route — agreed. None could honestly be FREEZE_READY: no payload exists on which a
  frozen stage could run, the certificate configuration (depth, panel) has no declared calibration artefact, SC-4w
  interval-drift enclosure is not implemented (SUPNORM:220-222), RSO-LR is single-drift, and every route needs U3.

## 5. Per-route gate review (reviewer's assessment vs Stream D's claims, D_309_ROUTE_SUMMARY:23-32)

| route | Stream D state | reviewer | gate changes |
|---|---|---|---|
| SC (SC-3, SC-4w, TC⁺, SC-T, SC-S1) + certificate | VALIDATED_NON_TARGET; real use BLOCKED | **agree**, with B1/N3/N4/N8/N16 repairs | G2 PASS (re-derived); G5 PASS on premise-level truth checks + reviewer's independent quadrature and containment runs; G6 now PASS for the math and the order-3 certificate (this review); G9 PASS for statements/formats only; G10 PASS for exact sups, **certified** gain unproven (N3) |
| CR (CR-1, CR-3, DRP-0/1) | VALIDATED_NON_TARGET (algebra); DRP-1 IMPLEMENTED; BLOCKED (NEW_REAL) | **agree**, with N9/N11/N12 | G2 PASS (leading-order, premises fixed); G7 PASS; "result-free" holds for DRP-0 only (after N11) |
| B2 | REFUTED (dominated by TPT) | **REFUTED only within the fixed-(g_hi, L, U) family** (review B2); validation "0 in 30/30" is by construction (B3) | G2 PASS for the scoped statement, via TPT-O (not via the test) |
| RSO-C4 | VALIDATED_NON_TARGET; narrow | **agree** | — |
| RSO-P / RSO-PM | VALIDATED_NON_TARGET; BLOCKED | **agree**, with N14/N15 and B1 (NC a) | G10 PASS iff ψ ≠ ‖ψ‖ μ-a.e. (N14 wording) |
| RSO-LR order 1 | VALIDATED_NON_TARGET (single drift) | **agree** | G3: single drift; block-uniform version absent |
| RSO-LR order 2 | THEORY_ONLY | **agree** (sketch only) | — |
| any route | FREEZE_READY: no | **agree** — none could honestly be FREEZE_READY (§4.3) | — |

## 6. Conditions for acceptance (all are labelling / control / guard repairs; none changes a theorem)

1. **B1** — relabel every arithmetic/harness "negative control" as such (`d309_hermite.py:350,357`;
   `d309_hermite_tf.py:130`; `d309_supnorm_fsm.py:67-68, 104`; `d309_rso.py:201-204, 428`; `d309_cover.py:238-239`),
   correct the "detected n/n" claims (SUPNORM:268-269, :294; RSO:286-293; PROGRESS:11-14), and add at least one
   code-path control per certificate claim (the reviewer's `rev_tf_attack2.py` planted-defect design and
   `rev_fsm_power.py` planted-invalid supplies are usable templates; report their power, §1.3 and §4.1).
2. **B2** — restate route B2 as "REFUTED within the fixed-(g_hi, L, U) family" (COVER:87-95, SCOPED:148-150,
   D_309_ROUTE_SUMMARY:27, :102) and record sub-segment operator-constant re-certification as a separate,
   unevaluated, record-free lever; fix "attained" → "supremum" (N10).
3. **B3** — relabel "B2 − TPT = 0 exactly, 30/30" as a transcription-consistency check (COVER:97, :267); CR-2's
   support is TPT-O.
4. Wording: SC gain "strict" only for exact sups (N3); DRP-1 is outcome-adaptive, DRP-0 result-free only with a
   certified `s_1` (N11, N12); RSO "iff" statement (N14, N15). The commit subject of 6d0f0615 cannot be edited
   (no git writes); the registry/final report must carry the corrected wording instead.
5. Add `Q.guard_drift` inside `box_upper_tf` and `box_upper_composite` (N8).
6. Label the FSM SC-4w/TC⁺ ratios as exact-source idealizations (N4) and state the enclosure check's measured power
   (N16).

Notes N1, N2, N5–N7, N9, N13, N17, N18 are advisory.

## 7. Reviewer reproducibility

Scripts and outputs: `SCR/review_D/{rev_common,rev_tf_attack,rev_tf_attack2,rev_quad,rev_fsm_power}.py` and the
matching `.json`/`.log`; ledger redirected to `SCR/review_D/REVIEWER_LEDGER.jsonl` (4 entries; an early `rev_fsm_power` start was stopped unlogged to keep two processes max; classes
NONTARGET_DRIFT_VALIDATION / SYNTHETIC_VALIDATION, `cells_touched = []`). Run with `python3 -B` under `nice` and a
1500 s alarm, at most two concurrently. No Stream-D `main()` was called; nothing in NS was written except this file.
