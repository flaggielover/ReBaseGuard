# Brief: R4 follow-up, a focused re-review of the fixes (R4-C2) and independent verification of the owner's D5 exception

This brief is committed before it is issued (condition C5).

**Recipient:** the independent pre-freeze reviewer R4 (author of `reviews/REVIEW_PREFREEZE_R4_P309.md`, verdict
FREEZE_BLOCKED). The other briefs' rules still hold: you produced none of the reviewed code, and you are not the
incident-independence reviewer or the verifier's author.

## Authority and boundaries (read first)

**Owner documents:**
* `governance/OWNER_DECISIONS_P309_VERBATIM.md`;
* `governance/OWNER_RULINGS_2_P309_VERBATIM.md`;
* **new:** `governance/OWNER_D5_RATIFICATION_P309_VERBATIM.md`. The owner ratified both D5 items and clarified the
  scanner ruling.

**The hard limits are unchanged.** No grant exists. NEW Γ309 TARGET EVALUATIONS must stay 0. Never create, arm or
consume any ref under `refs/p5y-k5-cell309-p309-r1/`, anywhere, including in a sandbox. Only TEST names are allowed in
sandboxes.

**The firewall of your first brief applies** (`reviews/BRIEF_PREFREEZE_R4_P309.md`):
* no consumer code;
* no target input;
* the RLR307 helpers and C1B modules only through `code/code_skeleton.py`;
* no 305–309 value;
* no git writes;
* write only your output file;
* ledger every execution through `code/p309_env.py`, with notes prefixed "R4 reviewer:";
* evidence to a scratch `P309_EVIDENCE_DIR`.

## What changed since your review (the candidate freeze tree)

**Commits**, from `7fe020c8` (the tree you reviewed) to the tip of `claude/p5y-k5-cell309-p309-r1`:
* `879e6908`: your review preserved;
* `cf4f16cc`: verifier-author brief 2;
* `f1a99aeb`: the verifier author's NB3/NB9/NB12;
* `35f3cf34`: the code for B1–B8 and D5;
* `9d885ba1`: governance and QC.

**The written record** is `governance/P309_REV2C_AMENDMENTS.md`, final section "Second delta" (A20–A30), and
`governance/ERRATA_FORMAL_P309.md` FE-9 (`cells.json` endpoints are stored as a sum of two strings; three readers had
misread them; none had ever run).

**The coordinator's dev results** at `9d885ba1`:
* QC11 flow groups 90/90 (pre-marker, admission A01–A26, post-marker, stage S01–S16, integration I01–I03);
* guard tests 60/60, with reasons asserted;
* D5 controls 54/54;
* scan PASS;
* static T1–T7 PASS;
* U2 check and controls pass;
* self-audit ok.

A pre-freeze dry run of the QC runner's items is in progress under the coordinator's scratchpad. Any fix it forces will
come to you as an addendum.

## Tasks

1. **B1–B8.** For each finding, check that the fix closes the failure scenario you described, or an equivalent one.
   Cite the code and the QC11, guard or D5 flow that exercises it. In particular:
   * **B1:** `expected_cell`, `cover_rat` and the cross-check against the consumer's cover;
   * **B2:** the top-level `stage1a`, P10 in review mode (I01/I02), and the postexec flags;
   * **B3:** `premarker_admission` plus the guard's `premarker_check`, and the 14-day horizon;
   * **B4:** the job-end mapping;
   * **B5:** the grant window (A19–A22 flows);
   * **B6:** `verdict_details`;
   * **B7:** I03 (the whole evaluation in-process on decoys), the context-parameterized checks, the freeze record (A23–A25), and the E1-1 positive (A18, N7i);
   * **B8:** `code/p309_qualify.py`, which runs one attempt, writes O_EXCL, and never retries.
2. **NB1–NB15.** Classify each as applied, or as a residual accepted with a reason. The coordinator's view of the
   residuals:
   * **NB6:** the guard does not refuse while an emergency file exists. The pid-bound run nonce binds target jobs to
     the live `execute` process, and an emergency file exists only after the evaluation.
   * **B7(b):** `check_bindings` and `check_governance_state` stay production-only. They are exercised by
     `preflight`, QC13 and the self-audit on this repository.
   * **B7(b):** the sandbox's guarded result paths are its own TEST paths.
   * **The committer-identity check has no QC11 flow.** Git's identity auto-detection depends on the environment.
   * **NB2 in QC11:** refusal flows assert the refusal code and unchanged refs; the guard tests assert reasons.
   Say which of these you accept.
3. **R4-C2 runs.** At the candidate tree, run once each:
   * `tests/test_p309_exactly_once.py` under `python3 -I -S -B` (it needs the flags now);
   * `tests/test_p309_guard.py`;
   * `tests/test_verify_scoped.py`;
   * `tests/test_p309_d5_exception.py`.

   The QC11 integration flows re-verify the committed TEST-band and a2_h5 decoy certificates in review mode, which
   takes minutes. Report the counts.
4. **Owner D5, step 1.** Verify independently that the D5 scanner exception is **exactly limited to the reviewed,
   AST-hash-pinned sites**, and that the scanner and static check still reject each of the owner's seven classes:
   1. any additional production marker mutation site;
   2. any additional pending-result mutation site;
   3. any unreviewed ref mutation path;
   4. any dynamically constructed equivalent;
   5. any mutation reachable without execute mode;
   6. any mutation reachable without a valid owner execution grant;
   7. any qualification or test path able to mutate the production refs.

   Review:
   * `code/p309_scan.py` schema 3;
   * `config/SCANNER_ALLOWANCE_P309.json`: the two sites with the owner-ratified hashes `1ee764b7…` and `13ee3ec3…`,
     `ref_mutation_functions` with reasons, `token_definitions`, `planted_control_files`;
   * `code/p309_scan_pins.py`, which refreshes only listed entries and never touches the sites;
   * `code/p309_static_check.py` T4, T6 and T7;
   * `tests/test_p309_d5_exception.py`.

   **Try your own adversarial mutants**: in temporary copies, never in this repository and never executed. Every listed
   whitelist entry must be necessary, and its reason true.
5. **Readiness.** Does anything else block the freeze?

## Output

`reviews/REVIEW_PREFREEZE_R4_FOLLOWUP_P309.md`:
* **Line 2**, exactly one of:
  * `FREEZE_APPROVED`;
  * `FREEZE_BLOCKED`.
* **One line**, exactly one of:
  * `D5_EXCEPTION_LIMITED_TO_RATIFIED_SITES: YES`;
  * `D5_EXCEPTION_LIMITED_TO_RATIFIED_SITES: NO`.
* **A section headed exactly `## Conditions`**, which the freeze parameters carry verbatim.
* **A disclosure section:** reads, runs (with ledger timestamps), what you never did.
