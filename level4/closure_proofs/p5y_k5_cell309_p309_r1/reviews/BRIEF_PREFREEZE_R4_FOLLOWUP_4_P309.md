# Brief: R4 follow-up 4, the focused re-confirmation R4F3-C3

This brief is committed before it is issued (condition C5).

**Recipient:** the independent pre-freeze reviewer R4, author of:
* `reviews/REVIEW_PREFREEZE_R4_P309.md`;
* `reviews/REVIEW_PREFREEZE_R4_FOLLOWUP_P309.md`;
* `reviews/REVIEW_PREFREEZE_R4_FOLLOWUP_2_P309.md`;
* `reviews/REVIEW_PREFREEZE_R4_FOLLOWUP_3_P309.md` (FREEZE_BLOCKED on F4, `D5_EXCEPTION_LIMITED_TO_RATIFIED_SITES: YES`).

The rules of your earlier briefs hold.

## Authority and boundaries (read first; unchanged)

Owner documents:
* `governance/OWNER_DECISIONS_P309_VERBATIM.md`;
* `governance/OWNER_RULINGS_2_P309_VERBATIM.md`;
* `governance/OWNER_D5_RATIFICATION_P309_VERBATIM.md`.

No grant exists, and NEW Γ309 TARGET EVALUATIONS must stay 0. Never create, arm or consume any ref under
`refs/p5y-k5-cell309-p309-r1/`, anywhere; TEST names only in sandboxes. Never run `execute`, `seal-only` or
`validate-grant` against this repository.

The firewall of your first brief applies:
* no consumer code and no target input;
* no 305–309 value;
* no git writes;
* write only your output file;
* ledger every run through `code/p309_env.py`, with notes prefixed "R4 reviewer:";
* evidence to a scratch `P309_EVIDENCE_DIR`.

## What changed since your follow-up 3

The tree to review is the commit that adds this brief. The written record is:
* `governance/P309_REV2C_AMENDMENTS.md`, final section "Fifth delta" (A43–A47);
* addendum 2 of `governance/D5_SITE_BACKSTOP_REPORT_P309.md`;
* addendum 5 of the qualification-review brief.

Summary:
* **R4F3-C1 (A43).** `run_seal_only` calls `check_host_git(ctx)` right after `check_flags()`, before its first git
  call.
* **NF7 (A44), adopted.** `execute` re-runs `check_host_git` in two places:
  * as the top-level statement after the historical control, before its first git write. A refusal there is before
    the marker (exit 2).
  * in `after_marker`, inside the try that holds the persist, just before it. A refusal there sends the evidence to
    the emergency file (exit 4), for `seal-only`.
* **NF6 (A45), adopted for the guard.**
  * The guard's `_git`, `_git_bytes` and `_git_ok` set `GIT_CONFIG_NOSYSTEM=1` and `GIT_CONFIG_GLOBAL=/dev/null` after
    stripping `GIT_*`.
  * The verifier variant is unchanged: inside `execute` it runs only in the Stage-1 jobs, which inherit the driver's
    `ENV`. The amendment gives the reasoning; check it.
* **NF8 (A46).**
  * QC11 H01–H07 and V11;
  * new QC12 **T10**: the host-git check precedes every git write, and the driver's, the jobs' and the guard's git
    environments are hermetic. T10 fails on your follow-up-3 tree.
  * D5 **X01–X11**: static mutants that must fail T10 itself.
* **NF9 (A47), adopted.** Your five over-provisioned entries are removed.

Whitelist changes are listed in the amendment. The dev manifest is regenerated.

**Coordinator's dev results at this tree** (development runs in a scratch clone first, then at this tree; the run
logs are in the coordinator's scratchpad):
* scan PASS, pins all current;
* static T1–T10 PASS;
* D5 controls, backstop controls, QC11 (112 flows), guard tests, scan-allowance controls, U2, self-audit: as recorded
  in the commit message of this tree.

## Tasks

1. **R4F3-C1.** Check A43. Does anything in `seal-only` still reach git before the check? `production_context` runs
   first, as in `execute`.
2. **NF6, NF7, NF8, NF9.** Check A44–A47:
   * the post-marker refusal path: emergency file, exit 4, then `seal-only`;
   * the verifier-variant reasoning;
   * T10's rules and whether they can be satisfied by code that still writes before a check;
   * the new flows;
   * the narrowing.

   **Try new adversarial mutants** against T10, in temporary copies only and never executed.
3. **R4F3-C3 runs**, once each under `-I -S -B` at this tree:
   * the D5 controls (including X01–X11 and all your earlier mutants);
   * the backstop controls;
   * QC11 (including H01–H07 and V11);
   * the static check T1–T10.
4. **R4F3-C4.** Confirm that the sites keep the owner-ratified hashes and the backstop keeps the A38 pins.
5. **Readiness.** Does anything else block the freeze?

## Output

`reviews/REVIEW_PREFREEZE_R4_FOLLOWUP_4_P309.md`:
* **Line 2**, exactly one of `FREEZE_APPROVED` or `FREEZE_BLOCKED`.
* **One line**, exactly one of `D5_EXCEPTION_LIMITED_TO_RATIFIED_SITES: YES` or
  `D5_EXCEPTION_LIMITED_TO_RATIFIED_SITES: NO`.
* **A section headed exactly `## Conditions`**, which the freeze parameters carry verbatim.
* **A disclosure section.**
