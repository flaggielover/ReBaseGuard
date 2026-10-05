# Owner return points, and the exact condition for OD-R2-0(D) (deliverable 9 of 10)

**Authority.**
- Owner message 5, OD-R2-0(D): "DEFER / REMAIN OPEN … This decision may be brought back to me only after all required
  pre-freeze prerequisites are satisfied and independently evidenced". Its sequence ends: "8. Return to me for
  OD-R2-0(D)".
- Owner message 6: "OD-R2-0(D) remains OPEN."

**Never early.** OD-R2-0(D) is never asked early. The intermediate returns below ask **other**, narrower decisions.
None of them asks for, implies or pre-empts OD-R2-0(D).

## 1. Return points

| point | trigger | what is brought to the owner | what it never asks |
|---|---|---|---|
| **R-0** (any time) | an INCIDENT: a target counter, a protected ref, a grant or result file; or any boundary breach | the facts and the evidence, at once | — |
| **R-1** | 8b-initial is issued (`HOST_CHANGES_REQUIRED`, `HOST_REJECTED` or a persistent `HOST_AUDIT_INCOMPLETE`) | (a) **OD-R2-4**, in the form of `OD_R2_4_HOST_CHANGE_PACKET.md` §5, with the exact current states from 8a; (b) **AF-1** with the evidence and the proposed amendment, only if 8b row B-12 fired; (c) **AF-2** with a minimal portability proposal, only if B-10 fired; (d) a host selection, only if the audited host is not the one message 3 names, or if it is rejected | OD-R2-0(D); a freeze; a grant |
| **R-1b** | 8b-final shows a further required change | the further OD-R2-4 items only | the same |
| **R-2** | the 8d drill is classified (PASS, FAIL, INTERRUPTED or a repeated NOT_STARTED) | (a) the classification with the validator output; (b) on PASS: a **filing authorization** for one separate, additive commit into r2 holding `evidence/drill/<stamp>/`, the one GOVERNANCE ledger row, the host evidence the owner chooses (the 8a audit, the 8b verdicts, the redacted cell-308 forms, `APPLIED_CHANGES`) and the owner's OD-R2-4 record, and, separately, permission to issue the pre-freeze review; (c) on anything but PASS: whether a further drill is authorized, after any host fix the failure needs | OD-R2-0(D) |
| **R-2b** | the pre-freeze review is ACCEPTED (with or without non-blocking follow-ups) | a filing authorization for one separate governance-only commit into r2 holding the review record (its `.md`, `.sha256` and execution ledger), unless R-2 already authorized it | OD-R2-0(D) |
| **R-3** | **every** condition of §2 holds | **OD-R2-0(D)**, together with the qualification-host confirmation that OD-R2-6(iii) requires | — |

## 2. The condition for R-3 (OD-R2-0(D)): all must hold, each independently evidenced

| # | condition | evidence that proves it |
|---|---|---|
| O-1 | the incorporated bytes are fixed: r2 contains `501f48cb` (SF1-A incorporated; `SF1: RESOLVED` for those bytes) | r2 `governance/R2_SF1A_INCORPORATION_RECORD.json`; message 6 |
| O-2 | **host accepted:** the 8b-final verdict is `HOST_ACCEPTED_FOR_WORKER_TIER`, recomputed by the pre-freeze reviewer (Q3) | `VERDICT_8B_final`; the review, Q3 |
| O-3 | **OD-R2-4 changes explicitly approved and applied:** every host change made was consented by the owner in writing (and by the cell-308 operator where host-wide) and applied exactly; none unconsented; the M4 holds restored after the window | the owner's OD-R2-4 record; `APPLIED_CHANGES`; the review, Q4 |
| O-4 | **8c complete:** the cell-308 forms A–D complete for the drill window; the window respected | the forms; the review, Q6 |
| O-5 | **worker-tier drill PASS** on `501f48cb` | `VALIDATION_8D` = PASS; E-1–E-5; the review, Q5 |
| O-6 | **pre-freeze review ACCEPTED**, with or without non-blocking follow-ups; no blocking condition left open | `REVIEW_PRE_FREEZE_501F48CB.md`, line 2 |
| O-7 | **all required governance records filed in r2,** each by its own authorized, separate, additive commit, verified from a fresh clone: the drill evidence and ledger row (R-2); the host evidence the owner chose (R-2); the OD-R2-4 record (R-2); the pre-freeze review record (R-2b). No earlier record edited | origin r2 at the final filing commit; a fresh-clone check that each commit only adds the authorized paths and that QC15 A1–A10 pass |
| O-8 | no open incident; no unreported interruption or retry | the review, Q8 and Q9 |
| O-9 | NEW Γ309 TARGET EVALUATIONS = 0; no grant; no protected ref; r5 unchanged; no r6; Cell 309 OPEN | the integrity count (ledgers and refs, locally and on origin), as in earlier records |
| O-10 | every other dependency the authoritative r2 governance packet names is either satisfied or listed for the owner as not blocking OD-R2-0(D), with the reviewer's classification | the review, Q10 |

**If any of O-1 to O-10 is not shown,** OD-R2-0(D) is not asked. The system returns at the matching point (R-1, R-2 or
R-2b) instead, or stays stopped.

## 3. The R-3 message (its form; it is sent only when §2 holds)

```text
P309-r2: OD-R2-0(D) may now be brought back (message 5).

r2 head <R2_FINAL> (drilled bytes 501f48cb; filings <list of commits>), verified from a fresh clone.
O-1 SF1 RESOLVED for 501f48cb ............................ <evidence>
O-2 host accepted (8b-final) .............................. <evidence>
O-3 OD-R2-4 changes consented and applied exactly ........ <evidence>
O-4 cell-308 coordination complete ........................ <evidence>
O-5 worker-tier drill PASS ................................ <evidence>
O-6 pre-freeze review <disposition> ...................... <evidence>
O-7 governance records filed ............................. <commits>
O-8 no incident / interruption / retry ................... <evidence>
O-9 integrity: 0 target evaluations, 0 grants, r5 unchanged, no r6, Cell 309 OPEN
O-10 remaining items, each marked blocking / not blocking: <list>

Decisions requested: OD-R2-0(D); with it, the qualification-host confirmation required by OD-R2-6(iii).
Nothing has been frozen, qualified, granted or evaluated. Gamma(309) remains forbidden.
```

## 4. What no return point authorizes by itself

Whatever the answer at R-1, R-1b, R-2 or R-2b, these remain forbidden until the owner explicitly authorizes them:
- a freeze, or the official qualification (`--mode official`), or the host re-run (`--mode host-rerun`);
- a grant (AF-4);
- any Γ309 or other target evaluation;
- adopting Cell 309, or a scientific-status change;
- modifying r5, or creating r6;
- touching cells 306–308.
