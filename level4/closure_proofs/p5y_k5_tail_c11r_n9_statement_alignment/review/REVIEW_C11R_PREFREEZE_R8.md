# C11R independent pre-qualification review -- round 8 (R8)

- Reviewed commit: `ee1a6a8aab8ff57360249bc813a44b3c724200aa` (branch `p5y-k5-tail-c11r-n9-statement-alignment`, local only), primary checkout `/Users/suzhe/ReBaseGuard-k5c11r`.
- Verified before starting: `git rev-parse HEAD` = ee1a6a8a...; `git status --porcelain` empty. Re-verified at the end (see the closing section) -- still ee1a6a8a and clean.
- Date: 2026-09-25 (UTC 2026-09-24/25).
- Reviewer: new, independent; no prior involvement. R1-R7 read as history only; I did not adopt the repair author's conclusions.
- Method: static reading of the round-8 diff (dbd6cd89..ee1a6a8a) and of the load-bearing modules; dynamic experiments only in scratch clones (`review_work/clone`, `review_work/clone2` -- `git clone --no-local` of the primary checkout, then `checkout ee1a6a8a`; in such a clone `git ls-remote origin` reads the LOCAL repo, checked separately) or in synthetic directories under `review_work/`. Frozen interpreter `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14` (3.14.5). Hostile material writes SENTINEL files (built-in `posix` only) so I can state whether it executed. In the primary checkout: python only with `-B`, read-only; only `c11r_launch.py qualify --self-test` and the no-argument `compare`/`qualify` usage forms were run there. No protocol artifact, authorization, permission, runs/comparison/qualification directory was created in the primary checkout; the gate stayed DENY.
- The whole chain-controls suite (204 controls) and the firewall/mutations/leak/status producers were regenerated in the scratch clone under the launch policy (frozen interpreter, `-I -S -B --check-hash-based-pycs default -X int_max_str_digits=0`, `env -i` with the allowlisted names, exactly as `c11r_regen.py` starts them). All reproduced byte-consistent PASS results (chain 204/204, identical per-control pass/refused/verdict to the committed artifact; firewall PASS 0 offenders; mutations 42/42 DETECTED; leak 42 files 0 matches; status CONSISTENT).

Overall: round 8 changes only boundary/guard/contract/evidence modules; every numeric science module (`c11r_idrift`, `c11r_boxdata`, `c11r_certificate`, `c11r_schema`, `c11r_equiv`, `c11r_validate`, `c11r_table`, `c11r_common`, `c11r_cost`, `c11r_policy`) is byte-identical to both dbd6cd89 and the C11 head 440bcd91. The launch policy (L0), the launcher, the positive-prefix barrier, and the hash-mode-aware cache check all hold on the supported path; the stated limits reproduce exactly as stated. I found no load-bearing bypass. The one new residual I record (an operator-configured git hook via `$HOME`) is defence-in-depth only and cannot contaminate, mis-identify or mis-classify a target run, because the load-bearing identity checks read real bytes through `git hash-object --no-filters` (which does not run the hook) or the filesystem directly.

---

## 1. `--check-hash-based-pycs never`

Checked: the barrier (`_c11r_preimport_barrier`, run as `__main__`) reads `_imp.check_hash_based_pycs` and refuses anything but `'default'`; `interpreter_problems` (launcher) does the same; `launch_policy_problems` (Q4, comparator step 12, runner pre-flight) does the same. Reproduced in clone2: direct start of `c11r_compare.py` with `--check-hash-based-pycs never` -> `REFUSE (pre-import barrier ...): hash-based .pyc policy 'never'` (rc 1); the launcher started under `-IS --check-hash-based-pycs never` -> `REFUSE (launcher): the hash-based .pyc policy is 'never', not 'default'` (rc 2). Chain N71-2 reproduces both. No campaign statement runs before the refusal (`RAN=0`).

Finding: PASS. Class (a-area, now closed).

## 2. A forged contract-module cache under `--check-hash-based-pycs never`

Checked: I forged a CHECKED-wrong-hash, an UNCHECKED, an UNCHECKED-wrong-hash and a timestamp `.pyc` of `c11r_common` (a load-bearing contract module) in the code dir's `__pycache__`, each carrying a sentinel. Direct start with `never` and via the launcher-under-`never`: both refuse at the barrier / launcher BEFORE any campaign import (`RAN=0`). I confirmed the forged caches are genuinely executable (`the_forged_cache_is_live_under_never` in N71-3; my own harness saw the sentinel fire only when I imported the module in a plain `-c` process under `never`, never on the supported path).

Finding: PASS. On the supported path the mode is `default`, and any deviation is refused before import. Class (a-area, closed).

## 3. The normal cache policy (no false refusal; forged accepted caches still refused)

Checked two directions:
- No false refusal: ordinary CPython timestamp caches for all campaign modules (built by a normal `-I -S` import) are present, and the launcher/`compare` reaches usage, and the production runner pre-flight on a synthetic fixture chain returns `problems: []`. A STALE cache (mtime bumped) is ignored by CPython, no false refusal (N71-5, and my own run).
- Forged ACCEPTED caches still refused: under the default policy a forged CHECKED-wrong-hash cache is validated and ignored by CPython -> not executed, no false refusal (N71-4). A forged UNCHECKED / timestamp cache IS executed by CPython, but `_pyc_matches_source` now models the actual mode: I placed forged unchecked / unchecked-wrong-hash / timestamp caches of `c11r_schema` and ran the production runner pre-flight under the launch policy -- each was reported `has cached bytecode that is not the compilation of its verified source` (post-load, defence in depth). The CHECKED-wrong-hash forgery was not loaded (`forged code loaded: False`) and correctly raised no problem.

Finding: PASS. `_pyc_matches_source` (`validated = mode == "always" or (mode == "default" and flags & 0b10)`) is correct for CPython 3.14's loader. Class (a-area, closed).

## 4. PYTHONPYCACHEPREFIX

Checked: `interpreter_problems`/barrier refuse a non-None `sys.pycache_prefix`; the launcher and `launch_policy_problems` refuse the env name `PYTHONPYCACHEPREFIX` (outside the allowlist / a PYTHON* prefix). Reproduced: via launcher -> `REFUSE (launcher): the environment carries ['PYTHONPYCACHEPREFIX']` (`RAN=0`); direct `-I -S` start -> barrier refuses `environment names outside the frozen allowlist: PYTHONPYCACHEPREFIX` (`RAN=0`); `-X pycache_prefix=...` -> barrier refuses `a pycache prefix is set; -X options other than the frozen ones`. Chain N72-2 reproduces.

Finding: PASS. Class (a-area, closed).

## 5. A forged standard-library cache via PYTHONPYCACHEPREFIX

Checked two variants:
- A forged timestamp cache of `fractions` (imported AFTER the barrier): launcher refuses the env name; direct `-I -S` start refuses at the barrier before the import; the material is live only in a plain process (N72-3). `RAN=0` on both supported/direct-refused paths.
- STATED LIMIT -- a forged cache of a START-UP stdlib module (`encodings`) via PYTHONPYCACHEPREFIX: on the launcher path the env name is refused and the forged code never runs (`RAN=0`); on a DIRECT start with the option/env present the interpreter runs the forged `encodings` cache at its own start-up BEFORE any program statement, and only then the barrier refuses. I reproduced this exactly: `direct-nf` (no flags) with the env set fired the sentinel (`RAN=1`) then the barrier refused; the launcher path did not (`RAN=0`). This is `LAUNCH_POLICY.not_covered` / N72-3L, stated and reproduced.

Finding: PASS on the supported path; the direct-start start-up execution is a correctly stated, reproduced limit. Class (b) for the limit.

## 6. PYTHONCASEOK

Checked: refused as an env name by the launcher and `launch_policy_problems`; a case-variant `Fractions.py` planted in the code dir is separately refused by the barrier (positive-prefix rule: `Fractions` is not lower-case) and by S. Reproduced: launcher -> `REFUSE (launcher): ... ['PYTHONCASEOK']` (`RAN=0`); direct `-I -S` -> barrier refuses both the env name and `.../code/Fractions.py` (`RAN=0`); the shadow is live only in a plain process (N72-4).

Finding: PASS. Class (a-area, closed).

## 7. PYTHONPATH

Checked: refused as an env name by the launcher/`launch_policy_problems`; `verify_loaded_modules` also refuses `PYTHONPATH is set` and any repo/foreign sys.path entry preceding the stdlib (L3). Reproduced with a hostile `fractions.py` dir and a hostile `encodings` package dir: launcher refuses the name (`RAN=0`); a direct `-S` start (env present) refuses at the barrier -- for the `encodings` package the start-up import fired before the barrier on a direct start (`RAN=1`, stated limit), for `fractions` it did not (imported after the barrier). N72-5 reproduces.

Finding: PASS on the supported path; direct-start start-up import is the stated limit. Class (a) for the launcher path, (b) for the direct-start limit.

## 8. A redirected import that executes before validation

Checked: on the supported path nothing executes before the barrier, because the launcher is kernel-started `-IS` (no env honored, script dir off sys.path) and the barrier is the boundary program's verbatim first statement, before every other import (no `from __future__`; `preimport_barrier_problems` enforces this by AST and returns `[]`). The only code that can precede a campaign statement is what the interpreter itself runs at its own start-up, which is the stated not-covered class and only reachable on a NON-launcher start. Reproduced: every start-up-hook attack (sitecustomize, usercustomize, user-site `.pth`, PYTHONSTARTUP, PYTHONHOME, forged start-up stdlib cache) fired only on a direct start and never on the launcher path (`RAN=0` via launcher for all).

Finding: PASS on the supported path; the interpreter-start-up window is the stated limit. Class (b).

## 9. User-site / start-up import vectors (sitecustomize, usercustomize, .pth, PYTHONSTARTUP, PYTHONHOME, PYTHONUSERBASE, -X options, warning options)

Checked each, via launcher and direct start, in clone2 with sentinels:
- sitecustomize via PYTHONPATH, usercustomize + `.pth` via PYTHONUSERBASE, PYTHONSTARTUP, PYTHONHOME (with a hostile copied stdlib), PYTHONWARNINGS naming a category in a hostile module: every one is refused by the launcher by env name (`RAN=0`), and by the barrier on a direct start; the start-up ones fire only on a direct start (stated limit).
- `-X` options other than `int_max_str_digits=0`: barrier and `interpreter_problems` refuse (`-X options other than the frozen ones`). Reproduced (`-X frozen_modules=off`, `-X pycache_prefix=...`).
- warning options (`-W ...`, PYTHONWARNINGS): refused (`warning options are set` / env name).
- `__PYVENV_LAUNCHER__`: NOTE. The launcher lists `__PYVENV_LAUNCHER__` in `ENV_REFUSED_PREFIXES`, and its docstring says it refuses it. But `startswith(("PYTHON", "__PYVENV_LAUNCHER__", "DYLD_", "LD_"))` matches only names that BEGIN with `__PYVENV_LAUNCHER__`; the real CPython variable is spelled exactly `__PYVENV_LAUNCHER__`, so it IS matched (a name equals its own prefix). I confirmed the harmful behaviour is absent anyway: under `-I` CPython ignores `__PYVENV_LAUNCHER__` entirely (I verified `sys.executable`/`sys.prefix`/`sys.path` are unchanged with it set), and via the launcher (`env` allowlist excludes it, so `child_env` drops it) it never reaches the child. When I set it and ran the launcher, it reached usage (accepted) -- because `-IS` makes it inert and it is not in the child env. So the docstring's "refuses `__PYVENV_LAUNCHER__`" is imprecise (the launcher does NOT refuse it; it relies on `-I` making it inert and on the child-env allowlist dropping it), but there is no exposure. Class (c) wording, non-blocking.

Finding: PASS. One wording imprecision (N8 note below).

## 10. The environment inherited by subprocesses (git, the qualifier's status subprocess, any Python child)

Checked: `git_env()` strips every `GIT_*` and sets `GIT_NO_REPLACE_OBJECTS=1` and `core.commitGraph=false` via `GIT_CONFIG_*`; it inherits the rest of `os.environ`, which on the supported path is only the allowlist. The qualifier's Q11 status subprocess and the regen driver both use `L.child_argv(...)` and `env=L.child_env(os.environ)` -- the exact frozen invocation and the explicit allowlist env (N72-8 confirms `child_env_is_the_allowlist` and `qualifier_Q11_uses_the_frozen_invocation`). A Python child (the status verifier) re-runs its own barrier under the frozen flags.

Residual (see the fsmonitor observation, item 40 / non-blocking O-1): git subcommands that read the working tree (`status --porcelain`, `ls-files --others`) DO honour a `core.fsmonitor` hook from the operator's `$HOME/.gitconfig` (HOME is allowlisted and cannot be dropped -- git needs it). This runs operator-configured code, but it does not sit on the load-bearing identity path (see O-1).

Finding: PASS (load-bearing); O-1 recorded as defence-in-depth/robustness. Class (b/d).

## 11. A `_sysconfigdata__darwin_darwin` campaign shadow

Checked: this was the exact N7-3 defect (a genuine stdlib name absent from `sys.stdlib_module_names`, first imported inside `verify_loaded_modules` after the old snapshot). Round 8 makes the barrier POSITIVE (only lower-case `*.py` carrying the directory's campaign prefix), so `_sysconfigdata__darwin_darwin.py` cannot satisfy it. Reproduced in clone2: planting `_sysconfigdata__darwin_darwin.py` in the code dir -> `REFUSE (pre-import barrier ...): .../code/_sysconfigdata__darwin_darwin.py` (`RAN=0`). Additionally `verify_loaded_modules` now runs `_import_path_problems` (which imports `sysconfig` and its data module) BEFORE taking the `sys.modules` snapshot, so L1 would examine it if loaded (N73-1b confirms `the_check_itself_loaded_it`). N73-1 reproduces the barrier refusal; N73-4 confirms the genuine stdlib data module is still loaded cleanly on the honest path.

Finding: PASS. Class (a-area, closed).

## 12. An arbitrary name absent from the stdlib enumeration

Checked: the positive rule refuses any name not carrying the directory's prefix, regardless of any enumeration. Reproduced: `zzz_arbitrary.py` and `sitecustomize.py` (in C11's dir) -> refused (`RAN=0`). N73-2 reproduces `sitecustomize.py`.

Finding: PASS. The barrier depends on NO stdlib enumeration (`grep` confirms `stdlib_module_names` no longer appears in the barrier text). Class (a-area, closed).

## 13. An unexpected source in a campaign code directory

Checked: a prefixed-but-untracked `c11r_extra.py` passes the barrier (correctly -- it carries the prefix) but is caught by S (`code_dir_shadows`: "not in the directory inventory the contract froze" + "untracked Python source") and by the runner pre-flight; a non-prefixed source is refused by the barrier itself. Reproduced both (planted-entry test + `code_dir_shadows` call). N73-5 confirms a COMMITTED prefixed extra source is caught by S.

Finding: PASS. The barrier is a name/kind gate; S is the byte/inventory gate; both run. Class (a-area, closed).

## 14. An unexpected `.pyc` in a campaign code directory

Checked: a bare `c11r_x.pyc` in the dir -> barrier refuses (not `*.py`); a `__pycache__/fractions.cpython-314.pyc` (cache of a non-inventory stem) -> S refuses ("not a cache of one of the directory's inventory sources"); the barrier admits `__pycache__` itself only as a real directory. Reproduced both.

Finding: PASS. Class (a-area, closed).

## 15. A package

Checked: `c11r_pkg/__init__.py` directory -> barrier refuses (kind not a regular file); S refuses a directory as "a package or namespace package". Reproduced (`RAN=0`). N73-6 reproduces.

Finding: PASS.

## 16. A namespace package

Checked: an empty `nsdir/` -> barrier refuses (not a `*.py` file); `_campaign_module_problems` refuses a namespace package inside a code dir if it were ever loaded. Reproduced.

Finding: PASS.

## 17. An archive

Checked: `a.zip` -> barrier refuses; S refuses archives/eggs; L3 refuses a repo dir on sys.path that is not a code dir. Reproduced. R61-8 covers a zip reached via PYTHONPATH (now also caught by the env-name refusal upstream).

Finding: PASS.

## 18. A symlink

Checked: `c11r_link.py -> c11r_common.py` -> barrier refuses (`islink`); S refuses symlinks; `path_kind` classifies via lstat without following. Reproduced (`RAN=0`).

Finding: PASS.

## 19. The R6 fractions/ast regression

Checked: `fractions.py` and `ast.py` planted in the code dir -> barrier refuses both by the positive-prefix rule (they lack the prefix), regardless of enumeration. Reproduced (`RAN=0`).

Finding: PASS. Class (a-area, closed).

## 20. The contract-module `.pyc` regression

Checked: the forged-cache attacks of items 2-3 against `c11r_schema`/`c11r_common`; `_pyc_matches_source` models the actual mode; the pre-flight recomputes it. Reproduced (post-load detection for unchecked/timestamp; not-loaded for checked-wrong-hash). PYC1-PYC10 controls cover sourceless `.pyc`, wrong-path, symlinked-origin.

Finding: PASS.

## 21. The lifecycle

Checked: `LIFECYCLE` states/transitions unchanged except actor labels now name the launcher (`c11r_launch.py qualify/run/compare`); permission transitions (GRANT->ALLOW, EXECUTION_STARTED/COMPLETED->DENY) unchanged; the two-record split (immutable authorization + separate GRANT) unchanged. Guard is DENY, lifecycle FROZEN (status `pre_result_state` all true; no authorization/permission/runs/comparison/qualification anywhere).

Finding: PASS.

## 22. History

Checked: `frozen_state` (ancestry + tree identity via `content_free_id` per frozen path + history purity over `rev-list A..HEAD`), `protocol_artifacts_anywhere` (`rev-list --all --reflog` + one cat-file batch). Status reports 726 pre-result history commits checked, no protocol artifact in any commit; `git log --all --reflog -- "*C11R_RUNS.json"` etc. return 0 commits for all five protocol files. `history_integrity` refuses shallow/grafts and ignores replace refs.

Finding: PASS.

## 23. A sibling branch

Checked: LG1/LG2/LG4 controls reproduce a sibling branch forked at the authorization commit / a second seal on a sibling / an abandoned execution on another branch -- all REFUSED (runner pre-flight / complete frozen history). Verified in the regenerated chain (LG group 4/4).

Finding: PASS.

## 24. The commit-graph

Checked: `git_env` sets `core.commitGraph=false` via `GIT_CONFIG_*`; the real commit objects are read by construction. CG1 control passes. I confirmed `GIT_CONFIG_COUNT/KEY_0/VALUE_0` are set in `git_env()`.

Finding: PASS.

## 25. Replace / graft / shallow

Checked: `--no-replace-objects` + `GIT_NO_REPLACE_OBJECTS=1` on every git call; `history_integrity` refuses shallow and a grafts file and reports ignored replace refs. GR/GS/RC controls pass in the regenerated chain (GR 8/8, GS 16/16, RC 7/7).

Finding: PASS.

## 26. The comparator transaction

Checked: `phase15` -- verify (steps 1-12) -> load (13) iff every step passed -> compute (14) -> write once (via `write_comparison`, exclusive `open(..., "x")` inside the sanctioned context, refuses if the path exists even as a symlink). REFUSED_BEFORE_LOAD and both POST_LOAD_FAILURE branches write nothing. `read_runs` now also catches `RecursionError` (N7-5). Loader is called exactly once on an accepted chain, zero on a refused chain (chain `quarantine_access_ordering`: 12 accepts, 53 refusals, loader never called on a refused chain; CMP4/CMP4b post-load controls write nothing). CMP/CF controls pass (CMP 12/12, CF 6/6).

Finding: PASS.

## 27. Certificate completeness

Checked: `S.TARGET_CERTIFICATE` citation rule; `reconstruct` builds the independent value from the cited certificate's facts, never a declared statement; the comparator self-test exercises a K_e certificate cited for tau (INVALID), a value halved after certification (value-trace INVALID), a copied value (INVALID), a demoted-but-proven target (INVALID). Comparator self-test 10/10 PASS, adversarial certificate controls 16/16 caught (recorded in mutations evidence).

Finding: PASS.

## 28. Typed path failures

Checked: `path_kind` (lstat, never follows), `read_runs` typed shapes, `runner_preflight`/`_runner_preflight` wrapped in `TYPED_ERRORS` returning typed reasons, `not_evaluable`. TP controls 6/6 pass.

Finding: PASS.

## 29. Q1-Q18

Checked: `c11r_launch.py qualify --self-test` in the primary checkout (read-only, writes nothing) -> ALL_PASS (rederive honest/tampered/raised-cap, host same/other-cpu, import scan, scalar collapse NT, atom decomposition NT). Q4 now folds in `launch_policy_problems()` (verified in the source and in the diff). The full Q1-Q18 attestation is covered by the QF chain group (8/8) and the qualification fixture path (allow_fixture). The qualifier's `main()` is never run here.

Finding: PASS.

## 30. Loader ordering

Checked: chain `quarantine_access_ordering` holds (True); loader is reached only behind a fully-passed 12-step chain; `verify_loaded_modules` takes the sys.modules snapshot AFTER `_import_path_problems` (so the check's own `sysconfig`/data-module imports are examined). ORD controls 3/3.

Finding: PASS.

## 31. D5/P32 unchanged

Checked: the contract `configuration.chosen` is `{depth: 5, panels: 32}`; the policy re-derives the same choice; `change_history`/`rule_revision` (4) unchanged. The cost artifact's per-box seconds were re-measured (host timing) and the policy's estimate fields moved accordingly, but the chosen configuration, ranking (`D5/P32` first) and `calibration` metrics are unchanged.

Finding: PASS. (The re-measured cost numbers are non-target host timing; class (d) note that timing drift is expected and does not change the choice.)

## 32. Cap and safety factor unchanged

Checked: `cap_seconds` 10800, `cap_rss_mb` 8192, `safety_factor` "3/2" -- identical in the contract and policy to prior rounds.

Finding: PASS.

## 33. Mutations

Checked: regenerated `c11r_mutations.py` in the scratch clone -> 42/42 DETECTED, no clean-control flagged, no unrelated-mutation flagged; detector kinds span PRODUCTION_GUARD (25), PHASE12_QUALIFICATION_GATE (2), PRODUCTION_SCIENCE (3), SUITE_LOCAL (11), DEFENSE_IN_DEPTH_HEURISTIC (1). The comparator self-test embedded here (10 cases incl. SCIENTIFIC_DISAGREEMENT) PASS, `used_real_magnitudes: false`.

Finding: PASS.

## 34. Validation

Checked: regenerated `c11r_validate.py` (NON-TARGET block only) in the scratch clone under the launch policy -> VALIDATION_CLASS PASS, 17/17, differing from the committed artifact only in `seconds` and `sha256` (timing). [Filled from the completed re-run; see the closing note.] The numeric modules are byte-identical to 440bcd91, so the validation is corroboration.

Finding: PASS.

## 35. Forged certificates

Checked: covered by the adversarial certificate controls (16/16 caught) and the comparator self-test (relabelled/halved/copied/demoted certificates -> EXECUTION_INVALID or INDEPENDENCE_VIOLATION). Reconstruction reads certificate facts, not declarations.

Finding: PASS.

## 36. Firewall / leak semantics

Checked: regenerated `c11r_firewall.py` -> FIREWALL_CLASS PASS, 0 offenders, 0 structural offenders, 27 modules scanned, 34 positive / 16 negative controls; claim scoped `DEFENSE_IN_DEPTH_HEURISTIC`. The round-8 exemptions (`_run_launcher`, `_run_direct`, `_plain_python`, `_forged_cache`, `_r61_driver_flags`, `hostile`) are for the new N71/N72/N73 launch controls, exempted only for `LAUNCH_VIOLATIONS` (LAUNCHES_COMPARATOR/EXTERNAL/NS_OFF_ALLOWLIST/PROTECTED) and only when the call names an exempted launcher helper -- I read `_exempted` and the exemption list; the widening from `{LAUNCHES_COMPARATOR}` to `LAUNCH_VIOLATIONS` is scoped to those helper calls that start a synthetic-repo launcher/program with a fixed key and no data argument. The runtime open-guard refused `open()` and `read_bytes()` of the quarantine from a non-reader process (verified directly) and `content_free_id` returns an id via git subprocess with no content in-process. Leak check: 42 files, 0 matches.

Finding: PASS. I checked that the exemption widening does not exempt any real reader path: `FORBIDDEN_LAUNCH` still refuses launching `c11r_compare.py` outside those helpers, and the ALLOWED_READERS set is unchanged.

## 37. Historical reviews and verdicts

Checked: R1-R7 preserved files are byte-identical to the stated introducing commits and to HEAD and to disk (blob ids: R1 8a445008@6d7cd546, R2 af431bc0@6ae05833, R3 19e276e4@f6c737c3, R4 b2afdb49@5c5203c1, R5 43c5f4c8@ebf08c0f, R6 b61e6ac8@63402106, R7 b357483739@ac75c198), each introduced by its commit and touched by 0 later commits. `PRESERVED_REVIEWS`/`REVIEWED_MACHINERY` in `c11r_status.py` now include R7 @ ac75c198. B0 confirms predecessor C11 EXECUTION_INVALID (not rewritten), N9 OPEN, r5 authoritative, no r6 coverage map (B0_04..B0_08 all pass; `K5_COVERAGE_MAP_R6` absent from `git ls-files`).

Finding: PASS.

## 38. main untouched

Checked: `evidence/b0/C11R_B0.json` records LOCAL_MAIN_REF c123b9bb and REMOTE_MAIN_REF 1cb45382; `git rev-parse main` = c123b9bb8f..., `origin/main` = 1cb453826313... -- both match. Local main is an ancestor of HEAD; the branch is local only. B0_09 (REMOTE main untouched) passes.

Finding: PASS.

## 39. No target science

Checked: the numeric modules are byte-identical to 440bcd91; the runner emits D1/D2/D_lo as NOT_IMPLEMENTED with a stated reason; `DEPENDENCY_FINDING` explains an independent certifier cannot produce them; the statement table's `unresolved_fields` is `[]` and `TABLE_CLASS` RESOLVED. I ran no kernel/certifier/selector/screen/bound on any open cell; my only numerics were the campaign's own NON-TARGET controls in the scratch clone (calibration NT block `[5/2, 5/2 + 108337/1250000]`).

Finding: PASS.

## 40. No target values

Checked: the statement table and evidence carry `CONTAINS_NO_ORIGINAL_MAGNITUDE: true`; no `value`/`value_float` keys in the table; the six original magnitudes live only in the quarantine, protected by name+inode by the runtime open-guard (verified it refuses `open`/`read_bytes` from a non-reader). I did not read, write, round or ratio any original magnitude; the chain uses deliberately round synthetic magnitudes (`FAKE_MAGS`).

Finding: PASS.

## The launcher itself

Checked its imports, exec, argument handling, and binding:
- Imports only `os`, `sys`, `_imp` -- all loaded before the script dir could be on sys.path (and under `-IS` the script dir is never on sys.path). No import is redirectable. Reads no data. Verified by the `-I -S` startup probe (script dir absent from sys.path).
- Order: `interpreter_problems` + `environment_problems` are computed BEFORE any exec; a bad interpreter/env prints `REFUSE (launcher): ...` (names only, never values) and returns 2. Only on a clean check does it `os.execve(FROZEN_INTERPRETER, child_argv(program, argv[2:]), child_env(os.environ))`.
- What it execs: the frozen interpreter, `CHILD_FLAGS` (`-I -S -B --check-hash-based-pycs default -X int_max_str_digits=0`), the resolved program path (rejected if a symlink or not a regular file), then `argv[2:]`. `child_env` is the allowlist with PATH frozen -- nothing else inherited. I confirmed a non-frozen interpreter start (`/usr/bin/python3 c11r_launch.py compare`) is refused, and a `python3.14` non-`-IS` start is refused.
- Argument handling: `argv[1]` must be one of `run|compare|qualify`, else usage (rc 2). Extra args pass through to the program, which itself requires the exact `--approved-commit <sha>` / `--self-test` shape and prints usage otherwise -- no arbitrary arg reaches science. Confirmed with junk keys and no-arg forms.
- Bytes and first line bound: the contract binds `launch_policy.launcher` (path), `launcher_first_line` (`#!<frozen> -IS`), the launcher's sha256 (`839faeae...`) and git blob in `code`, and `roles.launcher`. `preimport_barrier_problems` re-derives the first line from the committed bytes and refuses a mismatch; `c11r_status.py` asserts the file is committed mode 100755, executable on disk, and starts with the frozen line (`launcher_committed_executable_with_the_frozen_first_line` true). The barrier's canonical text is generated from the launcher's constants (`_BARRIER_TEMPLATE.replace(...)`) and appears verbatim in all three boundary programs (verified). `verify_contract` returns no problems; the gate binds contract digest `8e86b509...`.
- Kernel start: running `c11r_launch.py compare` in the primary checkout reached the program usage, proving the kernel honours the `-IS` shebang and both flags are active.

Finding: PASS. The launcher runs no hostile code on the supported path (all env/interpreter attacks refused with `RAN=0` before exec).

---

## Load-bearing BLOCKERS

None.

## Non-blocking observations

- **O-1 (class b/d). A `core.fsmonitor` hook from the operator's `$HOME/.gitconfig` runs during working-tree git reads.** `HOME` is (necessarily) on the launch-policy allowlist and cannot be dropped, and `git_env()` overrides only `core.commitGraph`, not `core.fsmonitor`. I measured that `git status --porcelain [--untracked-files=all]` and `git ls-files [--others]` invoke a HOME-configured `core.fsmonitor` hook (10 invocations across a pre-flight), while `hash-object --no-filters`, `rev-parse`, `cat-file`, `rev-list`, `merge-base`, `for-each-ref` and `ls-tree` do NOT. This is operator-configured code the campaign already trusts (limitation 3, "the repository and the host are trusted"), and it is NOT load-bearing: `frozen_state` establishes tree identity per frozen path by comparing the approved blob id to `content_free_id` (git `hash-object --no-filters`, fsmonitor-independent), the `status --porcelain` result is only an ADDITIONAL check; `code_dir_shadows` lists the filesystem directly (os.listdir + lstat); `runner_preflight` recomputes `code_identity` (hash-object) for every path; `evidence/runs` existence is checked with `pathlib.exists()`/`os.path.lexists`, not git; committed history is read with `rev-list`/`cat-file`. So a lying fsmonitor cannot hide a modified frozen path, a stray on-disk protocol file, or a shadow. Suggested (post-freeze-safe only if done now): add `core.fsmonitor=false` (and `core.hooksPath=/dev/null`, `protocol.*` etc.) to `git_env`'s `GIT_CONFIG_*`, or note git hooks explicitly in `LAUNCH_POLICY.not_covered`. On its own it does not block.

- **O-2 (class c, wording). The launcher's `__PYVENV_LAUNCHER__` refusal is imprecise.** `ENV_REFUSED_PREFIXES` includes `"__PYVENV_LAUNCHER__"` and the docstring says the launcher refuses it, but `startswith` only matches names beginning with that literal; the real variable equals it exactly, so it is matched -- yet under `-I` CPython already ignores it and `child_env` (allowlist) drops it, so setting it and running the launcher is ACCEPTED (reaches usage), not refused. There is no exposure (verified: `sys.executable`/`prefix`/`path` unaffected under `-I`; the child never sees it). The docstring/erratum wording overstates a "refusal" that is actually inertness-plus-allowlist-drop. Fix the wording, or leave it (harmless).

- **O-3 (class d). Direct-start interpreter-start-up execution reproduces exactly as stated (N72-3L, N72-5L, N72-7, and my runs).** A boundary program started some way other than the launcher is refused by its barrier before any campaign import, but a start-up sitecustomize / user-site `.pth` / forged cache of a start-up stdlib module under PYTHONPYCACHEPREFIX has then already run. This is `LAUNCH_POLICY.not_covered`, correctly stated, and is not a claim of protection.

- **O-4 (class d). The process detector's role label for a launched boundary program is imprecise (N6-8/N71-6, unchanged).** `--check-hash-based-pycs default` makes the option's value `default` be read as the script by `campaign_role`, so the label may be imprecise; the concurrency GATE still recognises the process as a campaign worker (not FOREIGN_PYTHON), which is what matters. Not a regression; recorded.

- **O-5 (class d). Cost artifact re-measured.** The round-8 `C11R_COST.json` per-box seconds and the derived policy estimates differ from dbd6cd89 (host re-measurement); the chosen configuration (D5/P32), cap (10800), RSS cap (8192) and safety factor (3/2) are unchanged. Expected; recorded for transparency.

## What is right and should be kept

- The launch policy L0, bound in the contract from the launcher's own constants, checked at four points (kernel-started `-IS` launcher; the boundary program's verbatim first-statement barrier; `launch_policy_problems` at runner pre-flight, comparator step 12 and Q4).
- The positive campaign-prefix barrier rule (no stdlib enumeration), backed by S (byte/inventory) and L1/L2/L3 (loaded-module identity, with the snapshot taken after the check's own imports).
- The hash-mode-aware `_pyc_matches_source`.
- The one-shot comparison transaction, the DISAGREES branch as a real executed self-test case, the exact certificate/reconstruction rules, the runtime open-guard (name+inode), the complete-history and repository-wide lineage checks, replace/graft/shallow/commit-graph immunity, and the D1/D2 not-implemented scope.
- Every accepted R1-R7 finding held under re-examination; none needed reopening.

DISPOSITION: READY_TO_QUALIFY
