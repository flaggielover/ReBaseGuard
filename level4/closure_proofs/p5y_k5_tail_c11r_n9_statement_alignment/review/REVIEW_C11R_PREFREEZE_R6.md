# C11R pre-freeze review, round 6 (independent)

- Reviewed commit: cc93e470123f217ea438bafd8a1eb2cb502a21dc (branch p5y-k5-tail-c11r-n9-statement-alignment, worktree /Users/suzhe/ReBaseGuard-k5c11r; local only)
- Date: 2026-09-24 (host clock at start: 2026-09-24 05:46 UTC)
- Reviewer: new independent reviewer (no involvement in C11R rounds 1-5; R1-R5 read as history only)
- Precondition: HEAD == cc93e470123f217ea438bafd8a1eb2cb502a21dc and `git status --porcelain` empty -- VERIFIED at the start of the review.
- Numerics policy: no kernel, certifier, selector, screen or bound evaluated on any open-cell drift block; numerics only on NT = [5/2, 5/2 + 108337/1250000] or e = 5/2. No original cell-306 magnitude, rounded/truncated form or ratio to one appears in this file; the quarantine is referred to by path and field only.
- Writes: only in scratch clones under .../scratchpad/r6/work/ (`git clone --no-local`, checked out at cc93e470) and in throwaway synthetic repositories under .../scratchpad/r6/. The primary checkout was only read.

(Written incrementally. Status: COMPLETE -- all 50 required attacks reached.)

## Method

- Scratch clones (each `git clone --no-local` of the worktree, checked out at cc93e470): `work/cloneA` (the code my harnesses import; `c11r_validate.py` and `c11r_status.py --verify-only` re-run there), `work/cloneB` (the repository under test, on throwaway `r6_*` branches), `work/cloneC` (producers re-run there: `c11r_chain.py`, `c11r_contract.py`, `c11r_gate.py`, `c11r_firewall.py`, `c11r_mutations.py`, `c11r_table.py --leak-check`; reset to cc93e470 and clean afterwards).
- Not run anywhere: `c11r_runs.py`, `c11r_compare.py --approved-commit`, `c11r_qualify.py --approved-commit`, the extraction `c11r_table.py` (without `--leak-check`). In the primary checkout only `python3 -B code/c11r_qualify.py --self-test` and read-only `git`/JSON inspection (`python3 -B -c`, no campaign module imported).
- My own harnesses are in `.../scratchpad/r6/probes/` (they call the production functions of c11r_contract, c11r_runs, c11r_compare, c11r_qualify directly; fixture qualification/authorization only; a counting stub loader; `c11r_compare.synthetic_certs`, no certifier runs).

## Attacks

### 1. R5-1 valid lifecycle, NEXT_STEPS followed literally -- PASS (two NOTES)

How: `probes/p_life.py`, `probes/p_cmpfile.py` (clone B, branch `r6_life_valid` / `r6_cmp_valid`, approved commit A = cc93e470 itself). Production calls only: `c11r_qualify.emit_qualification` (fixture items) -> commit; `c11r_contract.build_authorization(fixture=True)` -> `write_record` of the authorization AND the GRANT -> one commit; `c11r_runs.preflight` (no problem) -> `load_verified_inputs` (no problem) -> `begin_execution` -> `assemble` on `synthetic_certs` + `C.evidence_body(producer=c11r_runs.py)` -> `finish_execution`; then NEXT_STEPS[0] literally (`git add` of exactly `evidence/runs/C11R_RUNS.json` and `config/C11R_EXECUTION_PERMISSION.json`, one commit); the authorization untouched (NEXT_STEPS[1]); `execute_comparison` with a counting stub loader.
Finding: derived states FROZEN -> QUALIFIED -> AUTHORIZED -> EXECUTING -> EXECUTED_UNSEALED -> SEALED, each a transition of `LIFECYCLE`; at comparison `lifecycle` reports execution permission DENY, no problem; the comparator reaches the loader exactly once (AGREEMENT_INSUFFICIENT on synthetic data, `git status` clean). Then `write_comparison` (in a subprocess that makes `__main__` resolve to clone A's `c11r_compare.py` -- the reader residual the chain's CF5b also uses; a synthetic payload, no magnitude) writes the output exclusively; state is MALFORMED while it is uncommitted and COMPARED once committed; a second comparison is refused at step 2 (loader 0) and a second write is refused ("a file already exists"). The R5-1 construction is gone.
NOTES: (a) NEXT_STEPS names the two files by NAMESPACE-relative path (`evidence/runs/...`), not repository-relative; harmless (a wrong `git add` fails loudly) but worth saying. (b) NEXT_STEPS[2] prints "nothing re-enables execution under this approved commit", which is not true outside HEAD's history (item 5, 5g): the contract/runner/policy docstrings state the limit correctly, the printed operator message does not (N6-2).

### 2. DENY after execution with the authorization preserved -- PASS

`p_life2.py` 2: after the seal the state is SEALED, permission DENY (EXECUTION_COMPLETED), the authorization present and unchanged, comparison accepted (loader 1). Variants refused at step 2 with loader 0: an EXTRA DENY record (REVOKED_BEFORE_EXECUTION) committed after the seal ("holds an execution permission other than the GRANT and the final record", MALFORMED); the permission file deleted after the seal, uncommitted (MALFORMED) and committed ("holds the runs artifact without the DENY/EXECUTION_COMPLETED record").

### 3. Delete the authorization -- PASS

`p_life2.py` 3: deletion uncommitted and committed are both refused at step 1 ("no authorization artifact") with the history/lifecycle problems listed too; loader 0.

### 4. Delete / recreate the authorization -- PASS

`git revert` of the committed deletion: refused ("the authorization artifact was introduced by 2 commits", GRANT not introduced once, EXECUTION_COMPLETED "does not end the committed GRANT"), loader 0. The same content re-serialised (other bytes) and committed: refused (foreign authorization content). Deletion restored from git before any commit leaves no trace and is (correctly) accepted -- nothing changed. The chain controls GS6-GS8 reproduce.

### 5. A second execution after the seal (and after an interrupted execution) -- PASS for HEAD's history; NOTE

`p_life2.py` 5: after the seal the pre-flight refuses (SEALED != AUTHORIZED, "holds a runs artifact (a prior execution)", "a runs artifact already exists"); restoring the GRANT on disk after the seal: MALFORMED, refused. Interrupted execution (EXECUTION_STARTED on disk): EXECUTING, refused; committed (ABANDONED): refused, and re-committing the GRANT by `git revert` afterwards is refused ("GRANT was not introduced once"). Two stated-limit reproductions (NOTE N6-2): (5d) after an interrupted execution the operator can `git checkout` the GRANT back (the uncommitted EXECUTION_STARTED leaves no trace) and the pre-flight passes again; (5g) a second execution on a SIBLING branch forked at the authorization commit, while the first seal still sits on another branch: pre-flight passes, the second seal is compared with the loader called, although `c11r_contract.protocol_artifacts_anywhere` (already in the module, `rev-list --all --reflog`) lists the other runs content. Both are within the stated limit ("a run ... on an unmerged branch, or never committed at all is invisible"), and a retry of deterministic frozen code under a frozen configuration can only differ through the wall-clock cap; but the cheap `--all --reflog` check is not used at the runner's pre-flight or at the comparator, and NEXT_STEPS overstates.

### 6. Comparison under execution permission DENY; refusal under ALLOW -- PASS

DENY: item 2. ALLOW: the run sealed with the permission still the GRANT (only the runs artifact committed): refused at step 2 ("execution permission at HEAD is still the GRANT (ALLOW)"; MALFORMED; lifecycle `execution_permission` ALLOW), loader 0. A re-stamped EXECUTION_COMPLETED carrying `execution_permission: ALLOW`: refused (typed rule); EXECUTION_COMPLETED bound to another runs digest: refused; the permission committed in a separate commit after the runs artifact: refused ("not introduced in the sealing commit"). No production boundary except the runner's pre-flight accepts ALLOW (`STAGE_STATE`).

### 7. A sourceless .pyc shadow -- PASS for contract import names; DEFECT for any other import name (BLOCKER R6-1)

How: `probes/p_imp.py` -- a separate process whose execution root IS clone B (code imported from clone B, `sys.path[0]` = clone B's code directory, as when `c11r_runs.py` runs as a script), fixture-authorized branch, production `c11r_runs.preflight`, `verify_loaded_modules(role="runner")`, `code_dir_shadows`.
- R5's own construction (`c11r_certificate.pyc`, compiled from the module plus a marker, in C11's code directory): the module IS loaded from the shadow and refused twice -- "is SOURCELESS_BYTECODE (SourcelessFileLoader ...)" and "c11r_certificate.pyc in .../code carries the import name of contract module c11r_certificate". The same `.pyc` beside its own source (where the `.py` wins) is not loaded but still refused statically. R5-2 as stated is repaired.
- NEW: the repair is keyed on CONTRACT import names only. `probes/p_stdshadow.py` / `p_stdshadow_cmp.py`: a sourceless `fractions.pyc` (the interpreter's own `fractions.py` plus one marker line, `py_compile`) in the campaign's code directory, and a sourceless `ast.pyc` in C11's code directory. Both are git-ignored (`.gitignore:33:*.py[cod]`, `git status --porcelain` empty). The runner's module-level `from fractions import Fraction` loads the shadow (sys.path[0] is the campaign's code directory); `ast` is first imported lazily by `c11r_common.code_closure` INSIDE `verify_contract` (C11's code directory is ahead of the standard library by then). Result: the production runner pre-flight returns NO problem, `verify_loaded_modules` [] (12 modules checked, all 11 required present), `code_dir_shadows` [], while `sys.modules["fractions"].__file__` is the shadow and `c11r_runs.F`, `c11r_idrift.F` -- the rational arithmetic of every certifier, reconstruction and guard -- are the shadow's class. Committed after A (`git add -f`), identical result: the file is not a frozen path and not in the recomputed closure. The comparator (process with its execution root = clone A carrying the same shadows, repository under test = clone B with a sealed synthetic run, NO spoofing): all twelve steps pass, step 12 lists no problem, the loader is called, and `classify_numeric` (the numerical AGREES/STRONGER/INSUFFICIENT decision) runs on the shadow's `Fraction`. A stdlib-named PACKAGE (`code/fractions/__init__.py`) is refused only incidentally while untracked ("untracked Python source") and passes once committed after A. See BLOCKERS, R6-1.

### 8. A transitive sourceless .pyc -- PASS (contract names)

`c7_gaussian` as a sourceless PACKAGE (`c7_gaussian/__init__.pyc`) in C7's own code directory -- the only place that can precede `c7_gaussian.py`, because a package wins in its own directory: loaded, refused ("c7_gaussian.py ... is SOURCELESS_BYTECODE ... origin __init__.pyc" and the static name check). `c11_common.pyc` in the campaign directory: refused statically. The chain's PYC6 reproduces. (The non-contract-name gap of item 7 applies transitively as well: `ast.pyc` above is reached only through `c11r_common`.)

### 9. A stale, ignored .pyc -- PASS

A timestamp cache in `__pycache__` for `c11r_schema` with a different code object and a header mtime off by 7 s: CPython ignores it (marker not executed) and no refusal is raised. In the PRIMARY checkout (read-only, `CT._pyc_matches_source` imported from clone A): of the 20 caches present, 11 are accepted-by-the-loader AND equal to the compilation of their source, 9 are stale and ignored; none is accepted-but-different, and the three code directories hold nothing but `__pycache__` besides tracked `.py` files -- no false refusal is pending in production.

### 10. A forged, accepted .pyc -- PASS

Forged `__pycache__` entries CPython executes (marker ran each time), all refused ("has cached bytecode that is not the compilation of its verified source"): timestamp header with matching mtime and size; UNCHECKED hash-based header with an arbitrary hash; CHECKED hash-based header carrying the true source hash.

### 11. Wrong-origin module -- PASS (one NOTE)

Refused: an identical `.py` copy of `c11r_certificate` in C11's directory, untracked ("loaded from another file", "carries the import name", "untracked Python source") and committed after A (first two); a package directory `c11r_schema/` in C11's directory (static); a zip earlier on sys.path ("is ZIP (zipimporter)"); a `.py` shadow that rewrites its own `__file__` to the contract path (origin/loader path disagree: "loaded from another file"); IMP1-IMP9 reproduce. NOTE (N6-5): the contract path itself replaced by a symlink to an identical file OUTSIDE the repository makes `c11r_common._rel` raise `ValueError` inside `verify_contract` (the pre-flight crashes instead of returning a typed refusal). Fail-closed (nothing runs, no loader), but it is an exception, not a refusal record; a symlink to a file inside the repository is refused normally.

### 12. A required load-bearing module absent -- PASS

A process that imports only `c11r_contract` and checks with role "runner": seven "is required at the runner boundary but is not loaded" problems. Complete runner/comparator/qualifier processes: no problem (the import-time closures are present). PYC10 reproduces.

### 13. An uncommitted comparison file -- PASS

`p_cmpfile.py` 13: a file planted at the output path (by a shell, so no campaign process opens a protected name) -> step 2 "a comparison file already exists ... not committed", loader 0; the writer also refuses. CF1 reproduces.

### 14. A stale comparison file (earlier attempt, modified, symlink) -- PASS

Refused at step 2, loader 0: an earlier comparison committed and then removed ("holds a comparison artifact (a prior comparison)"); a committed comparison modified on disk; a dangling symlink at the output path ("the comparison path is a symlink"; the writer refuses too); the whole `evidence/comparison` DIRECTORY replaced by a symlink to an empty directory outside the repository ("an unexpected file under a protocol directory on disk"); another file name in that directory. CF2-CF5b reproduce.

### 15. Policy bytes changed with the stored hash unchanged -- PASS

`p_hist.py` 15: edited on disk with the stored `sha256` kept -> pre-flight refuses (contract artifact identity, stored field != body digest, tree identity). Swapped AFTER a passing pre-flight: `load_verified_inputs` refuses (recomputed digest differs; stored field != recomputation; configuration differs); the same swap with a consistently re-stamped `sha256`: refused. Same body, other bytes (re-serialised): `load_verified_inputs` accepts (the body the run uses IS the frozen one) and the pre-flight refuses on tree identity. PB1-PB3 reproduce.

### 16. git replace --graft hiding a frozen edit -- PASS

`p_hist.py` 16 (a side branch edits and reverts `c11r_policy.py`, merged `--no-ff` after the seal): refused before and after `git replace --graft <merge> <merge^1>`; an unprotected `git rev-list` sees 4 commits, the sanitized one 6. A hostile caller environment (`GIT_NO_REPLACE_OBJECTS=0`, `GIT_GRAFT_FILE`, `GIT_REPLACE_REF_BASE`): refused (the variables are dropped). A legacy `info/grafts` file: refused by `history_integrity` ("a grafts file rewrites commit parentage"). An object replacement of the edit commit (`git replace <edit> <fake>`): refused. I also forged a COMMIT-GRAPH file (`probes/cgraph.py`: the merge's second parent set to GRAPH_PARENT_NONE, trailer re-hashed): plain `rev-list --parents -n1 HEAD` then shows one parent, but the campaign's range walks (`rev-list A..HEAD`, `--parents A..HEAD`) still list the side commits and the comparator refuses (git 2.50.1) -- not a finding; recorded because `history_integrity` does not mention commit-graph files at all (N6-6).

### 17. git replace hiding a run -- PASS

A first run sealed on a side branch after the authorization, discarded there, merged, a second run sealed on the trunk: refused before and after grafting the merge to its first parent ("holds a runs artifact other than the current one", "another run was committed and discarded"), loader 0.

### 18. git replace hiding a seal -- PASS

Sealed, removed (GRANT restored), re-sealed; graft of the removal commit onto the authorization commit (hiding the first seal): refused before and after ("introduced by 2 commits"), loader 0.

### 19. Merge-topology regressions -- PASS

After a valid seal: side edit/revert of `c11r_boxdata.py` merged `--no-ff` -> refused (history purity); `-s ours` merge of an UNREVERTED edit to `c11r_policy.py` (tree identical to the first parent) -> refused by purity only; criss-cross + 3-parent octopus carrying an edit/revert of `c7_gaussian.py` (outside the namespace) -> refused; a branch forked BEFORE A merged after the seal -> refused (the stated N5-5 topology policy, all 43 frozen paths listed); a clean `--no-ff` merge of an unrelated note -> ACCEPTED (loader 1).

### 20. Complete-history regressions -- PASS

A linear edit + restore of `C11R_POLICY.json` before the qualification: authorization and pre-flight refuse (purity). A NEW module file committed in the campaign's code directory after A (execution root = repository, subprocess): authorization refuses ("frozen_paths differs from the recomputed value"; the set is `namespace_code()` of the running tree). An unrelated commit after the seal: accepted. (With execution root != repository -- the chain-control setting -- `namespace_code()` and `closure_paths()` are computed from the RUNNING tree, so that probe passed there; in production they coincide.)

### 21. The cProfile wrapper and the detector -- PASS (NOTE)

`probes/p_detector.py`: live children in a NEUTRAL scratch directory (no campaign token in any argv; the wrapper's campaign import sits under `if False:` so nothing is computed), classified by the production `c11r_procs.campaign_workers()` / `classify` (revision 4). Seen as CAMPAIGN_WRAPPER through the source read: `python3 -B -m cProfile -o /dev/null wrap.py`, `python3 -B -m trace --count -C <dir> wrap.py`, `python3 -B wrap.py` (relative path, cwd resolved through lsof). The N5-9 miss is repaired and the committed live controls now assert that argv ALONE does not flag the wrapper. Not seen (FOREIGN_PYTHON): `-m cProfile -m wrapmod` (module form -- covered by the disclosed "a script argument that does not end in .py" under `-m`), a plain wrapper script WITHOUT a `.py` suffix, and a long option with a value before the script (`--check-hash-based-pycs default wrap.py`: `script_token` takes the option's value as the script). The last two are not in `not_checked` (NOTE N6-8). The detector gates concurrency only; non-blocking.

### 22. Process-detector false positives -- PASS (NOTE)

No false positive for a neutral script, a neutral `-c` payload, the probe itself or its ancestors (self-chain excluded), or a shell naming a script. False POSITIVES (fail-safe: they block the pre-flight, cost and regeneration, they cannot admit anything): an unrelated script given an argument `C11_notes` (the case-insensitive `\bc11r?_` token), and an unrelated script whose source merely mentions the namespace name in a comment (the source-read regex matches the bare namespace string). Liveness only; worth one line in `not_checked`.

### 23. Open-guard scope and the accuracy of its claims -- PASS as defence in depth (NOTE)

`probes/p_guard.py`, PLANTED dummy files only (a dummy `evidence/quarantine/C11R_ORIGINAL_MAGNITUDES.json`, its inode registered with the production `C.protect_inode`, exactly as `c11r_common` registers the real quarantine and registry at import); every attempt opens and closes, nothing is read. Refused: `open(str)`, `io.FileIO(Path)` (N5-10 repaired), `os.open(bytes)`, `Path.read_bytes`, a symlink with an innocent name, a HARD link with an innocent name (inode), the file RENAMED (inode), opening the quarantine directory as a dir fd, `dir_fd(evidence)` + `quarantine/<name>`, chdir + bare name, a symlinked directory, entering the sanctioned context as a non-reader, and with `sys.argv[0]` faked. Not refused, all listed residuals: `dir_fd` + an innocent hard-link name, a hard link of review prose. Not refused and not literally listed: a COPY of the magnitude-bearing file under an innocent name (made by a subprocess -- "subprocess reads" is listed -- and then opened in-process: a new inode). The frozen G16 text and the firewall's `scope` are accurate; `c11r_common`'s comment says "a hard link or a renamed copy of either under an innocent name is refused too" -- a COPY is not (NOTE N6-7, wording only). The guard is not the trust boundary and no production code path relies on it.

### 24. The demotion null-id bypass, and other ways to misreport a disposition -- PASS for N5-11 (NOTE)

`probes/p_demote.py` (re-stamped runs artifacts sealed through the production lifecycle): Abar demoted to NOT_CERTIFIED with its id nulled -> refused at step 12 ("must cite its frozen certificate 'F_K'" and "demoted"), loader 0; the proving certificate additionally RENAMED (`F_Kx`) -> refused ("certificate(s) ['F_Kx'] prove it (demoted)"). NEW (NOTE N6-4): the proving certificate REMOVED from the artifact together with the demotion and the nulled id -> ACCEPTED, loader called, Abar INSUFFICIENT, verdict AGREEMENT_INSUFFICIENT. `validate_runs` does not require the certificate set the frozen runner always emits ({F_K, F_H, F_D}), and the citation rule then allows a null citation ("if it does not exist, the target may cite nothing"). Reachable only through a hand-edited, re-stamped runs artifact with a matching hand-built EXECUTION_COMPLETED (limitation (3), as N5-11 was); one line in the schema closes it.

### 25. Q1-Q18 -- PASS

`probes/p_qual.py` against the production builder/verifier: valid fixture -> []; each of missing (Q7), duplicated (Q3), unknown (Q19), status SKIP, a FAIL item, a renamed item, an item bound to another qualifier, a forged PASS class over a FAIL item, another approved commit, another host, a fixture without `allow_fixture` -> refused with the specific reason. Root of trust: a tag naming A and a 12-hex abbreviation are refused ("not a full 40-hex commit id"); the full id is accepted (N5-7 repaired). `c11r_qualify.main` emits Q1..Q18 once each (read); Q17 requires lifecycle FROZEN; Q4 uses `verify_loaded_modules(role="qualifier")` + `code_dir_shadows` (so it inherits R6-1). The qualification remains an attestation (`QUALIFICATION_PROVES`), as accepted.

### 26. Loader-spy ordering -- PASS

`probes/p_order.py`: in every comparison I ran (items 1-24, over 60 comparator calls) the stub loader was called exactly once when all twelve steps passed and never otherwise. An additional audit hook in the harness process recorded every Python-level open during four comparisons (valid, G8, G10, G19): code files and exactly the allowlisted JSON artifacts, the authorization, the permission record, the qualification and the runs artifact; never the quarantine, the registry or review prose.

### 27. G8 / G10 / G19 -- PASS

Same probe, re-stamped sealed runs: D1 reported NOT_CERTIFIED -> refused at step "G8"; F_D marked POINTWISE_INFEASIBLE yet sent -> refused at "G10"; internally consistent certificates made at depth 6 -> refused at "G19"; loader 0 in each. The comparator evaluates them in production (`pre_numeric` -> `c11r_certificate.evaluate_run`) with the certifier hashes from the contract AT A.

### 28. R3A-R3T regression -- PASS

`code/c11r_chain.py` re-run in scratch clone C (a third `--no-local` clone at cc93e470, exit 0): 123/123 controls pass, R3 25/25, "quarantine-access ordering holds: True", CHAIN_CLASS PASS. Mechanical comparison with the committed artifact: the same 123 ids in the same order; `pass`, `expected`, `stub_loader_calls`, `refused_at_step` and `stage` identical for every control; after masking object ids and temporary paths, every control record is identical (differences confined to `problems` and `files` text carrying synthetic commit ids and temp paths). My own harness independently reproduces R3A-class refusals on merged histories (items 16, 19, 20).

### 29. R4 controls regression -- PASS

Same run: MHT 15/15, LS 8/8, QF 8/8, IMP 11/11, ORD 3/3. Independently: items 16-20 (my topologies) and 25 (qualification).

### 30. R5 controls regression -- PASS

Same run: GS 16/16, PYC 11/11, CF 6/6, PB 3/3, GR 8/8, DM 5/5, AC 4/4; loader never called on the 44 comparator refusals and exactly once on the 12 comparator accepts. Independently reproduced: items 1-6 (GS), 7-12 (PYC/IMP), 13-14 (CF), 15 (PB), 16-18 (GR), 24 (DM), 25 (AC). Coverage caveat: every PYC/IMP control uses a CONTRACT import name, which is exactly why R6-1 is not caught; and DM2 ("a genuinely absent certificate ... citing nothing", ACCEPT) accepts a state the frozen runner never produces, which is the opening N6-4 uses.

### 31. Scientific validation -- PASS

`code/c11r_validate.py` re-run in clone A (NT block only, 567 s): VALIDATION_CLASS PASS, 17/17, failed []; every check record identical to the committed one; only `seconds` and `sha256` differ. `c11r_idrift.py`, `c11r_boxdata.py`, `c11r_equiv.py` are unchanged since round 5 (not in the round-6 diff); `c11_certifier.py`, `c7_gaussian.py` unchanged since 440bcd91 (no file outside the namespace changed).

### 32. Certificate forgeries -- PASS

Mutation suite re-run (item 33): adversarial certificate controls all caught ("adversarial missed: []"); comparator self-test 10/10, equivalence self-test 20/20. Consistent forgeries remain detectable only by re-execution (stated limit (3), accepted). The only new round-6 code in `c11r_certificate.py` is the citation rule (read in full; item 24 exercises it).

### 33. Mutations -- PASS

`code/c11r_mutations.py` re-run in clone C (66 s): MUTATION_CLASS PASS, 42/42 detected, "not detected: []"; separation control (same proposition, different value: statement EQUIVALENT both times, numeric AGREES -> INSUFFICIENT) passes. The regenerated artifact is byte-identical to the committed one (`git status` clean after the run); likewise `c11r_firewall.py` (FIREWALL_CLASS PASS, structural offenders [], runtime-guard controls ALL_PASS, CLAIM DEFENSE_IN_DEPTH_HEURISTIC) regenerates byte-identically.

### 34. Leak check -- PASS (NOTE N6-10)

The campaign's own `c11r_table.py --leak-check` re-run in clone C: 41 files, 0 matches, LEAK_CLASS PASS; the regenerated artifact differs only in the commit-message disclosure (now 13 commits since C11 incl. cc93e470's, 0 matches). My independent count-only scan (`probes/r6_leak_scan.py`: imports no campaign module; 196 textual forms of the six originals -- exact rational, float repr, 2-12 dp half-even/half-up/truncated with and without leading zero, 3-12 significant figures, scientific; forms shorter than 4 characters dropped; prints counts only; positive and negative controls pass; the R1 review prose, counted only, hits): 39 tracked namespace files outside `quarantine/` and `review/`, the cc93e470 commit message, this review and every probe/log file of mine -> 0 hits except four 4-5-character coincidences located (by key path and form TYPE only, never text) in measured wall-clock fields of `C11R_COST.json` and one NT-block field of `C11R_VALIDATION.json`; no form of 6 or more characters hits anywhere. The round-6 quarantine diff, digits masked, changes only provenance hashes.

### 35. D5/P32 unchanged -- PASS

Policy ebf08c0f -> cc93e470: `chosen` {depth 5, panels 32}, `rule`, `calibration`, cap, RSS cap, safety factor unchanged; changed only the cost-derived `candidates` estimates, `chosen_cap_fraction_with_safety_factor` (0.7334 -> 0.732), `cost_model` (the cost artifact was re-measured in round 6: timings only), stage 5's wording (R5-1), provenance and the statement-table digest. Feasible set unchanged {D4/P32, D4/P64, D4/P128, D5/P32} (fractions 0.2016, 0.4057, 0.8271, 0.732; D5/P64 at 1.4956 not borderline). The qualifier self-test's `rederive_honest` re-derives D5/P32 from the committed cost artifact by the frozen rule (item 40). Contract and gate regenerate BYTE-IDENTICALLY in clone C (contract body digest `ccf8b93d64b051a9bfe0fb7828fca0b042f43c9fd109b92062e8c5704bc1b5ae`, gate `631dcf06d5de1ae0afac8de850378eb8204c11f9c97bb9cb6e46a9ac68266484`, gate bound to that contract).

### 36. Cap unchanged -- PASS

10800 s / 8192 MB / SF 3/2 in `c11r_policy.py` (`CAP_SECONDS`, `CAP_RSS_MB`, `SAFETY_FACTOR`), the policy artifact and the contract's `configuration`; the qualifier self-test's `rederive_rejects_a_raised_cap` passes.

### 37. No target science -- PASS

The only evaluation on the cell-306 block is `c11r_runs.main` (`I.Blk(e_lo, e_hi)`, line 237), never run. Validation, mutations, cost, policy and the qualifier use NT or e = 5/2 (read; `grep "Blk("`). My harnesses and the chain controls use `synthetic_certs` (no certifier runs; the block is a label). I ran no kernel, certifier, selector, screen or bound on any open-cell block.

### 38. No target values -- PASS

Item 34. No original magnitude, rounded/truncated form or ratio to one appears in this review or in any file I wrote; the quarantine was opened only by the count-only scanner (no campaign module imported, nothing printed but counts, key paths and form types).

### 39. Guard DENY -- PASS

Gate `guard: DENY` (and `verify_gate` refuses anything else); `"guard": "ALLOW"` occurs at HEAD only in `c11r_b0.py`'s planted control, the quoted R4/R5 reviews and two C10 review markdowns; `"execution_permission": "ALLOW"` occurs nowhere at HEAD. No authorization or execution-permission record exists (item 41).

### 40. No qualification -- PASS

`evidence/qualification/` absent on disk and in all 723 commits reachable from any ref, reflog or HEAD (one `cat-file --batch-check` per commit; `git log --all --reflog --full-history -m` over the path: empty). `python3 -B code/c11r_qualify.py --self-test` in the primary checkout: 8/8 PASS, wrote nothing (the `__pycache__` modification times are unchanged; `git status` clean). `c11r_status.py --verify-only` (clone A): CONSISTENT, 15 artifacts fresh.

### 41. No authorization, no execution-permission record -- PASS

`config/C11R_AUTHORIZATION.json` and `config/C11R_EXECUTION_PERMISSION.json`: absent on disk and in all 723 reachable commits. (A preserved review committed after A -- simulated in clean clone C -- keeps `frozen_state` clean, the lifecycle FROZEN and status CONSISTENT, so preserving this review does not by itself break Q2/Q11.)

### 42. No evidence/runs/ -- PASS

Absent on disk and in all 723 reachable commits. My runs artifacts existed only on throwaway `r6_*` branches of scratch clone B.

### 43. No comparison -- PASS

`evidence/comparison/` absent on disk and in all 723 reachable commits.

### 44. Reviews R1-R5 preserved -- PASS

Blobs at HEAD == blobs at the preserving commits == working-tree `hash-object`: R1 8a445008 (6d7cd546), R2 af431bc0 (6ae05833), R3 19e276e4 (f6c737c3), R4 b2afdb49 (5c5203c1), R5 43c5f4c8 (ebf08c0f); each file is touched by exactly its preserving commit (`git log --all --full-history`). R4 and R5 are also identical to the reviewers' scratch originals (`scratchpad/r4/`, `scratchpad/r5/`). Errata E1-E38 and the review-3/4 dispositions are unchanged since ebf08c0f; E39-E48 and `review_5_findings_disposition` are additions.

### 45. Historical verdicts unchanged -- PASS

`git diff --name-only 440bcd91 cc93e470` outside the namespace: empty; no merge in the range; no commit in the range touches a file outside the namespace. B0_04 (C11 EXECUTION_INVALID, count-only) and B0_11 PASS.

### 46. N9 OPEN -- PASS

B0_05; the gate's `N9_entering_C11R: OPEN` and its conditional consequence ("if D1 and D2 are not independently certified, N9 remains OPEN"); D1/D2 NOT_IMPLEMENTED by policy and enforced by G8 (item 27), so N9_CLOSED is unreachable in this campaign.

### 47. K5 PARTIAL -- PASS

Gate `coverage: "r5 authoritative; open m=5 cells {306, 307, 308, 309}; K5 PARTIAL"`; B0_07 PASS; nothing outside the namespace changed.

### 48. r5 authoritative -- PASS

`K5_COVERAGE_MAP_R5.json` object f978eeb6 at 440bcd91 and at HEAD; B0_06 PASS.

### 49. No coverage r6 -- PASS

No `K5_COVERAGE_MAP_R6` in any ref's full history (`--all --reflog --full-history -m`) or on disk; B0_08 PASS.

### 50. Main untouched -- PASS

Local refs only (no fetch): `refs/heads/main` = c123b9bb8f15d17650545b3fce4aca8a6b61093b, `refs/remotes/origin/main` = 1cb453826313c189f0bdafd5b84120c1edb74da9; `evidence/b0/C11R_B0.json` records `LOCAL_MAIN_REF` and `REMOTE_MAIN_REF` as separate top-level fields with exactly these values (B0_09 PASS). No remote-tracking branch contains cc93e470.

---

## Reviewed identity (for any later auditor)

At cc93e470: contract body digest `ccf8b93d64b051a9bfe0fb7828fca0b042f43c9fd109b92062e8c5704bc1b5ae` (18 code files, 43 frozen paths incl. every Python file of the campaign code directory), gate `631dcf06d5de1ae0afac8de850378eb8204c11f9c97bb9cb6e46a9ac68266484`; both regenerate byte-identically in a scratch clone; `verify_contract`, `chain_roots` and `frozen_state(A)` return no problem there.

## Summary

Round 6 repairs both round-5 blockers as they were stated. R5-1: execution permission is now a separate forward-only record; followed literally, the runner's NEXT_STEPS take a valid run from AUTHORIZED through EXECUTING and EXECUTED_UNSEALED to SEALED under execution permission DENY with the authorization untouched, the comparator reaches the loader exactly once, writes its output once and the state becomes COMPARED; every deviation I tried (authorization deleted, recreated, reverted, re-serialised; extra DENY records; permission deleted; ALLOW at the seal; completion record bound elsewhere or committed separately; second executions, interrupted executions, ABANDONED + revert) is refused before the loader. R5-2 for CONTRACT import names: sourceless, packaged, zipped, symlinked, copied, forged-cache and `__file__`-rewriting shadows are all refused, and stale caches are correctly ignored (including the primary checkout's own). The sanitized git layer defeats replace refs, grafts, hostile `GIT_*` variables and shallow clones; the comparison output path, the verified runner inputs, the full-OID root of trust, the citation rule for the round-5 bypass, detector revision 4 and open-guard revision 3 behave as claimed, and every regression surface reproduces (chain 123/123, validation 17/17, mutations 42/42, firewall, leak check, contract and gate byte-identical, D5/P32, cap, reviews, predecessors, r5, no r6, main refs, no protocol artifact anywhere).

ONE load-bearing defect remains, in frozen code: the module-identity repair is keyed on contract import names, so a sourceless (or packaged) file with a STANDARD-LIBRARY import name placed in a campaign code directory -- which the campaign itself puts ahead of the standard library on `sys.path` -- runs inside the runner, the qualifier and the comparator while the pre-flight, Q4 and comparator step 12 report nothing. Demonstrated with `fractions`, which carries all of the certification arithmetic and the comparator's numerical classification (R6-1). The round-5 minimum fix named the missing clause; it is cheap to add now and impossible after the freeze.

## Load-bearing BLOCKERS

### R6-1 (MAJOR): the loaded-module identity repair (E40, part of G20) still lets a sourceless or package file with a NON-contract import name in a campaign code directory execute inside the runner, the qualifier and the comparator, unreported -- including the `fractions` module that carries all of the certification arithmetic and the comparator's numerical classification

**Where.** `c11r_contract.verify_loaded_modules` examines only the `sys.modules` entries whose KEY, or whose origin's import name, is a CONTRACT stem (`by_origin | by_key`, both intersected with `stems`); every other loaded module is skipped whatever its origin. `c11r_contract.code_dir_shadows` refuses only entries whose import name is a contract stem, plus untracked `*.py`. The contract's closure (`c11r_common.code_closure` / `_resolve_module`) resolves imported names against the campaign code directories, but only as `<name>.py`. Yet the campaign itself places those directories AHEAD of the standard library: the script directory of `c11r_runs.py`, `c11r_compare.py` and `c11r_qualify.py` is `sys.path[0]`, and `c11r_idrift` / `c11_certifier` insert C11's and C7's code directories at position 0. Every standard-library module not already imported at interpreter start-up (`fractions`, `json`, `__future__`, `ast`, `copy`, ...) is therefore resolved in those directories first. Round 5's minimum fix asked, besides the contract-name part, to "refuse any sys.modules entry whose origin lies in a campaign code directory but is not a contract path"; that clause was not implemented (E40's repair text omits it).

**Reproduce** (`probes/p_stdshadow.py`, `probes/p_stdshadow_cmp.py`, `probes/p_stdshadow_pkg.py`; clone B / clone A of cc93e470; production functions only; no spoofing on the runner or comparator paths):
1. `py_compile` the interpreter's own `fractions.py` plus one marker line into `<campaign>/code/fractions.pyc`, and its `ast.py` into `<C11>/code/ast.pyc`. Both are ignored (`.gitignore:33:*.py[cod]`); `git status --porcelain` is empty.
2. Runner: a process with `sys.path[0]` = the campaign code directory (as when `c11r_runs.py` runs) imports `c11r_runs` and calls the production pre-flight on a fixture-authorized branch: NO problem; `verify_loaded_modules(role="runner")` [] with all 11 required modules present; `code_dir_shadows` []. Meanwhile `sys.modules["fractions"].__file__` is the shadow, the marker ran in `fractions` and in `ast` (the latter inside `verify_contract` itself), and `c11r_runs.F` / `c11r_idrift.F` are the shadow's `Fraction`. Committing both files after A (`git add -f`) changes nothing: no frozen path, no closure entry.
3. Comparator: a process with its execution root = clone A carrying the same two files runs the production `execute_comparison` on clone B's sealed synthetic run: all twelve steps pass (step 12 lists no problem), the loader is called, and `classify_numeric` -- AGREES / STRONGER / INSUFFICIENT against the originals -- runs on the shadow's `Fraction`.
4. A stdlib-named PACKAGE (`code/fractions/__init__.py`, source-backed) is refused only incidentally while untracked ("untracked Python source") and passes the pre-flight once committed after A.

**Why it is load-bearing.** It is R5-2's class -- a file on disk in a campaign code directory, not in-memory patching -- with a non-contract name: the process that certifies, and the process that classifies against the original magnitudes, execute code from a file that is neither the contract's nor the interpreter's standard library, while the pre-flight, Q4 and comparator step 12 report the run as executed by the contract's code. A target run could be contaminated or mis-classified with every identity check green. The checks are frozen code. The contract's stated limit (2) ("code run through exec or under another module name ... NOT detected") is word for word the round-5 text under which R5-2 was ruled load-bearing; it concerns in-process execution, whereas this is a file on disk in the repository's own code directory, found by the import system through a path order the campaign sets up, and E40 describes the repair as keyed on "every loaded module's ORIGIN". The campaign's own closure definition (`code_closure` resolving imported names in these directories) already treats a same-named `.py` there as part of the bound code; only the `.pyc` / package forms escape.

**Minimum fix.** In `verify_loaded_modules`, refuse ANY `sys.modules` entry, whatever its name, whose origin (realpath of `__file__`, `__spec__.origin` or the loader's path) lies inside a campaign code directory of the execution root and is not a contract path (optionally: refuse any origin outside the contract paths and the interpreter's `sysconfig` stdlib/platstdlib directories). In `code_dir_shadows`, refuse every entry of the campaign code directories that is not a tracked `.py` file or `__pycache__`, regardless of its name (`.pyc`, `.so`, `.pyd`, archives, directories). Add chain controls for a stdlib-named `.pyc` in the campaign directory and in C11's, and for a committed stdlib-named package.

## Non-blocking observations

- **N6-1 (NOTE; item 1).** NEXT_STEPS names the seal's two files by namespace-relative path; say so (or print repository-relative paths).
- **N6-2 (NOTE; items 1, 5).** "Forward only" holds for COMMITTED history reachable from HEAD. Reproduced: (a) after an interrupted execution, `git checkout` of the GRANT returns the state to AUTHORIZED and the pre-flight passes (no trace); (b) a second execution on a sibling branch forked at the authorization commit, with the first seal still on another branch, is pre-flighted and compared (loader called), although `c11r_contract.protocol_artifacts_anywhere` (`rev-list --all --reflog`, already in the module) lists the other runs content. Both are inside the stated limit (1), but NEXT_STEPS[2] prints "nothing re-enables execution under this approved commit", which is not accurate; the runner prints no instruction for the crash case (commit the EXECUTION_STARTED record -> ABANDONED). Using `protocol_artifacts_anywhere` at the runner pre-flight and the comparator is cheap defence in depth.
- **N6-3 (NOTE; items 13, 14).** `c11r_compare.main` writes the comparison artifact even when the chain refused BEFORE the loader (no magnitude involved). That file then makes every later comparison refuse (uncommitted: MALFORMED; committed: COMPARED), and neither the policy nor the lifecycle says whether a pre-loader refusal may be retried after its cause is removed. Reproduced cause: a Finder `.DS_Store` (git-ignored) in `evidence/runs` -> "an unexpected file under a protocol directory on disk", EXECUTION_INVALID at step 2; after deleting it the same sealed run is accepted. Decide and state the rule before the freeze (e.g. write no artifact when `loader_called` is false, or declare pre-loader refusals retryable).
- **N6-4 (NOTE; item 24).** A re-stamped runs artifact that REMOVES the proving certificate, demotes its target and nulls the citation passes the citation rule and reaches the loader (AGREEMENT_INSUFFICIENT). The frozen runner always emits exactly {F_K, F_H, F_D}; requiring that set in `validate_runs` closes it. Hand-edited artifacts only (limitation 3), like N5-11.
- **N6-5 (NOTE; item 11).** A contract path replaced by a symlink to a file OUTSIDE the repository makes `c11r_common._rel` raise inside `verify_contract` (fail-closed crash, not a typed refusal).
- **N6-6 (NOTE; item 16).** `history_integrity` does not mention the commit-graph file. A forged commit-graph (second parent of a merge dropped, trailer re-hashed) is honoured by `rev-list --parents -n1 HEAD`, but on git 2.50.1 the campaign's range walks (`A..HEAD`) still reached the hidden commits and the comparator refused. Adding `-c core.commitGraph=false` to `git_run` would make "the REAL graph is read" true by construction rather than by observation.
- **N6-7 (NOTE; item 23).** `c11r_common`'s comment says "a hard link or a renamed copy of either under an innocent name is refused too"; a COPY (new inode) is not refused (reproduced on a dummy); the gate's G16 and the firewall's `scope` are accurate.
- **N6-8 (NOTE; items 21, 22).** Detector revision 4 misses a wrapper script without a `.py` suffix and a long option with a value before the script (`--check-hash-based-pycs default wrap.py`); neither is in `not_checked`. It flags as workers unrelated scripts with an argument like `C11_notes` or a comment naming the namespace (fail-safe false positives). Concurrency gate only.
- **N6-9 (NOTE).** B0_14's frozen label still says "detector revision 2" (the detector is revision 4).
- **N6-10 (NOTE; item 34).** My count-only scan (196 forms) finds four 4-5-character coincidences, all in measured wall-clock fields of the cost artifact and one NT-block validation field; zero hits at 6 or more characters, in the commit message, in this review and in my probe files. Not leaks; recorded so that a later scanner with short forms is not surprised.

## What is right and should be kept

The permission/evidence split with a DERIVED lifecycle and typed permission records; the literal NEXT_STEPS control; the introducer-based seal now tied to the EXECUTION_COMPLETED record in the same commit; name-AND-origin module identity with source-backed-only loading and per-boundary presence; the accepted-cache rule (no false refusal on the primary checkout's stale caches); one sanitized git entry point with grafts/shallow refused and a static scan; exclusive, sanctioned comparison write; `load_verified_inputs`; the full-OID root of trust; the exact-reason/exact-step chain controls with a loader spy. None of the accepted round-1..5 findings needed reopening.

## Blocker list

- R6-1 (MAJOR): `c11r_contract.verify_loaded_modules` examines only modules whose name or origin import name is a CONTRACT stem, and `code_dir_shadows` refuses only contract-named entries (plus untracked `*.py`); the campaign code directories precede the standard library on `sys.path`, so a git-ignored sourceless `fractions.pyc` in the campaign code directory (and `ast.pyc` in C11's) is executed by the runner and the comparator -- the certification arithmetic and the numerical classification run on the shadow's `Fraction` -- while the production runner pre-flight, `verify_loaded_modules(role=...)`, `code_dir_shadows` and comparator step 12 all return no problem and the loader is called (reproduced, `probes/p_stdshadow.py`, `p_stdshadow_cmp.py`; also when committed after A, and as a committed stdlib-named package, `p_stdshadow_pkg.py`). Fix: refuse any loaded module, whatever its name, whose origin lies in a campaign code directory and is not a contract path; refuse every non-`.py`/non-tracked importable entry of those directories; add the controls.

DISPOSITION: NOT_READY
