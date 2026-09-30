# Independent pre-freeze review R4, follow-up 3 (R4F2-C3 focused re-confirmation and the D5 exception), formal campaign p5y_k5_cell309_p309_r1
FREEZE_BLOCKED
D5_EXCEPTION_LIMITED_TO_RATIFIED_SITES: YES

**Reviewer.** R4, the author of `reviews/REVIEW_PREFREEZE_R4_P309.md` (879e6908), `…_FOLLOWUP_P309.md` (68019506) and
`…_FOLLOWUP_2_P309.md` (FREEZE_BLOCKED, D5 NO; preserved with its ledger and mutant suites). R4 wrote none of the
reviewed code. R4 is not R1–R3, the incident-independence reviewer, the delta reviewer or the verifier's author. Brief:
`reviews/BRIEF_PREFREEZE_R4_FOLLOWUP_3_P309.md` (committed before issue, bfa18252).

**State reviewed.**
* The code is as of **bfa18252**, the commit that adds the brief.
* The coordinator's addendum put **8a380f19** (tip d618961f) in scope. I checked its diff against bfa18252: it changes
  only two handoff-text files (`make_freeze_params.py`, `make_proposed_authorization.py`) for H2–H4. The driver, guard,
  scanner, static check, tests and config are byte-identical to bfa18252.
* I recomputed, at this tree, the two ratified site hashes and the four A38 backstop pins:
  * `_arm_marker` `1ee764b7…`, `_persist_pending` `13ee3ec3…` (owner-ratified, unchanged);
  * `_assert_execute_context` `c8a2fb51…`, `_site_backstop` `80d206ad…`, `_require_own_run_nonce` `23f3021d…`,
    `_SITE_CODES` `696a6102…` (the values I recorded in follow-up 2; now pinned by A38).

---

## 1. Verdict in brief

**FREEZE_BLOCKED**, on one finding (F4). **The D5 exception is now limited to the two ratified sites:
`D5_EXCEPTION_LIMITED_TO_RATIFIED_SITES: YES`.**

**My follow-up-2 findings are resolved.**
* **F3 is closed.** Schema 5's closed-world allowlists (A37) reject every one of my 54 round-3 mutants. Each one that
  passed at the follow-up-2 tree is now rejected; the genuine tree still passes.

  | group | follow-up 2 | this tree |
  |---|---|---|
  | N01–N20 (schema) | 3/20 rejected | **20/20 rejected** |
  | K01–K04 (composite test paths) | 0/4 | **4/4 rejected** |
  | T7a–T7d (T7) | 2/4 | **4/4 rejected** |
  | T8a–T8c (backstop neutered, same shape) | 0/3 | **3/3 rejected (T8 equality)** |
  | R01–R23 (runners and their env) | 21/23 | **23/23 rejected** |
  | M01–M18 (round-2 suite) | 18/18 | **18/18 rejected** |

* **The backstop is pinned (A38).** T8 is now an equality check against the four pinned hashes. My in-driver
  neuterings T8a–T8c, which T8 passed before, now fail T8. The three functions and `_SITE_CODES` are byte-for-byte the
  code I reviewed.
* **R4F2-C2 (delta-3 G4) is done (A39).** `validate-grant` runs `execute`'s read-only pre-marker checks under the same
  conditions as `run_execute`, and T9 checks that statically.
* **NF3, NF4 (A41) are done.** QC11 V10 (a window commit between validation and the grant) and QC13
  `execution_ledger_append_only_since_the_freeze`.
* **NF5 and the coordinator's finding (A40) are addressed for `execute`.** `execute`'s git is hermetic
  (`GIT_CONFIG_NOSYSTEM`, `GIT_CONFIG_GLOBAL=/dev/null`, a fixed identity), and `check_host_git` refuses before the
  marker unless the repository config is allowlisted and no hook is present.

**Runs at this tree** (`-I -S -B`):

| suite | result |
|---|---|
| D5 controls `tests/test_p309_d5_exception.py` (incl. N/K/T7/T8/R and M01–M15) | **155/155** |
| backstop controls `tests/test_p309_site_backstop.py` | **27/27** |
| QC11 `tests/test_p309_exactly_once.py` (incl. V10) | **104/104** |
| QC12 static T1–T9 (independent) | **9/9 pass** |
| my round-3 suites (N, K, T, R) and M-suite, static only | every mutant rejected; genuine passes |
| allowlist ablation (in memory) | §3 |

**The blocking finding: F4.** A40 makes `execute`'s git hermetic and adds `check_host_git`, but that guarantee does not
cover the whole sealing path. `run_seal_only` does not call `check_host_git` before its first git call. A git hook or a
disallowed repository-local config key added on the host between `execute` and `seal-only` would run at seal-only's
`update-ref` (the pending ref, or the branch) or `commit-tree`. This is the delta reviewer's note, left for my ruling.
My ruling is that it **must** call `check_host_git` (R4F3-C1). It is a one-line use of an already-reviewed, read-only
function; and under H7/H8 any later change to the git environment is a new delta, so it has to be done now, before the
freeze. Because it is a hole in the A40 binding for a ref-writing path, I make it blocking.

**Why the D5 line is YES despite the block.** F4 is about a host-configured program running during the recovery seal.
It is not an additional marker or pending mutation site, and it is not a way to mutate a production ref outside the two
sanctioned sites. The seven owner classes are all rejected, the backstop is pinned, and the two sites are unchanged. So
the D5 exception is limited to the ratified sites. F4 blocks the freeze on a different axis (the A40 host-git binding),
not on the D5 site question.

---

## 2. Tasks 1 and 2: R4F2-C1 and R4F2-C2 at this tree

### 2.1 R4F2-C1 (a)–(i): closed-world allowlists (A37)

I checked each part against `code/p309_scan.py` layer 6, `code/p309_static_check.py`, the allowance and the genuine
tree, and against my mutants.

* **(a) Imports.** `import_policy.allowed` is per directory; `import_policy.forbidden` is exactly the modules I named. A
  forbidden module is allowed only through an `import:<module>` reviewed permit or a hash-bound module-level exemption.
  Relative imports are findings. Rejected: N02 (runpy), N09 (pickle), N10 (code), N17 (multiprocessing), K02
  (inspect); N01/N03/N08 also raise IMPORT_UNLISTED.
* **(b) Introspection.** `INTROSPECTION_CALLS`, `INTROSPECTION_ATTRS`, `EXEC_NAMES`, `sys.modules`, `__builtins__`, and
  `getattr`/`setattr`/`delattr`/`hasattr` with a computed name or on a module, are findings outside the pinned backstop
  and reviewed `introspection` permits. Rejected: N07, N08 (builtins exec), T7a, T7b, T7c, T7d, K01, K04.
* **(c) Module stores (T7).** `MODULE_ATTRIBUTE_STORE` now fires on a store to an attribute of **any** module object,
  resolved through `FileCtx.module_of_expr`: import alias, local alias (`h = GG`), an attribute of another project
  module (`P.D`, `D.G`), or a `sys.modules`/`import_module` lookup. `T7_PATCHABLE` is gone. Rejected: N14, N15, N16,
  K01, K03, K04.
* **(d) Environment.** `env`/`env_extra` outside a reviewed runner must be `None`, a fixed module-level environment, or
  a literal dict with keys in `env_keys` (`GIT_INDEX_FILE`); `os.environ` mutation is a finding. Rejected: N04, N05,
  N06, N18, N19, N20, R21, R22, R23 (ENV_UNLISTED).
* **(e) Git verbs and options.** Each verb has its own option list; a verb absent takes none; `--end-of-options` ends
  option parsing. Rejected: N12, N13 (`git grep -O` / `--open-files-in-pager` — `grep` is gone anyway). Forwarded
  operands: `_forward_findings` requires a validation spec for `mirror`, `Sandbox.commit` and `_changed_paths`, and the
  verifier author added `--end-of-options` in `verify/scoped_sandbox.py` (A42), which I read.
* **(f) Tokens and paths.** `fold` now resolves `chr()`, `'<sep>'.join([...])`, `.decode()`, `.lower()`,
  `.replace(lit,lit)`, and bytes literals; the token/alias rules cover bytes constants; an unresolved piece directly
  under the repository root, or one that could complete a git-internal name, is a REF_FILE_WRITE. Rejected: N01 (bytes
  marker literal), N11 (`chr()` ref path).
* **(g) Backstop pins.** `backstop_pins` holds the four AST hashes; T8 is equality; `p309_scan_pins.py` never
  refreshes them. Rejected: T8a, T8b, T8c.
* **(h) `p309_postexec.py`.** Its blanket exemption is now a `FORBIDDEN_NAME`-only, hash-bound `t7_exemptions` entry.
  T7d (the composite in `p309_postexec.py`) is rejected.
* **(i) Controls.** All of N01–N20, K01–K04, T7a–T7d, T8a–T8c and R01–R23 are D5 controls, each rejected; the planted
  formal control fires IMPORT_UNLISTED, INTROSPECTION and ENV_UNLISTED (P0d).

**Necessity, by in-memory ablation** (`scratchpad/r4/perm_ablation5.py`, 2055 s). I removed each allowance entry in
turn and re-scanned the genuine tree read-only (for `t7_exemptions`: re-ran T7).

| allowlist | necessary (removal makes the genuine scan/T7 fail) | over-provisioned (removal is inert) |
|---|---|---|
| `reviewed_functions` permits (49) | **all** | none |
| `git_runners` (20) | **all** | none |
| `ref_mutation_functions` (17) | **all** | none |
| `env_keys` (1) | **all** | none |
| `import_policy.module_level_exemptions` (2) | **all** | none |
| `git_read_verbs`, `git_object_verbs` | **all** | none |
| `t7_exemptions` rules | **all** | none |
| `import_policy.allowed` | — | `code::importlib`, `tests::c2_d5_forecast`, `tests::tct_rule` |
| `git_verb_options` | — | `diff-tree --diff-filter=` |
| forwarded specs | protective (see below) | `Sandbox.commit::parents`, `Sandbox.commit::message` |

* **All the security-bearing lists are minimal.** Every permit, runner, ref-mutation function, env key, module-level
  exemption, git verb and T7 exemption is necessary: removing it makes the genuine tree fail.
* **The over-provisioned entries are a tightening opportunity, not a defect (NF9).** `code::importlib` (the code/
  files import only `importlib.util`, through a permit, not plain `importlib`), `tests::c2_d5_forecast` and
  `tests::tct_rule` (no test imports these consumer modules), and `diff-tree --diff-filter=` (the tree uses
  `--diff-filter` on `log` and as a forwarded operand, not on `diff-tree`) are allowed but unused; removing them
  narrows the surface. `read-tree --end-of-options` and `archive --end-of-options` are redundant list entries, because
  `--end-of-options` is always accepted as a terminator by `classify_git` before the per-verb check.
* **The two "over-provisioned" forwarded specs are protective, not removable.** `Sandbox.commit`'s `parents` and
  `message` specs enforce `--end-of-options` / option-argument placement on the forwarded operands; the genuine tree
  satisfies them, so their removal is inert against genuine code, but they bite mutated code. Removing all of a
  function's forwarded specs raises `FORWARD_UNVALIDATED`; keep them.

**Reasons I read against the code.** The two module-level `multiprocessing` exemptions (the verifier author's worker
pools; the workers run the variant's own functions, no program is started); the `introspection` permits
(`exec_module`, `_ind`, `_load_certifier_isolated`, `job_stage1a`, the guard's `__getattr__`/`object.__setattr__`
setters and `_Production.__init__`'s `globals()`, `stage_flows`' `sys.modules` diff, the verifier's TestContext); the
`import:importlib.util` permits (`job_stage1a`, `reverify`, `decoy_gate`); `env_keys = ['GIT_INDEX_FILE']`; the
per-verb option lists; the forwarded specs; and the extended `t7_exemptions`. Each reason is true.

### 2.2 R4F2-C2: validate-grant's added checks and T9 (A39)

`validate_grant` runs, through `run_check`, `check_flags`, `check_host_git`, `check_branch`, `check_not_evaluated`,
`check_result_paths`, `check_clean`, and (PRODUCTION only) `check_bindings` and `check_governance_state`; it records
each in `execute_prechecks`, and `pass` requires them all. **T9** (independently PASS) checks that `validate_grant`
calls the unconditional six in both it and `run_execute`, and calls the two PRODUCTION-gated ones under the identical
condition `ctx.kind == 'PRODUCTION'`. QC11 V01/V09/V10 confirm agreement with `execute`. The `grant_validation` text
now lists these checks, says a PASS does not guarantee admission, and (H4) says `execute` re-evaluates the horizon and
expiry when it starts. Accurate for this code.

---

## 3. Task 1 (ablation) and the whitelist

The ablation result is in §2.1. Over-provisioning, if any (options or verbs the genuine tree does not use), is a
tightening opportunity, not a security defect: each allowlisted option is a specific literal flag. I note any such
entries in the ablation block; removing them narrows what a future mutant could use.

---

## 4. Task 3: A40, the hermetic environment and check_host_git

**The environment.** `ENV` adds `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL=/dev/null` and a fixed
author/committer `p309-execute`. So `execute`'s driver git ignores the host's system and global config.

**`check_host_git`.** Right after `check_flags`, before any git call that could start a program, it lists
`git config --list --show-scope --name-only` and refuses unless every key is in local or worktree scope and matches
`REPO_CONFIG_ALLOWED`, and the hooks directory holds no live hook. It runs in `execute` and in `validate-grant`.

**Is the allowlist safe and sufficient for the driver's git?** For the driver's own git calls, yes.
* `REPO_CONFIG_ALLOWED` is core format/file-mode keys, remote url/fetch/pushurl, branch remote/merge/rebase, `gc.auto`,
  user name/email, and two extensions. None of these names a program to run.
* I confirmed in a throwaway scratch repository (`scratchpad/r4/gitexp.py`) that, under the hermetic `ENV`,
  `git config --list --show-scope` reports only local scope, and a global `commit.gpgSign` is invisible and inert to
  the driver's git.

**Does a correct run seal differently?** No, consistent with the delta-4 review's task 2.
* `commit-tree` with `commit.gpgSign` but no `-S` does not sign (I confirmed this in the scratch repo), so the fixed
  identity and no-signature seal change nothing an existing check reads. `A21 committer_identity` now always passes;
  harmless.
* The Stage-1 jobs receive `ENV` (six git vars); the job code reads no environment variable and runs under `-I`, so
  the computation is unaffected.

**F4 (blocking): the guarantee does not cover the whole sealing path.**
`run_seal_only` calls `check_flags` and `check_branch` but not `check_host_git`, then runs `git rev-parse`,
`_persist_pending` (`update-ref` of the pending ref) and `seal_blob` (`commit-tree`, branch move). `seal-only` does use
the hermetic `ENV`, so system and global config are already ignored; the gap is a **repository-local** hook or a
disallowed repository-local config key added between `execute` and `seal-only`. A `reference-transaction` hook would
run at seal-only's `update-ref`, and the hook still runs even if it then aborts the update. `seal-only` is a separate,
later invocation, so its exposure window is larger than execute's pre-marker window, not smaller. This does not risk a
second target evaluation, but it defeats A40's stated guarantee for the recovery path. Condition R4F3-C1.

**NF6 (residual): the guard's and verifier's git wrappers are not hermetic.** `code/p309_guard.py` (`_git`,
`_git_bytes`, `_git_ok`) strips `GIT_*` but keeps `HOME`, so it reads the host's `~/.gitconfig`; the verifier's
`_run_git` sets a few `GIT_*` vars but not `GIT_CONFIG_NOSYSTEM`/`GLOBAL`. `check_host_git`, run under the driver's
hermetic `ENV`, cannot see host global or system config, so A40's guarantee does not extend to the guard's git calls
during pre-marker admission (`premarker_check` → `_check_official` → `git log --format=%H --diff-filter=A HEAD -- <grant>`).
I confirmed in a scratch repo that `git log --format=%H … -- <path>` with `log.showSignature=true` on a signed commit
runs the signing/verify program and prepends signature lines to stdout (which would corrupt the guard's one-commit
count → a fail-closed refusal). The realistic trigger (a host **global** `log.showSignature`) is uncommon, and the
common case (a global `commit.gpgSign`, as on this host) does not affect the guard's `log --format=%H`; the guard's
other verbs read blobs (`show <rev>:<path>`), for-each-ref, rev-parse and diff-tree `--name-only`, which do not run a
program. So this is a residual, not a blocker. **Recommended:** make the guard's and verifier's git wrappers hermetic
(set `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL=/dev/null`), or have `check_host_git` also vet the host global/system
config; whichever is chosen, it is part of the frozen git environment under H7.

**NF7 (residual): `check_host_git` is a pre-flight (time-of-check) test.** A hook or config added after the check but
before a later git write would still run: between the check and `execute`'s post-marker seal (the evaluation duration),
and — closed by R4F3-C1 — between `execute` and `seal-only`. The marker window (check to `_arm_marker`) is short. This
is inherent to a pre-flight check; re-checking `check_host_git` immediately before the post-marker seal would remove the
intra-execute window. Post-marker, no re-evaluation is at risk. Recommended, not required.

**NF8 (test coverage): no negative control for `check_host_git`.** Its refusal path (a disallowed repository config
key; a present hook) is not exercised by any control; QC11 only exercises the passing path (a clean sandbox). Add a
control that plants a disallowed key and a hook in a sandbox and asserts a `HOST_GIT` refusal before the marker.

**On this host.** git 2.43; the repository's own config keys are all inside the allowlist (the only out-of-allowlist
keys are command-scope keys from the session environment, which the fixed `ENV` does not inherit); no hooks. So no
spurious refusal is expected. The execution host remains the owner's choice.

---

## 5. Task 4: R4F2-C3 runs

All under `python3 -I -S -B`, `P309_EVIDENCE_DIR=scratchpad/r4/evidence3`. Test modules ran unchanged through my
wrapper `scratchpad/r4/r4c3_run.py`, which only redirects `SCRATCH` into `scratchpad/r4`, so the coordinator's runs
were undisturbed. Sandboxes were light repositories with TEST names only, all deleted.

| run | ledger UTC | result |
|---|---|---|
| backstop controls | (evidence3/R4C4_backstop.json) | **27/27** |
| QC11, all flow groups incl. V10 | (evidence3/R4C4_qc11.json) | **104/104** |
| D5 controls | (evidence3/R4C4_d5.json) | **155/155** |
| QC12 static T1–T9 (independent) | run5_static.log | **9/9 PASS** |
| my M-suite M01–M18 (static) | run5_r5_mutants1.log | 18/18 rejected; M00 passes |
| my N suite (static) | run5_r5_mutants2.log | 20/20 rejected; N00 passes |
| my K suite (static) | run5_r5_mutants3.log | 4/4 rejected; K00 passes |
| my T suite (static) | run5_r5_mutants4.log | 7/7 rejected; T00 passes |
| my R suite (static) | run5_r5_mutants5.log | 23/23 rejected; R00 passes |
| allowlist ablation | run5_ablation.log | §2.1 |
| scratch git experiments (A40) | run5_gitexp.log, run5_guardenv.log | §4 |

The counts match the coordinator's dev results (D5 155/155, backstop 27/27, QC11 104/104).

---

## 6. Task 5: R4F2-C4 (NF3, NF4, NF5)

* **NF3 (V10): accepted.** QC11 V10 validates, makes one ledger-only window commit touching both ledgers, commits the
  candidate alone, and `execute` admits it. It passes.
* **NF4 (append-only ledger): accepted.** QC13 `execution_ledger_append_only_since_the_freeze` checks that every
  committed version of the execution ledger from the freeze to HEAD, and the working copy, is a byte prefix of the
  next. The qualification-review brief addendum 4 asks the reviewer to confirm it independently.
* **NF5 (hermetic host git): accepted for `execute`, with F4 and NF6 outstanding.** `execute`'s driver git is
  hermetic and `check_host_git` guards it. The recovery seal (F4) and the guard/verifier wrappers (NF6) are not yet
  covered.

---

## 7. Task 6: readiness

The delta-4 conditions H1–H8 are the coordinator's and the delta reviewer's; I checked only that the text-only changes
for H2–H4 landed (they did, in 8a380f19) and that H6/H7 refer to a true state (the sites and the backstop carry the
pinned hashes I recomputed at this tree). H7 freezes `ENV`, `REPO_CONFIG_ALLOWED` and `check_host_git` "as R4 follow-up
3 confirms them" — so R4F3-C1 (and, if adopted, NF6) must be settled before that confirmation is final; that is the
reason F4 is blocking rather than deferred.

Apart from F4, nothing else blocks the freeze from my side. B1–B8, F1, F2 and F3 are closed; the D5 exception is
limited to the ratified sites; the runs pass.

---

## Conditions

* **R4F3-C1 (F4; before the freeze).** `run_seal_only` calls `check_host_git(ctx)` before its first git call (before
  the `rev-parse` of the marker), so that a repository-local hook or a disallowed repository-local config key added on
  the host between `execute` and `seal-only` is refused before seal-only's `update-ref` or `commit-tree`. It is
  `execute`'s own already-reviewed, read-only check; no new behaviour. A control plants a hook (and a disallowed
  repository config key) in a sandbox and asserts that `seal-only` refuses with `HOST_GIT` before writing any ref
  (this also discharges NF8's negative control for the shared function).
* **R4F3-C2 (NF6, NF7, NF8; recommended, the owner's or coordinator's call).**
  * **(NF6)** Make the guard's git wrappers (`code/p309_guard.py` `_git`, `_git_bytes`, `_git_ok`) and the verifier's
    `_run_git` hermetic (`GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL=/dev/null`), or have `check_host_git` additionally
    reject any host global or system config key that could run a program on a read (for example `log.showSignature`
    with a signing program, `core.fsmonitor`, `core.pager`, or `include`/`includeIf`). Whichever is chosen becomes
    part of the git environment frozen under H7.
  * **(NF7)** Re-run `check_host_git` immediately before the post-marker seal in `run_execute`, to close the
    time-of-check window between admission and the seal.
  * **(NF8)** If R4F3-C1's control does not already cover it, add a negative control for `check_host_git`'s refusal
    path.
* **R4F3-C3 (re-confirmation).** A focused re-confirmation by R4 or another independent reviewer at the tree that
  applies R4F3-C1 (and any of R4F3-C2 that is adopted): the D5 controls, the backstop controls, QC11, QC12 T1–T9, and
  the new `check_host_git` refusal control. Only then FREEZE_APPROVED. `D5_EXCEPTION_LIMITED_TO_RATIFIED_SITES: YES`
  already holds at this tree and R4F3-C1 does not affect it (F4 is not a ref-mutation-site question).
* **R4F3-C4 (standing).** At the freeze, the two sites keep the owner-ratified AST hashes
  (`1ee764b7…`, `13ee3ec3…`) and the backstop keeps the A38 pins (`c8a2fb51…`, `80d206ad…`, `23f3021d…`,
  `696a6102…`); the R4 follow-up-2 item is cited as resolved and this review's verdict is cited (H6).

---

## 8. Disclosures

**Reads.**
* FNS and RNS files, and git metadata.
* The diff bfa18252 ← 046b63aa, and 8a380f19 ← bfa18252.
* `governance/P309_REV2C_AMENDMENTS.md` (Fourth delta, A37–A42) and the `D5_SITE_BACKSTOP_REPORT` addendum.
* `reviews/REVIEW_DELTA4_INCIDENT_P309.md` (H1–H8, and its A40 analysis, task 2) and the qualification-review brief
  addendum 4.
* `code/p309_driver.py`, `code/p309_guard.py`, `code/p309_scan.py`, `code/p309_static_check.py`,
  `code/p309_qualify.py`, `verify/scoped_sandbox.py`, `verify/srk_verify_indep_scoped.py`, and the test files.
* The execution ledger, to separate my runs from the coordinator's.
* No consumer code, no target input, no 305–309 value. I did not open THEOREM_TCT.md.

**Indirect reads by the test code I ran.** QC11's integration flows verify the committed TEST-band decoy certificates
in review mode and compose the a2_h5 decoys with manufactured Stage-1b records. No cover-cell entry and no campaign
results file is read; nothing was displayed.

**Executions.** All carry notes prefixed "R4 reviewer:" and `new_target_evaluations` 0, on 2026-09-30 (ledger UTC; a
suite that appears twice was re-run with output captured):

| UTC | what | class |
|---|---|---|
| 09:00:53 | scratch git experiment: signing / showSignature (throwaway repo) | SYNTHETIC |
| 09:03:07 | backstop controls, 27/27 | SYNTHETIC |
| 09:03:09 | QC11, 104/104 | NONTARGET_DECOY |
| 09:03:09 | D5 controls, 155/155 (finished ~09:38) | GOVERNANCE |
| 09:03:16, 09:04:54 | my M-suite (static) | GOVERNANCE |
| 09:03:16, 09:13:02 | my N-suite (static) | GOVERNANCE |
| 09:10:15, 09:19:22 | my K-suite (static) | GOVERNANCE |
| 09:11:38, 09:20:52 | my T-suite (static) | GOVERNANCE |
| 09:13:41, 09:22:46 | my R-suite (static) | GOVERNANCE |
| 09:03:49 | allowlist ablation (in memory) | GOVERNANCE |
| 09:27:04 | scratch git experiment: guard env vs host global config (throwaway repo) | SYNTHETIC |
| 09:31:00 | QC12 static T1–T9 (independent) | GOVERNANCE |

The exact lines are in `scratchpad/r4/evidence3/R4_FOLLOWUP3_EXEC_LEDGER.jsonl`. Results:
`scratchpad/r4/evidence3/R4C4_*.json` and `scratchpad/r4/run5_*.log`, where `scratchpad/r4` is
`/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/r4`.

**How the executions were contained.**
* Sandboxes and the two git experiments were throwaway repositories under `scratchpad/r4`, with `refs/heads/*` or TEST
  names only, never pushed, and deleted. The git experiments used a fake signing/verify program that only records its
  arguments.
* Mutant copies were parsed only, never imported or executed, and deleted.
* The ablation changed only the in-memory allowance of my own process.

**What was never done.**
* `execute`, `seal-only` and `validate-grant` were never run against this repository.
* Every mutant of the N, K, T, R and M suites was analysed statically and never executed.
* No ref was created, armed or consumed under `refs/p5y-k5-cell309-p309-r1/` anywhere; 0 such refs and 0
  `refs/p309-test/` refs here, checked after all runs.
* The production grant path was never written. No git write was made. No kernel ran in [6/5, 13/5] or its mirror.
  Nothing was evaluated for cells 305–309.

**Writes.** This file only, plus my ledger lines through `p309_env`, and scratch files under `scratchpad/r4`.

NEW Γ309 TARGET EVALUATIONS = 0.
