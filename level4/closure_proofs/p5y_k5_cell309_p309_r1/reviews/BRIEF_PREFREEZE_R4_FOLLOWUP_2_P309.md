# Brief: R4 follow-up 2, the focused confirmation R4F-C3 (and the D5 exception)

This brief is committed before it is issued (condition C5).

**Recipient:** the independent pre-freeze reviewer R4, author of:
* `reviews/REVIEW_PREFREEZE_R4_P309.md`;
* `reviews/REVIEW_PREFREEZE_R4_FOLLOWUP_P309.md` (FREEZE_BLOCKED, `D5_EXCEPTION_LIMITED_TO_RATIFIED_SITES: NO`).

The rules of your earlier briefs still hold: you produced none of the reviewed code, and you are not the
incident-independence reviewer or the verifier's author.

## Authority and boundaries (read first; unchanged)

Owner documents:
* `governance/OWNER_DECISIONS_P309_VERBATIM.md`;
* `governance/OWNER_RULINGS_2_P309_VERBATIM.md`;
* `governance/OWNER_D5_RATIFICATION_P309_VERBATIM.md`.

No grant exists, and NEW Γ309 TARGET EVALUATIONS must stay 0. Never create, arm or consume any ref under
`refs/p5y-k5-cell309-p309-r1/`, anywhere, including a sandbox; only TEST names are allowed in sandboxes. Never run
`execute`, `seal-only` or `validate-grant` against this repository.

The firewall of your first brief applies:
* no consumer code;
* no target input;
* the RLR307 helpers and C1B modules only through `code/code_skeleton.py`;
* no 305–309 value;
* no git writes;
* write only your output file;
* ledger every execution through `code/p309_env.py`, with notes prefixed "R4 reviewer:";
* evidence to a scratch `P309_EVIDENCE_DIR`.

## What changed since your follow-up review

**Commits on `claude/p5y-k5-cell309-p309-r1`:**
* `3cb5d513`: the code, controls and governance for F1, F2, NF1 and NF2;
* `147ba3a2`: a scanner cache reset, with no rule change, so that repeated plantings do not retain every parsed tree;
  the dev evidence; the dev manifest;
* the commit that adds this brief. The coordinator's first D5 run at `3cb5d513` found **your M07 not rejected** (97/98):
  a ref path built into a local variable. The fix folds write targets through local bindings and helper returns, and
  adds three controls; see the "A32 addendum" in `governance/P309_REV2C_AMENDMENTS.md`.

Review the tree at the commit that adds this brief.

**The written record:**
* `governance/P309_REV2C_AMENDMENTS.md`, final section "Third delta" (A31–A36);
* `governance/D5_SITE_BACKSTOP_REPORT_P309.md`, the report to the owner that R4F-C1 requires;
* `reviews/BRIEF_QUALIFICATION_REVIEW_P309.md`, addendum 2 (NF2).

The site ASTs are unchanged (`1ee764b7…`, `13ee3ec3…`). Whitelist changes against the tree you reviewed:
* `ref_mutation_functions`, removed because their only ref-looking call is a read form (`symbolic-ref -q HEAD`) that
  schema 4 classifies as read:
  * `production_context`;
  * `sandbox_context`;
  * `_check_official`;
  * `TestFC2Scoped.fresh`;
  * `_admission`.
* `ref_mutation_functions`, also removed: the D5 test's `run`, which no longer moves a ref.
* `ref_mutation_functions`, added: `test_p309_site_backstop.run` and `test_p309_exactly_once.validate_flows`.
* `ref_mutation_functions`, rehashed: `checkpoint_push_p309.main` and `test_p309_exactly_once.admission_flows`.
* New lists: `process_policy.reviewed_functions` (with permits), `process_policy.git_runners`, and `t7_exemptions`,
  each entry with a reason.

**Coordinator's dev results** (evidence under `evidence/`, run logs in the coordinator's scratchpad):
* scan PASS; the planted formal control fires all 7 formal and 11 process kinds;
* static T1–T8 PASS;
* D5 controls **101/101**, including M01–M15;
* backstop controls 27/27;
* QC11 **103/103** under `-I -S -B` (including A27, A28 and V01–V09);
* guard tests 60/60;
* scan-allowance controls 19/19;
* U2 check and controls pass;
* self-audit A1–A10 ok;
* `p309_scan_pins.py --list` all current.

## Tasks

1. **R4F-C1 (F1).** For each of (a), (b) and (c), check that the fix is the one you described or an equivalent, and that
   it closes the failure scenarios.
   * **(a)** `_assert_execute_context`, `_site_backstop` and `_require_own_run_nonce` in `code/p309_driver.py`, and
     `tests/test_p309_site_backstop.py` (B01–B11), which exercises them in sandboxes.
   * **(b)** Scanner schema 4, `code/p309_scan.py` layer 5.
   * **(c)** T7 and T8 in `code/p309_static_check.py`.

   In particular, check that:
   * every entry of `process_policy.reviewed_functions`, `git_runners`, `ref_mutation_functions` and `t7_exemptions`
     is necessary and its reason is true;
   * the permits are the minimum;
   * no listed runner forwards a parameter into a program or verb position unless it is registered, so that its
     callers are checked;
   * the owner's seven D5 classes are rejected.
2. **R4F-C2 (F2).** Check:
   * the narrowed `PLACEHOLDER_MARKS`;
   * `validate-grant` (`validate_grant`, `grant_content_checks`, `walk_chain` and `G.candidate_check`): it must write
     nothing but its ledger lines (production context) and must agree with `execute`'s admission (QC11 V09);
   * the handoff text (`code/make_proposed_authorization.py`, `grant_validation`);
   * QC11 A27, A28 and V01–V09.
3. **R4F-C3 runs.** At that tree, run once each, under `-I -S -B`:
   * `tests/test_p309_d5_exception.py` (it now contains your M01–M15);
   * your own mutant suite (`reviews/R4_FOLLOWUP_D5_MUTANTS.py.txt`, or your scratch copy), against a temporary copy
     of this tree: static analysis only, never executed;
   * `tests/test_p309_exactly_once.py`.

   Also run `tests/test_p309_site_backstop.py` (sandboxes, TEST names only). Report the counts. **Try new adversarial
   mutants** against schema 4, T7 and T8, in temporary copies only and never executed.
4. **R4F-C4.** NF1 is applied: `execution_host.worktree` is required (A34, QC11 A28, V03). NF2 is addendum 2 of the
   qualification-review brief. Accept each, or say what is missing.
5. **Readiness.** Does anything else block the freeze?

## Output

`reviews/REVIEW_PREFREEZE_R4_FOLLOWUP_2_P309.md`:
* **Line 2**, exactly one of `FREEZE_APPROVED` or `FREEZE_BLOCKED`.
* **One line**, exactly one of `D5_EXCEPTION_LIMITED_TO_RATIFIED_SITES: YES` or
  `D5_EXCEPTION_LIMITED_TO_RATIFIED_SITES: NO`.
* **A section headed exactly `## Conditions`**, which the freeze parameters carry verbatim.
* **A disclosure section:** reads, runs (with ledger timestamps), and what you never did.
