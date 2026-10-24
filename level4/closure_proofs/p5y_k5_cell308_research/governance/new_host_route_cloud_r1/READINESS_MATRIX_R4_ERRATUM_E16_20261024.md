# Erratum RM-E16 to readiness matrix R4 (Cell-308 Cloud route r1): A6C-E15, sanitized input set S1 and manifest R2 adopted; the A6c row after candidate 5

**Status: CURRENT STATE RECORD · MECHANICAL STATUS UPDATE.** This erratum amends `READINESS_MATRIX_R4_20261016.md`
together with errata RM-E1 to RM-E15 (files `READINESS_MATRIX_R4_ERRATUM_E1` … `_E15`). All are preserved unchanged.
Where they differ, this erratum governs. `new_target_evaluations = 0` · `cell309_activity = none`.

**Naming.** Readiness-matrix errata carry the prefix "RM-". Brief errata carry the prefix "A6C-". So this erratum is
RM-E16 (file `READINESS_MATRIX_R4_ERRATUM_E16_20261024.md`). It is a different document from brief errata A6C-E14 and
A6C-E15.

**Sources:**
* `OWNER_DECISION_A6C_E15_ADOPTION_20261024.md`;
* `A6C_SANITIZED_INPUT_SET_S1_AUDIT_AND_PROTOCOL_PROPOSAL_20261024.md`;
* `A6C_CANDIDATE5_PHASE2_STOP_AND_ENTRY6_AUDIT_20261024.md`;
* `OWNER_DETERMINATION_A6C_CANDIDATE5_ELIGIBILITY_20261024.md`.

| row | kind | state now | requires | note |
|---|---|---|---|---|
| **A6c** | EXT | **BLOCKED: owner appointment of a new candidate** | E-5; the brief at `797248fc`, as amended by A6C-E14 (`cd2fb234`) and **A6C-E15** (`a2aff3cb`, `680b4d3e…d701`); **manifest R2** (`0c6c0a30`, `a1247013…07cf`), with sanitized input set **S1** (`90d12cef`) for entries 4, 6 and 7; the adopted B2 classification rule | candidate 5: Phase 2 stopped at entry 6 (B2-derived content); **permanently stopped**; no result; nothing adopted. Candidates 1–5 and the A6b External Candidate are declined (A6C-E15.7). Phase 1 fetches only the brief (A6C-E15.5). B2-derived incident-review material is OUT OF SCOPE (A6C-E15.3). Manifest R1 is no longer used. Part D / A16 stays NOT_IN_SCOPE. **No result exists; nothing adopted** |
| A14b | OD | unchanged: consequence decided (E-5, option (a)) | — | — |
| A15, A16, A17, YC1 | — | as RM-E14 | — | — |

**Order (amends RM-E15's order at the A6c steps):**

**A6c appointment of a new candidate (Phase 1: the brief only) → Phase 1 → A14b row for the candidate → owner
determination → proceed (A6C-E14, A6C-E15 and manifest R2 fetched and verified) → A6c Phase 2 → receipt → T6 ruling
item 3 → statement 2 (adoption, item by item) → OD-1 → inventory.**

**Open, for the owner:**
* how the adopted classification rule reaches the next candidate (decision record §3 N3);
* whether entry 24 line 115 is an explicit incident-review attribution under that rule (§3 N2).

**Unchanged:**
* every other row;
* statements 1, 1B and 1A stay open;
* S12-Q (GC-5) stays open before any freeze;
* C-1 to C-5 remain unresolved;
* `T6_TRANSFER: TRANSFERS_UNMET`;
* no host, implementation, caps, qualification, L-DET, decoy, freeze, OD-3, S1, marker or formal-run gate is passed.
