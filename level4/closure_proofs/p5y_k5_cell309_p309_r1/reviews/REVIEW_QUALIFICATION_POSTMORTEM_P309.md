# Independent review of the qualification-failure postmortem, formal campaign p5y_k5_cell309_p309_r1
POSTMORTEM_DISPUTED

**Reviewer.** A new independent reviewer ("PM reviewer"). I wrote none of the campaign's code and I am not its
coordinator.

**Brief.** `reviews/BRIEF_QUALIFICATION_POSTMORTEM_P309.md`, committed before issue at `2b149412`.

**State reviewed.**
* HEAD `91a5747f254ec420f99cc33a3ef8b42ffd7a4c6a`. A read-only `ls-remote` at 22:53Z shows the same value for
  `refs/heads/claude/p5y-k5-cell309-p309-r1`.
* The report is `handoff/QUALIFICATION_FAILURE_POSTMORTEM_P309.md` (`2b149412`).
* The preserved attempt is `qualification/attempt_1/` (`f433d490`).

**NEW Γ309 TARGET EVALUATIONS = 0.** This review evaluated nothing and created no ref.

## Verdict in brief

The dispute is narrow. The report's conclusions are confirmed, each recomputed:
* The one official attempt failed gate Q11, and a host reboot then interrupted it during QC-D5.
* The Q11 root cause is as stated. I reproduced it independently, with a counterfactual.
* The defect is a deterministic, target-free harness defect that shows only after a real freeze. The production reader
  is unaffected.
* A27 and the owner's "QUALIFICATION FAILURE" rule require stopping here, and they permit no in-place repair.
* Target integrity holds.

**Nothing below changes the stop. Nothing below supports a retry, resumption, repair or grant.**

I dispute the report because the brief requires any wrong or overstated claim to be disputed. Three claims are
overstated or inaccurate (D1–D3). One is unverified (D4) and one is imprecise (D5). The exact corrections are in the
section "Disputed claims". I have applied none of them.

## Findings

### 1. The freeze: confirmed (one wording dispute, D3)

**F and FR.**
* F = `4c754a73767903a5ad5dddff725f1e173a0a6876`: parent `cffef234`, committed 17:05:58Z.
* FR = `2f66bc566bcc67402d883513474c1f04acbeb108`: its only parent is F.
* Across all local refs, FR is F's only child (`git rev-list --all --parents`).
* `git diff --name-status F FR` gives exactly `A …/ledger/FREEZE_RECORD.json`.
* In HEAD's history, FR is the only commit that touches the record.
* The record names F, the manifest hash and the parameters hash.

**Hashes.** I recomputed sha256 at F, at HEAD and in the working tree:
* `freeze/P309_FREEZE.json`: `b9b0f510…22284c77fa5e`, identical in all three;
* `freeze/P309_FREEZE_MANIFEST.json`: `728fbf10…2243c3fe7733c6c`, identical in all three.

**Manifest.**
* 114 code pins and 10 data pins.
* All 124 pinned git blob ids are equal at F and HEAD (0 mismatches).
* No path under the seven frozen directories changed between F and HEAD.

**Placeholder history.**
* `evidence/freeze/PLACEHOLDER_CHECK_AT_FREEZE_FAIL_1.json`:
  * sha256 `f56a1fba…fb172001`; added only in `cffef234`;
  * `pass` false, run at 17:04:19Z;
  * 6 unallowed hits, all in `freeze/P309_FREEZE.json`: line 30 "placeholder", line 36 "TBD" and "TODO", line 182
    "placeholder", line 217 "TBD" and "TODO";
  * 0 nulls.
* I read a window of about 200 characters around each hit, with every digit masked. All six are rule statements: the
  A34 history of the authority test, A21's pre-marker admission text, and the delta-3 conditions quoted verbatim. The
  report's "six rule quotations" is correct.
* `cffef234` (17:05:12Z) adds exactly two `ALLOW` entries to `code/p309_placeholder_check.py`: file
  `freeze/P309_FREEZE.json`, patterns `placeholder` and `TBD|TODO`.
* The PASS output `evidence/freeze/PLACEHOLDER_CHECK.json` has head `cffef234`, ran at 17:05:22Z and was added in F. It
  has `pass` true, 0 unallowed hits and 0 nulls. Its allowed hits in the parameter file are exactly those six.
* QC13 in the attempt re-ran the check: pass, 0 unallowed.

**D3: "reviewed" is overstated.** The two entries were committed by the coordinator 46 s before F.
* The last independent review before F is R4 follow-up 4 (`d3fd6fa9`, 11:57:46Z). No review file changed after
  `cffef234`.
* Brief addendum 8 assigns the check to the qualification reviewer: "Confirm that each of the six allowed hits is a
  rule statement … and that the entries allow nothing else". That review never took place.
* My own reading above supports the fix on the merits.

The entries are scoped by file and pattern, not by line. At F they admit exactly the six hits, and the file is
frozen.

### 2. One attempt: confirmed

**Execution ledger.**
* There is exactly one `QUALIFICATION RUN START` row in the whole ledger: row 1173, 17:07:03Z,
  `code/p309_qualify.py`. It comes after FR's commit time (17:06:09Z).
* There are 0 `HOST RERUN START` rows.
* The ledger has 1172 rows at F, at FR and at `c950054a`.
* Each committed version (F → FR → `c950054a` → `f433d490` → `61952023` → `2b149412` → `91a5747f`) is a byte prefix of
  the next.

**Attempt tree unaltered.**
* It holds 31 files. Its tree id `f1f1ab27` is identical at `f433d490`, at HEAD and in the working tree (`git status`
  clean). Only `f433d490` touches `qualification/`.
* Every file and directory has a ctime between 17:07:04.59Z and 22:35:21.84Z, and 0 have a ctime after 22:35:22Z.
  Nothing in `attempt_1` changed after the runner's last write, before or after the reboot.

**Internal consistency.**
* Every gate file carries `freeze_commit` = F.
* Each gate's `utc` minus its `wall_s` equals the previous gate's `utc` to within 1 s, from the launch at 17:07:03Z
  (`scratchpad/qualification_official.launch_utc`) to QC_U2 at 22:35:21Z, in the runner's fixed order
  (`p309_qualify.py` 409–432). There is no gap in which a rerun could fit.
* The `pass` flags and `wall_s` values match the report's table. The runner's original stdout
  (`scratchpad/qualification_official.out`, mtime 22:35:21Z) is byte-identical to
  `handoff/QUALIFICATION_ATTEMPT_1_RUNNER_STDOUT.txt`.

**No summary fabricated.** There is no `P309_QUALIFICATION.json` and no `QC_D5.json`, either in the working tree or in
any commit on any ref (`git log --all --diff-filter=A`).

**Limit.** The runner's only hash record of its files would have been the summary's `files` map, which was never
written. "Unaltered" therefore rests on ctime, git identity and internal consistency. Together they leave no room for
a change after writing.

### 3. The Q11 root cause: confirmed and reproduced independently

**The QC11 record.** `QC11.json` shows rc 1 and an empty stdout. The traceback runs:
* test line 939 `validate_flows()`;
* → line 598 V01;
* → line 594 `D.validate_grant`;
* → driver line 668 `recorded_freeze(ctx.repo)`;
* → driver line 346, `Refusal FREEZE_RECORD: the freeze record was changed after it was made`.

**The code.**
* `new_sandbox` (test lines 67–85) points the sandbox branch at this repository's HEAD, through a read-only
  alternates link.
* `build_chain` (lines 108–159) adds a sandbox freeze commit and a freeze-record commit (line 122).
* `recorded_freeze` (driver lines 333–352) refuses unless exactly one commit in the history touches
  `ledger/FREEZE_RECORD.json` (lines 344–346).

**The history.**
* The only record commit is FR `2f66bc56`, which first exists at 17:06:09Z.
* It was already in HEAD (`c950054a`) when the attempt ran; the QC11 ledger row is 1335, at 22:22:30Z.
* Every development run of QC11 predates it (for example ledger rows 902–904 and 912, 10:14–11:11Z).

**My diagnostic.** One TEST-only sandbox; **not qualification evidence**; results in scratch `PM_DIAG_QC11_RESULT.json`.
* I built it with the frozen `new_sandbox` and `build_chain`, with `SCRATCH` redirected in memory to
  `scratchpad/pm_review/`. Its base is `91a5747f`.
* The sandbox has **2** record commits: its synthetic `5d858d4c` and the real `2f66bc56`.
* `recorded_freeze` on it gives **Refusal FREEZE_RECORD**, with the same message as in `QC11.json`.
* **Counterfactual, in the same sandbox:** a synthetic freeze `9b06b824` and record `c81393f7`, placed on the real F,
  whose history holds 0 record commits. `recorded_freeze` at `c81393f7` **passes** and returns `9b06b824`.
* **Control:** `recorded_freeze` on this repository returns `4c754a73…`.

The inherited real FR is therefore the sole cause of the refusal.

**A precision (not a dispute).** The defect is not specific to V01.
* `pre_marker_flows` and `admission_flows` run first, and they also use `build_chain`.
* The test's `execute` wrapper (test lines 198–204) turns the driver's Refusal into `("REFUSED", "FREEZE_RECORD")`.
  Flows that reach `check_grant`'s `recorded_freeze` were therefore recorded as FAIL in memory. Flows that expect
  FREEZE_RECORD passed for the wrong reason.
* V01 is where the defect surfaces as an uncaught exception, because `validate_grant` calls `recorded_freeze` outside
  its `run_check` wrapper (driver line 668). The process then died before printing or writing any flow results, which
  is why stdout is empty.

### 4. The classification: confirmed, with one overstatement (D1)

**Each part of the classification holds.**
* **Deterministic and decision-independent:** the refusal depends only on the git history.
* **Target-free:** TEST names and stub evaluators; ledger row 1335 has `cells_touched` [] and 0 target evaluations.
* **Shows only after a real freeze:** the record exists only from 17:06:09Z.
* **Production path unaffected:** `check_grant` (driver line 488) calls `recorded_freeze(repo)` on the real history,
  which has exactly one record commit. My control returns F.
* **Any post-freeze run fails the same way:** the runner itself requires `recorded_freeze` on this repository's HEAD
  (`p309_qualify.py` line 385). So FR is always in the history, every sandbox built on HEAD has at least 2 record
  commits, and V01 always raises.

**The backstop shares the harness: confirmed.** `tests/test_p309_site_backstop.py` imports `test_p309_exactly_once as
X` (line 35). It builds `BS_no_grant`, `BS_granted`, `BS_marker_without_grant` and `BS_execute_pending` with
`X.new_sandbox` and `X.build_chain` (lines 73–113). Their sandboxes would carry the two record commits.

**D1: "probably exposed to the same defect" is overstated.** No backstop control reads the freeze record.
* **What the controls call.** They call only `D._arm_marker`, `D._persist_pending` and `D._assert_execute_context`.
* **Call closure.** I computed the static call closure within the driver from the two sites: `_arm_marker`,
  `_persist_pending`, `_assert_execute_context`, `_site_backstop`, `_require_own_run_nonce`, `git`, `git_blob_id` and
  `git_dir`. It contains no `recorded_freeze`, `freeze_commit`, `check_grant` or `walk_chain`.
* **Arm backstop.** It calls `G.premarker_check`, which is the guard's `_check_official` (guard lines 289–338). That
  reads the grant, the manifest at the grant's `frozen_commit`, the marker namespace, the refs, the expiry and the
  host. It never reads the freeze record; the guard has no reference to it.
* **Pending backstop.** It checks only the marker and the grant path.

So the second record commit has no path to change any backstop outcome. The backstop controls were never reached:
there is no `test_p309_site_backstop.py` ledger row after FR. Their outcome is unknown, but this defect gives no
reason to expect them to fail.

**The D5 mutant controls: confirmed.**
* They copy files into temporary directories and scan them statically.
* The only real git call in `tests/test_p309_d5_exception.py` is one read-only `for-each-ref` on this repository.
* `p309_scan.py`, `p309_static_check.py` and `p309_scan_pins.py` make no git calls and do not read the freeze record.

### 5. The interruption: confirmed (one unverified detail, D4)

**Boot time.** `/proc/stat` btime 1790808072 = **2026-09-30T22:41:12Z**. `uptime -s` and PID 1's start time agree.

**The runner's last writes.**
* Its last write to `attempt_1` is `QC_U2.json` and the U2 evidence, at **22:35:21Z** (maximum ctime 22:35:21.84Z).
* Its last ledger row is 1418 at 22:35:21Z, `tests/test_p309_d5_exception.py`, which is QC-D5's first part.
* The stdout file was last written at 22:35:21Z.

**Supplement: the QC-D5 child was alive until at most 20 s before boot.**
* `scratchpad/d5_controls/d5ctlhzfk7e5q` was born at 22:40:52.17Z, and its `code/p309_driver.py` was mutated at
  22:40:52Z. The D5 test creates each planted copy with `mkdtemp` and removes it after each scan (test line 64), so
  this copy was in use when the process died.
* The ledger holds no other D5 start.
* In development the D5 suite took 13–17 min (ledger rows 507→508, 509→510, 905→906, each from the suite's start row
  to the next row), so being mid-suite 5.5 min in is expected.
* The runner records any per-gate `Exception` as a FAIL and still writes the gate file. A missing `QC_D5.json` with a
  live child 20 s before boot is consistent only with the process being killed.

**Q11 came first.** Q11's FAIL was recorded at 22:23:06Z, 18 min 06 s before boot, so the interruption did not cause
it. Each event on its own ends the attempt under A27.

**D4: unverified.** The report says the reboot was "the second restart in this session; the first, around 15:19Z,
restarted only the harness and left processes alive", and that "No host control could prevent it".
* Nothing in the repository records a restart at 15:19Z. The recovered briefs record restarts on 2026-09-29 only.
* btime shows only the latest boot.
* This is the coordinator's account, and it is immaterial to the attempt, which began 1 h 47 min later.

### 6. Governance: stop is required; no in-place repair is permitted (confirmed)

**A27.** The rule is rev. 2c A27. The frozen `P309_FREEZE.json` has `qualification_rule` = "one complete run
(qualification/attempt_1, O_EXCL); no retry, no resumption (A27); gates Q01-Q17, Q-U2, Q-D5".
* A27 says: "A failed or interrupted attempt is preserved, and the campaign stops".
* This attempt is both failed (Q11) and interrupted (Q-D5 missing, no summary). Either alone suffices.
* The runner enforces the rule: it refuses whenever any `attempt_*` exists (`p309_qualify.py` lines 400–402).

**The owner's "QUALIFICATION FAILURE" rule.** On a blocking verdict from the qualification itself:
* do not issue a grant, arm the marker or execute;
* "Preserve the verdict and stop";
* "Target-free repairs are allowed only where the frozen governance explicitly permits them";
* "Do not silently re-freeze or weaken a failed qualification gate".

No independent review for acceptance is needed before stopping.

**The frozen governance permits no post-freeze repair.**
* The frozen parameter strings about retry, repair or attempts yield only the rule above and pre-freeze liabilities.
* The governance prose says the opposite of a repair route: ERRATA FE-11, "after the freeze record, the QC runner is
  invoked once only"; the no-placeholder statement, qualification "is not a choice point".

**Repair is also impossible in place without changing a reviewed rule.**
* `tests/` is a frozen directory (driver `FROZEN_DIRS`). A harness fix after F would make `freeze_commit` differ from
  the recorded F: "a frozen directory changed after the recorded freeze".
* A re-freeze needs a second record commit, which A24 forbids ("never changed afterwards") and `recorded_freeze`
  refuses.

### 7. Target integrity: confirmed (one inaccurate count, D2)

**No production ref anywhere.** Nothing under `refs/p5y-k5-cell309-p309-r1/` in any of these places:
* this repository: 48 refs, no `packed-refs` file, loose refs only under heads, remotes and tags;
* the remote: read-only `ls-remote`, 95 refs;
* any of the 100 directories under `scratchpad/qc11_sandboxes/` (27 of them hold TEST-namespace refs, as designed);
* my own sandbox, which holds only `refs/heads/p309-test-sandbox`.

There is no `refs/p309-test/` in this repository or on the remote.

**No grant.** There is no `authorization/` directory, at HEAD or in the working tree. No `P309_GRANT.json` exists in
any commit on any ref, and there is no `TEST_ONLY/` at HEAD.

**The execution ledger.** All 1420 committed rows have `new_target_evaluations`, `target_equivalent_proxies` and
`target_informed_optimisation` equal to 0. All 248 rows after FR have `cells_touched` []. My appended row 1421 is also
0.

**r5, r6 and the research namespace.**
* r5 `K5_COVERAGE_MAP_R5.json` has blob `f978eeb6…` at HEAD, the same as at `eb9a9c22`; 0 commits have touched it
  since.
* No path matches `COVERAGE_MAP_R6`.
* The research namespace has 0 changed paths since `eb9a9c22`.

**Cell 308 (git metadata only).**
* All 138 commits in `eb9a9c22..HEAD` (0 merges) change only paths under the formal namespace. No changed path
  mentions 307 or 308, and no path with 308 in its name has a commit in that range.
* The checkpoint pushes were plain fast-forwards of the formal branch, overwriting 0 remote-only commits.

**D2: "0 in all 100 QC11 sandboxes" miscounts.** The zero holds for 100 directories, but they are not 100 sandboxes
from the attempt's QC11. By mtime and by ctime:
* **57** were built by the attempt's QC11 (22:22:30–22:23:06Z);
* **42** predate the attempt: development runs from 05:59–11:11Z, including the four site-backstop sandboxes `BS_*`
  and the three ad-hoc diagnostics `BS_diag`, `V10_diag` and `DBG_F28`;
* **1**, `PM_qc11_root_cause` (22:44:00Z), is the coordinator's own post-reboot diagnostic, built in the QC11 scratch
  directory.

### 8. The successor notes (§6): accurate and bounded, with two corrections

**Nothing was applied.**
* No r2 path, branch or ref exists, locally or on the remote.
* No frozen directory has changed since F.
* The notes are worded as needs for an owner decision.

**Note by note.**
* **Note 1:** correct.
* **Note 2:** correct. A24, `recorded_freeze` and the runner's refusal of any existing attempt leave a new namespace as
  the only route that keeps r1's frozen rules. Changing the rules is the owner's matter.
* **Note 3:** correct for QC11. My counterfactual shows that a chain built on F passes `recorded_freeze`; it tests only
  that function, not QC11 as a whole. For the backstop controls, the "must" rests on D1. Fixing the shared builder
  covers them anyway, so the advice is harmless, but its stated reason should follow D1.
* **Note 4:** sensible. The rehearsal must itself stay TEST-only.
* **Note 5:** the time is understated (D5). QC01–QC_U2 alone took 19 698 s (5.47 h), and QC11 failed after only 36 s.
  In development a passing QC11 took about 3–6 min (rows 902–904 and 912), and the D5 suite 13–17 min. A complete
  attempt is therefore about 5.7–5.9 h, plus margin.
* **Note 6:** correct.

## Disputed claims (exact corrections; none applied by me)

* **D1 (§3, QC-D5).** "so they were probably exposed to the same defect" should read: "they share `new_sandbox` and
  `build_chain`, so their sandboxes also carry two freeze-record commits. However, no backstop control reads the freeze
  record (the sites, `_site_backstop` and the guard's `premarker_check` never call `recorded_freeze`, `check_grant` or
  `freeze_commit`), so this defect gives no reason to expect them to fail. They were never run, and their outcome is
  unknown."
* **D2 (§5).** "0 in all 100 QC11 sandboxes" should read: "0 in all 100 sandbox directories under
  `scratchpad/qc11_sandboxes/`: 57 from the attempt's QC11, 42 from pre-freeze development and 1 from the postmortem
  diagnostic".
* **D3 (§1).** "two reviewed allowlist entries" should read: "two allowlist entries, with reasons, whose check was
  assigned to the qualification review (brief addendum 8), which has not taken place". This review's item 1 finds the
  six hits to be rule statements.
* **D4 (§4).** The first restart (~15:19Z, "restarted only the harness and left processes alive") and "No host control
  could prevent it" should be marked as the coordinator's unverified account. Neither is recorded in the repository.
* **D5 (§6.5).** "about 5.5 hours" should read "about 5.5 hours for QC01–QC_U2 alone; a complete attempt about 5.7–5.9
  hours".

None of D1–D5 changes the verdict, the stop, the target counter or the successor route.

## Disclosure (reads, runs, writes)

**Scratch ledger.** Every read and run is logged, with timestamps, at
`/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/pm_review/PM_LEDGER.jsonl`.

**Reads.** Paths relative to the formal namespace:
* the brief; the report;
* `governance/P309_REV2C_AMENDMENTS.md` (the second delta, including A24, A27, A35 and A36, plus greps);
* `governance/OWNER_DECISIONS_P309_VERBATIM.md` (lines 165–195 and 240–403);
* `governance/ERRATA_FORMAL_P309.md` (lines 150–200); `governance/NO_PLACEHOLDER_STATEMENT_P309.md` (lines 10–24 and
  50–75);
* `code/p309_qualify.py`; parts of `code/p309_driver.py`, `code/p309_guard.py` and `code/p309_env.py`;
* parts of `tests/test_p309_exactly_once.py`, `tests/test_p309_site_backstop.py` and `tests/test_p309_d5_exception.py`;
* `code/p309_scan.py`, `code/p309_static_check.py` and `code/p309_scan_pins.py`, by AST or grep only;
* the manifest's structure and pins;
* `freeze/P309_FREEZE.json`: string values only, digits masked, and the windows around the six hits;
* the three placeholder-check outputs (hit metadata);
* `qualification/attempt_1/QC*.json`: only `qc`, `pass`, `wall_s`, `utc` and `freeze_commit`, plus the full
  `QC11.json` and QC13's `checks`;
* the execution ledger: counters and fields, the GOVERNANCE rows and the rows after row 1405. The decoy rows' content
  was withheld from display;
* `ledger/CHECKPOINT_PUSHES.jsonl` (the last rows);
* `handoff/QUALIFICATION_ATTEMPT_1_RUNNER_STDOUT.txt`;
* the coordinator's scratch files `postmortem_qc11.py`, `qualification_official.out` and
  `qualification_official.launch_utc`;
* file metadata only (find and stat) under `scratchpad/d5_controls/` and `scratchpad/qc11_sandboxes/`;
* the headings of two earlier reviews, for format.

**Runs.**
* Read-only git: `log`, `diff`, `rev-list`, `ls-tree`, `show`, `for-each-ref` (here and in each of the 100 QC11
  scratch sandboxes), `status`, `merge-base`, `grep`, and one `ls-remote origin` (a network read).
* `date`, `/proc/stat`, `/proc/uptime`, `ps`.
* Static AST parses, with nothing imported.
* **One** Python run of campaign code: `scratchpad/pm_review/pm_diag_qc11.py`, which built the single TEST-only
  diagnostic sandbox described in finding 3.
  * It is ledgered through `code/p309_env.py` as execution-ledger **row 1421** (2026-09-30T22:52:45Z, class GOVERNANCE,
    notes prefixed "PM reviewer:", 0 target evaluations).
  * **Not qualification evidence.** It ran no flow, no QC item, and no `execute`, `seal-only` or `validate-grant`.
  * It used TEST names only. The sandbox is at `scratchpad/pm_review/sandbox_root/PM_REVIEW_TEST_ONLY_SANDBOX`
    (alternates, no remote, never pushed; its only ref is `refs/heads/p309-test-sandbox`).
  * `P309_EVIDENCE_DIR` pointed to `scratchpad/pm_review/evidence`. Nothing was written there.

**Writes.**
* This file.
* Execution-ledger row 1421 (appended). It is uncommitted, and the committed ledger is a byte prefix of the working
  copy.
* Scratch files under `scratchpad/pm_review/` only.

Before and after the run, HEAD, all 48 refs and the other two ledgers were unchanged. No git write of any kind was
made to this repository.

**Firewall notes.**
* **(a) Cell-307 files.** My first pin check hashed every pinned blob through `git show`. That piped the bytes of four
  pinned cell-307 campaign files through sha256: `p5y_k5_cell307_rlr_r1/protocol/RLR307_FREEZE.json` and
  `code/rlr307_{stage1,independent,pinned}.py`. Their content was never displayed; only hash equality was printed. I
  then repeated the check using `ls-tree` blob ids, which is metadata only. This goes beyond "git metadata" for those
  four files, and I disclose it.
* **(b)** No value for cells 305–309 was read or shown.
* **(c) QC09 decoy outputs.** Neither `QC09_DECOY_STAGE1B_*.json` file, nor `QC09.json` beyond its five summary fields,
  was opened. No per-cell decoy result is quoted.
  * The diagnostic sandbox's checkout held copies of the namespace at HEAD, including `attempt_1`. They were never
    read, and I deleted the checked-out files, keeping `.git`.
  * Scratch copies of the committed ledger versions, used for the prefix check, were deleted after use.
