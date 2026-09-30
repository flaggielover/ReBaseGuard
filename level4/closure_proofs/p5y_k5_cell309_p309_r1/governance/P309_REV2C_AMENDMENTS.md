# P309 package rev. 2c: the complete list of changes from the reviewed rev. 2b (pre-freeze; formal campaign)

**Base.** Package rev. 2b, the research-namespace blobs that the incident review's condition C2 names:

| document | blob |
|---|---|
| `P309_PROTOCOL.md` | 5ac10d01 |
| `P309_FORMAL_PACKAGE.md` | 0867df9d |
| `P309_REVIEW_BRIEFS.md` | dadbf178 |
| `P309_OWNER_DECISIONS.md` | 613b2949 |

Those files are **not edited**, since the research namespace stays unchanged. The frozen package is rev. 2b **plus this
document**, which governs wherever the two differ.

**Review.** Incident review condition C2 says "Any change to a rule or parameter after this review needs a new
incident-independence review of the delta." Every change below is therefore submitted to:
* (a) that delta review;
* (b) the independent pre-freeze review.

The changes come from:
* the owner's rulings 2 (`governance/OWNER_RULINGS_2_P309_VERBATIM.md`);
* the independent reviews (`reviews/REVIEW_INCIDENT_INDEPENDENCE_P309.md`, `reviews/REVIEW_U2_CHECK_P309.md`);
* implementation constraints found while building FC1–FC6.

**No Stage-1 scientific parameter changes.** The following are all exactly as in rev. 2b:
* the degree ladders;
* the indices;
* the numerics;
* the hull rules;
* the cover;
* the 48 CPU-h start threshold and the 12 CPU-h per-job limit;
* the Stage-1b budget of 21 600 s;
* the failure mapping;
* the Stage-1b fallback;
* the outcome table;
* strictness, rounding and adoption semantics.

## Changes

| id | rev. 2b text | rev. 2c | source | direction for closure |
|---|---|---|---|---|
| **A1** | QC14: `rehearse --cell 305`, a historical reproduction of 305 | **QC14′**: the full Stage-2 pipeline on **manufactured** consumer inputs, with the committed certificates of the declared out-of-band decoy cell (A2 family, h = 5, [1/2, 37/72]). Checks R1–R5 are in `code/p309_rehearse.py`. The real-data reproduction remains the post-grant, pre-marker historical control (protocol §4, unchanged) | the inherited quarantine forbids Γ(5,305) before a grant; flagged at the start of this campaign | none (qualification only) |
| **A2** | FC2 per protocol §7 and the rev. 1 spec | `fc2/FC2_SPEC_R2.md`: <br>• REAL band geometry-blind; <br>• TEST band = the hull of the declared synthetic h3 decoy cell; <br>• structurally separated production and test contexts; <br>• fail-closed admission bound to schema, cell, geometry, Ew (outward 2⁻¹⁰ hull of the cell), grant commit, frozen commit, manifest sha and self-pin, own identity, marker, the namespace, expiry, host and runtime; <br>• review mode; <br>• synthetic marker `refs/p309-test/TEST_ONLY_DO_NOT_EXECUTE_P309_MARKER`; <br>• the production marker is never created anywhere before the grant | owner rulings 2 (FC2 test band, sandbox marker, admission code) | none (refusal-only before a grant) |
| **A3** | QC08 on the declared A2 decoy cells (h3 and h5) | QC08 on the **h5** A2 decoy cell only. The h3 A2 cell is now the FC2 TEST band: the variant refuses it without a test context, and QC16 verifies its committed certificates under the sandbox test context | consequence of A2 | none |
| **A4** | protocol §7(a): a guard for Stage 1a | the same `p309_guard.producer_adapter` is injected **also as the Stage-1b certifier's `ov_quarantine`**, through the pinned RLR307 loader, in execute mode only. The Stage-1b hulls (the outward 2⁻²⁰ dyadic hull of each sub-block) lie inside Ew (the outward 2⁻¹⁰ hull of the cell), because a floor or ceiling on the coarser grid bounds the one on the finer grid. So the same admission window applies | U2-check §9 (a Stage-1b band guard was missing; without it an in-band Stage 1b raises, which gives EXECUTION_INDETERMINATE) | toward validity of execution; no parameter change |
| **A5** | Stage-1b budget "accounted as in §2.5" (no per-job limit stated) | Stage-1b per-job CPU limit = 21 600 s (the whole Stage-1b budget). Start threshold 21 600 s. Job order = the RLR307 order (degree descending, then block). Terminated jobs are discarded, which falls back | implementation needed a stated limit | none (a job can never exceed the total anyway) |
| **A6** | 307 driver pattern: a post-marker wall-clock cap (EVAL_CAP_S) that raises | **no post-marker wall-clock cap.** Stopping is by protocol §2.5 budget mechanics only (not starting jobs; RLIMIT_CPU per job), and "neither raises an exception" | protocol §2.5 wording; a raising wall cap would convert a slow host into EXECUTION_INDETERMINATE | removes a host-speed route to INDETERMINATE; wall time is unbounded but CPU is bounded (48 + 4 × 12 CPU-h for Stage 1a, 6 CPU-h for Stage 1b) |
| **A7** | `protocol/P309_FREEZE.json`; `postexec/`; "grant-scoped verifier" file | `freeze/P309_FREEZE.json` and `freeze/P309_FREEZE_MANIFEST.json`; post-execution checks in `code/p309_postexec.py`; the variant is `verify/srk_verify_indep_scoped.py` | the formal push procedure (check 7) refuses paths under `protocol/`, `postexec/` and any path containing `GRANT` | none |
| **A8** | check_grant: HEAD^^^ = freeze → qualification → review → grant | the same chain, but **checkpoint-record commits that touch only `ledger/CHECKPOINT_PUSHES.jsonl` may occur between the chain commits**. Q may touch only `qualification/` and the two execution/exposure ledgers; Rv only `reviews/REVIEW_QUALIFICATION_P309*`; G only the grant file, with exactly one parent. The frozen directories (code, config, fc2, freeze, tests, verify, governance) must be unchanged after F | the record-first checkpoint push adds one ledger-only commit per push | none |
| **A9** | grant schema (package §D) | adds the fields the admission checks read: <br>• `cell_interval`, `drift_hull_Ew` (must equal the outward 2⁻¹⁰ hull), `geometry`; <br>• `frozen_commit`, `frozen_manifest_sha256`, `verifier_id`, `guard_id`, `driver_sha256`; <br>• `execution_host.host_id_sha256`, `execution_host.worktree`, `runtime.python`; <br>• `marker_ref`, `not_after_utc`, `executions_authorized` = 1; <br>• `qualification_commit`, `qualification_review_commit` | owner rulings 2 ("grant bound to frozen protocol/hash, cell 309, Ew, verifier identity, execution identity/host requirements, and marker identity") | none |
| **A10** | exactly-once names in package §A | the marker `PRODUCTION_MARKER` and the pending ref `PENDING_REF` are defined once, in `code/p309_guard.py`. The scanner allowance covers the pending-ref NAME in the guard file only, under the owner's conditions (a)–(e) **(an extension of the owner's marker-name allowance, proposed here for review)**. The refs are created only in the two **exactly-once sites** `_arm_marker` and `_persist_pending` of `code/p309_driver.py`. Each begins with `_assert_execute_context`, and each is listed in `config/SCANNER_ALLOWANCE_P309.json` by function name and AST sha256 at the freeze. Emergency file: `<gitdir>/p309-emergency-result.json` | owner rulings 2 (scanner); FC6 | none |
| **A11** | protocol §4.5 "exactly as the pinned direct / combine compute it" | the pinned `c2_d5_forecast.direct` is **called unchanged** through a shim whose `tail_enclosure` returns 𝓗_SRK, computed beforehand from the same arguments (asserted), and whose internal crosscheck returns the same pair (vacuous for SRK). The genuine TC-T crosscheck runs first on the pinned `tct_rule`. QC14′ R2 shows that the shim gives exactly the unchanged `direct`'s Γ on the EMPTY path | U2-check U4(i) | none |
| **A12** | historical control (protocol §4) | two parts, both required byte-identical to C2's committed record for the target cell: <br>• (a) the 307-pattern control (S_I1 through the unchanged `direct`: Γ, A, provenance, 𝓗, M, pass, per-supply); <br>• (b) the P309 pipeline with the EMPTY GateResult. <br>Their digest is sealed | protocol §4; U2 F-U2-3 | none |
| **A13** | K1 record binding (candidate manifest open item) | the 307 pattern: the measurement's `k1_record_sha256` = the adopted input's `record_sha256` = the entry of the pinned K1 export manifest (`COMPOSITE_EXPORT_MANIFEST.json`), and the adopted inputs' `manifest_sha256` = that manifest's pinned sha256. C_upper, the auxiliary evidence and eps_cell_refined are read from the byte-pinned adopted inputs. No other copy of a P3 record (C6's recovered files included) enters | U2-check U6 | none |
| **A14** | QC10 "re-run on the execution host" | the **proposed** execution host is this isolated cloud environment. Its host id (sha256 of machine-id and hostname), interpreter and platform are recorded in the manifest, and QC10 runs here. If the owner names another host in the grant, QC10's host re-run must be repeated there before `execute`, as a grant condition | owner decision on execution isolation | none |
| **A15** | QC09 "RLR Stage-1 decoy per the RLR307 pattern" | declared Stage-1b decoy cover cells: **297 and 316**, the RLR307 decoys, both outside the band (guard-checked at run time) | declaring the decoys prospectively | none |
| **A16** | QC12 static structure | adds: <br>• `cell_inputs` reachable only from `run_execute`; <br>• the two exactly-once sites begin with `_assert_execute_context` and are called only from `run_execute`, `after_marker` and `run_seal_only`; <br>• no call of `main`, `compose`, `requirement`, `classify`, `critical_ratio` or `atom_constant_requirement` of the consumer, and no read of the C2 gate baselines (U2 F-U2-2) | U2-check U4(ii), F-U2-2 | none |
| **A17** | QC suite | **QC-U2**: the extended U2 structure checker (U2-check U3) and its controls pass on the frozen tree, **including the driver and the FC2 components** (U4). If it cannot pass, U2_UNRESOLVED ⇒ STOP before the freeze | U2-check U3/U4 | none |
| **A18** | QC16 | per `fc2/FC2_SPEC_R2.md` §8, both implementations: N1–N13, P1, P2, I1, D1, and the scanner allowance controls | owner rulings 2 | none |
| **A19** | quarantine scan | `code/p309_scan.py`: the research scanner unchanged, plus the owner-authorized narrow allowance, plus the formal rules MARKER_MUTATION, MARKER_ALIAS, MARKER_REBIND and GRANT_WRITE, plus the reviewed exactly-once sites | owner rulings 2 (scanner) | none |

## What is not changed (for the reviewers)

* Protocol §§1–6 (scope, Stage 1a, Stage 1b rules and fallback, Stage 2, the outcome table, the quarantine), except as
  A4–A6 and A11–A12 state.
* No new quantity is computed on the target path.
* No decoy result informed any change. A1 and A3 follow from the quarantine; A2 comes from the owner's ruling; A4–A19
  are mechanics and bindings.

## Corrections required by the delta review (condition D2; append-only)

The rows A5 and A6 above stay as written. Where they differ from this section, this section governs.
Source: `reviews/REVIEW_DELTA_INCIDENT_P309.md` §7 D2, commit e53a678c.

**A5, corrected.**
* **Classification.** A5 introduces a **new parameter**: the Stage-1b per-job CPU limit. It is **efficacy-relevant, with
  an ambiguous direction**.
  * A larger limit lets a slow rung finish and certify (toward closure).
  * It can also let one rung consume the budget that later rungs would have used (against closure).
* **Rationale withdrawn.** The stated rationale "a job can never exceed the total anyway" is **false**, and is withdrawn.
  The Stage-1b budget is a *start threshold*, not a cap on total consumption, so a job started below the threshold can run
  past it.
* **Value.** The value stays **21 600 s**, equal to the start threshold. This is the most generous limit considered. The
  pre-freeze review, the delta review and the owner were each offered a smaller limit (for example 5 400 s, the Stage-1a
  ratio 12/48 applied to 21 600 s); none has set one.
* **Who may change it.** The exposed coordinator does not change the value. A change is possible only before any QC09
  or other Stage-1b run, and would be reviewed as a delta (D2).
* **Basis.** The limit was chosen without any target or decoy cost evidence.

**A6, corrected bound.**
* **No post-marker wall-clock cap.**
* **CPU bound.** The CPU used is bounded by the start-threshold mechanics:
  * a job is started only while the accounted CPU (finished jobs plus the live CPU of running jobs) is below the
    threshold;
  * at most `WORKERS` = 4 jobs run at once;
  * each job is killed at its per-job limit.

  So each stage's total CPU is **below threshold + 4 × per-job limit**:
  * **Stage 1a:** < 48 + 4 × 12 = **96 CPU-h**.
  * **Stage 1b:** < 21 600 + 4 × 21 600 s = **108 000 s = 30 CPU-h**.
* **Wall time.** Wall time is **unbounded**: it depends on the host's speed and load (A14).

The sentence "(48 + 4 × 12 CPU-h for Stage 1a, 6 CPU-h for Stage 1b)" in row A6 is superseded by the bound above.

**"What is not changed", qualified.** The Stage-1b figure of 21 600 s in protocol §3 is a **start threshold**. The
effective ceiling of Stage 1b is set by the threshold together with the per-job limit (A5), as stated above.

**QC11 coverage.** QC11 flow `S14_frozen_budget_mechanics` checks the frozen values as the job runner receives them:
* Stage 1b: per-job limit 21 600 s, start threshold 21 600 s, the RLR307 order (degree descending, then block);
* Stage 1a: 12 CPU-h per job, 48 CPU-h threshold;
* `WORKERS` = 4.

Flows S06 and S07 check the limit and threshold mechanics themselves.

## Second delta: resolution of the pre-freeze review R4 (FREEZE_BLOCKED) and the owner's D5 decision (append-only)

**Sources:**
* `reviews/REVIEW_PREFREEZE_R4_P309.md`: B1–B8 and NB1–NB15; conditions R4-C1 to R4-C5.
* `governance/OWNER_D5_RATIFICATION_P309_VERBATIM.md`: the owner's D5 decision.

Code: commit 35f3cf34 and its successors before the freeze. The rows above and the D2 section stay as written. Where
they differ from this section, this section governs.

**Review status.**
* Every row marked **new rule** is a delta under incident-review condition C2, and goes to the delta reviewer before
  the freeze (R4-C1).
* All rows go to R4's focused re-review (R4-C2), which also verifies independently that the D5 exception is limited to
  the two ratified sites.

| id | source | change | direction | new rule? |
|---|---|---|---|---|
| **A20** | R4 B1 | `execute` derives the cell interval C itself, from the pinned `cells.json`: the CUSUM entry of the target cell, each endpoint read in the canonical sum form (FE-9). It is cross-checked against the consumer's cover. The grant's `cell_interval` must equal C exactly, and `drift_hull_Ew` must equal `cell_blocks(C)[0]`. Otherwise `execute` refuses before the marker. The grant never supplies C | none on efficacy; closes an invalid-closure route | no (it enforces protocol §2.1) |
| **A21** | R4 B3, NB8 | **Pre-marker dry admission**: the guard's own checks 2–6, 8 and 9, and check 7 with an empty namespace, via `premarker_check`, plus the driver's checks: exact geometry strings, `verifier_id` and `guard_id` equal to the pinned sha256, `marker_ref`, host id, worktree, runtime, `issued_utc` not in the future, `authority` not a placeholder, and a git committer identity present. **New frozen rule: at arming, `not_after_utc` ≥ now + 14 days.** A failure is exit 2 with no marker | toward a conclusive outcome: avoidable post-marker refusals become pre-marker refusals | **yes** (the 14-day horizon) |
| **A22** | R4 B4 | Stage-1 job end mapping: **only** the kernel's CPU-limit enforcement (SIGXCPU, or SIGKILL with CPU ≥ the per-job limit) is a budget termination, which falls back. Every other abnormal end (an OOM kill, a `kill -9` below the limit) is JOB_EXCEPTION, which gives EXECUTION_INDETERMINATE. `RLIMIT_CORE` = 0. Hard limit = limit + 5 s (R4 §3.2); the A6 bound is < threshold + 4 × (limit + 5 s) | against closure in a failure case, toward conformity: implements the owner's STAGE-1a FAILURE SEMANTICS; removes a post-marker operator lever | **yes** (a precision of the failure mapping) |
| **A23** | R4 B5 | **A8 amended (grant window).** Between the review commit Rv and the grant commit G, window commits are allowed. Each changes only these paths: `ledger/ZERO_TARGET_LEDGER.jsonl`, `ledger/EXPOSURE_LEDGER.jsonl`, `ledger/CHECKPOINT_PUSHES.jsonl`, `handoff/…` and `qualification/host_rerun/…` (A14's host re-run evidence is committed there, before G). Only checkpoint-record commits may appear elsewhere in the chain. Nothing ledgered may run between G and `execute`: `execute` requires a clean tree | none | **yes** (A8) |
| **A24** | R4 B7(c) | **Freeze record.** `ledger/FREEZE_RECORD.json` names F. It is added by F's only child, which changes nothing else, and it is never changed afterwards. F must remain the last change to a frozen directory. `check_grant`, QC13, the QC runner and the proposal tool all compare against it. Chain: F ← FR ← [records] ← Q ← [records] ← Rv ← [window or records] ← G | none | **yes** (A8) |
| **A25** | R4 B2 | The sealed record carries a **top-level `stage1a`** (spec §3), so the variant's review mode can read it. P10 is strict: an evaluated record without `stage1a` fails. Post-execution invocation: `python3 -I -S -B code/p309_postexec.py`; without these flags it refuses to start | toward a conclusive outcome: a correct run no longer ends INDETERMINATE | no |
| **A26** | R4 B6 | Stage-1a verdicts are sealed **with reasons** (`stage1a.verdict_details`) through a recording proxy of the pinned variant (same file, same `verifier_identity`). A job whose reasons do not cover its verdicts raises | none | no |
| **A27** | R4 B8 | Qualification is **one complete run**: `qualification/attempt_1/`, every file O_EXCL, never overwritten, and the summary O_EXCL. If any attempt exists, the runner refuses: **no retry, no resumption**. A failed or interrupted attempt is preserved, and the campaign stops | none | **yes** (the retry rule: none) |
| **A28** | R4 NB4–NB6, NB14 | Test hooks are refused outside a sandbox context. An exception in the historical control is CONTROL_FAILED (sealed, exit 3, not consumed); any other pre-marker exception is exit 2. A **run nonce** (O_EXCL in the git dir, token and pid) binds target-mode jobs to the live `execute` process. Job children run under `-I -S -B` | none | no |
| **A29** | owner D5 | `seal-only` creates the pending ref only for emergency evidence bound to a marker that names a commit carrying the grant. HEAD must be attached to a branch under `refs/heads/`. **Scanner schema 3:** <br>• every ref-moving git call must be in a ratified site or in a function listed with its AST sha256 and a reason; <br>• marker and grant-path aliases are tracked through values; <br>• production-name tokens are allowed only in the reviewed definitions; <br>• writes into refs paths are findings; <br>• a planted-control mark in an unlisted file is a finding; <br>• a site must be the unique module-level function of its name. <br>**Static check:** T6 (arming only after `check_grant`, the dry admission and the nonce; seal-only's pending ref only behind its three guards) and T7 (no production execution path from tests or qualification tools). **QC_D5 gate:** `tests/test_p309_d5_exception.py` and a current whitelist | none | no (implements the owner's decision) |
| **A30** | R4 NB7, NB10 | **Text corrections.** <br>• A4 and FC2 spec §5 say that the adapter is injected "in execute mode only". In fact it is injected in every mode, and in the decoy modes it only returns NOT_BANDED. Target-mode records are labelled `job_mode` in the sealed record. <br>• A16's ban on consumer calls is checked by QC-U2, not QC12 | none | no |

## Third delta: resolution of the R4 follow-up review (FREEZE_BLOCKED; D5 exception not limited) (append-only)

**Sources:**
* `reviews/REVIEW_PREFREEZE_R4_FOLLOWUP_P309.md`: F1, F2, NF1, NF2; conditions R4F-C1 to R4F-C4;
* R4's mutant suite, committed as `reviews/R4_FOLLOWUP_D5_MUTANTS.py.txt`;
* the owner's D5 decision (`governance/OWNER_D5_RATIFICATION_P309_VERBATIM.md`), which lists the seven classes the
  scanner must keep rejecting.

The rows above, the D2 section and the second delta stay as written. Where they differ from this section, this section
governs. **The two owner-ratified sites are unchanged:** `_arm_marker` AST sha256 `1ee764b7…` and `_persist_pending`
`13ee3ec3…`, as ratified.

**Review status.**
* A31 and A34 change what a site call or a grant must satisfy. They go to the delta reviewer (conditions C2 and D8,
  delta-2 E10).
* All rows go to R4's focused confirmation (R4F-C3).
* A31 is reported to the owner in `governance/D5_SITE_BACKSTOP_REPORT_P309.md` (R4F-C1).

| id | source | change | direction | new rule? |
|---|---|---|---|---|
| **A31** | R4F F1(a) | **Runtime backstop at the sites**, in `_assert_execute_context` (outside the ratified ASTs). After the existing mode and shape checks, the caller frame's code object must be one of the two sites (`_SITE_CODES`, a read-only mapping); anything else is refused (`NOT_A_SITE`). Then `_site_backstop` checks the site's own preconditions immediately before its ref mutation. <br>• **arm:** `execute` mode only; the guard's `premarker_check` passes **now** (checks 2–6, 8, 9 and an empty marker namespace); the run nonce exists in the git dir and names this process's pid. <br>• **pending:** the marker exists and its commit carries the grant path (the seal-only D5 gate, re-checked at the site); in `execute` mode, also this process's run nonce. <br>In a correct run each condition already holds when the site is reached, so no outcome changes. The backstop matters only for a call that bypasses `run_execute` / `run_seal_only`, which it refuses before any ref moves | none on efficacy; fail-closed (no mutation without a grant, whatever the call path) | **yes** (a strengthened site precondition) |
| **A32** | R4F F1(b) | **Scanner schema 4: an allowlist for process execution.** Every call that can start a process or run git is a finding unless it lies in a ratified site or in a function listed in `process_policy.reviewed_functions` (file, qualified name, AST sha256, permits, reason), or it is a git call whose literal verb is in the read-only allowlist. <br>• Verbs are classified read / object / ref; unknown verbs are ref-moving. Starred or non-literal verbs and forbidden options (`-c`, `--git-dir`, … before the verb; `--output`, `--exec`, … after it) are findings. <br>• Git runners are registered with how their callers pass arguments, and every caller is classified. A reviewed wrapper that forwards its parameters into the program or verb position must be a registered runner. <br>• Findings, always: `os.system`, `popen`, `exec*`, `spawn*` and `fork*`; `pty.spawn`; `shell=True`; subprocess attributes other than `run`, `Popen`, `call`, `check_call` and `check_output`. Findings unless listed: aliases or `getattr` of process functions and modules; `__import__` / `import_module` with non-literal names; `exec` / `eval` / `compile` of non-literal code. <br>• A `python -c` code string is folded (concatenation, %-format, f-strings) and scanned with every rule. <br>• Filesystem writes whose target is built from a git directory are findings (`GITDIR_WRITE`). Ref-file paths are folded, so `'re' + 'fs'` and `'/packed' + '-refs'` count. <br>• Every file of the scanned tree needs an allowed suffix (`.py .md .json .jsonl .txt .sha256`) and no executable bit, and no module may shadow a research module. <br>• No file is skipped by its name: the `q309_guard.py` name exemption is removed from the scanner, T7 and `p309_scan_pins`. <br>• The planted formal control fires all eleven process kinds. <br>`ref_mutation_functions`: the entries whose only ref-looking call is a read form (`symbolic-ref -q HEAD`) are removed: `production_context`, `sandbox_context`, `_check_official`, `TestFC2Scoped.fresh`, `_admission`, and the D5 test's `run`, which no longer moves a ref. One entry is added: `test_p309_site_backstop.run`, which sets TEST markers in sandboxes. One is rehashed: `checkpoint_push_p309.main`, whose two `python -c` strings are now literal. The exactly-once sites, `names` and `token_definitions` are unchanged | none | no (implements the owner's D5 classes) |
| **A33** | R4F F1(c) | **T7 hardened; new T8.** <br>T7 now also flags, in tests and qualification tools: <br>• `from p309_driver import` of the forbidden names (or `G`, `*`); `from p309_guard import PRODUCTION`; <br>• `__dict__`, `getattr`, `setattr`, `delattr`, `hasattr` and `vars` on the driver or guard module, and `sys.modules`, `import_module` or `__import__` access to either; <br>• any attribute store on the guard module, and on the driver module except the QC11 stub point `persist_emergency`; <br>• references to the guard's PRODUCTION context; <br>• `_MODE` and the backstop names; <br>• in tests and the QC tools, string constants naming a forbidden name; <br>• `python -c` code strings, parsed and checked by the same rules. <br>A file listed in `t7_exemptions` (module AST sha256, the exempted rules, a reason) is exempt from those rules only: `tests/test_p309_guard.py` (PRODUCTION_REFERENCE, MODULE_ATTRIBUTE_STORE) and `tests/test_p309_site_backstop.py` (FORBIDDEN_NAME, PRODUCTION_REFERENCE). <br>T8 checks A31's structure. T1 covers the new `validate-grant` mode. T4 accepts the `_SITE_CODES` mapping as the only module-level reference to the sites | none | no |
| **A34** | R4F F2, NF1 | **Grant admission and validation.** <br>• `authority`: only the proposal's own placeholder texts are refused (`<THE OWNER'S GRANT INSTRUCTION`, `<SET BY THE OWNER`). A grant quoting the owner's words, with `<`, `>` or `->`, is admitted. Before, any `<` or `>` was refused, which could have made a genuine grant commit irreparable. <br>• `execution_host.worktree` must be present (NF1). <br>• **`validate-grant --grant FILE`**, a driver mode run before the grant commit on the execution host with HEAD at the would-be parent. It runs the same content checks as `execute`'s dry admission (`grant_content_checks`, shared), the same chain walk (`walk_chain`, factored out of `check_grant`), the guard's field parser, and the guard's checks 2, 3, 5–9 on the uncommitted candidate (`G.candidate_check`, which shares checks 3, 5, 6, 8 and 9 with `_check_official`, unchanged in order and messages). It creates no commit and no ref and runs nothing of Stage 1 or 2. Its only writes are its ledger lines, which are committed as one ledger-only window commit before the grant. <br>• Handoff: a grant commit that `execute` refuses is terminal without a new owner decision | toward a conclusive outcome (a genuine grant is no longer refused on its wording, and grant defects are found before the grant commit); NF1 against malformed grants, before the marker | **yes** (the authority test; the worktree field) |
| **A35** | R4F-C1, R4F-C3 | **Controls.** <br>• `tests/test_p309_site_backstop.py` (new, listed): A31 at run time, in sandboxes with TEST names only. B01–B11 cover each arm and pending refusal and the positive cases, `NOT_A_SITE`, and the former D5 R-controls (shape refusals). <br>• `tests/test_p309_d5_exception.py`: R4's M01–M15, each of which must be rejected; controls for A32 (verb classes, git-dir writes, file rules, runner aliases, unregistered wrappers, `-c` code, forbidden options, dynamic imports, module aliases, a changed runner) and A33 (T7 access forms, the hash-bound exemption, T8 mutations). Forbidden names are assembled from pieces. <br>• QC11: A27 (an authority quoting the owner is admitted), A28 (NF1), and V01–V09 (`validate-grant`: a pass, each named failing check, a dirty tree, nothing written; a validated candidate committed alone is admitted by `execute`). I03 loads the isolated certifier, used only for its κ constants, with a TEST-context adapter | none | no |
| **A36** | R4F NF2 | The qualification reviewer checks the committed execution ledger (the single `QUALIFICATION RUN START` line) together with the attempt tree, because an attempt directory deleted before the Q commit is detectable only through the ledger (brief addendum) | none | no |

**Proposal and freeze parameters.** The proposal tool carries a `grant_validation` step before the
`execution_procedure`. The freeze parameters carry `grant_rules.grant_validation`, `grant_rules.site_backstop`, the
amended `premarker_admission` text, and the R4 follow-up liability.
