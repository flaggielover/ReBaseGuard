# Brief: R4 follow-up 3, the focused re-confirmation R4F2-C3 (and the D5 exception)

This brief is committed before it is issued (condition C5).

**Recipient:** the independent pre-freeze reviewer R4, author of:
* `reviews/REVIEW_PREFREEZE_R4_P309.md`;
* `reviews/REVIEW_PREFREEZE_R4_FOLLOWUP_P309.md`;
* `reviews/REVIEW_PREFREEZE_R4_FOLLOWUP_2_P309.md` (FREEZE_BLOCKED, `D5_EXCEPTION_LIMITED_TO_RATIFIED_SITES: NO`).

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

## What changed since your follow-up 2

The tree to review is the commit that adds this brief. The written record is:
* `governance/P309_REV2C_AMENDMENTS.md`, final section "Fourth delta" (A37–A42);
* the addendum to `governance/D5_SITE_BACKSTOP_REPORT_P309.md`;
* addendum 4 of the qualification-review brief;
* `reviews/BRIEF_FC2_VERIFIER_VARIANT_AUTHOR_FOLLOWUP_3.md` to `…_5.md`, the verifier author's three one-line
  changes to `verify/scoped_sandbox.py` (A42).

Summary:
* **R4F2-C1 (A37).** Scanner schema 5 adds closed-world allowlists:
  * imports, per directory, with your forbidden modules;
  * introspection;
  * module stores in T7, with module-valued alias resolution;
  * environments;
  * per-verb git options, with the 17 unused verbs removed and the forwarded-operand specs validated;
  * bytes tokens, and `chr()` / `join` / `decode` folding;
  * unresolved pieces under the repository root.

  `p309_postexec.py`'s exemption is now rule-specific and hash-bound. All your round-3 mutants are D5 controls:
  N01–N20, K01–K04, T7a–T7d, T8a–T8c and R01–R23.
* **R4F2-C1(g) (A38).** The backstop functions and `_SITE_CODES` are pinned with the hashes you recorded. T8 is an
  equality check. The functions are unchanged.
* **R4F2-C2 (A39).** validate-grant runs `check_flags`, `check_host_git`, `check_branch`, `check_not_evaluated`,
  `check_result_paths` and `check_clean`, and in production `check_bindings` and `check_governance_state`. New T9 checks
  the conditions. The grant_validation texts are updated.
* **NF5 and a coordinator finding (A40).** `execute`'s git now ignores the host's system and global config
  (`GIT_CONFIG_NOSYSTEM`, `GIT_CONFIG_GLOBAL=/dev/null`) and commits with a fixed identity. The new `check_host_git`, run
  right after the flag check, refuses before the marker unless:
  * the repository config holds only allowlisted keys, in the local or worktree scope;
  * no hook is present.

  The finding: this host's global config sets `commit.gpgSign` with an ssh signing program, which the post-marker
  seal's `commit-tree` would have run.
* **NF3 and NF4 (A41).** QC11 V10 (a window commit between validation and the grant). QC13
  `execution_ledger_append_only_since_the_freeze`.

**Coordinator's dev results at this tree** (evidence under `evidence/`, run logs in the coordinator's scratchpad):
* scan PASS; the planted formal control fires every formal, process and closed-world kind;
* static T1–T9 PASS;
* D5 controls **155/155**, including your N01–N20, K01–K04, T7a–T7d, T8a–T8c and R01–R23, and M01–M15;
* backstop controls 27/27;
* QC11 **104/104** under `-I -S -B` (including V10);
* guard tests 60/60;
* scan-allowance controls 19/19;
* U2 check and controls pass;
* self-audit A1–A11 ok;
* `p309_scan_pins.py --list` all current;
* the verifier author's `tests/test_verify_scoped.py` 37/37 after each helper change.

Whitelist changes against your follow-up-2 tree:
* `ref_mutation_functions`: none added or removed; rehashed `validate_flows`, `test_p309_site_backstop.run`,
  `Sandbox.commit`, `Sandbox.reset_hard_index` and `Sandbox.update_ref`.
* `reviewed_functions`: 11 added (the `introspection` and `import:importlib.util` permits named in A37); rehashed
  `run_execute`, `mirror`, `run` and `Sandbox.commit`; `exec_module` gains `introspection`.
* Forwarded specs for `mirror`, `Sandbox.commit` and `_changed_paths`.
* New lists: `import_policy`, `env_keys`, `git_verb_options` and `backstop_pins`; `t7_exemptions` extended.

## Tasks

1. **R4F2-C1.** Check that each part (a)–(i) is met as you stated it, and that every allowlist entry is necessary and
   true: imports, the two module-level `multiprocessing` exemptions, the `introspection` and `import:importlib.util`
   permits, `env_keys`, the per-verb options, `t7_exemptions` and the forwarded specs. **Try new adversarial mutants**
   against schema 5, T7, T8 and T9, in temporary copies only and never executed.
2. **R4F2-C2.** Check validate-grant's added checks and T9, and that the texts are accurate.
3. **A40.** Check the hermetic environment and `check_host_git` in `execute` and validate-grant. Is the allowlist of
   repository config keys safe and sufficient? Does anything now differ in how a correct run seals?
4. **R4F2-C3 runs**, once each under `-I -S -B` at this tree:
   * the D5 controls (including all your mutants);
   * the backstop controls;
   * QC11.

   Also run your own round-3 suites against a temporary copy, static only.
5. **R4F2-C4.** NF3, NF4 and NF5: accept each, or say what is missing.
6. **Readiness.** Does anything else block the freeze?

## Output

`reviews/REVIEW_PREFREEZE_R4_FOLLOWUP_3_P309.md`:
* **Line 2**, exactly one of `FREEZE_APPROVED` or `FREEZE_BLOCKED`.
* **One line**, exactly one of `D5_EXCEPTION_LIMITED_TO_RATIFIED_SITES: YES` or
  `D5_EXCEPTION_LIMITED_TO_RATIFIED_SITES: NO`.
* **A section headed exactly `## Conditions`**, which the freeze parameters carry verbatim.
* **A disclosure section.**
