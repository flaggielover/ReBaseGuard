# Brief: independent package review R3 of the P309 formal-campaign package (candidate; never executed)

You are an **independent reviewer**, with no stake in the outcome, and you are neither the R1 nor the R2 reviewer. The
route (P309 package 1) has been classified FREEZE_READY by independent review R2 (`reviews/REVIEW_SRK_R2.md`). Your
task is to decide whether the **prospective formal-campaign package** in `protocol_prep/` is complete, internally
consistent, consistent with the reviewed route and with R2's formal-campaign items FC1–FC6, and prospectively
defensible, so that the owner could authorize a freeze of it.

## Firewall (strict)

* **Allowed reading:**
  * everything in the research namespace `level4/closure_proofs/p5y_k5_cell309_research_r1/` (NS), except
    `ledger/EXPOSURE_LEDGER.jsonl` and `ledger/INCIDENT_*`, which you need not open;
  * `reviews/REVIEW_SRK_R1.md` and `reviews/REVIEW_SRK_R2.md`;
  * `dossier/sources/READER_B_GOVERNANCE_REPORT.md`, a sanitized description of the governance pattern of earlier
    formal campaigns.
* **Forbidden:**
  * every file of the cell-307 and cell-308 campaigns and every other file outside NS;
  * any file that may carry numbers for CUSUM m = 5 cells 305–309;
  * running anything on the real kernel (h = 5, k = 1/2) at drifts in [6/5, 13/5] or its mirror;
  * any evaluation for cells 305–309;
  * any git write;
  * modifying any file other than your review file.
* **Allowed running:**
  * read-only checks, `code/self_audit.py`, `code/verifier_probe_envelope.py`, and the tests under NS/tests. Declare
    anything else inside your review before running it, and keep it to decoys at e ≤ 33/32 or synthetic geometries;
  * redirect the q309 execution ledger to your scratch file, or list your executions in your review.

## What to review (PASS / FAIL / NOTE, with evidence)

1. **Completeness.** Does the package cover every item the owner required for Phase 4?
   * prospective protocol;
   * frozen parameter specification;
   * target quarantine rules;
   * qualification suite;
   * independent review brief(s);
   * exactly-once driver design;
   * grant schema;
   * design for recording the result from memory;
   * post-execution checks;
   * execution-review brief;
   * adjudication rule;
   * adjudication-review brief;
   * failure and recovery semantics;
   * pinned source hashes and constants;
   * candidate freeze manifest.
2. **The consumer criterion is fixed before any target evaluation.** Check the pass criterion (Γ < 0, exact, strict),
   the outcome table, strictness, rounding and scope (closure only). Are they unambiguous, and would a freeze commit
   them unchanged?
3. **Consistency with the reviewed route.** Check against THEOREM_SRK §§3, 11, 12; the gate (`impl/srk_gate.py`); the
   adapter (`impl/srk_adapter.py`: its signature, bindings and refusals); rule S and the SRK-T exclusion; and the
   supply S.
4. **R2's FC1–FC6.** Is each one correctly carried into the package, including the FC2 extension? The extension
   requires:
   * genuine-only verification of in-band certificates, with no mutant battery;
   * probe construction guarded independently of any lifted band list;
   * a grant-scoped guard and a verifier variant with their own re-qualification;
   * a grant that names Ew.
5. **Exactly-once and failure semantics.** Is there any path by which the target could be evaluated twice, evaluated
   without the historical control, or evaluated with parameters chosen after a 309 number is known? Is a Stage-1
   failure handled without retry? Is the TC-T fallback stated honestly?
6. **Candidate manifest.** Do the pins match the committed files (blob and sha256)? Are the data pins metadata-only?
   Is anything the package relies on missing from the pins?
7. **Governance.** Is it clear that nothing is frozen, authorized or executed, and that the actual freeze requires the
   owner (P0-1)? Is `P309_OWNER_DECISIONS.md` complete relative to R2's owner list?
8. **Claim discipline.** Does any text overstate what the evidence shows? Examples: efficacy at 309, "independent" where
   git cannot prove authorship, readiness versus authorization.

## Verdict (line 2 of your review file)

One of:
* `PACKAGE_REVIEW: COMPLETE`: ready to be presented to the owner for a freeze decision.
* `PACKAGE_REVIEW: COMPLETE_WITH_NOTES`: list them. Notes are text-level fixes that change no rule.
* `PACKAGE_REVIEW: INCOMPLETE`: list the gaps.

Write your review to `NS/reviews/REVIEW_P309_PACKAGE_R3.md`. Keep numbers for cells 305–309 out of it.
