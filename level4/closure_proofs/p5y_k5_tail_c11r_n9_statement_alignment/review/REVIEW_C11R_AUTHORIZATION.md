# C11R -- Independent review of the Phase 13 AUTHORIZATION

- Subject (authorization commit): `377bbcbb8359a8265e37663bdda6956a357b03c3`
- Qualification commit: `c06ce3774d3cc100fd16dfbd2d1c49c29e7d1021` (qualification review preserved at `445fd84e20d63529319b616e5d6397118716f5cf`, QUALIFICATION_ACCEPTED, sha256 c81e5fb4... verified)
- Approved commit (root of trust): `ee1a6a8aab8ff57360249bc813a44b3c724200aa` (R8 review preserved at `5890511b6c74b1196112eb5d0e4d5c43b15b739e`, READY_TO_QUALIFY, names ee1a6a8a... verified)
- Branch / checkout: `p5y-k5-tail-c11r-n9-statement-alignment`, worktree `/Users/suzhe/ReBaseGuard-k5c11r` (common git dir `/Users/suzhe/ReBaseGuard/.git`), local only
- Brief: `BRIEF_AUTHORIZATION_REVIEW.md`, sha256 b7497e25dd2906d25aa1e030976e721668961346359e917fa56bdc1965c82209 (verified before starting)
- Reviewer: new, independent authorization reviewer (Claude Opus 5.5 via Claude Code); no prior involvement. Earlier reviews read as history only.
- Date: 2026-09-25 (UTC 02:21Z - 03:05Z)

Entry check: `git rev-parse HEAD` = 377bbcbb8359a8265e37663bdda6956a357b03c3; `git status --porcelain --untracked-files=all` empty (also with `--ignored`); no
`__pycache__`/`.pyc` in the three campaign code directories; no campaign process in `ps -axww`. The tree was held fixed throughout.

## Method and safety

- Everything that writes was done under `review_work/` (this directory's sibling): scratch clones `clone1` (at 377bbcbb), `clone_q` (at the issue
  point 445fd84e, with 377bbcbb made unreachable: branch and remote-tracking ref deleted, reflogs expired), `mclone` (mutation clone, reset after
  every mutation), `shallow` (depth-6 clone), and SYNTHETIC repositories `syn_*` built from scratch with FIXTURE records (my own builder, a
  re-implementation of `c11r_chain.Chain.__init__/freeze/qualify/authorize` that does not import `c11r_chain`, because that module imports the runner).
- Every Python run used the frozen interpreter under the launch policy (`env -i` allowlist, `python3.14 -I -S -B --check-hash-based-pycs default
  -X int_max_str_digits=0`, wrapper `review_work/h/run.sh`). Every harness first installs `review_work/h/guard.py`, a `sys.meta_path` blocker that
  raises on any import of `c11r_runs`, `c11r_chain`, `c11r_compare`, `c11r_table`, `c11r_regen`, and asserts at the end that none was loaded
  (all harness outputs: `forbidden_modules_loaded: []`).
- Never run: `c11r_runs.py` (in any form, anywhere), `c11r_launch.py run`, `c11r_compare.py`/`compare` with or without arguments,
  `build_authorization(fixture=False)`, `qualify --approved-commit`, `c11r_contract.py` as a program. `build_authorization` was called only with
  `fixture=True` (it writes nothing) and in synthetic repositories. No file named C11R_AUTHORIZATION.json / C11R_EXECUTION_PERMISSION.json / runs /
  comparison was written anywhere except inside synthetic fixture repositories (the scratch clones hold the committed records only because
  `git checkout` of 377bbcbb materialises them; I never wrote or edited them there). The quarantine was never read (its identity only via the
  campaign's own `git hash-object`); no original cell-306 magnitude, rounding or ratio appears in any file I wrote. Reviews were read with shell tools.
- Only permitted boundary-program starts: `c11r_launch.py qualify --self-test` and the no-argument `qualify` usage form (clone1 and mclone), plus
  direct starts of `c11r_qualify.py` with no argument (usage form) to exercise the barrier; and `c11r_status.py --verify-only` (read-only mode)
  in clone1.
- Harnesses (all in `review_work/h/`): `core.py` (read-only production verifiers), `repro.py` (byte-exact reproduction at the issue point),
  `inmem.py` (in-memory mutated records), `mutcheck.py` + `mutate.sh` (mutated scratch clone), `synth.py` / `synth32.py` / `synth_pf.py` (synthetic
  fixture repositories), `caches.py` (cache classification, no campaign import), `forge.py` + `loadcheck.py` (forged cache), `probe_driver.py`
  (shim equivalence), `driver_barrier_replica.py`. Outputs: `core_primary.json`, `core_clone1.json`, `repro.json`, `inmem.json`, `mut/*.json`,
  `synth.json`, `caches.json`.

### Reviewer procedural deviation (disclosed; corrected; no effect on the subject)

While testing the author's Phase 13 shim for equivalence (attack 22, case e5: "shim started without -B"), the shim -- which imports
`c11r_launch` from the PRIMARY code directory before it checks for `-B` -- wrote
`.../p5y_k5_tail_c11r_n9_statement_alignment/code/__pycache__/c11r_launch.cpython-314.pyc` into the primary at 11:52:03 +0900 before refusing.
I found it 12 s later, verified it is the genuine compilation of the current source (sha256 05a002d0..., byte-identical to the author's moved
genuine cache of the same file), moved it to `review_work/my_accidental_cache/` and removed the empty `__pycache__` (the code directory's
mtime is therefore 11:52 +0900). No campaign program ran in that window. Final state: HEAD 377bbcbb, porcelain (incl. ignored) empty, 0
caches in the three code directories. This is my error, not a finding against the authorization; it does expose finding F-3 about the shim.

## The subject, from bytes

`git diff-tree -r 445fd84e 377bbcbb` (replace objects off, commit-graph off): exactly two additions, mode 100644 --
`config/C11R_AUTHORIZATION.json` blob a7abbce9 (file sha256 be9ef5fe..., body digest 193b0122...) and `config/C11R_EXECUTION_PERMISSION.json`
blob 47a7a8ea (file sha256 6493d2cc..., body digest ad95eef7...). 377bbcbb has one parent, 445fd84e; the history A -> 5890511b -> c06ce377 ->
445fd84e -> 377bbcbb is linear. On disk both files equal HEAD; both were born and last modified at 11:15:45 +0900 (= 02:15:45Z, the END of the
driver run in `authorize_run.log`) and have not been rewritten since.

Byte-exact reproduction (`repro.py`, clone_q at 445fd84e with the authorization commit unreachable): preconditions as the driver checked them --
launch policy, barrier, code-dir shadows, loaded modules: no problems; no worker; lifecycle QUALIFIED; `_authorization_facts(A, stage="authorize")`:
`problems: []`. Building the authorization body BY HAND exactly as `build_authorization` does (from `_authorization_facts`, `fixture: False`,
the committed operator string), `permission_record("GRANT", ...)`, and serialising exactly as `write_record` does, gives objects AND bytes
identical to the committed files (`hand_auth_bytes_equal_committed: true`, `hand_grant_bytes_equal_committed: true`, digest 193b0122...).
`build_authorization(..., fixture=True)` at the same point differs from the committed record only in `fixture` and `sha256`. The two records
are therefore exactly what the frozen mechanism produces at the issue point; nothing was edited by hand.

Independent recomputation from the bytes AT A (git show, my own canonical-JSON digest): contract body 8e86b509..., gate 2d23a8b8... (guard
DENY, bound to 8e86b509), policy a6b33ef3..., statement table b937cace..., runner = sha256(c11r_runs.py at A) = d958a457... (= HEAD = disk =
contract), qualifier 95520529..., launcher 839faeae..., launch-policy canonical digest 773246f3...; qualification at c06ce377 body digest
114713ef... = stored, class PASS, bound to exactly these identities and A. Authorization `configuration` == contract-at-A `configuration`
(depth 5, panels 32, cap_seconds 10800, cap_rss_mb 8192, safety_factor "3/2", rule text verbatim); policy at A chosen {5, 32}, caps and
safety factor identical.

Production verifiers at HEAD, primary checkout (`core_primary.json`) and clone1 (`core_clone1.json`), identical results:
`lifecycle` = AUTHORIZED, problems [], held [authorization, permission, qualification], permission GRANT at HEAD and on disk, execution
permission ALLOW; `verify_authorization(stage="run")` problems []; `validate_permission(GRANT)` []; `protocol_history(A, "run")` problems [],
introducers qualification [c06ce377], authorization [377bbcbb], permission_grant [377bbcbb], runs [], permission_final []; `frozen_state`
clean (44 paths, 4 commits); `verify_qualification` PASS []; `code_dir_shadows` []; `preimport_barrier_problems` []; `verify_loaded_modules` []
(132 modules); `launch_policy_problems` []; `campaign_workers` []; `protocol_artifacts_anywhere` (731 commits): authorization and permission
only in 377bbcbb, no runs, no comparison, protocol directories: only evidence/qualification.

## Required attacks

### 1. A wrong qualification -- PASS
In memory (`inmem.py`, clone1): the committed authorization with `qualification_sha256` = zeros, or = the digest of a different qualification
body, re-sealed -> `verify_authorization(run)` REFUSES ("qualification_sha256 does not match the recomputed value"). On disk (`mutate.sh`,
mclone): the qualification replaced (re-sealed) uncommitted -> lifecycle MALFORMED, refused; committed -> refused ("holds a qualification
artifact other than the current one" for c06ce377/445fd84e/377bbcbb). A qualification bound to another approved commit / contract / gate /
policy -> `verify_qualification` refuses. The committed authorization binds 114713ef..., the accepted qualification (Q-review 445fd84e).

### 2. A second qualification (branch, tag, stash, reflog) -- PASS for this repository; NOTE (b), carried N-3
Real repository (read-only): 741 commits (731 reachable from 117 refs incl. 36 tags, 0 stashes, HEAD and every reflog, plus the 10 unreachable
commits `git fsck --unreachable` reports) -> the qualification path holds exactly ONE blob (cdc65e4c) in 3 commits; its only introducer is
c06ce377 (`protocol_history`); `rev-list --objects --all --reflog` shows no other qualification-like path; none of the 196 unreachable blobs
contains the string `C11R_QUALIFICATION/`. Mechanism (mclone): a different qualification on a sibling branch, in a tag, in a stash or
reflog-only is NOT refused at stage run (`verify_authorization` ACCEPTED in all four) -- `_protocol_elsewhere` does not cover the
qualification (carried Q-review N-3, class (b)). The same qualification re-introduced on HEAD's line -> refused ("introduced by 2 commits").

### 3. A forged qualification PASS -- PASS; NOTE (b), carried N-2
`QUALIFICATION_CLASS: PASS` over a FAIL item -> refused (class != recomputed disposition); class FAIL over all-PASS items -> refused; stale digest
-> refused. As the frozen `QUALIFICATION_PROVES` states, the record is an attestation: a re-sealed record varying provenance.code_closure or an
item's detail is accepted by `verify_qualification` (reproduced) -- carried N-2 (b). For THIS record I recomputed every provenance hash
(14 code-closure files, 9 inputs, producer): equal at A, at HEAD, on disk and in the contract; `chain_root_problems` [], `fixture` false,
`computes_on_open_cells` false, `produces_target_constants` false; the blob is unchanged since c06ce377.

### 4. An altered Q item -- PASS
In memory: Q11 FAIL; Q4 renamed; Q18 dropped; Q19 added; Q1 duplicated; Q4 bound to another qualifier -> each refused by
`qualification_disposition` / `verify_qualification`. Committed in mclone (Q8 FAIL, class left PASS, re-sealed) -> `verify_authorization(run)` refused.

### 5. A wrong approved commit -- PASS
The committed records name ee1a6a8a... (full id), the commit R8 reviewed and the qualification binds. In memory, the authorization re-sealed with
approved_commit = A^, = 5890511b, = c06ce377 -> refused (tree identity / GRANT bound to another approved commit / qualification bound to another
approved commit / "approved commit already holds a qualification").

### 6. A wrong qualification digest -- PASS
See 1: any `qualification_sha256` other than the recomputed body digest of the on-disk, committed, uniquely introduced qualification is refused.

### 7. A wrong contract -- PASS
In memory: `execution_contract_sha256` altered -> refused. mclone: the contract JSON altered and re-sealed -> refused (contract recompute, gate
bound to another contract, tree identity, qualification bound to another contract).

### 8. A wrong gate -- PASS
In memory: `gate_sha256` altered -> refused. mclone: gate guard set to ALLOW (re-sealed) -> refused ("guard is 'ALLOW', not DENY", tree identity,
digest mismatch); any other gate edit -> refused.

### 9. A wrong policy -- PASS
In memory: `policy_sha256` / `statements_sha256` altered -> refused. mclone: every policy edit (see 13-15) -> refused.

### 10. A wrong launcher -- PASS; NOTE (d), carried N-6
mclone: first line `-IS` -> `-I` -> refused (code identity, "does not start with the frozen interpreter line", tree identity); a changed launcher
constant (`ENV_REFUSED_PREFIXES`) -> refused. A committed mode change 100755 -> 100644 with identical bytes -> ACCEPTED (carried N-6, (d)). The
real launcher is 100755 at A, at HEAD and on disk, bytes 839faeae... = contract.

### 11. A wrong qualifier -- PASS
mclone: one byte appended to c11r_qualify.py -> refused (code identity, tree identity). In memory: qualification bound to another qualifier,
provenance producer altered -> refused.

### 12. Changed input/code hashes -- PASS
mclone: c11r_certificate.py changed uncommitted -> refused; committed -> refused (also history purity); c11r_idrift.py edited, committed and
reverted (tree identical again) -> refused by HISTORY PURITY; C11R_COST.json, C11R_VALIDATION.json, the statement table changed -> refused
(artifact identity / declared input changed / tree identity). In memory: `runner_sha256` altered -> refused.

### 13. Changed D5/P32 -- PASS
In memory: depth 6, panels 64, or the rule text with one trailing space -> refused ("configuration does not match"). mclone: policy
chosen depth 6 / panels 64 (re-sealed) -> refused (policy identity, configuration, "the policy's selected configuration is not the contract's").

### 14. A changed cap (10800 s; RSS 8192 MB) -- PASS
In memory: cap_seconds 10801, cap_rss_mb 8193 -> refused. mclone: policy cap_seconds 10801 / cap_rss_mb 16384 -> refused.

### 15. A changed safety factor (3/2) -- PASS
In memory: "4/3" refused; "6/4" (the same value, another spelling) also refused (exact comparison). mclone: policy safety_factor "6/4" ->
refused; `SAFETY_FACTOR = F(2)` in c11r_policy.py -> refused (code identity, "policy: produced by other code").

### 16. A wrong hostname -- PASS
In memory: qualification with another `node` -> refused (not the cost host, not this host). In-process host patch (`c11r_cost.host_identity`
returning another node) against the committed state -> `verify_authorization(run)` REFUSED "qualification: environment is not this host".
Now: `uname -n` = platform.node() = suzhedeMacBook.local = qualification `environment.host.node` = contract `cost_host.node`.

### 17. A hostname changed after qualification -- PASS (failure is safe); NOTE (d), carried N-14
The authorization record binds no host; the qualification does, and every later boundary re-derives it. With the host patched in-process,
`runner_preflight` on an AUTHORIZED synthetic fixture repository reports "qualification: environment is not this host"; `c11r_runs.main`
(source read, not run) returns 2 on any pre-flight problem BEFORE `begin_execution`, so nothing runs and the permission stays the committed
GRANT: the failure is safe. It is not self-healing: `scutil --get HostName` is still "not set" (dynamic name from LocalHostName
"suzhedeMacBook"; a Bonjour conflict could make it "suzhedeMacBook-2.local"). Remedy then: restore the host name (the operator's decision), or the
terminal REVOKED_BEFORE_EXECUTION; never edit a record. Recommendation (d): re-check `uname -n` immediately before Phase 14.

### 18. A campaign __pycache__ -- PASS for the authorization; NOTE (b) for Phase 14
The author found 21 git-ignored caches (ignored by `level4/.gitignore: __pycache__/`) and MOVED them to `q13/removed_pycache/`; all 21 are there,
hashes equal `removed_pycache.sha256`, the three code directories' mtimes are all 11:09:28 +0900 (= 02:09:28Z). My own classification
(`caches.py`: header parse, `marshal.loads`, `compile()` of source text; no campaign import; every committed version enumerated over all 741
commits via cat-file): 12 timestamp caches whose header matches the current source (accepted by the loader) and whose code object EQUALS the
compilation of the current source (c11_certifier, c11_common, c11r_boxdata, c11r_common, c11r_contract, c11r_cost, c11r_equiv, c11r_idrift,
c11r_launch, c11r_procs, c11r_schema, c7_gaussian); 6 stale (header mismatch -> ignored by the loader) equal to a committed earlier version
(c11r_certificate, c11r_compare, c11r_gate, c11r_policy, c11r_qualify, c11r_runs); 3 stale matching no committed version (c11r_chain,
c11r_errata, c11r_firewall; cache file mtimes 22:33:44 / 22:43:14 / 22:56:23 +0900 on 2026-09-23, each the same second as its header's source
mtime). The author's classification is correct. At authorization time no cache existed: the log's PRECHECK (0 at 02:15:42Z) and, decisively,
the driver's own barrier, which refuses ANY non-`c11r_*.py`/`c11_*.py`/`c7_*.py` entry including an empty `__pycache__` (I ran a byte-for-byte
replica of that barrier against mclone: clean -> passes; empty `__pycache__` -> AUTHORIZATION_REFUSED; without -B -> refused; extra env name ->
refused). The frozen barrier/`code_dir_shadows` admit a real `__pycache__` of inventory stems (copied genuine cache and foreign stem: foreign
stem refused by `code_dir_shadows`, inventory stem admitted) -- see 19.

### 19. A forged campaign .pyc -- PASS for the authorization; NOTE (b), carried N-4
In mclone I forged an ACCEPTED timestamp cache of the inventory stem c11r_schema (source + a sentinel write through the builtin `posix` module).
On the SUPPORTED path (`c11r_launch.py qualify`, no argument) the forged code EXECUTED (sentinel created) before any check; the static
verifiers (`verify_authorization`, `code_dir_shadows`) accept the tree; `verify_loaded_modules` detects it only post-load ("cached bytecode that
is not the compilation of its verified source"; sentinel created again). This is Q-review N-4, class (b), and it applies to Phase 14's runner
exactly as to the qualifier. The authorization process was not exposed (driver barrier: no `__pycache__` at all). Recommendation: repeat the
zero-cache precondition immediately before Phase 14.

### 20. A sourceless cache -- PASS
mclone: `code/c11r_schema.pyc` -> `code_dir_shadows` refuses ("not Python source", "carries the import name of contract module", not in inventory);
the runtime barrier refuses any non-`*.py` entry; the driver barrier likewise. `verify_authorization` alone does not look at the directory
(it is `runner_preflight` that adds `code_dir_shadows`) -- consistent with the frozen split of duties.

### 21. An unexpected campaign source -- PASS
mclone: untracked `c11r_extra.py` -> refused (contract `code_directories` differs; not in inventory; untracked); committed -> refused;
`fractions.py` -> refused (also by the barrier's prefix rule); `c11_extra.py` in the C11 code directory -> refused. Primary: the three
directories hold exactly the frozen inventory (`code_dir_shadows` [], contract-at-A `code_directories` equal).

### 22. A direct start instead of the launcher; the Phase 13 shim -- PASS; NOTE (b)/(c), carried N-7; F-3 (d)
Direct starts (clone1, qualifier usage form): without `-I -S` and with hostile PYTHONPATH/user-site `.pth` -> barrier refuses, but
`sitecustomize` and the `.pth` had ALREADY run (sentinels) -- the stated `not_covered`; `--check-hash-based-pycs never`, `-O`, an extra env name
-> refused; a direct start with exactly CHILD_FLAGS and the allowlisted environment passes the barrier (carried N-7: the policy is enforced, not
the launcher's use). The launcher refuses PYTHON* and DYLD_* names.
The shim (`q13/p13_launch.py`, sha256 5bdc6f2e... = log): I started it exactly as documented with a probe driver (`probe_driver.py`, no campaign
import). The child's `orig_argv` is the frozen interpreter with `-I -S -B --check-hash-based-pycs default -X int_max_str_digits=0 <driver> <args>`
and its environment exactly {HOME, LANG, LOGNAME, PATH=/usr/bin:/bin:/usr/sbin:/sbin, TMPDIR, USER} + the platform's `__CF_USER_TEXT_ENCODING`;
extra names (FOO, GIT_DIR) are dropped; flags isolated/no_site/no_user_site/safe_path/dont_write_bytecode, hash mode default, no pycache prefix,
no warnoptions -- identical to `L.child_argv`/`L.child_env`, i.e. to what the launcher execs. The shim refuses a start without `-I -S`, without
`-B`, or with PYTHON* names. Because the shim refuses unless `-I -S` held, a driver that ran proves no PYTHON*/site/user-site code ran in the shim.
The frozen LIFECYCLE names the Phase 13 actor as `build_authorization`, not the launcher (whose PROGRAMS are run|compare|qualify); the launch
policy governs boundary programs. Using a shim that reproduces the launcher's checks and exact exec is therefore not a protocol deviation; it
is stricter than required. WHAT THE RECORD ATTESTS: only recomputable identities (approved commit, issue point, contract, gate, policy,
statements, qualification, runner, configuration, operator text, fixture false). It attests nothing about the host, the interpreter invocation,
the cache state or the process that wrote it; those rest on the commit message and on scratchpad logs (F-4). Since I reproduced both records
byte-exactly from the frozen functions, and the runner re-derives every identity at pre-flight, the content does not depend on how the writing
process was started. F-3 (d): the shim imports `c11r_launch` from the primary BEFORE checking `-B`; a shim mis-started without `-B` writes a
genuine cache into the campaign code directory before refusing (demonstrated, unintentionally, by me -- see the disclosed deviation). The author's
run was unaffected (PRECHECK 0 caches; the driver barrier would have refused any `__pycache__`).

### 23. A hostile Python environment (sentinels; supported vs direct) -- PASS; NOTE (b), stated scope
Supported path: `env -i ... PYTHONPATH=<dir with sitecustomize writing a sentinel>` + user-site `.pth` in HOME -> `c11r_launch.py qualify` REFUSED
("the environment carries ['PYTHONPATH']") and NO sentinel was written (the kernel starts the launcher with `-IS`); `DYLD_FOO` refused. Clean
environment -> usage, exit 2; `qualify --self-test` via the launcher -> ALL_PASS 8/8, wrote nothing (clone1 clean afterwards). Direct start: see
22 (sentinels written before the refusal: the documented `not_covered`, class (b)). The Phase 13 driver's own barrier re-checks flags,
interpreter, env allowlist, host name and the code directories before its first non-builtin import.

### 24. git replace -- PASS
mclone: a bad policy committed on HEAD, then `git replace <bad> <clean-looking commit>`: plain `git show HEAD:...` no longer shows the change,
but the campaign's git (`--no-replace-objects`, `GIT_NO_REPLACE_OBJECTS=1`) sees the real commit -> REFUSED (artifact identity, configuration,
tree identity, history purity). Synthetic: a replace ref hiding a merge's second parent that holds a runs artifact -> plain git does not see
the side commit; the campaign refuses ("holds a runs artifact (a prior execution)", protocol lineage). Primary: no replace refs.

### 25. A graft -- PASS
mclone `.git/info/grafts` -> REFUSED ("a grafts file rewrites commit parentage", ancestry, issue order). Primary: no grafts file.

### 26. A shallow repository -- PASS
`git clone --depth 6` of the branch (A inside the depth) -> REFUSED ("the repository is shallow"). Primary: not shallow.

### 27. A hostile commit graph -- PASS
Synthetic: side commit with a runs artifact merged `-s ours`, side ref deleted, reflogs expired, `commit-graph write`, then the merge's second
parent patched to GRAPH_PARENT_NONE in the CDAT chunk: plain `git rev-list --all --reflog HEAD` no longer lists the side commit; the campaign
(`core.commitGraph=false`) sees it -> REFUSED. Primary: a split commit-graph exists; `rev-list --parents --all --reflog HEAD` with and without it
is byte-identical (731 commits).

### 28. Hostile GIT_* state -- PASS
The evaluating process carried GIT_DIR, GIT_WORK_TREE, GIT_INDEX_FILE, GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES,
GIT_REPLACE_REF_BASE, GIT_NAMESPACE, GIT_CONFIG_GLOBAL (hostile file), GIT_CONFIG_NOSYSTEM, GIT_CONFIG_PARAMETERS (commitGraph true),
GIT_EXEC_PATH, GIT_NO_REPLACE_OBJECTS=0, GIT_GRAFT_FILE, GIT_SHALLOW_FILE pointing at another repository: a repository with a bad committed
policy is still REFUSED and the pristine clone still ACCEPTED -- `git_env()` strips every GIT_* name.

### 29. An fsmonitor or hook -- PASS for this host; NOTE (b), carried N-12/O-1
A `core.fsmonitor` hook in `$HOME/.gitconfig` (HOME is passed through `git_env`) EXECUTED during the campaign's read-only git calls (sentinel
`FSMONITOR_HOOK_RAN`) while the verdict was unchanged -- carried O-1, class (b). The operator's effective configuration (read-only
`git config --show-origin --list`): Xcode system file (init.defaultbranch), `~/.gitconfig` (safe.directory, user.name), repository config
(core basics, remotes, branches, http); no fsmonitor, hooksPath, include/includeIf, alias; no worktree config; `.git/hooks` holds only
`*.sample`. The only hook-running operation in Phase 13 was the author's `git commit`; no active hook existed.

### 30. A second authorization -- PASS
Real repository: exactly one authorization blob (a7abbce9) and one permission blob (47a7a8ea) in 741 commits (all refs, tags, reflogs,
unreachable); none of the 196 unreachable blobs contains `C11R_AUTHORIZATION/` or `C11R_EXECUTION_PERMISSION/`; no other worktree (33 listed)
holds either file; a filesystem search found only the primary's files and old SYNTHETIC fixture leftovers (F-7). Synthetic (`synth.py`): a
second authorization + GRANT on a sibling branch, in a tag only, in a stash only, reflog-only -> each REFUSED at stage run ("protocol
lineage: ... hold a permission/authorization artifact that stage run does not admit"); a second Phase 13 on an AUTHORIZED tree
(`build_authorization(fixture=True)`) -> refused (prior authorization/permission; lifecycle).

### 31. An authorization edit / revert / recreate -- PASS
Synthetic: operator edited, re-sealed, GRANT re-bound, committed -> REFUSED (authorization other than the current one; permission other than
the GRANT); edited on disk only -> MALFORMED, refused; `git revert` of the authorization commit -> state QUALIFIED, stage run refused, and a
re-authorization (stage authorize) refused ("holds an authorization (a prior one)"); identical bytes re-committed after the revert -> refused
("introduced by 2 commits"); permission removed -> MALFORMED; authorization removed with the GRANT kept -> MALFORMED.

### 32. An authorization bound to a moving ref -- PASS for the record; F-1 (d)
The committed `approved_commit` and `issued_at_head` are full 40-hex ids that name themselves. `approved_commit` as a branch name, `HEAD`, an
abbreviation or `<id>~3` -> refused by `approved_commit_problems`. BUT `issued_at_head` is only checked with `cat-file -e <x>^{commit}` and
ancestry: in memory AND committed in a synthetic repository, an authorization whose `issued_at_head` is `trunk`, `HEAD`, `HEAD~1` or a
10-character abbreviation is ACCEPTED (F-1, class (d): the frozen builder always writes `git rev-parse HEAD`, a full id, and the committed
record carries 445fd84e...; not exploitable through the frozen mechanism).

### 33. A target run accidentally started -- PASS
Process table (`ps -axww`, start and end): no c11r_/p13_ process; the only Python processes are unrelated MCP servers and an agent gateway.
evidence/runs: absent on disk in the primary and in every worktree; no runs artifact or `evidence/runs` path in any of the 741 commits; no
`C11R_RUNS/` string in any unreachable blob. Permission record: on disk = HEAD = GRANT (blob 47a7a8ea, sha256 6493d2cc...), born and last
modified at 02:15:45Z and never rewritten -- `begin_execution` (source read) rewrites it to DENY/EXECUTION_STARTED BEFORE any science, and a
restore from git would have changed its mtime/ctime; the branch reflog shows no movement after 377bbcbb. Synthetic: a runs artifact on disk
(MALFORMED), EXECUTION_STARTED on disk (state EXECUTING), a runs artifact on a sibling branch, another file under evidence/runs -> each
refused at stage run. Scope (stated by LIFECYCLE_SCOPE, not claimed): an execution in another clone that left no trace here.

### 34. Target-value contamination -- PASS
Every leaf of both records, by key path: authorization -- `cell` 306 (int, target cell id); `configuration.cap_rss_mb` 8192,
`configuration.cap_seconds` 10800, `configuration.depth` 5, `configuration.panels` 32 (ints, = contract at A); `configuration.safety_factor`
"3/2" and `configuration.rule` (text, = contract at A; only digit "1" in "panels + 1"); `operator` (text; tokens 13, 2026-09-25, 5.5 = Phase
number, date, model version); `schema` "C11R_AUTHORIZATION/5"; `authorizes` "ONE_EXECUTION"; `fixture` false; eight 40/64-hex ids/digests.
Permission -- `cell` 306; `schema`, `transition` GRANT, `execution_permission` ALLOW, two hex ids, `grant_sha256`/`runs_sha256` null, `fixture`
false. Commit message: every numeric token is a count (730, 117, 36, 21, 18, 12, 9, 14, 6, 3, 2, 1, 0), a phase/item number, a date/time, a
fragment of a hex id, a frozen configuration value (306, D5/P32, 10800, 8192, 3/2), or a version (3.14, 5.5); no other decimal. The commit adds
no other file. The author's scratchpad outputs (p13_verify.json, p13_postauth_*.json, caches_classified.json, provenance3.json,
authorize_run.log) contain no float leaf and no long decimal.

### 35. A comparison accidentally created -- PASS
No `evidence/comparison` on disk (primary and all worktrees), in any of the 741 commits, or as `C11R_COMPARISON` in any unreachable blob.
Synthetic: a comparison in a tag -> refused at stage run ("a prior comparison").

### 36. r5 mutation -- PASS
K5_COVERAGE_MAP_R5.json: blob f978eeb6 at A, at HEAD and on disk; the only blob at that path in all 741 commits (82 holders).

### 37. r6 creation -- PASS
No path matching COVERAGE_MAP_R6 in `rev-list --objects --all --reflog HEAD`, in the 10 unreachable commits' trees, or on disk (the only
"R6" paths are the R6 reviews of C2/C11R and an unrelated `test_r6.py`).

### 38. Historical review mutation -- PASS
R1-R8 and REVIEW_C11R_QUALIFICATION.md: each path holds exactly ONE blob across all 741 commits, introduced by its preservation commit (absent in
the parent); the disk bytes equal it (`git hash-object`). Q-review sha256 c81e5fb4..., R8 8322f74b....

### 39. main mutation -- PASS
Local `refs/heads/main` = c123b9bb8f15d17650545b3fce4aca8a6b61093b (last reflog entry 2026-09-03); GitHub (`git -C /Users/suzhe/ReBaseGuard
ls-remote origin refs/heads/main`, read-only) = 1cb453826313c189f0bdafd5b84120c1edb74da9; `refs/remotes/origin/main` = 1cb45382.

### 40. G13/Q11 phase semantics -- PASS; NOTE (c), carried N-1
G13 ("c11r_status reports STATUS_CLASS = CONSISTENT") is a gate predicate frozen at A; the gate was not modified (frozen path, blob = A). It is not
a REQUIRED_PREDICATE (the contract binds evaluators for G2, G8, G10, G18-G21 only) and nothing on the Phase 13 path (`build_authorization`,
`_authorization_facts`, `lifecycle`, `protocol_history`) nor the runner's pre-flight (source read) evaluates it. The status verifier's
PRE-RESULT conditions require no qualification, no authorization, no permission and no protocol directory in any commit, so after Phase 12 it
refuses by construction; the accepted qualification's Q11 ran it immediately before the qualification was written (exit 0, CONSISTENT; the
Q-review reproduced it). I ran `c11r_status.py --verify-only` in clone1 at 377bbcbb: exit 1, `STATUS_CLASS = REFUSE`, with `not fresh []`, `class
failures {}`, `committed status report FRESH`, and as the ONLY contradiction the inventory entries C11R_AUTHORIZATION.json,
C11R_EXECUTION_PERMISSION.json and C11R_QUALIFICATION.json. So the substance of G13 (freshness and cross-artifact consistency) still holds at
377bbcbb; only the pre-result-state clause fails, as designed. Treating G13 as discharged by Q11 is correct; the Q-review asked for exactly this
statement in the Phase 13 record, and the author put it in the commit message. The wording defect (G13's prose carries no phase scope) is
carried N-1, class (c).

## The "authorization + GRANT in one commit" interpretation -- CORRECT under the frozen protocol

The frozen LIFECYCLE (bound in the contract at A) defines QUALIFIED -> AUTHORIZED as "the authorization AND the execution permission GRANT are
committed in ONE commit", writes [AUTH_REL, PERMISSION_REL], execution permission after ALLOW; `c11r_chain.Chain.authorize` (the fixture
rehearsal) does exactly that. I tested the alternatives in synthetic fixture repositories:
- authorization committed ALONE -> state MALFORMED ("no state of the frozen transition table"), refused;
- then the GRANT in a LATER commit -> the state computes as AUTHORIZED, but `protocol_history(run)` refuses for ever ("no execution permission
  GRANT was committed together with the authorization"; the GRANT must be introduced in the authorization's introducing commit);
- authorization committed, removed, then authorization + GRANT together -> refused ("introduced by 2 commits"), and a fresh Phase 13 is refused
  ("holds an authorization (a prior one)");
- GRANT alone -> MALFORMED.
So committing the authorization alone would have left the campaign MALFORMED with no valid continuation under A. The only frozen form of
Phase 13 is both records in one commit, and that is what 377bbcbb is. Committing the GRANT does not execute anything and does not consume it;
the step that consumes it (`begin_execution`) belongs to Phase 14. The consequence -- execution permission ALLOW at HEAD, so any start of
`c11r_runs.py` is a Phase 14 execution attempt (the runner parses no arguments: even `--help` runs `main()`; F-6) -- is inherent to the
frozen AUTHORIZED state, not a defect of this authorization.

## The authorization commit message, claim by claim

1. "Phase 13 only. Nothing was executed: no run, no comparison, no target value." -- VERIFIED (33, 34, 35).
2. Holds exactly C11R_AUTHORIZATION/5 (body 193b0122...) and the GRANT (ALLOW, body ad95eef7..., bound to the authorization) -- VERIFIED (diff-tree,
   digests, `validate_permission` []).
3. "Both were built by the frozen build_authorization (fixture=False) and written by write_record, as Chain.authorize does ...; nothing was
   edited by hand." -- VERIFIED to the extent bytes allow: both files are byte-identical to the frozen builder's output at the issue point; the
   driver source (sha256 16fe35c9... = log) calls exactly those functions once; `fixture` false.
4. "The GRANT is not consumed." -- VERIFIED (on disk = HEAD = GRANT; file never rewritten).
5. BINDINGS (A; issued at 445fd84e; qualification 114713ef... introduced once by c06ce377; contract 8e86b509; gate 2d23a8b8; policy a6b33ef3;
   statement table b937cace; runner d958a457; D5/P32, 10800 s, 8192 MB, 3/2; cell 306; one execution) -- VERIFIED from bytes at A.
6. G13/Q11 paragraph -- VERIFIED and judged correct (40).
7. N-14 host (`uname -n` = suzhedeMacBook.local = the qualification's host; checked 02:15:42Z and inside the driver) -- VERIFIED for the values and
   the driver's check (replica); the timestamp is from the log.
8. N-4 caches (21: c11r 18, c11 2, c7 1; 12/6/3 classification; no campaign code executed to classify; moved and preserved with sha256 at
   02:09:28Z; 0 before authorization; the driver refused any cache) -- VERIFIED (18). Wording: "written 2026-09-23 22:33-22:56" is local time
   (+0900) while every other time in the message is UTC (F-5, (c)).
9. N-2 hashes (14 code, 9 inputs, producer, contract, gate, policy, statements, qualifier, launcher, launch policy 773246f3; equal now, at A,
   to the root of trust) -- VERIFIED (independent recomputation from git objects; root-of-trust values as cited by the Q-review).
10. N-3 (one qualification lineage in 730 commits, 117 refs, 36 tags, 0 stashes, every reflog; one blob, one introducer; the schema string
    elsewhere only in c11r_qualify.py source) -- VERIFIED (now 731 + 10 unreachable; the pickaxe hits are two HISTORICAL versions of
    c11r_qualify.py, 38f59993 and bd00c1f6 -- accurate, if terse).
11. Git/runtime integrity (no replace refs, grafts, shallow, fsmonitor, hooksPath, includes, active hooks; commit-graph ignored 730 = 730;
    inventory, launch policy, barrier, module identity clean) -- VERIFIED (24-29, 21; parent lists with/without the graph identical).
12. Launcher paragraph (no Phase 13 program; driver started with the launcher's checks and exact child invocation; `_authorization_facts
    (stage="authorize")` no problems) -- VERIFIED (22 probe; `repro.py` at the issue point: `facts_problems: []`).

## BLOCKERS

none.

## Non-blocking observations

New in this review:
- **F-1 (d).** `_issue_order` accepts an `issued_at_head` that is a moving ref (branch name, `HEAD`, `HEAD~1`, an abbreviation), in memory and
  committed (synthetic `S32_*` ACCEPTED). `approved_commit` is protected by `approved_commit_problems`; `issued_at_head` is not. The frozen
  builder writes a full id and the committed record carries one, so nothing is open for this record.
- **F-2 (d).** `verify_authorization` has no closed key set and does not bind `operator`: an extra field or another operator text, re-sealed,
  passes in memory. Committed, any such change is refused by `protocol_history` (the authorization is immutable once introduced). The committed
  record has exactly the builder's 15 keys.
- **F-3 (d).** The Phase 13 shim (not frozen code) imports `c11r_launch` from the primary before it checks `-B`; mis-started without `-B` it
  plants a (genuine) cache in the campaign code directory before refusing. No effect on the authorization (see 22 and the disclosed deviation).
- **F-4 (b)/(c).** The Phase 13 process evidence (host check, cache classification and move, shim, drivers, logs, the 21 moved caches) exists
  only in the commit message and in the session scratchpad `q13/` outside the repository; the frozen authorization schema carries none of it.
  The records themselves do not depend on it (byte-exact reproduction), but the evidence is not durable: preserve `q13/` (with hashes) before the
  session scratchpad is cleaned.
- **F-5 (c).** Commit message mixes an unlabeled local time ("22:33-22:56", +0900) with UTC "Z" times.
- **F-6 (d), pre-existing frozen code.** `c11r_runs.py` has no argument handling (`if __name__ == "__main__": raise SystemExit(main())`): any
  start, `--help` included, is a Phase 14 execution attempt now that the GRANT is at HEAD. Until Phase 14 is instructed, no one should start it
  in any clone or worktree (a clone carries the same valid GRANT).
- **F-7 (d).** Old SYNTHETIC chain-control repositories with fixture authorization/permission/runs files remain in
  `scratchpad/r7/review_work/tmp/c11r_chain_*` and `$TMPDIR/c11r_chain_*` (fixture true, synthetic approved commits); harmless, but they
  match a filesystem search for protocol files.
Carried from the qualification review, re-measured here:
- **N-1 (c).** G13's prose carries no phase scope (40).
- **N-2 (b).** `verify_qualification` checks an attestation, not the provenance/detail (3).
- **N-3 (b).** Qualification uniqueness outside HEAD's history is not enforced at stage run (2); this repository holds exactly one.
- **N-4 (b).** A forged ACCEPTED cache of an inventory stem executes on the supported path before detection (19); repeat the zero-cache
  precondition before Phase 14.
- **N-6 (d).** Launcher file mode not bound (10).
- **N-7 (b)/(c).** A policy-compliant direct start passes the barrier (22).
- **N-12 / O-1 (b).** `core.fsmonitor` from `$HOME/.gitconfig` runs inside campaign git calls (29); the operator's configuration has none.
- **N-14 (d).** Dynamic host name; the failure is safe (17); re-check `uname -n` before Phase 14.

## Final state of the primary checkout after this review

HEAD 377bbcbb8359a8265e37663bdda6956a357b03c3; `git status --porcelain --ignored --untracked-files=all` empty; 0 `__pycache__`/`.pyc`/`.pyo` in
the three campaign code directories (after correcting my own 12-second cache, disclosed above); the permission on disk is still the committed
GRANT (sha256 6493d2cc..., mtime 11:15:45 +0900); nothing committed, pushed or fetched; main c123b9bb (local) / 1cb45382 (GitHub); no git
config, hook, host name or system setting changed; no background process left running; no campaign process in the process table.

VERDICT: AUTHORIZATION_ACCEPTED
