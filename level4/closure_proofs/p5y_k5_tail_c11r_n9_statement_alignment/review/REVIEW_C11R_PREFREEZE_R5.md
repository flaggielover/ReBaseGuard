# C11R pre-freeze review, round 5 (independent)

- Reviewed commit: 5d89686ed7e4cd64d9c4a832b2c86ad938d52491 (branch p5y-k5-tail-c11r-n9-statement-alignment, worktree /Users/suzhe/ReBaseGuard-k5c11r)
- Date: 2026-09-24 (host clock at start: 2026-09-23 17:05 UTC)
- Reviewer: new independent reviewer (no involvement in C11R rounds 1-4; R1-R4 read as history only)
- Precondition: HEAD == 5d89686ed7e4cd64d9c4a832b2c86ad938d52491 and `git status --porcelain` empty -- VERIFIED at the start of the review.
- Numerics policy: no kernel, certifier, selector, screen or bound evaluated on any open-cell drift block; numerics only on NT = [5/2, 5/2 + 108337/1250000] or e = 5/2. No original cell-306 magnitude, rounded/truncated form or ratio to one appears here; the quarantine is referred to by path and field only.
- Writes: only in scratch clones under .../scratchpad/r5/work/ (git clone --no-local, checked out at 5d89686e) and in throwaway synthetic git repositories. The primary checkout was only read (python there only with -B, and only the permitted `c11r_qualify.py --self-test`).

(Written incrementally. Status: COMPLETE -- all 54 required attacks reached.)

## Method

- Read in full: `c11r_contract.py`, `c11r_compare.py`, `c11r_runs.py`, `c11r_qualify.py`, `c11r_procs.py`, `c11r_chain.py`, `c11r_common.py`, `c11r_status.py`; the guard/reconstruction part of `c11r_certificate.py`, `c11r_schema.validate_runs`; the contract, gate, policy (stages/stop conditions), errata E28 addendum + E32-E38 + `review_4_findings_disposition`; the R4 review. The round-5 diff (`git diff 5c5203c1 5d89686e`, 33 files) was surveyed; the quarantine diff was inspected with every digit masked (provenance hashes only changed).
- Scratch clones (both `git clone --no-local` of the worktree, checked out at 5d89686e): `work/cloneA` (the code that is imported; where producers were re-run) and `work/cloneB` (a FULL clone used as the repository under test, on throwaway `r5s_*` branches, reset to 5d89686e and clean after every probe).
- My own harnesses (not `c11r_chain.py`'s `Chain` class) in `.../scratchpad/r5/probes/`: `r5_harness.py` (drives the production `emit_qualification`, `build_authorization`, `c11r_runs.preflight/assemble`, `C.evidence_body`, `c11r_compare.execute_comparison` against clone B with a counting stub loader), `r5_topologies.py` (T0-T14 history topologies), `r5_guards.py` (G1-G8 guard/loader-order probes, forged and stale qualification), `r5_imp_driver.py` + `r5_preflight_driver.py` (loaded-module identity and the real runner pre-flight in a separate process whose execution root is clone B), `r5_detector_probe.py` (live processes vs `c11r_procs.campaign_workers`). Logs: `probes/topo.log`, `probes/guards.log`.
- Synthetic material only: fixture qualification/authorization (`allow_fixture=True`), `c11r_compare.synthetic_certs` (no certifier runs), stub loader. The quarantine was never opened or copied by any probe (content-free ids only, via production code).
- Not run anywhere: `c11r_runs.py`, `c11r_compare.py --approved-commit`, `c11r_qualify.py --approved-commit`, `c11r_table.py`. Run in clone A only: `c11r_chain.py`, `c11r_status.py --verify-only`, and the NT-only producers listed in items 39-43. In the primary checkout only `python3 -B code/c11r_qualify.py --self-test` (permitted) and read-only JSON inspection with `python3 -B -c` (no campaign module imported).

## Attacks

### 1. Full-history semantics -- PASS

`frozen_state` enumerates `git rev-list A..HEAD` (no pathspec) and reads the object id of every frozen path (35, taken from the contract AT A via `contract_at`) in every listed commit with one `cat-file --batch-check`; a commit fails HISTORY PURITY if any frozen path's id differs from A's (absent == None on both sides is equal). `protocol_history` uses `rev-list --parents A..HEAD` plus the out-of-range parents, and `protocol_artifacts_anywhere` (status) uses `rev-list --all --reflog HEAD`. Checked on my own topologies in the full clone (items 3-8): `commits_checked` equalled the number of commits I created after A in every case (e.g. 3 for the linear chain, 7 for T1, 9 for the criss-cross T3, 8 for the octopus T4), side-branch and merge commits included. The chain controls reproduce 69/69 in clone A (item 33).

### 2. History-simplification bypass -- PASS (one NOTE)

`grep` of every module for `log`, `rev-list`, `diff-tree`, `--first-parent`, `show`, `diff`: the only load-bearing traversals are the three `rev-list` calls above, none with a pathspec. Remaining `git log` uses are `c11r_table` (commit-message leak scan, no pathspec -> no simplification), `c11r_firewall` (now `--full-history -m`), and tree diffs in B0/mutations (`diff --name-only 440bcd91..HEAD`, pre-result bookkeeping, not execution). NOTE (N5-4 below): `rev-list` honours replace refs/grafts and the `GIT_*` environment; `git replace --graft <merge> <first-parent>` hides a merged side-branch edit from every check (T13: before the graft EXECUTION_INVALID at step 2; after it the comparator accepts and calls the loader). This is a deliberate history manipulation equivalent in effect to rewriting history (already a stated limit), so non-blocking; `git --no-replace-objects` plus a refusal when `refs/replace/*`, `info/grafts` or a shallow file exist would close it cheaply.

### 3. Side-branch edit + revert -- PASS

T1 (`c7_gaussian.py` edited, committed, reverted on a side branch; `merge --no-ff`): refused at step 2 "complete frozen history", history purity names the side commit, loader 0. The round-4 method (`git log A..HEAD -- <frozen>`) lists 0 commits here, `--full-history` lists 2 -- the R4-1 construction, now caught. Same result in the committed MHT3/MHT9/LS_HISTORY controls.

### 4. No-ff merge and other merge strategies -- PASS

- T2 `-s ours` merge of a side branch with an UNREVERTED edit to `c11r_policy.py` (final tree identical to A): refused at step 2 by history purity only (tree identity clean), loader 0; round-4 log lists 0.
- T3 criss-cross (branches x and y merged into each other, then x again; x edited and reverted `c11r_schema.py`): refused at step 2, loader 0.
- T4 octopus (4 parents; the edit/revert of `c11r_equiv.py` in the SECOND parent): refused at step 2, loader 0; round-4 log lists 0.
- Committed MHT6 (`-s ours`), MHT_octopus reproduce.

### 5. Hidden run artifact in merged history -- PASS

T6: a first runs artifact committed on a side branch and never deleted, the side merged `-s ours`, a second run sealed on the trunk: refused at step 2 ("holds a runs artifact other than the current one") and at the seal ("1 reachable commits hold other runs content"), loader 0. Committed MHT4 (run -> delete -> merge) and MHT4_preflight (the runner pre-flight refuses it) reproduce. T8: a run committed on a branch forked from the qualification commit BEFORE the authorization, merged: refused ("the authorization was not committed before the seal").

### 6. Hidden seal artifact -- PASS

T9: the SAME runs bytes sealed, deleted, re-added (linear): "introduced by 2 commits" at step 2 and at the seal, loader 0. Committed MHT5 (same bytes on a merged side branch) and MHT_Sa (different bytes, linear retry) reproduce. A second seal with different bytes is a foreign runs content in every variant I built.

### 7. Transitive-helper mutation in merged history -- PASS

T1 uses `c7_gaussian.py` (the rational Phi/phi core, imported only through `c11r_idrift`/`c11_certifier`; no certificate field records it): refused by history purity. Committed MHT9 and LS_HISTORY also use it.

### 8. Clean merge acceptance -- PASS, with a NOTE on conservatism

- Accepted (loader called exactly once, AGREEMENT_INSUFFICIENT with synthetic data): T0 linear; T7 the seal committed on a side branch forked after the authorization and merged normally; committed MHT7 (clean no-ff merge), MHT8 (merged branch touching only non-frozen files), MHT10, R3T_unrelated; and (clone A) an unrelated commit after A adding `review/REVIEW_C11R_PREFREEZE_R5.md` keeps `frozen_state` clean and `c11r_status.py --verify-only` CONSISTENT, so preserving this review after A does not break Q2/Q11.
- NOTE (N5-5): T5 -- a merge of a branch forked BEFORE A (from `A~1`) that only adds an unrelated note is REFUSED: its commits hold the pre-A state of 27 frozen paths. This is the intended semantics of a STATE check (any reachable commit not descending from A that holds another state fails), so merging e.g. `main` into the branch after A kills the chain. The protocol needs no such merge, so this is a liveness note, not a defect; it should be stated in `frozen_state`'s docstring.

### 9. Current-tree identity vs history purity -- PASS

`frozen_state` returns `ancestry`, `tree_identity`, `history_purity` separately; `verify_frozen_at` concatenates all three and every boundary (`_authorization_facts` -> authorize/run/compare, Q2, comparator step 2 + step 1 for ancestry) requires all empty. Distinguished in practice: T2 (purity only), the symlink case in item 18 (tree identity only: "a frozen path has uncommitted changes"), MHT1 (both). Tree identity includes `git status --porcelain --untracked-files=all` on the frozen paths.

### 10. Seal history -- PASS

`verify_seal` locates the seal as the unique INTRODUCER of the current runs content in `protocol_history(stage="compare")` (a commit holding the content none of whose parents holds it), requires exactly one, no foreign runs content anywhere after A, disk == seal blob, not dirty, schema-valid, stored sha == recomputed body digest. T6, T9, G7 (runs edited on disk after the seal: refused at step 2 and step 8, loader 0) and T7 (seal on a merged side branch: accepted) behave as specified. The docstrings and the policy's stop conditions now state that an uncommitted/unreachable discarded run is invisible to git (N4-9 closed as documentation).

### 11. Contract binding -- PASS (one NOTE)

`verify_contract` in clones A and B: no problems; `COMPARED_KEYS` now include `qualification_items`, `qualification_unknown_item_rule`, `protocol_paths`, `frozen_paths`; the committed contract carries 18 code files, 35 frozen paths (18 code + 16 pre-result artifacts incl. contract/gate + the quarantine + c7/c11 helpers), `protocol_paths` for runs/comparison/authorization/qualification, `qualification_unknown_item_rule: REFUSE`, `contains_target_results: false`. The gate is cross-checked against the contract's policy and statement digests (N4-1). NOTE (N5-6): the bound `frozen_paths` list is only COMPARED; `frozen_state` recomputes the set with the running code's `frozen_paths()` from A's contract. Equivalent while the code is the contract's (which the same check verifies), but using `contract_at(A)["frozen_paths"]` directly would make the root of trust literal.

### 12. Approved commit (root of trust) -- PASS (NOTE)

Step 1 reads the contract AT A (`contract_at`), step 3 requires the tree's contract object to equal it, and the frozen set comes from A's contract. R3S reproduces (wrong A refused before the loader; the same chain under its own A accepted). NOTE (N5-7): nothing requires `approved_commit` to be a full 40-hex commit id. T12: a TAG naming A is accepted end to end (qualification, authorization, pre-flight, comparator with the loader called); a movable ref makes the root of trust movable. Relative refs (`HEAD~1`) refuse themselves through the protocol-history checks, but a tag or branch name does not. Require `re.fullmatch("[0-9a-f]{40}")` and `rev-parse --verify A^{commit} == A`. Within the accepted human-root-of-trust limitation (4), hence a NOTE.

### 13. Qualification Q1-Q18 completeness -- PASS

`qualification_disposition` requires exactly the 18 ids, once each, canonical names, status in {PASS, FAIL}, every item bound to the recomputed contract digest, A and the bound qualifier digest; unknown ids REFUSE; the class is recomputed and a differing stored class refused. `c11r_qualify.main` emits Q1..Q18 each exactly once (read). QF1-QF8 reproduce.

### 14. Forged qualification PASS -- NOTE (inherent; accepted design)

A NON-fixture qualification built with the production `emit_qualification` from 18 PASS items with arbitrary details (no check run) is accepted by `build_authorization(fixture=False)` (probe Q_forged: problems []). Structure is enforced, execution of the checks is not (item details are never validated; only Q1/Q2/Q16/Q17-like facts are independently recomputed at later boundaries). This is the accepted qualification-binding design; it should be stated as such (the qualification evidences the qualifier's run only by the operator's protocol).

### 15. Stale qualification -- PASS

Refused: another contract (R3E, R3R), another approved commit (QF5 and `bound.approved_commit`), another host (probe Q_stale_host: both host checks fire), a replaced/failed earlier qualification committed in history (ORD2: foreign qualification content), a qualification present AT A (protocol history). Not refused: a later edit of the unfrozen `c11r_status.py`, which Q11 executes (see N5-8).

### 16. Import-path shadow -- DEFECT (BLOCKER R5-2)

The round-5 repair keys the loaded-module check on the BASENAME of `module.__file__` (`if name not in by_name: continue`) and the shadow scan on `git ls-files --others -- <code dir>/*.py`. A shadow that is not a `.py` file is invisible to both. Reproduced in clone B (a separate process whose execution root is clone B, production functions):
- `c11r_certificate.pyc` (a sourceless bytecode file compiled from the module plus one marker line) placed in C11's code directory -- exactly R4's N4-3 location, which `c11r_idrift`'s `sys.path.insert(0, C11/code)` puts ahead of HERE -- is imported by the runner's own import order (`SourcelessFileLoader`, marker executed), and the PRODUCTION runner pre-flight (`c11r_runs.preflight` on a fixture-authorized scratch branch) returns NO problem.
- `c11r_schema.pyc` in the same directory is loaded in the comparator's import order; `verify_loaded_modules` returns [] and silently drops `c11r_schema.py` from its `checked` list; `code_dir_shadows` returns [].
- The file is git-ignored (`*.pyc`), so `git status` shows nothing and it leaves no trace once deleted; a COMMITTED `.pyc` is equally invisible (the tracked-duplicate check also globs `*.py`, and no history check covers it).
By contrast a `.py` shadow (untracked or tracked), a package directory `c11r_schema/__init__.py`, a symlink and a zip of `.py` are caught (the package only by `code_dir_shadows`; `verify_loaded_modules` misses it too). See BLOCKERS.

### 17. Wrong module.__file__ -- NOTE

`verify_loaded_modules` trusts the module's own `__file__`. A `.py` shadow whose last line assigns `__file__ = <execution root>/<contract path>` passes `verify_loaded_modules` ([]) although `__spec__.origin` names the shadow; it is caught only by `code_dir_shadows` (untracked, or tracked duplicate). A module rewriting its own dunder is in-process code, i.e. inside the disclosed "in-memory patching" limit; checking `__spec__.origin` and `__spec__.loader.path` as well is cheap and should accompany the R5-2 fix.

### 18. Symlinked load-bearing module -- PASS

Replacing `code/c11r_schema.py` in the execution root with a symlink to an identical external copy: `verify_loaded_modules` reports "reached through a symlink" and "loaded from another file", and tree identity reports "a frozen path has uncommitted changes" (typechange). IMP2 (symlink in a shadow directory) reproduces.

### 19. Wrong checkout -- PASS

In production `main()` passes `C.REPO` as the repository and the execution root, so the code checked is the checkout's own. A wrapper that points the comparator at another repository cannot load magnitudes: `load_original_magnitudes` needs `sanctioned_protected_access`, which requires `__main__` to resolve to the real `c11r_compare.py` (item 31), and `execute_comparison`/`verify_seal` on `C.REPO` from any other program raise (`GUARD_real_repository*` reproduce). The loaded-module check compares against `<C.REPO>/<contract path>`; a module imported from a different checkout is "loaded from another file" (IMP1/IMP4 reproduce).

### 20. Wrapper Python process -- PASS for the claimed forms; NOTE (undisclosed miss; weak live control)

Live, on this host, against the production `c11r_procs.campaign_workers()` (`probes/r5_detector_probe.py`; each child only imports `c11r_boxdata` and sleeps; no computation): a wrapper script in a neutral directory importing a campaign module is CAMPAIGN_WRAPPER when given by absolute path, by relative path from another cwd (resolved through `lsof`), and under `-X importtime`; a wrapper using `importlib.import_module("c11r_" + ...)` is also caught (the literal prefix matches). NOT seen (FOREIGN_PYTHON): the same wrapper run as `python3 -m cProfile -o /dev/null wrapper.py` or `python3 -m trace --count ... wrapper.py` -- `-m <tool> <script>` never reads the script, and this common profiling form is not in `not_checked`/E36 (NOTE N5-9). Also: the committed live control `wrapper_script_importing_campaign_detected` is satisfied through the ARGV branch (its temporary directory is named `c11r_procs_*`, which matches CAMPAIGN_TOKEN), not through the source read: `campaign_role(<that argv>, script_source=None)` is already CAMPAIGN_WRAPPER, while the same argv from a neutral directory gives None. So the live control could not fail if the source-reading branch broke (my probe exercised that branch live, and it works). The detector gates concurrency only (cost, pre-flight, B0, regen), not identity or classification -- non-blocking.

### 21. -c / -Bc process -- PASS

Live `-Bc "...import c11r_boxdata..."` is CAMPAIGN_ADHOC; planted `-c`, `-Bc`, `-cimport ...`, `-Bm c11r_runs` rows pass (28/28 planted controls re-run in clone A). `-c "exec(os.environ[...])"` is not seen -- disclosed ("code built at run time").

### 22. Framework-build Python -- PASS

The host interpreter is `/Library/Frameworks/Python.framework/.../Python.app/Contents/MacOS/Python`; every live child above was classified from that executable; `live_controls()` re-run in clone A: ALL_PASS (framework child detected, exited child gone).

### 23. Detector self-match resistance -- PASS

The calling process and its whole ppid chain are EXCLUDED_SELF_CHAIN (my probe: own pid in `self_chain`, not a worker); shells are never interpreters, so a shell whose string names a campaign script cannot match (live and planted). Vanished pids are VANISHED. Known design consequence (as R4 noted): a campaign process that launched the checker is excluded as an ancestor.

### 24. Guards before the loader (the twelve-step order) -- PASS

Code: `execute_comparison` records steps 1-8 (approved commit, complete frozen history, contract, gate, qualification, authorization, run, seal); only if all pass does it call `pre_numeric` (no magnitude) and record G8, G10, G19 and step 12 (value trace incl. demotion, INVALID targets, independence, `verify_loaded_modules`, `code_dir_shadows`, comparison rule); `mags = loader(stmt)` is reached only when every step passed (`if problems or not all(pass): return ... loader_called=False`); the step names are asserted against `STEPS`. Controls: LS_G8/G10/G19/DEMOTE/SEAL/CONTRACT/HISTORY refuse at their named step with the spy at 0, LS_VALID calls it once (reproduced). Nothing before step 13 reads the quarantine (step 2 takes its content-free id through `git hash-object`).

### 25. G8 failure does not open magnitudes -- PASS

Probe G1 (full clone; D1 reported NOT_CERTIFIED, run re-stamped, otherwise valid chain): EXECUTION_INVALID refused at "G8", loader 0.

### 26. G10 failure does not open magnitudes -- PASS

Probe G2 (F_D marked POINTWISE_INFEASIBLE yet sent): refused at "G10" (and step 12 also records the value-trace consequence), loader 0.

### 27. G19 failure does not open magnitudes -- PASS

Probe G3 (internally consistent certificates at depth 6 instead of 5): refused at "G19", loader 0.

### 28. Bad history does not open magnitudes -- PASS

T1-T4, T6, T8-T10 (items 3-6) all refused at step 2 with loader 0. Only the graft of N5-4 (item 2) gets through.

### 29. Bad seal does not open magnitudes -- PASS

G7 (sealed runs edited on disk and re-stamped, uncommitted): refused at step 2 ("not committed at HEAD", foreign content) and step 8 ("uncommitted changes"), loader 0; T9 (re-introduced seal) likewise.

### 30. N4-8 verdict wiring (demotion) -- PASS for the repaired case; NOTE (bypass)

Probe G4 (Abar reported NOT_CERTIFIED while its cited F_K certificate proves it): refused at step 12 "(demoted)", loader 0; `numeric_phase` also makes `guards_ok` include the value trace. NOTE (N5-11): probe G5 -- the same demotion with the target's `certificate_id` set to null -- is NOT detected: `evaluate_target` looks only at the certificate the target cites, `validate_runs` accepts a NOT_CERTIFIED target citing nothing, and the comparator reaches the loader (AGREEMENT_INSUFFICIENT). `c11r_runs.assemble` always cites `TARGET_MAP[k]` when that certificate exists, so requiring exactly that citation would close it. Reachable only through a hand-edited runs artifact (limitation 3), hence non-blocking.

### 31. Runtime open-guard scope and the accuracy of its claims -- PASS as defence in depth; NOTE (claims overstated)

Planted dummy file `probes/guard/quarantine/C11R_ORIGINAL_MAGNITUDES.json` (never the real quarantine), production `c11r_common` guard: refused -- `open(str)`, `open(Path)`, `Path.read_bytes`, `os.open(str|bytes)`, a symlink with an innocent name, chdir + bare name, opening the quarantine directory as a dir fd, `sys.argv[0] = "c11r_compare.py"` inside `sanctioned_protected_access`. NOT refused: (a) `io.FileIO(pathlib.Path(...))` -- the audit event carries the PathLike object and `_open_guard` returns for any non-str/bytes argument (`# a file descriptor, not a path`); (b) a HARD link with an innocent name (`os.link` raises no `open` event; realpath of a hard link is itself); (c) `os.replace` of the protected file to an innocent name, then `open`. None of these is used by production code and the guard is not the trust boundary, but the frozen gate's G16 ("refuses any Python-level open of a protected path -- judged as given, absolute and realpath") and the `runtime_open_guard_controls.scope` / `c11r_common` "what it still does not see" lists are inaccurate: (a) is a Python-level open of a protected path. NOTE N5-10: apply `os.fspath` to PathLike arguments and list hard links / renames as not covered.

### 32. Symlink / chdir controls -- PASS

Both refused in my probe (item 31) and in the committed firewall `runtime_open_guard_controls` (ALL_PASS). The residual (`__main__.__file__` rewritten and the sanctioned context entered) is recorded as demonstrated.

### 33. R3A-R3T regression -- PASS

`code/c11r_chain.py` re-run in clone A (6 min): 69/69 ok -- R3 25/25, MHT 15/15, LS 8/8, QF 8/8, IMP 10/10, ORD 3/3; "quarantine-access ordering holds: True"; CHAIN_CLASS PASS. Each control carries its exact expected reason and, at the comparator, its expected step (`record` requires both, plus loader 0 for every refusal and exactly 1 for every comparator ACCEPT). The regenerated artifact differs from the committed one ONLY in absolute temporary paths and synthetic commit ids (58 lines; classified mechanically). My own harness independently reproduces the R3A class on merged history (T1) and the valid path (T0). (Contract binding probe for the new keys: dropping Q18 from the running schema, moving a protocol path, or dropping a pre-result artifact from the frozen set each makes `verify_contract` refuse on `qualification_items` / `protocol_paths` / `frozen_paths`.)

### 34. B-1 regression (seal/schema compatibility) -- PASS

Producer-built runs artifacts (`c11r_runs.assemble` + `C.evidence_body(producer=c11r_runs.py)`, exactly what `main` writes) are sealed and accepted by the real `verify_seal`/`execute_comparison` in the full clone (T0, T7, T12); the comparator's typed seal controls pass (comparator self-test 10/10 in my mutations re-run).

### 35. B-2 regression (firewall truth in production) -- PASS

Audit-hook trace (`probes/r5_trace.py`) of `c11r_status.py --verify-only` in clone A: no protected open; only the 16 allowlisted JSON artifacts opened; the only content-capable git command is `cat-file --batch-check` (ids). The runtime guard was live in every campaign process I ran (chain, status, mutations, validation, harnesses) and never fired on production code. Count-only value scan (item 45): 0 hits. Firewall artifact: CLAIM DEFENSE_IN_DEPTH_HEURISTIC; the unresolved-pattern list now holds only flags/revisions/code-shaped fallbacks and planted guard-control names (N4-11 closed).

### 36. B-3 regression (certificate -> proposition) -- PASS

`c11r_certificate.py`, `c11r_schema.py`, `c11r_equiv.py`, `c11r_boxdata.py`, `c11r_idrift.py` are blob-identical to bd00c1f6 (idrift also to 49b17ab4; `c11_certifier.py`, `c7_gaussian.py` to 440bcd91). Mutations re-run in clone A: 16/16 adversarial certificate controls caught, none missed.

### 37. B-4 regression (production guards) -- PASS

G8, G10, G19 and value tracing evaluated in production and refused before the loader (items 25-27, 30); mutations re-run: 41/41 DETECTED, MUTATION_CLASS PASS; labels now 24 PRODUCTION_GUARD, 3 PRODUCTION_SCIENCE, 2 PHASE12_QUALIFICATION_GATE (M01/M02), 1 DEFENSE_IN_DEPTH_HEURISTIC (M03), 7 SUITE_LOCAL_PROPERTY, 4 SUITE_LOCAL_AUDIT; the retracted "defines no guard" sentence survives only as a quotation of the retraction (N4-7 closed). The regenerated mutations artifact differs from the committed one only through the validation artifact's wall-clock field (its recorded input hash).

### 38. B-5 regression (qualifier on the frozen policy, NT only) -- PASS

`python3 -B code/c11r_qualify.py --self-test` in the primary checkout: 8/8 PASS, wrote nothing (the existing `__pycache__` files were not modified). `main` not run; its numerical items use NT and e = 5/2 only (read). Every bytecode cache present in the primary checkout's three code directories is either accepted-and-equal to its source's compilation or ignored by the loader, so the new cached-bytecode check will not refuse falsely there.

### 39. Scientific validation -- PASS

`c11r_validate.py` re-run in clone A (NT only, 487 s): VALIDATION_CLASS PASS, 17/17, failed []; every check record identical to the committed one; the file differs only in the top-level `seconds` (and hence its `sha256`).

### 40. Certificate forgery controls -- PASS

16/16 adversarial controls caught (re-run); probe G8 (a certificate attributed to `taboo_certify.py`) -> INDEPENDENCE_VIOLATION with loader 0. Consistent forgeries remain detectable only by re-execution (stated limit; accepted).

### 41. Statement/numeric separation -- PASS

Mutations re-run: "same proposition, different value: statement EQUIVALENT both times; numeric AGREES -> INSUFFICIENT: pass". `pre_numeric` decides statement status without magnitudes; `numeric_phase` only classifies statement-EQUIVALENT/STRONGER targets.

### 42. D5/P32 policy unchanged -- PASS

Policy 5c5203c1 -> 5d89686e: `rule`, `candidate_family`, `calibration`, `calibration_workload`, `chosen`, `cap_seconds`, `cap_rss_mb`, `safety_factor`, `screen_grid`, `boxes_at_depth` unchanged; changed only `candidates` (estimates from the re-measured revision-3 cost), `chosen_cap_fraction_with_safety_factor` (0.720 -> 0.7334), `cost_model`, the N4-9 wording, provenance and the statement-table digest (the table was re-extracted because `c11r_table.py` gained `sanctioned_protected_access`; the quarantine diff, digits masked, changed only provenance hashes). Feasible set unchanged {D4/P32 0.202, D4/P64 0.408, D4/P128 0.839, D5/P32 0.733}; D5/P64 at 1.505 is not borderline. Contract and gate regenerate BYTE-IDENTICALLY in clone A (contract body digest 6056d238..., gate fe70321a...). NT calibration not re-run (the `calibration` block is byte-unchanged since R4 reproduced it exactly).

### 43. Cap unchanged and the N4-9 wording -- PASS

10800 s / 8192 MB / SF 3/2 unchanged. The policy's stop conditions and `c11r_runs` docstring now say accurately that the cap is checked before each stage and certification, that a running certification is not interrupted (overrun bounded by that certification), and that "no retry" is enforced only against COMMITTED runs.

### 44. No target science -- PASS

The only `Blk(` on the cell-306 block is `c11r_runs.main` (never run); validation, mutations, qualifier and cost use NT or e = 5/2 (grep and read); the chain controls and my harnesses use `synthetic_certs` (no certifier runs; the drift block is a label). I ran no certifier, selector, screen or bound on any open-cell block.

### 45. No target values -- PASS

`probes/r5_leak_scan.py` (count-only; imports no campaign module; prints counts only): 165 forms of the six originals (exact rational, float repr, 2-10 dp half-even/half-up/truncated with and without leading zero, 3-10 significant figures, scientific) over all 39 tracked namespace files outside quarantine/ and review/ at 5d89686e, the 5d89686e commit message, this review and my probe logs: 0 hits. Controls: a synthetic string carrying a generated form hits; a clean string does not; the (protected) R1 review, counted only, has 11 hits.

### 46. No qualification -- PASS

`evidence/qualification/C11R_QUALIFICATION.json` absent on disk and in all 721 commits reachable from any ref, reflog or HEAD (one `cat-file --batch-check` per commit; also `git log --all --reflog --full-history -m --name-only` over the directory: empty).

### 47. No authorization -- PASS

`config/C11R_AUTHORIZATION.json`: same result (absent everywhere). `"guard": "ALLOW"` at HEAD occurs only in `c11r_contract.build_authorization` (a builder), B0's planted control string, the quoted R4 review, two C10 review markdowns and an order-3 adjudication key -- no live setting.

### 48. Guard DENY -- PASS

Gate `guard: DENY` (and `verify_gate` refuses anything else); no authorization anywhere. (But see R5-1: the frozen runner's instruction to "set the guard back to DENY" before Phase 15.)

### 49. No evidence/runs/ -- PASS

Absent on disk and in all 721 reachable commits; `evidence/comparison/` likewise. My runs artifacts existed only on throwaway branches of scratch clone B, now deleted (clone B back at 5d89686e, clean).

### 50. Historical reviews preserved -- PASS

R1/R2/R3/R4 blobs at HEAD == blobs at 6d7cd546 / 6ae05833 / f6c737c3 / 5c5203c1 == working-tree `hash-object` (8a445008, af431bc0, 19e276e4, b2afdb49); each file is touched by exactly its preserving commit (`git log --all --full-history`); R4 is also identical to the R4 reviewer's scratch original.

### 51. Historical verdicts unchanged -- PASS

`git diff --name-only 440bcd91 5d89686e` outside the C11R namespace: empty; per-commit `diff-tree` over the (merge-free) range 440bcd91..5d89686e: no file outside the namespace ever touched. C11's EXECUTION_INVALID stands (B0_04, count-only).

### 52. r5 authoritative -- PASS

`K5_COVERAGE_MAP_R5.json` object f978eeb6 at 440bcd91 and at HEAD; B0_06 PASS.

### 53. No r6 -- PASS

No `K5_COVERAGE_MAP_R6` in any ref's full history (`--all --reflog --full-history -m`) or in the index.

### 54. Main untouched -- PASS

Local refs only (no fetch): `refs/heads/main` = c123b9bb..., `refs/remotes/origin/main` = 1cb45382...; `evidence/b0/C11R_B0.json` records `LOCAL_MAIN_REF` and `REMOTE_MAIN_REF` as separate top-level fields with exactly these values (B0_09 PASS). The campaign branch is on no remote-tracking ref (0 remote branches contain 5d89686e).

---

## Reviewed identity (for any later auditor)

At 5d89686e: contract body digest `6056d238301e1fac95e08e22b890ee6fdedaf0757030adb0e3f3b1850004aa09` (18 code files, 35 frozen paths); gate `fe70321af68611cf37d64342627bcd26c7225c49b0f64f5c822d5e80d63acc65` (its `execution_contract_sha256` equals the contract digest); policy `4d0b3a53...`; statement table `2cba1245...`; cost `24adc06f...`. Contract and gate regenerate byte-identically in a scratch clone; `verify_contract`, `chain_roots` and `frozen_state(A)` return no problem there.

## Summary

Round 5 closes R4-1 in fact, not only on linear histories: every load-bearing history check now enumerates complete reachable history without a pathspec and checks the STATE of every frozen path in every commit; tree identity and history purity are reported separately and both required; the seal is the unique introducer of the sealed content. My own topologies in a full clone -- side-branch edit/revert with `--no-ff`, `-s ours` with an unreverted edit, criss-cross, a 4-parent octopus, hidden runs and seals, a run committed before the authorization, re-introduced seals, a committed-then-deleted comparison -- are all refused at step 2 with the loader never called, and the legitimate topologies I built are accepted. The twelve-step order holds (G8/G10/G19/demotion/seal/history failures all refuse before the loader), the typed Q1-Q18 schema and the contract's new keys are enforced, and every regression item reproduces (chain 69/69, validation 17/17, mutations 41/41 with 16/16 forgeries caught, contract and gate byte-identical, no target science, no target value, no qualification/authorization/runs/comparison anywhere, guard DENY, r5, no r6, main refs recorded). TWO load-bearing defects remain, both in frozen code and both cheap to fix now and impossible to fix after the freeze: the frozen runner (and policy) instruct the operator to "set the guard back to DENY" before Phase 15, which makes the comparator refuse a valid run irrecoverably (R5-1); and the new loaded-module identity check -- the N4-3 repair, bound as part of G20 -- is blind to a non-`.py` shadow, so R4's own N4-3 construction with a `.pyc` suffix passes the runner pre-flight and the comparator's step 12 (R5-2).

## Load-bearing BLOCKERS

### R5-1 (MAJOR): the frozen Phase 14 instruction "set the guard back to DENY" makes a valid run EXECUTION_INVALID, irrecoverably

**Where.** `code/c11r_runs.py` line 228 (frozen, bound in the contract) prints after writing the runs artifact: "NEXT: commit this artifact to seal it, set the guard back to DENY, and only then run c11r_compare.py." The frozen policy's stage 5 says "every output written and hashed under the frozen run schema; then guard DENY". In this code base "guard DENY" MEANS "no authorization": the gate is DENY permanently (`verify_gate` refuses anything else), the only ALLOW is `config/C11R_AUTHORIZATION.json`, and both `verify_authorization` and `execute_comparison` report its absence as "no authorization; guard is DENY". The comparator, however, REQUIRES the authorization to be present, committed at HEAD and introduced exactly once before the seal (step 1; `protocol_history(stage="compare")`; `_issue_order`).

**Reproduce** (`probes/r5_topologies.py` T11; full scratch clone of 5d89686e; production `emit_qualification`, `build_authorization`, `c11r_runs.preflight/assemble`, `C.evidence_body`, `execute_comparison`; fixture artifacts; counting stub loader): qualify, authorize, pre-flight, seal a valid synthetic run; then do what the runner says -- remove the authorization.
1. Uncommitted removal: EXECUTION_INVALID at step 1 ("no authorization; guard is DENY"; step 2 also "the authorization was not committed before the seal"), loader 0.
2. Removal committed: the same.
3. Restoring it with `git revert` of that commit: still EXECUTION_INVALID -- "the authorization artifact was introduced by 2 commits".
Any other reading of the instruction (editing the authorization's `guard` to DENY) is refused as well (foreign authorization content; "not an ALLOW for cell 306"). Once the removal is committed, no forward-only repository action recovers the chain; only a new approved commit (a new freeze) or a history rewrite, which the protocol treats as undetectable misconduct.

**Why it is load-bearing.** Phase 14 is ONE execution with no retry; following the frozen tool's own printed next step converts a valid run into EXECUTION_INVALID (the class of outcome that already ended C11). The text is in frozen files and cannot be corrected after the freeze.

**Minimum fix.** Make the runner's message and policy stage 5 say that the authorization stays committed and unchanged through Phase 15 (e.g. "commit this artifact to seal it; do not modify or remove the authorization; then run c11r_compare.py --approved-commit <A>"), or define "guard DENY after the run" as something the comparator accepts; add a chain control that follows the runner's printed instructions literally.

### R5-2 (MAJOR): the loaded-module identity check (N4-3 repair, part of G20) is blind to non-`.py` shadows; R4's N4-3 construction with a `.pyc` passes the runner pre-flight and the comparator's step 12

**Where.** `c11r_contract.verify_loaded_modules` selects the modules to check by the BASENAME of `module.__file__` (`if name not in by_name: continue`), so a contract module loaded from `c11r_certificate.pyc`, a `.so` extension, a package `__init__.py` or a zip member `x.pyc` is silently skipped (and dropped from its `checked` list). `c11r_contract.code_dir_shadows` lists only `git ls-files [--others] -- <dir>/*.py`. Both are in the frozen contract; the gate's G20 states "the loaded modules to be the contract's files"; E35 classifies the repair FIX_NOW_LOAD_BEARING; the contract docstring states the check "establishes what the import system loaded, from which file".

**Reproduce** (`probes/r5_imp_driver.py`, `probes/r5_preflight_driver.py`; a separate process whose execution root is scratch clone B, production functions only):
1. Compile `c11r_certificate.py` plus one marker line into a sourceless `c11r_certificate.pyc` (`py_compile.compile(..., cfile=<C11 code dir>/c11r_certificate.pyc)`) -- the directory R4 used, which `c11r_idrift`'s `sys.path.insert(0, C11/code)` places ahead of HERE. The file is git-ignored (`*.pyc`), so `git status` shows nothing.
2. Import in `c11r_runs.py`'s order (`c11r_boxdata` first): `c11r_certificate` is loaded by `SourcelessFileLoader` from the shadow and its marker runs; the PRODUCTION `c11r_runs.preflight` (fixture qualification + authorization committed on a scratch branch) returns NO problem.
3. Same with `c11r_schema.pyc` in the comparator's import order: `verify_loaded_modules(contract_at(A))` returns [] and omits `c11r_schema.py` from `checked`; `code_dir_shadows` returns [].
A COMMITTED `.pyc` there is equally invisible (the tracked-duplicate test also globs `*.py`; no history check covers the path). By contrast the `.py` variants (IMP_stray) are caught, as are symlinks and zips of `.py`.

**Why it is load-bearing.** The guards and the reconstruction (`c11r_certificate`), the run schema (`c11r_schema`), the process detector, etc. can execute from a file that is not the contract's while the pre-flight, Q4 and comparator step 12 report the run as executed by the contract's code -- a mis-identified run under G20, by the very construction N4-3 described, and not by in-memory patching (which is disclosed and out of scope). The check is frozen code.

**Minimum fix.** Iterate over the contract's module NAMES: for every contract module stem present in `sys.modules`, require `__spec__.origin` (and `__file__`, and `__spec__.loader.path`) to resolve to exactly `<root>/<contract path>` with a `SourceFileLoader`; refuse any `sys.modules` entry whose origin lies in a campaign code directory but is not a contract path; make `code_dir_shadows` refuse ANY file or directory (tracked, untracked or ignored; `.pyc`, `.so`, `.pyd`, packages, `.zip`) in `CODE_DIRS` whose import name equals a contract module's; add IMP controls for a sourceless `.pyc`, a package directory and a module that rewrites its own `__file__`.

## Non-blocking observations

- **N5-1 (NOTE; item 14).** A non-fixture qualification built with the production builder from 18 PASS items, without running any check, is accepted by `build_authorization`. Inherent to a record-based qualification (accepted design); say explicitly that the qualification evidences the checks only through the operator's protocol.
- **N5-2 (MINOR; T14).** At stage "compare" nothing refuses an UNCOMMITTED `evidence/comparison/C11R_COMPARISON.json` already on disk (a previous, discarded comparator run); the comparator reaches the loader and would overwrite it. The runner-stage existence check exists; add the same at the comparator.
- **N5-3 (NOTE).** `c11r_runs.main` re-reads the policy and statement table after the pre-flight and records their STORED `sha256` fields as `policy_sha256`/`statements_sha256`; it never re-checks the body digest of the bytes it actually uses. Only a file swap during the run window reaches this (runtime-modification class), but verifying `body_digest(policy) == identity["policy_sha256"]` after loading is one line.
- **N5-4 (NOTE; item 2, T13).** `rev-list` honours replace refs, grafts and the `GIT_*` environment: `git replace --graft <merge> <first-parent>` hides a merged side-branch edit and the comparator accepts. Deliberate history manipulation (like a rewrite); run history commands with `--no-replace-objects` and refuse when `refs/replace/*`, `info/grafts` or a shallow file exist. (I also checked a git clean filter: it can make `git hash-object` report the committed id for modified bytes, but tree identity's `git status` still flags the file -- not an issue.)
- **N5-5 (NOTE; item 8, T5).** Merging any branch forked before A (e.g. `main`) after A is refused by the state check even if it touches nothing frozen; intended by design but not stated.
- **N5-6 (NOTE; item 11).** `frozen_state` recomputes the frozen set with the running code instead of using `contract_at(A)["frozen_paths"]`; equivalent while the code is the contract's.
- **N5-7 (NOTE; item 12, T12).** `approved_commit` may be any revision expression; a tag naming A is accepted end to end, making the root of trust movable. Require a full 40-hex id that `rev-parse --verify` maps to itself.
- **N5-8 (NOTE; item 15).** Q11 executes `c11r_status.py`, which is not a frozen path (nor are `c11r_chain.py`, `c11r_mutations.py`, `c11r_firewall.py`, `c11r_validate.py`, whose artifacts are frozen); a post-A edit of `c11r_status.py` is caught by nothing but that same file's own freshness logic. Freeze it (or drop Q11's reliance on it).
- **N5-9 (NOTE; item 20).** Detector revision 3 does not see `python -m cProfile|trace ... wrapper.py` (the script is never read under `-m`), undisclosed in `not_checked`/E36; the committed live wrapper control is satisfied through its `c11r_procs_*` temporary-directory name in argv, not through the source read, so it cannot fail if that branch breaks.
- **N5-10 (NOTE; item 31).** The runtime open-guard does not refuse `io.FileIO(pathlib.Path(...))` (PathLike audit argument skipped), a hard link with an innocent name, or `os.replace` then open; the frozen G16 text ("refuses any Python-level open of a protected path") and the guard's scope lists overstate it. Apply `os.fspath` and list the rest as not covered.
- **N5-11 (NOTE; item 30, G5).** The demotion check is bypassed by also nulling the target's `certificate_id` (loader reached, AGREEMENT_INSUFFICIENT); require NOT_CERTIFIED implementable targets to cite `TARGET_MAP[k]` whenever that certificate exists. Hand-edited artifact only.
- **N5-12 (NOTE).** `protocol_history` is path-exact: a discarded run or comparison committed under another file name is not seen, although the docstrings say "a replaced, hidden or discarded run on any branch". Deliberate renaming only; state it.
- **N5-13 (NOTE; item 17).** `verify_loaded_modules` trusts `module.__file__`; a `.py` shadow that assigns its own `__file__` passes it (only `code_dir_shadows` then catches it). Check `__spec__.origin` too (part of the R5-2 fix).

## What is right and should be kept

The complete-history design (state check over `rev-list` without pathspec; separate tree identity and history purity; introducer-based seal; protocol-artifact ordering), the twelve-step comparator with the loader strictly last, the typed and recomputed qualification disposition, the contract's new bound keys, the exact-reason/exact-step chain controls with a loader spy, and the intact pre-result state. The regression surface (validation, mutations, forgeries, separation, cost/policy choice, cap, reviews, predecessors, r5, main refs) reproduces.

## Blocker list

- R5-1 (MAJOR): the frozen runner (`c11r_runs.py` NEXT message) and policy stage 5 instruct "set the guard back to DENY" before Phase 15; in this code base guard DENY = no authorization, and the comparator requires the authorization committed at HEAD and introduced once -- following the instruction yields EXECUTION_INVALID for a valid run (reproduced: removal uncommitted, committed, and restored by revert all refused), irrecoverable once committed.
- R5-2 (MAJOR): `c11r_contract.verify_loaded_modules` (keyed on `__file__` basename) and `code_dir_shadows` (`*.py` only) miss non-`.py` shadows; a sourceless `c11r_certificate.pyc` (or `c11r_schema.pyc`) in C11's code directory is loaded by the runner's (comparator's) import order while the production runner pre-flight and comparator step 12 report no problem -- G20's "the loaded modules to be the contract's files" is not implemented.

DISPOSITION: NOT_READY
