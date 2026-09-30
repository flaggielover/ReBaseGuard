# Owner decisions for P309 (VERBATIM; received 2026-09-30, session transcript timestamp 2026-09-30T01:38:50.164Z)

The text below is the owner's instruction, reproduced byte-for-byte from the session transcript between the two
`~~~` fences. sha256 of the fenced body (UTF-8, including the final newline): `bc4cdb4869f906cad78b91a7496320099bfb39d0d3f52566853b59541918992c`.
It is the **authority** for formal campaign p5y_k5_cell309_p309_r1. **It does NOT issue the target execution grant.**

~~~text
I have reviewed the repository state and the owner-decision package for
P309 package 1.

I now authorize the next formal-campaign stage for K5 cell 309, subject
to the decisions and hard boundaries below.

============================================================
OWNER DECISIONS — P309
============================================================

P0-1 / G2 — AUTHORIZED, WITH A SEPARATE LATER GRANT

Authorize creation of a separate closure-only, exactly-once formal
campaign:

    p5y_k5_cell309_p309_r1

using P309 package 1, candidate rev. 2b.

This authorization includes:

- the incident-independence review;
- FC1–FC6 preparation;
- construction of the grant-scoped guard/verifier variants;
- their target-free re-qualification;
- the formal freeze;
- qualification QC01–QC17 / Q01–Q17;
- independent qualification review;
- preparation of the final grant package.

IMPORTANT:

THIS AUTHORIZATION DOES NOT ISSUE THE TARGET EXECUTION GRANT.

Do not arm or consume an exactly-once marker.
Do not execute Stage 1 on the cell-309 target.
Do not compute Γ309 or any in-band target quantity.
Do not begin target execution.

After QUALIFICATION_ACCEPTED, stop and return to me for a separate
owner grant decision.

============================================================
CELL SET
============================================================

Authorized formal-campaign cell set:

    {309}

Cells 305, 306, 307 and 308 are excluded.

Any Stage-1 material generated for 309 is permanently bound to cell 309
and must never be reused as evidence for another cell, including any
neighbouring cell whose drift range overlaps Ew.

============================================================
EXECUTION HOST
============================================================

The formal campaign must remain isolated from cell 308.

Do not use the cell-308 machine, worktree, marker, process, evidence
namespace or execution environment while 308 is live.

You may prepare, qualify and freeze P309 in this isolated cloud
environment provided doing so cannot interfere with 308.

The eventual target-execution host must be explicitly recorded in the
grant and must satisfy the frozen host/runtime requirements.

============================================================
G1 — ACCEPTED
============================================================

I acknowledge and accept SRK's MEDIUM-HIGH motivation/provenance
liability as disclosed by the research campaign.

This includes the disclosed effects of:

- 309R1-01;
- 309R1-02;
- programme-wide dominance knowledge;
- the exposed rule-S coordinator threshold.

This acceptance does not permit concealment, reclassification or
removal of those disclosures.

They remain permanently visible in the formal campaign record.

============================================================
G3 — RLR CONFIRMED
============================================================

Confirm RLR as the min-composed A1/A2 component:

    S =
    (
        A0_I1,
        min(A1_I1, A1_RLR),
        min(A2_I1, A2_RLR)
    )

with the disclosed MEDIUM liability.

For P309, adopt the candidate rev. 2b Stage-1b failure semantics:

    RLR certification failure -> fallback to S_I1

NOT the cell-307 NOT_CLOSED rule.

Reason:

In cell 307, RLR constituted the closure route itself.

In P309, RLR is only a min-composed component of an independently valid
existing supply. Failure to certify the optional RLR improvement does
not invalidate S_I1.

This choice must be frozen prospectively and must not be changed after
any target information exists.

============================================================
U2 — NOT TRIGGERED
============================================================

Confirm that U2 is not triggered for P309 package 1 because the
authorized route uses no P3-derived quantity.

If the formal-campaign reconstruction discovers that this statement is
factually false, STOP before freeze and report the discrepancy.

Do not silently reinterpret U2.

============================================================
U3 — CLOSURE_ONLY
============================================================

Set:

    U3 = CLOSURE_ONLY

Do not create a floor extension.

P309 may establish scientific closure only.

It must not:

- modify floor r2;
- modify r5;
- create r6;
- adopt cell 309;
- change K5 status;
- change P5Y status.

============================================================
STAGE-1a FAILURE SEMANTICS
============================================================

Accept protocol rev. 2b §2.5.

Before/within the eventual exactly-once target execution:

- non-CERTIFIED SRK status -> safe TC-T fallback;
- non-ACCEPT verifier verdict -> safe TC-T fallback;
- exhaustion of the frozen 48 CPU-hour budget -> safe TC-T fallback;
- an actual software/runtime exception after the exactly-once marker
  has been consumed -> EXECUTION_INDETERMINATE.

An exception after marker consumption uses the single target
evaluation.

There is NO retry.

Do not convert a post-marker software exception into a fallback merely
to preserve efficacy.

Recovery after such an event is seal/review only unless the frozen
protocol explicitly establishes otherwise before execution.

============================================================
INCIDENT ACKNOWLEDGEMENT
============================================================

I acknowledge the disclosed campaign history, including:

- inherited overnight incidents 01–03;
- 309R1-01;
- 309R1-02;
- 309R1-03;
- 309R1-04;
- ERRATA E-3;
- ERRATA E-17(a);
- ERRATA E-18;
- the pre-R2 manifest-generator hashing events disclosed by R3;
- all other E-1…E-18 records already incorporated into the reviewed
  package.

Their existing classifications are accepted for purposes of proceeding
to the formal campaign.

Do not delete, weaken or rewrite any historical incident or erratum.

============================================================
EFFICACY
============================================================

I acknowledge:

    P309 efficacy at cell 309 is UNKNOWN BY DESIGN.

No inference from the decoys may be used to predict Γ309.

If SRK does not certify during the eventual exactly-once execution,
the frozen fallback semantics apply.

The fact that the single evaluation may be consumed without scientific
closure is accepted.

============================================================
SRK-T
============================================================

SRK-T remains OUT of package 1.

Do not reconsider, qualify or add SRK-T during this formal campaign.

============================================================
FORMAL CAMPAIGN PROCEDURE
============================================================

Proceed conservatively in the order required by the reviewed package.

At minimum:

1. Create the dedicated formal-campaign namespace/branch without
   rewriting the research campaign.

2. Preserve the owner decisions verbatim.

3. Perform the independent incident-independence review, including
   direct comparison against the preserved pre-FREEZE_READY scratchpad
   drafts.

4. Complete FC1.

5. Build FC2 grant-scoped guard/verifier variants.

6. Re-qualify those variants using only permitted target-free
   evidence/decoys.

7. Obtain any required independent FC2 review.

8. Complete FC3–FC6.

9. Construct the final pin set.

10. Freeze the protocol, parameters, outcome table, failure semantics,
    guard/verifier identities, evidence schema and exactly-once design.

11. Prove that the frozen package contains no unresolved placeholder,
    mutable scientific decision or post-result choice.

12. Run qualification QC01–QC17 / Q01–Q17 exactly as frozen.

13. Preserve the complete qualification evidence.

14. Obtain an independent qualification review.

============================================================
QUALIFICATION FAILURE
============================================================

If qualification or its independent review returns a blocking verdict:

DO NOT issue a grant.
DO NOT arm the marker.
DO NOT execute the target.

Preserve the verdict and stop at the appropriate formal-campaign
state.

Target-free repairs are allowed only where the frozen governance
explicitly permits them.

Do not silently re-freeze or weaken a failed qualification gate.

============================================================
SUCCESSFUL QUALIFICATION ENDPOINT
============================================================

If and only if the independent qualification review returns:

    QUALIFICATION_ACCEPTED

prepare the complete proposed execution grant, including:

- frozen commit/hash;
- protocol identity;
- cell = 309;
- Ew;
- guard identity;
- verifier identity;
- execution host/runtime identity;
- exactly-once marker identity;
- historical-control procedure;
- Stage-1a and Stage-1b procedure;
- Stage-2 driver;
- CPU budget;
- failure/recovery semantics;
- recording procedure;
- post-execution checks;
- execution-review procedure;
- adjudication table;
- adjudication-review procedure.

Then STOP.

Report:

    READY_FOR_OWNER_GRANT_DECISION

and wait for my explicit authorization.

============================================================
ABSOLUTE BOUNDARY
============================================================

Until I issue that later grant:

    NEW Γ309 TARGET EVALUATIONS MUST REMAIN 0.

No target execution.
No in-band Stage-1 target computation.
No Γ309.
No target-equivalent proxy.
No marker consumption.
No result-directed tuning.
No extrapolation from decoys.
No adoption.
No r6.
No r5 mutation.
No K5/P5Y status change.

Do not touch cell 308.

============================================================
GITHUB / HISTORY
============================================================

Preserve the research branch and its history unchanged.

The formal campaign must be additive.

You may checkpoint the dedicated formal-campaign branch/namespace as
needed, using the same conservative single-ref safety procedure.

Do not merge to main.
Do not rewrite historical branches.
Do not force-push shared history.
Do not push unrelated refs or tags.

============================================================
FINAL HANDOFF FOR THIS STAGE
============================================================

Before stopping for the grant decision, report:

- formal-campaign branch and namespace;
- exact local/remote HEAD;
- freeze commit/hash;
- frozen manifest;
- incident-independence verdict;
- FC1–FC6 status;
- FC2 re-qualification result;
- QC01–QC17 results;
- independent qualification verdict;
- target counter;
- marker state;
- execution host proposed;
- any new incidents/errata;
- r5/r6/adoption/K5/P5Y state;
- exact proposed grant.

The required endpoint is:

    QUALIFICATION_ACCEPTED
    READY_FOR_OWNER_GRANT_DECISION
    NEW Γ309 TARGET EVALUATIONS = 0

or a preserved blocking verdict.

Begin by reconstructing and independently verifying the repository
state at research HEAD eb9a9c22 and the reviewed package rev. 2b.
Do not rely solely on the previous session's prose summary.
~~~
