# Formal campaign p5y_k5_cell309_p309_r1 — P309 package 1 (closure-only, exactly-once) — PRE-GRANT STAGE

**Authority.** `governance/OWNER_DECISIONS_P309_VERBATIM.md` (owner, 2026-09-30).
**This stage does NOT hold a target execution grant.** No exactly-once marker is armed. Cell 309 is not evaluated.
NEW Γ309 TARGET EVALUATIONS = 0.

| item | value |
|---|---|
| branch | `claude/p5y-k5-cell309-p309-r1` (additive; starts at research HEAD `eb9a9c22`; the research branch is preserved unchanged) |
| namespace | `level4/closure_proofs/p5y_k5_cell309_p309_r1/` (every commit of this campaign stays inside it) |
| route | P309 package 1, candidate rev. 2b (`level4/closure_proofs/p5y_k5_cell309_research_r1/protocol_prep/`) — FREEZE_READY (review R2), PACKAGE_REVIEW: COMPLETE (review R3) |
| cell set | {309}; 305, 306, 307, 308 excluded |
| scope | U3 = CLOSURE_ONLY; U2 not triggered (to be confirmed factually before the freeze) |
| owner decisions | G1 accepted (MEDIUM-HIGH); G3 RLR confirmed with Stage-1b fallback to S_I1; Stage-1a failure semantics per protocol §2.5; incidents acknowledged; efficacy unknown by design; SRK-T OUT |
| quarantine | `config/FORMAL_QUARANTINE_P309.json` (inherits the research quarantine until a grant) |
| environment | `code/p309_env.py`: research modules read-only on sys.path; every ledger redirected into this namespace |
| checkpoint | `code/checkpoint_push_p309.py`: the nine-check single-ref procedure, bound to this branch and namespace, plus "research namespace unchanged" |

## Stage plan (owner order) and state

| # | step | state |
|---|---|---|
| 0 | independent start-state reconstruction at eb9a9c22 (`start_state/`) | DONE: all pins match; verdicts; evidence complete; research self-audit PASS |
| 1 | namespace/branch; owner decisions verbatim | DONE |
| 2 | coordinator incident audit + independent incident-independence review (incl. direct comparison with the preserved pre-FREEZE_READY drafts) | pending |
| 3 | FC1 pin set | pending |
| 4 | FC2 grant-scoped guard (coordinator) and verifier variant (verifier's author) | pending |
| 5 | FC2 target-free re-qualification; independent FC2 review | pending |
| 6 | FC3–FC6 (driver, exactly-once machinery, recording, post-exec, briefs) | pending |
| 7 | final pin set; freeze; placeholder / mutable-decision proof | pending |
| 8 | qualification QC01–QC17 / Q01–Q17 exactly as frozen; evidence preserved | pending |
| 9 | independent qualification review | pending |
| 10 | if QUALIFICATION_ACCEPTED: proposed execution grant; STOP → READY_FOR_OWNER_GRANT_DECISION | pending |

A blocking verdict at any step: preserve it and STOP (no grant, no marker, no target).
