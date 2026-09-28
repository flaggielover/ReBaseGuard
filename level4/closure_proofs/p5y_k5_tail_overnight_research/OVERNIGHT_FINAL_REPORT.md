# K5 cells 306–309: overnight research campaign, morning handover

| cell | start state | end scientific state | best new result | freeze-ready? |
|---|---|---|---|---|
| 306 | OPEN / NOT ADOPTED (C12-R2) | OPEN / NOT ADOPTED, unchanged. The I1/I2 disagreement is now attributed at the level of statements and methods. | The disagreement is **implementation slack acting through the binding eff branch**: I1 binds on τ/D_lo, I2 on Ā. Proposition PF: I2's p-flat taboo family forces τ = C_T ≥ the whole-kernel ARL. Theorem CV, a two-verifier common certificate with certified bracketing, is IMPLEMENTED, qualification needed. | **No.** No legitimate 306 route exists under current governance (306-c/d/g). |
| 307 | OPEN | OPEN. The higher-order bottleneck is now characterised structurally. | **RLR atom constants**: a new theorem, certified on the real kernel at non-target drifts. Its supply is min(RLR, Dv′, Lemma G); RLR alone beats Dv′ only for exact ρ (REVIEW_RLR_R2). The A1/A2 slack is sign cancellation. The real order-3 object carries more information but is governance-blocked. | **Route level: YES, closure-only.** The RLR certifier (supply min(RLR, Dv′, Lemma G)) is FREEZE_READY, reviewed by R2 and R3. Its inactive protocol covers cell 307 only. Not freeze-ready for adoption, which needs U3. |
| 308 | OPEN | OPEN. The exclusion question is precisely posed and structurally settled as decidable. | **Theorem M**: E_a[τ] is even and nonincreasing in \| **No.** An A1/A2-only route cannot close 308 under the frozen consumer (committed C3 knockout). The exclusion protocol is a draft with zero closure leverage. | (reviewed and accepted with corrections). The operator-level RLR route, and the C2b tight certifier (reviewed and accepted with conditions). | **No.** The exclusion protocol is a draft only, with zero closure leverage. |
| 309 | OPEN (REFUTED WITHIN SCOPE for the uniform-A0 family) | OPEN | **SC composite-sup theorem**: the surrogate's slack is exactly the Leibniz gap. **TPT**, an assembly theorem that strictly dominates C5-T. **Cover refinement** is quantified: 1 − 1/N^j per order, and a split without new records gains 0 over TPT. **RSO** also validated. | **No.** SC and RSO are data-blocked. TPT's tail use is BLOCKED (incident 01). An A1/A2-only route cannot close 309 (committed C3 knockout). |

**Target integrity.**
* New Γ evaluations: **0 / 0 / 0 / 0**.
* Target-informed optimisation: **0**.
* Qualitative proxy exposures: **4**. These are incidents 01–03 plus a residue of 01. None computed a number. Each
  was caught by independent review, recorded, and retracted or blocked.
* Disclosed quarantine-rule breaches with no proxy content: **2**.

See §K.

---

## A. Repository

| item | value |
|---|---|
| worktree | `/Users/suzhe/ReBaseGuard-k5ov` |
| branch | `p5y-k5-tail-overnight-306-309`, **local only, not pushed** |
| start | base `8b9fc0bb` (the tip of `p5y-k5-tail-c11rd-d1d2-extension`) |
| charter commit | `6735d945` (02:32 +0900), before any science |
| end HEAD | the commit that adds this report (51 commits since base; `git log 8b9fc0bb..HEAD`) |
| commits | all additive, all inside `level4/closure_proofs/p5y_k5_tail_overnight_research/` |
| untouched | r5 (blob `f978eeb6`); no r6 on any ref; floor r2; C12-R2; the rejected closeout freezes and reviews; the exactly-once refs; main |

## B. Scientific work (theorems, proofs, implementations)

| id | object | status | where |
|---|---|---|---|
| TPT | Taylor-profile transport: the transport consumes the \|t−e0\| profile of theorem TC's radius (new Lemma TC-P). Dominates C5-T; sharp in its input family (supremum). Plus TPT-B (block-resolved). | theory sound (review R1); `tpt.py` r2 VALIDATED_NON_TARGET; **tail use BLOCKED** (incident 01) | `streams/E_assembly/` |
| LR / RLR | Score-martingale representation of ∂R and ∂²R at the atom. LR-3: with exact ρ the regenerative version is never worse than Dv′ on the same inputs; with certified ρ only min(RLR, Dv′, Lemma G) is guaranteed (REVIEW_RLR_R2). Plain LR is incomparable with Dv′. | theory (self-checked); FSM 24/24; real-kernel certificate at non-target drifts (C1b) | `streams/C_308/LR/` |
| Theorem M | E_a[τ](e) even and nonincreasing in \|e\|, from the atom and from diagonal starts. V-mask representation plus Anderson. | THEOREM_REVIEW ACCEPTED_WITH_CORRECTIONS (applied) | `streams/C_308/A0X/EXCLUSION_308.md` |
| C2b strategy | Cell-independent tight supersolution certifier: piecewise-linear triangulated family, fine α ladder, drift-through-y lemma, block floor Ā ≥ Λ* ≥ sup Λ | CERTIFIER_REVIEW ACCEPTED_WITH_CONDITIONS (C1–C5 before any freeze) | `streams/C_308/A0X/gen/` |
| SC | Composite-sup theorem for the order-3 surrogate; certified composite sup via a centred Taylor form | VALIDATED_NON_TARGET; review ACCEPTED_WITH_CONDITIONS, repaired | `streams/D_309/` |
| RSO | Residual-specific order-0, extended to derivative terms | as SC | `streams/D_309/` |
| Cover | Order-wise slack removal under refinement; result-free policy DRP-0 (DRP-1 is outcome-adaptive) | as SC | `streams/D_309/` |
| RO3-S/F/E | Structure of the order-3 surrogate versus a real candidate | propositions checked on fixtures | `streams/B_307/` |
| PF, CV | 306: p-flat families force τ = C_T ≥ the whole-kernel ARL; a two-verifier common certificate with certified bracketing | PF validated (float, non-target); CV IMPLEMENTED, qualification needed | `streams/A_306/` |
| Dependency graph | 34 nodes, primitives to Γ (md + producer JSON); a structural looseness inventory (r1, after the incident-01 retraction) | done | `graph/` |

## C. Cell 306

* **Current state:** OPEN / NOT ADOPTED (C12-R2 sealed Γ(S_I2) > 0; floor r2 F1′(d) fails). Unchanged.
* **Disagreement decomposition** (`streams/A_306/CELL306_I1_I2_DISAGREEMENT_AUDIT.md`):
  * 22 discrepancies classified.
  * Consumer and non-constant inputs are identical.
  * Five of six statements are equivalent; I2's D_lo statement is stronger (no premises).
  * Each supply's own A0/A1/A2 reproduces exactly from its own committed constants (sanctioned historical read).
  * **Verdict: IMPLEMENTATION_SLACK, acting through the binding eff branch.**
  * No defect was found; I2's D2 soundness is UNKNOWN (no refuting object exists).
* **Strongest surviving route:** none for 306.
  * Theorem CV and certified bracketing are general trust infrastructure. They are IMPLEMENTED at a non-target block,
    qualification needed (global review F5/F11).
  * They cover 4 of the 6 constants; the D upper bound is vacuous.
  * Applied to 306, every route falls into the accepted audit's 306-c/d/g classes. p-dependent I2 families are
    INVALID_RESULT_CHASING at 306.
* **FREEZE_READY:** no.

## D. Cell 307

* **Higher-order decomposition** (`streams/B_307/HIGHER_ORDER_AUDIT_307.md`):
  * The A1/A2 terms' certified orders exceed the true orders purely through discarded sign cancellation.
  * The order-3 surrogate is a norm-only bound on a signed point value.
* **Order-3 findings** (`REAL_ORDER3_THEORY.md`):
  * The real order-3 object carries strictly more information: on the lower front the enclosure narrows 4.42–9.35×
    (the pure-tower σ3 baseline favours the real candidate).
  * But it is **BLOCKED** by governance (new real addresses; guard DENY; N1/N5/N7).
  * ADLR, the atom-direct LR Taylor enclosure, is valid but incomparable (a negative result).
* **Strongest surviving route: RLR** (A1, A2), host-free.
  * Certified on the real kernel at non-target drifts.
  * Closure-only under floor r2.
* **RLR reviews:** R2 ACCEPTED_WITH_CONDITIONS, C1–C5 met; R3 CONFIRMED_WITH_NOTES. N3/N5/N2 were fixed afterwards and
  re-verified by the coordinator. The combined supply is min(RLR, Dv′, Lemma G); raw RLR beats Dv′ only for exact ρ.
* **Remaining gap:**
  * user decisions U3 and the incident disclosure;
  * the qualification package on decoys;
  * the single sealed evaluation under the inactive protocol `streams/C_308/LR/RLR_FREEZE_PROTOCOL_DRAFT.md`.
  * Optional, not affecting soundness: block cost at wider blocks and e-affine candidates.
* **FREEZE_READY:** **yes at route level, closure-only** (RLR certifier, cell 307). No for adoption.

## E. Cell 308

* **Operator-level findings:** RLR (as for 307); the C2b certifier.
  * A block-uniform Ā pays an intrinsic floor Λ*(E) ≥ sup Λ, for **any** single-supersolution certifier.
  * In C2b's blocks, the measured excess over that floor is proposal overhead.
* **Exclusion-theorem status:** X308 is precisely posed (a sup over the cell).
  * By Theorem M it is decidable by one certified computation at e_lo(308).
  * On certified evidence it is undecided, and it has zero closure leverage.
  * Route L and R4 are refuted as proof routes.
  * The protocol is a **DRAFT** (`FREEZE_308_EXCLUSION_PROTOCOL_DRAFT.md`). It must disclose incidents 02 and 03.
* **Strongest surviving route:** an A0-channel improvement combined with RLR at the operator level. RLR alone
  (A1/A2) cannot close 308 under the frozen consumer, by the committed C3 knockout. The C2b A0 certifier has open
  freeze conditions (C1–C5 of its review).
* **FREEZE_READY:** no.

## F. Cell 309

* **Scoped negative families** (`SCOPED_NEGATIVE_FAMILIES_309.md`): quoted with their exact scopes. The route list
  starts from them.
* **Sup-norm (SC):** genuinely stronger than the surrogate, not a relabelling.
  * The surrogate's slack is exactly the Leibniz gap, strictly positive for exact sups.
  * The certified composite sup is sound.
  * **Data-blocked:** the candidate payloads were never serialized (U1 host, U2 P3 admissibility).
* **Cover:** real refinement removes 1 − 1/N^j of the order-j slack. A split without new records gains exactly 0
  over TPT (an identity).
  * DRP-0 is result-free.
  * **BLOCKED:** needs new K1 records.
* **Residual-specific (RSO):** its gain is the occupation shape factor. It collapses into the refuted family for
  constant ψ. Data-blocked.
* **Assembly (TPT):** sound and dominant over C5-T, but **tail use BLOCKED** in this campaign (incident 01).
* **Strongest surviving route (structural ranking only):** SC combined with TPT, among routes needing no new real
  objects. Both are blocked, as above.
* **FREEZE_READY:** no.

## G. Routes killed

| route | reason |
|---|---|
| ADLR | Valid but incomparable, and much looser with certifiable constants. |
| Plain LR as a replacement for Dv′ | Loses asymptotically in bounded-C_T regimes (it survives as one more term in the minimum). |
| Refinement without new records | Identical to TPT. |
| Route B2 | REFUTED only within the fixed-(g_hi, L, U) family. B2c, re-certifying constants on sub-segments, remains THEORY_ONLY. |
| Harmonising the 306 D statements | Cosmetic. |
| X308 proof via route L / R4 | Their committed maxima are below the threshold. |
| p-dependent I2 families at 306 | INVALID_RESULT_CHASING. |
| TPT-B | Sound but negligible; not a route. |
| Corollary-T g_hi | Small by structure; inventory only. |

## H. Routes surviving (all closure-only under floor r2)

RLR (operator), C2b certifier (operator), Theorem M (structural), SC/RSO (data-blocked), real refinement and real
order-3 (governance-blocked), TPT (blocked for tail use this campaign), Theorem CV (trust infrastructure).
See `registry/K5_OVERNIGHT_ROUTE_REGISTRY.md` and `registry/CROSS_ROUTE_THEOREM_COMPARISON.md`.

## I. Independent reviews (all preserved verbatim in `reviews/`)

| review | verdict | blockers → disposition |
|---|---|---|
| REVIEW_TPT_R1 | **NOT_READY** | B1 implicit tail proxy → incident 01, route tail use BLOCKED. B2 tautological controls, B3 V2 never run → repaired (r2). B4 tail path → design only. |
| REVIEW_THEOREM_M_R1 | **ACCEPTED_WITH_CORRECTIONS** | C1, C2, N3 applied. N4 → incident 02. N5 → amendment 2. |
| REVIEW_STREAM_D_R1 | **ACCEPTED_WITH_CONDITIONS** | B1 controls that cannot fail, B2 overreach, B3 identity → repaired. |
| REVIEW_C2B_STRATEGY_R1 | **ACCEPTED_WITH_CONDITIONS** | no blockers. Freeze conditions C1–C5 open. N2 → incident 03. |
| REVIEW_STREAM_D_R1 (repair verified by the global review) | see above | — |
| REVIEW_GLOBAL_INTEGRITY_R1 | **DEFECTS_FOUND** (all MEDIUM/LOW; governance clean; no new target quantity) | F1–F4: governance tools rebuilt. F5–F7: controls in streams A, B and C1a re-planted or withdrawn. F8: probe producer plus erratum. F9–F11: registry and cross-route corrected; R-CV and bracketing downgraded to IMPLEMENTED. F12: incident-02 residue re-worded. F13: incident-01 residue moved out of the graph. F14: amendment 3. F15–F18: errata E1–E8 and guards. A second global review was not run. |
| REVIEW_RLR_R1 | **INCOMPLETE**: the reviewer stalled twice. Preserved, NOT a verdict. | — |
| REVIEW_RLR_R2 (completion review) | **ACCEPTED_WITH_CONDITIONS** (no soundness blocker; 21/21 exact reproduction; all planted-invalid certificates rejected) | C1: "never worse than Dv′" is a theorem for exact ρ only → corrected everywhere. C2: min(RLR, Dv′, Lemma G) implemented in code, with a test that catches mutants. C3: block-path class-(a) controls added. C4: evidence regenerated with pinned hashes. C5: amendment 4. |
| REVIEW_RLR_R3_VERIFY (repair verification, incl. the new D13 coverage rule) | **CONFIRMED_WITH_NOTES** | D13 is sound: states with both arms positive have p+m ≤ 4, confirmed by exact walks. C1–C5 met. N5: the one-sided combined-supply test was made two-sided, and 4 too-small mutants are now caught (re-verified by the coordinator). N3: pre-pin evidence moved. N2: provenance added. |

## J. Compute

* **Local only:** a 6-core Mac, stdlib Python 3.14. No AWS, no Vultr, no installs.
* **Heaviest jobs:**
  * C2b exact certification: about 2–300 CPU-s per run, 48 runs, with float proposals up to about 190 s;
  * C1b certificates: minutes per drift, the block run 246 s;
  * TPT validations: under 2 min each;
  * stream B / D fixtures: minutes.
* **Wall time:** about 02:30–09:45 +0900, including two usage-limit pauses and one laptop sleep.
* **Ledger runs:** 242 lines. By class: HISTORICAL_READ 2, INFRASTRUCTURE 2, NONTARGET_DRIFT_VALIDATION 170, NONTARGET_REAL_VALIDATION 8, PROXY_EXPOSURE 4, QUARANTINE_RULE_BREACH 2, SYNTHETIC_VALIDATION 54.
* **Peak memory:** small; no job was memory-bound.
* **Ledger:** `ledger/ZERO_TARGET_LEDGER.jsonl` has one line per sensitive execution.

## K. Target-integrity ledger

| quantity | count |
|---|---|
| new Γ306 evaluations | **0** |
| new Γ307 evaluations | **0** |
| new Γ308 evaluations | **0** |
| new Γ309 evaluations | **0** |
| target-equivalent proxies | **4, all qualitative (prose or reasoning; no number computed), each caught by independent review** |
| quarantine-rule breaches without proxy content (disclosed) | **2** |
| target-informed optimisation runs | **0** |

The four proxy exposures and two rule breaches:
* **Incident 01**, by the coordinator: the dependency graph placed tail radius shares next to TPT-G factors.
  * Consequence: TPT's tail use is BLOCKED for this campaign.
* **Incident 02**, by stream C2a's first version: a cross-cell re-attribution of a committed 309 floor to 308.
  * Withdrawn.
* **Incident 03**, by the coordinator: the C2b brief defined a comparison scale derived from cell-308 figures.
  * Consequence: the comparison sentence must not be used.
* **Incident 01 residue**, found by the global review: the same graph co-located tail dominance shares with route
  factors elsewhere in the document.
  * The shares moved to a route-free history file.
* **Rule breach, incident 02 residue:** a cross-cell ceiling re-attribution (R2.4) with nil sign information.
  * Re-worded.
* **Rule breach found by stream A:** non-target values co-located with committed 306 numbers (R2.1).
  * Made qualitative.

The ledger has 242 lines: 0 target evaluations, 4 proxies and 6 LEAK_FLAG lines. Every LEAK_FLAG line has an
accounted incident class. `code/ov_audit.py` therefore reports FAIL, and says that it fails **solely** because of these
recorded incidents.

Quarantine amendments 1 and 2 (stricter only) were added as risks surfaced:
* a drift band;
* the Theorem M transfer policy.

The static scan (rebuilt after F3) passes: 56 files, 0 findings, 1 sanctioned historical-read file with its 3 lines
listed. Its multi-shape negative control fires. Nothing outside the namespace changed.

## L. Governance: what may legally happen next

* Nothing adopts. There is no r6; r5 is authoritative; K5 remains OPEN (PARTIAL).
* Every surviving route is **closure-only** under floor r2. Any adoption path needs a **user-decided floor extension
  frozen before any evaluation** (C2 Condition 1; route audit U3).
* Routes needing candidate payloads need the user decisions U1 (certifying host) and U2 (P3 admissibility).
* Real order-3 and real refinement need separately governed real computation.
* No protocol drafted tonight is active. Nothing in this campaign authorizes any target evaluation.
* The rejected closeout-freeze line (R2 rejected) is untouched and remains a separate governance track.

## M. Recommended next action

**One route is FREEZE_READY at route level, closure-only: the RLR atom-constant certifier, for cell 307.** Its
prospective protocol is drafted and **not activated**: `streams/C_308/LR/RLR_FREEZE_PROTOCOL_DRAFT.md`. Nothing else
is freeze-ready, and nothing is freeze-ready for adoption.

**1. Governance first (user decisions; nothing scientific can adopt without them).**
* Every surviving route is closure-only under floor r2.
* Decide U3: whether any closure-only route may ever lead to adoption through a floor extension. Such an extension
  must be frozen before any evaluation (C2 Condition 1). Without it, the best any route can deliver is scientific
  closure without adoption.
* Decide U1 and U2 (host; P3 admissibility) only if the data-blocked routes (SC, RSO) are to be pursued.

**2. Strongest scientifically defensible next campaign (host-free, closure-only unless U3 says otherwise).**
* **What:** two steps.
  * **Now (freeze-ready):** a prospectively frozen certification of cell 307's pre-registered sub-blocks with the
    combined supply **min(RLR, Dv′, Lemma G)** for A1 and A2. A0 stays C2's committed value. Then a single sealed Γ
    evaluation of cell 307 under the **existing frozen consumer**.
  * **Later, for 308 and 309:** the same pipeline with the C2b certifier for A0, τ and C_T, once C2b meets its
    conditions.
  * Not TPT: its tail use is blocked by incident 01.
* **Why this one:**
  * it attacks the structurally dominant slack of the atom constants, sign cancellation, with a reviewed theorem;
  * it needs no candidate payloads, no host and no new real K1 addresses;
  * its certificates run in exact stdlib arithmetic on this Mac.
* **Missing work, exactly:**
  * **RLR (cell 307):**
    * the user decides U3 (closure-only, or a pre-frozen floor extension) and acknowledges incidents 01–03;
    * then freeze the drafted protocol, qualify it on decoys, obtain an independent qualification review and a grant,
      and run the single sealed evaluation;
    * optional before the freeze: block cost at wider blocks, e-affine candidates, and a second implementation of the
      checker.
  * **For 308 and 309**, the A0 channel is also needed, through **C2b** and its review's C1–C5:
    * persist the exact W with a standalone verifier;
    * a deterministic stopping rule;
    * a governed execution path past the quarantine guard;
    * claim fixes;
    * an err-path control and full-coverage FD in the qualification.
    * The block proposal overhead (amendment r1, robust proposal) should be validated first.
  * **Cell set:** decided prospectively and disclosed.
    * 306 stays OUT (route audit 306-c/d/g).
    * 305 stays OUT.
    * 307 (and later 308–309) enter only with incidents 01–03 disclosed.
    * **Risk:** the committed per-cell factors are known, so this is a MEDIUM result-chasing risk that the authorizing
      user must weigh.
* **Cost:** local CPU; minutes to hours per block (C1b, C2b measurements). No AWS or Vultr.

**3. Research items that remain open, and why they are blocked.**
* **TPT tail use:** a future campaign may use it only with incident 01 disclosed and the design in
  `FREEZE_DESIGN_TPT_TAIL.md`.
* **SC composite sup and RSO:** blocked by U1 and U2 (candidate payloads).
* **Real refinement and real order-3:** blocked by separately governed new real computation.
* **X308 exclusion:** zero closure leverage. A draft protocol exists, and it must disclose incidents 02 and 03.
* **Theorem CV and certified bracketing:** general trust infrastructure; qualification needed.
* **306:** no legitimate route under current governance.

**4. Not recommended.**
* Any re-evaluation of 306.
* Any floor change decided after results.
* Any use of the committed "x-eff" factors to choose between the routes above. They were not used tonight either.
