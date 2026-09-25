# C11R Phase 12 — independent QUALIFICATION review

- Reviewed qualification commit: `c06ce3774d3cc100fd16dfbd2d1c49c29e7d1021` (adds only
  `NS/evidence/qualification/C11R_QUALIFICATION.json`, blob `cdc65e4ca2ae778a035cca4f2e1555ccdd7f07c6`)
- Approved commit (root of trust, R8-reviewed): `ee1a6a8aab8ff57360249bc813a44b3c724200aa`
- R8 preservation commit (parent of the qualification commit): `5890511b6c74b1196112eb5d0e4d5c43b15b739e`
- Primary checkout: `/Users/suzhe/ReBaseGuard-k5c11r`, branch `p5y-k5-tail-c11r-n9-statement-alignment`
- NS = `level4/closure_proofs/p5y_k5_tail_c11r_n9_statement_alignment`
- Date of review: 2026-09-25
- Reviewer: new, independent qualification reviewer (no involvement in R1-R8 or in the qualification run).
- Work area (all writes): `.../scratchpad/q12/review_work` (scratch clones `clone*`, synthetic repos, harness scripts, outputs).

Finding classes used below: (a) real load-bearing defect in the qualification or its evidence;
(b) defence-in-depth limitation; (c) wording defect; (d) non-blocking robustness issue.

## 0. Entry checks

- `git rev-parse HEAD` in the primary checkout = `c06ce3774d3cc100fd16dfbd2d1c49c29e7d1021`; `git status --porcelain` empty. PASS.
- `c06ce377` has exactly one parent `5890511b`, whose parent is `ee1a6a8a`. `git diff-tree -r -M -C --find-copies-harder c06ce377`
  lists exactly one change: `A NS/evidence/qualification/C11R_QUALIFICATION.json`. `git diff --name-status A HEAD` lists only that
  file and `NS/review/REVIEW_C11R_PREFREEZE_R8.md` (added at 5890511b). PASS.
- Committed file: sha256 `56999720aeca1f03c25e7e103355e857acd5daf7239eaee37d7d24db4c5a0fcf`, git blob `cdc65e4c...` (disk = HEAD), mode 100644; matches the author's claim.
- Loose objects written into the common object store on 2026-09-25 after 03:53 local: exactly one blob (`cdc65e4c`, the qualification), six trees and the commit `c06ce377`, all at 10:05:11 local (= 01:05:11Z, the commit time). No second qualification blob, no other staged-and-abandoned object; packs are older (latest Sep 20). The worktree's HEAD reflog shows `5890511b -> c06ce377` as a plain commit, no reset/amend.

## Method (how I checked, briefly)

- Static reading of `c11r_launch.py`, `c11r_qualify.py`, `c11r_contract.py` (all 2199 lines), `c11r_common.py`, `c11r_status.py`, the gate and the contract; R8 read as history.
- All Python ran under the launch-policy invocation (frozen interpreter `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14`,
  `-I -S -B --check-hash-based-pycs default -X int_max_str_digits=0`, `env -i` with HOME, LANG, LOGNAME, USER, TMPDIR and the frozen PATH).
- In the PRIMARY checkout I ran only read-only things: git plumbing with `GIT_OPTIONAL_LOCKS=0` (no index refresh), my read-only harness
  `review_work/harness_a.py` (independent re-verification of the record), `review_work/cachecheck.py`, `review_work/prestatus_mine.py`,
  and the permitted `c11r_launch.py qualify --self-test` and no-argument `qualify`. Afterwards: HEAD still `c06ce377`, `git status --porcelain
  --untracked-files=all` empty, the `__pycache__` listing byte-identical before/after (md5 of `ls -laT`), index file mtime unchanged (10:05:11, the commit).
- Scratch repositories (all under `review_work/`): `clone1` (`git clone --no-local` + checkout `c06ce377`), `qclone` (a copy of clone1 moved back to
  `5890511b` with every ref that contained `c06ce377` moved to `5890511b` and reflogs expired = the exact pre-qualification repository state),
  `hclone` (copy of clone1 for hostile starts and planted material), and per-scenario copies `scen/S*` (deleted after use, results recorded below).
- Harnesses: `harness_a.py` (record re-verification), `harness_b.py` (forged records vs `verify_qualification`), `harness_c_eval.py` + `scen.sh`
  (synthetic repositories vs `lifecycle`, `protocol_history(stage="authorize")`, `frozen_state`, `protocol_artifacts_anywhere`, `_authorization_facts(stage="authorize")`),
  `harness_d.py` (Q1-Q18 facts recomputed at 5890511b), `harness_e.py` (module-origin attacks), `hostile_env.sh`, `plant.sh`, `forge_pyc.py`, `detect.py` (sentinel matrix).
- What I did NOT do: I never ran `c11r_qualify.py --approved-commit` / `c11r_launch.py qualify --approved-commit` on the supported path anywhere;
  never ran `c11r_runs.py` with an argument (only the permitted no-argument `c11r_launch.py run` usage form in the scratch clone `hclone`);
  never ran any compare with `--approved-commit`; never called `build_authorization`; never read the quarantine; never ran the chain-controls suite
  (it launches `c11r_runs.py` with arguments in synthetic repositories). No background process was started.

## The committed record, re-verified from bytes (basis for attacks 1-12)

`harness_a.py` on the primary checkout (read-only), independent of the author's scripts:
- file bytes == `json.dumps(record, indent=1, sort_keys=True) + "\n"` (exactly what `write_evidence` writes; pure ASCII);
  HEAD blob == disk bytes; stored `sha256` == my own recomputation of the canonical body digest (`114713ef...`), without using CT.
- `bound`: approved_commit == A (full 40-hex); `execution_contract_sha256` == body digest of the contract AS COMMITTED AT A (`8e86b509...`, which is also
  its stored `sha256`); `gate_sha256` == body digest of the gate at A (`2d23a8b8...`); `policy_sha256` / `statements_sha256` == body digests at A ==
  the contract's `artifacts.{policy,statements}.body_sha256` (`a6b33ef3...`, `b937cace...`); `qualifier_sha256` == sha256 of `c11r_qualify.py` at A ==
  the contract's code entry (`95520529...`). (The provenance `inputs` show `C11R_POLICY.json` / `N9R_GATE_C11R.json` with different digests because
  those are FILE sha256s; I checked them separately, below.)
- items: exactly 18, ids Q1..Q18 in order, no duplicate/unknown, every name equal to the contract-at-A `qualification_items`, every status `PASS`,
  every item's `bound` exactly `{approved_commit: A, execution_contract_sha256: 8e86b509..., qualifier_sha256: 95520529...}`, every item exactly the keys
  `{bound, detail, id, name, status}`. My independent class: PASS == stored class.
- `c11r_contract.verify_qualification(repo, q, chain_roots(repo), approved_commit=A)` -> `problems: []`, disposition PASS.
- provenance: producer path = `NS/code/c11r_qualify.py`, producer_sha256 == qualifier at A; each of the 14 `code_closure` entries equals the sha256 of that
  file AT A and the contract's code entry (incl. `c11r_launch.py` 839faeae...); the closure key set equals `code_closure(c11r_qualify.py)` recomputed;
  the 9 `inputs` are exactly the nine artifacts `main()` loads and each equals the file sha256 at A.
- `environment.host` == contract-at-A `cost_host` == this host now. `fixture: false`, schema `C11R_QUALIFICATION/5`, `chain_root_problems: []`,
  `computes_on_open_cells: false`, `produces_target_constants: false`, `runs_before: "any target execution"`, `nt_configuration` = NT / 5/2.
- chain_roots now: no problems; contract/gate digests now == at A; `approved_commit_problems(A)` = []; `code_dir_shadows(contract@A)` = [];
  `preimport_barrier_problems` = [].

## Required attacks

### 1. A missing Q-item
Checked: `harness_b.py` feeds forged records (re-sealed with a correct body digest, so only the item logic can refuse) to the production
`verify_qualification`. Dropping Q7 -> refused (`required item(s) missing: ['Q7']` + stored class != recomputed FAIL); unsealed variant also refused on the
digest; empty item list, items as a dict, `items` key absent -> refused. The committed record has all 18 (independent count above).
Finding: PASS.

### 2. A duplicated Q-item
Checked: an extra copy of Q3; Q18 replaced by a second Q3 (18 items, one missing, one duplicate); a duplicate Q5 whose second copy is FAIL -> all refused
(`duplicate item(s)`, plus `missing` / `failing` where applicable). Committed record: no duplicate.
Finding: PASS.

### 3. A forged top-level PASS
Checked: Q5 status FAIL with class PASS (re-sealed) -> refused (`failing item(s) ['Q5']; stored class 'PASS' is not the recomputed disposition 'FAIL'`);
class `"PASS "`, class absent -> refused; an honest FAIL record -> refused (FAIL). In a synthetic repository (scenario S14) the forged-PASS record committed in place of the
real one -> `_authorization_facts(stage="authorize")` refuses (lifecycle MALFORMED / protocol history). The disposition is recomputed from the items; nothing stored is trusted.
Finding: PASS.

### 4. One failing Q-item hidden under PASS
Checked status spellings on Q11: `pass`, `"PASS "`, `True`, `None`, `1`, `["PASS"]`, key absent -> each refused (`not one of ['PASS','FAIL']` + failing);
non-canonical name, id `q11`, id `11`, unknown `Q19`, a non-dict item -> refused. NOTE (by design, stated in `QUALIFICATION_PROVES`): an item whose `detail`
says it failed (`{"pass": false, "exit": 1, "last_line": "... REFUSE"}`) but whose `status` is PASS is ACCEPTED -- the record is an attestation of statuses,
not of executed checks. For the committed record I checked every detail against its status and recomputed the facts (section "Q1-Q18 recomputed"): no detail contradicts its PASS.
Finding: PASS for the record; the detail/status non-coupling is class (b), already stated by the contract.

### 5. A wrong approved commit
Checked: a record bound (top level and items, re-sealed) to `5890511b...` verified against A -> refused; items-only and top-only rebinds -> refused; the
honest record verified against `5890511b` -> refused. Chain level: `_authorization_facts(stage="authorize")` with approved commit `5890511b` (a full id whose
frozen state is identical to A's -- the contract's stated limitation (4)) -> REFUSED because the committed qualification binds A (scenario S15b). So this
qualification pins the root of trust to the R8-reviewed commit: a Phase 13 authorization naming any other commit is refused by it.
Finding: PASS. (Stated limit (4) remains for a hypothetical re-qualification bound to another equivalent commit: class (b), not this record.)

### 6. An abbreviated or moving reference
Checked `ee1a6a8a`, `ee1a6a8aab8f`, `HEAD`, the branch name, `A^{commit}`, `HEAD~2`, upper-case A, A plus newline, and A's TREE id:
`approved_commit_problems` refuses every one (not a full 40-hex commit id / does not exist); `frozen_state(...)["ancestry"]` refuses every one; a record carrying
any of them is refused when verified against A; `_authorization_facts` with the short id refuses (S15). The committed record carries the full id.
NOTE: `verify_qualification` by itself accepts a record carrying a moving ref IF the caller passes the same moving ref (it compares, it does not call
`approved_commit_problems`); every production caller (`_authorization_facts`) calls `approved_commit_problems` and `frozen_state` first. Class (d).
Finding: PASS.

### 7. A wrong contract
Checked: `bound.execution_contract_sha256` wrong (top+items), items-only, and the contract FILE sha256 used instead of the body digest -> refused.
Chain level (S21): a contract edited and committed after the qualification -> `tree identity` + `history purity` refusals (and a typed `not evaluable` refusal
for the malformed file) at `_authorization_facts`. The committed record's contract digest equals the contract at A.
Finding: PASS.

### 8. A wrong gate
Checked: `bound.gate_sha256` wrong -> refused (`gate_sha256 belongs to another contract or tree`). The gate is a frozen path; its body digest at A is the
bound one; guard DENY; bound to contract 8e86b509.
Finding: PASS.

### 9. A wrong policy
Checked: `bound.policy_sha256` wrong, and the policy FILE sha256 instead of its body digest -> refused; `statements_sha256` wrong -> refused.
Finding: PASS.

### 10. A wrong launcher (bytes, mode, first line, path)
Checked: bytes -- the launcher is a contract code root (`roles.launcher`), frozen path, sha256 `839faeae...` == A == HEAD == disk, and appears in the
record's provenance closure with that digest. S22 (first line with `-IS` removed, committed) -> `code identity differs for ['c11r_launch.py']`,
`launch policy: c11r_launch.py does not start with the frozen interpreter line`, tree identity, history purity: refused. Mode -- 100755 at A, at HEAD, in the
index, executable on disk. BUT (S23) a committed mode change 100755 -> 100644 with unchanged bytes is NOT detected by `frozen_state` (blob ids carry no mode)
nor by anything on the authorization path; only `c11r_status`'s pre-result condition checks the mode, and that verifier is REFUSE by design after Phase 12.
Impact: none on what runs (a non-executable launcher cannot be kernel-started; `python3.14 c11r_launch.py` is refused as not isolated; `python3.14 -IS
c11r_launch.py` is equivalent to the kernel start). Path -- the launcher execs the program next to its own realpath and refuses a symlinked or non-regular
program; the record cannot show which path was used (class (b), next item).
Finding: PASS for this qualification; mode not bound by the contract/chain: class (d).

### 11. A wrong qualifier (bytes; provenance producer)
Checked: qualifier digest wrong everywhere + provenance -> refused (`produced by another qualifier`, `provenance producer is not the bound qualifier`, items
bound to another qualifier); provenance producer digest only -> refused; provenance absent -> refused. NOT refused by `verify_qualification`: a changed
provenance producer PATH with the right digest, a foreign digest for `c11r_contract.py` inside `provenance.code_closure`, emptied `provenance.inputs`
(harness_b rows 11c-11e). For the committed record I verified all three by hand (producer path = the NS qualifier; all 14 closure digests = A; all 9 inputs = A).
Finding: PASS for the record; the verifier's unchecked provenance closure/inputs: class (b) (see non-blocking N-2).

### 12. A stale qualification
Checked: another host (node, python) -> refused (not the cost host / not this host); schema /4 -> refused; `fixture: true` and `fixture: "false"` -> refused
(`allow_fixture` defaults to False in every production entry point and is passed as True only by `c11r_chain.py`); bad stored digest -> refused; `None` -> refused. Replaced / re-introduced (synthetic
repositories): S1 edited+re-sealed qualification committed on top -> refused (`commit c06ce377 holds a qualification artifact other than the current one`);
S2 delete + re-add of identical bytes -> refused (`introduced by 2 commits`); S3 edit then revert -> refused; S5 on disk but uncommitted -> refused
(MALFORMED; not committed at HEAD); S6 committed but modified on disk -> refused. Earlier commit / other tree: the record does not bind the HEAD it was produced at;
its Q2 detail (`commits_checked: 1`) is consistent only with HEAD = 5890511b at run time (A..HEAD = one commit), and every bound digest equals A.
NOT refused: a DIFFERENT qualification held on a sibling branch (S7), only in a reflog entry (S7b), or a second introduction on a sibling (S7c):
`protocol_history(stage="authorize")` checks the qualification only in HEAD's history after A, and `_protocol_elsewhere` does not cover the qualification.
For THIS repository I checked directly: of the 729 commits reachable from any ref, HEAD or any reflog entry, exactly one (`c06ce377`) holds any file
under `evidence/qualification/`, and the object store holds no other qualification blob (loose-object census, section 0).
Finding: PASS for the record; qualification uniqueness outside HEAD's history is not enforced by the chain: class (b) (N-3).

### 13. A direct qualifier invocation instead of the launcher
Checked (scratch clone `hclone` only; each form first probed with `--self-test`, then the brief-sanctioned hostile `--approved-commit A` form):
- `python3.14 c11r_qualify.py --approved-commit A` (allowlisted env, no flags) -> `REFUSE (pre-import barrier ...): not started isolated and without site`, rc 1;
- launch flags + one extra env name (`FOO=1`) -> refused (`environment names outside the frozen allowlist: FOO`);
- launch flags + `-O` -> refused (`assertions stripped`); `--check-hash-based-pycs never` -> refused; PATH not frozen -> refused;
- `python3.14 c11r_launch.py qualify --approved-commit A` from a NON-isolated interpreter with PYTHONPATH -> `REFUSE (launcher)` rc 2.
After all of them the clone's qualification file had the same sha256 and mtime and `git status --porcelain --untracked-files=all` was empty: nothing was written.
NOTE: the barrier and L0 enforce the interpreter POLICY, not the launcher's use. A direct start with exactly `CHILD_FLAGS` and the allowlisted environment
is accepted (it is what the launcher execs), and so is a policy-compliant `-c` wrapper that first executes arbitrary code and then `runpy.run_path`s the program
(demonstrated with `--self-test` only: sentinel `wrapper_ran_first` written, the program ran, `launch_policy_problems()` in that process = []).
The record can therefore attest "run under the launch policy", not "run through c11r_launch.py"; a wrapper is deliberately malicious in-process code, which
the contract does not claim to cover. The launcher docstring's "a direct start is refused by the program's barrier" and `LAUNCH_POLICY.not_covered`'s
"a boundary program started some other way is refused by its barrier" are true only for NON-compliant starts (class (c), N-7).
Finding: PASS for the qualification (evidence in item 40 / "supported path" section); class (b) + (c) noted.

### 14. An unsafe interpreter mode
Checked against the launcher (`python3.14 <opts> hclone/.../c11r_launch.py qualify --self-test`): `-O`, `-OO`, `--check-hash-based-pycs never`, `... always`,
`-X dev`, `-X pycache_prefix=...`, `-X frozen_modules=off`, `-X utf8`, `-X importtime`, `-W error`, `-b`, `-I` without `-S`, `-S` without `-I`, `-E -s -S`
-> every one `REFUSE (launcher)` rc 2 (`-X int_max_str_digits=100` is a fatal CPython start-up error, rc 1). Another interpreter: `/usr/bin/python3` -> refused
(not isolated, not the frozen one); a byte-copy of the frozen binary -> refused (`not the frozen one`); `/usr/bin/python3 -I -S` crashes with
`AttributeError: 'sys.flags' object has no attribute 'safe_path'` before any exec (class (d), harmless). Accepted: `-IS` (kernel-equivalent), `-X
int_max_str_digits=0 -IS`, a symlink to the frozen binary (same realpath), and the launcher-only `-v`, `-u`, `-d` (they affect only the launcher process,
which then execs the child with the fixed `CHILD_FLAGS`). Direct qualifier starts with the policy flags plus one unsafe option (`-O`, `never`, `-X
pycache_prefix`) -> refused by the barrier. `-X pycache_prefix=<dir with a forged start-up encodings cache>` on the launcher fires the forged cache at
interpreter start-up BEFORE the refusal (sentinel `pcp_encodings`) -- a non-supported start, the stated not-covered class.
Finding: PASS on the supported path; class (b) for the stated start-up window of non-supported starts.

### 15. A hostile Python environment (sentinels written with `posix`)
Positive controls first (a plain `python3.14 -c pass`): PYTHONPATH (sitecustomize+usercustomize), PYTHONUSERBASE (.pth), PYTHONPYCACHEPREFIX (forged
timestamp-valid `encodings/__init__` cache), PYTHONHOME (symlinked stdlib + sitecustomize), user-site `.pth` via a hostile HOME, and DYLD_INSERT_LIBRARIES
(an unsigned arm64 dylib constructor; the frozen binary carries `allow-dyld-environment-variables` and `disable-library-validation`) all FIRE;
PYTHONSTARTUP (non-interactive), PYTHONCASEOK, LD_PRELOAD/LD_LIBRARY_PATH do not.
- SUPPORTED LAUNCHER PATH (kernel start of `c11r_launch.py qualify --self-test`): PYTHONPATH, PYTHONUSERBASE, PYTHONSTARTUP, PYTHONPYCACHEPREFIX,
  PYTHONHOME, PYTHONCASEOK, LD_PRELOAD/LD_LIBRARY_PATH -> `REFUSE (launcher): the environment carries [...]`, rc 2, NO sentinel (no hostile Python ran).
  Hostile HOME with a user-site `.pth` -> accepted (HOME is allowlisted), self-test ALL_PASS, NO sentinel (`-IS` / `-I -S`: no user site).
  Extra names incl. `GIT_DIR`, `TERM`, `FOO` -> accepted and dropped by `child_env` (the child's barrier would otherwise refuse them), NO sentinel.
  `__PYVENV_LAUNCHER__` -> accepted, inert (R8 O-2). DYLD_INSERT_LIBRARIES -> refused by name, BUT the dylib constructor HAD ALREADY RUN (sentinel
  `dyld` twice: the framework stub and the interpreter) -- hostile NATIVE code executes on the supported path before the refusal; this is exactly the stated
  not-covered class ("native code injected by the dynamic linker ... acts before any Python"); the child never starts.
- DIRECT START (`python3.14 c11r_qualify.py --self-test`): PYTHONPATH, PYTHONUSERBASE, PYTHONPYCACHEPREFIX, PYTHONHOME, hostile-HOME user site and DYLD all
  FIRE at interpreter start-up, then the barrier refuses (rc 1); PYTHONSTARTUP, PYTHONCASEOK, LD_* do not fire; all refused.
Finding: PASS: on the supported launcher path no hostile PYTHON*/HOME code executed; DYLD native injection executes (stated, class (b)); direct starts
execute start-up hooks and are then refused (stated, class (b)). For the actual run: the launcher would have refused any PYTHON*/DYLD_*/LD_* name, so the
successful run itself implies none was present in its environment.

### 16. A loaded-module shadow
Checked (hclone, supported launcher): `fractions.py` and `sitecustomize.py` in the c11r code dir, an unprefixed file in C11's code dir -> barrier refuses,
no sentinel (launcher and direct). A prefixed extra source (`c11r_evil.py`, `c11r_common_copy.py`) passes the barrier by design (never imported, no sentinel) and is
refused by S (`code_dir_shadows`: not in the frozen inventory; untracked). `harness_e.py` (synthetic module tables, production `verify_loaded_modules`): a same-bytes
copy of `c11r_schema` loaded from another directory -> `loaded from another file`; `__file__`/`__spec__.origin` disagreeing -> L2 refusal; a contract file loaded
under another name -> refused; the honest module -> no problem. In the committed record: Q4 `loaded_modules.problems: []`, 14 checked modules == 14 required.
Finding: PASS.

### 17. Unexpected campaign-directory material
Checked: package dir, empty namespace dir, `x.zip`, symlink `c11r_link.py` in the code dir -> barrier refuses (launcher path, no sentinel). Primary checkout now:
`code_dir_shadows(contract@A)` = [], barrier problems = [], the only untracked/ignored material under NS is `__pycache__` (21 cache files, all dated before the
run, see 18); `git ls-files --others --ignored --exclude-standard` in NS lists nothing else; no NS file other than the qualification has an mtime after the R8
file (03:53). evidence/config inventory: the qualification file is the only file outside `PRE_RESULT_ARTIFACTS` + quarantine (expected after Phase 12).
Finding: PASS.

### 18. A sourceless .pyc
Checked: a bare `c11r_schema.pyc` in the code dir -> barrier refuses; `__pycache__/fractions.cpython-314.pyc` (non-inventory stem, unchecked header) -> not
executed (no sentinel; CPython reads `__pycache__` only for a found source) and refused by S; a sourceless loader for a contract module -> L1 refuses.
RESIDUAL (known since R8 item 3, re-measured): a forged ACCEPTED cache of an INVENTORY stem (`__pycache__/c11r_schema.cpython-314.pyc`, unchecked-hash or
matching-timestamp header) passes the barrier (which admits `__pycache__` wholesale) and S (it is named like an inventory cache) and EXECUTES on the supported
launcher path (sentinel fired during `qualify --self-test`); it is detected only post-load by `_pyc_matches_source` (`has cached bytecode that is not the
compilation of its verified source`, which Q4 / runner pre-flight / comparator step 12 would report). For the actual run: `cachecheck.py` on the primary shows
every cache CPython would accept (12 files) equals the compilation of its verified source, the other 9 are stale (ignored by the loader), all mtimes predate
the run, and Q4 recorded no cache problem. Evidence that `-B` was in effect: stale caches of modules the qualifier and its Q11 subprocess import
(`c11r_certificate`, `c11r_policy`, `c11r_qualify`) were NOT rewritten at 10:03.
Finding: PASS for the qualification; pre-detection execution of a forged accepted cache: class (b) (N-4).

### 19. A wrong module origin
Checked: see 16 (harness_e rows a, b, c, e) and a module named `fractions` loaded from inside a campaign code dir -> `not an approved contract source`.
Record: Q4 `execution_root` is the primary checkout; `campaign_origin_modules` contains `__main__` (not `c11r_qualify`), i.e. the qualifier ran as the program,
and `c11r_launch` (imported by `c11r_contract`); my own process under the same policy reproduces the same 14 checked names.
Finding: PASS.

### 20. git replace
Checked (S16): `git replace` of the qualification blob by an edited blob and `git replace --graft HEAD A`. Plain git then shows the replaced content
(`seconds` changed) and a one-commit A..HEAD; the campaign (`--no-replace-objects` + `GIT_NO_REPLACE_OBJECTS=1`) reads the real objects:
lifecycle QUALIFIED, protocol history clean, qualification digest the real one. Primary: 0 replace refs.
Finding: PASS.

### 21. Grafts
Checked (S17): `.git/info/grafts` present -> `history integrity: a grafts file rewrites commit parentage` -> `frozen_state` ancestry problem ->
`_authorization_facts` refuses. Primary: no grafts file.
Finding: PASS.

### 22. Shallow history
Checked (S18): `git clone --depth 3` -> `history integrity: the repository is shallow` -> refused. Primary: `--is-shallow-repository` false, no `shallow` file.
Finding: PASS.

### 23. A hostile commit-graph
Checked (S20): a side branch holding a foreign qualification AND an edited frozen file, merged with `-s ours`; `git commit-graph write`; I patched the CDAT
record of the merge so its second parent is GRAPH_PARENT_NONE and recomputed the trailer. After deleting the side ref and expiring reflogs, plain git
(graph honoured) reports ONE parent and `rev-list HEAD` / `rev-list --all --reflog` omit the side commit; with `core.commitGraph=false` (what `git_env` sets)
the side commit is seen and `_authorization_facts` refuses (history purity for `c11r_launch.py` + foreign qualification). Primary: split commit-graph files
dated Sep 18-19 (ignored by campaign git); `rev-list --all --reflog HEAD` gives 729 commits with and without the graph (author's 728 + the qualification commit).
Finding: PASS.

### 24. Hostile GIT_* state
Checked: (i) S19 -- the evaluating process given `GIT_DIR`/`GIT_WORK_TREE`/`GIT_OBJECT_DIRECTORY` pointing at another repository at 5890511b, `GIT_INDEX_FILE`,
`GIT_REPLACE_REF_BASE`, `GIT_GRAFT_FILE`, `GIT_CONFIG_PARAMETERS` (commitGraph=true), `GIT_NAMESPACE`: every result identical to the honest clone
(`git_env` strips every `GIT_*`); (ii) on the supported path `GIT_*` never reaches the child (launcher test with `GIT_DIR=/nonexistent` passed). Config reached
through HOME (R8 O-1, `core.fsmonitor`): the operator's effective config (`git config --list --show-origin`) has no `core.fsmonitor`, `core.hooksPath`,
`include`, `excludesFile` or alias; `~/.gitconfig` (Sep 12) sets only `safe.directory`/user; `~/.config/git/ignore` (Aug 20) ignores only
`**/.claude/settings.local.json`; no `/etc/gitconfig`. So no operator git hook could have run during the qualification.
Finding: PASS; O-1 remains class (b/d) as recorded by R8.

### 25. An authorization unexpectedly present
Checked: primary -- no `config/C11R_AUTHORIZATION.json` on disk, none in any of the 729 commits. Synthetic: S8 dummy authorization on disk -> lifecycle MALFORMED,
`_authorization_facts` refuses; S12 authorization committed on a sibling branch -> `protocol lineage: ... hold a authorization artifact that stage authorize does not admit`.
Finding: PASS.

### 26. Execution permission unexpectedly ALLOW
Checked: primary -- no permission record anywhere; gate guard DENY (at A and now); `lifecycle(...)["execution_permission"]` = DENY. S9 a planted record
claiming GRANT/ALLOW on disk -> MALFORMED + `no execution permission GRANT was committed with the authorization` -> refused. The qualification contains no
guard/permission field.
Finding: PASS.

### 27. Runs unexpectedly present
Checked: primary -- no `evidence/runs` on disk or in any commit. S10 empty `evidence/runs/` -> `a runs artifact already exists`; S10b a dummy runs file -> MALFORMED + refused.
Finding: PASS.

### 28. A comparison unexpectedly present
Checked: primary -- no `evidence/comparison` anywhere. S11 dummy comparison -> MALFORMED (`a comparison file already exists ... not committed`) -> refused.
Finding: PASS.

### 29. Target-science contamination
Checked: statically, the qualifier's `main()` computes only: Q3 the policy's pure choice rule on the committed NON-TARGET cost model; Q5 an AST import scan;
Q13 `X.kernel_apply` / `I.kernel_apply_iv` at the scalar 5/2 (point block [5/2, 5/2]); Q14 `kernel_apply_iv` / `atom_contribution_iv` on
NT = [5/2, 5/2 + 108337/1250000]; Q11 runs `c11r_status.py --verify-only`, whose only numerics are `Q.self_test()` (same NT/5/2 functions). No module in the
import closure performs a computation at import time (AST scan of module-level statements: only constants, NT definitions, regexes, `sys.path` inserts,
the open-guard install). The record states `computes_on_open_cells: false`, `nt_configuration` NT/5/2. My own recomputations (Q13, Q14) used only 5/2 and NT;
I evaluated nothing on 306-309.
Finding: PASS.

### 30. Target-value contamination
Checked without reading the quarantine: every numeric leaf of the record, by key path (harness_a): counts (`commits_checked` 1, `paths_checked` 44,
`replace_refs_ignored` 0, `approved_sources` 27, `modules_examined` 119, `modules` 27, `exit` 0), configuration (depth 5, panels 32), NT/5/2 labels,
probe states "0","0","3","1", host strings, `disk_free_gb`, `seconds`, and ONE non-integer computed float, Q14 `separation`, which I recomputed bit-identically on NT
(harness_d). Every string digit sequence is a hash, a path, a module name, a version or an NT constant. The commit message's numbers are digests, times,
the frozen caps/safety factor/configuration and the co-author line. The commit adds no other file. No `value`/`magnitude`-type key exists in the record
(its keys are exactly the typed schema). The quarantine's object id at HEAD is unchanged (frozen path; `frozen_state` tree identity + history purity clean).
Finding: PASS.

### 31. D5/P32 drift
Checked: contract at A and at HEAD: depth 5, panels 32; policy at A and HEAD `chosen` {5, 32}; Q3 re-derived {5, 32} == frozen, and I re-derived it myself (harness_d, equal detail).
Finding: PASS.

### 32. Cap drift
Checked: contract and policy at A and HEAD: `cap_seconds` 10800, `cap_rss_mb` 8192; `c11r_policy.CAP_SECONDS`/`CAP_RSS_MB` identical at A and HEAD; the
policy/contract/cost files were last touched by A (`ee1a6a8a`) and are frozen paths.
Finding: PASS.

### 33. Safety-factor drift
Checked: `safety_factor` "3/2" in contract and policy at A and HEAD; `c11r_policy.SAFETY_FACTOR = F(3, 2)` at A and HEAD; Q3 checks it (no problem).
Finding: PASS.

### 34. Qualification commit ordering
Checked: introduced exactly once (`c06ce377`, a descendant of A via `5890511b`), committed at HEAD (HEAD blob == disk), nothing else in the commit
(diff-tree with rename/copy detection), no delete/recreate/revert cycle (the path is touched by one commit in `git log --all --reflog -m`), no other ref
or reflog entry holds any file under `evidence/qualification/` (729 commits), no other qualification blob in the object store. Now:
`protocol_history(A, "authorize")` -> `problems: []`, `introducers.qualification = [c06ce377]`, `foreign` empty, 2 commits after A, 729 repository commits;
`lifecycle(A)` -> QUALIFIED, `problems: []`, held `["qualification"]`, execution permission DENY; `lifecycle_problems(A, "authorize")` = [];
`frozen_state(A)` clean with 2 commits checked (clone). And `_authorization_facts(A, stage="authorize")` on an exact clone -> `problems: []` with
`qualification_digest` 114713ef... -- the next phase is not blocked by anything in the chain. The chain itself does not enforce "nothing else in that commit"
(S4: a qualification commit that also adds a review file is accepted) -- class (d), N-5; verified by hand here.
Finding: PASS.

### 35. R1-R8 preservation
Checked each file: disk blob == HEAD blob == blob at its preservation commit; absent in that commit's parent; touched by exactly that one commit in all refs +
reflog (with `-m`): R1 8a445008 @6d7cd546, R2 af431bc0 @6ae05833, R3 19e276e4 @f6c737c3, R4 b2afdb49 @5c5203c1, R5 43c5f4c8 @ebf08c0f, R6 b61e6ac8 @63402106,
R7 b3574837 @ac75c198, R8 e82ffa5e @5890511b (last line `DISPOSITION: READY_TO_QUALIFY`). The review directory holds exactly these eight files.
Finding: PASS.

### 36. Historical verdict preservation
Checked: the C11 head 440bcd91 is an ancestor of HEAD, and `git diff --name-only 440bcd91 HEAD` outside NS is EMPTY: no predecessor (C2-C11) file, and no file
anywhere outside this namespace, changed since C11 was published. C11's verdict artifacts still carry EXECUTION_INVALID (count-only grep: README, `c11_result.py`,
`N9_GATE_C11.json`, `C11_N9_RESULT.json`). B0 (frozen, produced before A) records B0_04 (C11 EXECUTION_INVALID, not rewritten), B0_05 (N9 OPEN), B0_11
(no predecessor file modified); the gate's `predecessor_state_preserved` states C2-C10 immutable, C11 EXECUTION_INVALID, N9 OPEN.
Finding: PASS.

### 37. r5 authority
Checked: `K5_COVERAGE_MAP_R5.json` blob `f978eeb6...` at HEAD, at A, at 440bcd91 and on disk; introduced by one commit (`ae4cbc2c`) and never modified in any ref/reflog.
Finding: PASS.

### 38. Absence of coverage-map r6
Checked: `git log --all --reflog -m --name-only` over all history lists no path matching `COVERAGE_MAP_R6` (case-insensitive); `git ls-files` 0; no such file
in the working tree (find, excluding .git); the coverage directory holds only `K5_COVERAGE_MAP_R5.json`.
Finding: PASS.

### 39. main untouched
Checked: local `refs/heads/main` = `c123b9bb8f15d17650545b3fce4aca8a6b61093b` (packed ref; last reflog move 2026-09-03), ancestor of HEAD;
`git -C /Users/suzhe/ReBaseGuard ls-remote origin refs/heads/main` = `1cb453826313c189f0bdafd5b84120c1edb74da9` (GitHub); both equal
`C11R_B0.json` LOCAL_MAIN_REF / REMOTE_MAIN_REF. The C11R branch does not exist on GitHub (ls-remote empty): never pushed.
Finding: PASS.

### 40. Launcher isolation guarantees
Checked:
- Before validation the launcher process loads only built-in/frozen modules (`os`, `posix`, `_imp`, ...) plus the host stdlib's `encodings`, `encodings.aliases`,
  `encodings.utf_8` at interpreter start-up (`-IS -v` trace); no campaign file and nothing from the environment is imported. Its own imports (`os`, `sys`, `_imp`)
  are already-loaded/built-in.
- It checks its interpreter (flags, hash mode, pycache prefix, -X, warnings, realpath of the executable) and refuses PYTHON*/DYLD_*/LD_* names (names only)
  before anything else; only then `os.execve(FROZEN_INTERPRETER, [interp, -I, -S, -B, --check-hash-based-pycs, default, -X, int_max_str_digits=0, <realpath
  program>, *argv[2:]], child_env)`; a symlinked or non-regular program is refused.
- Arguments: `argv[1]` must be run|compare|qualify (else usage, rc 2); the rest is passed as the program's argv after the program path (cannot become
  interpreter options: `qualify -c 'print(1)'` reaches the qualifier's usage refusal). Junk/no-argument forms all end in usage refusals.
- Child environment: exactly the allowlisted names present, PATH forced to `/usr/bin:/bin:/usr/sbin:/sbin`; extra names are dropped (verified: the child's barrier,
  which refuses any extra name, passed).
- Hostile code on the supported path: none from PYTHON* variables, user site, `.pth`, start-up hooks, pycache prefix, PYTHONHOME (sentinel matrix, 15);
  DYLD_INSERT_LIBRARIES native code DOES execute in the launcher process before its refusal (stated not-covered); a forged accepted cache of an inventory stem in a
  campaign `__pycache__` DOES execute in the child before post-load detection (18, class (b)); the host interpreter and its stdlib (group-admin writable on this
  host) are trusted by statement.
- Binding: bytes (sha256 839faeae..., blob d280ee02, frozen path, code root `roles.launcher`), first line (`LAUNCH_POLICY.launcher_first_line`, re-derived from the
  committed bytes by `preimport_barrier_problems`), path (`LAUNCH_POLICY.launcher`) and the whole launch policy (canonical sha256 773246f3..., equal to the module
  constants and to A's) are bound in the contract. The mode is not (10; class (d)).
Finding: PASS, with the stated residuals (b).

## Is the evidence consistent with exactly ONE supported-path run of the frozen qualifier?

- Code: the qualifier, launcher and every closure module that ran are A's bytes (record provenance closure == A; Q4 attested the loaded modules; my
  re-derivation of the required set and of the 14 checked names matches).
- Policy: Q4 folds in `launch_policy_problems()` = [] (flags, hash mode, prefix, -X, warnings, frozen executable, env allowlist, frozen PATH) -- attested; the
  launcher would have refused any PYTHON*/DYLD_*/LD_* name, and the child's barrier any extra name.
- `-B` in effect: stale caches of modules the qualifier (`c11r_certificate`, `c11r_policy`) and its Q11 subprocess (`c11r_qualify`, imported by the status
  verifier) load were NOT rewritten at 10:03 (their mtimes are Sep 23-24); no cache in any campaign `__pycache__` is newer than 01:49 local.
- Program: `campaign_origin_modules` contains `__main__` from the campaign directory and Q4 checked `c11r_qualify.py`; `execution_root` = primary checkout.
- Time line: preverify 09:58:50; ROOT_OF_TRUST 10:02:56; log START 01:03:07Z / END 01:03:22Z (= record `seconds` 15.0); the artifact's mtime is 10:03:22
  (the END second, never touched afterwards); post-verifications 10:04:34 (file sha256 56999720... uncommitted) and 10:05:28 (committed); commit 10:05:11
  local = 01:05:11Z. Q2 `commits_checked: 1` => HEAD was 5890511b at run time; Q17 `lifecycle_state: FROZEN` => no qualification file existed at run time.
- Uniqueness: one qualification blob ever written to the object store; one commit (of 729) holds the path; Q11/Q17 of any re-run on a qualified tree would FAIL.
- Limits (stated, not claimed): the record cannot distinguish the launcher from any other launch-policy-compliant start (13), and an earlier run whose file was
  deleted before commit would leave no trace in git (the chain does not claim otherwise; `QUALIFICATION_PROVES`). Nothing I found suggests either.
Conclusion: consistent with exactly one supported-path run.

## The disclosed status-verifier observation (G13 / Q11) -- adjudication

Reproduced: in `qclone` (the exact pre-qualification repository state: HEAD 5890511b, no commit anywhere holding a qualification) `c11r_status.py --verify-only`
prints `VERIFY-ONLY STATUS_CLASS = CONSISTENT`, exit 0 -- exactly Q11's recorded `{exit: 0, last_line: "VERIFY-ONLY STATUS_CLASS = CONSISTENT"}`. At
`c06ce377` (clone1) it prints REFUSE, exit 1, with `not fresh []`, `class failures {}`, committed status report FRESH, and one contradiction: the inventory's
unexpected `evidence/qualification/C11R_QUALIFICATION.json`. My recomputation of the pre-result conditions on the primary (read-only) and on clone1: exactly
`no_qualification_artifact`, `no_qualification_in_any_commit`, `no_protocol_directory_in_any_commit` are false, every other condition true; in qclone all true.
So the author's description is accurate.

Judgement: CORRECT BY DESIGN for the qualification; a WORDING/SCOPE defect in the prose; not a defect that matters for Phase 12 or Phase 13.
- The status verifier's pre-result block and its inventory (expected = `PRE_RESULT_ARTIFACTS` + quarantine) define the FROZEN state; after the
  FROZEN -> QUALIFIED transition it can only REFUSE, forever. Q11 runs it BEFORE the artifact is written (code order: `status_verify_only()` at line 334, write at
  359), the only moment it can be CONSISTENT -- and that is also why a re-run of the qualifier on a qualified tree fails (Q11, Q17).
- Nothing after Phase 12 consumes it: no code in `c11r_contract` (authorization facts, lifecycle, pre-flight), `c11r_runs`, `c11r_compare` or the policy calls
  the status verifier or reads STATUS_CLASS; G13 is not a REQUIRED_PREDICATE; `_authorization_facts(A, stage="authorize")` on an exact clone returns no
  problem. Freshness cannot silently drift afterwards either: every artifact and code file it checks is a frozen path re-verified byte-for-byte against A
  (tree identity + history purity) at every later boundary.
- Wording (class (c), N-1): G13's prose ("c11r_status reports STATUS_CLASS = CONSISTENT") carries no scope although it is satisfiable only in the FROZEN state
  (it should read "at Phase 12, Q11, before the qualification is written"); the status module docstring's item 5 lists runs/authorization/comparison but not the
  qualification it actually requires absent, and item 4 does not say the inventory excludes the qualification.
- Robustness (class (d), N-1): after Phase 12 there is no tool that reports the status verifier's freshness/contradiction/review-preservation findings as
  CONSISTENT; a genuine post-qualification inconsistency would be indistinguishable in its verdict line from the expected one (the detailed lines still show it).
  A Phase 13 operator who treats G13 as a standing gate predicate would see it permanently false; the Phase 13 instructions should state that G13 was
  discharged by Q11.

## Q1-Q18 as I recomputed them (harness_d.py at 5890511b, i.e. the state the qualifier saw; qualifier `main()` never run)

| Item | Record | My recomputation | Result |
|---|---|---|---|
| Q1 contract+gate verify from bytes | PASS, problems [] | `chain_roots` problems [] (also now, at HEAD) | equal |
| Q2 frozen paths, tree + history | PASS, 44 paths, 1 commit | `frozen_state(A)` detail dict EQUAL (ancestry/tree/history [], 44, 1, method text, 0 replace refs) | equal |
| Q3 configuration re-derived | PASS, {5,32}=={5,32} | `rederive_configuration` detail EQUAL | equal |
| Q4 certifiers + loaded modules | PASS | contract/tree/reviewed-idrift hashes EQUAL; required set EQUAL (14); approved sources 27; shadows []; L0 [] in a launch-policy process; same 14 checked names (mine has `c11r_qualify` where the record has `__main__`) | consistent |
| Q5 import scan | PASS, 27 modules, no hits | EQUAL | equal |
| Q6 backend absent | PASS | `toolchain_present` EQUAL (all six false) | equal |
| Q7 VALIDATION_CLASS | PASS, failed [] | frozen artifact PASS, failed [] | equal |
| Q8 MUTATION_CLASS | PASS | frozen artifact PASS | equal |
| Q9 FIREWALL_CLASS | PASS (detail {}) | frozen artifact PASS | equal |
| Q10 LEAK_CLASS | PASS (detail {}) | frozen artifact PASS | equal |
| Q11 status verifier run now | PASS, exit 0, CONSISTENT | reproduced in qclone: exit 0, CONSISTENT (see adjudication) | equal |
| Q12 equivalence self-test | PASS (detail {}) | frozen artifact EQUIV_CLASS READY, self_test.PASS true | equal |
| Q13 scalar collapse at 5/2 | PASS, 4 probes bit-equal | `scalar_collapse_nt()` detail EQUAL | equal |
| Q14 K_e = Khat_e + atom on NT | PASS, separation <= 0 | `atom_decomposition_nt()` detail EQUAL (float bit-identical) | equal |
| Q15 chain controls | PASS, failed [] | frozen artifact CHAIN_CLASS PASS, failed [], 204 controls | equal |
| Q16 host = cost host | PASS, match | `host_matches(cost.host, host_identity())` EQUAL | equal |
| Q17 guard prerequisites | PASS, DENY, none present, FROZEN, workers [] | at 5890511b: DENY, no auth/permission/runs, FROZEN, workers [] now | equal |
| Q18 disk space | PASS, 215.5 GB | 180+ GB free now (> 2 GiB threshold) | consistent |

Q7-Q10, Q12, Q15 read the stored classes of frozen artifacts; those artifacts are frozen paths (verified), and the status verifier at 5890511b reported all 15
pre-result artifacts FRESH (producer, closure and inputs equal the tree), so the stored classes are the outputs of the frozen producers. Q12's canonical name
("the equivalence comparator's self-test passes") reads as if the self-test were executed; it reads the recorded result (class (c), N-8).

## Load-bearing BLOCKERS

None. I found no class-(a) defect in the qualification or its evidence: the record is complete (Q1-Q18, once each, canonical names, all PASS), correctly
bound to the approved commit ee1a6a8a and to the contract, gate, policy, statement table and qualifier as committed at A, produced on this host by A's
qualifier code, byte-identical to what `write_evidence` writes, introduced by exactly one commit that adds nothing else, and every recomputable fact behind
its items reproduces exactly at the pre-qualification state. No authorization, permission, runs or comparison exists anywhere; guard DENY; lifecycle
QUALIFIED; no target computation or value; main, r5, R1-R8, predecessors and every frozen path untouched.

## Non-blocking observations

- **N-1 (c) + (d). G13 / status-verifier scope.** Correct by design (see adjudication); G13's prose and the status docstring (items 4-5) omit that the
  verifier is a FROZEN-state check that REFUSEs permanently after Phase 12; afterwards no tool reports its findings as CONSISTENT. State in the Phase 13
  instructions that G13 was discharged by Q11 at Phase 12.
- **N-2 (b). `verify_qualification` checks less of the record than the record carries.** It does not check `provenance.code_closure`, `provenance.inputs`,
  the provenance producer PATH, the recorded `chain_root_problems`, the self-declared `computes_on_open_cells` / `produces_target_constants`, the HEAD the
  record was produced at, or detail/status coherence (a forged record varying any of these, re-sealed, is accepted: harness_b 04h, 11c-11e, 12g, 12h).
  Consistent with `QUALIFICATION_PROVES` (attestation); for THIS record I verified every one of them by hand (all equal A / empty / false / coherent).
- **N-3 (b). Qualification uniqueness is enforced only in HEAD's history after A.** A different qualification on a sibling branch, in a reflog entry, or a
  second introduction elsewhere is not refused at stage authorize (S7, S7b, S7c); `_protocol_elsewhere` covers runs, permission, comparison and authorization
  but not the qualification. Verified directly for this repository: exactly one of 729 commits holds any qualification file; one qualification blob exists.
- **N-4 (b). A forged ACCEPTED cache of an inventory stem runs on the supported path before detection** (known since R8 item 3, re-measured with sentinels):
  the barrier admits `__pycache__` wholesale and S accepts inventory-named caches; `_pyc_matches_source` detects it only post-load. The primary's accepted
  caches are all genuine and predate the run. A cheap hardening would be for the barrier to refuse any `__pycache__` entry (the launch policy already uses `-B`).
- **N-5 (d).** The chain does not enforce that the qualification commit contains nothing else (S4). Verified by hand for c06ce377.
- **N-6 (d).** The launcher's file mode is not bound by the contract or checked by the authorization path (S23; only the pre-result status checks it).
  No effect on what runs; mode is 100755 at A, HEAD and on disk.
- **N-7 (c) / (b).** The launcher docstring ("a direct start is refused by the program's barrier") and `LAUNCH_POLICY.not_covered` ("a boundary program started
  some other way is refused by its barrier") hold only for non-compliant starts: a direct start with exactly the launch policy, or a policy-compliant `-c`
  wrapper that runs arbitrary code first and then `runpy`s the program, passes the barrier, L0 and Q4. The record attests the interpreter policy, not the launcher.
- **N-8 (c).** Q12's name ("... self-test passes") suggests execution; Q7-Q10, Q12, Q15 read the recorded classes of frozen artifacts (which are fresh).
- **N-9 (b), stated.** DYLD_INSERT_LIBRARIES native code executes in the launcher process before its refusal (the frozen binary permits DYLD variables and
  disables library validation); the interpreter binary and stdlib are writable by the admin group on this host. Both are the stated host-trust class.
- **N-10 (d).** `verify_qualification` accepts a moving/abbreviated ref when the caller passes the same ref; every production caller checks
  `approved_commit_problems` and `frozen_state` first (S15), so no path is open.
- **N-11 (d).** `/usr/bin/python3 -I -S c11r_launch.py ...` crashes with AttributeError (`sys.flags.safe_path`) instead of a typed REFUSE; nothing is exec'd.
- **N-12 (b/d), carried from R8.** O-1 (`core.fsmonitor` via `$HOME/.gitconfig` runs in `git status` / `ls-files`): the operator's effective git configuration
  has no such hook (checked). O-2 (`__PYVENV_LAUNCHER__` is inert, not refused): unchanged.
- **N-13 (c), trivial.** The commit message says the launcher digest is "not a qualification field"; it is recorded in `provenance.code_closure`
  (`c11r_launch.py` 839faeae...) as well as bound by the contract.
- **N-14 (d), next-phase robustness.** The record binds `host.node` = `suzhedeMacBook.local`; `scutil --get HostName` is "not set", so the kernel host name is
  dynamic (DHCP / Bonjour conflict renaming can change it). If it changes before Phase 13, `verify_qualification` refuses ("environment is not this host")
  and the protocol offers no re-qualification under A (a replaced qualification is refused). Check `uname -n` before Phase 13; do not "fix" it by editing the record.

## Final state of the primary checkout after this review

HEAD `c06ce3774d3cc100fd16dfbd2d1c49c29e7d1021`; `git status --porcelain --untracked-files=all` empty; campaign `__pycache__` listings unchanged;
no file added, modified or deleted; nothing committed, pushed or fetched; main untouched; no background process left running.

VERDICT: QUALIFICATION_ACCEPTED
