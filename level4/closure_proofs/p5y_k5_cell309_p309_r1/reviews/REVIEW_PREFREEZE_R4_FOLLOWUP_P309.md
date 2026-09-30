# Independent pre-freeze review R4, follow-up (R4-C2 focused re-review and owner D5 step 1), formal campaign p5y_k5_cell309_p309_r1
FREEZE_BLOCKED
D5_EXCEPTION_LIMITED_TO_RATIFIED_SITES: NO

**Reviewer.** R4, the author of `reviews/REVIEW_PREFREEZE_R4_P309.md` (FREEZE_BLOCKED, preserved at 879e6908). R4 wrote
none of the reviewed code. Brief: `reviews/BRIEF_PREFREEZE_R4_FOLLOWUP_P309.md` (committed before issue, 4ac99bc1).

**State reviewed.**
* The code is as of **70927a08**. The commits after it (166df145, 317ac9b7, 95fb1ce6, 89d08c56, ea59b2b6) touch
  ledgers only.
* It includes the fixes at 35f3cf34 and 9d885ba1, the verifier author's f1a99aeb, FE-10 at 44b10d63 (addendum 1), and
  the delta-2 conditions at 70927a08 (addendum 2).
* The two ratified sites have the owner-ratified AST hashes, recomputed by R4:
  * `_arm_marker`: `1ee764b7…`;
  * `_persist_pending`: `13ee3ec3…`.

---

## 1. Verdict in brief

**FREEZE_BLOCKED.** B1–B8 are fixed, and the fixes close the failure scenarios I described (§3). The R4-C2 runs pass:

| suite | run at | result |
|---|---|---|
| QC11 | 70927a08 | 92/92 |
| guard | — | 60/60 |
| variant | — | 37/37 |
| D5 controls | 70927a08 | 54/54 |

Two findings block the freeze:
* **F1 (owner D5, step 1).** The scanner and static check do **not** reject the owner's seven classes. Fifteen
  independent mutants, several of them ordinary Python, pass both the formal scan and static checks T1–T7 cleanly. Two of
  them, a test-path call to a ratified site and a call through the module dict, would create a production ref at
  runtime, with no grant, if executed. So the only protection is static, and it can be evaded. Hence
  `D5_EXCEPTION_LIMITED_TO_RATIFIED_SITES: NO`.

  The **sanctioning** mechanism itself is correctly limited. It sanctions only the two unique module-level functions
  with the ratified hashes.
* **F2 (grant trap).** The dry admission rejects any `authority` text containing `<` or `>`. For example, an owner
  instruction pasted verbatim with "->" would fail. There is also no way to validate a candidate grant before it is
  committed. Under the amended chain, a grant commit refused by `execute` cannot be replaced additively. A defective grant
  is therefore terminal without a history rewrite, which the owner forbids.

Both fixes are small. F1's runtime part does not touch the ratified ASTs.

---

## 2. Blocking findings

### F1. The seven D5 classes are not rejected: static evasions, and no runtime backstop at the sites

**How I tested.** `scratchpad/r4/d5_mutants.py` (ledgered) plants each mutant in a temporary copy of
`code/`, `config/`, `tests/` and `verify/`. The copy is only parsed, by `p309_scan.scan` and `p309_static_check.run`; it is
never executed, and it is deleted afterwards.

The genuine tree passes. My three NB1 aliasing snippets from the first review are now caught: MARKER_MUTATION /
REF_MUTATION_UNLISTED and GRANT_WRITE. **Every mutant below passes the scan (PASS, no findings) and T1–T7**, at 70927a08
(`evidence`: `scratchpad/r4/evidence/R4_D5_MUTANTS_at_70927a08.txt`).

| id | mutant (added to a copy) | owner class |
|---|---|---|
| M01 | a file `code/q309_guard.py` in FNS with `subprocess.run(['git','-C',repo,'update-ref',<marker literal>,g])`. The scanner and T7 skip every file named `q309_guard.py`, and `p309_env` puts FNS/code first on `sys.path` | 1, 3 |
| M02 | `os.system('git update-ref ' + G.PRODUCTION_MARKER + ' ' + g)` | 1, 3 |
| M03 | `subprocess.run('git … update-ref refs/heads/x HEAD', shell=True)` | 3 |
| M04 | `verb = 'update-' + 'ref'; git(verb, ctx.marker_ref, g, '0'*40, repo=ctx.repo)` | 1, 4 |
| M05 | `r = ctx.pending_ref; args = ['update-ref', r, b]; git(*args, repo=ctx.repo)` | 2, 4 |
| M06 | `git('-c', 'alias.u=update-ref', 'u', ctx.marker_ref, g, '0'*40, repo=ctx.repo)` | 1, 4 |
| M07 | `(Path(str(gd)) / ('re' + 'fs') / 'heads' / 'x').write_text('0'*40)` (a raw ref file) | 3, 4 |
| M08 | `open(str(gd) + '/packed' + '-refs', 'a').write(…)` | 3, 4 |
| M09 | `r = subprocess.run; r(['git','update-ref','refs/heads/x','HEAD'])` | 3, 4 |
| M10 | `getattr(subprocess, 'run')(['git','update-ref',…])` | 3, 4 |
| M11 | `os.execvp('git', ['git','update-ref',…])` | 3 |
| M12 | `subprocess.getoutput('git update-ref …')` | 3 |
| M13 | **a test file**: `from p309_driver import _arm_marker as arm`; `D._MODE['mode'] = 'execute'`; a `SimpleNamespace` with `kind='PRODUCTION'`, `guard_ctx=D.G.PRODUCTION`, the production names and `repo=D.REPO`; `arm(c, g)` | 5, 6, 7 |
| M14 | **a test file**: the same, with `D.__dict__['_persist_' + 'pending'](c, data)` in seal-only mode | 5, 6, 7 |
| M15 | `code/arm.sh` (`git update-ref "$1" "$2"`), invoked by `subprocess.run(['bash','code/arm.sh',ref,g])` (non-.py files are never scanned) | 3 |

**Why M13 and M14 matter most.** `_assert_execute_context` (driver 167–181) checks only `_MODE` and the shape of the
context: kind, `guard_ctx is G.PRODUCTION`, the names, and `repo == REPO`. It does not check that a grant exists. A caller
that sets `_MODE` and passes a production-shaped namespace therefore reaches `git update-ref <production marker>` in this
repository.

The only thing standing between that and a mutation without a grant is T6/T7's static reachability analysis. T7 inspects
only `ast.Name` / `ast.Attribute` nodes, so it misses both an `import … as` alias and string-keyed access.
(I did **not** execute M13 or M14. This is reasoning from the code.)

**Fix I would accept.** All three parts, with M01–M15 added as D5 controls (each must be rejected), and the genuine tree
passing:
* **(a) A runtime backstop, outside the ratified ASTs.** Strengthen `_assert_execute_context` for `kind == "PRODUCTION"`:
  * **arming:** `G.premarker_check(G.PRODUCTION)` must pass, and the run nonce must exist in the git dir with this
    process's pid and token;
  * **`_persist_pending`:** the marker must exist and name a commit carrying the grant path, and either the live nonce
    holds (in execute) or the seal-only guards have run.

  No grant exists before the owner's grant, so no caller can then mutate a production ref through the sites, however the
  call is reached. This closes classes 5, 6 and 7 at runtime. The sites' hashes are unchanged. The change strengthens the
  sites' precondition in the fail-closed direction, and should be reported to the owner with the D5 record.
* **(b) Scanner: allowlist process execution instead of denylisting verbs.**
  * Scan every file in the frozen directories, not only `*.py`: forbid non-Python executables, or scan them for tokens
    and git verbs.
  * Exempt only the research guard's **path**, not the name `q309_guard.py`.
  * Every call that can start a process or run git is a finding unless it sits in a ratified site or a listed function,
    or unless all its arguments are literals and the verb is in a **read-only** allowlist. This covers:
    * any attribute of `subprocess`, `os.system`/`popen`/`exec*`/`spawn*`/`posix_spawn*`, `pty.spawn`;
    * aliases of those, and `getattr` on them;
    * the git runners.
  * `shell=True`, single-string commands, starred or non-literal verb positions, `-c`/alias/`--exec-path`/`--git-dir`
    options, and `exec`/`eval`/`__import__` with non-literal arguments outside listed functions are findings.
  * Filesystem writes in a function that references a git directory (`git_dir`, `.git`) are findings unless the function
    is listed. `persist_emergency`, `create_run_nonce` and `remove_run_nonce` are listed with reasons.
* **(c) T7.** Flag, in tests and qualification tools:
  * `ImportFrom` of forbidden names;
  * string constants naming a forbidden function or `_MODE`;
  * `__dict__` / `getattr` / `vars` access on the driver module;
  * any store into `_MODE`;
  * any reference to `G.PRODUCTION` / `PRODUCTION`.

### F2. The `authority` placeholder test is a trap, and there is no validation before the grant commit

* **Where.**
  * `p309_driver.premarker_admission` rejects any `authority` containing one of `PLACEHOLDER_MARKS = ("<", ">", "SET BY
    THE OWNER", "TBD", "TODO")`.
  * The proposal says `"<THE OWNER'S GRANT INSTRUCTION, verbatim reference>"`.
* **Failure scenario.**
  1. The owner puts the grant instruction, or a quote of it, into `authority`. The owner's messages routinely contain
     "->".
  2. `execute` refuses before the marker. That part is safe.
  3. The grant commit G cannot be superseded. A second grant commit G2 makes G1 a non-window, non-record commit between
     Rv and G2, so `check_grant` refuses forever. Recovery would need a history rewrite, which the owner forbids.
* **Fix I would accept.**
  * Detect only the proposal tool's exact placeholder strings, or make `authority` a structured field, for example
    `{"message_sha256": <64 hex>, "received_utc": …}` validated by format.
  * Add a read-only candidate-grant validator. It runs `check_grant`'s field checks, `premarker_admission` and the guard's
    `premarker_check` on an **uncommitted** grant file, for example in a light sandbox, or through a pure-function
    refactor.
  * The handoff tells the owner to run the validator (or have it run) before making the grant commit. It also states that
    a grant commit that `execute` refuses cannot be repaired without a new owner decision.

---

## 3. Task 1: B1–B8

| finding | fix (code) | exercised by | status |
|---|---|---|---|
| B1 cell from the grant | `expected_cell` (production: the CUSUM row of the pinned `cells.json`, read with `cover_rat`/`cover_interval` in the sum form, FE-9) and the cross-check with the consumer's cover. **Checked:** `k5_minimality.load_cells` returns the raw rows, so `cover_interval(con["cover"][309])` is well defined (masked skeleton). `premarker_admission` requires `grant.cell_interval == C` and `drift_hull_Ew == cell_blocks(C)[0]`. C feeds the control, Stage 1a, Stage 1b and Stage 2 | QC11 A01 (a same-width shifted cell is refused pre-marker); I03 (the whole evaluation); `cover_interval` also in QC09 and in FE-9's 326-cell check | **closed**. Residual accepted: the production `expected_cell` branch is exercised only at `execute`, because reading the target row before the freeze is excluded (C4) |
| B2 P10 / P5 | the top-level `stage1a` (`after_marker`); a strict `reverify` (an evaluated record without `stage1a` fails, and the sets must be equal); postexec refuses to start without `-I -S -B` | I01 (the real variant in review mode, TEST context, 16 h3 certificates: P10 true); I02 (one wrong sealed verdict: P10 false); P5 on the flags path | **closed** |
| B3 dry admission | `premarker_admission` plus the guard's `premarker_check` (checks 2–6, 8, 9; check 7 with an empty namespace; attached HEAD); `check_branch`; the 14-day horizon; `issued_utc`; `authority`; the committer identity | QC11 A02–A17 (the D2 codes and unchanged refs); guard PM1–PM3 | **closed**, except F2 (the `authority` test) |
| B4 job end | `run_jobs`: a budget stop only for SIGXCPU with `cpu ≥ limit − 0.05 s`, or SIGKILL with `cpu ≥ limit`; else JOB_EXCEPTION. `RLIMIT_CORE = 0`; children run `-I -S -B` | S06 (genuine SIGXCPU: TERMINATED at cpu 1.005 for a limit of 1); S15 (SIGKILL: JOB_EXCEPTION); S17 (kill -XCPU below the limit: JOB_EXCEPTION) | **closed**. **Delta-2 E2 confirmed**: it also closes the residual SIGXCPU lever I noted |
| B5 grant window | A23: `_chain_kind` (record / freeze_record / window / chain), window commits only between Rv and G | A19 (window commits allowed); A20–A22 (the wrong paths or the wrong place are refused) | **closed** |
| B6 reasons | `_RecordingVerifier` (same `__file__`, so `verifier_identity` is unchanged); `stage1a.verdict_details`; a job whose reasons do not cover its verdicts raises | I03 (`verdict_details` equals the verdict keys) | **closed** |
| B7 QC blind spots | (a) `evaluate()` is one body for `execute` and I03; (b) `check_flags`, `check_grant` fields, the B1/B3 checks and the context-specific result path now run in the sandbox; (c) `ledger/FREEZE_RECORD.json`, checked by `recorded_freeze`, QC13, the runner, the proposal tool and `check_grant`; (d) E1-1 positive | (a) I03; (b) A-flows, F-flows; (c) A23–A25 and QC13; (d) A18 and guard N7i; also guard N7j (detached HEAD) | **closed** |
| B8 retry | `p309_qualify`: one `attempt_1/`, created exclusively, every file O_EXCL; the runner refuses if any attempt exists; delta-2 E6 adds one ledger start line, and QC13 checks there was exactly one run after the freeze record | code reading | **closed** |

---

## 4. Task 2: NB1–NB15

**Applied:**
* **NB1**, taint tracking. My snippets M16–M18 are now caught. F1 is a different class of evasion.
* **NB3**, the tripwire uses `own_bands`.
* **NB4**, hooks are refused outside a sandbox (A26).
* **NB5**, a control exception gives CONTROL_FAILED; any other pre-marker exception gives exit 2.
* **NB6**, the pid-bound run nonce (S16).
* **NB7**, `job_mode` labels.
* **NB8**, `issued_utc` and `authority` are checked (but see F2).
* **NB9**, the README states the shared top-level session and that no separate agent id is available.
* **NB10**, A30.
* **NB11**, the immutable list is extended.
* **NB12**, light sandboxes.
* **NB13**, the freeze parameters carry `## 7. Conditions` and this file's `## Conditions`.
* **NB14**, children run `-I -S -B`.
* **NB15**, the proposal tool's procedure text (`__pycache__`, branch, flags).

**Residuals: the coordinator's view, and my ruling:**
* **NB6, no guard refusal while an emergency file exists.** **Accepted.** The nonce binds target jobs. There remains an
  accepted residual: while HEAD = G and the marker is the only ref in its namespace (during `execute`, or after
  CONSUMED_UNRECORDED), official admission is open to a *direct* caller such as the variant CLI. That would be in-band
  verification by deliberate misuse, not a ref mutation.
* **B7(b), `check_bindings` and `check_governance_state` production-only.** **Accepted.** They are exercised by
  `preflight`, QC13 and the self-audit on this repository.
* **B7(b), the sandbox's guarded paths are its own TEST paths.** **Accepted.**
* **No QC11 flow for the committer identity.** **Accepted.** `git var GIT_COMMITTER_IDENT` resolves the identity exactly
  as `commit-tree` does.
* **NB2 in QC11.** **Accepted.** Every refusal flow is a single defect on a base chain that is shown valid (F26, F27, A18,
  A19). The guard tests assert reasons.

**New non-blocking notes:**
* **NF1.** `premarker_admission`'s worktree check passes when `execution_host.worktree` is missing and the cwd is the
  repository root. Require the field to be present.
* **NF2.** An attempt directory can be deleted before the Q commit. E6's ledger anchoring detects a second run only if the
  ledger line is kept, so the qualification reviewer should check the ledger together with the attempt tree.

---

## 5. Task 3: R4-C2 runs

The runs used a wrapper, `scratchpad/r4/r4c2_run.py`. It runs the committed test functions unchanged, with only each
module's `SCRATCH` path redirected into `scratchpad/r4`, so that the coordinator's concurrent dry run was not disturbed.
Evidence went to `scratchpad/r4/evidence`.

| suite | at | result |
|---|---|---|
| `tests/test_p309_exactly_once.py`, under `python3 -I -S -B` | 44b10d63-code | 91/91 |
| the same | **70927a08** | **92/92** (F 45, A 26, S 17 including S17, I 3, Z 1) |
| `tests/test_p309_guard.py` | 44b10d63-code; unchanged since | **60/60** |
| `tests/test_verify_scoped.py`, as committed | unchanged since | **37/37 OK** (108 s) |
| `tests/test_p309_d5_exception.py`, under `-I -S -B` | 44b10d63-code | 54/54 |
| the same | **70927a08** | **54/54** |
| `code/p309_scan_pins.py --list` | 70927a08 | every whitelist entry has a ref-moving call and is current; nothing is unlisted |

---

## 6. Task 4: owner D5, step 1

**What holds.**
* The sites are unique module-level functions, with the ratified hashes.
* The allowance sanctions only those two, for exactly those names. The author's controls C01–C04 (an additional site, a
  duplicate, a copy in another file) are rejected.
* T4: each site starts with the context assertion, and is called only from `run_execute`, `after_marker` and
  `run_seal_only`.
* T6: arming is dominated by `check_grant`, the dry admission and the nonce, in top-level statements. The pending ref in
  seal-only sits behind its three guards.
* The 22 `ref_mutation_functions` entries are each necessary (each has a ref-moving call), and each reason is true:
  * the checkpoint push moves only the explicit branch refspec;
  * `seal_blob` moves only `ctx.branch_ref`, under `refs/heads/`;
  * the context functions, `_check_official` and `_admission` use the read form `symbolic-ref -q HEAD`;
  * the test and helper entries operate on scratch sandboxes only.
* `token_definitions` has one entry, the sandbox helper's refusal constant, which is necessary.
* `planted_control_files` lists the two controls; C18 shows the control mark cannot exempt another file.
* `p309_scan_pins.py` refreshes only listed entries and never touches `exactly_once_sites` (code reading).

**What fails.** F1. The scanner's rejection of classes 1–7 depends on the call shape. Fifteen realistic shapes evade it,
and the sites have no runtime backstop against a caller without a grant. Hence **NO**. With F1's fix (a)–(c), and M01–M15
rejected as controls, I would expect to answer YES.

---

## 7. Task 5: readiness

Apart from F1 and F2, nothing else blocks the freeze:
* the delta-2 review is accepted (E2 confirmed here);
* FE-10 is limited to the mirror paths and the pins;
* the freeze manifest is to be regenerated (111 code pins).

Before the freeze, the full dry run of the QC runner should end at the final tree with every gate passing. The
coordinator is running it.

---

## Conditions

* **R4F-C1.** F1 is fixed: the runtime backstop in `_assert_execute_context` (the sites' ASTs unchanged) and the hardened
  scanner and T7. My mutants M01–M15 are added as D5 controls, each rejected, and the genuine tree passes. The
  strengthened site precondition is reported to the owner with the D5 record.
* **R4F-C2.** F2 is fixed: a narrow or structured `authority` test, a candidate-grant validator run before the owner's
  grant commit, and handoff text stating that a refused grant commit is terminal without a new owner decision.
* **R4F-C3.** A focused confirmation by R4 or another independent reviewer, at the tree containing both fixes:
  * the D5 control suite;
  * my mutant suite (`scratchpad/r4/d5_mutants.py`, or an equivalent committed copy);
  * one QC11 run under `-I -S -B`.

  Only then `D5_EXCEPTION_LIMITED_TO_RATIFIED_SITES: YES` and FREEZE_APPROVED.
* **R4F-C4.** R4-C3 is satisfied (the owner ratified D5). R4-C4 stands (D2 unchanged; the E2 precision is confirmed).
  NF1 and NF2 are applied or recorded as accepted residuals.

---

## 8. Disclosures

**Reads.**
* FNS and RNS, and git metadata.
* Masked skeletons (`code/code_skeleton.py`) of:
  * `consumption_adapter.frozen_components`;
  * `k5_minimality.load_cells` / `rat`, the cover loader, to check B1's cross-check. Only the row structure was seen, no
    cell entry.
* No other consumer code. No target input. No 305–309 value.

**Indirect reads by the test code I ran.**
* The 44b10d63-code QC11 run's old I03 read the cell-307 campaign's decoy results file for cover cell 297 and the
  `cells.json` row of cell 297. Both are decoys and out of band, and nothing was displayed.
* The 70927a08 run no longer reads them (E4).

**Executions** (ledger UTC, notes prefixed "R4 reviewer:"):

| UTC | what |
|---|---|
| 05:00:33 | skeletons |
| 05:03:03 | D5 mutants |
| 05:06:02 | guard tests (60/60) |
| 05:06:23 | QC11 (91/91) |
| 05:06:25 | D5 controls (54/54) |
| 05:10:21 | variant tests (37/37; the test also writes its own per-test lines) |
| 05:13:18 | QC11 at 70927a08 (92/92) |
| 05:13:23 | D5 controls at 70927a08 (54/54) |
| 05:17:27 | D5 mutants at 70927a08 |
| 05:19:13 | `p309_scan_pins.py --list` (read-only) |

**How the executions were contained.**
* Sandboxes were light repositories under `scratchpad/r4`, with TEST names only. They were deleted.
* Mutant copies were parsed only, never executed, and deleted.

**What was never done.**
* `execute` and `seal-only` were never run on this repository.
* No ref was created under `refs/p5y-k5-cell309-p309-r1/` anywhere: 0 here, and 0 `refs/p309-test/` here.
* The production grant path was never written.
* No git write was made.
* No kernel ran in the band.
* M13 and M14 were never executed.

**Writes.** This file only, plus the ledger lines through `p309_env`.

NEW Γ309 TARGET EVALUATIONS = 0.
