# K5 overnight route registry: cells 306–309

**Scope of this registry.**
* Route states only. **CLOSED is never used for a route.**
* Numbers are not repeated here; each row points to the evidence.
* Under floor r2, every route that changes the consumer or its non-constant inputs, or that supplies constants other
  than Lemma G or Lemma Dv′ r2, is **closure-only**. Adoption would need a user-decided floor extension, frozen before
  any evaluation (U3).
* **U1:** certifying host. **U2:** P3 admissibility of new quantities derived from tail K1 records. **U3:** floor
  extension.

## Assembly (stream E)

| route | cells potentially relevant | prospective motivation | theory status | implementation status | non-target validation | governance status | blocker | next action |
|---|---|---|---|---|---|---|---|---|
| **TPT**: Taylor-profile transport (`streams/E_assembly/THEOREM_TPT.md`) | 307–309. 305 and 306 are OUT, decided prospectively. | The whole-cell radius is charged at every t of the transport. The route is outside C5's exhausted two-input family. | Sound. Review R1 re-derived it. | `tpt.py` r2 (05cebc9c) | V1, r2 controls, V2 cap path, V3 136/136 lower-front | **BLOCKED (PROXY_EXPOSURE, incident 01)** for tail use in this campaign; closure-only | incident 01 (G8 at campaign level); U3 | A future disclosed campaign per `FREEZE_DESIGN_TPT_TAIL.md` |
| TPT-B: block-resolved profile | 307–309 | Worst-case sub-block constants are used simultaneously. | Sound | IMPLEMENTED | VALIDATED_NON_TARGET: 24/24; gain negligible on the fixtures | closure-only | low value | None; a remark only |
| Corollary-T g_hi (atom-functional midpoint eps) | all | AD Corollary T is not applied on the tail. | Existing adopted theorem | not implemented | — | closure-only | small by structure (∝ midpoint residuals) | Inventory only |

## Operator level (streams C1, C2)

| route | cells | motivation | theory | implementation | non-target validation | governance | blocker | next action |
|---|---|---|---|---|---|---|---|---|
| **RLR**: regenerative likelihood-ratio atom constants (`streams/C_308/LR/THEOREM_LR.md`) | 307 (A1, A2 blocker per committed C3/C4); 308, 309 as components | The positive-kernel and quotient bounds discard the sign cancellation of K₁ and K₂. | LR-1…LR-4, RLR (LR-3) proved (self-checked) | FSM (`lr_fsm.py`); **real CUSUM kernel (C1b): certified end to end at the declared drifts e ∈ {0, 1/4, 1/2, 1, 3} and on the block [1/2, 17/32]**, exact arithmetic | FSM 24/24; real kernel: Dv′ recomputed from the same certified inputs is larger at every declared drift (C1B_*.json); controls detected, with one design-error control preserved and replaced | closure-only; host-free (stdlib) | independent review (REVIEW_RLR_R1, running); U3 | Review, then a freeze as a certifier on a pre-registered block |
| Plain LR | as RLR | as RLR | proved | FSM | 24/24 | closure-only | loses to Dv′ asymptotically | Only as one more term in the minimum |
| **Theorem M**: E_a[τ] even and nonincreasing in \|e\| (`streams/C_308/A0X/EXCLUSION_308.md` §c) | 308 (exclusion); all cells structurally | Settles C4's caveat on where the sup lies. | **VALIDATED_NON_TARGET**: review ACCEPTED_WITH_CORRECTIONS, corrections C1, C2 and N3 applied, residues completed in ef6d8846 | non-target numerics by the reviewer | yes | general lemma. Its transfer implications are fenced by amendment 2. | — | Cite in any future exclusion protocol |
| X308 refutation (single-drift certificate at e_lo) | 308 (exclusion only; zero closure leverage) | Replaces uncertified MC intuition by proof. | THEORY_ONLY | draft protocol only | — | DRAFT, not authorized; must disclose incidents 02 and 03 (§0a of the draft) | P2–P5 of the draft; in-band computation needs user authorization | User decision; low priority (zero leverage) |
| X308 proof route | 308 | — | C4 route L and R4 **REFUTED** as proof routes | — | — | — | — | — |
| **C2b strategy**: tight supersolution generator (`streams/C_308/A0X/gen/STRATEGY.md`) | any block (A0, τ, C_T) | A cell-independent operator-tuple strategy (brief §17), replacing the first-rung α-ladder rule. | proved lemmas; block floor Ā ≥ Λ* ≥ sup Λ | IMPLEMENTED (exact) | pointwise 30/30 certified; blocks; controls | closure-only (a third implementation; no D_lo, D1, D2) | independent review of STRATEGY §5.3 | Review, then freeze as a certifier |

## Higher order (stream B)

| route | cells | motivation | theory | implementation | validation | governance | blocker | next action |
|---|---|---|---|---|---|---|---|---|
| R1: real order-3 candidate | 307–309 | The surrogate is a norm-only bound on a signed point value; RO3-S/F/E. | THEORY_ONLY (propositions checked on fixtures) | lower-front comparison only | fixtures; lower front: enclosure narrows 4.42–9.35× (the pure-tower σ3 baseline favours R1) | **BLOCKED**: new real addresses, guard DENY, N1/N5/N7 open | governance and host | A separately governed R-stage |
| R2: ADLR (atom-direct LR Taylor) | 307–309 | Avoids A0 × whole-function sups. | valid | fixtures | valid but **incomparable**; much looser with the certifiable constants | BLOCKED | needs certified Λ₃ and Λ₄ | None now (negative result) |
| R3: Hermite tower for σ3/σ4 | 307–309 | Leibniz tower slack | THEORY_ONLY | — | — | — | G6, G9 | Research |
| R4: joint (unsplit) residual | 307–309 | Triangle inequality over r | — | — | — | BLOCKED | pointwise residuals never serialized | — |

## Cell 309 (stream D)

| route | cells | motivation | theory | implementation | validation | governance | blocker | next action |
|---|---|---|---|---|---|---|---|---|
| SC: composite-sup theorem | 307–309 | The surrogate's slack is exactly the Leibniz gap, which is strictly positive. | proved | IMPLEMENTED (centred Taylor-form certified sup) | VALIDATED_NON_TARGET (FSM; Hermite closed form on the real kernel at declared drifts) | closure-only; **data-blocked** | candidate payloads were never serialized (U1, U2) | A host plus an admissibility ruling |
| Real cover refinement | 309 and others | Order-j slack removal of 1 − 1/N^j | proved | IMPLEMENTED (algebra) | FSM | **BLOCKED** (new K1 records) | U1 plus governance | DRP-0 (result-free, certified slack coefficient) is ready; DRP-1 is outcome-adaptive (review D) |
| Refinement without new records (C5 route B2) | — | — | within the fixed-(g_hi, L, U) family it equals TPT (an implementation identity, not validation evidence; review D B3) | — | — | **REFUTED within the fixed-input family only** (review D B2) | — | — |
| B2c: re-certifying constants on sub-segments without new records | 307–309 | a separate lever not covered by the B2 refutation | THEORY_ONLY | — | — | not evaluated | — | research |
| RSO: residual-specific order-0 | 307–309 | The order-0 bound is sharp only at f ≡ 1. | proved; the order-2 score form is THEORY_ONLY | IMPLEMENTED | FSM | closure-only; data-blocked | pointwise residuals | Combine with SC |

## Cell 306 (stream A)

| route | cells | motivation | theory | implementation | validation | governance | blocker | next action |
|---|---|---|---|---|---|---|---|---|
| Theorem CV: two-verifier common certificate | general (306 motivating) | separates certificate search from verification | proved; covers 4 of the 6 constants (no D1/D2 kind) | two stdlib verifiers (V_A exact, V_B directed decimal) | **IMPLEMENTED, qualification needed** (global review F5/F11): 7 valid, 9 planted, 1 discrimination check at [3, 49/16]; the D upper bound is vacuous; no distinct taboo lower certificate | **blocked for 306**: 306-c/d/g, ROUTE_AUDIT_R1 §5 | governance; qualification | General trust infrastructure |
| Certified bracketing (sub- and supersolutions) | general | makes "STRONGER" claims refutable | proved | implemented | **IMPLEMENTED** (downgraded after global review F11: its earlier "validated" rested on class (c)/(d) controls; intervals are about 46 % wide at the validation block) | blocked at 306 (in-band) | qualification; the band | — |
| p-dependent candidate families for I2 | 306 | removes I2's p-flat slack (Proposition PF) | THEORY_ONLY | — | non-target mechanism study | **INVALID_RESULT_CHASING at 306**: designed knowing the sealed adverse I2 result | G1 at 306 | none for 306 |
| Harmonising the D statements | 306 | — | — | — | — | REFUTED as a value lever (cosmetic) | G10 | — |
