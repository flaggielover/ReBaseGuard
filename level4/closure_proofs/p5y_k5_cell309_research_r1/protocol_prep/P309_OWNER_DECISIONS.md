# P309: decisions reserved to the owner (rev. 2; none taken by the research campaign)

The research campaign has established only that the route is **FREEZE_READY** (independent review R2, phases A–D).
The candidate package was reviewed by independent package review R3 (see `reviews/`). Everything below is the owner's
to decide.

Until then:
* nothing is frozen;
* no grant exists;
* no exactly-once marker exists;
* no cell-309 target evaluation has taken place (NEW Γ309 TARGET EVALUATIONS = 0).

## Required before an actual freeze

| id | decision | notes |
|---|---|---|
| **P0-1 / G2** | Authorize a separate, closure-only, exactly-once formal campaign for cell 309 on route P309 package 1. The authorization covers new in-band Stage-1 computation over the drift hull Ew (the 2⁻¹⁰ outward hull of the cell, not only the cell) and the grant-scoped guard/verifier variants (protocol §7) | Freezing is itself a step of that campaign. Name the execution host (not the cell-308 machine while 308 is live). **Ew may overlap a neighbouring quarantined cell's drift range.** 309 Stage-1 material is bound to 309 and never reused for another cell |
| **Cell set** | Confirm the cell set {309}; 305–308 are excluded (protocol §1) | — |
| **G1** | Accept SRK's **MEDIUM-HIGH** motivation-provenance liability | Sources: incidents 309R1-01 and 309R1-02; programme-wide dominance knowledge; rule S's "BLOCKED-only" C4 threshold, set by an exposed coordinator |
| **G3** | Confirm RLR as the min-composed A1/A2 component, at liability **MEDIUM** (its knockout is known; it carries the cell-307 disclosures) | **Asymmetry to note:** RLR307 treated CERTIFICATION_FAILED as NOT_CLOSED, because there RLR was the whole route. The candidate protocol rev. 2 instead lets a Stage-1b failure **fall back to S_I1** (a valid min component, protocol §3), symmetric with the SRK fallback. Accept this, or require the RLR307 NOT_CLOSED rule |
| **U2** | Rule on U2, or confirm it is not triggered (P309 uses no P3-derived quantity) | Required before any Stage-1 freeze (R2) |
| **U3** | CLOSURE_ONLY (the default), or a frozen floor extension naming P309, before Stage 1 | The outcome table and grant schema are written for CLOSURE_ONLY. An extension would require revising them before the freeze |
| **Stage-1a failure mapping** | Accept protocol §2.5: non-CERTIFIED statuses, non-ACCEPT verdicts and exhaustion of the 48 CPU-h budget fall back to TC-T; **any exception gives EXECUTION_INDETERMINATE**. Or instead map exceptions to fallback | An exception after the marker consumes the target with no conclusion. A fallback spends the single evaluation without that SRK index. Either way, efficacy is at risk, never validity |
| **Incidents** | Acknowledge every disclosed incident and liability: overnight 01–03; 309R1-01; 309R1-02; **309R1-03** (an unsanctioned in-band verifier probe, refused at parse time, nothing evaluated, liability NONE); ERRATA **E-3** (unverifiable ordering of the early real-kernel probe); ERRATA **E-17(a)** (unrecorded pre-commit verifier self-test runs); the manifest-generator run that hashed two other campaigns' governance files (R3 N13) | Assessment in `ledger/INCIDENT_309R1_0*.md`, `reviews/REVIEW_SRK_R2.md` and `ERRATA.md` |
| **Efficacy** | Acknowledge that efficacy at 309 is unknown by design | Decoys stop at 33/32. If SRK does not certify at 309, the route falls back to TC-T. That is safe for validity, but spends the single evaluation |

## Required later, inside an authorized campaign

| id | decision |
|---|---|
| **Grant** | A **separate** owner decision to issue the grant, after `QUALIFICATION_ACCEPTED` (formal package §D) |
| **Push / merge** | Any push beyond the research branch, and any merge, including of the formal campaign's namespace, its refs and its eventual result |

## Optional

| id | decision | constraint |
|---|---|---|
| **SRK-T** | Reconsider the exclusion of the taboo form under rule S criterion C5 | Only before any 309 Stage-1 number exists. Requires the full declared taboo decoy family (ERRATA E-15), a certified D_lo path and a review |

## What the research campaign did NOT do (by design)

* No grant was issued, no marker was armed, and nothing was frozen.
* No Γ309 and no in-band quantity was computed.
* r5 was not modified, no r6 was created, no adoption was performed, and no K5/P5Y status changed.
* The cell-308 campaign was not touched in any way.
