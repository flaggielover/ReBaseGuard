# C11R pre-freeze review, round 7 (independent)

- Reviewed commit: dbd6cd89485b6fea9e9af22f68983a9ed0f5d507 (branch p5y-k5-tail-c11r-n9-statement-alignment, worktree /Users/suzhe/ReBaseGuard-k5c11r; local only)
- Date: 2026-09-24 (host clock at start: 2026-09-24 12:20 UTC)
- Reviewer: new independent reviewer (no involvement in C11R rounds 1-6; R1-R6 read as history only)
- Precondition: HEAD == dbd6cd89485b6fea9e9af22f68983a9ed0f5d507 and `git status --porcelain` empty -- VERIFIED at the start of the review.
- Numerics policy: no kernel, certifier, selector, screen or bound evaluated on any open-cell drift block; numerics only on NT or e = 5/2. No original cell-306 magnitude, rounded/truncated form or ratio to one appears in this file.
- Writes: only in scratch clones under .../scratchpad/r7/review_work/ (`git clone --no-local`, checked out at dbd6cd89) and synthetic repositories there. The primary checkout was only read.

(Written incrementally.)

## Method

- Scratch clones (each `git clone --no-local` of the worktree, checked out at dbd6cd89): `review_work/cloneA` (the code my in-process harnesses import), `review_work/cloneB` (spare), `review_work/cloneC` (producers re-run there: `c11r_chain.py`, `c11r_mutations.py`, `c11r_firewall.py`, `c11r_contract.py`, `c11r_gate.py`, `c11r_table.py --leak-check`, `c11r_validate.py`, `c11r_status.py --verify-only`).
- Synthetic repositories: built with cloneA's production `c11r_chain.Chain` helper (closure + namespace code copied, contract and gate built by the production builders, fixture qualification/authorization, `synthetic_certs`, no certifier run) under `review_work/tmp/`. Two harness styles: (1) IN-PROCESS (cloneA's code executes, the repository under test is synthetic -- the chain-control setting); (2) EXEC-ROOT = REPOSITORY: a driver outside the repository puts the SYNTHETIC repository's code directory first on sys.path and imports the campaign modules FROM THAT REPOSITORY, so `C.REPO`, the code directories checked by L1/S/B and the repository under test coincide, as in production (`probes/atk_driver.py`, `attack.py`, `battery.py`, `e1_*.py`..`e5.py`). For the comparator in style (2) the synthetic repository's `c11r_compare` module object is made `__main__` (synthetic repositories only).
- Boundary programs were launched only in synthetic repositories: `c11r_compare.py` / `c11r_qualify.py` with NO argument (usage or barrier), and `c11r_runs.py` with no argument ONLY where `c11r_compare.py` had just refused at the barrier for the same plant.
- Primary checkout: only read (`git` read-only commands, `python3 -B` inspection importing cloneA's modules and pointing the read-only production verifiers at the primary path: `verify_contract`, `verify_gate`, `code_dir_shadows`, `preimport_barrier_problems`, `_pyc_matches_source`; no `git status` there), and `python3 -B code/c11r_qualify.py --self-test`.
- Not run anywhere: `c11r_runs.py` main on anything but a barrier refusal, `c11r_compare.py --approved-commit`, `c11r_qualify.py --approved-commit`, the extraction `c11r_table.py` (without `--leak-check`). No open-cell numerics.

## Attacks

### 1. A stdlib-named sourceless .pyc (fractions.pyc in the campaign's code directory, ast.pyc in C11's and C7's) -- PASS

How: `probes/battery.py` A1a/A1b/A1c, exec-root = repository (authorized chain for the runner and Q4, sealed chain for the comparator), plant made with `py_compile` from the interpreter's own source plus a marker.
- Boundary program start: `c11r_compare.py` and `c11r_qualify.py` (no argument) exit 1 at "REFUSE (pre-import barrier ...)" and the marker did NOT run; `c11r_runs.py` (no argument) likewise refuses at the barrier, marker not run. In driver mode, importing `c11r_runs`/`c11r_compare`/`c11r_qualify` as modules also raises the barrier's SystemExit (the barrier is module-level code).
- Behind the barrier (driver importing barrier-free campaign modules, then the production checks -- what would remain if a program were started without its barrier): fractions.pyc -> L1 "module 'fractions' was loaded from .../code/fractions.pyc, inside a campaign code directory, which is not an approved contract source" + S (not Python source; stdlib import name; not in the frozen inventory). ast.pyc in C11's and in C7's code directory (reached lazily through `verify_contract` -> `ast`): the same L1 + S refusals. The R6-1 construction is repaired.
Finding class: none (repaired).

### 2. A stdlib-named source file in a campaign code directory -- PASS

A2a (`fractions.py` in the campaign directory) and A2b (`ast.py` in C11's): barrier refuses all three programs (marker not run). Behind the barrier: `verify_contract` alone already refuses ("code identity differs for ['fractions.py']", "frozen_paths differs", "code_directories differs": the recomputed closure and inventory see the new source), plus L1 and S (stdlib name, not in inventory, untracked).

### 3. A committed stdlib-named package -- PASS

A3 (`fractions/__init__.py` in the campaign directory, `git add -f` + commit after A) and A3b (`ast/__init__.py` committed in C7's directory): barrier refuses (a directory entry); behind the barrier L1 (loaded from `.../fractions/__init__.py`, not approved) and S ("is a directory (a package or namespace package)", stdlib name, not in the inventory). Committing changes nothing (S is keyed on the frozen inventory, not on tracking).

### 4. An untracked stdlib-named package -- PASS

A4: identical refusals to 3 (tracking is irrelevant to S and L1).

### 5. A namespace package -- PASS

A5a (`ast/` without `__init__`, holding a text file, in C11's directory): barrier refuses; behind it S refuses (directory, stdlib name, not in inventory). The stdlib `ast` still wins (a regular module beats a namespace portion), so L1 has nothing to report -- S is the check that matters and it fires. A5b (`ast/__init__.pyc`, a SOURCELESS package in C11's directory): barrier; behind it L1 + S. The chain's R61-7 (a namespace package actually imported) reproduces (L1 "is a namespace package inside a campaign code directory").

### 6. A zip/egg import shadow -- PASS

A6a (`shadow.egg` holding `fractions.py`, not on sys.path) and A6b (`fractions.zip`, `x.pth` in the code directory): barrier refuses (non-.py entries); behind it S refuses each by name and kind (a `.pth` in a code directory is inert -- only site directories process `.pth` -- and is refused anyway). An archive can only act if it is ON sys.path; R61-8 (prepended) reproduces: L3 "sys.path holds a repository directory that is not a campaign code directory (shadow.egg)" + L1. A zip reached through `PYTHONPATH` is refused by the PYTHONPATH/L3 checks (but see N7-2 on the timing of those checks).

### 7. A wrong-origin non-contract loaded module -- PASS

`probes` in-process fixtures through the production `verify_loaded_modules(modules=...)`: a module file inside a code directory with a non-contract name (L1 refused), a TRACKED but unbound C11 module (`c11_runs`) actually loaded (L1 "not an approved contract source"), an approved frozen_code file loaded under another module name (L1 "loaded under another module name"), a sourceless loader for an approved path (L1 SOURCELESS_BYTECODE). Exec-root = repository: A7a (untracked `c11x_helper.py`, imported by nothing) -> runner pre-flight refused by `verify_contract` (frozen_paths / frozen_code / code_directories differ) and S; comparator refused at step 3 (loader 0); A7b (a COMMITTED `c11_extra.py` in C11's directory) -> "code_directories differs" + S, comparator refused at step 3. Note: an approved `frozen_code` module (a producer such as `c11r_status`) loaded under its own name at a boundary is ACCEPTED by design (byte-verified, frozen) -- harmless.

### 8. __file__ / __spec__.origin disagreement -- PASS

Fixtures: `__file__` in the stdlib and `spec.origin` elsewhere (L2 "its __file__, __spec__.origin and loader path disagree"); `__file__` in a code directory with origin/loader in the stdlib (L2 + L1). Naturally occurring: my first comparator harness left `__main__.__file__` pointing at the synthetic `c11r_compare.py` while its loader named the driver -- step 12 refused with exactly the L2 message (loader 0). R61-15 (a code-directory `fractions.py` rewriting its own `__file__`) reproduces.

### 9. An out-of-repository symlink -- PASS

A9a (`c11x_link.py` -> a file outside the repository): barrier refuses (symlink); behind it `verify_contract` (frozen_paths/frozen_code) and S ("a symlink resolving OUTSIDE the repository"). A9b (the contract path `c11r_schema.py` replaced by a symlink to IDENTICAL bytes outside): barrier refuses; behind it a TYPED refusal from `verify_contract` ("paths: c11r_schema.py is a symlink resolving OUTSIDE the repository"; no exception -- N6-5 repaired), L1 ("reached through a symlink resolving OUTSIDE", "loaded from another file than <execution root>/..."), S.

### 10. A dangling symlink -- PASS

A10a (non-contract name): barrier; `verify_contract` + S ("a dangling symlink"). A10b (the contract path `c11_common.py` in C11's directory replaced by a dangling symlink): barrier; behind it typed refusals ("code identity differs for ['c11_common.py']", "paths: c11_common.py is a dangling symlink", S) -- the imports that need it fail with ModuleNotFoundError, nothing raises out of the verifiers.

### 11. The approved contract source, normal case (no false refusal) -- PASS

Exec-root = repository, clean synthetic repositories: runner pre-flight [] (authorized), Q4 [] , comparator all twelve steps pass with the stub loader called exactly once (AGREEMENT_INSUFFICIENT on synthetic data), `phase15` COMPARED and the artifact written once; `c11r_compare.py` / `c11r_qualify.py` with no argument pass the barrier and print usage (rc 2). PRIMARY checkout, read-only: `verify_contract` [] (body digest 2ce6fc557566283a618ecca39c328e7736f4551e49b4eed23df979adfe1a9040), `verify_gate` [] (0f282aa081849f4dc593be775daa8ad04c3ebaea57b2520d07dcb9d6f15395d6, guard DENY), `code_dir_shadows` [], `preimport_barrier_problems` []; the three code directories hold only inventory `.py` files and a `__pycache__` whose 20 entries are all `<inventory stem>.cpython-314.pyc`; of those, every cache CPython would accept equals the compilation of its source (`_pyc_matches_source` True for 11, None = stale/ignored for 9, never False). No false refusal is pending in production. (A Finder `.DS_Store` in a code directory is refused, fail-closed -- item 23.)

### 12. An ordinary valid stdlib import, normal case -- PASS

Same runs: every stdlib module the boundary processes load comes from the interpreter (my import survey, `probes/survey_driver.py`: 55 stdlib top-level names requested through the path finders in the runner pre-flight, all resolved in the stdlib); R61-12 reproduces.

### 13. R5's sourceless contract-module .pyc regression -- PASS

A13 (`c11r_certificate.pyc`, compiled from the module plus a marker, in C11's code directory): barrier refuses all three programs; behind it S refuses ("not Python source", "carries the import name of contract module c11r_certificate", not in inventory). The chain's PYC controls reproduce (item 36 run).

### 14. Stale .pyc regression -- PASS

A14: a timestamp cache of `c11r_schema` with other code and a header mtime off by 7 s: CPython ignores it (marker not run) and nothing is refused -- runner pre-flight [], Q4 [], comparator loader 1. Primary checkout: 9 stale caches, correctly ignored (item 11).

### 15. Forged .pyc regression -- PASS under the default interpreter configuration (NOTE N7-1)

A15: forged caches CPython executes (marker ran each time) -- timestamp header matching mtime and size; UNCHECKED hash-based header; CHECKED hash-based header carrying the true source hash -- each refused at the runner pre-flight, at Q4 and at comparator step 12 ("has cached bytecode that is not the compilation of its verified source"), loader 0.
NOTE N7-1 (class b): `_pyc_matches_source` models CPython's acceptance only for `--check-hash-based-pycs default`. `probes/e3_hashpyc.py`: a forged CHECKED hash-based cache of `c11r_schema` with a WRONG source hash, interpreter launched with `--check-hash-based-pycs never`: CPython executes the forged bytecode (marker ran) and the production runner pre-flight returns NO problem (the verifier judges the cache "stale", S admits `c11r_schema.cpython-314.pyc` by name). Under `default` and `always` the cache is not executed. The bound `cache_policy` text ("a cache CPython would accept must equal the compilation of its verified source") is therefore true only for the default mode; the verifier checks PYTHONPATH and `-O` but not this option. It needs a deliberate, non-documented interpreter option at launch (no environment variable sets it) plus a deliberately forged cache, i.e. an operator deviating from the protocol -- within the trust the campaign already places in the operator (limitation 3 lets such an operator hand-write a run anyway). Cheap fix: refuse unless `_imp.check_hash_based_pycs == "default"` (or treat checked caches as accepted when it is `never`).

### 16. The authorization lifecycle -- PASS

`probes/p_life.py` (in-process, production functions on synthetic repositories): authorization before qualification refused ("state is FROZEN; stage authorize requires QUALIFIED", "no qualification artifact"); a fixture qualification refused without `allow_fixture` ("a synthetic fixture is not a qualification"); AUTHORIZED -> pre-flight []; a SECOND authorization after the first refused (history and repository-wide lineage: "holds an authorization (a prior one)"); authorization and GRANT committed in TWO commits refused at pre-flight ("no execution permission GRANT was committed together with the authorization").

### 17. The execution-permission lifecycle -- PASS

Same probe, the runner's own `begin_execution` / `finish_execution`: AUTHORIZED (comparator refuses: "execution permission at HEAD is still the GRANT (ALLOW)"); EXECUTING (pre-flight refuses, comparator refuses); EXECUTED_UNSEALED (both refuse); SEALED after committing exactly the two NEXT_STEPS files (pre-flight refuses a second execution; `phase15` COMPARED, loader 1, writer 1). REVOKED_BEFORE_EXECUTION committed: terminal (pre-flight and comparator refuse); the revocation `git revert`-ed (GRANT back at HEAD): state derives as AUTHORIZED but the pre-flight refuses ("GRANT was not introduced once", foreign permission content, lineage). NEXT_STEPS now prints repository-relative paths (N6-1 repaired; printed text read).

### 18. Deletion / recreation / revert of the authorization -- PASS

Covered by the chain's GS6-GS8 (re-run, item 36, identical results) and by 16d/17f above: a second authorization content, a reverted revocation and a re-introduced GRANT are refused by `protocol_history` ("introduced by N commits" / "not introduced once") and by the repository-wide lineage check.

### 19. A second run: on the authoritative lineage, on a sibling branch, after an interrupted run -- PASS (stated limits reproduced as stated)

19a trunk after the seal: refused (history + lineage). 19b SIBLING branch forked at the authorization commit while the first seal sits on trunk: refused by the new lineage check (R6's 5g repaired). 19c the first seal's branch DELETED (reflog entries remain): still refused. 19e trunk reset before the seal, a TAG keeping the first run: refused. 19f after a committed comparison: refused. 20c an interrupted run whose EXECUTION_STARTED record was put in `git stash` (GRANT back on disk): refused (refs/stash is walked). STATED LIMITS, reproduced and NOT claimed (LIFECYCLE_SCOPE): 19d the first seal made unreachable (branch deleted, `reflog expire --expire=now --all`, `gc --prune=now`): the pre-flight passes; 20d the stash DROPPED (an unreachable object): passes; 20e interrupted, uncommitted, GRANT restored with `git checkout`: passes (LG3). All three require deliberately destroying the repository's own record; the operator instruction for the interrupted case (INTERRUPTED_EXECUTION) is printed by `begin_execution` before any science (observed).

### 20. An interrupted run -- PASS

EXECUTION_STARTED committed -> ABANDONED (terminal): pre-flight and comparator refuse; the GRANT re-committed by `git revert` afterwards: refused. The uncommitted cases are item 19's stated limits.

### 21. Comparison under ALLOW -- PASS

Runs artifact sealed with the permission restored to the GRANT (only the runs artifact committed): MALFORMED; refused before the loader ("holds the runs artifact without the DENY/EXECUTION_COMPLETED permission record", "still the GRANT (ALLOW)"); loader 0, writer 0, no file.

### 22. Comparison under SEALED / DENY -- PASS

SEALED with DENY/EXECUTION_COMPLETED committed in the sealing commit: all twelve steps pass, loader called exactly once, writer once. Exec-root = repository (`atk_driver.py phase15`): COMPARED, the artifact written once by the synthetic repository's own comparator inside the sanctioned context; no module is imported for the first time after the loader is entered (a finder spy recorded none), so nothing new can be resolved from a code directory after step 12.

### 23. A stray .DS_Store in evidence/runs -- PASS

Refused before the loader ("an unexpected file under a protocol directory on disk"), REFUSED_BEFORE_LOAD, writer 0, no file; after deleting it the SAME seal compares (loader 1): the N6-3 retry rule works. Also refused, fail-closed: `.DS_Store` in `evidence/comparison`, and in the campaign CODE directory (S: "not Python source"; the barrier would refuse the programs too). (d) Finder creates `.DS_Store` when a folder is opened in Finder: an operator note would save a confusing refusal.

### 24. A refused comparison leaves no final result -- PASS

Every refusal in items 16-25 returned REFUSED_BEFORE_LOAD with writer 0 and no file at the output path; `phase15` re-raises only an exception from steps 1-12 (typed by construction) and writes nothing. Chain CMP4/CMP4b (loader entered then failure; write failure) reproduce: POST_LOAD_FAILURE, nothing written. NOTE N7-4 (c): on a pre-load refusal `phase15` prints the typed problems but NOT the computed `N9_VERDICT`; for a refusal whose cause is intrinsic to the sealed run (G8/G10/G19, value trace, statement non-equivalence, INDEPENDENCE_VIOLATION) the printed retry sentence ("once the cause is removed the comparator may be run again") is inapt -- the cause cannot be removed without changing a protocol record -- and nothing records the classification persistently. It cannot mis-classify (the state stays SEALED, nothing claims agreement), but the refusal line should print the verdict class and say when a retry cannot help.

### 25. A stale comparison -- PASS

An untracked file at the output path (planted by a shell): refused at step 2, writer 0 (the stale file untouched); a comparison committed on ANOTHER branch while trunk is clean: refused by the lineage check (new in round 7); a committed comparison on HEAD's history: refused (19f). CF1-CF5b reproduce.

### 26. A required certificate removed -- PASS

`probes/p_cert.py` (re-stamped runs artifacts sealed through `begin_execution` / `finish_execution`, so EXECUTION_COMPLETED is bound to the edited body; comparator with a counting stub loader): F_K removed (Abar left CERTIFIED citing it) and F_D removed -> refused at step 7 "run" ("certificates are [...], expected exactly ['F_D', 'F_H', 'F_K']"), loader 0; R6's N6-4 construction (F_K removed + Abar demoted + citation nulled) -> refused at step 7, loader 0 (it reached the loader in round 6). At emission, `c11r_runs.assemble` without F_K raises ("emit_runs would produce an invalid artifact"). N6-4 repaired.

### 27. A required certificate nulled -- PASS

Abar's citation nulled while CERTIFIED; Abar demoted to NOT_CERTIFIED with the citation nulled and F_K present; tau's `certificate_id` field deleted: each refused at step 7 ("cites None; its frozen citation is 'F_K'", "missing 'certificate_id'"), loader 0.

### 28. Wrong certificate substitution -- PASS

Abar citing F_H (step 7, frozen citation); F_H's content stored under the F_K key (step 12, "value trace: Abar: its certificate proves ['C_T', 'tau'], not 'Abar'"); F_K and F_H contents swapped with ids renamed consistently (step 12, value trace for Abar, C_T and tau); an extra certificate F_X (step 7, exact set); key F_K holding id F_H (step 7); D1 (NOT_IMPLEMENTED) citing F_K (step 7): all refused, loader 0.

### 29. git replace -- PASS

`probes/p_git.py`: a side edit/revert of `c11r_boxdata.py` merged `--no-ff` after the seal: refused at step 2 (history purity). After `git replace --graft <merge> <merge^1>`: an unprotected `git rev-list A..HEAD` sees 4 commits, the campaign 6; still refused. `git replace <edit> <fake>` (a fake commit carrying the parent's tree): refused (the replaced commit's real tree is read).

### 30. Grafts -- PASS

A legacy `info/grafts` file hiding the side branch: refused ("a grafts file rewrites commit parentage").

### 31. A shallow repository -- PASS

A `.git/shallow` boundary at the approved commit: refused ("the repository is shallow").

### 32. Hostile GIT_* variables and a forged commit-graph -- PASS

A valid seal compared with the calling environment carrying GIT_DIR / GIT_WORK_TREE / GIT_INDEX_FILE / GIT_OBJECT_DIRECTORY pointing at ANOTHER repository, GIT_NO_REPLACE_OBJECTS=0, GIT_REPLACE_REF_BASE, GIT_GRAFT_FILE, GIT_CONFIG_PARAMETERS and GIT_CONFIG_COUNT/KEY/VALUE setting core.commitGraph=true, GIT_CEILING_DIRECTORIES, GIT_NAMESPACE: ACCEPTED with loader 1 (every variable dropped; the right repository read). Forged commit-graph (`probes/p_cg.py`): a run sealed on a side branch, merged `-s ours`, the side branch deleted and reflogs expired, a REPOSITORY-LOCAL `core.commitGraph=true`, a graph written and forged (the merge's second parent dropped, trailer re-hashed with the chain's `_forge_commit_graph`): unprotected git sees 4 commits and one parent; the campaign's `--all --reflog` walk sees 5 and finds the runs holder; the pre-flight refuses. The command-scope `core.commitGraph=false` overrides the repository's own setting (N6-6 repaired by construction). The chain's CG1 reproduces. The object database and repository configuration beyond the sanitized settings remain trusted (stated in `c11r_common`).

### 33. Merge topology -- PASS

After a valid seal: side edit/revert of `c11r_contract.py` merged `--no-ff`; `-s ours` merge of an UNREVERTED policy edit (tree identical to trunk); an octopus merge carrying an edit/revert of `c7_gaussian.py` (outside the namespace); an unrelated (orphan) history merged `--allow-unrelated-histories -s ours` (the stated N5-5 policy: every frozen path listed): all refused at step 2 by history purity, loader 0. An unrelated note merged `--no-ff`: accepted, loader 1. MHT 15/15 reproduces.

### 34. Complete history -- PASS

A linear edit + restore of the policy before qualification: authorization refused (history purity). An unrelated commit after the seal: accepted (loader 1). Every commit reachable from any ref/reflog/HEAD of the PRIMARY repository (725) holds no qualification, runs, comparison, authorization or execution-permission path (one `cat-file --batch-check` per commit, read-only).

### 35. Policy-byte mutation -- PASS

Policy edited on disk with the stored `sha256` kept: pre-flight refuses (artifact identity, configuration, stored field != body digest). Swapped AFTER a passing pre-flight: `load_verified_inputs` refuses (recomputed digest differs, stored field); re-stamped consistently: refused (digest differs from the pre-flight's, configuration differs). PB1-PB3 reproduce.

### 36. Q1-Q18 -- PASS

`probes/p_qual.py` against the production builder/verifier: valid fixture []; Q7 missing, Q3 duplicated, unknown Q19, status SKIP, a FAIL item, a renamed item, an item bound to another qualifier, a forged PASS class over a FAIL item, another host, a stale stored `sha256`, a fixture without `allow_fixture`, a qualification built for another approved commit: each refused with its specific reason. Root of trust: a 12-hex abbreviation, `HEAD` and a branch name refused; the full id accepted. `c11r_qualify.main` (read) emits Q1..Q18 once each, Q1 (`chain_roots` -> `verify_contract`) BEFORE Q4, Q17 requires lifecycle FROZEN; Q4 = `verify_loaded_modules(role="qualifier")` + `code_dir_shadows`. The qualification remains an attestation (QUALIFICATION_PROVES), as accepted. `python3 -B code/c11r_qualify.py --self-test` in the PRIMARY checkout: 8/8 PASS, wrote nothing (the `__pycache__` modification times are unchanged).

### 37. Loader ordering -- PASS

In every comparison of this review (items 11-35: 60+ comparator calls, in-process and exec-root = repository) the stub loader was called exactly once when all twelve steps passed and never otherwise. An audit hook in the harness recorded every Python-level open during four comparisons (valid, G8, G10, G19): code files and exactly the allowlisted artifacts (authorization, contract, permission, policy, gate, cost, qualification, runs, statement table, the policy's declared validation input) -- never the quarantine, the registry or review prose. In the exec-root = repository `phase15` run a finder spy saw NO module imported for the first time after the loader was entered. The regenerated chain artifact: `quarantine_access_ordering` 53 comparator refusals with the loader never called, 12 accepts.

### 38. G8 / G10 / G19 / G21 -- PASS

`p_cert.py`: D1 reported NOT_CERTIFIED -> refused at "G8"; F_D POINTWISE_INFEASIBLE yet sent -> "G10"; certificates at another depth -> "G19" (and the chain's internally consistent G19 control reproduces); loader 0 each. G21 (the lifecycle): items 16-22.

### 39. Detector wrapper cases -- PASS (limits as documented)

Detector revision 4, detection logic unchanged since round 6 (the round-7 diff of `c11r_procs.py` touches only `main()`'s artifact text: two misses added to `not_checked`, `known_false_positives` added). Live children in a neutral scratch directory classified by the production `campaign_workers()` (`probes/p_det.py`; the wrapper's campaign import sits under `if False:`): flagged -- `-m cProfile -o /dev/null wrap.py`, `-m trace --count -C <dir> wrap.py`, `wrap.py`; NOT flagged, and now listed in `not_checked` -- a wrapper without `.py` suffix, and `--check-hash-based-pycs default wrap.py`; a neutral script not flagged. Concurrency gate only; not load-bearing.

### 40. Open-guard scope and the accuracy of its claims -- PASS as defence in depth

Dummy files only (a planted `C11R_ORIGINAL_MAGNITUDES.json` in a scratch directory, its inode registered with the production `protect_inode`; nothing read): refused -- `open(str)`, `io.FileIO(Path)`, `os.open(bytes)`, a symlink with an innocent name, a hard link renamed innocently, entering the sanctioned context as a non-reader; OPENED -- a COPY under an innocent name. The round-7 comment in `c11r_common` now states exactly that (N6-7 repaired); the firewall's regenerated runtime-guard controls are ALL_PASS with the two demonstrated residuals, and its `scope` text and the gate's G16 are accurate. Not the trust boundary; no production path relies on it.

### 41. D5/P32 unchanged -- PASS

Policy ebf08c0f -> 63402106 -> dbd6cd89: `chosen` {depth 5, panels 32}, `rule` (sha of the rule object identical), calibration unchanged; the cost artifact was re-measured, so the candidate estimates and `chosen_cap_fraction_with_safety_factor` changed (0.7334 -> 0.732 -> 0.7121). Feasible set unchanged {D4/P32, D4/P64, D4/P128, D5/P32} (0.1962, 0.3964, 0.808, 0.7121); D5/P64 at 1.4614, not borderline. The qualifier self-test's `rederive_honest` re-derives D5/P32 from the committed cost artifact (item 36). Contract and gate regenerate BYTE-IDENTICALLY in clone C (2ce6fc55..., 0f282aa0...).

### 42. Cap unchanged -- PASS

10800 s / 8192 MB in `c11r_policy.py` (`CAP_SECONDS`, `CAP_RSS_MB`), the policy artifact and the contract's `configuration`; `rederive_rejects_a_raised_cap` passes.

### 43. Safety factor unchanged -- PASS

`SAFETY_FACTOR = F(3, 2)`; policy `safety_factor` "3/2"; bound in the contract's configuration.

### 44. Scientific validation -- PASS

`c11r_validate.py` re-run in clone C (NT only, 471 s, run WITHOUT `PYTHONINTMAXSTRDIGITS`, which only the regeneration driver sets): VALIDATION_CLASS PASS, 17/17, failed []; the regenerated artifact differs from the committed one only in `seconds` and `sha256`. The numerical modules (`c11r_idrift`, `c11r_boxdata`, `c11r_equiv`, `c11r_validate`, `c11r_mutations`, `c11r_table`) are untouched by round 7; no file outside the namespace changed since 440bcd91.

### 45. Certificate forgeries -- PASS

Mutation suite re-run (item 46): 16 adversarial certificate controls, none missed; comparator self-test 10/10, equivalence self-test 20/20; items 26-28 above. Consistent forgeries remain detectable only by re-execution (stated limitation 3, accepted).

### 46. Mutations -- PASS

`c11r_mutations.py` re-run in clone C (59 s): MUTATION_CLASS PASS, 42/42 detected, not detected [], separation control passes. The regenerated artifact differs from the committed one only in the input hash of the (regenerated) chain artifact.

### 47. Leak / firewall semantics -- PASS

`c11r_firewall.py` regenerates BYTE-IDENTICALLY (FIREWALL_CLASS PASS, structural offenders [], runtime-guard controls ALL_PASS, claim DEFENSE_IN_DEPTH_HEURISTIC). `c11r_table.py --leak-check` in clone C: 41 files, 0 matches, LEAK_CLASS PASS; the regenerated artifact differs only in the commit-message disclosure (now 15 commits since C11, dbd6cd89 included, 0 matches) and input hashes. My own count-only scan (`probes/leakscan.py`: imports no campaign module; 196 textual forms of the six originals built in memory -- exact rational, float repr, the stored float field, 2-12 dp half-even/half-up/truncated with and without leading zero, 3-12 significant figures, scientific; prints counts and form TYPES only; in-memory positive and negative controls; the R1 review prose, counted only, hits): the 39 tracked namespace files outside `quarantine/` and `review/`, the dbd6cd89 commit message, this review and every probe and log file of mine -> 0 hits at 6 or more characters and 0 coincidences at 4-5 characters.

### 48. No target science -- PASS

The only evaluation on the cell-306 block is `c11r_runs.main` (`I.Blk(e_lo, e_hi)`, line 281), never run; every other `Blk(` is NT or e = 5/2 (read). My harnesses used `synthetic_certs` (no certifier), the stub loader, and launched `c11r_runs.py` only where its barrier refused. No kernel, certifier, selector, screen or bound on any open-cell block.

### 49. No target values -- PASS

Item 47. No original magnitude, rounded/truncated form or ratio to one appears in this review or in any file I wrote; the quarantine was read only by the count-only scanner.

### 50. Historical reviews, verdicts, main and r5 preserved -- PASS

R1-R6: blob at HEAD == blob at the preserving commit == working-tree `hash-object` (R1 8a445008 @ 6d7cd546, R2 af431bc0 @ 6ae05833, R3 19e276e4 @ f6c737c3, R4 b2afdb49 @ 5c5203c1, R5 43c5f4c8 @ ebf08c0f, R6 b61e6ac8 @ 63402106); each file is touched by exactly its preserving commit (`git log --all --full-history`); R6 is byte-identical to its reviewer's scratch original. Errata: E1-E48 preserved, E49-E55 and `review_6_findings_disposition` added (read). `git diff --name-only 440bcd91 dbd6cd89` outside the namespace: empty; no merge and no commit touching anything outside the namespace in the range. B0 (committed artifact, 14/14): B0_04 "C11 verdict is EXECUTION_INVALID and is not rewritten as success", B0_05 N9 OPEN, B0_06 r5 authoritative, B0_07 open set {306..309}, B0_08 no r6, B0_09 remote main, B0_11 C2-C11 integrity, B0_14 label now derived from the detector label (N6-9 repaired). Gate: guard DENY, `predecessor_state_preserved` = {C11 EXECUTION_INVALID, C2-C10 immutable, N9 OPEN, "r5 authoritative; open m=5 cells {306, 307, 308, 309}; K5 PARTIAL"}. `K5_COVERAGE_MAP_R5.json` object f978eeb6 at 440bcd91 and HEAD; no `K5_COVERAGE_MAP_R6` in any ref's history or on disk. Local refs (no fetch): `refs/heads/main` c123b9bb8f15d17650545b3fce4aca8a6b61093b, `refs/remotes/origin/main` 1cb453826313c189f0bdafd5b84120c1edb74da9, equal to B0's `LOCAL_MAIN_REF` / `REMOTE_MAIN_REF`; no remote-tracking branch contains dbd6cd89. `c11r_status.py --verify-only` on a clean clone: CONSISTENT, 15 artifacts fresh. Chain re-run in clone C: 175/175, same ids in the same order, `pass`/`expected`/`stub_loader_calls`/`refused_at_step`/`stage`/`required` identical for every control; masked problem texts differ only in two temp-path strings (R61-P, TP4).

---

## Reviewed identity (for any later auditor)

At dbd6cd89: contract `C11R_CONTRACT/4`, body digest 2ce6fc557566283a618ecca39c328e7736f4551e49b4eed23df979adfe1a9040 (18 code files, 8 `frozen_code` files, 43 frozen paths, inventories of 23 / 8 / 10 files for the campaign's, C11's and C7's code directories); gate 0f282aa081849f4dc593be775daa8ad04c3ebaea57b2520d07dcb9d6f15395d6 (guard DENY). Both regenerate byte-identically in a scratch clone and verify with no problem against the PRIMARY checkout (read-only), where `code_dir_shadows` and `preimport_barrier_problems` also return none.

## Summary

Round 7 repairs R6-1 as it was stated, and does so in depth. Location-keyed L1 refuses any module loaded from a campaign code directory that is not an approved, byte-verified source, whatever its name. Every stdlib-named shadow I planted (sourceless `.pyc`, `.py` source, committed or untracked package, namespace package, sourceless package, archive, extension name, symlinks inside/outside/dangling), in the campaign's, C11's and C7's code directories, is refused BEFORE it can execute by the boundary programs' pre-import barrier. Behind the barrier the same material is still refused by L1 and by the exact inventory (S). For any extra `.py`, the recomputed contract (`frozen_paths` / `frozen_code` / `code_directories` / the closure) refuses as well. That contract check runs at every boundary before the module check (runner: authorization before modules; comparator: step 3 before step 12; qualifier: Q1 before Q4).

The clean case gives no false refusal, in synthetic repositories whose code is the executing code and in the primary checkout (read-only). The other round-7 repairs also behave as claimed:
- repository-wide lineage: sibling branches, tags, stashes and deleted-but-reflogged branches are refused;
- the comparison transaction: a refusal writes nothing, the retry after a `.DS_Store` works, and POST_LOAD_FAILURE writes nothing;
- the exact certificate set and frozen citations: the N6-4 construction is now refused at the run step and at emission;
- typed path refusals, and `core.commitGraph=false`: a forged graph plus a repository-local `core.commitGraph=true` hides a merged run from plain git, but not from the campaign.

Every regression surface reproduces: chain 175/175, validation 17/17, mutations 42/42, firewall/contract/gate byte-identical, leak 0, D5/P32 / 10800 s / 3/2, reviews, predecessors, r5, no r6, main refs, and no protocol artifact anywhere in 725 reachable commits.

What remains are limits on defence in depth and wording. None of them lets a target run be contaminated, mis-stated, mis-identified or mis-classified under the documented invocation with a non-hostile interpreter environment. Each needs a deliberately non-default interpreter option, a hostile environment variable, or deliberately self-concealing code, all of which lie within the stated not-covered class or the trust the campaign already places in the operator (limitation 3). They are cheap to fix now and impossible after the freeze, so I recommend fixing N7-1 to N7-3 before freezing if another pre-result round happens. On their own they do not block.

## Load-bearing BLOCKERS

None.

## Non-blocking observations

- **N7-1 (b, with a (c) wording part; item 15). `_pyc_matches_source` models the loader only for `--check-hash-based-pycs default`.** Reproduce with `probes/e3_hashpyc.py`: put a forged CHECKED hash-based cache of `c11r_schema` with a wrong source hash in the code directory's `__pycache__`, then launch the interpreter with `--check-hash-based-pycs never`. The forged bytecode executes, and the production runner pre-flight reports no problem, because the verifier treats the cache as stale and S admits it by name. Under `default` and `always` the cache is not executed. The bound `cache_policy` sentence is therefore true only in the default mode. There is no environment variable for this option: the launcher must pass it. Fix: refuse unless `_imp.check_hash_based_pycs == "default"`, in `verify_loaded_modules` and in the barrier (`_imp` is built in).
- **N7-2 (b). The interpreter environment is not bound at program start.** The barrier checks only the directories. `PYTHONPATH` is checked only after the imports it redirects have run, and `PYTHONCASEOK`, `PYTHONPYCACHEPREFIX` and `PYTHONHOME` are not checked at all. Reproduced:
  - `e2_caseok.py`: with `PYTHONCASEOK=1`, a case-variant `Fractions.py` passes the barrier and runs at program start. A plain shadow is refused by L1, S and `verify_contract`. A shadow that deletes its file and rewrites its metadata leaves the pre-flight green.
  - `e5.py`: `PYTHONPATH` gives the same pattern. A plain shadow is refused ("PYTHONPATH is set", L3). A concealing shadow that also removes the variable leaves everything green.
  - `e3_hashpyc.py` / E4: `PYTHONPYCACHEPREFIX` plus a forged timestamp cache of the STANDARD LIBRARY's `fractions` gives a green pre-flight with no concealment and nothing in the repository. The standard library is not verified at all; the stated scope covers code directories only.

  The concealing variants belong to the stated not-covered class ("a module that rewrites its own metadata or deletes its file"). Fix: the barrier refuses `PYTHONPATH`, `PYTHONCASEOK`, `PYTHONPYCACHEPREFIX` / `sys.pycache_prefix`, `PYTHONHOME` and a non-default hash mode, and compares case-folded names. The runs artifact should record `sys.orig_argv` and these settings. `not_covered` should name the interpreter and its environment explicitly.
- **N7-3 (c/d; E1, `e1_sysconfigdata.py`, `e1b.py`). The barrier's claim is broader than its rule.** `_sysconfigdata__darwin_darwin` is a standard-library module whose name is not in `sys.stdlib_module_names`, so the barrier admits a `.py` of that name. `sysconfig` first imports it INSIDE `verify_loaded_modules` (`_import_path_problems`), after the `sys.modules` snapshot is taken, so L1 never examines it. It is caught by `verify_contract` (which runs earlier at every boundary; at the comparator, before the shadow even executes) and by S. The following statements are overstated:
  - the barrier docstring: "anything a standard-library import could resolve to";
  - L3's "(L1), (S) and (B) cover";
  - G20's "every module loaded from a campaign code directory".

  Fix: take the snapshot after `_import_path_problems` (or import `sysconfig` at module load), and word the barrier as covering `sys.stdlib_module_names`.
- **N7-4 (c; item 24). The refusal message loses the verdict class.** On a pre-load refusal `phase15` prints the problems but not the computed `N9_VERDICT`, so an INDEPENDENCE_VIOLATION or EXECUTION_INVALID class is never printed or recorded. Its retry sentence ("once the cause is removed the comparator may be run again") is also inapt when the cause is intrinsic to the sealed run: G8/G10/G19, the value trace, statement non-equivalence, independence. This cannot cause a mis-classification: the state stays SEALED and nothing claims agreement. Print the class and say when a retry cannot help.
- **N7-5 (d; N6-5). Not every step-1-12 failure is a typed refusal.** A pathologically nested runs artifact (`[[[[...`) makes `read_runs` raise `RecursionError`, which is neither caught there nor in TYPED_ERRORS, out of `execute_comparison` and `phase15`. This is fail-closed: loader 0, nothing written, no traceback leak of values. It still contradicts "no path through steps 1-12 raises". Catch `RecursionError` in `read_runs`.
- **N7-6 (d; item 23). A Finder `.DS_Store` causes a fail-closed refusal.** In a code directory the barrier and S refuse it; in a protocol directory `protocol_history` refuses it. Worth one operator note.
- **N7-7 (b; items 19-20). The stated limits reproduce exactly as stated (LIFECYCLE_SCOPE), and are not claimed:**
  - a dropped stash;
  - a first seal made unreachable (branch deleted, reflogs expired, `gc`);
  - an interrupted, uncommitted execution with the GRANT restored by `git checkout`.
- **N7-8 (d). The chain controls do not cover a non-default interpreter.** Every R61 and IMP control runs with a default environment (PYTHONPATH removed) and default interpreter options, so none of them covers N7-1 or N7-2.
- **N7-9 (d). An approved `frozen_code` module can be loaded at a boundary.** A producer such as `c11r_status` loaded under its own name is ACCEPTED by L1 by design (it is byte-verified and frozen). This is harmless; it is recorded so the "approved source" set is understood as including producers.

## What is right and should be kept

- location-keyed L1 with origin agreement (L2) and import-path precedence (L3);
- an exact frozen inventory (S), backed by a recomputed contract that sees every extra `.py`, and a verbatim, checked barrier;
- a repository-wide lineage check over all refs, stashes and reflogs;
- a one-shot comparison transaction;
- an exact certificate set enforced at emission and at the run step;
- typed path shapes;
- a sanitized git layer that reads the real commits.

None of the accepted round-1..6 findings needed reopening.

DISPOSITION: READY_TO_FREEZE
