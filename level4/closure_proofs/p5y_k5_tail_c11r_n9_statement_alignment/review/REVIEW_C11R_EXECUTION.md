# C11R Phase 14 -- independent EXECUTION review

| item | value |
|---|---|
| subject | the sealed Phase 14 execution of cell 306 |
| seal commit (reviewed) | 5ff4cc5b310b31bc7b61213598aade9a5188964e |
| Phase 14 entry HEAD / authorization review | 9bd17be5408a8676bba6ff94e00e3d32110ebffc (AUTHORIZATION_ACCEPTED) |
| authorization + GRANT commit | 377bbcbb8359a8265e37663bdda6956a357b03c3 |
| qualification commit | c06ce3774d3cc100fd16dfbd2d1c49c29e7d1021 (review 445fd84e, QUALIFICATION_ACCEPTED) |
| approved commit (R8-reviewed) | ee1a6a8aab8ff57360249bc813a44b3c724200aa (R8 review 5890511b, READY_TO_QUALIFY) |
| primary checkout | /Users/suzhe/ReBaseGuard-k5c11r (branch p5y-k5-tail-c11r-n9-statement-alignment, common git dir /Users/suzhe/ReBaseGuard/.git) |
| brief | BRIEF_EXECUTION_REVIEW.md, sha256 7acfc6496a4e5fcdf9f5d8c4b309a339d6fcdab85462e0c55df86075f78c255c (verified before starting) |
| review date | 2026-09-25 (all times below UTC unless marked +0900) |
| reviewer | new, independent execution reviewer (no prior involvement in C11R) |

## 0. Scope, method and what this reviewer did NOT do

- The runner was NOT started in any form, anywhere (`c11r_runs.py`, `c11r_launch.py run`); `c11r_runs`
  was never imported. The comparator was never run or imported (`c11r_compare`, `c11r_launch.py
  compare`, phase15). No checkout of 377bbcbb or 9bd17be5 was made anywhere; their trees were read
  with `git ls-tree` / `git cat-file` / `git show` only.
- The quarantine and the C2 registry were never content-read by this reviewer's processes. Their
  identities were obtained only as git object ids (`git ls-tree`, and the frozen
  `c11r_common.content_free_id`, i.e. `git hash-object --no-filters` in a git subprocess, which the
  frozen `verify_contract` / `frozen_state` call). Disclosure: that frozen call updated the access
  time of `REGISTRY_C2.json` (05:39:08Z); no byte of it entered the reviewer's process. Review prose
  (`REVIEW_*`, `ADJUDICATION_*`) was hashed and only its `VERDICT` / disposition token extracted.
- The runs artifact was parsed programmatically; only structure, digests, bindings, field presence,
  counts, resource totals, protocol states and booleans were emitted. No target value, selection,
  certificate result, margin, per-target status/outcome, screen classification or per-certificate
  timing appears in this file or in any file written by this reviewer.
- Everything written: `review_work/h_exec.py` (sha256 5302c2dacf73d6dc328bc9e9dc7d877c4fd793897b3b034676c7b449501ecb4b),
  its output `review_work/h_exec_out.json`, `review_work/all_commits.txt`, and this file. Nothing in
  /Users/suzhe/ReBaseGuard-k5c11r or /Users/suzhe/ReBaseGuard-forensics was modified; no git
  config, hook, ref or remote was touched; the only network access was the brief-mandated
  `git -C /Users/suzhe/ReBaseGuard ls-remote origin refs/heads/main`.
- Harness invocation (launch-policy form): `env -i HOME LANG LOGNAME USER TMPDIR
  PATH=/usr/bin:/bin:/usr/sbin:/sbin /Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14
  -I -S -B --check-hash-based-pycs default -X int_max_str_digits=0 h_exec.py out.json`. It imports
  c11r_common, c11r_contract, c11r_schema, c11r_procs and (for the pure production guards)
  c11r_certificate; it asserts `c11r_runs`/`c11r_compare` are not in `sys.modules`; it refuses to
  start if any campaign `__pycache__` exists and records that none exists afterwards. It calls only
  read-only contract/schema/guard functions (no `main()`, no certifier, no writer).
- Start and end state: HEAD = 5ff4cc5b310b31bc7b61213598aade9a5188964e;
  `git status --porcelain --untracked-files=all --ignored` empty; 0 `__pycache__`/`.pyc`/`.pyo` in
  the three campaign namespaces; no campaign, runner, comparator or caffeinate process
  (`ps -axo` listing; PID 12156 absent). No runner or comparator process was ever seen starting.

Independent evidence sources used: git object store (loose-object creation times, all refs, all
reflogs incl. worktree reflogs, `fsck --unreachable`), filesystem metadata (birth/modify times of
protocol files and code directories), the frozen contract functions re-run from bytes, the
forensic directory (both MANIFESTs re-verified: top MANIFEST.sha256 = 1f3525fd6857bf3b02ae1a943395576bb99399d85dc87ca3ad898f74aefcef7f,
all 101 entries OK; phase14_execution/MANIFEST.sha256 all 9 entries OK; phase13 removed_pycache
manifest 21/21 OK), the orchestrating session's tool-call transcript (commands and their recorded
results only), the Codex log database (read-only query), a Spotlight/`find` search of the host for
copies of protocol files, and every git worktree and scratch clone on the host.

## 1-40. Required verifications

### 1. Entry lifecycle was AUTHORIZED -- PASS
At 9bd17be5 the committed protocol set is exactly {qualification (blob cdc65e4c), authorization
(a7abbce9), permission = GRANT (47a7a8ea)}; no runs, no comparison (repository-wide scan below).
The author's pre-flight record (p14_preflight.json, 03:42:00Z, manifest-verified) shows
`lifecycle(A)` = AUTHORIZED with no problems and disk = HEAD for all three records. Independently
and load-bearing: `c11r_runs.main()` returns 2 before `begin_execution` whenever
`runner_preflight` reports anything, and that pre-flight includes
`lifecycle_problems(stage="run")` (requires AUTHORIZED). The permission record reached
EXECUTION_STARTED (see 25), which the frozen code writes only after that pre-flight passed.

### 2. Accepted qualification -- PASS
Qualification body digest 114713efdc00900c4d2f352bccf512e412b8362096fa8c655649de12f83de0e5 (stored =
recomputed), schema C11R_QUALIFICATION/5, fixture false, class PASS; `verify_qualification(A)` now:
no problems, recomputed disposition PASS (host binding included). Blob cdc65e4c identical at
c06ce377, HEAD and on disk; introduced once (c06ce377). Review 445fd84e (REVIEW_C11R_QUALIFICATION.md,
blob 8bdccda1, sha256 c81e5fb4... equal to the forensic copy) ends `VERDICT: QUALIFICATION_ACCEPTED`.

### 3. Accepted authorization -- PASS
Authorization body 193b012227bcfd4970dea5c58ea902f71f102656cb5c8cff300a3531714bd088 (stored =
recomputed), schema C11R_AUTHORIZATION/5, `authorizes` ONE_EXECUTION, cell 306, fixture false, no
`guard` key. `verify_authorization(stage="compare")`: no problems (all seven bindings recompute:
contract, gate, policy, statements, qualification, runner, configuration; issue order: issued at
445fd84e, descends from A and from the qualification introducer, precedes its own introducer).
Review 9bd17be5 (REVIEW_C11R_AUTHORIZATION.md, blob cb1aa581, sha256 5957de10... equal to the
forensic copy) ends `VERDICT: AUTHORIZATION_ACCEPTED`.

### 4. Correct authorization commit -- PASS
Across all 733 commits reachable from any ref, HEAD or reflog, the authorization path is held only
by 377bbcbb, 9bd17be5, 5ff4cc5b, always blob a7abbce9; its single introducer is 377bbcbb (parent
445fd84e), which adds exactly the authorization and the permission GRANT and nothing else.

### 5. Correct GRANT -- PASS
Permission at 377bbcbb (= at 9bd17be5): transition GRANT, execution_permission ALLOW, cell 306,
approved_commit A, fixture false, body ad95eef75cc77b93f722007751bed9947cde6c638d88634fbb96618f1abdc2bc
(stored = recomputed); `validate_permission(GRANT, authorization 193b0122)`: no problems. GRANT
introducer = authorization introducer = 377bbcbb (protocol_history).

### 6. GRANT unconsumed before the run -- PASS
Before the seal, no commit anywhere in the repository holds a permission other than the GRANT blob
47a7a8ea (only 377bbcbb, 9bd17be5); no runs artifact anywhere before 5ff4cc5b. Loose-object store:
the only objects created after the 9bd17be5 commit (03:16:46Z) are the ten objects of the seal
commit (05:14:40Z) -- no staged or dangling permission/runs blob. On disk at start: the frozen
`begin_execution` refuses unless the on-disk transition is GRANT, and the final record's
`grant_sha256` (ad95eef7...) is the body digest `begin_execution` took from that on-disk GRANT.

### 7. Hostname precondition -- PASS
run.log (manifest-verified): `uname -n : suzhedeMacBook.local at 2026-09-25T03:44:14Z`; the
wrapper (run_phase14_once.sh, sha256 cb07aa80...) refuses and starts nothing when `uname -n` differs.
Independently, the runner's pre-flight ran `verify_qualification`, which requires the current host
(node included) to equal the contract's `cost_host` (node suzhedeMacBook.local); the run proceeded.
Host now: suzhedeMacBook.local.

### 8. Zero-cache precondition -- PASS (see note N2)
run.log: `caches : 0 in the three campaign namespaces` (wrapper counts `__pycache__`, `*.pyc`,
`*.pyo` over the whole NS, C11 and C7 namespaces and refuses on non-zero). Independent post-hoc
proof: the directory mtimes of the three code directories are 02:52:26Z (NS/code) and 02:09:28Z
(C11/code, C7/code) -- all before START 03:44:15Z -- and they hold 0 caches now; a cache present at
START would still be present or its removal would have moved the directory mtime. (02:52:26Z is the
Phase 13 reviewer moving out an accidental `c11r_launch` cache, preserved at
q13/review_work/my_accidental_cache; the 21 caches of Phase 13 are preserved, manifest 21/21 OK.)

### 9. Frozen code inventory -- PASS
`frozen_state(A)`: ancestry, tree identity and history purity all empty over 44 frozen paths and
all 6 commits after A; `code_identity` equals the contract for all 19 bound files; `frozen_code`
no mismatch; `code_directories` on disk equals the contract's inventory; `code_dir_shadows` and
`preimport_barrier_problems` empty; contract on disk equals contract at A. `git diff A HEAD`
touches only the seven protocol/review files (no code).

### 10. Launcher identity -- PASS
c11r_launch.py sha256 839faeae408d60f2acc95364988974d9a05eb25254284c32f56642924ff09806 at A, in the
contract and on disk, and recorded in run.log at start; mode 100755 at A and HEAD; first line
`#!/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -IS`; `LAUNCH_POLICY` bound in
the contract equals the code's. Process evidence (transcript snapshot 03:44:22Z): PID 12156 (parent
12056 = the wrapper) running the frozen framework interpreter with `-I -S -B
--check-hash-based-pycs default -X int_max_str_digits=0`, i.e. the launcher's CHILD_FLAGS after
execve.

### 11. Runner identity -- PASS
c11r_runs.py sha256 d958a45793506613e7749953530eafb1f728a61e828b741f262f90ee41041f7c at A, at the
seal, on disk, in the contract, in `authorization.runner_sha256`, in
`execution_identity.runner_sha256`, and as the runs artifact's `provenance.producer_sha256`.
Source read in full: pre-import barrier first; `preflight` -> `load_verified_inputs` ->
`begin_execution` precede any computation; one pass; `finish_execution` writes runs + EXECUTION_COMPLETED.

### 12. Exact target cell 306 -- PASS
Contract scope cell 306; authorization cell 306; GRANT and final permission cell 306; the runs
drift block equals the contract scope's drift block (the statement table's cell-306 block), in the
top level and in each certificate's inputs. (The runs artifact itself carries no `cell` field: see N6.)

### 13. Only one execution -- PASS
- Once-marker: STARTED.once = `2026-09-25T03:44:14Z` (created with noclobber; a second wrapper start
  exits 9). runner.pid holds exactly one line (`RUNNER_PID 12156`).
- run.log: exactly one START (03:44:15Z), one EXIT 0, one END (05:06:33Z), one
  EXECUTION_STARTED line, one pair of `wrote` lines.
- Session transcript of the orchestrating session and all its sub-agents since 03:00Z: exactly one
  command invoking the wrapper (03:43:42Z, backgrounded); no other invocation of `c11r_launch.py
  run` or `c11r_runs.py`. The only other Claude session active today mentions none of them; the
  Codex log DB has 487 entries between 03:03Z and 05:39Z, none mentioning c11r/k5c11r/run_phase14.
- Permission transitions: GRANT (committed 377bbcbb) -> EXECUTION_STARTED (on disk only, as the
  lifecycle prescribes; seen by transcript snapshots at 03:44:22Z and 03:46:40Z with no runs
  directory) -> EXECUTION_COMPLETED (on disk 05:06:33Z, committed in the seal).
- Git: one runs blob (a5351603) in one commit anywhere; linear reflogs (branch and worktree HEAD)
  with no reset/checkout since 440bcd91; no stash; no other ref contains any C11R commit;
  `fsck --unreachable`: 10 unreachable commits, all from 2026-09-13/16, none holding a protocol
  artifact; no unreachable blob of runs/permission size.
- Other worktrees: of 34 worktrees only the primary descends from A or holds the C11R namespace.
- Host search: the only non-fixture runs artifact / EXECUTION_COMPLETED record on the host is the
  primary's. See N1 for three scratch clones that carry a live GRANT (never used: clean, no runs
  directory, no file newer than 03:30Z).

### 14. No earlier run -- PASS
No runs artifact, runs directory, non-GRANT permission or comparison in any commit before the seal
(repository-wide, `rev-list --all --reflog HEAD`, 733 commits); p14_preflight at 03:42Z:
`evidence/runs` absent; the runner's own pre-flight (which refuses on an existing runs path or any
committed run anywhere) passed. Earlier synthetic artifacts on the host are fixtures of review
controls (q13 syn_33a: a 46-byte planted file; r7 chain temp: `fixture: true`, approved commits
6c18f926/5a8c118c, dated 2026-09-24) -- not executions under this GRANT.

### 15. No concurrent campaign worker -- PASS (see N3)
The runner's pre-flight includes `c11r_procs.campaign_workers()` and refuses on any worker; it
passed. Author pre-flight 03:42Z: []. Transcript snapshots during the run show only 12156 and its
caffeinate. Now: `campaign_workers()` = []. No other agent session touched the campaign.

### 16. Exact approved commit -- PASS
ee1a6a8aab8ff57360249bc813a44b3c724200aa is a full self-naming commit id (`approved_commit_problems`
empty), HEAD descends from it, and it is the approved commit in the authorization, the GRANT, the
final permission record and `execution_identity.approved_commit`. R8 review (5890511b, child of A)
disposition READY_TO_QUALIFY.

### 17. Qualification binding -- PASS
`execution_identity.qualification_sha256` = authorization `qualification_sha256` = recomputed
qualification body digest 114713ef...; `verify_run_identity` empty.

### 18. Authorization binding -- PASS
`execution_identity.authorization_sha256` = final permission `authorization_sha256` = GRANT
`authorization_sha256` = recomputed body digest 193b0122...

### 19. Contract binding -- PASS
Recomputed contract digest 8e86b50925c709f053a0be5b0c7be44ce1e7f3dcf3da2c9b453beb3ca3108cd8 =
`execution_identity.execution_contract_sha256` = authorization; `chain_roots` / `verify_contract`
empty; `execution_identity.code_sha256` equals the contract's 19 code hashes.

### 20. Gate binding -- PASS
Gate digest 2d23a8b8005dc48312c9088311bc28dcabfd5a3c128e83e48baca1a557e5e453 recomputed, bound to
the contract, guard DENY, predicates bound to their evaluators (`verify_gate` empty); equals
`execution_identity.gate_sha256` and the authorization.

### 21. Policy binding -- PASS
Policy body a6b33ef384376a485d781aa6f6a4f8cca554909f44bdabc33c39623ab2f85e9f and statement table
b937cace6ae29701b8271a8d659d8817b017cde7094231b1339e4cd3e22a2ca1 equal the contract, the
authorization, `execution_identity` and the runs top-level digests. `provenance.inputs` lists
exactly these two files (no protected path), each at its file sha256 at A (the bytes
`load_verified_inputs` read once and used).

### 22. D5/P32 binding -- PASS
Contract, authorization and `execution_identity` configuration: depth 5, panels 32; policy chosen
D5/P32; each of the three certificates records inputs depth 5 / panels 32 and cover
`c11_certifier.cover` at depth 5; runs `configuration` = depth 5, panels 32, boxes 363 = policy
`boxes_at_depth["5"]`; G19 (configuration adherence) passes on re-evaluation.

### 23. Cap -- PASS
`total_seconds` 4938.1 <= 10800; `peak_rss_mb` 48.5 <= 8192; `stop_reason` null. Wall clock
START->END = 4938 s (second resolution), consistent with `total_seconds`.

### 24. Safety factor 3/2 -- PASS
`safety_factor` "3/2" in the contract, authorization and `execution_identity` configuration. Policy
(pre-result): chosen D5/P32 estimate 5338.3 s x 3/2 = 8007.4 s <= 10800 (recorded cap fraction
0.7414); the realised 4938.1 s is below the unscaled estimate.

### 25. Run ordering -- PASS
Code order: `begin_execution` (line 304) precedes the first computation (line 325).
Evidence order: entry commit 9bd17be5 03:16:46Z < author pre-flight 03:42:00Z < once-marker
03:44:14Z < START 03:44:15Z < EXECUTION_STARTED on disk with no runs directory (snapshot 03:44:22Z,
runner age 9 s; again 03:46:40Z) < runs file birth = mtime = permission mtime = END 05:06:33Z
(runs directory birth 05:06:33Z) < unsealed check 05:14:09Z (status: exactly ` M permission`,
`?? runs`; lifecycle EXECUTED_UNSEALED) < seal commit 05:14:40Z. The EXECUTION_COMPLETED record
binds runs body 1e0d82ac5cbe6fce07e667d8995bc1ecdf8c766295e07a281bff17c668de7e9d, which equals the
recomputed body digest of the committed runs artifact.

### 26. GRANT consumption -- PASS
Final record: transition EXECUTION_COMPLETED, DENY, `grant_sha256` = ad95eef7..., `runs_sha256` =
1e0d82ac..., fixture false, stored sha256 585228317e987fc8491e37e75873d5b6ea5f9f05efc86c47219dc25902f5ed82
= recomputed; it is byte-for-byte what `permission_record(...)` + `write_record` produce
(deterministic rebuild equal; file bytes in the write format). `validate_permission` empty;
`lifecycle(A, runs_sha256)` = SEALED, runs binding checked, no problems. The intermediate
EXECUTION_STARTED record is deterministic (rebuilt sha256 40426d02356b13ed2533f73fff8fdf3557534ba05c6269dccf145e9ae038b18e, validates).

### 27. No reusable GRANT -- PASS (see N1)
At HEAD and on disk: EXECUTION_COMPLETED. The GRANT blob survives only inside 377bbcbb and 9bd17be5,
and no ref, stash or reflog points to a commit that holds it without the seal being reachable too.
What a runner pre-flight would say NOW (frozen `runner_preflight(repo)` called read-only, runner not
started): 8 problems, including `lifecycle: the state is SEALED; stage run requires AUTHORIZED`,
`protocol history: commit 5ff4cc5b310b holds a runs artifact (a prior execution)`, two
repository-wide `protocol lineage` refusals and `a runs artifact already exists` (the eighth,
"c11r_runs.py ... not loaded", is an artefact of calling it from a non-runner process). A worktree
of THIS repository checked out at 377bbcbb/9bd17be5 would still be refused, because
`_protocol_elsewhere` scans every ref/reflog and the seal is reachable from the branch ref. Outside
the repository (LIFECYCLE_SCOPE): see N1.

### 28. Exactly one run -- PASS
One runs artifact (one blob, one introducer 5ff4cc5b, `evidence/runs` holds only C11R_RUNS.json),
one START/END, one runner PID, one EXECUTION_COMPLETED record bound to its digest.

### 29. Seal validity -- PASS
5ff4cc5b: single parent 9bd17be5; changes exactly `A evidence/runs/C11R_RUNS.json` and
`M config/C11R_EXECUTION_PERMISSION.json` (GRANT -> EXECUTION_COMPLETED); authorization untouched.
`protocol_history(stage="compare")`: no problems, no foreign artifacts; introducers qualification
c06ce377 <= authorization 377bbcbb (= GRANT) < seal 5ff4cc5b (= runs = final permission); no commit
restores the GRANT after the seal. `_authorization_facts(stage="compare")`,
`lifecycle_problems(stage="compare")`, `verify_run_identity`: all empty. Committed blobs equal the
on-disk files; runs file bytes are exactly the runner's write format; stored sha256 = body digest.

### 30. Required certificates -- PASS
`certificates` has exactly {F_D, F_H, F_K} (= `REQUIRED_CERTIFICATES`). Each carries all 13
`CERT_FIELDS` and no extra field; every `inputs`, `certifier` and `certifier_result` sub-field
required by the schema is present; certifier modules c11r_boxdata.py (F_D) / c11r_idrift.py (F_H,
F_K) with `module_sha256` equal to the contract; each `input_digest` recomputes; premises empty;
aggregation single_certificate_whole_block. (Presence only; no content reported.)
`validate_runs`: no problems; `forbidden_payload`: none; seal record {sealed_before_comparison:
true, contains_original_magnitudes: false}; targets: exactly the six constants, all fields present,
each citing its frozen certificate id (none for D1/D2), no declared statement.

### 31. Target evidence provenance -- PASS
Producer `.../code/c11r_runs.py` at the runner hash; recorded `code_closure` (13 modules:
c11_certifier, c11_common, c11r_boxdata, c11r_certificate, c11r_common, c11r_contract, c11r_cost,
c11r_idrift, c11r_launch, c11r_procs, c11r_runs, c11r_schema, c7_gaussian) equals
`runner_closure(contract)` with every hash equal to the contract; inputs = policy + statement table
at A; `execution_identity` equals the recomputed chain in all ten fields. The production guards,
re-evaluated independently from the sealed bytes with the contract's certifier hashes
(`c11r_certificate.evaluate_run`, pure: no certifier executed): ALL_GUARDS_PASS true, 0 violations
in G8, G10, G19 and value tracing, no independence violation, and the sealed `self_check` block is
identical to the re-evaluation.

### 32. No run mutation after the seal -- PASS
HEAD = seal; runs blob a5351603 and permission blob af332d25 identical at the seal, at HEAD and on
disk; runs file sha256 1552dfa99d2250da2bc7e6269957168f89f08e4d60e32eaca2387c6800438f59, 16400
bytes, birth = mtime = 05:06:33Z; no commit, stash or object after the seal; status clean.

### 33. No second target execution -- PASS (see N1, N3)
Items 13, 14, 28; no other copy of a non-fixture runs artifact or EXECUTION_COMPLETED/STARTED
record on the host; the scratch clones carrying a GRANT show no activity after 03:30Z.

### 34. No comparison -- PASS (see N4)
No `evidence/comparison` path in any commit of the repository or on disk; `lifecycle` state SEALED
(not COMPARED); quarantine tree a42969e3 / blob 219e0122 identical at A and HEAD; no comparator
invocation in any agent log since 03:00Z.

### 35. No adoption -- PASS
No change outside the C11R namespace since 440bcd91 (C11 head); no coverage map written; no r6
(item 37); no adjudication artifact added.

### 36. r5 unchanged -- PASS
K5_COVERAGE_MAP_R5.json blob f978eeb6 at A, at 440bcd91, at HEAD and on disk; introduced once
(ae4cbc2c, 2026-09-21), never touched since in any ref or reflog.

### 37. No r6 -- PASS
No path matching COVERAGE_MAP_R6 / `_R6.json` in any commit of any ref or reflog (`git log --all
--reflog -m --name-only`); none on disk in the checkout (the only *R6* file is the historical
REVIEW_C2_PREFREEZE_R6.md).

### 38. Reviews unchanged -- PASS
Each of R1-R8, the qualification review and the authorization review is touched by exactly one
commit (its preserving commit: 6d7cd546, 6ae05833, f6c737c3, 5c5203c1, ebf08c0f, 63402106,
ac75c198, 5890511b, 445fd84e, 9bd17be5), and its blob at HEAD and on disk equals that commit's.
Dispositions: R1-R6 NOT_READY, R7 READY_TO_FREEZE, R8 READY_TO_QUALIFY, QUALIFICATION_ACCEPTED,
AUTHORIZATION_ACCEPTED.

### 39. Historical verdicts unchanged -- PASS
The trees of the C2, C3, C4, C5, C6, C7, C8, C9, C10 and C11 namespaces are identical at 440bcd91
and at HEAD and clean on disk; their branch refs last moved 2026-09-20..23. C11:
`C11_N9_RESULT.json` carries `"N9_VERDICT": "EXECUTION_INVALID"` (unchanged since 440bcd91).

### 40. main untouched -- PASS
Local refs/heads/main = c123b9bb8f15d17650545b3fce4aca8a6b61093b (last reflog entry 2026-09-03);
GitHub (`git -C /Users/suzhe/ReBaseGuard ls-remote origin refs/heads/main`) =
1cb453826313c189f0bdafd5b84120c1edb74da9. Merge-base of the campaign branch with main = main.

## Claims of the seal commit message, checked

| claim | finding |
|---|---|
| seal = runs artifact + DENY/EXECUTION_COMPLETED committed together in ONE commit | TRUE (29) |
| the authorization is not touched | TRUE (blob a7abbce9 unchanged since 377bbcbb) |
| both files committed exactly as the runner wrote them; nothing edited | TRUE: mtimes = END and < seal; runs bytes in exact write format, body digest = the digest bound in the permission; the permission is the deterministic `permission_record` output |
| started ONCE through the frozen launcher `.../c11r_launch.py run` | TRUE (13; process snapshot shows the launcher's child flags) |
| at 03:44:15Z, host suzhedeMacBook.local, 0 campaign caches, clean tree, HEAD 9bd17be5 | TRUE (run.log; wrapper refusal conditions; 7, 8; reflog: HEAD 9bd17be5 from 03:16:46Z to 05:14:40Z) |
| exit 0 at 05:06:33Z | TRUE (run.log EXIT 0 / END; task output `WRAPPER_EXIT 0`) |
| total 4938.1 s (cap 10800 s), peak RSS 48.5 MB (cap 8192 MB) | TRUE (23) |
| no stop reason; runner guard self-check: pass | TRUE (`stop_reason` null; ALL_GUARDS_PASS true, independently re-evaluated) |
| approved ee1a6a8a...; qualification 114713ef (c06ce377); authorization 193b0122 (377bbcbb); GRANT ad95eef7 | TRUE (2-5, 16) |
| GRANT consumed: EXECUTION_STARTED before any science, then EXECUTION_COMPLETED bound to runs body 1e0d82ac... | TRUE (25, 26) |
| contract 8e86b509; gate 2d23a8b8; policy a6b33ef3; statement table b937cace; runner d958a457 | TRUE (11, 19-21) |
| D5/P32 (363 boxes), safety factor 3/2; certificates exactly F_D, F_H, F_K | TRUE (22, 24, 30) |
| no comparison, no adjudication, no adoption, no coverage-map r6; comparator not run | TRUE as far as mechanically observable (34-37; N4) |

The brief's further author claims (entry state, forensic preservation with top MANIFEST
1f3525fd..., wrapper sha256 cb07aa80..., PID 12156 with caffeinate -w, the p14 pre-/post-run
records) were each checked against bytes and found accurate.

## BLOCKERS

none

## Non-blocking observations

- **N1 (b) defence-in-depth limitation -- live GRANT in scratch clones.** Three scratch clones of the
  repository left by the Phase 13 authorization review,
  `/private/tmp/claude-501/-Users-suzhe-ReBaseGuard/ea6191ae-93b1-4f9c-b9ba-6cd0430d32ee/scratchpad/q13/review_work/{clone1,mclone,shallow}`,
  are checked out at 377bbcbb with a non-fixture GRANT (ALLOW) on disk. They are separate
  repositories whose refs predate the seal (the seal is not reachable there), so a runner pre-flight
  in clone1 or mclone (not shallow; `shallow` would be refused by `history_integrity`) could not see
  the seal: this is exactly the "another clone" case LIFECYCLE_SCOPE excludes. They were not used
  (clean status, no runs directory, no file newer than 03:30Z). Recommendation: the user removes
  these three clones (this reviewer may not). Not a defect of the sealed execution.
- **N2 (b) zero-cache precondition not enforced by the frozen runner.** The runner's pre-flight
  admits valid caches (frozen cache policy); zero caches at START rests on the wrapper's check
  and is corroborated here only post hoc (directory mtimes before START, 0 now).
- **N3 (b) concurrent-worker exclusion is point-in-time.** The process detector runs once at the
  pre-flight; no continuous monitoring over the 82-minute run. Corroborated by transcript
  snapshots and by agent logs showing no other campaign activity; absence is not provable.
- **N4 (b) "comparator not run" is not provable from artifacts.** By COMPARISON_TRANSACTION a
  pre-load refusal writes nothing; the absence of any comparator invocation rests on the agent
  logs (Claude transcripts, Codex log DB), not on repository state. File access times on this
  volume are lazily updated and cannot settle it.
- **N5 (d) EXECUTION_STARTED record not preserved as bytes.** Per protocol it is overwritten in place;
  its existence is shown by the runner's log line, two transcript snapshots and the
  `grant_sha256` carried into the final record (and it is deterministically reconstructible,
  sha256 40426d02...). A copy in phase14_execution would have been cheap corroboration.
- **N6 (d) the runs artifact names no cell.** Cell 306 is bound only indirectly (contract digest
  and scope, drift block, authorization/permission). Sufficient under the chain, but a reader of
  the runs artifact alone cannot see the cell.
- **N7 (c) path wording in the runner's output.** The `wrote ...` lines in run.log print
  namespace-relative paths while NEXT_STEPS (N6-1) prints repository-relative paths. Cosmetic.
- **N8 (d) disclosure of this review's own footprint.** The frozen identity checks called by the
  harness hash the C2 registry and the quarantine through `git hash-object` subprocesses
  (content-free ids); this updated the registry's access time. No content entered the reviewer's
  process; nothing else was written outside review_work.

No (a) load-bearing defect was found.

VERDICT: EXECUTION_ACCEPTED
