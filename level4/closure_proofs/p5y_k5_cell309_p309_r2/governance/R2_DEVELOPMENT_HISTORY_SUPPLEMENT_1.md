# P309-r2: development history supplement 1 (additive)

This record is filed under the owner's OD-R2-0(C) answer in `governance/OWNER_DECISIONS_R2_MSG5_VERBATIM.md`:
"ACKNOWLEDGE. Also record the later development-only interruptions discovered during the recovery, hardening,
adoption-candidate, and review work as additive history. Do not rewrite the earlier record."

**This record is additive.**
- It changes no earlier record. The liabilities list in `OWNER_DECISION_PACKET_R2.md` and the r2 development history
  under `evidence/drill/` are unchanged.
- It records **development-only** events. None of them was an official qualification attempt, a freeze, a grant or a
  target evaluation.
- Every interrupted run was classified from its content (INTERRUPTED, never PASS) and **never resumed**. Each
  replacement run started in a new directory, as message 1 §5B and r2 P23 require.

## Events

| # | work | event | what happened to the run | evidence (branch @ commit: path) |
|---|---|---|---|---|
| 1 | r1 Q11 recovery (development replay of r1 bytes in the cloud session) | a tool time limit stopped Run A | classified INTERRUPTED; not resumed; replaced by new runs | `claude/p309-q11-recovery-20261005` @ `290b6c10`: `level4/closure_proofs/p5y_k5_cell309_q11_recovery/QUALIFICATION_RECOVERY_REPORT_P309_Q11.md` §5 ("Observed for real") |
| 2 | r1 Q11 recovery | a container restart stopped Run B, at QC10 (all of QC01–QC09 had passed) | classified INTERRUPTED; not resumed | same report, §4 table (QC01–QC09 row) and §5 |
| 3 | r1 Q11 recovery | a container restart stopped the r2-items run (its QC-D5) | classified INTERRUPTED; not resumed; QC-D5 covered by another complete run | same report, §4 and §5 |
| 4 | adoption candidate `93d55063` (task 3), light result-free rehearsal | the cloud container's disk allowance was exhausted during the rehearsal's clone | `status` gave **INTERRUPTED** ("no provenance (interrupted before the first write)"); the root was preserved and not reused; a new root ran to PASS | `claude/p309-r2-hardening-20261005` @ `5e43e84c`: `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/r2_candidate/evidence/rehearsal/ATTEMPT1_STATUS.json`; `r2_candidate/R2_CANDIDATE_VALIDATION_REPORT.md` (STEP 6) |
| 5 | S1–S3 follow-up of the candidate `a119e978` (task 4) | a container reboot stopped the regression (after QC12) and the light rehearsal (after QC13) | the rehearsal's `status` gave **INTERRUPTED** ("the host rebooted since the rehearsal started (boot id changed)"); the partial regression output was kept; both ran again from scratch into new roots, after a fresh replica built by a second crash-matrix run (identical to the first) | `claude/p309-r2-hardening-20261005` @ `4b3baebd`: `…/r2_candidate_followup/evidence/rehearsal/ATTEMPT1_STATUS.json`, `…/evidence/REG_a119e978_ATTEMPT1_INTERRUPTED_partial.json`, `…/evidence/MATRIX_a119e978_run2.json`; `…/FINAL_R2_CANDIDATE_REVIEW.md` ("Interruption (disclosed)") |

**Hardening (task 2) and the formal review (follow-up 5).** Their committed records report no unplanned interruption of
an evidence run. Task 2's deliberate kill test of the rehearsal tool is a planned control, not an interruption
(`FULL_RESULT_FREE_REHEARSAL.md`, "kill test").

## What these events show, for the record

- **They are infrastructure events in a development environment.** Message 4 item 13 excludes that environment as an
  official durable host. They are part of why the durable-host prerequisites exist (`R2_HOST_REQUIREMENTS.md`; the
  durable-host packet on the hardening branch).
- **Each event behaved as the hardened protocol requires:**
  - the interrupted run was never resumed;
  - it was classified INTERRUPTED, not PASS;
  - its replacement ran in a new location.

NEW Γ309 TARGET EVALUATIONS = 0. No grant. Cell 309 remains OPEN.
