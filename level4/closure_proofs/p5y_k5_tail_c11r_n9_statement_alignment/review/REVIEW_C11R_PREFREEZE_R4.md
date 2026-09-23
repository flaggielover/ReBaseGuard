# C11R pre-freeze review, round 4 (independent)

- Reviewed commit: bd00c1f62de74d756bea6a522d283e2a038c52bd (branch p5y-k5-tail-c11r-n9-statement-alignment, worktree /Users/suzhe/ReBaseGuard-k5c11r)
- Date: 2026-09-23
- Reviewer: new independent reviewer (no prior involvement in C11R rounds 1-3)
- Precondition: HEAD == bd00c1f62de74d756bea6a522d283e2a038c52bd and `git status --porcelain` empty -- VERIFIED at the start of the review.
- Numerics policy: no kernel, certifier, selector, screen or bound evaluated on any open-cell drift block; numerics only on NT = [5/2, 5/2 + 108337/1250000] or e = 5/2. No original cell-306 magnitude, rounded/truncated form or ratio to one appears here; the quarantine is referred to by path only.
- All writes happened in scratch clones under .../scratchpad/r4/work/ (git clone --no-local, checked out at bd00c1f6) or in throwaway temporary git repositories. The primary checkout was only read.

(Written incrementally. Status: COMPLETE -- all 50 required attacks reached. Additional probes beyond those listed under Method: `r4_wrongA_probe.py` (wrong approved commit), `r4_leak_scan.py` (count-only value scan), `r4_trace.py` + `r4_trace_analyse.py` (audit-hook traces).)

**Summary.** Round 4 repairs R3-1 in design and, on linear histories, in fact: the execution contract is canonical, deterministic and target-free; every boundary recomputes identities from bytes; R3B and R3A-as-committed-linearly are refused at every stage by my own harness on a full clone; the chain controls, contract, gate and NT calibration all reproduce exactly; the configuration choice is robust to the new rule's normalisation and to its calibration weights. ONE load-bearing defect remains (R4-1): the "untouched by every later commit" and "sealed by exactly one commit" checks use git's default history simplification, so an edit-use-revert on a merged side branch (with no record field forged, e.g. in `c7_gaussian.py`) and an earlier run on a merged side branch are invisible and the comparator reaches the magnitude loader. Thirteen non-blocking observations (N4-1..N4-13) should be fixed in the same repair where they touch frozen modules.

## Method

- Read in full: c11r_contract, c11r_compare, c11r_runs, c11r_certificate, c11r_common, c11r_qualify, c11r_chain, c11r_procs, c11r_cost, c11r_policy, c11r_gate; the relevant parts of c11r_schema, c11r_status, c11r_b0, c11r_firewall, c11r_mutations, c11r_errata; every committed JSON artifact except the quarantine's values; the R3 review; errata E24-E31 and `review_3_findings_disposition`.
- Two scratch clones of the reviewed commit: `work/clone` ("clone A": the code that is imported, and where producers were re-run) and `work/cloneB` ("clone B": a FULL clone used as the repository under test). My own harnesses are in `.../scratchpad/r4/probes/`: `r4_chain_probe.py` (R3A/R3B and variants), `r4_misc_probe.py` (qualification, guard ordering, seal), `guard_probe.py` (runtime open-guard), `r4_nt_calib.py` (NON-TARGET calibration reproduction). None of them uses `c11r_chain.py`'s `Chain` class; they drive the production functions (`c11r_contract.*`, `c11r_qualify.emit_qualification`, `c11r_runs.preflight/assemble`, `c11r_compare.execute_comparison`) directly against a full clone.
- Synthetic material in my harnesses: fixture qualification/authorization (`allow_fixture=True`), `c11r_compare.synthetic_certs` (no certifier runs), and a stub magnitude loader that only counts its calls. The quarantine was never copied or opened by any probe; the open-guard probe used a planted dummy file.
- Not run anywhere: `c11r_runs.py`, `c11r_compare.py --approved-commit`, `c11r_qualify.py --approved-commit`, `c11r_table.py`. Run in clone A only: `c11r_chain.py` (reproduced its artifact byte-identically), `c11r_qualify.py --self-test`, `c11r_status.py --verify-only`, `c11r_procs` live functions (read-only).
- Numerics: only the NON-TARGET calibration of `c11r_policy.calibration` (NT block) and pure classifier/identity code.

## Reviewed identity (for any later auditor)

At bd00c1f6: `config/C11R_CONTRACT.json` body digest `bba7be9c353138dce70db048e924ca1a86ce4d861bea427dc407e61e52956f59`; `config/N9R_GATE_C11R.json` body digest `b71d4314d4d48b8aa64711bdb802474a1ee78a6650474a0feb5c7746770cda9a` (its `execution_contract_sha256` equals the contract digest); policy body `a3174a85...`; statement table body `f9941a3d...`; cost body `cb1266ec...`. The contract recomputed from bytes in a full clone equals the committed one on every compared key, twice (deterministic), and `verify_contract` / `chain_roots` / `verify_frozen_at(A)` return no problems. 24 frozen paths (18 code files incl. `c7_gaussian.py`, `c11_certifier.py`, `c11_common.py`; contract, gate, policy, statement table, cost, validation).

## Attacks

### 1. R3-1 root-of-trust design -- DEFECT (BLOCKER R4-1 lives here); design otherwise sound

**What the design is.** The contract at the reviewed commit A is the authority. A is not in the contract (it cannot be); it is named by the Phase 13 authorization (`approved_commit`) and passed to the comparator (`--approved-commit`), which refuses if the two differ (`verify_chain`). Every boundary calls `_authorization_facts` -> `chain_roots` (contract and gate recomputed from bytes) + `verify_frozen_at(A)` (every frozen path byte-identical to A, HEAD descends from A, no commit in `A..HEAD` touched a frozen path, no uncommitted change) + `verify_qualification`.

**Checked mechanically (clone B, my own harness, not c11r_chain.py).** The design closes the three R3-1 gaps it targets: expectations now come from the contract, never from the seal commit's tree; policy/table/gate identities are recomputed, never read from `sha256` fields; the runner and the comparator both walk the chain. R3A on a LINEAR history and R3B are refused at every stage (items 14, 15).

**DEFECT (blocker R4-1).** The "no later commit touched a frozen path" leg -- the only mechanism the design relies on for an edited-then-reverted change (c11r_certificate docstring: "modified code can neither pass the pre-flight nor be reverted unseen"; G20: "untouched by every later commit"; the refusal text "(edited-then-reverted changes included)") -- is `git log A..HEAD -- <paths>` with git's DEFAULT history simplification. A merge that is TREESAME to one parent for the frozen paths prunes the other parent's history, so commits on a merged side branch that edit and revert a frozen path are never listed. Reproduced (item 14): the comparator reaches the magnitude loader and classifies the run. The same simplification affects the seal (item 11). Fix: `--full-history` (or `git rev-list A..HEAD` + `git diff-tree -m --name-only` per commit, or refuse any merge commit in `A..HEAD`), in `verify_frozen_at` and `verify_seal`, plus merge-topology controls.

**NOTE (human root of trust).** An operator who re-generates contract and gate at a later commit A' and names A' in both the authorization and the comparator invocation is accepted; only a human check that A' is the reviewed commit (or content-identical to it on the 24 frozen paths) catches this. The contract docstring states this honestly (limitation 3). I record the reviewed identity above so that check is mechanical for an auditor.

### 2. Canonical execution contract -- PASS

- `canon` = `json.dumps(sort_keys, separators=(",",":"), ensure_ascii=True)`; `body_digest` excludes only `sha256`; this equals what `C.write_evidence`/`sha256_obj` stores (checked: `CT.body_digest(contract) == contract["sha256"]`).
- `contract_body(repo)` computed twice in clone B: canonical bytes identical; equal to the committed contract on all 12 `COMPARED_KEYS`. No floats in the body (configuration values are strings/ints).
- Content: code identities (sha256 + git blob) for 18 closure files, three artifact identities (file digest, body digest, stored sha, schema, producer + producer digest, declared inputs, blob), REGISTRY_C2 by content-free id, schemas, configuration (D5/P32, cap 10800 s / 8192 MB, SF 3/2, rule text), comparison rule factor + rule digest, cost host, required predicates (G2, G8, G10, G18, G19, G20). `contains_target_results: false`; the only cell-306 content is the statement-semantics drift block. No magnitude, no ratio, no target computation output.
- The quarantine is not a frozen path, but its content-free id is recorded in the (frozen) statement table and checked by `load_original_magnitudes` before loading, so it is transitively bound.

### 3. Transitive code closure -- DEFECT (non-blocking, N4-3): load-bearing code can execute from outside it

- The closure is the AST import graph of the 16 role modules, resolved by `C._resolve_module` against `CODE_DIRS = (HERE, C11/code, C7/code)` in THAT order. 18 files; every campaign import in them resolves (checked by grep: only stdlib otherwise; no importlib/exec/runpy in closure modules; function-level imports are included by `ast.walk`).
- **Resolution-order mismatch (demonstrated).** At runtime `c11r_idrift` does `sys.path.insert(0, C11/code)` and `sys.path.insert(0, C7/code)`, so any module imported after `c11r_idrift` by a module whose own `insert(0, HERE)` ran earlier is looked up in C7/code and C11/code BEFORE HERE. The runner imports `c11r_boxdata` (-> idrift) and then `c11r_certificate`. I placed an untracked `c11r_certificate.py` (a one-line `raise SystemExit`) in C11's code directory of clone B: the runner's import sequence loads it ("R4 SHADOW ... LOADED"), while `verify_contract` and `verify_frozen_at(A)` both return `[]` (the closure resolves HERE first, and the shadow is not a frozen path; `git status` is checked only on frozen paths). The comparator has the same exposure for `c11r_schema` (imported by `c11r_certificate` after `c11r_idrift`).
- **Also outside the contract:** the interpreter and stdlib (bound only by the version string through the host check), the process environment (`PYTHONPATH`, `.pth`, `sitecustomize`), and timestamp-validated `__pycache__` bytecode. The contract hashes files by path; it never checks that the modules actually executing (`sys.modules[*].__file__`) are those files.
- **Why non-blocking.** Every one of these needs a deliberately planted file or environment; the contract's limitation (1) already concedes deliberate substitution against the runner. But it is not disclosed, and the fix is cheap and belongs in the same (frozen) modules: at pre-flight and in the comparator, require every loaded module under the repository (and every non-stdlib module) to map to a contract path with the bound hash; run Phase 14/15 with `python3 -I -B`; refuse untracked `*.py` in `CODE_DIRS`. Otherwise add it to the stated limitations.
- The modules NOT in the closure (errata, status, firewall, mutations, validate, b0, regen, chain) are not on the execution path; but see item 7 (the qualifier reads their unfrozen artifacts).

### 4. Recomputation vs self-declared hashes at every boundary -- PASS, with two NOTES

- Contract: body recomputed and every compared field recomputed from bytes. Gate: body digest recomputed; bound to the recomputed contract digest. Policy/table/cost: stored field must equal recomputed body digest; producer digest must equal the bound code; declared namespace inputs re-hashed. Qualification/authorization: body digests recomputed; every bound field compared with recomputed roots. Runner pre-flight: every contract code file re-hashed. Seal: runs body digest recomputed. Comparison rule: factor and rule digest recomputed. R3O/R3P and my R3B variants (field changed with body unchanged; body changed with field unchanged; consistent re-stamp) are all refused.
- NOTE: `verify_run_identity` checks `provenance.code_closure` only for entries that are present; a run whose `code_closure` is emptied (re-stamped) passes G20 (`r4_misc_probe.py` Ia: loader called, AGREEMENT_INSUFFICIENT). Only reachable with a hand-made artifact (limitation 2), but a one-line equality check would close it.
- NOTE: `verify_gate` does not compare the gate's own `policy_sha256` / `statements_sha256` / `comparison_rule` with the recomputed ones (the comparator re-checks the rule; the digests rely on the gate being frozen at A). They are consistent at A.

### 5. Gate binding -- PASS

The gate at A binds the recomputed contract digest; is itself a frozen path; is `guard: DENY`; carries G2, G8, G10, G18, G19, G20 with evaluators equal to `REQUIRED_PREDICATES` (checked both ways by `verify_gate`), each evaluator exists (`c11r_gate.main` refuses otherwise; I checked `callable` for all seven). Producer digest equals the bound `c11r_gate.py`. R3D (gate edited and re-stamped) is refused ("frozen path N9R_GATE_C11R.json differs").

### 6. Explicit G19 and G20 -- PASS as stated predicates; G20's text is not fully implemented (R4-1)

G19 (configuration adherence, `c11r_certificate.configuration_adherence`) and G20 (execution identity chain, `c11r_contract.verify_run_identity` + chain checks) are stated with evaluators. G19 is evaluated by the runner self-check and by the comparator and a failure yields EXECUTION_INVALID (my Ga probe). G20's clause "untouched by every later commit" is false for merged side branches (R4-1). G20's clause "all BEFORE any original magnitude is loaded" holds; G19/G10/G8 are evaluated AFTER the loader (item 13).

### 7. Qualification binding -- DEFECT (non-blocking, N4-4)

- Binding: contract, gate, policy, statements digests, qualifier digest (bound code), host == cost host == current host, class PASS with no failing item, not a fixture. Stale/forged cases (R3E, R3F, R3R) refused; my re-stamped-policy case (s4d) produced a NO_TARGET_EXECUTION qualification that `build_authorization` refuses.
- **Gap (demonstrated, `r4_misc_probe.py` Qa).** A NON-fixture qualification whose only item is `{"id": "ANYTHING", "pass": true}`, built with the production `emit_qualification`, passes `verify_qualification`, `build_authorization` and the runner pre-flight. The execution path verifies that a qualification is BOUND, not that it IS the Phase 12 qualification: the item set Q1-Q18 is never required. So Q5/Q6 (import scan; backend absent from the environment), Q7-Q12/Q15 (evidence classes), Q13/Q14 (NT exercises), Q17 (no worker) and Q18 (disk) reach Phase 14 only if the real qualifier produced the file. Requires constructing a qualification by hand (deliberate), hence non-blocking; fix: require exactly {Q1..Q18}, all passing.
- NOTE: Q7-Q12 and Q15 read artifacts (validation aside) that are NOT frozen paths and whose producers (mutations, firewall, status, chain, equivalence) are not in the contract; a post-A regeneration by unbound code would satisfy them. Q11 reads the committed `STATUS_CLASS` instead of running the status verifier (a presence check).

### 8. Authorization binding -- PASS; NOTE

`build_authorization` binds A, the recomputed contract/gate/policy/statement/qualification digests, the runner digest and the configuration; `verify_authorization` recomputes all of them at run and compare stages (R3G, R3S, my wrong-A case refused). NOTE: `issued_at_head` and `operator` are recorded but unverified, and nothing checks that the authorization and qualification were committed BEFORE the seal commit (the comparator only checks they were committed at all; ordering rests on the digest chain qualification -> authorization -> run identity).

### 9. Runner binding -- PASS; NOTE

`c11r_runs.main` calls `preflight` first; no science precedes it except module import (disclosed limitation 1; module-level code computes nothing on the target). The pre-flight re-derives everything itself (it does not trust the authorization's digests), re-hashes every contract code file, refuses an existing runs directory, and refuses if a campaign worker runs. It depends on the authorization only for the value of A (unavoidable; the comparator re-checks A against the operator). R3H/R3I (runner / reconstruction edited after authorization) refused; my R3B-after-authorization refused. NOTE: the worker check inherits item 21's blind spot; the executed-module gap is item 3.

### 10. Run-artifact binding -- PASS; NOTE

`verify_run_identity` requires `execution_identity` (contract, gate, qualification, authorization, policy, statements, runner, configuration, code map) to equal the recomputed chain, the top-level policy/statement digests to be the frozen ones (R3 F11 closed), the drift block to be the contract's (N-5 closed), the runs producer digest to be the bound runner, and each certificate's certifier digest to be the contract's. R3N (another authorization) refused. NOTE: certificates record only `c11r_idrift`/`c11r_boxdata` digests, so an edit to any other closure file (e.g. `c7_gaussian.py`, the rational Phi/phi core of both certifiers) leaves no trace in any certificate field -- the history check is the only detector for it (see R4-1). NOTE: empty `code_closure` accepted (item 4).

### 11. Seal binding -- DEFECT (part of BLOCKER R4-1)

`verify_seal`: exactly one commit touches the runs path, disk == that commit's blob, not dirty, schema-valid (typed seal fields), body digest recomputed; seal commit descends from A. R3M (runs edited and re-committed) refused. **But** "exactly one commit" uses the same default-simplified `git log`. Demonstrated (`r4_misc_probe.py` Sa): a first runs artifact committed on a side branch, a second run sealed on the line, and a `merge -s ours` of the side branch: `git log -- <runs>` lists 1 commit (`--full-history` lists 3), and the comparator accepts the second run (loader called). That is an undetected RETRY -- the "ONE execution, no retry" property the seal is meant to evidence -- by an operator who, per errata E11/E21, already knows the original values. (An uncommitted discarded first run is undetectable by any git check; that part is an inherent limit and should be stated.)

### 12. Comparator binding -- PASS except R4-1

`verify_chain` runs `verify_authorization(stage="compare")` (contract, gate, frozen paths, qualification, authorization recomputed), requires the authorization's A to equal the operator's, runs G20, requires the seal to descend from A, requires authorization and qualification to be committed, and checks the comparison rule (factor == 2 == table == contract, rule digest == contract, gate rule == table) -- M10/N-6 closed in production. `expected_certifier_sha` comes from the contract, `runs_producer` from the recomputed runner digest. Real-repository guard: `verify_seal(C.REPO)` from any program other than `c11r_compare.py` raises (reproduced).

### 13. Chain verified BEFORE any quarantine access -- PASS for the identity chain as implemented; DEFECT via R4-1; DEFECT (non-blocking, N4-5) in the documented order

- Every identity refusal in the chain controls and in my harness returns before the loader (stub call count 0). **But** with an invalid chain in the R4-1 sense (frozen paths edited and reverted on a merged branch; a hidden earlier run) the loader IS reached (S3a, S3c, S3d, Sa).
- **Documented order not implemented.** The comparator docstring lists "3 every production guard (reconstruction; value tracing, G8, G10, G19)" BEFORE "4 ... the ORIGINAL magnitudes". In code, `mags = loader(stmt)` precedes `run_comparison` -> `CV.evaluate_run`. Demonstrated (Ga): a valid chain with certificates at another depth (G19) or a mislabelled screen (G10) calls the loader, computes and records per-target numeric classes and ratios to the originals, then returns EXECUTION_INVALID. G14/G20's "before any original magnitude is loaded" is satisfied; the docstring is not. Reachable only with a non-runner artifact. Fix before freeze (the comparator is post-seal code): evaluate the guards first and refuse the loader on any guard failure, or correct the docstring.

### 14. R3A reproduced independently -- DEFECT (BLOCKER R4-1)

Harness `r4_chain_probe.py`, full clone B, production functions, no `Chain` class. Every scenario: qualification + authorization committed after A, pre-flight identity taken, then the attack, seal, `execute_comparison` with a counting stub loader.

| Scenario | History of frozen paths after A | Certificate record | Result |
|---|---|---|---|
| S0 valid chain | untouched | frozen | accepted, loader called once (control) |
| S1 linear: edit `c11r_boxdata.py` -> commit -> use -> revert -> commit -> seal | 2 commits, linear | edited digest (honest) | REFUSED (history + certificate digest); pre-flight at the edit refused |
| S2 same | 2 commits, linear | frozen digest | REFUSED (history) |
| S3a edit/revert `c11r_boxdata.py` on a side branch, `merge --no-ff` | 2 commits on a merged branch | frozen digest | **ACCEPTED -- loader called, AGREEMENT_INSUFFICIENT; `verify_frozen_at` returns []** |
| S3b same | same | edited digest | REFUSED (certificate digest only) |
| S3c edit/revert `c7_gaussian.py` on a merged side branch | same | nothing to forge (certificates record only idrift/boxdata digests) | **ACCEPTED -- loader called** |
| S3d edit/revert `c11r_policy.py` on a merged side branch | same | nothing to forge | **ACCEPTED -- loader called** |

In every accepted case `git log --full-history A..HEAD -- <frozen paths>` lists the two side commits; the default `git log` used by `verify_frozen_at` lists none. S3c is R3's own construction (assemble + write_evidence with the pre-edit identity) with no record field forged: a run produced with a modified Phi/phi core is classified as the frozen certifier's. The committed R3A control uses a linear history only (controls written to match the known attack).

### 15. R3B reproduced independently -- PASS

Policy edited in place (depth 6 / 128 panels, cap 10^6, `sha256` field kept): `build_authorization` refuses uncommitted and committed (contract artifact identity, configuration, stored-vs-body digest, frozen path differs / touched, selected configuration != contract); the runner pre-flight after a valid authorization refuses; the comparator after a post-seal policy edit refuses before the loader; a consistently re-stamped policy is refused at authorization (and its qualification is NO_TARGET_EXECUTION).

### 16. R3C-R3T controls -- PASS (real, non-vacuous, production logic); NOTES

- Re-ran `code/c11r_chain.py` in clone A: 24/24 ok, CHAIN_CLASS PASS, and the artifact is BYTE-IDENTICAL to the committed one (`git status` clean after the run).
- Each control calls production functions (`CT.*`, `R.preflight/assemble`, `Q.emit_qualification`, `K.execute_comparison`, `GA.build`); each refusal is required to carry an expected reason; positive controls R3T/R3T_unrelated reach the loader exactly once; the real-repository guard is exercised.
- NOTES: several expected reasons are weak substrings (`"policy"` for R3B/R3J/R3K/R3L/R3O) that many unrelated refusals contain; all controls use a linear history (no merge, no second branch), which is why R4-1 survived; R3S checks only the approved-commit mismatch path.

### 17. Stale qualification -- PASS

R3R (qualified under contract 1, legitimately re-frozen, then authorized under contract 2) refused on contract and gate digests; my re-stamped-policy case refused. Host staleness: `verify_qualification` requires the recorded host to equal both the cost host and the current host at authorize, run AND compare stages.

### 18. Wrong-contract authorization -- PASS

R3G (authorization bound to another contract digest) refused at the runner pre-flight. My own `r4_wrongA_probe.py` (clone B): an authorization naming an OLDER commit is refused at `build_authorization` (frozen paths differ); with the authorization naming A, a comparator given the older commit, or a content-identical descendant of A, refuses before the loader ("names another approved commit"); given A it accepts (non-vacuous).

### 19. Wrong-contract seal -- PASS

R3N (seal carrying another authorization's digest) and R3S (valid-looking seal from another contract, comparator given A1) refused before the loader; the same chain under its own contract is accepted (non-vacuous).

### 20. Changed transitive helper -- PASS on a linear history; DEFECT via R4-1 and item 3

R3Q (`c7_gaussian.py` edited and committed, then authorize) refused. My S3c (same helper, merged side branch, reverted) accepted; a shadowing module (item 3) is never seen.

### 21. The process detector on this actual host -- PASS for what it claims to see; DEFECT (non-blocking, N4-6) in what it is claimed to establish

- Live on this host (clone A, read-only calls): `planted_controls()` ALL_PASS; `live_controls()` ALL_PASS -- a framework-build child (`.../Python.app/Contents/MacOS/Python`) is seen, a shell mentioning a script is not, the detector itself is not, the exited child is gone. `campaign_workers()` sees 5 foreign interpreters (a `hermes` agent venv and four `rebaseguard-mcp` servers), matching the constant `foreign_python: 5` in every cost sample and in B0_14.
- **Blind spot, demonstrated.** While my NON-TARGET calibration probe (`python3 -B r4_nt_calib.py <clone>/.../code`, importing `c11r_policy`/`c11r_idrift`/`c11r_boxdata` at ~98% CPU) was running, `campaign_workers()["workers"]` was `[]`; the process was classified FOREIGN_PYTHON. This is exactly the form of R3's own N-2 demonstration (`nt_rehearsal.py <code dir> D P`): revision 2 still does not see it. Relevance is decided from argv tokens only, so any wrapper script that imports campaign modules -- the way every ad-hoc probe, E11/E21's scripts and both reviewers' rehearsals were run -- is invisible. On the pure classifier also: `-Bc "import c11r_boxdata"` (combined flag), `-cimport ...` (no space) and stdin are FOREIGN_PYTHON.
- The live control's child is classified CAMPAIGN_ADHOC through the `-c` branch (its marker follows a `-c` payload), so no real process exercises the script-path branch on this host; the planted rows do.
- **Why non-blocking.** The detector gates concurrency (cost measurement, runner pre-flight, B0_14, regen pre-flight), not identity or classification: undetected concurrent load can only inflate cost or trip the cap. But `not_checked` / E27 omit this, the most common case; add "a Python process whose argv names no campaign script (wrapper scripts importing campaign modules)" or classify by open files / imported modules.

### 22. Capital-P / framework-build Python -- PASS

`is_python_executable` accepts any path containing `/python.framework/` or `/python.app/` (case-insensitive) and `^python(\d+(\.\d+)*)?w?$` basenames; `ps -o comm` on this host reports the full framework executable path; live framework child detected. Also accepted: `/usr/bin/python3`, the Command Line Tools `Python3.framework/.../Python.app/.../Python`, uv-managed `python3.14`. Not accepted: `pypy3` (acceptable; not used here).

### 23. Self-match resistance -- PASS

The detector excludes its own PID and the whole ppid ancestor chain (my probes' own process and zsh parent were EXCLUDED_SELF_CHAIN); shells are never interpreters (a `zsh -c` whose string names a campaign script is NOT_AN_INTERPRETER), so the `pgrep -f` trap cannot fire; vanished PIDs are classified, not counted. NOTE: an ancestor that IS a campaign worker (e.g. regen launching producers) is excluded by design, so the check cannot detect a campaign process that launched the checker.

### 24. The regenerated cost measurement -- PASS

- Body digest recomputed = stored; producer digest = current `c11r_cost.py`; host = the contract's cost host. I re-derived every per-box-panel maximum and the screen constant from the raw observations with my own code (exact match), and every candidate's estimate and cap test (exact match to the policy): feasible = {D4/P32, D4/P64, D4/P128, D5/P32}; D5/P32 at 0.720 of the cap with SF 3/2; D5/P64 at 1.476 (not borderline). `len(X.cover(d))` = 97/363/1402 (geometry only).
- Samples monotone, span 756 s = `wall_seconds`; measured 19:50-20:03, committed 20:18 (regen3). The author's scratch logs show four round-4 cost measurements (debug run and regens 1-3), all with the same feasible set and the same choice; the committed one is the last. No selection effect is possible on the configuration (D5/P64 needs a 32% lower cost to become feasible).

### 25. Is the sequentiality claim now supported? -- PARTIALLY; stated precisely

- **Established:** at 5 stage samples and 74 background samples (10 s period) no Python process whose argv names a campaign script/module (other than the measuring process's own chain) existed; the foreign-interpreter count was 5 at every stage sample, consistent with the 5 persistent service interpreters on this host, i.e. no additional Python process at those instants.
- **Not established:** (a) absence of wrapper-script campaign work (item 21: such a process is FOREIGN_PYTHON; only the constant foreign count argues against one, and background samples do not record it); (b) absence of non-Python load -- the recorded load average was 2.4-3.6 on 6 cores, i.e. other runnable work was present; (c) anything between samples. The artifact's own `what_it_does_not_establish` is accurate for (b); it does not mention (a).
- **Consequence:** contamination can only inflate the measurement; it cannot change the configuration toward a target-favourable one. Non-blocking.

### 26. The E24 replacement rule is genuinely prospective -- PASS

- Nothing on any open-cell block was computed (item 41). The rule's inputs are the committed NT cost artifact and an NT calibration; it names no configuration. Family, cap, SF, grid, `b_max`, `beta_max`, `mu`, screen grid are unchanged since revisions 2/3 (checked in `affdf8a3`, `eaca931e`, `bd00c1f6`).
- I re-ran `c11r_policy.calibration` on NT for all four feasible configurations in clone A: every metric is EXACTLY the committed one (D5/P32 0.22013, D4/P32 0.29769, D4/P64 0.29388, D4/P128 0.29200). The qualifier only re-derives the choice from the recorded metrics; this independent recomputation closes that circularity for the reviewed commit.
- "Prospective" here means target-blind, not answer-blind: the author knew from E24/R3 that D5/P32 led on NT before writing the rule (disclosed in E24/E28). R3 judged that legitimate; not reopened.

### 27. The E24 rule does not encode D5/P32 as a desired winner -- PASS; calibration workload, normalisation and chronology judged

- **Normalisation is immaterial to the winner.** From the committed raw calibration rows (24 per configuration: 8 states x {K_e, Khat_e supersolution, sub-solution}) I ranked the four feasible configurations under six criteria -- raw max gap, relative max (the rule), supersolution max, sub-solution max, mean relative, mean raw. All six give the same order: D5/P32 < D4/P128 < D4/P64 < D4/P32. `relative == gap / scale` and `metric == max(relative)` hold exactly on every row. (Under the relative metric the sub-solution margin is the binding one for all four configurations; under the raw metric the supersolution is.) So the E28 chronology -- one D5/P32 calibration seen before the relative normalisation was declared -- cannot have steered the outcome, whatever its exact order.
- **Calibration workload.** The supersolution weight w = 12 - 3/2 m is the revision-1 K_e candidate that E9 says was written with the originals in view; the cost artifact uses it too. That is a legitimate question for a configuration rule, so I re-ran the whole calibration on NT with NEUTRAL weights that were never candidates (w = 20 - 2m, u = 1/4 + m/10, scales 20 and 1/4): the ranking is again D5/P32 < D4/P128 < D4/P64 < D4/P32 under the relative, supersolution-raw and sub-solution-raw criteria (`probes/nt_calib.log`). The weight does not steer the choice; the depth does (depth-5 boxes halve the height term, which dominates the loss on NT). States are the regular {0, 5/4, 5/2}^2 pattern minus one; sample points are corners + centre -- nothing target-shaped.
- **Chronology (E28).** Disclosed candidly, including that the author knew the NT leader beforehand (E24). The scratch logs show the relative metric already in use at the author's first full calibration (18:17) and four identical choices across the round-4 regenerations. NOTE: E28 should also say that the calibration weight is an E9 candidate (with the neutral-weight robustness above as the answer).

### 28. The finite candidate family -- PASS

`CONFIG_CANDIDATES = {4,5,6} x {32,64,128}` is byte-identical in revisions 2, 3 and 4; the rule evaluates every cap-feasible member (four) and only those; D5/P64 and deeper are excluded by the unchanged cap and SF, not by the calibration.

### 29. Cap enforcement (freeze, qualification, execution) -- PASS; NOTE

- Freeze: the policy refuses if no candidate fits `estimate x 3/2 <= 10800 s` and RSS <= 8192 MB; the chosen D5/P32 is at 0.720 (my recomputation). The contract binds cap, RSS cap and SF; R3L (cap raised, policy re-stamped) is refused.
- Qualification: `rederive_configuration` requires SF and caps equal to the module constants, the cost artifact to be the one the policy was frozen against, and re-derives the choice (self-test rows `rederive_rejects_a_raised_cap`, `..._tampered_choice` pass); host equality is enforced again at authorize/run/compare.
- Execution: `over_cap()` (wall clock since start, `ru_maxrss`) is checked before every box of the data pass and before each of the three certifications; an overrun records RESOURCE_CAP and NOT_REACHED, no retry. NOTE: nothing interrupts a certification in progress and there is no hard `setrlimit`, so a run can exceed the cap by up to one family's certification (~ 363 boxes x ~2 s at P=32 from the cost artifact, i.e. roughly 7% of the cap); the policy's "the runner checks the cap before every certification" is accurate, its `stop_conditions` wording ("if the wall clock exceeds the cap ... STOP") slightly overstates it.

### 30. The firewall claim is now scoped honestly -- PASS; NOTE

`CLAIM: DEFENSE_IN_DEPTH_HEURISTIC`, `what_it_does_not_prove`, R3's 20 probes recorded as known misses (6 flagged / 14 missed, `asserted: false`), G16 restated (static analysis "a DEFENSE_IN_DEPTH_HEURISTIC with recorded known misses, not a proof"), M03 renamed ("any PLANTED path (a heuristic ...)"), E29. NOTE: the artifact's `load_bearing_protections` lists "the comparator refusing before quarantine access when the execution identity fails", which R4-1 shows is not yet true for merged histories; and the unresolved-pattern list includes data-artifact names with a forced `.py` suffix (`config/C11R_POLICY.py`, ...) -- infeasible at runtime (`code_bytes` raises on a non-`.py` path), but exactly the kind of entry its own note calls a defect; it should be explained or eliminated.

### 31. Explicit production allowlists and the runtime open-guard -- PASS for the allowlists; NOTE on the guard's stated scope

- Allowlists: `PRE_RESULT_ARTIFACTS` / `ALLOWED_NS_INPUTS` are explicit tuples; `c11r_contract.artifact_bytes` and `C.load_allowlisted` refuse anything else. Audit-hook traces (clone A) of `c11r_contract`, `c11r_gate`, `c11r_procs`, `c11r_status` (full and `--verify-only`) and `c11r_qualify --self-test`: no protected file opened, only allowlisted JSON read, and the only git subprocesses touching protected paths are `hash-object` / `rev-parse` (ids, never content). Contract and gate re-generated in clone A are BYTE-IDENTICAL to the committed ones.
- Runtime open-guard (`guard_probe.py`, planted dummy file under a `quarantine/` directory, never the real quarantine): refused -- `open`, `Path.read_bytes`, `os.open`, `C.load`, and even opening the quarantine directory for a `dir_fd` open. NOT refused: a symlink with an innocent name pointing at the file; `os.chdir` into the directory and open by bare name; `sys.argv[0]` set to `c11r_compare.py` (or any program so named); a subprocess (`cat`) -- the last is disclosed. The guard tests the PATH STRING, so "refuses any Python-level open of a PROTECTED path" overstates it. Defence in depth only, and no production module does any of these; fix cheaply with `os.path.realpath(os.path.abspath(path))` before `is_protected`, and say that the reader test is by program name.

### 32. M10 and mutation/production alignment (detector_kind labels) -- PASS for M10; DEFECT (non-blocking, N4-7) in the labels and the record

- M10 now calls `c11r_compare.comparison_rule_problems`, which `verify_chain` runs before the loader; `FACTOR` is checked against the table, the contract and the gate at run time. N-6 closed.
- Labels: 26 PRODUCTION_GUARD, 3 PRODUCTION_SCIENCE, 7 SUITE_LOCAL_PROPERTY, 4 SUITE_LOCAL_AUDIT, and `what_demonstrates_production_enforcement` = the PRODUCTION_* rows. But M01/M02 (the import rule) are enforced on the execution path only through Q5 of a qualification whose item set is never checked (item 7), and M03 is the firewall heuristic, which does not run at Phase 14/15; labelling them PRODUCTION_GUARD overstates "production enforcement".
- **Retracted claim left live:** the artifact's `rules` list -- emitted by revision-4 code (`c11r_mutations.py` line 649) -- still reads "every detector is a production function; this module defines no guard", the exact sentence E30 retracts; the module docstring still carries the same text under "THE RULES NOW". Fix the emitted rule text.

### 33. B-1 (seal/schema compatibility) remains intact -- PASS

A producer-built runs artifact (`c11r_runs.assemble` + `C.evidence_body(producer=c11r_runs.py)`, exactly what `main` writes) is sealed and accepted by the real `verify_seal` and `execute_comparison` in a full clone (S0: loader called once, AGREEMENT_INSUFFICIENT). The seal is checked on typed fields (`seal_problems`); the comparator self-test's typed controls pass (in the committed mutations artifact and in my re-run of `c11r_chain.py`). `validate_runs` now also requires the `execution_identity` field set and certificate key == `certificate_id`.

### 34. B-2 (firewall truth in production) remains intact -- PASS

- Runtime traces (item 31) of the new/changed producers: no protected open, only allowlisted inputs, id-only git access to protected paths. The runtime open-guard would additionally have raised on any Python-level protected open in every campaign process I ran (chain controls, status, qualifier self-test, calibration) -- none did.
- Value-based leak scan (`probes/r4_leak_scan.py`, prints counts only): 165 forms of the six originals with >= 3 digits (exact rational, float repr, 2-10 dp rounded half-even / half-up / truncated with and without leading zero, 3-10 significant figures, scientific notation) over all 39 tracked namespace files outside `quarantine/` and `review/` at bd00c1f6, and over bd00c1f6's own commit message: ZERO hits. Positive control: 5 forms found in the (protected) R1 review, as expected. No value was printed or written.

### 35. B-3 (certificate -> proposition reconstruction) remains intact -- PASS

The only changes to `c11r_certificate.reconstruct` since eaca931e are the N-5 box-count cross-check (effective: it adds a problem, so the target is INVALID) and the demotion check in `evaluate_target` (item 36). Deductions, kernel/argument consistency, digest, premises, cover, family and value recomputation are unchanged; the 16 adversarial certificate controls are all caught, none missed; statement/number separation passes.

### 36. B-4 (production guards) remains intact -- PASS; DEFECT (non-blocking, N4-8) in the new N-5 demotion guard

- G8, G10, G19 and value tracing are evaluated in `c11r_certificate.evaluate_run`, called by the runner's self-check and re-run by the comparator; a G8/G10/G19 failure or an INVALID target gives EXECUTION_INVALID (my Ga probe for G19 and G10).
- **The N-5 "demoted target flagged" repair is not wired into the verdict.** With a synthetic run whose Abar target is set to NOT_CERTIFIED although its certificate reconstructs cleanly: `validate_runs` accepts it, `evaluate_run` records a value-trace violation ("... proves Abar, yet it is reported NOT_CERTIFIED (demoted)"), but `run_comparison` classifies Abar INSUFFICIENT through its status branch and computes `guards_ok` from G8/G10/G19 only, so the verdict is AGREEMENT_INSUFFICIENT -- identical to the honest run -- instead of EXECUTION_INVALID. No mutant or control exercises it (grep: "demot" occurs only in the certificate module and the errata). Reachable only by editing a runs artifact by hand before sealing; fix in the same comparator repair (include `value_trace` in `guards_ok`, or map a demoted target to INVALID) and add a control. This is the "fix recorded but never wired in" class.

### 37. B-5 (qualifier on the frozen policy, NT only) remains intact -- PASS

`--self-test` (clone A): 8/8 rows PASS, writes nothing; its trace opens only the policy and the cost artifact. Every numerical exercise uses NT or e = 5/2. `main` was not run. See item 7 for what the execution path does and does not require of a qualification.

### 38. The D_lo route remains rigorous -- PASS (not reopened)

`c11r_boxdata.py` and `c11r_idrift.py` are byte-identical to eaca931e (and `c11r_idrift.py` to 49b17ab4, the round-1 reviewed version). The sub-solution deduction is unchanged: `premises: ()`, and `holds` requires margin > 0, `h_min` > 0 and `u_nonnegative`. The policy's `F_D_non_target_record` is unchanged in substance.

### 39. D1/D2 remain unimplemented -- PASS

The derivative deduction is `implemented: False`; `c11r_runs.assemble` marks every constant outside `implementable_under_this_policy` = {Abar, tau, C_T, D_lo} NOT_IMPLEMENTED; G8 refuses any other status for D1/D2; the contract's `scope.not_implemented` = [D1, D2]; the policy's D1/D2 requirement list now includes the source-derivative bounds (N-6).

### 40. N9 remains conditional/open -- PASS

`run_comparison` returns N9_CLOSED only if all six classes are AGREES/STRONGER; D1/D2 are always INSUFFICIENT, so the production ceiling is AGREEMENT_INSUFFICIENT (S0 and every accepted probe returned exactly that). The gate's SCOPE and `forbidden_conclusions`, the policy's `target_scope.N9` and the errata state the subset limit.

### 41. No target science -- PASS

No runs/qualification/comparison/authorization artifact under any ref (`git log --all`: 0 for each pattern). The only `Blk(` on the cell-306 block is in `c11r_runs.main` (never run); every other drift block in every module is NT or e = 5/2 (grep); the firewall's open-cell-literal scan is empty for all 26 modules. bd00c1f6 adds only NT computations (cost, calibration, validation re-run) and synthetic chain controls. My own numerics were NT-only.

### 42. No qualification -- PASS

No `evidence/qualification/` on disk or in any commit; `c11r_qualify.main` was not run by me.

### 43. No authorization -- PASS

No `config/C11R_AUTHORIZATION.json` on disk or in any commit. The string `"guard": "ALLOW"` now also occurs in `c11r_contract.build_authorization` (a builder, not a setting).

### 44. No evidence/runs/ -- PASS

Absent on disk and in every ref. All my runs artifacts lived only in scratch clone B on scratch branches, which the harness reset afterwards (clone B is back at bd00c1f6, clean).

### 45. Guard DENY -- PASS; NOTE carried

Gate `guard: DENY`; no authorization. Whole-repository names-only scan at bd00c1f6 for any `"*guard*": "ALLOW"`: only B0's planted control string, the contract's authorization builder, two C10 markdown reports and an order-3 adjudication record key -- none a live setting. `EXECUTION_AUTHORIZED: true` stands only in the two other campaigns' files R3 listed (unchanged since 440bcd91) and in the quoted R3 review. N-10 carried as a documented limitation.

### 46. Historical reviews preserved -- PASS

`review/REVIEW_C11R_PREFREEZE.md`, `_R2.md`, `_R3.md`: blob at bd00c1f6 == blob at 6d7cd546 / 6ae05833 / f6c737c3 respectively == working-tree `hash-object`; each file is touched by exactly one commit (its preserving commit). The R3 file is also byte-identical to the R3 reviewer's original in the scratch directory.

### 47. Historical verdicts unchanged -- PASS

`git diff --name-only 440bcd91 bd00c1f6` outside the C11R namespace is empty: C2-C10 artifacts and C11 (EXECUTION_INVALID; B0_04 by count-only grep) are untouched.

### 48. r5 remains authoritative -- PASS

`K5_COVERAGE_MAP_R5.json` unchanged since 440bcd91 (`git diff --quiet`); B0_06 now compares the r5 object id at the C11 HEAD and at HEAD and lists the revisions present (3, 4, 5) -- it can now fail (N-7 closed).

### 49. No r6 -- PASS

No `*K5_COVERAGE_MAP_R6*` in any ref or in the index.

### 50. Main untouched -- PASS

`evidence/b0/C11R_B0.json` records `LOCAL_MAIN_REF = c123b9bb...` and `REMOTE_MAIN_REF = 1cb45382...` as separate top-level fields (and in B0_09). Now: `refs/heads/main` = c123b9bb, `refs/remotes/origin/main` = 1cb45382 (local refs only; I did not fetch or query the network).

---

## Load-bearing BLOCKERS

### R4-1 (MAJOR): the Phase 13-15 history checks use git's default history simplification, so merged side branches are invisible -- the R3A class is not closed, and the seal does not evidence "one execution"

**Where.** `c11r_contract.verify_frozen_at`: `git log --format=%H A..HEAD -- <frozen paths>`; `c11r_compare.verify_seal`: `git log --format=%H -- <runs path>`. Both omit `--full-history`, so any merge that is TREESAME to one parent for the given paths prunes the other parent's commits.

**What it breaks.** G20 ("untouched by every later commit"), the refusal text "(edited-then-reverted changes included)", the `c11r_certificate` integrity argument ("modified code can neither pass the pre-flight nor be reverted unseen"), E25's repair statement, the firewall artifact's "comparator refusing before quarantine access when the execution identity fails", and the seal's "committed by exactly one commit and never touched again".

**Reproduce** (full scratch clone of bd00c1f6; production functions; fixture qualification/authorization; `c11r_compare.synthetic_certs`; counting stub loader; `probes/r4_chain_probe.py` and `probes/r4_misc_probe.py`):
1. After A: commit the qualification and the authorization; take `c11r_runs.preflight` identity.
2. `git checkout -b side`; append a comment line to `c7_gaussian.py` (or `c11r_policy.py`, or `c11r_boxdata.py`); commit; build the runs artifact with `c11r_runs.assemble` (R3's own R3A construction); restore the file; commit.
3. `git checkout line; git merge --no-ff side`; write the runs artifact with `C.evidence_body(producer=c11r_runs.py)`; commit (seal).
4. `c11r_compare.execute_comparison(repo, approved_commit=A, ...)`: no identity problem, the loader is called, verdict AGREEMENT_INSUFFICIENT. `verify_frozen_at(A)` returns `[]`; `git log --full-history A..HEAD -- <frozen paths>` lists the two side commits. For `c7_gaussian.py` (the rational Phi/phi core of both certifiers) and `c11r_policy.py` no record field is forged at all; for `c11r_boxdata.py` it is accepted when the F_D certificate carries the frozen digest.
5. Seal variant: commit a first runs artifact on a side branch, seal a second one on the line, `git merge -s ours side`: `git log -- <runs>` lists 1 commit (`--full-history`: 3); the comparator accepts the second run.

**Why it must be fixed before the freeze.** Both functions are in the frozen, post-seal toolchain (`c11r_contract.py`, `c11r_compare.py`); they cannot be amended once a runs artifact exists. The fix is small.

**Minimum fix.** Use `git log --full-history` (or enumerate `git rev-list A..HEAD` and check `git diff-tree -m -r --name-only` against every parent), or refuse any merge commit in `A..HEAD`, in `verify_frozen_at` and `verify_seal`; state in the seal's docstring that an uncommitted, discarded run is undetectable by git; add chain controls for (i) edit/revert on a merged side branch and (ii) an earlier runs artifact on a merged side branch.

## Non-blocking observations (fix in the same repair where they touch frozen modules; none alone would let a target run be contaminated, mis-stated or mis-classified by the frozen runner operated as documented)

- **N4-1 (MINOR; items 4, 10).** `verify_run_identity` accepts a run whose `provenance.code_closure` is empty (checks only entries present); `verify_gate` does not cross-check the gate's own `policy_sha256`/`statements_sha256`. Certificates record only the two certifier digests, so edits to any other closure file leave no trace in a certificate.
- **N4-2 (MINOR; item 31).** The runtime open-guard tests the path string and the program NAME: a symlink with an innocent name, `chdir` + bare name, or `sys.argv[0]` spoofing / any program named `c11r_compare.py` bypass it. Normalise with `realpath(abspath(path))`; restate "any Python-level open of a protected path".
- **N4-3 (MODERATE; item 3).** Executed code is not verified against the contract: sys.path shadowing (demonstrated -- an untracked `c11r_certificate.py` in C11's code directory is loaded by the runner's import order while `verify_contract` and `verify_frozen_at` pass), environment (`PYTHONPATH`, `.pth`), stale bytecode. Verify `sys.modules` against the contract at pre-flight and in the comparator, run with `-I -B`, refuse untracked `.py` in `CODE_DIRS` -- or add it to the stated limitations.
- **N4-4 (MODERATE; item 7).** The execution path accepts ANY bound, PASS-class qualification: a non-fixture qualification with one arbitrary item passes `verify_qualification`, `build_authorization` and the runner pre-flight (demonstrated). Require exactly Q1-Q18, all passing. Q7-Q12/Q15 read unfrozen artifacts produced by unbound code; Q11 reads a committed class instead of running the verifier.
- **N4-5 (MINOR-MODERATE; item 13).** The comparator calls the magnitude loader BEFORE G8/G10/G19/value tracing, contrary to its documented order; a run failing G19 or G10 (valid identity) opens the quarantine and records per-target numeric classes and ratios before returning EXECUTION_INVALID (demonstrated).
- **N4-6 (MODERATE; items 21, 25).** The revision-2 detector still misses R3's own demonstration form: a wrapper script importing campaign modules is FOREIGN_PYTHON (demonstrated live with my NT calibration probe at ~98% CPU), as are `-Bc`, `-c<payload>` and stdin. Undisclosed in `not_checked`/E27. The "sequential" cost claim is supported only in the narrow sense stated in item 25.
- **N4-7 (MINOR; item 32).** M01/M02/M03 are labelled PRODUCTION_GUARD though not enforced at Phase 14/15; the mutations artifact's `rules` (emitted by revision-4 code) and the module docstring still carry the E30-retracted sentence "every detector is a production function; this module defines no guard".
- **N4-8 (MINOR-MODERATE; item 36).** The N-5 demotion check is recorded as a value-trace violation but does not reach the verdict (AGREEMENT_INSUFFICIENT, same as honest) and has no control.
- **N4-9 (NOTE; items 11, 29).** A certification in progress is never interrupted (overrun up to about one family's certification, roughly 7% of the cap at D5/P32); "ONE execution, no retry" is unenforceable against an uncommitted discarded run -- say so.
- **N4-10 (NOTE; item 8).** Nothing checks that the authorization and qualification commits precede the seal commit, and `issued_at_head` is unverified; ordering rests on the digest chain.
- **N4-11 (NOTE; item 30).** The firewall's unresolved-pattern list contains data-artifact names with a forced `.py` suffix; explain or eliminate them (the artifact's own note calls such an entry a defect).
- **N4-12 (NOTE; item 27).** E28 should disclose that the calibration's supersolution weight is an E9 (originals-in-view) candidate, with the neutral-weight robustness (same ranking) as the answer.
- **N4-13 (NOTE; item 16).** Several chain-control expected reasons are weak substrings ("policy"); all controls are linear-history.

## What is right and should be kept

- The contract design itself: identities recomputed from bytes at every boundary, never read from stored fields; expectations taken from the contract, never from the seal commit's tree; the comparator refuses before the loader on identity failures (linear history); contract and gate regenerate byte-identically; R3B and linear-history R3A refused at every stage in a FULL clone by my own harness; wrong-A, wrong-contract and stale-qualification cases refused; the chain-controls artifact reproduces byte-identically.
- The NT calibration reproduces exactly for all four feasible configurations, and the configuration choice is robust to the normalisation and to the calibration weights; cost derivation and feasibility reproduce exactly; the cap and family are unchanged.
- The honest downgrade of the firewall claim, the runtime open-guard (effective for direct opens), a clean value-based leak scan, clean runtime traces, the capital-P detector fix, the preserved reviews and the intact pre-result state (no runs, qualification, authorization or comparison anywhere; guard DENY; r5 authoritative; no r6; main refs recorded separately and unchanged).

## Blocker list

- R4-1 (MAJOR): `c11r_contract.verify_frozen_at` and `c11r_compare.verify_seal` use `git log` with default history simplification. Commits on a merged side branch that edit and revert a frozen path (demonstrated with `c7_gaussian.py`, `c11r_policy.py`, `c11r_boxdata.py`) are invisible, so the comparator verifies the chain and calls the magnitude loader on a run produced after such an edit; and an earlier runs artifact on a merged side branch is invisible to the seal, hiding a retry. Fix with `--full-history` (or per-commit diff against every parent, or refuse merges in `A..HEAD`) in both functions, plus merge-topology chain controls.

DISPOSITION: NOT_READY
