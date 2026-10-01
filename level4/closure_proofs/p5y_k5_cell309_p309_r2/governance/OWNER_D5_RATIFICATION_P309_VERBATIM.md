# Owner decision D5 for P309 (VERBATIM; received 2026-09-30)

One owner message, reproduced byte-for-byte from the session transcript between `~~~` fences. The sha256 of the fenced
body (UTF-8, with a final newline added if absent) is given above it. It answers
`governance/D5_OWNER_RATIFICATION_REQUEST_P309.md` (delta review condition D5). With
`OWNER_DECISIONS_P309_VERBATIM.md` and `OWNER_RULINGS_2_P309_VERBATIM.md`, it is **authority** for formal campaign
p5y_k5_cell309_p309_r1. **It does not issue the target execution grant.**

## Message received 2026-09-30T04:09:06.820Z (transcript uuid a1a825cb-f85b-487c-8130-335199415309)

sha256 `f75c4d0707a03619bb570c6e5f7ab457ad0dc69ba976fde6a525b0431bc6c373`

~~~text
D5 OWNER DECISION — RATIFY BOTH

I have reviewed the D5 conflict and ratify both items described in
governance/D5_OWNER_RATIFICATION_REQUEST_P309.md.

============================================================
D5-1 — PENDING-RESULT REF
============================================================

RATIFIED.

The frozen package may contain the inert production ref name:

    refs/p5y-k5-cell309-p309-r1/pending-result

and the reviewed recovery mechanism associated with it.

This ratification permits the NAME, schema, validation logic and
grant-gated implementation to exist in the frozen tree.

It does NOT authorize creation, mutation or use of that production ref
before the later explicit execution grant.

The purpose of the pending-result ref is accepted: preserving
recoverable evidence across the failure window between exactly-once
marker consumption and final result sealing.

============================================================
D5-2 — MARKER-CREATING FUNCTIONS
============================================================

RATIFIED.

The frozen tree may contain the independently reviewed, AST-hash-pinned
production mutation sites:

    _arm_marker
    _persist_pending

including the code necessary for those functions to create their
respective production refs during a future authorized execution.

This supersedes my earlier scanner wording ONLY to the narrow extent
necessary to allow these reviewed production mutation sites to EXIST
in the frozen package.

It does NOT authorize either function to mutate a production ref now.

============================================================
CLARIFICATION OF THE EARLIER SCANNER RULING
============================================================

The earlier statement that the scanner allowance "must NOT permit
creation of the marker ref ... consumption of the marker" is clarified
as follows:

Before the final execution grant:

    ACTUAL production-ref creation, mutation or consumption is
    forbidden.

However:

    frozen, reviewed, fail-closed CODE CAPABLE of performing those
    operations after a valid future execution grant may exist.

This exception is limited strictly to the reviewed and pinned mutation
sites identified by D5.

It is not a general scanner exemption.

The scanner must continue to reject:

- any additional production marker mutation site;
- any additional pending-result mutation site;
- any unreviewed ref mutation path;
- any dynamically constructed equivalent;
- any mutation reachable without execute mode;
- any mutation reachable without a valid owner execution grant;
- any qualification/test path capable of mutating the production refs.

The allowed sites must remain pinned by AST hash in the frozen
manifest.

Any change to their semantics or AST identity after freeze invalidates
the authorization and requires review/requalification before execution.

============================================================
EXECUTION AUTHORITY REMAINS WITHHELD
============================================================

This D5 ratification is NOT the execution grant.

Therefore, until my later explicit grant:

- do not create the production marker;
- do not create pending-result;
- do not arm or consume the production marker;
- do not perform a Γ309 target evaluation;
- do not perform an in-band target-equivalent computation;
- do not execute Stage 1 on the target;
- do not infer target results from decoys.

NEW Γ309 TARGET EVALUATIONS must remain exactly 0.

============================================================
NEXT STEPS
============================================================

Preserve this owner decision verbatim.

Allow R4 to finish independently.

If R4 identifies any blocker, preserve its verdict and resolve it
prospectively before freeze.

If R4 accepts the package and all D1–D8 conditions are satisfied:

1. independently verify the D5 scanner exception is exactly limited to
   the reviewed AST-hash-pinned sites;
2. rerun the relevant scanner/static/negative controls;
3. complete the final pin set;
4. perform the formal freeze;
5. run the frozen QC01–QC17 plus QC-U2 qualification suite;
6. preserve all qualification evidence;
7. obtain the independent qualification review.

Do NOT issue or execute the proposed grant.

If and only if the independent qualification verdict is:

    QUALIFICATION_ACCEPTED

stop at:

    READY_FOR_OWNER_GRANT_DECISION

and present the exact frozen grant proposal to me.

Required invariant at that stopping point:

    NEW Γ309 TARGET EVALUATIONS = 0
    production marker absent
    pending-result ref absent
    r5 unchanged
    no r6
    no adoption
    cell 308 untouched
~~~
