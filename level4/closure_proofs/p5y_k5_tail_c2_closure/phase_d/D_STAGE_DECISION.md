# Campaign C2, D stage — result, class and decision

Gate frozen and pushed at `87309610` (sha256 `098dd7f5…`) before any C2 number existed. Guard **DENY**;
**NEW_REAL_ADDRESSES = 0**; 2.69 CPU-h of deterministic operator certification, none of it new-real.

## 1. Result

`evidence/phase_d5/C2_D5_FORECAST.json`. Atom constants are the gate's **pre-registered componentwise minimum** over
three valid certified supplies (Lemma G generic, Lemma Dv′ from C1's one-block-per-cell registry, Lemma Dv′ from C2's
refined sub-block registry), with provenance recorded per cell and per field.

| cell | magnitude | M needed | Γ | margin | required uniform A-reduction | gap | **gap fall vs baseline** | materially tightened (≥ 20 %) |
|---|---|---|---|---|---|---|---|---|
| 305 | 3.615110 | 4.891579 | **−0.088029** | **1.353×** | 1.000 | 0.000 | — | **CLOSES** |
| 306 | 3.511946 | 3.905056 | **−0.030469** | **1.112×** | 1.000 | 0.000 | — | **CLOSES** |
| 307 | 3.451359 | 3.076148 | +0.033133 | 0.891× | 1.140764 | 0.1408 | **46.29 %** | yes |
| 308 | 3.452456 | 2.432398 | +0.102700 | 0.705× | 1.500288 | 0.5003 | **24.59 %** | yes |
| 309 | 3.400934 | 1.969828 | +0.162249 | 0.579× | 1.899015 | 0.8990 | **18.39 %** | **no** |

No previously passing cell regresses; m = 1, 2, 3 remain complete on 0–309; no TC-T intersection is empty.

    D_STAGE_CLASS = D_PARTIAL
    closed        = {305, 306}
    still open    = {307, 308, 309}

**D_USEFUL fails on one cell by 1.6 percentage points.** It requires every still-open cell to be materially
tightened; 307 and 308 clear the frozen 20 % threshold comfortably, 309 reaches 18.39 %. The threshold was frozen
before any of these numbers existed and is not adjusted now.

## 2. What the refinement actually bought

The D2/D3 refinement (sub-blocks ≤ 1/100, denominator certified per sub-block, worst taken over the cover):

| cell | D_lo | D1 | D2 | τ | C_T |
|---|---|---|---|---|---|
| 305 | 0.768609 → **0.821410** | 1.618684 → **0.520713** | 28.5065 → **6.2573** | 5.291155 → 5.391442 | 6.028953 → 6.197599 |
| 309 | 0.848046 → **0.907807** | 1.284353 → **0.274845** | 19.3360 → **3.1019** | 4.418493 → 4.517254 | 4.705512 → 4.842907 |

D2 improved 4.6–6.2×, D1 3.1–4.7×, D_lo about 7 % — **but τ and C_T got 2–3 % worse.** A narrower block does not
automatically admit a tighter supersolution: the degree-20 candidate is driven by the same α ladder on a different
interval, and the worst sub-block can exceed the single wide-block bound. C2 reports this rather than presenting the
refinement as uniformly favourable. The net on A0 = τ/D_lo is still a 4.5–4.9 % gain, because the D_lo gain
outweighs the τ loss.

Phase D1's elasticities explain why the result is modest despite the large D2 win: A0 carries 0.63 of the magnitude
response, A1 0.165, A2 0.022. The 46 % improvement in A2 is worth about 1 % of magnitude; the 4.5 % improvement in
A0 is worth about 2.8 %.

**The pre-registered combination rule changed nothing.** C2's supply is the minimum on all three fields of all five
cells, so the componentwise minimum reduced to "use C2". Two selector mutants in the adversarial suite are recorded
as *equivalent* for exactly this reason. Pre-registering the rule was still right — had C2's τ regression been larger
than its D_lo gain, Lemma G or C1 would have been selected for A0 and the rule would have been load-bearing.

## 3. Robustness and the thin cell (supplementary; not gate inputs)

`evidence/phase_d5/C2_ROBUSTNESS_AND_R_ATTRIBUTION.json`. The C2 gate defines no degradation scenario; these figures
are recorded because Campaign C1's reviewer was right to ask for them.

| cell | Γ | margin | Γ with every constant × 1.25 | survives |
|---|---|---|---|---|
| 305 | −0.088029 | 1.353× | −0.033733 | yes |
| 306 | −0.030469 | 1.112× | +0.029163 | no |

**Cell 306's margin is now 11.2 %, against 1.9 % under C1.** That is the direct answer to the C1 pre-freeze
reviewer's objection — it recommended not adopting 306 without an independent re-certification of its operator
constants and a pre-frozen margin floor. C2 re-certified those constants from scratch on a finer partition, and the
margin rose sixfold. It still does not survive a 25 % degradation, and that is stated rather than buried.

## 4. Decision, under the rule frozen before the forecast

The gate's `D_stage_decision_rule` for `D_PARTIAL` says, verbatim:

> ADOPT THE CLOSED SUBSET ANYWAY, and in the same campaign produce the R-stage design for the remainder. … an
> adopted cell is permanent progress that costs no new real compute and removes that cell from every future
> campaign's universe, whereas declining to adopt it preserves nothing and has twice already left a soundly closed
> cell 305 unadopted. Adoption and R-stage design are therefore NOT exclusive.

So C2 proceeds to freeze, qualification, seal, consumption and independent adjudication for the **closed subset
{305, 306}**, and produces the R-stage design for {307, 308, 309} in `phase_r/`. No real scientific address is
evaluated in either activity; the R stage may not execute until its own sub-gate, review, qualification and
authorization exist, with N1 closed first.

This is the rule that exists because the programme has now computed a sound closure of cell 305 three times — under
Campaign B's Lemma G constants, under C1's Lemma Dv′ constants, and again here — and adopted it none of those times.

## 5. R-stage eligibility

Both conditions the gate pre-registered are satisfied:

- **(a)** the D stage does not close all five cells — 307, 308 and 309 remain open;
- **(b)** the residual is order-3-attributable on every still-open cell. Recomputed under C2's own constants: with
  f_G at its `eps_src[3]` floor the magnitudes fall to 1.131 / 1.174 / 1.200 and Γ becomes −0.1718 / −0.1267 /
  −0.0873, so every one of them closes.

The design in `phase_r/` must model a *real* candidate, not a perfect one. Under C2's constants the critical ratio —
the largest certified order-3 candidate supremum, as a multiple of the measured order-2 supremum, at which a real
candidate still closes each cell — is **37.32 (307), 23.26 (308), 14.16 (309)**, against 32.03 / 19.20 / 10.55 under
C1's constants and an adopted lower-front value of 34.8–80.5. C2's deterministic work has therefore moved the R
stage from implausible toward borderline, and cell 307 is now at the edge of the adopted range rather than far below
it.
