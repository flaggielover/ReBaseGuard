# Erratum E4 to readiness matrix R4 (Cell-308 Cloud route r1): external B3 recorded; T6 dependency order corrected

**Status: CURRENT STATE RECORD · NOTHING ACCEPTED OR DECIDED.** This erratum amends `READINESS_MATRIX_R4_20261016.md`
together with errata E1–E3 (`READINESS_MATRIX_R4_ERRATUM_E3_20261016.md`, `57fccc52…0398`). All are preserved
unchanged. Where they differ, this erratum governs.

Sources:
* external B3 (`reviews/external/REVIEW_EXTERNAL_B3_PROVENANCE.md`, `16188ffd…e96a`; receipt
  `OWNER_RELEASE_B3_20261016.md`);
* `T6_TRANSFER_DISPOSITION_20261016.md`.

`new_target_evaluations = 0` · `cell309_activity = none`.

## E4.1 — Rows replaced, and rows added

| row | kind | state now | requires | change |
|---|---|---|---|---|
| A6 (B3) | EXT | **DONE, as advice.** `PROVENANCE: TRACED_WITH_FREE_CHOICE` as qualified; `T6_TRANSFER: TRANSFERS_UNMET`; Y5 BLOCKING, Y1–Y4 and Y6 MAJOR, Y7–Y8 NOTE. Eligibility: no concrete disqualifier within the available evidence; full-register status and isolation **UNVERIFIED** | — | — |
| A9 (bounded corrections of B2 / B3 findings) | TEXT | **PC** (this round): recommendations erratum E1; package erratum E2; the provenance record; the T6 disposition; ER-T6; this erratum; register erratum E4; owner package erratum E1 | A6 | — |
| **A9c (new)** | EXT (text) | **BLOCKED: the owner forwards the confirmation package** to the same B3 conversation | A9 | B3's **single** confirmation. No further round. A confirmation of text is not VC unless the owner accepts B3's standing |
| **A14a (new)** | EXT | **BLOCKED: owner commissioning** | — | ER-T6: a permitted reader checks the role holders R1–R6 against the E1″ register (`EVIDENCE_REQUEST_ER_T6_ROLE_HOLDER_CHECK_20261016.md`). It runs in parallel with A9c |
| A14 (**T6 ruling**) | OD | BLOCKED | A6, A9, **A9c**, **A14a** | **Scope corrected (K-T6-1):** A14 rules on (1) no automatic historical transfer, (2) T6 and S13 applying unamended, (3) role-holder status per ER-T6, and (4) optionally a **new** prospective safeguard package. It does **not** rule on M3's satisfaction, and it never records M1–M8 as met |
| A15 (adoption of the texts) | OD | BLOCKED | (as before) **plus A14a: no HOLDER, and no CANNOT_TELL, on R1–R3** | (K-T6-4) |
| A17 (D-*, set-asides, N1, N2) | OD | BLOCKED | A6, **A9c**, A14, A15 | N1 and N2 are adopted with recommendations erratum E1's choices in view, not "as derived" |
| **B9-T (new)** | EXT | BLOCKED | B8 | an M1-style trace of every **code-level** constant the successor build introduces, done at the implementation review by a non-holder (K-T6-2). Any untraced code constant blocks B10 |
| B10 (L-DET interpreter build) | OPS | BLOCKED | (as before) **plus B9-T** | — |
| **C1-M3 (new; CONDITIONAL on A14 item 4)** | EXT, OPS | CONDITIONAL | C1 | if the owner adopts the prospective package: a non-holder confirms or replaces the memory-cap rule, headroom, exclusivity and allow-list from the official non-holder decoys, before C4 (K-T6-1) |
| C4 (pre-freeze decision) | OD | BLOCKED | (as before) **plus C1-M3, if it was adopted** | — |

## E4.2 — The order

**B2 → B3 → bounded corrections → B3 confirmation and ER-T6 → owner T6 ruling → adoption and D-* → OD-1 → inventory.**

B3's confirmation (A9c) and ER-T6 (A14a) are independent of each other. Both precede the T6 ruling.

## E4.3 — Unchanged

* `T1_ON_PLATFORM_CHANGE: CANNOT_TELL`, and the floor, not lower than HIGH.
* The machine-wide veto.
* Every other row.
* No row marks OPS, IT or AX. No row marks any historical T6 mitigation as satisfied.
