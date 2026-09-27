# Theorem TPT — Taylor-profile transport for the K5-B direct clause (revision r2)

**Status after independent review R1** (`reviews/REVIEW_TPT_R1.md`, NOT_READY, preserved at 32413877) **and repair r2**:

| component | state |
|---|---|
| Theorem TPT, Corollaries TPT-M/P, Propositions TPT-D/O/G, Lemma TC-P, Theorem TPT-B | mathematics **sound** (review R1 §1, re-derived by the reviewer) |
| implementation `tpt.py` r2 (sha256 `05cebc9c…`) | **VALIDATED_NON_TARGET** on exact synthetic fixtures (V1, r2 controls, V2 cap path) and on the TC input path of 136 real lower-front pairs (V3) |
| application to CUSUM m = 5 cells 306–309 | **BLOCKED (PROXY_EXPOSURE, incident 01)**: fails G8 at campaign level; cannot become FREEZE_READY in this campaign (charter rule G1/G7/G8) |
| TC-T / C2 tail input path | **unvalidated by design**: its inputs exist only for the quarantined cells; see `FREEZE_DESIGN_TPT_TAIL.md` (design only, for a future disclosed campaign) |
| floor r2 | **closure-only** |

TPT has **never been evaluated on CUSUM m = 5 cells 305–309**.

## 0. Motivation, and its provenance

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
* Before designing TPT, the author knew the committed C5 decomposition of the tail radius. Its order-3 and order-4
  terms dominate, and its midpoint residual term is about 0.1 %. The r0 sentence reflected that knowledge.
* TPT's content is general and nothing in it is tuned. But the choice to develop it first was informed by committed
  tail structure.

The C5 adjudication (`p5y_k5_tail_c5_exhaustion/evidence/adjudication/C5_ADJUDICATION.md` §7–§9) scopes C5-T's
exhaustion to exactly two inputs (`g_hi` and a whole-cell `[H_lo, H_hi]`). It lists "a transport consuming a third
certified input … a midpoint or sub-cell enclosure of R''" as unexcluded.

TPT is neither C5 route B2 (split the cell) nor D3 (second-order transport, which needs R''') (review R1 N15). Its
third input is a finer reading of the same certified premises, not new information. TPT therefore cannot exceed what
those premises imply (TPT-O).

## 1. Transport theorem

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

## 2. Lemma TC-P (the third input)

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

**Correction per review R1 B1(b).** The r0 text said that combining this proposition with committed tail
decompositions "was not done". **At campaign level it was done.** The coordinator's dependency graph placed the
committed tail shares next to these factors (commit 4403f86f). It is retracted and recorded as incident 01, and TPT's
tail application is BLOCKED for this campaign.

## 2b. Theorem TPT-B (block-resolved profile)

Let each block's constants `(A0^b, A1^b, A2^b)` be valid on that block. Then Lemma TC-P holds pointwise with the
constants of the block containing t, because TC §4 step 3 is pointwise. Within one block the integrand is monotone,
so the running integral is quasi-convex on each piece. Hence

    P*_B = max(0, running integral at the piece ends),

which is exact. It satisfies `P*_B ≤ P*_TPT` whenever `A^b ≤ A^cell`.

The mathematics is sound (review R1 N16).

Validation r2 on 24 exact fixtures:

| check | result |
|---|---|
| pointwise violations | 0 |
| transport certified sound | 24/24 |
| dominance | 24/24 |
| code-path control | detected 24/24 |
| θ-controls, 1/2 / 9/10 / 99/100 | detected 22 / 10 / 4 |

The r1 control was a tautology and is withdrawn.

The gain on these fixtures is P*_B/P*_TPT ∈ [0.99896, 1]. That result is specific to these fixtures, whose k_i are
bounded over [0, e_hi], not per block. TPT-B is not ranked as a route.

## 3. What TPT changes, and its governance

| item | status |
|---|---|
| inputs | `g_hi`, the consumed whole-cell enclosure, W, A, `f_*`, Env4, ρ, cover: **unchanged** |
| TC / TC-T radius | used pointwise in t |
| consumer | **changed**: the direct clause is replaced by `g_hi + P*` |
| floor r2 | **closure-only**. The anchor is `quantity_compared.adoption_quantity` ("the frozen consumer path … with the atom constants S substituted and every other input unchanged"), with `fail_closed[2]`. The r0 citation of `fail_closed[3]` was inapt (N10). Adoption would need a floor extension frozen before any evaluation (C2 Condition 1; route audit U3). |
| chain clause (γ_k) | not in the adoption quantity. A consumer feeding γ_k would need only `g(x_k) ≤ g_hi + I_right(ρ)`, which is not implemented (N11). |
| cells 305 / 306 | **305 OUT**: adopted under r1 and not re-adjudicable. **306 OUT**, decided prospectively here: a TPT evaluation at 306 would be designed knowing the sealed adverse I2 result, which the route audit classes RESULT_CHASING_RISK / GOVERNANCE_BARRED (306-g). (N12) |
| G10 | **undetermined prospectively**. The only non-target real evidence gives 0.7–2.5 % of the penalty on the lower front, which is cosmetic there. Any claim of material tail value would go through the incident-01 proxy (N14). |

## 4. Validation record (pinned `tpt.py` r2, sha256 `05cebc9c…`)

| id | what | result | file |
|---|---|---|---|
| V1 | exact FSM fixtures: Lemma TC-P pointwise; transport certified sound (rigorous sup g, adaptive bisection) | 0 violations; 12/12 sound | `validation/TPT_SYNTHETIC.json` (its r1 negative control is marked WITHDRAWN inside the file) |
| r2 controls | code-path pointwise plant (A and \|G\| scaled so rad_poly is invalid); transport plants θ·P and mutants M2 (t sign), M4 (radius at s/2), M5 (Env4 dropped) | code path detected 12/12; transport θ = 1/2, 9/10, 99/100 detected 11, 5, 2; M2, M4, M5 detected 6, 4, 2; every control fires somewhere | `validation/TPT_R2_VALIDATION.json` |
| V2 | cap/split path with a rigorously **certified truth cap** (grid R'' ± (h/2)·B3) | 12/12 sound; 12/12 dominated by C5-T with the same cap; interior splits right 11/12, left 12/12 | `validation/TPT_R2_VALIDATION.json` |
| V3 | 136 real lower-front pairs, TC input path; independent TC re-derivation reproduces the committed H_TC exactly | gate 136/136; P_tpt/P_c5t 0.975–0.993 (regenerated against r2) | `validation/TPT_V3_LOWER_FRONT.json`, `v3/` |
| V4 | Riemann upper and lower sums against the closed form | bracket holds. Same module and same profile derivation, so this is **not** an independent implementation (N8). | same |
| guards | `test_tpt_guards.py` G1–G8 | pass on r2; G1–G5 fail on r0, G6–G8 on r1 | — |
| not done | the non-monotone P₊ path (unimplemented, theory only); the TC-T tail input path (quarantined; design only) | — | — |
