# Owner decisions for P309-r2, message 5 (VERBATIM; received 2026-10-05 in the coordinating cloud session)

This record holds the owner's answers to the owner decision execution packet (level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/owner_decision_packet/OWNER_DECISION_EXECUTION_PACKET.md (hardening branch 8c21918a)) verbatim, in one fenced block,
with its sha256 below it. The hash follows addendum 2, F10: it covers the body without the newline that precedes the
closing fence.

* **Transcription.** The message was received as chat text and is transcribed here with its line breaks as received.
  Nothing is redacted, and nothing is added inside the block.
* **Additive.** It is a new file. No earlier governance record is changed, including `OWNER_INSTRUCTIONS_R2_VERBATIM.md`
  and `OWNER_INSTRUCTIONS_R2_MSG4_VERBATIM.md`.
* **Structured form.** `OWNER_DECISIONS_R2_RECORD_1.json` maps each answer to the packet's decision IDs and quotes the
  owner's own answer line. Where the two differ, this verbatim text governs.
* **What it authorizes.** Exactly what the text states, and nothing more. In particular it authorizes no freeze, no
  qualification, no grant and no Γ309 evaluation, and Cell 309 remains OPEN.

## Message 5

```text
I am issuing the following owner decisions for ReBaseGuard Cell 309 / P309 r2.
These decisions are governance decisions only. They do not authorize any action beyond what is explicitly stated below.
OD-R2-0(A)
CONFIRM.
OD-R2-0(B)
CONFIRM ALL ROWS.
OD-R2-0(C)
ACKNOWLEDGE.
Also record the later development-only interruptions discovered during the recovery, hardening, adoption-candidate, and review work as additive history. Do not rewrite the earlier record.
OD-R2-0(D)
DEFER / REMAIN OPEN.
I do not yet authorize the freeze or the single official qualification attempt.
This decision may be brought back to me only after all required pre-freeze prerequisites are satisfied and independently evidenced, including at minimum:

* incorporation of the formally accepted candidate;
* SF1 resolution;
* worker-tier drill on the incorporated bytes;
* required host audit and host acceptance;
* required governance records filed in r2;
* required pre-freeze review;
* all other dependencies identified by the authoritative r2 governance packet.

Nothing in this message authorizes a qualification attempt.
OD-R2-1
SELECT OPTION (b).
OD-R2-1b
CONFIRM.
OD-R2-2
RATIFY.
OD-R2-3
APPROVE the read-only host audit only.
This approval does not authorize mutation of the qualification host, installation or removal of software, service changes, permission changes, reboot, qualification execution, or target evaluation.
Dedicated qualification-host availability is not decided by this answer. Treat it as pending host selection/confirmation unless an already-authoritative owner record states otherwise.
OD-R2-4
DEFER.
Bring OD-R2-4 back to me after the read-only host audit identifies the exact host changes, if any, that require owner consent.
Do not infer consent to host mutation from OD-R2-3.
OD-R2-5
SELECT OPTION (i).
OD-R2-6(ii)
REQUIRE the QC10 host re-run before any grant may be considered.
OD-R2-6(iii)
NO HOST IS NAMED AT FREEZE at this time.
A qualification host must be selected and accepted through the required governance process before the official qualification is authorized.
SF1
SELECT SF1-A.
Resolve ledger appendability by extending the pre-launch probe under a narrowly scoped reviewed delta before the worker-tier drill.
This authorization is limited to the minimal SF1 probe extension and its required tests/review.
It does not authorize unrelated hardening.
OD-R2-H
SELECT H-A.
I approve incorporation of the formally reviewed candidate strictly under formal-review condition C1:
fast-forward r2 from:
101ef2cb
to:
a119e978
with no other change in the same incorporation step.
This authorization applies only to that exact fast-forward.
It does NOT authorize:

* freeze;
* qualification;
* grant issuance or consumption;
* Gamma(309) evaluation;
* any target evaluation;
* Cell 309 adoption;
* scientific-status change;
* r5 modification;
* creation of r6;
* unrelated commits bundled into the incorporation step.

Before performing the fast-forward, verify again that the candidate is exactly a119e978 and that r2 is exactly 101ef2cb. Fail closed on any mismatch.
F-DRILL-ORDER
SELECT FD-A.
I accept the formally reviewed F-DRILL-ORDER correction contained in candidate a119e978.
Treat this as a separate recorded owner action even though the reviewed bytes enter r2 through OD-R2-H.
Do not expand this authorization beyond the reviewed correction.
AF-1
CONDITIONAL / NOT YET TRIGGERED.
If and only if the read-only host audit establishes that the Cell-308 checkout is world-readable, return with the exact proposed amendment and evidence before changing anything.
AF-2
CONDITIONAL / NOT YET TRIGGERED.
If and only if the selected durable host lacks the metadata service required by the incorporated qualification package, return with a minimal reviewed portability proposal.
Do not implement it preemptively.
AF-3
AUTHORIZE FILING OF GOVERNANCE RECORDS.
After the OD-R2-H fast-forward has been performed and independently verified, I authorize filing into r2, in a separate additive governance-only commit, the already accepted formal delta review record, required re-pin/governance supplements, and this owner-decision record.
Do not combine those governance files with the C1 fast-forward step.
Preserve previous governance records unchanged.
AF-4
DEFER.
No grant is authorized.
Any future grant decision requires a separate explicit owner decision after successful qualification and all required evidence/reviews.
AF-5
NOT TRIGGERED.
Do not create or enter an r3 path unless r2's future authorized qualification fails and the governing process requires a new owner decision.
Execution order authorized by this message
The permitted sequence is:

1. Record these owner decisions additively.
2. Perform the exact C1 fast-forward incorporation:
r2 101ef2cb -> a119e978.
3. Independently verify the resulting r2 bytes and ancestry.
4. In a separate governance-only commit, file the approved review/governance records and this owner-decision record.
5. Implement only the narrowly scoped SF1-A change under its own branch/review process.
6. Perform the required worker-tier drill on the incorporated/reviewed bytes when the host prerequisites are satisfied.
7. Complete the required host audit and remaining pre-freeze reviews.
8. Return to me for OD-R2-0(D).

STOP before freeze.
Gamma(309) remains forbidden.
No grant is authorized.
Cell 309 remains OPEN until a later explicitly authorized governance action says otherwise.
```

sha256: `bf393a77cd4ee39bcc71b94019ffe320f13db2e8fbf53c90af556bc1f1b91094` (bytes: 5439)
