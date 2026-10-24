# Erratum E6 to readiness matrix R4 (Cell-308 Cloud route r1): ER-T6 lookup recorded; A14b prepared

**Status: CURRENT STATE RECORD · AUTHOR CORRECTION · NOTHING ACCEPTED OR DECIDED.** This erratum amends
`READINESS_MATRIX_R4_20261016.md` together with errata E1–E5 (`READINESS_MATRIX_R4_ERRATUM_E5_20261017.md`,
`0d8a129c…0067`). All are preserved unchanged. Where they differ, this erratum governs.

Sources:
* the ER-T6 report (`reviews/external/READING_EXTERNAL_ER_T6_ROLE_HOLDERS.md`, `e2bcb406…dcbc4`; receipt
  `OWNER_RELEASE_ER_T6_REPORT_20261017.md`);
* the owner's clarification record (`OWNER_CLARIFICATION_AND_ER_T6_ROUTING_CORRECTION_20261017.md`);
* the A14b evidence table (`A14B_ELIGIBILITY_EVIDENCE_TABLE_20261017.md`).

`new_target_evaluations = 0` · `cell309_activity = none`.

## E6.1 — Rows replaced

| row | kind | state now | requires | note |
|---|---|---|---|---|
| A14a (ER-T6) | EXT | **PROCEDURALLY COMPLETE.** The bounded lookup was performed by the owner-appointed dedicated reader, and the deliverable was received and recorded verbatim (hash MATCH, 0 tail-figure hits). Result: 24 rows CANNOT_TELL (plus R3c's two sublabels), 0 HOLDER, 0 NOT_LISTED | — | see E6.2 for what stays pending. **Not repeated.** No replacement reader |
| A14b (owner eligibility) | OD | **OPEN: BLOCKED ON OWNER AUTHORITY** (MA1–MA4 of the A14b table). The per-row facts are listed in that table | A14a (done, procedurally) | no accepted text supplies the criterion. Template: owner statement 4 (A14b table §5) |
| A6b (policy-provenance trace) | EXT | **BLOCKED** on A14b (MA1–MA2 for the appointee) and on an owner appointment | A14b | its handoff item "the step-1 register lookup run on them before they start" is replaced (handoff erratum E1 §E1.3). A lookup on a new name returns [K] CANNOT_TELL by construction. The MA2 standard decides instead |
| A14 (T6 ruling) | OD | BLOCKED | A9c (done), A14b; item 4 also needs A14p | items 1–2 may issue now (statement 1B). Item 3 needs A14b |

## E6.2 — A14a, kept in four layers

| layer | state |
|---|---|
| (a) receipt and integrity of the released artifact | **DONE**: `e2bcb40660129665ed1ad5b45b80e578168ed5904c4e12a17d3ee2f2f68dcbc4`, 16,213 bytes, MATCH |
| (b) completion of the bounded lookup | **DONE** as reported. It is not "incomplete" because its results are indeterminate |
| (c) any further acceptance or standing condition | **PENDING. No adopted acceptance criterion exists**: ER-T6 r2 is author-prepared. The owner's appointment governed. What remains is the owner's acceptance of the report as A14b evidence (MA4), given: <br>• Q5 UNVERIFIED, with the reader in the coordinator's environment `env_01GTgmTdDaUY28GtoGZVi3QY`; <br>• the register digest and blob were computed by the reader, with no independently supplied expected digest (Q2); <br>• the location list's containment in the register (L110–L124) is a report claim. <br>The request and governance bindings A–D are corroborated by the coordinator |
| (d) person-specific eligibility, and later adoption and execution gates | **OPEN** (A14b, A15, A17 and later rows). Nothing passes on the strength of (a)–(b) |

## E6.3 — The order (replaces E5.2)

**ER-T6 lookup (done) → owner statement 4: the A14b criterion, MA1–MA4, plus the owner's Q1 facts → A14b, applied
per row → A6b appointment and trace → T6 ruling → adoption and D-* → OD-1 → inventory.**

* Statement 1 (A3, A10) and statement 1B items 1–3 and 5 may issue at any time.
  * Statement 1B item 4's wording is out of date (owner package erratum E2 §E2.1). Replacement text is in handoff
    erratum E1 §E1.4.
* Statement 1A (material change) remains the owner's, with no verdict prepared.
* A14p remains conditional.

## E6.4 — Unchanged

* `T1_ON_PLATFORM_CHANGE: CANNOT_TELL`, and the floor, not lower than HIGH.
* `T6_TRANSFER: TRANSFERS_UNMET`. T6 applicability undecided.
* No OPS, IT or AX is reached.
* No L-DET, decoy, caps, qualification, freeze, OD-3, S1, marker or formal run is ready or authorized.
* Every other row.
