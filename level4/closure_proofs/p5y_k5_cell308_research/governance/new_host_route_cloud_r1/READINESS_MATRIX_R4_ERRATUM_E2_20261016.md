# Erratum E2 to readiness matrix R4 (Cell-308 Cloud route r1): B2's reading and the missing M1–M6

**Status: CURRENT STATE RECORD · NOTHING ACCEPTED OR DECIDED.** This erratum amends `READINESS_MATRIX_R4_20261016.md`
(`82782289…7414`) together with its erratum E1 (`READINESS_MATRIX_R4_ERRATUM_E1_20261016.md`, `316475d0…6cc6`). Both
are preserved unchanged. Where they differ, this erratum governs. Its source is the B2 reading
(`reviews/external/READING_EXTERNAL_B2_INCIDENT_REVIEW.md`, `201aa5af…f9b2`; receipt `OWNER_RELEASE_B2_20261016.md`).
`new_target_evaluations = 0` · `cell309_activity = none`.

## E2.1 — Rows replaced, and one row added

| row | change |
|---|---|
| A5 (B2 reading) | **DONE.** Recorded verbatim, with 0 tail-figure hits. N1–N4, T1–T6 and the Q4 premises are quoted. Both amendment quotation comparisons are **MATCH**. `T1_ON_PLATFORM_CHANGE: CANNOT_TELL`. **M1–M6 NOT EXTRACTABLE** |
| **A5s (new)** | B2 supplement: M1–M6 extracted by the **original B2 reader** from the one added source the owner authorized. Kind: EXT. State: **BLOCKED** (owner-authorized; awaiting the owner's release with its sha256). Authority: O authorizes and releases; the B2 reader extracts. The coordinator side never reads that source |
| A6 (B3) | May start after A5 (now DONE), under brief r2 with handoff addendum A2 §2. Task items 1, 1a and 2 do not wait. **Task item 3 (T6 transfer) requires A5s.** Without A5s, B3 records "NOT ASSESSED", which is not a T6 finding |
| A9 (bounded corrections of B2 / B3 findings) | Requires A5, A6 and A5s |
| A14 (**T6 transfer ruling**) | Requires A5, **A5s**, A6 (with task item 3 assessed on the actual M1–M6) and A9. The prerequisite is **not discharged** until then |
| A17 (**D-* decisions**) | Unchanged in its dependencies (A6, A14, A15). It therefore waits on A5s through A14 |

## E2.2 — The T1 reading leaves the floor unchanged

* `T1_ON_PLATFORM_CHANGE: CANNOT_TELL` is recorded as it stands. It is not FIRED and not NOT_FIRED.
* The rating floor stays **not lower than HIGH** on trigger-independent accepted text (amendment erratum E2.3).
* No row may treat T1 as unfired.
* The S1 brief carries B2's T1–T6 quotations and this verdict (owner package R4 §6).

## E2.3 — Unchanged

* The order B2 → B3 → bounded corrections → T6 ruling → D-* adoption → OD-1 → inventory. A5s is part of the B2 step
  for the T6 ruling.
* Every other row.
