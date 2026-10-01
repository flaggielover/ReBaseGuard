# Owner rulings 2 for P309 (VERBATIM; received 2026-09-30)

Two owner messages, reproduced byte-for-byte from the session transcript, each between `~~~` fences. The sha256 of
each fenced body (UTF-8, with a final newline added) is given above it. Together with `OWNER_DECISIONS_P309_VERBATIM.md`
they are the **authority** for formal campaign p5y_k5_cell309_p309_r1. **Neither issues the target execution grant.**

## Message received 2026-09-30T02:26:19.605Z (transcript uuid 5b374916-3e25-4ad1-9740-4fbef5babb66)

sha256 `71c939eef84e55ecbd040f02cecf8968300874a96273b2e6225f629ed81d0bc6`

~~~text
Continue in THIS SAME SESSION after the permission mode has been changed
to Default. Preserve the current container state first.

Before doing any new scientific/formal work:

1. verify that commit 2f1b6073 still exists;
2. verify that
   reviews/REVIEW_INCIDENT_INDEPENDENCE_P309.md
   still exists and is unmodified;
3. inspect git status and the formal branch identity;
4. commit the independent incident review additively;
5. run the formal-branch checkpoint safety procedure;
6. push ONLY the dedicated formal-campaign branch;
7. verify local HEAD == remote HEAD.

Do not reconstruct or regenerate surviving work merely for cleanliness.

============================================================
OWNER RULING — U2
============================================================

I confirm U2 = NOT_TRIGGERED only on the corrected/amended premise
established by the repository reconstruction and independent incident
review.

Do NOT preserve the earlier overbroad wording that "P309 uses no
P3-derived quantity" if that statement is not literally supported by
the dependency graph.

Instead:

- preserve the independent review's
  NOT_TRIGGERED_WORDING_DISCREPANCY verbatim;
- write the corrected proposition precisely;
- identify every potentially P3-derived quantity encountered;
- distinguish incidental/non-load-bearing presence from a
  load-bearing dependency;
- establish that the frozen P309 load-bearing path does not invoke a
  quantity requiring U2 authorization.

If that corrected proposition cannot be established from committed
evidence, STOP before freeze with U2_UNRESOLVED.

Do not reinterpret U2 merely to make the campaign proceed.

============================================================
OWNER RULING — FC2 TEST BAND
============================================================

Move FC2 admission-mechanism qualification tests OUTSIDE the real
quarantined target band.

The grant-lift mechanism must be testable prospectively without
performing an in-band scientific computation.

Use an explicitly synthetic/decoy band that is disjoint from the
cell-309 quarantined band.

The test must exercise the same admission state machine, binding,
refusal logic and verifier path, but it must not expose or approximate
the real target.

Add planted negative controls proving at least that:

- no grant -> refusal;
- malformed grant -> refusal;
- wrong cell -> refusal;
- wrong Ew -> refusal;
- wrong verifier -> refusal;
- wrong frozen hash -> refusal;
- expired/consumed/wrong marker binding -> refusal where applicable;
- synthetic test authorization cannot authorize the production band;
- production authorization cannot be synthesized from test artifacts.

No Γ309 or in-band quantity may be computed during FC2 qualification.

============================================================
OWNER RULING — QUARANTINE SCANNER
============================================================

A narrowly scoped scanner allowance for the production marker NAME is
permitted only where the name occurs as inert protocol/schema/code
metadata necessary to define or verify the mechanism.

This is NOT a general textual whitelist.

Implement the narrowest defensible allowance, preferably bound to:

- exact files;
- exact syntactic/structural context;
- exact expected literal/hash where appropriate.

The allowance must NOT permit:

- creation of the marker ref;
- mutation of the marker;
- consumption of the marker;
- construction of a production grant;
- bypass of quarantine;
- hidden evaluation.

Add positive and negative scanner controls demonstrating this
distinction.

============================================================
OWNER RULING — SANDBOX MARKER
============================================================

A sandbox ref using the REAL production marker name counts as marker
creation for governance purposes.

Therefore it is FORBIDDEN before the final owner grant.

Do not create the real marker name anywhere, including a sandbox,
temporary namespace or mock repository.

For testing, use a clearly non-production identifier such as:

    TEST_ONLY_DO_NOT_EXECUTE_P309_MARKER

or another frozen synthetic equivalent.

The synthetic marker must be structurally incapable of being accepted
by the production admission path.

Add a negative control showing that substituting the synthetic marker
for the production marker is refused.

============================================================
OWNER RULING — GRANT ADMISSION CODE
============================================================

The independent verifier/admission author IS authorized to implement
the grant-scoped admission mechanism needed by FC2.

This authorization is permission to WRITE AND TEST THE MECHANISM ONLY.

It is NOT permission to issue a grant or lift the real quarantine.

The implementation must satisfy:

- fail closed by default;
- no embedded/hard-coded valid production grant;
- no implicit grant;
- no default admission=true;
- no production marker creation;
- no real in-band computation;
- no target-derived constants;
- no test-only bypass reachable from the production path;
- grant bound to frozen protocol/hash, cell 309, Ew, verifier identity,
  execution identity/host requirements, and marker identity as required
  by the reviewed specification;
- malformed/missing/mismatched grants refused;
- synthetic qualification artifacts cannot authorize production;
- production admission cannot occur until the later explicit owner
  grant exists.

Keep producer/admission/verifier roles separated according to the
reviewed package. Do not have the coordinator silently implement an
independent component merely because another author is unavailable.

After implementation:

1. obtain independent code/spec review;
2. run the target-free FC2 re-qualification;
3. preserve all results;
4. resolve findings prospectively;
5. only then continue FC1 and FC3–FC6.

============================================================
FORMAL CAMPAIGN CONTINUATION
============================================================

After the above rulings are incorporated and independently checked,
continue the previously authorized formal campaign:

incident-independence closure
-> FC1–FC6
-> FC2 re-qualification
-> final pin set
-> freeze
-> QC01–QC17
-> independent qualification review.

You may continue autonomously through those stages.

However the previous hard boundary remains unchanged:

DO NOT issue the final execution grant.
DO NOT create/arm/consume the production marker.
DO NOT perform Stage-1 target computation.
DO NOT compute Γ309.
DO NOT compute any target-equivalent in-band proxy.
DO NOT modify r5.
DO NOT create r6.
DO NOT adopt 309.
DO NOT change K5/P5Y status.
DO NOT touch cell 308.

NEW Γ309 TARGET EVALUATIONS must remain exactly 0.

If qualification is accepted, STOP at:

    QUALIFICATION_ACCEPTED
    READY_FOR_OWNER_GRANT_DECISION
    NEW Γ309 TARGET EVALUATIONS = 0

If any blocking verdict occurs, preserve it and stop rather than
weakening the protocol.

Begin by preserving and checkpointing the existing unpushed work
before making any further modifications.
~~~

## Message received 2026-09-30T02:30:45.294Z (transcript uuid fe10cf42-8e64-4b61-a4d9-c0dd20d2e2fd)

sha256 `600c7e0462b23624a1fc95364a6244a18acef01e6d4e12fa505d1c55fa200666`

~~~text
The current session is now in Default permission mode.

Go ahead.

Resume exactly from the preservation boundary in my previous
instruction. Do not perform any new scientific or formal-campaign work
until the existing container-only work has been safely preserved.

First execute steps 1–7 exactly as previously specified:

1. verify commit 2f1b6073;
2. verify the existing incident-independence review file;
3. inspect git status and formal-branch identity;
4. commit the review additively, including its execution ledger and
   record its hash at commit time;
5. run the formal-branch checkpoint safety procedure;
6. push ONLY claude/p5y-k5-cell309-p309-r1;
7. verify local HEAD == remote HEAD.

After that preservation checkpoint succeeds, continue with my already
issued owner rulings in the exact order previously specified:

U2
-> FC2 test band
-> scanner allowance
-> sandbox marker
-> grant-admission implementation
-> independent review/requalification
-> FC1–FC6
-> freeze
-> QC01–QC17
-> independent qualification review.

All previous hard boundaries remain unchanged.

Do not issue the final execution grant.
Do not create, arm or consume the production marker.
Do not compute Γ309 or any target-equivalent in-band quantity.
Do not touch cell 308.

Stop at either a preserved blocking verdict or:

QUALIFICATION_ACCEPTED
READY_FOR_OWNER_GRANT_DECISION
NEW Γ309 TARGET EVALUATIONS = 0
~~~

