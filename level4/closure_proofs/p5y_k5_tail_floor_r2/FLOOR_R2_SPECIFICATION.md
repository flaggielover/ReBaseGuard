# K5 tail adoption floor r2 — replacement of limb F1 after N9 closure

**Status:** PROPOSED at its own commit; in force (frozen, prospective) only once a fresh read-only review
returns `REPLACEMENT_FLOOR_ACCEPTED` and that review is preserved in its own commit.
**Nature:** governance and protocol design only. Nothing was recomputed: no Γ, no atom constant, no margin,
no operator constant; cell 306 was not re-run, re-compared or adopted; cells 307–309 were not touched; r5 is
unchanged and authoritative; r6 does not exist; K5 is PARTIAL.

Machine-readable rule: `config/K5_TAIL_ADOPTION_FLOOR_R2.json`. Cell-306 gate: `config/CELL306_ADOPTION_GATE_R2.json`.
Both are written by `code/floor_r2_build.py` and carry a self-verifying `sha256`. `code/floor_r2_verify.py` checks
every quotation below against its source blob, the bound blobs and commits, the hashes, the governance state and
the leak scans, with negative controls for each detector (`evidence/FLOOR_R2_VERIFY.json`).

## 1. The frozen language (audit)

All quotations are verbatim up to line wrapping and markdown blockquote markers; "…" marks an elision. The verifier
extracts every quotation in this document and checks each piece against the sources at their bound blobs.

| # | question | frozen text | source |
|---|---|---|---|
| 1 | the old floor and F1 | *"A pair (m, k) may be adopted only if the frozen K5-B certifies it (Γ < 0 under the campaign's own frozen closure rule) **and at least one of**:"* F1 — *"Γ < 0 also holds under a certified atom-constant supply that does **not** depend on the Arb/FLINT supersolution operator registry — i.e. under Lemma G …"*; F2 — *"Γ < 0 still holds when every atom constant of the chosen supply is degraded uniformly in the unfavourable direction by the factor **×1.25**"* | C2 adjudication §K (blob `cfc5b3ed`) |
| 2 | when F1 lapses | *"This limb is available for as long as **N9** (no second, independently written certifier of the operator constants) remains open, and lapses when N9 is closed."* | C2 §K |
| 3 | what N9 closure unlocks | *"a **second, independently written certifier** reproducing the six operator constants for cell 306 (closing N9), at which point the registry-dependence objection is answered and a successor should freeze a replacement floor requiring agreement between two independent certifier implementations rather than F1"* (first of three discharge routes for 306). C10 classes this sentence as corroborating, with Condition 1 as the primary authority. | C2 §K; C10 README Q2 (blob `6e0e70a9`) |
| 4 | freeze before recomputation | Condition 1: *"**The floor above is now the standard** for K5 m = 5 tail adoptions, prospectively. A successor that wishes to replace it must freeze the replacement **before** recomputing any magnitude"*. C10: *"A future successor **may** freeze a different prospective adoption rule without retroactively altering C2"*, and *"What it may **not** do is re-adjudicate 305 or 306 under a new rule, or apply its own"* rule to an adoption already made. | C2 Conditions; C10 README, C10_GOVERNANCE.json (blob `bc3fb1e6`) |
| 5 | two independent implementations | the §K sentence of row 3. The purpose: *"The open risk is N9: a possible systematic error in a single implementation of the Arb supersolution machinery … What does protect against it is a second, structurally independent route"*. C10: an alternative must *"answer IMPLEMENTATION INDEPENDENCE, not merely add margin"*. C2's own standard of independence: re-running the same certifier *"is a re-execution with different inputs, not an independent check"*. | C2 §K; C10_GOVERNANCE Q2_phase9; C2 `phase_d/CELL_306_ADOPTION.md` (blob `f5db4cd9`) |

The consumer these rules speak about:
* Γ is computed by the frozen K5-B path through TC-T.
* The atom constants come from the six operator constants by Lemma Dv′ r2 (THEOREM_AD §4, blob `586ecc6d`): *"A0 = Ā_eff, A1 = Ā_eff (κ₁C + δ₁), A2 = Ā_eff (2κ₁²C² + κ₂C + 2κ₁Cδ₁ + 2δ₁² + δ₂), Ā_eff := min(Ā, τ/D_lo)"*.
* C2 combines supplies by its D4 rule: *"A_j := min over valid supplies, componentwise"*.
* This is the chain that wrote C2's committed Γ: `c2_d5_forecast.py` (blob `18403dbe`), `deflated_consume.py` (`a0a836fa`), `tct_rule.py` (`98f6eee4`).

## 2. The old limb F1 after N9 closure

**F1 has LAPSED**, by its own frozen condition. N9 is CLOSED, by the accepted adjudication `7d67989d` (review
`fb237288`). F1 may not be used for any adoption decided by a campaign frozen after that.

* **The whole limb lapses.** N9 as worded concerns cell 306 only, but F1's availability is conditioned on N9's
  status, not on a cell. A lapse only removes a route to adoption, so it fails safe. The N9 adjudication itself
  applied the lapse to no cell, and no adoption is decided here.
* **The lapse is not retroactive.** C2's adoption of cell 305 under r1 stands, and no historical verdict is
  re-adjudicated.
* **The rest of r1 survives.** Its base clause and limb F2 do not lapse; r2 carries them over.

**r2 is not a re-adjudication of 306.** C10 defines the forbidden retroactivity: it *"would mean re-adjudicating
305 or 306 under a new rule, which is the thing that is forbidden"*. On whether a future campaign may target 306,
C10's answer is *"YES, prospectively"*, for a campaign that freezes its own gate before its own result. C2 §K says
a deferred cell *"is recomputed next cycle at no compute cost, with its refined registry intact, under a floor frozen
in advance"*. So C2's historical deferral of 306 stands. A future decision on 306 under r2 is a new, prospective
decision by a separately instructed campaign.

## 3. The rule

> **K5 tail adoption floor (r2).** A pair (m = 5, k) may be adopted only if the frozen K5-B certifies it — Γ < 0 under
> the campaign's own frozen closure rule, evaluated on the campaign's **chosen supply** — **and at least one of** F1′ or F2.
>
> **Chosen-supply restriction.** The chosen supply (used by the base clause and by F2) is a **single-implementation**
> supply. It is the componentwise minimum (C2's D4 rule) over registry-free Lemma G and Lemma Dv′ r2 applied to
> constant sets produced by **one** operator-constant implementation. It never combines constants or atom constants
> of two different implementations, and it is frozen before any evaluation.
>
> **F1′ — two-implementation agreement.** For cell k, all four of the following hold:
>
> * (a) two operator-constant certifier implementations I1 and I2, independent as defined in §7, have each
>   certified the six operator constants C_T, τ, Ā, D_lo, D1, D2 of cell k on the cell's whole drift block;
> * (b) the two sets were compared under the frozen N9 rule, with every constant AGREES or STRONGER and every
>   statement EQUIVALENT or STRONGER, in an independently reviewed and accepted comparison;
> * (c) each implementation carries the soundness evidence of §6;
> * (d) **Γ(5, k; S_I) < 0 holds for EACH of I1 and I2 separately.**
>
> **F2 — degradation survival (r1, verbatim).** Γ < 0 still holds when every atom constant of the chosen supply is
> degraded uniformly in the unfavourable direction by the factor ×1.25, i.e. the cell's uniform-A margin is ≥ 1.25.

**Why F1′ answers N9.** Suppose either implementation carries a systematic error of unknown size. Then the other
implementation's own supply still certifies closure, and it is valid provided that implementation is sound. So an
adoption under F1′ is correct **whenever at least one of the two implementations is sound**: it tolerates a fault
in either one. It neither requires nor infers that any particular one is sound.

**Why the chosen supply may not mix implementations.** C2's "componentwise best" of two constant sets is valid only
if both sources are sound. Across two implementations, that is exactly the assumption the floor exists not to make.
Mixing would let a much stronger constant from one implementation, such as a D2 bound, enter the base or F2
evaluation without the other implementation closing. So r2 forbids it everywhere. Cross-implementation evidence
enters **only** through F1′, where each implementation must close on its own.

## 4. What exactly is compared

* **Adoption quantity.** Γ(5, k; S) is the exact rational that C2's frozen consumer path computes for pair (5, k)
  with atom constants S, with every other input unchanged. The criterion is **Γ < 0, strictly**; Γ = 0 or an
  incomplete evaluation fails.
* **Supplies.** S_I is the componentwise minimum of (A0, A1, A2) over {Lemma G} ∪ {Lemma Dv′ r2 applied to each
  six-constant set of cell k certified by implementation I}.
  * Each set is used as certified. No operator-level recombination of sets (the D′ mixed-operator supply of C2
    Condition 3 / N7) is part of S_I.
  * For I1 at cell 306, S_I1 is exactly C2's adopted supply {G, C1, C2} (`c2_d5_forecast.combine`).
  * κ₁ and κ₂ are the consumer's own frozen constants (`deflated_consume.K1_BOUND`, `K2_BOUND`). They are the same
    for every supply and are outputs of neither implementation.
  * The consumer's own validation (τ ≥ 1, C ≥ τ, D_lo > 0, Ā ≥ 1) must hold for every set. Otherwise the set is
    invalid and the evaluation fails closed.
  * Every other consumer input is identical in both evaluations: the adopted K1 stack, the Lemma G inputs, the TC-T
    premises (zero order-3 candidate, σ3/σ4) and `cells.json`. Only the operator-constant sets differ.
* **Per-constant precondition.** The frozen N9 comparison rule (C11R statement table, unchanged in the C11RD
  freeze):
  * factor 2;
  * UPPER_BOUND: STRONGER if independent ≤ original, AGREES if original < independent ≤ 2 × original, else
    INSUFFICIENT;
  * LOWER_BOUND: mirrored;
  * an exactly equal value is INVALID;
  * same statement before same number.

## 5. Statement and domain compatibility; thresholds; STRONGER; asymmetric bounds

* **Statements and domains.**
  * Each constant is a certified statement, uniform in e, on a domain that contains the cell's whole block. A scalar
    drift or a strict sub-interval never qualifies.
  * Each implementation's six statements are EQUIVALENT or STRONGER to the frozen original statements: same
    constant, quantity, kernel (Khat_e atom-removed for C_T, τ, D_lo, D1, D2; K_e for Ā), direction, state set and
    proposition; premises the same or fewer.
  * Each set is consumed as C2's chain consumes a registry block: one six-constant set per source per cell, valid
    uniformly on the whole cell. C1's block is the cell; C2's sub-blocks are composed onto the cell inside its
    registry; I2's statements are whole-block.
* **Thresholds.** Per constant, the factor 2 (all six AGREES or STRONGER). For adoption there is no ratio threshold:
  only the sign of Γ under each implementation's own supply counts.
* **STRONGER.**
  * It is accepted as agreement for the per-constant precondition, per the frozen rule.
  * It **never substitutes**. A STRONGER constant is used only inside its own implementation's supply.
  * It is **not soundness evidence**: an unsound certifier also looks STRONGER on an upper bound. Soundness rests on
    §6, and F1′ is correct if either implementation is sound.
* **Asymmetric bounds.**
  * D_lo is the only lower bound (C11R's `why_the_asymmetry_matters`).
  * Each implementation's own D_lo enters its own supply, in the denominators of Lemma Dv′. The comparison applies
    the lower-bound rule to it. Nothing is mixed across implementations.
  * If two-sided information ever showed one implementation's upper bound below the other's lower bound, that is
    SCIENTIFIC_DISAGREEMENT (§8).

## 6. The two implementations and the evidence for each one's soundness

| | I1 — the original certifier | I2 — the independent line |
|---|---|---|
| implementation | `taboo_certify.py` (`certify_cell`), Arb/FLINT supersolutions; REGISTRY_C2 (blob `1a3adfd3`) and REGISTRY_C1 | C11R's certifier (C_T, τ, Ā, D_lo; sealed runs blob `a5351603`, seal `5ff4cc5b`) and C11RD's certifier (D1, D2; freeze `ce5b8595`, seal `4547bcd4`, runs sha256 `c28a8cea`). C11RD consumes C11R's accepted F_H certificate as a dependency. |
| soundness evidence | C2's two-pass re-certification of cell 306's 18 artifacts on a recorded host (bit-identical at 256 bits; safe-side domination at 384 bits); the C2 adjudicator's independent re-certification of five artifacts and exact re-derivation of Γ; six-constant agreement with I2 (N9 CLOSED) | C11R: pre-freeze R1–R8, qualification, authorization, EXECUTION_ACCEPTED (`22537709`), COMPARISON_ACCEPTED (`7375b9cd`); exact-rational whole-block certificates. C11RD: theory (Proposition 1, Lemmas 0–4 and 6, Theorem 5) READY_TO_QUALIFY (`3c1eff11`); validation 29/29, including V04, V13, V15, V22, V24 and V25; non-target rehearsal; QUALIFICATION_ACCEPTED (`e27c2ffd`); EXECUTION_ACCEPTED (`db1c6118`); COMPARISON_ACCEPTED (`90265349`), with an independent exact recomputation of every propagation; ADJUDICATION_ACCEPTED (`fb237288`) |
| residuals (disclosed) | **N10 remains OPEN** (the registry records no build host, toolchain or precision); never independently re-implemented before C11R/C11RD | the comparison cannot detect unsoundness in the STRONGER direction (review N2); independence is implementation-level, not authorship (N3); the propagation used **C_T = the exact supremum** of C11R's F_H weight (3429/500), about 3.7e-97 below C11R's outward-rounded C_T record (N1), which is sound and was frozen before the run |

**The I2 constants for cell 306** are bound by path, blob and field, and no value is restated here:
* C_T, τ, Ā, D_lo: C11R's accepted comparison (blob `5269c2aa`), `result.per_target[k].independent_value`. These are
  the values that comparison classified. C_T is the outward-rounded record, the conservative choice.
* D1, D2: `C11RD_COMPARISON.json` at `8e2defab`, `per_target[k].independent_value`, which equals the sealed runs'
  `targets[k].value`.

## 7. Independence

* **Required.** Implementation and code independence in the frozen C11R sense:
  * disjoint load-bearing import graphs: none of `taboo_certify`, `opnorms`, `intervals`, `fast_range`,
    `ra_certifier`, `resolvent_certificate`, `rebaseguard_certify`, `rung3_engine`, `spec`, `numpy` or `flint` on
    the independent path;
  * no consumption of the other implementation's outputs as premises (C11R `DEPENDENCY_FINDING`);
  * dependencies inside one implementation are allowed (C11RD on C11R).

  Re-executing one certifier on new inputs or another host is **not** independence (C2).
* **Not claimed.** Independent authorship.
* **Disclosed.**
  * I2 shares an author lineage with the programme.
  * I2's author had seen the original D1/D2 values before C11RD's freeze (`docs/C11RD_INDEPENDENCE_AUDIT.md`).
  * Certified bounds do not depend on authorship.
* **Common-mode residual.** Both implementations certify statements of the same frozen model, kernel definition and
  derivative theory, and both evaluations share Lemma G and the consumer. An error there is common-mode, and it is
  outside what F1′ (or N9) protects against.

## 8. Disagreement and fail-closed behaviour

* **Per-constant disagreement.** Any constant INSUFFICIENT, INVALID or DISAGREES, any statement not EQUIVALENT or
  STRONGER, or any independence violation makes F1′ **unavailable** for that cell.
* **Closure disagreement.** Γ < 0 under one implementation's supply and Γ ≥ 0 under the other's means **F1′ fails**
  for that cell. The disagreement is recorded, and there is no adoption under F1′. F2 may still be evaluated on its
  frozen single-implementation supply.
* **Contradiction** between two-sided certificates is SCIENTIFIC_DISAGREEMENT. That cell cannot be adopted under any
  limb until a separate adjudication resolves it.
* **After any disagreement,** there is no re-evaluation, parameter change or supply change in the same campaign.
* **Fail closed:**
  * an unbound, altered or unreviewed input;
  * a consumer validation failure;
  * an incomplete Γ;
  * a control that does not reproduce C2's committed Γ_exact on S_I1;
  * a chosen supply that mixes implementations;
  * neither limb established.

  In every one of these cases: **DO NOT ADOPT**, and the cell stays OPEN.

## 9. Scope, closure versus adoption

* **Scope.**
  * **Standing floor.** Under C2 Condition 1, r2 replaces r1 prospectively as the standing floor for K5 m = 5 tail
    adoptions decided by campaigns frozen after r2 is in force. It changes no past adoption.
  * F1′ is available only for a cell with its own two-implementation evidence. At freeze, only cell 306 has it.
  * **Operative scope of this campaign: cell 306 only.** The gate and the future adoption criterion concern cell 306
    and nothing else.
* **Cells 307–309 are out of scope.** No independent certification of their constants exists. r2:
  * authorizes no work on them and computes nothing for them;
  * sets no gate or criterion for them;
  * does not extend F1′ to them;
  * says nothing about their closure or adoptability.

  Any future campaign concerning them needs its own instruction. Under C2 Condition 1, it must freeze any further
  replacement before recomputing.
* **Scientific closure** is Γ < 0 under the frozen K5-B clause: a fact about a cell.
* **Adoption** is a governance decision, requiring all of:
  * closure;
  * F1′ or F2;
  * a complete prospective chain: freeze before evaluation, qualification, one sealed evaluation, independent
    reviews, and an adjudication that applies r2.

  Only that adjudication's chain generates a coverage map.
* **N9_CLOSED** is a trust condition on the constants. It is neither closure nor adoption, and it does not close K5.

## 10. The future cell-306 adoption criterion

**The chosen supply for cell 306 is fixed here**, so that no supply can be chosen after seeing a value. It is
**S_I1 = C2's adopted supply**: the componentwise minimum over Lemma G and Lemma Dv′ r2 of the I1 registries.

**Adopt (m = 5, k = 306) if and only if**, in a separately instructed campaign frozen before any evaluation:
1. Γ(5, 306; S_I1) < 0 is reproduced exactly as C2's committed `Gamma_exact`
   (`p5y_k5_tail_c2_closure/evidence/phase_d5/C2_D5_FORECAST.json`, blob `a191557f`, `cells['306'].Gamma_exact`).
   This is the control.
2. Γ(5, 306; S_I2) < 0, evaluated **once** and sealed (F1′). Alternatively, F2 holds on S_I1.
   * C2 published that F2 does not hold on S_I1, and this rule does not revisit that.
   * A campaign that re-evaluates F2 must bind C2's F2 procedure in its freeze. It stops if its result differs from
     C2's published classification.
3. Every item G00–G14 of `config/CELL306_ADOPTION_GATE_R2.json` passes.
4. An independent adjudication applies r2.

Otherwise cell 306 is **not adopted** and stays open. This rule does not predict, estimate or imply whether
Γ(5, 306; S_I2) < 0.

**The gate, G00–G14:**
* G00: floor r2 in force.
* G01: N9 CLOSED.
* G02: the governance entry state.
* G03: a prospective freeze of every input, the consumer, the supplies and the decision table, **before** any Γ
  involving an I2 constant is computed.
* G04–G05: the I1 and I2 input bindings.
* G06: all six AGREES or STRONGER.
* G07: soundness evidence and the disclosed residuals.
* G08: no mixing of implementations.
* G09: consumer validation and κ.
* G10: the S_I1 control, exact.
* G11: one sealed S_I2 evaluation.
* G12: the decision table.
* G13: independent execution review and adoption adjudication; only that chain may create r6.
* G14: cells 307–309 and r5 untouched.

## 11. Statement: no post-N9 adoption magnitude was inspected

No Γ, atom constant, uniform-A margin or F2 value was computed, estimated or inspected for any supply that contains
a C11R or C11RD constant. That holds before this freeze and while writing it. `REGISTRY_C2.json` and
`C2_D5_FORECAST.json` were bound by blob id only and not opened.

What the designer had seen, and discloses:
* the historical, pre-N9 published figures in the C2 adjudication, C2's `CELL_306_ADOPTION.md` and C10;
* the N9 comparison classes and ratios of the six constants.

The rule depends on none of those numbers. Its supplies mirror C2's adopted construction, with I1's registry
replaced by I2's constant set. Its thresholds are r1's and the frozen N9 rule's.
