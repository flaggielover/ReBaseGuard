# Disposition of the Phase C strategy review (PASS_WITH_NOTES)

Every finding was handled before the T-EXT freeze. No T-EXT hull wider than x1 was evaluated before the freeze.

| finding | disposition | where |
|---|---|---|
| F1 widened-η qualification coverage | **Adopted.** Two new frozen manufactured families: wide slow-even (η·C_e0 up to 20) and small-determinant (slow even and odd modes, strong drift, dense η grid). Frozen gate: ≥ 100 RAN, max η·C_e0 ≥ 10.7, ≥ 3 with η·C_e0 ≥ 4, ≥ 2 graded with 0 < det ≤ 0.1, min graded det ≤ 0.06, ≥ 1 scalar-fallback case, 0 violations. Calibrated only on seed-disjoint DEV seeds (+900000 and +800000, both passing). The ee-cap regime (hulls 33–40) is stated as not fixture-covered: it is min of two valid bounds. | `transport_extension/code/text_fixtures.py`, TEXT_SPEC §4 |
| F2 piecewise transport | **Adopted** as the frozen channel Λ(k), with an additional −M3 floor. The single-hull value is reported for disclosure only. | TEXT_SPEC §2–3, `text_transport.channel` |
| F3 seal M2–M4 | **Adopted.** M2..M5 are exported for every hull. A second frozen consumption C2 tightens curvature with M2 on cells 0–40. M4 is sealed for later hybrid-anchor designs (no use now). | TEXT_SPEC §2–3, `text_consume.py` |
| F4 proof reason | **Adopted.** Proof rewritten rule-wise; monotonicity used only as a gate. | TEXT_SPEC §2, STRATEGY §1 |
| F5 P1 authority | **Adopted.** Split into P1a (L5: R only) and P1b (R2/R3 producer premises for the tower). | TEXT_SPEC §2 |
| F6 drift ≡ hull | **Adopted.** The wrapper refuses a drift different from η. Mutants TM01/TM02/TM03/TM05 are required gates. | `text_transport.tower` |
| F7 index symbols | **Adopted.** Λ(k) for the K1-indexed channel, L_{k+1} for the theorem object. CM01 (the unsound direction) is a required gate. | TEXT_SPEC notation |
| F8 anchors at a ≠ 0 | **Adopted.** Restated as UNFORECAST, with the hybrid route recorded. | STRATEGY §3, §4, §7; FRONT_BLOCKER §2 |
| F9 §8 number and mechanism | **Adopted.** 18–51× at cells 40–41 (10³× near cell 10); the cross-term mechanism; the order-≤ 1 counter-route recorded as not a route. | STRATEGY §8, FRONT_BLOCKER |
| F10 numeric/reference nits | **Adopted.** | OPEN_CELL_AUDIT §2, STRATEGY |
| F11 guard, ledger, sign-blind verdict | **Adopted.** `evaluate` refuses unless the protocol is committed, clean, FROZEN_PRE_RESULT and pin-exact (verified pre-freeze: refused). Added EVAL_LEDGER.jsonl, verdict QUALIFIED / NOT_QUALIFIED / VOID, and no rerun. | `text_transport.require_frozen`, `qualify_text.py` |
| F12 tail details | **Adopted.** Point binding is new code (REQUIRES_NEW_CODE_AND_QUALIFICATION); the consumer must check the cell-309 target gate; no adaptive refinement. | TAIL_DESIGN, STRATEGY §5, §9 |
| F13 relation to slot-1 | **Adopted.** Successor consumption; no amendment of the slot-1 result, its E6 output or its POSITIVE map. | TEXT_SPEC header, protocol `relation_to_slot1` |
