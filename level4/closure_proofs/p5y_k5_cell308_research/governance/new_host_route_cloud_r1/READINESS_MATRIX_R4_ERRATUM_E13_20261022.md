# Erratum E13 to readiness matrix R4 (Cell-308 Cloud route r1): owner decision E-5 and the new A6c row

**Status: CURRENT STATE RECORD · MECHANICAL STATUS UPDATE.** This erratum amends `READINESS_MATRIX_R4_20261016.md`
together with errata E1–E12. All are preserved unchanged. Where they differ, this erratum governs.
`new_target_evaluations = 0` · `cell309_activity = none`.

**Sources:**
* `OWNER_DECISION_E5_A14B_CONSEQUENCE_OPTION_A_20261022.md` (`1ad2509d…6121`, commit `4f814796`) and its receipt;
* `A6C_APPOINTMENT_HANDOFF_20261022.md`;
* the brief `ledger/briefs/A6C_REDERIVATION_CLOUD_R1.txt` (`489dec78…2f0c`).

| row | kind | state now | requires | note |
|---|---|---|---|---|
| A14b | OD | **CONSEQUENCE DECIDED** (E-5, option (a)) | — | Rows R1a, R1b, R2, R3a–R3c and R6a stay UNRESOLVED, with no HOLDER finding. Covered-function outputs of R1a, R2 and R3a are **not adoptable** before independent re-derivation or confirmation. The no-cure rule is preserved |
| A6b | EXT | unchanged from E12: complete, **input only** | — | adopted nothing |
| **A6c (new)** | EXT | **BLOCKED: owner launch and appointment** | E-5; the brief and handoff (prepared) | independent re-derivation or confirmation by an eligible non-holder outside the coordinator's reach, of scope S1–S11. **S4 (the L-DET reference list) only if A16 stays in scope.** Steps: appointment → Phase 1 → A14b row for the candidate → owner determination → proceed instruction → Phase 2 → receipt |
| A15 | OD | BLOCKED | (as E5) **plus A6c** | no affected text is adopted before A6c's result is recorded, and before the owner decides item by item |
| A16 | OD | BLOCKED | (as R4) **plus A6c Part D, if A16 is pursued** | FR1's earlier re-derivation (L-DET erratum E1 §5) does not satisfy E-5 |
| A17 | OD | BLOCKED | (as E5) **plus A6c** | — |
| YC1 | — | BLOCKING (unchanged) | A6b (done, input only), A6c | — |

**Order (replaces E7.2 from A6b onward):**

**A6b trace (done; input only) → E-5 (done) → A6c appointment → Phase 1 → A6c determination → proceed → A6c Phase 2
→ receipt → T6 ruling item 3 → statement 2 (adoption, item by item) → OD-1 → inventory.**

* Statements 1, 1B and 1A stay open, and may issue in parallel.
* S12-Q (GC-5) stays open before any freeze.

**Unchanged:**
* every other row;
* C-1 to C-5 remain unresolved;
* `T6_TRANSFER: TRANSFERS_UNMET`;
* no host, implementation, caps, qualification, L-DET, decoy, freeze, OD-3, S1, marker or formal-run gate is passed.
