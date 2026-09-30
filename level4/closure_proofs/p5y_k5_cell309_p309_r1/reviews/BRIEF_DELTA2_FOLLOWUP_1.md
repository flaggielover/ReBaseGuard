# Follow-up brief 1: closure check of the delta-2 pre-freeze conditions (committed before issue)

**Recipient:** the incident-independence reviewer, author of `reviews/REVIEW_DELTA2_INCIDENT_P309.md`
(DELTA2_INDEPENDENCE_ACCEPTED, E1–E10). Your earlier firewall applies.

**Question.** Do the coordinator's changes close conditions **E2, E3, E4, E8 and E9** exactly? And, per E10, does any
of them change a rule, parameter or binding beyond what those conditions ask?

| condition | what changed |
|---|---|
| **E2** | `p309_driver.run_jobs`: SIGXCPU counts as a budget stop only when `cpu ≥ job_limit_s − 0.05 s`, with the tolerance documented as `SIGXCPU_TOLERANCE_S`. SIGKILL needs `cpu ≥ job_limit_s`, as before. New QC11 flow S17: a stub child sends itself SIGXCPU at low CPU, and the result is JOB_EXCEPTION and the stage raises |
| **E3** | FE-9 addendum in `governance/ERRATA_FORMAL_P309.md`. The `post_grant_derivations.cell_interval` text is corrected in `code/make_freeze_params.py`. QC11 no longer reads `cells.json` |
| **E4** | I03 now composes manufactured, internally consistent Stage-1b rung records (the S12 pattern, with the pinned certifier's kappa) on the synthetic interval [1/2, 51/100]. The cell-307 file is no longer read. A retrospective exposure-ledger row covers the earlier reads, including the coordinator's display of the file's structure, rung statuses and one timing |
| **E6/E7** (not pre-freeze) | The QC runner logs a single `QUALIFICATION RUN START`, and QC13 checks, from the ledger anchored at the freeze record, that exactly one run happened after it. Dry-run labels. The proposal cites the host re-run commit. `not_after_utc` and the grant carry the horizon notice |
| **E8** | The whitelist hashes are unchanged: no listed function was touched, and `code/p309_scan_pins.py --list` shows every entry current. The allowance's `authority` text cites the owner's D5 ratification |
| **E9** | `DISCLOSED_LIABILITIES` gains your §4 (a)–(e), and the E2 precision. The grant's `incident_review_conditions_verbatim` carries C, D and E verbatim |

**Output:** append a section headed `## Follow-up 1 (closure of E2, E3, E4, E8, E9)` to your review file, starting with
one line, exactly one of:
* `E_CONDITIONS_CLOSED`;
* `E_CONDITIONS_OPEN`, with the list.

Write only that file. No git writes.
