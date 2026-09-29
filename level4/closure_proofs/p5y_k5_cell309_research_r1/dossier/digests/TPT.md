# Digest: Theorem TPT (Taylor-profile transport), implementation, validation, review R1 and r2 repair

Firewalled digest. Sources: `level4/closure_proofs/p5y_k5_tail_overnight_research/` (NS) —
`streams/E_assembly/{THEOREM_TPT.md, FREEZE_DESIGN_TPT_TAIL.md, IDEA_ADLR_ATOM_DIRECT.md, tpt.py, validate_tpt_r2.py,
validate_tpt_synthetic.py, validate_tptb_synthetic.py, test_tpt_guards.py, v3/*}`, `reviews/REVIEW_TPT_R1.md`.
Redaction tokens: `[TAIL-NUMBER REDACTED]`, `[TAIL-COMPARISON REDACTED]`, `[LATENT-PROXY REDACTED]`.
All numbers kept below are synthetic-fixture, lower-front (non-tail, e ≈ 0.006–0.025) or generic.

---

## 0. Status block of THEOREM_TPT.md (revision r2), near-verbatim

Status after independent review R1 (`reviews/REVIEW_TPT_R1.md`, NOT_READY, preserved at 32413877) and repair r2:

| component | state |
|---|---|
| Theorem TPT, Corollaries TPT-M/P, Propositions TPT-D/O/G, Lemma TC-P, Theorem TPT-B | mathematics **sound** (review R1 §1, re-derived by the reviewer) |
| implementation `tpt.py` r2 (sha256 `05cebc9c…`) | **VALIDATED_NON_TARGET** on exact synthetic fixtures (V1, r2 controls, V2 cap path) and on the TC input path of 136 real lower-front pairs (V3) |
| application to CUSUM m = 5 cells 306–309 | **BLOCKED (PROXY_EXPOSURE, incident 01)**: fails G8 at campaign level; cannot become FREEZE_READY in this campaign (charter rule G1/G7/G8) |
| TC-T / C2 tail input path | **unvalidated by design**: its inputs exist only for the quarantined cells; see `FREEZE_DESIGN_TPT_TAIL.md` (design only, for a future disclosed campaign) |
| floor r2 | **closure-only** |

"TPT has **never been evaluated on CUSUM m = 5 cells 305–309**."

## 0b. Motivation and provenance (§0), near-verbatim

The K5-B direct clause and its C5-T sharpening transport the midpoint value `g(e0)` across the cell by
`g(e) − g(e0) = −∫_{e0}^{e} t R''(t) dt`. Both then bound `R''(t)` by **one whole-cell interval**.

Theorem TC's proof (`p5y_k5_lower_front_order3/theorem/THEOREM_TC.md` §4 step 1) bounds each Taylor remainder at
distance `|t − e0|`, and only then replaces `|t − e0|` by ρ. Keeping `s = |t − e0|` gives a **new lemma, TC-P** (§2).
It is a small extension of TC's proof, reviewed in R1 (N2, N3), and not something TC itself certifies. It yields a
pointwise profile of the enclosure. At the midpoint the TC radius is only the midpoint-residual part
`rad_r(0) = A0 f_H + 2A1 f_D + A2 f_F`.

**Erratum TPT-E1.** The r0 text said `rad_r(0)` is "typically orders of magnitude smaller" than `rad_r(ρ)`. That is
regime-dependent. On the 136 real lower-front pairs the ratio is 0.94–0.97 (`v3/TPT_V3_REPORT.md`).

**Provenance disclosure (review R1 B1(c); `ledger/INCIDENT_01_TPT_GRAPH_PROXY.md`).**
* Before designing TPT, the author knew the committed C5 decomposition of the tail radius. [TAIL-COMPARISON REDACTED]
  The r0 sentence reflected that knowledge.
* TPT's content is general and nothing in it is tuned. But the choice to develop it first was informed by committed
  tail structure.

The C5 adjudication (`p5y_k5_tail_c5_exhaustion/evidence/adjudication/C5_ADJUDICATION.md` §7–§9) scopes C5-T's
exhaustion to exactly two inputs (`g_hi` and a whole-cell `[H_lo, H_hi]`). It lists "a transport consuming a third
certified input … a midpoint or sub-cell enclosure of R''" as unexcluded.

TPT is neither C5 route B2 (split the cell) nor D3 (second-order transport, which needs R''') (review R1 N15). Its
third input is a finer reading of the same certified premises, not new information. TPT therefore cannot exceed what
those premises imply (TPT-O).

## 1. Transport theorem (§1), verbatim

**Setting.** A cell `C = [x_lo, x_hi] = [e0 − ρ, e0 + ρ]` with **`x_lo > 0`**. `R` is C² on C, and
`g(e) := R(e) − eR'(e)`, so `g'(e) = −eR''(e)`.

**Inputs.**
* (i) `g(e0) ≤ g_hi`.
* (ii) Measurable `L, U` with `L(t) ≤ R''(t) ≤ U(t)` for every t ∈ C.

**Theorem TPT.** For every `e ∈ C`, `g(e) ≤ g_hi + P*`, where

    P* := max( 0,  sup_{e∈[e0,x_hi]} ∫_{e0}^{e} t·(−L(t)) dt,  sup_{e∈[x_lo,e0]} ∫_{e}^{e0} t·U(t) dt ).

*Proof.*
* g is absolutely continuous.
* For `e ≥ e0`: `g(e) − g(e0) = −∫ t R'' ≤ ∫ t(−L)`, because t > 0.
* For `e ≤ e0`: `g(e) − g(e0) = ∫ t R'' ≤ ∫ t U`.
* The case `e = e0` gives the 0 term. ∎

**Corollary TPT-M.** Assume `−L(e0+s)` and `U(e0−s)` are non-decreasing in s. Then
`P* = max(0, ∫_{e0}^{x_hi} t(−L), ∫_{x_lo}^{e0} tU)`.
*Proof.* `I'(s) = (e0+s)(−L(e0+s))` changes sign at most once, from − to +. So I is quasi-convex and its maximum is
at an endpoint. The left side is the same. ∎

**Corollary TPT-P.** `P* ≤ P₊ := max(∫ t(−L)⁺, ∫ tU⁺)`. This is theory only; `tpt.py` does not implement P₊. It is
never needed for record-based inputs (§2).

**Proposition TPT-D.** With `L ≥ H_lo` and `U ≤ H_hi`: `P* ≤ P₊ ≤ P_C5T < ρ x_hi M`.
* C5-T is TPT with the constant profile.
* The dominance over the **consumed** clause needs L and U to lie inside the consumed whole-cell enclosure
  `H_final`, meaning everything the consumer intersects (review R1 N7).

**Proposition TPT-O (sharpness within the three-input family; corrected per review R1 N1).** For given
`(g_hi, L, U)` with `L ≤ U`, the value `g_hi + P*` is the **supremum** over C² functions consistent with the inputs.
* It is approached by mollifying the witness that takes `R'' = L` right of e0 and `R'' = U` left of e0.
* It is attained only in the relaxed class where R'' is merely measurable. The r0 text wrongly said it is "attained".
* So no bound built from these three inputs alone is smaller.
* Scope, as in C5 §8: the witness is not resolvent-type, and the result is not valid for `x_lo = 0`.

## 2. Lemma TC-P (the third input) — VERBATIM

**Lemma TC-P.** Assume the premises of theorem TC, namely (P1)–(P4), or those of TC-T, namely (P1), (P2′), (P3′) and
Lemma G. For `t ∈ C` let `s = |t − e0|` and define

    p0(s) := f_F + s f_D + s² f_H/2 + s³ f_G/6 + s⁴ Env4/24,   p1(s) := f_D + s f_H + s² f_G/2 + s³ Env4/6,
    p2(s) := f_H + s f_G + s² Env4/2,                          rad_r(s) := A0 p2(s) + 2A1 p1(s) + A2 p0(s).

Then `|F_r''(t)(a) − Ĥ_r(a) − (t − e0)Ĝ_r(a)| ≤ rad_r(s)` for every t ∈ C.

*Proof* (restated precisely, per review R1 N2).
* **Taylor remainders at e0.** The expansions at e0 with integral remainder give `‖φ⁽ʲ⁾(t)‖ ≤ p_{2−j}(s)`, using:
  * the **midpoint** premises f_F, f_D, f_H, f_G. σ3, a midpoint premise, enters only through f_G, which is the
    coefficient of the φ‴(e0) term. That is a midpoint object.
  * the **whole-cell** bound Env4 on ‖φ⁗(u)‖ for u ∈ [e0, t] ⊂ C.
    * Env4 itself uses |t| ≤ ρ inside (P3).
    * In TC-T, σ4 comes from the (P3′) cell tower, which carries a ρ mean-value correction.
    * Both are whole-cell constants and stay valid at every u of the segment.
* **Error identities and constants.** TC §4 steps 2–3 are unchanged. The error identities hold at every e, and
  step 3 is pointwise in t. The A-constants of Lemma G or Lemma Dv′ are uniform on C.
* **Centre motion.** The relaxation per r, `(t − e0)Ĝ_r(a) ∈ [−s|Ĝ_r(a)|, s|Ĝ_r(a)|]`, is valid. ∎

**Profile enclosure.**

    R''_m(t) ∈ Σ_{r<m} (1/m)[Ĥ_r(a) ± (rad_r(s) + s|Ĝ_r(a)|)] + Σ c·𝒲_(r,j),

where the whole-cell W enclosures are constant in t. With `H_final` the **consumed** whole-cell enclosure (N7):

    L(t) := max(H_final.lo, lo(s)),   U(t) := min(H_final.hi, hi(s)).

The profile coefficients are all ≥ 0, so lo is non-increasing in s and hi is non-decreasing. Corollary TPT-M then
applies exactly. The committed records carry only |Ĝ(a)|, so the symmetric relaxation is what is used.

**Fail-closed rules, enforced by `tpt.py` r2:**
* Refuse a pointwise-empty intersection. It is narrowest at s = 0 (N5).
* Accept exact rationals only (N6).
* If the consumed M_k is supplied, it must equal `mag(H_final)` (N7).
* Refuse unordered intervals, and refuse an m label that does not match the number of source terms.

**The geometry guard is defence in depth only (N4).**
* The enclosure does not depend on e0, and P* is affine in e0.
* So the real barrier against target evaluation is the input-path quarantine: no new code reads tail input files.

**Proposition TPT-G (target-free structure of the gain; premises made explicit per N13).**
* On the binding right side, write `−L(e0+s) = c + αs + βs² + γs³ + δs⁴`, where
  `c = −W_lo − Σ_r (Ĥ_r,lo − rad_r(0))/m`, and α, β, … are the s-coefficients (all ≥ 0).
* The whole-cell charge of the `s^k` term exceeds the profile integral by the factor
  `(x0 + ρ/2)/(x0/(k+1) + ρ/(k+2))`, where `x0 = e0`. As ρ/x0 → 0 this factor tends to k + 1.
* The constant term c is charged identically by both.
* The comparison assumes `c ≥ 0`, which is a data-dependent sign premise.
* (Review N13 confirms the finite-ρ ratios `(x0/2 + ρ/3)/(x0 + ρ/2)` and `(x0/3 + ρ/4)/(x0 + ρ/2)` for the
  linear/quadratic components.)

**Correction per review R1 B1(b).** The r0 text said that combining this proposition with committed tail
decompositions "was not done". **At campaign level it was done.** The coordinator's dependency graph placed the
committed tail shares next to these factors (commit 4403f86f). It is retracted and recorded as incident 01, and TPT's
tail application is BLOCKED for this campaign.

## 2b. Theorem TPT-B (block-resolved profile), near-verbatim

Let each block's constants `(A0^b, A1^b, A2^b)` be valid on that block. Then Lemma TC-P holds pointwise with the
constants of the block containing t, because TC §4 step 3 is pointwise. Within one block the integrand is monotone,
so the running integral is quasi-convex on each piece. Hence

    P*_B = max(0, running integral at the piece ends),

which is exact. It satisfies `P*_B ≤ P*_TPT` whenever `A^b ≤ A^cell`. Mathematics sound (review R1 N16).

Validation r2 on 24 exact fixtures: pointwise violations 0; transport certified sound 24/24; dominance 24/24;
code-path control detected 24/24; θ-controls 1/2 / 9/10 / 99/100 detected 22 / 10 / 4. The r1 control was a tautology
and is withdrawn. Gain on these fixtures P*_B/P*_TPT ∈ [0.99896, 1] — specific to these fixtures (k_i bounded over
[0, e_hi], not per block). TPT-B is not ranked as a route.

## 3. What TPT changes, and its governance (§3), near-verbatim

| item | status |
|---|---|
| inputs | `g_hi`, the consumed whole-cell enclosure, W, A, `f_*`, Env4, ρ, cover: **unchanged** |
| TC / TC-T radius | used pointwise in t |
| consumer | **changed**: the direct clause is replaced by `g_hi + P*` |
| floor r2 | **closure-only**. The anchor is `quantity_compared.adoption_quantity` ("the frozen consumer path … with the atom constants S substituted and every other input unchanged"), with `fail_closed[2]`. The r0 citation of `fail_closed[3]` was inapt (N10). Adoption would need a floor extension frozen before any evaluation (C2 Condition 1; route audit U3). |
| chain clause (γ_k) | not in the adoption quantity. A consumer feeding γ_k would need only `g(x_k) ≤ g_hi + I_right(ρ)`, which is not implemented (N11). |
| cells 305 / 306 | **305 OUT**: adopted under r1 and not re-adjudicable. **306 OUT**, decided prospectively here: a TPT evaluation at 306 would be designed knowing the sealed adverse I2 result, which the route audit classes RESULT_CHASING_RISK / GOVERNANCE_BARRED (306-g). (N12) |
| G10 | **undetermined prospectively**. The only non-target real evidence gives 0.7–2.5 % of the penalty on the lower front, which is cosmetic there. Any claim of material tail value would go through the incident-01 proxy (N14). |

## 4. Validation record (§4; pinned `tpt.py` r2 sha256 `05cebc9c…`)

| id | what | result | file |
|---|---|---|---|
| V1 | exact FSM fixtures: Lemma TC-P pointwise; transport certified sound (rigorous sup g, adaptive bisection) | 0 violations; 12/12 sound | `validation/TPT_SYNTHETIC.json` (r1 negative control marked WITHDRAWN inside) |
| r2 controls | code-path pointwise plant (A and \|G\| scaled so rad_poly is invalid); transport plants θ·P and mutants M2 (t sign), M4 (radius at s/2), M5 (Env4 dropped) | code path detected 12/12; θ = 1/2, 9/10, 99/100 detected 11, 5, 2; M2, M4, M5 detected 6, 4, 2; every control fires somewhere | `validation/TPT_R2_VALIDATION.json` |
| V2 | cap/split path with a rigorously **certified truth cap** (grid R'' ± (h/2)·B3) | 12/12 sound; 12/12 dominated by C5-T with same cap; interior splits right 11/12, left 12/12 | `validation/TPT_R2_VALIDATION.json` |
| V3 | 136 real lower-front pairs, TC input path; independent TC re-derivation reproduces the committed H_TC exactly | gate 136/136; P_tpt/P_c5t 0.975–0.993 (regenerated against r2) | `validation/TPT_V3_LOWER_FRONT.json`, `v3/` |
| V4 | Riemann upper and lower sums vs closed form | bracket holds; same module and same profile derivation, so **not** an independent implementation (N8) | same |
| guards | `test_tpt_guards.py` G1–G8 | pass on r2; G1–G5 fail on r0, G6–G8 on r1 | — |
| not done | non-monotone P₊ path (theory only); TC-T tail input path (quarantined; design only) | — | — |

---

## 5. `tpt.py` (r2) — functions and exact formulas implemented

Stdlib only, exact `fractions.Fraction`. Imports `NS/code/ov_quarantine` and calls `Q.install_import_guard()`.
Polynomials are coefficient lists in s, low → high.

Helpers: `padd(a,b,sb)` = a + sb·b; `pscale(a,c)`; `pmul`; `peval` (Horner); `pint(a,lo,hi)` = exact
Σ_k c_k (hi^{k+1} − lo^{k+1})/(k+1).

Data classes:
* `SourceTerm`: `H_at_a` (lo, hi) enclosure of Ĥ_r(a); `abs_G_at_a` = |Ĝ_r(a)| (0 under TC-T (P2′)); `fF, fD, fH, fG,
  Env4`.
* `CellProfile`: detector, m, cell, e0, rho, g_hi, A0, A1, A2, terms (r = 0..m−1, each weighted 1/m), `W` (lo, hi)
  whole-cell W enclosure sum (already c-weighted), `H_K1` (the CONSUMED whole-cell enclosure H_final, or None),
  label, meta, `M_consumed` (optional). Properties x_lo = e0 − ρ, x_hi = e0 + ρ.
* `Block(e_lo, e_hi, A0, A1, A2)` for TPT-B.

Formulas:
* `rad_poly(cp, t)`: p0 = [fF, fD, fH/2, fG/6, Env4/24], p1 = [fD, fH, fG/2, Env4/6], p2 = [fH, fG, Env4/2];
  rad = A0·p2 + 2A1·p1 + A2·p0, **plus** the centre-motion term s·|Ĝ(a)| (added to the s¹ coefficient).
* `lo_hi_polys(cp)`: lo(s) = W_lo + Σ_r (1/m)(H_at_a.lo − radpoly_r(s)); hi(s) = W_hi + Σ_r (1/m)(H_at_a.hi +
  radpoly_r(s)) (no cap).
* `_check(cp)` (called by every public function): `Q.guard_cell(detector, m, cell)`; `_check_types` (N6: every numeric
  field must be Fraction or int, bool/float refused); `Q.guard_drift(x_lo, x_hi)` (geometry binding: refuses the tail
  band whatever the label); `len(terms) == m`; ordered intervals for W, H_K1, every H_at_a; `x_lo > 0`; `rho > 0`;
  all profile coefficients (abs_G, fF, fD, fH, fG, Env4) ≥ 0; A0, A1, A2 ≥ 0.
* `_crossing(poly, level, rho, decreasing, bits=60)`: rational s' in [0, ρ] at or BEFORE the crossing of poly with
  the cap level (60-bit bisection), returning the **non-binding side** endpoint `a` (T3 repair); None if the profile
  binds on all of [0, ρ]; 0 if the cap binds already at s = 0.
* `check_nonempty(cp)` (N5): L0 = lo(0), U0 = hi(0), intersected with H_K1; refuse if L0 > U0.
* `penalty_closed(cp)` (Corollary TPT-M): right integrand (e0 + s)(−L(s)), L = max(capLo, lo(s)); left integrand
  (e0 − s)·U(e0 − s), U = min(capHi, hi(s)). Without a crossing: I_right = ∫_0^ρ (e0+s)(−lo(s)) ds,
  I_left = ∫_0^ρ (e0−s) hi(s) ds. With a crossing s': profile integral on [0, s'] plus constant-cap integral
  ∫_{s'}^{ρ} (e0 ± s)·cap ds (an upper bound). P* = max(0, I_right, I_left). Returns P_star, I_right, I_left,
  split_right, split_left.
* `penalty_riemann(cp, N=64)`: monotone Riemann **upper** sum on a uniform partition; f = −L(b) (sup on [a,b] at b),
  weight max((e0+a)f, (e0+b)f); left symmetric with U(b).
* `penalty_riemann_lower(cp, N=64)`: Riemann **lower** sum (uses L(a), U(a) and min of the weights).
* `whole_cell_enclosure(cp)`: (lo(ρ), hi(ρ)) intersected with H_K1; raises on empty.
* `penalty_c5t(cp)`: with H = whole-cell enclosure, wR = ρ(x_hi − ρ/2), wL = ρ(x_lo + ρ/2);
  P_c5t = max(max(−H_lo, 0)·wR, max(H_hi, 0)·wL).
* `penalty_frozen(cp)`: ρ·x_hi·mag(H), mag = max(|H_lo|, |H_hi|); if `M_consumed` is given it must equal mag (N7) else
  ValueError.
* `evaluate(cp)`: computes all of the above; asserts lower sum ≤ P_closed and ≤ P_riemann (V4 bracket), asserts
  P_tpt ≤ P_c5t ≤ P_frozen (TPT-D) else AssertionError; returns P_tpt, P_riemann, P_riemann_lower, P_c5t, P_frozen,
  Gamma_tpt = g_hi + P_tpt, Gamma_c5t, Gamma_frozen, detail.
* `_lo_hi_with(cp, A)`, `_check_blocks(cp, blocks)` (blocks must cover the cell, be contiguous, each passes
  `guard_drift`, A ≥ 0, exact types), `penalty_blocked(cp, blocks)` (Theorem TPT-B): cuts at e0, x_hi/x_lo and block
  edges; per piece the componentwise max of A over the containing blocks; `piece_integral` handles the cap per piece
  with the non-binding-side split; running integral from e0 outward on each side, P*_B = max(0, running values at
  piece ends). Returns P_star_B, I_right_full, I_left_full, pieces.

Revision history in the docstring: r1 (after V3 report) = T1 guard on every public function; T2 label/terms/geometry
binding; T3 split point on the non-binding side; T4 Riemann lower-sum bracket replaces the "closed ≤ Riemann upper"
assertion, interval orders validated. r2 (after REVIEW_TPT_R1) = N5 empty pointwise intersection refused; N6 exact
rational contract; N7 H_K1 must be H_final, M_consumed checked. Docstring states the guards are DEFENCE IN DEPTH ONLY;
"no freeze may rely on these guards as a safety property".

## 6. Validation scripts

### `validate_tpt_synthetic.py` (V1/V2/V4 of r0/r1; writes `validation/TPT_SYNTHETIC.json`)
* Fixtures: seeds 1..12, n = 4 + seed%3, m = 1 + seed%3, ρ ∈ {1/64, 1/32, 1/16}[seed%3], perturbation
  ∈ {1e-6, 1e-4, 1e-3}[seed%3], e0 = 1/8, Ĝ mode "zero" (even seeds) or "real" (odd).
* `build_fixture`: random sub-Markov polynomial drift family (`ov_fixtures.random_family`), m polynomial sources;
  k_i = sup over [0, e0+ρ] of row sums of |K_i| (polynomial abs bounds); certified C ≥ sup ‖R_e‖ by the Neumann bound
  ‖R_e‖ ≤ ‖R0‖/(1 − ‖R0‖d); Lemma-G constants A0 = C, A1 = k1 C², A2 = k2 C² + 2 k1² C³; perturbed candidates
  F̂, D̂, Ĥ (and Ĝ = 0 or ≈ F'''); exact residuals φ0..φ3; f_X = sup norms of φ_j; σ4 = sup of S''''; Env4 = σ4 +
  4k1 sG + 6k2(sH + ρsG) + 4k3(sD + ρsH + ρ²sG/2) + k4(sF + ρsD + ρ²sH/2 + ρ³sG/6); g_hi = exact g(e0).
* `third_derivative_bound`: certified B3 ≥ sup|R_m'''| via the Leibniz tower ‖F^(n)‖ ≤ C(σ_n + Σ_i C(n,i) k_i ‖F^(n−i)‖).
* `check_fixture`: Lemma TC-P pointwise on a 401-point rational grid vs exact F_r''(t)(a); transport soundness with
  rigorous sup g (grid max + (h/2)·x_hi·(max|R''| + (h/2)B3), adaptive bisection to depth 16); r1 negative control
  (radius := max true dev/2) — **WITHDRAWN** per review B2 (exercised only the comparison).

### `validate_tpt_r2.py` (repairs B2, B3; writes `validation/TPT_R2_VALIDATION.json`; records sha256 of tpt.py)
Same 12 configs. Per fixture:
* P1: pointwise Lemma TC-P (0 expected) and a CODE-PATH control: A0, A1, A2 and |G(a)| scaled by
  λ = (max true dev / 2)/(max rad) so that `tpt.rad_poly` itself yields an invalid radius → must report ≥ 1 violation.
* P2: transport soundness (rigorous sup g) for TPT; TRANSPORT-LEVEL controls: planted bounds g_hi + θP for
  θ ∈ {1/2, 9/10, 99/100}, and mutants M2 (right-side weight t → e0 − s), M4 (radius evaluated at s/2), M5 (Env4
  dropped); DETECTED when the exact grid maximum of g exceeds the planted bound.
* V2: H_K1 := certified truth cap [min R'' − (h/2)B3, max R'' + (h/2)B3]; checks soundness, dominance vs C5-T with the
  same cap, interior split counts, cap tightens P, and the N5 check.
* Summary flag `P2_every_control_fires_somewhere`.

### `validate_tptb_synthetic.py` (TPT-B; writes `validation/TPTB_SYNTHETIC.json`)
Same seeds; each cell split into nb ∈ {2, 4} blocks, each with its own certified Lemma-G constants
(`block_constants`: C over the block by Neumann, k1, k2 over [0, e_hi]). Checks: B1 pointwise with the block's
constants; B2 rigorous transport soundness vs g_hi + P*_B; B3 dominance P*_B ≤ P_tpt(cell-max constants) ≤ P_c5t;
B4 (r2) code-path plant: block constants scaled by λ so `rad_at` via `tpt._lo_hi_with` is invalid (r1's
`x > max(d)/2` count was a tautology, withdrawn); B5 θ-controls.

### `test_tpt_guards.py` (G1–G8, each must be able to fail on older code)
* G1: tail-band geometry (an e0 inside the quarantined band, specific value omitted) labelled as lower-front cell 44,
  m = 5 → refused by `guard_drift` (message must contain DRIFT_BAND), not by the label.
* G2: label m = 3 carrying five terms → refused.
* G3: every public function (rad_poly, lo_hi_polys, whole_cell_enclosure, penalty_closed, penalty_riemann,
  penalty_riemann_lower, penalty_c5t, penalty_frozen, evaluate) refuses a target label (cell 307, benign geometry).
* G4: split-side: cap crossing at ρ/2^70 (below 60-bit resolution) — no spurious TPT-D violation, closed ≤ C5-T,
  lower ≤ closed.
* G5: unordered centre interval refused. G6 (N6): float Env4 refused. G7 (N5): empty intersection at s = 0 refused
  (cap (0, 10) above hi(0)). G8 (N7): `M_consumed` ≠ mag(H_final) refused by `penalty_frozen`.
* Synthetic base profile: e0 = 1/2, ρ = 1/20, g_hi = −1/10, A = (2, 3, 10), term H_at_a = (−1, −1), fF = fD = fH =
  1/100, fG = 1, Env4 = 2.

## 7. V3 — the independent verifier (`v3/`)

**What it is:** class NONTARGET_REAL_VALIDATION. Theorem TPT applied to the **real, non-target lower-front** TC cells
(CUSUM cells 11–44, m ∈ {1, 2, 3, 5} → 136 pairs; e ∈ [0.0057097, 0.0252261], ρ ∈ [2.66e-4, 3.10e-4]). 0 target
cells evaluated; runtime guard ran 139 times, 0 refusals; static scan 0 findings.

* `v3/tc_reder.py`: **independent re-derivation** of theorem TC from THEOREM_TC.md §2–3, importing no historical
  module (no tc_rule, tc_crosscheck or consumer); record fields read as data only. Route deliberately different:
  p0, p1, p2 are P(ρ), P′(ρ), P″(ρ) of ONE quartic P(s) = f_F + s f_D + s² f_H/2 + s³ f_G/6 + s⁴ Env4/24 with
  f_X = δ_X + eps_src[order(X)]; Env4 = σ4 + Σ_{i=1..4} C(4,i) k_i T_{4−i}(ρ), T_n = n-th derivative of the candidate
  majorant Mc(s) = s_F + s s_D + s² s_H/2 + s³ s_G/6 at ρ; σ4: r = 0 → sup_S0[4]; r ≥ 1 → Leibniz Σ C(4,i) j_i
  ‖h_r^(4−i)‖ with the true-object h-tower (‖h_j‖ ≤ 1, ‖h_1^(n)‖ ≤ sup_S0[n−1], ‖h_j^(n)‖ ≤ Σ C(n,i) k_i
  ‖h_{j−1}^(n−i)‖); rad_r = A0 p2 + 2A1 p1 + A2 p0; half_r = ρ|Ĝ_r(a)| + rad_r; assembly F_r weight 1/m, W2["r:j"] weight
  1/t − 1/m (j = t − r − 1). A-constants taken as given from `tc_audit[cell][m]["A"]`. Refuses non-Fraction or
  negative inputs (`_nn`). Also `profile_polys`, `exact_Pstar_nocap` (closed-form antiderivatives), `lower_sum`.
* `v3/tpt_v3_lower_front.py`: driver. Reads only `p5y_k5_lower_front_order3/evidence/tc_r1/cells/TC_CELL_{11..44}.json`
  and `TC_CONSUMPTION.json` (restricted to cells 11–44 immediately after load; its per-cell dict holds cells 0–159
  only). Steps: (1) whole-cell TC enclosure from records; (2) REPRODUCTION GATE: re-derived 𝓗_m == committed
  `H_TC` exactly; (3) `tpt.CellProfile` from the same per-source quantities; variant A H_K1 = None, variant B
  H_K1 := H_final (identical on all 136, since H_final = H_TC on both sides); g_hi = R.hi − e0·D.lo (frozen
  `k5b_literal` form); P_tpt, P_riemann (N = 64, 256), P_c5t, P_frozen, frozen clause ρ·x_hi·M_k; independent exact P*
  and lower-sum bracket.
* Results (lower front): gate 136/136; P_tpt = independent P* 136/136; lower₆₄ ≤ P_tpt ≤ P_riemann₂₅₆ ≤ P_riemann₆₄;
  TPT-D 136/136; P_tpt/P_c5t min/median/max 0.97520/0.98856/0.99262; P_tpt/P_frozen 0.9128/0.9608/0.9743; P_c5t/P_frozen
  0.9360/0.9720/0.9816; Γ_c5t − Γ_tpt ∈ [4.54e-7, 3.50e-6]; direct-clause passes (Γ < 0): frozen 30, C5-T 30, TPT 31
  (one flip: lower-front cell 41, m = 5: frozen +5.39e-6, C5-T +2.16e-8, TPT −2.10e-6); no pair's overall status
  changes (all closed via chain).
* Findings: TPT sound, gain 0.7–2.5 % of penalty; R'' > 0 on every cell (P* on left side); rad(0)/rad(ρ) = 0.939–0.969
  on all 136 pairs (so the "orders of magnitude" claim is false here); most gain from centre motion ρ|Ĝ(a)|
  (7–14 % of half-width); "No inference is made about the tail." Signed Ĝ_r(a) not recorded — only |Ĝ|, so the
  symmetric relaxation is used and the P₊ branch is never needed.
* Defects reported (not fixed by V3): T1 guard coverage gap (lo_hi_polys, rad_poly, whole_cell_enclosure unguarded);
  T2 m label not bound to terms (label bypass demonstrated on cell 11 only), cell label not bound to geometry; T3
  split point could land past the crossing (spurious TPT-D assertion on a SYNTH probe); T4 minor (P_closed ≤ P_riemann
  asserted though not a theorem after a split; penalty_frozen uses mag(H) not M_k; interval order unchecked; Env4 used
  at whole-cell value though Env4(s) allowed). All repaired in tpt.py r1/r2.
* Limitations: no ground truth on real cells (only s = ρ externally anchored); cap/split path untested on real data;
  only the direct clause evaluated; two prototype runs logged retroactively; full-namespace scan not run.

## 8. FREEZE_DESIGN_TPT_TAIL.md (answer to R1 B4) — DESIGN ONLY, NOT FROZEN, NOT AUTHORIZED

* §0 preconditions (user decisions, in order): (1) disclosure of incident 01 to the authorizing user; (2) U3 floor
  extension naming the TPT clause frozen before any evaluation, else explicitly CLOSURE_ONLY; (3) cell set fixed now
  = {307, 308, 309}; 305 OUT (adopted under r1), 306 OUT (sealed adverse I2 result known; route audit 306-g); no cell
  added after any result.
* §1 evaluated once per k ∈ {307, 308, 309}: Γ_TPT(k) = g_hi(k) + P*(k); supply S_I1 as frozen by floor r2
  (componentwise min over {Lemma G, C1, C2}, C2's committed provenance); P* from Lemma TC-P under TC-T premises; cap =
  consumed H_final; all other inputs C2's frozen consumer inputs.
* §2 extraction from the **frozen code path** (R1 B4(a)): import pinned modules `c2_d5_forecast.py` 18403dbe,
  `deflated_consume.py` a0a836fa, `tct_rule.py` 98f6eee4, `tail_forecast_r2.py` (pinned by hash); read per-r tuple
  `(f_F, f_D, f_H, f_G, Env4, Ĥ_r(a), |Ĝ_r(a)| = 0)`, the W sum, supply A, g_hi = R.hi − e0·D.lo, H_final and M; wrap
  without modifying; record called functions.
* §3 reproduction gates (exact rational equality) inside the sealed execution, before P*: G-R1 rebuilt whole-cell
  enclosure at s = ρ == C2's committed `H_exact`; G-R2 frozen-clause Γ == C2's committed `Gamma_exact` (floor r2
  `fail_closed[2]` control); G-R3 per-r (f_*, Env4) == committed per-r values (catches errors preserving rad(ρ) but
  mis-shaping rad(s)); G-R4 `M_consumed == mag(H_final)` and s = 0 non-emptiness. Any failure → STOP,
  `REPRODUCTION_FAILED`.
* §4 qualification on manufactured TC-T-shaped decoys (Ĝ = 0, two towers, synthetic numbers), planted mismatches must
  STOP; sandbox built at the freeze commit (C12 lesson); every written path a seal precondition (lexists/lstat,
  O_CREAT|O_EXCL|O_NOFOLLOW; post-marker failures sealable); tpt.py pinned `05cebc9c…`; every validation regenerated
  against that hash (N9).
* §5 exactly-once (C12-R2 pattern): consumed ref `refs/tpt-tail/target-consumed` → grant commit; pending-result ref and
  sealed result committed alone; ledger line written before execution (N17); refusals are recorded outcomes; no
  re-run.
* §6 leakage: the evaluation is the target itself (three Γ values, consumed once); result-chasing risk MEDIUM–HIGH
  (tail relevance anticipated from committed tail structure; no parameter tunable after freeze); a pass under
  CLOSURE_ONLY is scientific closure, not adoption, creates no r6.

## 9. IDEA_ADLR_ATOM_DIRECT.md (timestamped 2026-09-27 ~18:30Z, no cell data; passed to stream B)

Identity (killed CUSUM kernel, drift only through φ(z + e); LR identity from `streams/C_308/IDEA_LR_SCORE_CONSTANTS.md`):

    (∂_e^j R_e f)(a) = E_a[ Σ_{n<τ} f(X_n) · H_j(M_n, n) ],   M_n = Σ_{k≤n} S_k,  S_k = −(Z_k + e) ~ N(0,1),
    H_0 = 1, H_1 = M, H_2 = M² − n, H_3 = M³ − 3nM, H_4 = M⁴ − 6nM² + 3n².

Leibniz on F_r(e) = R_e S_r(e) at the atom: `|F_r^{(k)}(e)(a)| ≤ Σ_{j=0..k} C(k,j) Λ_j(e) ‖S_r^{(k−j)}(e)‖`,
`Λ_j(e) := E_a[Σ_{n<τ} |H_j(M_n, n)|]`, Λ_0 = Λ.

Enclosure: `F_r''(t)(a) ∈ Ĥ_r(a) ± [rad_TC(0) + s·B3_r + (s²/2)·B4_r]`, s = |t − e0|, rad_TC(0) = A0 f_H + 2A1 f_D +
A2 f_F (theorem AD midpoint bound), B3_r ≥ |F_r'''(e0)(a)|, B4_r ≥ sup_cell |F_r''''(u)(a)|, with source-derivative
sups σ_n(r). No candidate payloads needed for orders 3–4; avoids A0 × whole-function sups in f_G; combines with TPT
(same (constant, s, s²) shape). Status THEORY_ONLY; needs Λ_j certified uniformly over the cell and σ_n valid on the
cell (n = 4) and at e0 (n = 3); closure-only under floor r2; must never be evaluated on cells 305–309 or drifts in
[1.2, 2.6]. (Evaluated on fixtures by stream B: see ORDER3 digest.)

---

## 10. REVIEW_TPT_R1 — ROUTE_REVIEW: NOT_READY

Reviewer independent, read-only; 2026-09-28. Scope: THEOREM_TPT.md, tpt.py (sha256 `77c1646e…` = HEAD `ccc4ea36`),
test_tpt_guards.py, validate_tpt_synthetic.py, validate_tptb_synthetic.py, v3/*, the three validation JSONs.
Reviewer runs on synthetic FSM fixtures (e0 ∈ {1/8, 1/4, 1/2}) and two hand-written synthetic profiles at
e0 ∈ {1/2, 3/4}; ledger redirected to scratch; `python3 -B`.

### Summary table (verbatim-close)
| question | finding |
|---|---|
| 1 derivation | **Sound.** TPT, TPT-M, TPT-P, TPT-D, Lemma TC-P (under TC (P1)–(P4) and TC-T (P1), (P2′), (P3′), Lemma G), TPT-B all hold. Wording defects: TPT-O "attained" (N1), Lemma TC-P "no inequality uses s = ρ" (N2), "already certified by TC" (N3), TPT-G sign premise (N13). Consumer-contract gaps: H_K1 must be the consumed H_final, M_k = mag(H_final), empty-intersection refusal, exact types (N5–N7). |
| 2 novelty | **Genuinely new** (N15): C5 adjudication §9 lists "every transport using a third certified input" as unexcluded; TPT is neither B2 nor D3. |
| 3 implementation | **Correct; not broken.** 0 unsound in 576 exact-truth evaluations incl. 192 with interior cap splits; guard tests pass on r1, fail on r0. Guard overclaim (N4), missing fail-closed branches (N5, N6). |
| 4 tests | **Inadequate as committed** (B2, B3). |
| 5 leakage | **Defect** (B1): the campaign graph combines TPT-G's charges with tail-cell S̄ shares. No target value computed by the route (ledger clean). Cell 306 not addressed (N12). |
| 6 governance | Closure-only **correct**; `fail_closed[3]` citation inapt (N10). **FREEZE_READY not justified** (B4). |

Route states supported: TC path VALIDATED_NON_TARGET; TC-T/C2 path IMPLEMENTED, unvalidated; overall not FREEZE_READY;
r2 closure-only. Gates: G1 disputed (B1), G2 PASS, G3 PASS with N1/N2/N13 wording, G4 PASS, G5 PASS on TC path only
(B4), G6 PARTIAL (N8), G7 PASS for the route's own runs, G8 FAIL at campaign level (B1), G9 NOT YET (B4, N5–N7, N9,
N11, N12), G10 undetermined prospectively (N14).

### Blockers
**B1. An implicit tail forecast built on TPT-G is in the campaign record; THEOREM_TPT's "was not done" is false at
campaign level.**
* r0 THEOREM_TPT.md:154-155: "Combining this proposition with committed per-cell radius decompositions or C8 factors
  to predict any tail cell's Γ is a target-equivalent proxy. It is forbidden in this campaign and was not done."
* `graph/K5_TAIL_DEPENDENCY_GRAPH.md:110` (committed `4403f86f`, after TPT-G `9db36e13`), rank-1 row, owner TPT:
  [TAIL-COMPARISON REDACTED]
* The percentages in that row are **tail-cell** shares of S̄ quoted from `graph/sources/graph_A_consumer.md:488-491`
  (A0·ρ·f_G, cells 306–309: [TAIL-NUMBER REDACTED]) and `:512-513` (A0·ρ²·Env4/2: [TAIL-NUMBER REDACTED]). S̄ is the
  m = 5 tail radius mean (`graph_A_consumer.md:80`), and the penalty on 306–309 is an affine function of S̄
  (`:126-128`; exact tail-specific form withheld: [TAIL-COMPARISON REDACTED]). Share × charge is a direct estimator of TPT's tail penalty reduction, i.e. "a ratio from which such a
  Γ could be inferred" — load-bearing under ROUTE_AUDIT_R1.md:560-563. It also ranks the route by target-cell data
  (S1).
* Motivation provenance: the first version of §0 (`git show af4365aa:…/THEOREM_TPT.md`, line 16) said the midpoint
  radius is "typically orders of magnitude smaller" than rad_r(ρ). [TAIL-COMPARISON REDACTED] It is false on the only
  non-target real data (0.94–0.97, TPT_V3_REPORT.md). The erratum TPT-E1 fixes the claim but does not disclose where
  "typically" came from; the reviewer cannot establish what the author saw.
* Aggravating fact: on the tail every TPT input (per-r f_F…f_G, Env4, Ĥ_r(a), W, A of the supply) is already a
  committed number (e.g. Env4 per r for 306–309 at `graph_A_consumer.md:505-508`), so TPT's tail Γ is a closed-form
  function of committed data. Blindness rests entirely on nobody doing that arithmetic; the graph row does most of it.
* **Required:** (a) retract or quarantine-label the graph row (and its JSON twin) as a target-equivalent proxy;
  (b) correct THEOREM_TPT.md:154-155 to disclose the combination exists; (c) record in §0 what tail-derived material
  was read before af4365aa; (d) a user ruling (U3 context) that a TPT floor extension would be decided knowing this
  proxy.

**B2. Negative controls that cannot fail, or do not exercise the object under test (S2, S7).**
* TPT-B B4 is a tautology: `validate_tptb_synthetic.py:77` `viol_nc = sum(1 for d in devs for x in d if x > max(d)/2)`
  — detects on every fixture regardless of `rad_at`, `penalty_blocked`; reported as "B4 truth-relative negative
  control detected | 24/24".
* V1's control does not touch the transport (replaces every radius by max(true dev)/2, counts d > r); no negative
  control for `sound_transport_certified`.
* Reviewer A2 shows the fixture set does have power (θ·P detected for θ = 0.99 on 2/12, 0.9 on 5/12, 0.5 on 11/12;
  mutants 2–6/12).
* **Required:** replace B4 by a truth-relative plant through `penalty_blocked`/`rad_at`; add transport-level plants
  (θ·P and ≥ 1 implementation mutant) with coverage; correct the TPT-B row.

**B3. Declared validation obligations V2 were never executed; claims outrun code.**
* V2 declared: non-monotone profiles (P₊ path), H_K1 binding on part of the cell, planted invalid profile. `grep
  H_K1` finds no use in the validators; `tpt.py` has no P₊. The only cap exercise was `test_tpt_guards.py` G4 (no truth)
  and V3 variant B (cap never binds). The split code — the only non-trivial branch — had no truth-relative test.
* Reviewer A3 exercised the cap/split path against exact truth: 0 unsound.
* **Required:** commit its own V2 (or delete V2 from §4 and the purpose string); state that the P₊ branch is
  unimplemented.

**B4. The tail input path (TC-T / C2 consumer) is unvalidated and has no freeze design.**
* V3 validates only the TC path (real Ĝ, registry-r1 Lemma Dv′ constants taken as given, (P3) tower). The tail uses
  TC-T: Ĝ := 0, (P2′) f_G = 3k₁s_H + 3k₂s_D + k₃s_F + σ3 (+ eps_src[3]), (P3′) two towers with the mean-value
  correction, and the D4 minimum over Lemma G ∪ Lemma Dv′ r2 via `c2_d5_forecast` → `deflated_consume` → `tct_rule`.
* TC-T per-r inputs exist only for cells 305–309 (`p5y_k5_m5_tail_closure/evidence/measurement_r1/TCT_INPUTS_305..309.json`),
  all quarantined; no non-target real cell exists on which to rehearse the extraction.
* Unspecified: (a) extraction of per-r inputs from frozen `tct_rule` without hand re-derivation; (b) a reproduction
  gate re-deriving the committed 𝓗_5 (and C2's `Gamma_exact`, floor r2 `fail_closed[2]`) exactly inside the sealed
  execution before P*; (c) decoy/synthetic qualification on manufactured TC-T-shaped inputs (Ĝ = 0, two towers);
  (d) exactly-once mechanics.
* A gate at s = ρ cannot see an error that preserves rad_r(ρ) but mis-shapes rad_r(s): also check the per-r coefficient
  vector against committed per-r values, or extract from the frozen code path itself.

### Notes N1–N17 (condensed, near-verbatim)
* **N1** TPT-O "attained" false in the stated class (witness has R'' jumps, R not C²); bound is the supremum over C²
  members. Rephrase.
* **N2** Lemma TC-P proof wording "No inequality of TC uses s = ρ except the final substitution" is literally false
  ((P3) Env4 uses |t| ≤ ρ; TC-T (P3′) cell tower uses ρ in the mean-value correction); but both are whole-cell
  constants valid at every u ∈ [e0, t], so the lemma is correct. Reviewer checked each term (p_j Taylor with whole-cell
  Env4; f_G/σ3 midpoint; σ4 only in Env4; A's uniform; TC §4 step 3 pointwise; centre relaxation valid; W constant in t).
* **N3** "the pointwise profile that theorem TC already certifies" is wrong: TC certifies only the ρ-substituted
  enclosure; Lemma TC-P is new and must be reviewed as such.
* **N4** Geometry guard overclaim: rad_poly, lo_hi_polys, whole_cell_enclosure don't depend on e0 and each side of P* is
  affine in e0 (reviewer: I_right(e0+d) = I_right(e0) + d·∫(−lo) exactly under a synthetic shift 1/2 → 3/4). Effective
  barrier is the input-path quarantine (`ov_quarantine.FORBIDDEN_PATH_PATTERNS`); a freeze must not rely on the guard.
* **N5** No fail-closed on pointwise-empty intersection; narrowest at s = 0; reviewer synthetic case accepted with
  P_tpt = 0.1205. Freeze must refuse if max(capLo, lo(0)) > min(capHi, hi(0)).
* **N6** No exact-rational contract (float Env4 accepted; P_tpt returned as float).
* **N7** H_K1 must be H_final (everything the consumer intersects: R2, AD/deflated, T-EXT C1/C2, TC-T); penalty_frozen
  uses mag(H), equal to consumed M_k only when M_k = mag(H_final); bind H_K1 := H_final and assert M_k.
* **N8** Independence weaker than stated: V4 is in the same module; V3 builds `tpt.CellProfile` from tc_reder's terms,
  so the profile/P* agreement shares input derivation; only external check is the s = ρ reproduction (136/136), A's
  taken as given; no real ground truth for the s-profile.
* **N9** Provenance drift: V3 report cites sha256 `9d497ef1…` (r0, `af4365aa`), JSON records `8a17dd1e…` (r1,
  `48392744`), HEAD `77c1646e…` (`ccc4ea36`). Pin one hash, regenerate all.
* **N10** Floor r2 `fail_closed[3]` citation inapt (it is the chosen-supply restriction); operative anchor is
  `quantity_compared.adoption_quantity` + `fail_closed[2]`; conclusion correct. ROUTE_AUDIT_R1.md:42 uses the same
  inapt index.
* **N11** Chain clause: γ_k uses Γ_k; a consumer must state whether γ_k consumes Γ_TPT; for γ_k only g(x_k) needed →
  I_right(ρ) suffices. On the tail only the direct clause is the adoption quantity, but frozen `k5b_literal` evaluates
  both.
* **N12** Cells 305/306 not addressed: 306 closed under I1's supply, not certified under I2's, with Γ(5, 306; S_I2) =
  [TAIL-NUMBER REDACTED] sealed once (adverse). Floor r2 F1′(d) needs Γ < 0 under EACH supply, so a penalty-lowering
  consumer is foreseeably the lever that would flip that clause → a TPT evaluation at 306 would be designed knowing
  the adverse I2 result (result-chasing HIGH for 306). 305 adopted under r1, not re-adjudicable. Route must state 305
  OUT and decide 306 prospectively.
* **N13** TPT-G premise "all coefficients ≥ 0" includes c ≥ 0 (data-dependent sign premise); precise c on the right is
  −W_lo − Σ_r (Ĥ_r,lo − rad_r(0))/m; finite-ρ ratios confirmed.
* **N14** G10 undetermined prospectively: only non-target real evidence 0.7–2.5 % of the penalty; any claim of material
  tail value goes through the B1 proxy.
* **N15** Novelty: TPT not in C5's 14-route ledger; B2 needs g at sub-midpoints (TPT keeps one midpoint); D3 needs R'''
  (TPT needs none); C5 lists the third-input transport as unexcluded. Genuinely new; but its third input is a finer
  reading of the same premises (cannot exceed what they imply; TPT-O).
* **N16** TPT-B sound; reviewer synthetic overlapping non-monotone blocks: P*_B = 0.189725 ≥ dense lower running sup
  0.189705, < cell-max TPT 0.215165. Validation k_i bounded over [0, e_hi], so "negligible gain" is fixture-specific;
  at the tail blocks would come from REGISTRY_C2 sub-blocks (quarantined path). Correctly not ranked.
* **N17** Minor: fixed 60-bit `_crossing` (sound, slightly loose); `evaluate` raises AssertionError — a freeze should
  turn every such branch into a recorded refusal; retroactively logged V3 prototype runs — exactly-once design must
  log before execution.

### Reviewer runs (synthetic only)
* A1: P_tpt and P_c5t of all 12 committed V1 fixtures reproduced exactly.
* A2: transport-level controls on 12 fixtures: θ 0.99 → 2/12, 0.95 → 4/12, 0.9 → 5/12, 0.5 → 11/12; M1 (no centre
  motion) 3/12; M2 (t sign) 6/12; M3 (no Env4) 2/12; M4 (radius at s/2) 4/12; true_excess_lower/P 0.338…0.998.
* A3: 576 evaluations (plain / cap / W × m ∈ {1,2,3,5}, e0 ∈ {1/8,1/4,1/2}, ρ/e0 ∈ {1/8,1/4,1/2,3/4}); UNSOUND_by_truth
  0; certified_sound 576/576; P ≥ exact 200-bit lower bracket 576; dense running sup ≤ P 576; 192 cap variants all with
  interior split both sides; min P_tpt/P_c5t 0.262 (large gains when ρ/x0 large).
* B probes: B1 translation (whole_cell_enclosure equal under e0 shift, I_right/I_left affine exact); B2 float accepted;
  B3 empty intersection not refused (P_tpt 0.1205033); B4 TPT-B non-monotone blocks (above); B5 guard tests PASS.
* r0 discrimination: r0 tpt.py fails G1–G4 (`TPT GUARD TESTS FAIL`).

### X. What the reviewer could not check
Anything at the tail (by design): whether the TC-T/C2 per-r inputs reproduce the committed 𝓗_5, whether H_final = 𝓗_5
there, whether M_k = mag(H_final) there; frozen tct_rule/deflated_consume/c2_d5_forecast (read only); real-data
soundness of the s-profile; Lemma G/Dv′, Arb rounding, W construction (taken as adopted); graph-row authorship; P₊
and Env4(s) refinement (not implemented); concurrent IDEA_ADLR (not reviewed).

### Path to ACCEPTED_FOR_FREEZE_PREPARATION (review's list)
1. B1 (a)–(d). 2. B2 and B3 repaired and re-run against one pinned hash (N9), coverage stated. 3. N4–N7 as enforced
refusals with truth-relative tests. 4. Written freeze design for B4 (frozen-path extraction, coefficient-level + s = ρ
reproduction gate, decoy qualification on manufactured TC-T inputs, exactly-once) and an explicit 305-out / 306
decision (N12). 5. A user instruction for a floor extension (U3) before freezing, since closure-only under r2.

## 11. What was repaired in r2 (mapping review item → repair)

| review item | r2 repair (where) |
|---|---|
| B1(a) graph row | retracted; recorded as incident 01 (`ledger/INCIDENT_01_TPT_GRAPH_PROXY.md`); TPT tail application BLOCKED (PROXY_EXPOSURE) for this campaign (THEOREM_TPT status, TPT-G correction) |
| B1(b) "was not done" | corrected: "At campaign level it was done" (TPT-G correction paragraph) |
| B1(c) provenance | provenance disclosure paragraph in §0 |
| B1(d) user ruling | moved to FREEZE_DESIGN §0 precondition 1 (disclosure) + U3 |
| B2 tautological/non-transport controls | V1 r1 control WITHDRAWN (marked in JSON); `validate_tpt_r2.py` code-path pointwise plant + θ·P + mutants M2/M4/M5; TPT-B B4 replaced by code-path λ-scaled block constants; r1 TPT-B control withdrawn |
| B3 V2 never run | V2 implemented in `validate_tpt_r2.py` with a certified truth cap; P₊ stated "theory only, not implemented, never needed for record-based inputs" |
| B4 no freeze design | `FREEZE_DESIGN_TPT_TAIL.md` (design only; not frozen/authorized) |
| N1 | TPT-O now "supremum", attained only in the relaxed (measurable R'') class |
| N2, N3 | Lemma TC-P proof restated precisely; TC-P described as new lemma, not certified by TC |
| N4 | geometry guard declared defence in depth only (THEOREM_TPT §2, tpt.py docstring) |
| N5, N6, N7 | `check_nonempty` at s = 0; `_check_types` exact rationals; H_K1 := consumed H_final, `M_consumed` check (tests G6–G8) |
| N8 | V4 labelled not independent |
| N9 | tpt.py pinned `05cebc9c…`; V1/r2/V2/V3/TPT-B regenerated against r2 (V3 ratio range regenerated 0.975–0.993) |
| N10 | anchor changed to `adoption_quantity` + `fail_closed[2]` |
| N11 | chain clause noted as not implemented |
| N12 | 305 OUT, 306 OUT (prospective) |
| N13 | TPT-G premise c ≥ 0 and precise c made explicit |
| N14 | G10 "undetermined prospectively" |
| T-series from V3 (earlier, r1) | T1 guard on every public function; T2 label/terms/geometry binding; T3 non-binding-side split; T4 lower-sum bracket, interval validation |
| Erratum TPT-E1 | "orders of magnitude" claim corrected (regime-dependent; lower front 0.94–0.97) |
