# C11R — independent COMPARISON review (Phase 15 comparison + N9 adjudication)

| item | value |
|---|---|
| reviewer | new, independent comparison reviewer (Claude Opus 5.5 subagent); no prior involvement in C11R |
| date | 2026-09-25 |
| brief | BRIEF_COMPARISON_REVIEW.md, sha256 4572fbc9844947cd50cde0777d4b8bfe711d71548bf59cbdd5eb233a54bd2b34 (verified) |
| primary checkout | /Users/suzhe/ReBaseGuard-k5c11r, branch p5y-k5-tail-c11r-n9-statement-alignment |
| comparison commit (subject) | 2c24a98935fee46a07b73f15337191f9045432e1 (adds only NS/evidence/comparison/C11R_COMPARISON.json, file sha256 800447ad…, body sha256 142259bf…) |
| adjudication commit (subject) | 118008f5ef23954fbc470656154571eb63e11bc6 = HEAD (adds only NS/adjudication/ADJUDICATION_C11R_N9.md, sha256 2a2b362e4d953ea2bba7406220e09e304f379a51e3dee82ce82f0eab812922de) |
| NS | level4/closure_proofs/p5y_k5_tail_c11r_n9_statement_alignment |
| mode | READ-ONLY. Runner never started or imported; comparator never run (only pure `classify_numeric`/`render` imported with -B, and an independent standalone re-derivation); nothing written outside q15/review_work and this file |

Initial state check: `git rev-parse HEAD` = 118008f5ef23954fbc470656154571eb63e11bc6; `git status --porcelain --untracked-files=all --ignored` = empty (0 lines). Proceeding.

## Method and safety

- Git history was read only with `git log/show/rev-parse/cat-file/ls-tree/diff/for-each-ref` (after the initial brief-mandated `git status`, every further git call used `--no-optional-locks`). No commit before the seal was checked out anywhere. No scratch clone was made.
- Review scripts (all under `q15/review_work/`, run with `/usr/bin/python3 -B`, importing **no** campaign module): `q_check.py` (quarantine vs comparison `original_value`, standalone JSON read of the quarantine blob via `git show`), `reg_check.py` (re-aggregation of the ORIGINAL cell-306 values from REGISTRY_C2), `classify_check.py` (every ratio and class re-derived from the emitted exact rationals with a literal transcription of the gate's frozen rule, then cross-checked against the comparator's own pure `classify_numeric` and `render`, extracted from the committed source by AST and exec'd in a bare namespace — the module itself was never imported, so its pre-import barrier, `_real_repository_guard`, loader and writer were never reachable), `digest_check.py`, `cert_check.py`. Host searches: `find` over /private/tmp, /private/var/folders (unbounded) and /Users/suzhe (depth 8/9, Library excluded), `mdfind`, and a `git cat-file -e` probe of every git repository found (58 under the temp roots, 39 under home).
- Nothing was recomputed with a certifier; no certifier, runner or comparator code path was executed.
- Self-disclosure (harmless, recorded for completeness): the brief-mandated `git status` in the primary updated only the **directory mtime** of the worktree admin dir `/Users/suzhe/ReBaseGuard/.git/worktrees/ReBaseGuard-k5c11r/` (15:52:52+0900; its `index` is unchanged at 15:50:26); one plain `git status --porcelain` I ran in the Phase 13 reviewer clone `q13/review_work/clone_q` likewise changed only that clone's `.git` directory mtime (16:04:12+0900; index, refs and objects unchanged). No file content anywhere outside `q15/review_work` and this file was changed.

## Required verifications

### 1. Entry HEAD — PASS
`2c24a989`'s only parent is `22537709a8a0bc564b71c30d1560df393b8c525d`; `compare.log` records `HEAD : 22537709…` at 06:37:51Z; `p15_entry.json` records `head 22537709…`; `p15_sealed_integrity.json` (`--sealed`) records head 22537709, lifecycle SEALED, permission DENY/EXECUTION_COMPLETED at HEAD and on disk, `protocol_history_compare.problems []`, `frozen_state` ancestry/tree_identity/history_purity empty, `evidence_comparison_exists false`. NOTE: the brief's "entry at 06:23Z" is not visible in the forensic files, whose entry outputs are stamped 06:33:19–06:34:32Z (p15_entry.py/json, p15_sealed_integrity.json); immaterial.

### 2. Accepted qualification — PASS
`evidence/qualification/C11R_QUALIFICATION.json` is introduced by exactly one commit in all refs and reflogs (`c06ce377`) and is byte-identical at HEAD; `QUALIFICATION_CLASS = PASS`; stored sha256 = recomputed canonical body digest = `114713ef…` = the authorization's `qualification_sha256`. `REVIEW_C11R_QUALIFICATION.md` (introduced once, `445fd84e`) ends `VERDICT: QUALIFICATION_ACCEPTED`.

### 3. Accepted authorization — PASS
`config/C11R_AUTHORIZATION.json` introduced once (`377bbcbb`), bytes unchanged at HEAD, body digest `193b0122…` recomputes; approved commit ee1a6a8a, cell 306, ONE_EXECUTION, contract 8e86b509, gate 2d23a8b8, policy a6b33ef3, statements b937cace, runner d958a457. `REVIEW_C11R_AUTHORIZATION.md` (`9bd17be5`, introduced once) ends `VERDICT: AUTHORIZATION_ACCEPTED`.

### 4. EXECUTION_ACCEPTED review — PASS
`REVIEW_C11R_EXECUTION.md`, introduced once by `22537709`, sha256 `ae2fbf70…` (= the commit message's), last line `VERDICT: EXECUTION_ACCEPTED`, "Blockers: none", N1–N8 non-blocking.

### 5. Seal commit — PASS
`5ff4cc5b` (parent 9bd17be5) adds `evidence/runs/C11R_RUNS.json` and changes `config/C11R_EXECUTION_PERMISSION.json` (GRANT → DENY/EXECUTION_COMPLETED) and nothing else; authorization untouched. Runs file sha256 `1552dfa9…`, stored body sha256 `1e0d82ac…` = recomputed canonical body digest; the permission record's `runs_sha256` = `1e0d82ac…`, `grant_sha256` = `ad95eef7…` = recomputed body digest of the GRANT committed at 377bbcbb, `authorization_sha256` = `193b0122…`; its own digest recomputes.

### 6. Exactly one run — PASS (within LIFECYCLE_SCOPE)
`git log --all --reflog -m -- evidence/runs` lists only 5ff4cc5b; the permission path is touched only by 377bbcbb (GRANT) and 5ff4cc5b (EXECUTION_COMPLETED); `protocol_history` introducers (forensic `--sealed` output): runs [5ff4cc5b], problems []. Forensics `phase14_execution/STARTED.once` 03:44:14Z, a single `START 03:44:15Z … EXIT 0 … END 05:06:33Z` in `run.log`; both forensic manifests verify (`shasum -c`: all OK). The runs file's birth time = mtime = 14:06:33+0900 (05:06:33Z): never rewritten. No other non-synthetic runs artifact exists on the host (the two other `C11R_RUNS.json` files are synthetic fixtures: one empty-target, one with the self-test values 1111/100, 999/100, 3/5). No repository outside the main repository's worktrees contains the seal commit.

### 7. No reusable GRANT (repository and host) — PASS, with a (b) observation
Repository: permission at HEAD, on disk and at the seal = DENY/EXECUTION_COMPLETED (identical bytes, blob af332d25); the only GRANT is historical (377bbcbb), and with a runs artifact committed the lifecycle is no longer AUTHORIZED (`run_stage_refuses_now`: "state is SEALED; stage run requires AUTHORIZED", and now COMPARED — item 10). Host: 27 permission records on disk; the only `fixture: false` record is the primary's EXECUTION_COMPLETED; the 24 GRANTs are all `fixture: true` in synthetic repositories (`q13/review_work/syn_*`, approved commit dc051946; `r7/…/c11r_chain_mhxptawp`, 5a8c118c). The three Phase 13 clones `clone1`, `mclone`, `shallow` are gone. Spotlight shows only the primary's record. No campaign process (`ps -axo`: none). **Observation N1 below:** the Phase 13 reviewer clone `q13/review_work/clone_q` (HEAD 445fd84e, no seal) still holds the unreachable commit 377bbcbb and the non-fixture GRANT blob `47a7a8ea` (GRANT/ALLOW/fixture false/ad95eef7) in its object store — not checked out, no activity since 11:27+0900 (before Phase 14). This is the "another clone / dangling objects" case LIFECYCLE_SCOPE explicitly does not cover, and the GRANT is in any case byte-reproducible from any clone at 445fd84e (the authorization reviewer demonstrated exactly that); it is not a defect of the comparison.

### 8. Runs artifact unchanged — PASS
Seal blob = HEAD blob = disk bytes (sha256 `1552dfa9…`), stored sha256 = recomputed body digest `1e0d82ac…`; the comparison's `result.seal.runs_file_sha256` is the same `1552dfa9…`.

### 9. Permission record unchanged — PASS
Bytes at 5ff4cc5b = 22537709 = 2c24a989 = 118008f5 = disk; DENY/EXECUTION_COMPLETED, bound to runs `1e0d82ac…`, GRANT `ad95eef7…`, authorization `193b0122…`.

### 10. Comparator invoked once — PASS (as far as artifacts can show; (b) N4)
`phase15_comparison/run_phase15_compare_once.sh` (noclobber once-marker, host/cache/clean-tree gates, then exactly one `"$LAUNCHER" compare --approved-commit ee1a6a8a…`); `STARTED.once` = 06:37:51Z; `compare.log`: one START 06:37:51Z, the ten rendered lines, `wrote … sha256 142259bf814641eb...`, EXIT 0, END 06:37:56Z. Launcher sha256 839faeae = contract. The comparison file and its directory `evidence/comparison/` were both born 15:37:56+0900 (06:37:56Z), mtime = ctime = birth (never modified); `git log --all --reflog` shows the comparison introduced once (2c24a989); the output directory holds exactly the one frozen name; no other `C11R_COMPARISON*` anywhere on the host or in Spotlight. Lifecycle, derived mechanically from the frozen table (`c11r_contract.lifecycle`, lines 1869–1892): qualification, authorization, permission, runs and comparison all committed and clean, permission at HEAD EXECUTION_COMPLETED ⇒ **COMPARED**; the adjudication path is neither a protocol path nor a frozen path. Residual: a pre-load refusal writes nothing, so an earlier refused start (or a start not through the wrapper) cannot be excluded from artifacts; the quarantine atime (02:07:58+0900) is uninformative under relatime semantics. Nothing suggests one.

### 11. Comparison source digest and seal binding — PASS, (b) note
`result.seal = {seal_commit: 5ff4cc5b…, runs_file_sha256: 1552dfa9…}` = the sealed file; steps 1–12 all `evaluated: true, pass: true, problems: []`; `loader_called: true`, `refused_at: null`; `approved_commit` ee1a6a8a; producer `c11r_compare.py` sha256 7065cc6a = the contract's `code` entry; all 15 `code_closure` hashes equal the files at A and at HEAD; `provenance.inputs` = the quarantine only, `gitobj:219e0122…` = the statement table's recorded content-free id. Stored sha256 `142259bf…` = recomputed `sha256_obj(body)`, and the committed bytes are exactly `json.dumps(body, indent=1, sort_keys=True)+"\n"` (the writer's form); file sha256 `800447ad…`. Note N5: `provenance.inputs` does not list the runs artifact, statement table, policy, gate or contract the comparator read (they are read through `read_runs`/`load_artifact`, not `C.load`); the binding to the run rests on `result.seal` and the step-2 lifecycle check, which suffice.

### 12. Target = cell 306 — PASS
Gate `target.cell 306`; contract `scope.cell 306` (implemented Abar, tau, C_T, D_lo; not implemented D1, D2); authorization and permission `cell 306`; quarantine `cell 306`; runs `drift_block` = cell 306's block.

### 13. Correct cell-306 drift interval — PASS
Runs top-level `drift_block` and each certificate's `inputs.drift_block` = ["680769/400000", "17885921/10000000"] = [1.7019225, 1.7885921] = contract `scope.drift_block` = gate `target.drift_domain` = statement table `drift_domain` = REGISTRY_C2 block for cell 306 (e_lo/e_hi read from the registry: exact match). The statement table's nine original sub-blocks are contiguous and tile the block exactly (re-checked from the registry). Every drift field anywhere in the runs artifact carries only these two endpoints.

### 14. No use of the cell-307 interval — PASS
REGISTRY_C2 cell 307 = [17885921/10000000, 1882413/1000000] = [1.7885921, 1.882413]. The string 1882413 / 1.882413 occurs in no runs, comparison, contract or authorization byte; the adjudication mentions it once, to say it was not used. The instruction discrepancy was resolved in the frozen statement table (`CAMPAIGN_INSTRUCTION_DISCREPANCY`, resolved to cell 306 before the freeze); `substitutions_forbidden` includes cell 307.

### 15. K vs Khat — PASS
F_K: `inputs.atom_removed_argument false`, `certifier_result.kernel K_e`; F_H and F_D: `true`, `Khat_e`. The frozen runner passes `atom_removed=ar` straight to `supersolution_margin_iv` (c11r_runs.py:341–361, `("F_K","K",False), ("F_H","H",True)`), the certifier derives its reported kernel from that argument, and the comparator's `reconstruct` refuses any certificate whose `atom_removed_argument` contradicts its reported kernel, keys the deduction on (module, function, kernel), and builds the independent statement's `kernel` field from the certificate; `EQ.compare` requires `kernel` among the EXACT fields. Citations follow `c11r_schema.TARGET_CERTIFICATE` exactly: Abar→F_K, tau→F_H, C_T→F_H, D_lo→F_D. Original kernels (statement table): Abar K_e; C_T, tau, D_lo, D1, D2 Khat_e — matched.

### 16. Abar vs tau — PASS, (d) note
Two distinct certificates: F_K input digest `927411e0…`, F_H `913fa6aa…`, both recomputed by me from (weight, inputs, certifier) and matching; they differ exactly in `atom_removed_argument`; separate certification calls (799.9 s and 761.1 s). Both carry the same weight w = 3429/500 − (1113/1000)·m, chosen by the frozen grid selector for each family independently (`selection_detail` F_K and F_H: A = 3429/500, B = 1113/1000, identical `A_req_exact`), and both report the identical `margin_lower_bound` and `w_min_lower_bound` (1.293 = A − 5B). This is mathematically expected, not a substitution: w ≥ 0 and the atom piece of K_e w is non-negative, so K_e w ≥ Khat_e w and any K_e supersolution is a Khat_e supersolution; the equal box-margin minima mean the binding box lies outside the atom window (the window is non-empty only for p + m < 1), so removing the atom does not move the binding constraint. tau = w(a) is thus certified as a Khat_e statement "(Ghat_e 1)(a) ≤ 3429/500" and Abar as the K_e statement "E_a[τ] ≤ 3429/500"; each is compared with its own original (5.1698… and 7.9124…), with different classes (AGREES 1.3265 vs STRONGER 0.8667). The gate's forbidden "Abar in place of tau" is a citation/statement substitution, and none occurred. (d) N6: the independent tau is only as tight as the K_e bound; the Khat_e structure was not exercised at the binding constraint.

### 17. The six N9 constants — PASS
All six are present in the comparison with the gate's constant list. Their `original_value`s equal, exactly and as strings, the quarantine's six values (standalone read of blob 219e0122, unchanged since A), and I re-derived all six from REGISTRY_C2 (blob 1a3adfd3, the quarantine's recorded input): C_T = max, tau = max, D1 = max, D2 = max, D_lo = min over the nine cell-306 sub-rows, Abar = the single ARL record (artifact bdf05e57 = the statement table's) — all exact matches. Independent status: C_T, tau, Abar, D_lo CERTIFIED; D1, D2 NOT_IMPLEMENTED (value null, `certificate_id` null, reason recorded).

### 18. Aggregation directions — PASS
Frozen directions (statement table `original_statements`, gate rule): C_T, tau, Abar, D1, D2 UPPER_BOUND; D_lo the only LOWER_BOUND. The comparison's `direction` fields equal them; D_lo was classified with the lower-bound rule (a smaller independent value is weaker: 0.505 vs 0.8445 → AGREES, not STRONGER). Original aggregation max/max/max/max/min/single re-verified from the registry (item 17); the independent side is a single whole-block certificate for each certified constant.

### 19. Independent-certifier identity and independence — PASS, (b) note
Certifier modules `c11r_idrift.py` (dd611a71) and `c11r_boxdata.py` (6bd427f9), cover `c11_certifier.cover`, all at their contract hashes. Their import graph (read from source) is `fractions`, `math`, `functools`, `pathlib`, `sys`, `c11r_common`, `c11r_idrift`, C11's `c11_certifier`/`c11_common` and C7's `c7_gaussian` (which imports only `fractions`); no module of the original's load-bearing graph (taboo_certify, resolvent_certificate, opnorms, ra_certifier, fast_range, intervals, …) and no numpy/scipy/flint/mpmath/sympy/gmpy2 import anywhere in the three campaign code directories. Exact rational arithmetic. Certificate `premises` are all empty; no original constant is consumed; the only original-value access in the campaign is the comparator's post-verification loader. The comparator's independence predicate recorded no violation. (b) N2, N3: "independently written" holds in the frozen C11R sense (no shared load-bearing graph or outputs); the implementations come from the same programme and author lineage, which had seen original magnitudes in C11; the deterministic frozen selector and policy (item 22) prevent that knowledge from steering a value.

### 20. Block-uniform statement — PASS
Each certificate is one interval-drift certification over the whole block (`aggregation single_certificate_whole_block`, `inputs.drift_block` = full block, cover at depth 5, 363 boxes = `len(cover(5))`). The reconstructed propositions are "for every e in the block …" with `drift_domain` = the full block; `EQ.compare` found domain EQUAL for all four (a wider block would be SUPERSET, a sub-interval SUBSET → WEAKER → INVALID). C_T, tau, Abar: premises SAME → EQUIVALENT; D_lo: premises FEWER (the original D_lo is conditional on C_T, tau; F_D is premise-free) → STRONGER. The F_D route is sound without C_T/tau: u = 101/200 + (21/250)·m ≥ 0, u ≤ h_1 + Khat_e u on the cover with margin > 0, and h_1 ≥ h_min ≈ 7.29e-5 > 0 gives Khat_e 1 ≤ 1 − h_min, so Khat_e^n u → 0 and u ≤ Ghat_e h_1 = d; D_lo = u(a) = 101/200.

### 21. No scalar-collapse substitution — PASS
No certificate is at a scalar drift, midpoint or sub-interval; the certifier carries e as an interval; the four emitted values are exactly w(a), w(a), sup-cover w (= 3429/500 + 99/2.67e101, outward rounding) and u(a), recomputed from the recorded weights.

### 22. Frozen policy identity — PASS
Policy body digest recomputes to `a6b33ef3…` = runs `policy_sha256` = `execution_identity.policy_sha256` = gate `policy_sha256` = authorization; chosen configuration depth 5 / panels 32 / safety 3/2 = contract and authorization configuration = the runs' `configuration` and every certificate's inputs (G19 PASS). All 44 contract `frozen_paths` are byte-identical (same blob ids) at A, 5ff4cc5b, 22537709, 2c24a989 and HEAD.

### 23. C2 prospective-floor handling — PASS
C2_ADJUDICATION.md: the floor (F1 supply independence, F2 ×1.25 degradation) is "prospective"; F1 is "available for as long as N9 … remains open, and lapses when N9 is closed" (lines 430–433); Condition 1: a replacement "must freeze the replacement before recomputing any magnitude" (536–537); the "two independent certifier implementations" replacement is one of three routes for cell 306, "at which point" N9 is closed (501–503). C10 README Q2 reads it the same way (F1 lapse, Condition 1 primary, the two-certifier sentence corroborating only and conditioned on closing N9). The adjudication keeps the floor as the standard, F1 live, the replacement route not reached, and applies no successor floor ("No successor floor was frozen before this magnitude was computed, so none may be applied now"). Correct. The gate forbids concluding that the floor may be replaced or F1 has lapsed; neither is concluded.

### 24. No post-result threshold change — PASS
Gate, statement table (rule sha `4ac6ece9…` recomputed = contract `comparison_rule.rule_sha256`), contract (factor 2) and comparator (`FACTOR = 2`, `PRECEDENCE`) are frozen paths unchanged since A (item 22); `gate.comparison_rule == table.comparison_semantics_frozen_before_results`; the comparison's `precedence` equals the gate's `N9_classification_precedence`. The adjudication introduces no threshold, floor or reclassification.

### 25. Scientific closure result — PASS
C11R's frozen comparison contains no K5 closure criterion (no Γ, no K5-B evaluation, no margin); the gate forbids "that any cell is closed or adopted". The adjudication (§4 B) states "not evaluated by C11R" and does not re-adjudicate cell 306's historical evidence. What C11R may conclude: statement and numerical agreement per constant and the frozen N9 classification. Nothing more is concluded. (c) wording note N10 on the "(C3/C5-T)" attribution.

### 26. Prospective adoption result — PASS
Not satisfied / not reached: N9 open ⇒ F1 live and the two-certifier replacement route unreached; no replacement floor frozen; no adoption performed or recommended as an act.

### 27. Robustness calculation — PASS (the frozen comparison computes none beyond ratio and class)
The frozen comparison computes, per statement-equivalent target, only ratio = independent/original and the factor-2 class; there is no degradation, Γ or margin computation, and none may be added post-result. I re-derived every ratio and class from the emitted exact rationals, (i) with a literal transcription of the gate's frozen text and (ii) with the comparator's own pure `classify_numeric` (AST-extracted), and re-rendered the ten `rendered` lines with the frozen `render`: all identical to the artifact, emitted ratios exactly equal to independent/original, and no independent value equals its original (the "copied" rule is not triggered).

| constant | dir | independent | original | ratio (exact, rendered) | STRONGER bound | AGREES bound | class (mine = frozen fn = emitted) |
|---|---|---|---|---|---|---|---|
| C_T | UPPER | 6.858 (+3.7e-97) | 5.829887954 | 1.176351939 | ≤ 5.829887954 | ≤ 11.659775908 | AGREES |
| tau | UPPER | 3429/500 | 5.169819806 | 1.326545268 | ≤ 5.169819806 | ≤ 10.339639612 | AGREES |
| Abar | UPPER | 3429/500 | 7.912416712 | 0.866738981 | ≤ 7.912416712 | ≤ 15.824833423 | STRONGER |
| D_lo | LOWER | 101/200 | 0.844492286 | 0.597992437 | ≥ 0.844492286 | ≥ 0.422246143 | AGREES |
| D1 | UPPER | none (NOT_IMPLEMENTED) | 0.455295982 | — | — | — | INSUFFICIENT |
| D2 | UPPER | none (NOT_IMPLEMENTED) | 5.416355434 | — | — | — | INSUFFICIENT |

Re-derived verdict by the frozen precedence: no independence violation, no DISAGREES, no INVALID, all guards PASS, not all six in {AGREES, STRONGER} ⇒ **AGREEMENT_INSUFFICIENT** = emitted. Opposite-direction pairs: none possible (no implemented certificate bounds an original quantity from the other side), 0 emitted. Class counts {AGREES 3, STRONGER 1, INSUFFICIENT 2} = emitted.

### 28. The N9 adjudication — PASS (with (c) wording notes)
Read in full (151 lines). Its conclusion follows mechanically from the comparison and the frozen texts; checked claim by claim below.

### 29. Is N9_CLOSED justified? — No; PASS
The gate's `SCOPE.N9_closure_requires` "all six constants for cell 306 classified AGREES or STRONGER, each with an EQUIVALENT or STRONGER statement"; `consequence_stated_conditionally`: "if D1 and D2 are not independently certified, N9 remains OPEN whatever the other four constants yield"; `forbidden_conclusions` includes "that N9 is closed while any of the six constants lacks an independent statement". D1 and D2 have no independent statement (NO_INDEPENDENT_STATEMENT, INSUFFICIENT). N9_CLOSED is not justified; N9 remains open.

### 30. K5 consequence — PASS
K5 PARTIAL; r5 authoritative (`K5_COVERAGE_COMPLETE: false`, m = 5 open {306, 307, 308, 309}); no coverage update; no r6. Justified by 29 and by the gate's `predecessor_state_preserved`.

### 31. No automatic inference N9_CLOSED → K5_CLOSED — PASS
The adjudication states "N9_CLOSED would not by itself have meant K5_CLOSED; the question does not arise", and C2's own text makes N9 closure the precondition of a successor floor, not an adoption.

### 32. No execution of 307–309 — PASS
The only runs artifact is cell 306's (drift block item 13); contract scope cell 306; no other non-synthetic runs artifact on the host or in any history; r5 cells 307–309 OPEN and unchanged.

### 33. No second 306 execution — PASS (within LIFECYCLE_SCOPE; see N1)
Items 6–9: one runs introducer, permission GRANT → EXECUTION_COMPLETED only, one Phase 14 once-marker, runs file never rewritten, no repository outside the main one holding the seal, no campaign process now.

### 34. No comparator retry — PASS (see N4)
Item 10: one start, one artifact born at 06:37:56Z and never modified; lifecycle COMPARED, so any later start refuses at step 2 and writes nothing.

### 35. No adoption — PASS
No adoption artifact, no coverage change; the whole C11R branch (26 commits since the C11 head 440bcd91) changes only paths under NS (`git diff --name-only 440bcd91 HEAD` outside NS: empty); the C2, C10 and C11 namespaces are byte-identical to 440bcd91.

### 36. r5 unchanged — PASS
`K5_COVERAGE_MAP_R5.json` blob f978eeb6 at A, 22537709 and HEAD and on disk; last changed by ae4cbc2c (C2, 2026-09-21).

### 37. No r6 — PASS
No path matching COVERAGE_MAP_R6 in any commit of any ref or reflog; none on disk under /Users/suzhe or /private/tmp.

### 38. Historical verdicts unchanged — PASS
Nothing outside NS changed on the C11R branch (item 35), so the documents carrying the original P8 FAIL, P9 PARTIAL, P8R/P9R CLOSED, P4 PARTIAL, P4Z CLOSED, C11 EXECUTION_INVALID (C11 README) and C2–C10 verdicts are byte-identical to their pre-C11R state; the adjudication restates them without modification.

### 39. Reviews unchanged — PASS
All 11 review files (R1–R8, qualification, authorization, execution) are each touched by exactly one commit (their preserving commit: 6d7cd546, 6ae05833, f6c737c3, 5c5203c1, ebf08c0f, 63402106, ac75c198, 5890511b, 445fd84e, 9bd17be5, 22537709) across all refs and reflogs; verdict lines unchanged (NOT_READY ×6, READY_TO_FREEZE, READY_TO_QUALIFY, QUALIFICATION_ACCEPTED, AUTHORIZATION_ACCEPTED, EXECUTION_ACCEPTED).

### 40. Main untouched — PASS
Local `refs/heads/main` = c123b9bb8f15d17650545b3fce4aca8a6b61093b; `git -C /Users/suzhe/ReBaseGuard ls-remote origin refs/heads/main` = 1cb453826313c189f0bdafd5b84120c1edb74da9 (GitHub); the C11R branch is not on GitHub (ls-remote returned no such ref); `origin/main` tracking ref 1cb45382. Only the C11R branch contains 2c24a989 and 118008f5.

## The comparison commit message (2c24a989), claim by claim

| claim | finding |
|---|---|
| artifact "exactly as the frozen comparator wrote it" | TRUE: bytes = writer serialisation of a body whose sha256 recomputes; file never modified after 06:37:56Z; commit adds only this file |
| one start through `c11r_launch.py compare --approved-commit ee1a6a8a…`, 06:37:51Z–06:37:56Z, exit 0 = COMPARED | TRUE (compare.log, once-marker, file birth time) |
| lifecycle SEALED → COMPARED; nothing else in the commit | TRUE (item 10; `--name-status`: one A) |
| C11R_COMPARISON/6, body sha256 142259bf… | TRUE |
| steps 1–12 passed before the loader; loader called once | TRUE (12 steps pass, `loader_called true`, `refused_at null`; one invocation) |
| seal 5ff4cc5b (runs file 1552dfa9…) | TRUE |
| comparator = the contract's c11r_compare.py (7065cc6a…) | TRUE |
| frozen verdict AGREEMENT_INSUFFICIENT; per-target classes; factor 2 frozen before results | TRUE (independently re-derived, item 27) |
| G8, G10, G19, value trace pass; no independence violation; no opposite-direction pair | TRUE |
| no adjudication, adoption, coverage change, r6 | TRUE |

## The adjudication commit message (118008f5), claim by claim

| claim | finding |
|---|---|
| kept in its own commit | TRUE (adds only ADJUDICATION_C11R_N9.md, sha256 2a2b362e…) |
| verdict N9_REMAINS_OPEN | follows from the gate (item 29) |
| "Four of the six … independently certified as the same block-uniform statements (C_T, tau AGREES; Abar STRONGER; D_lo AGREES with a STRONGER statement)" | TRUE in substance; "the same" is loose for D_lo, whose statement is STRONGER (premise-free), as the parenthesis itself says (N9, class c) |
| D1, D2 NOT_IMPLEMENTED; N9 then remains OPEN whatever the other four yield | TRUE, verbatim gate SCOPE |
| scientific closure and prospective adoption separate; neither a C11R output; C2 floor and F1 unchanged | TRUE |
| K5 PARTIAL; r5 authoritative; no coverage change; no r6; no adoption; proposed classification final only after this review | TRUE |

## The adjudication (ADJUDICATION_C11R_N9.md), claim by claim

- **Header table**: artifact, commit, schema and body digest; runs body `1e0d82ac…` / file `1552dfa9…`; EXECUTION_ACCEPTED at 22537709; chain ee1a6a8a/5890511b, c06ce377/445fd84e, 377bbcbb/9bd17be5; gate 2d23a8b8 "frozen before any target run" (`frozen_before: "any target certification run"`); table b937cace; comparator 7065cc6a — all TRUE.
- **"The first component to interpret the sealed cell-306 values was the frozen comparator"** — consistent with the record: the runner prints no value; the Phase 14 post-run script and the execution review state they emitted no target value (and none appears in their outputs or the review). Not provable in the absolute (b); no contrary evidence. The later `p15_lifecycle.py` (06:47:07Z, after the comparison commit) reads the runs file directly, which is harmless post-comparison (N7).
- **§1 frozen rule restatement** — verbatim-equivalent to the gate's rule; "factor 2 equal in the table, the contract and the gate" TRUE.
- **§1 table and threshold bullets** — every decimal is a correct rendering of the emitted exact rationals (item 27).
- **§1 guards, independence, opposite pairs, class counts, precedence, AGREEMENT_INSUFFICIENT** — TRUE.
- **§2 Q1 independence** — TRUE (item 19). The phrase "as the statement table's DEPENDENCY_FINDING requires" is loose: F_D satisfies the finding's independence consequence (never the original's C_T/tau) but does not follow its `ordering_forced` route (own C_T, tau → D_lo); it is a premise-free sub-solution route, which the frozen DEDUCTIONS and the gate's SCOPE ("the D_lo sub-solution route does not establish D1 or D2") anticipated (N9, c).
- **Q2 same statement** — TRUE (item 20).
- **Q3 correct interval** — TRUE (items 13, 14).
- **Q4 K vs Khat** — TRUE (item 15).
- **Q5 Abar vs tau** — TRUE; input digests `927411e0…`/`913fa6aa…` recomputed; the supersolution explanation is correct (item 16).
- **Q6 directions and aggregation** — TRUE; "D1 and D2 were not handled at all: NOT_IMPLEMENTED by design" with the DEPENDENCY_FINDING's machinery list — TRUE.
- **Q7 prospective** — TRUE for the rules (item 24); see N3 on author exposure.
- **Q8, Q9** — TRUE.
- **Q10** — N9 wording quoted verbatim from C2_ADJUDICATION.md:501 as frozen in the table; gate quotes verbatim, except that the first is truncated mid-sentence without an ellipsis (the gate continues ", each with an EQUIVALENT or STRONGER statement"); the omission drops a further requirement and does not weaken anything (N9, c).
- **§3 verdict N9_REMAINS_OPEN; C11 stays EXECUTION_INVALID** — follows. The comparator docstring quote is accurate ("In production, D1 and D2 are NOT_IMPLEMENTED, so N9_CLOSED is unreachable by scope"). "N9_REMAINS_OPEN" is not one of the gate's `permitted_N9_classifications`; it is the N9 status the gate's SCOPE sentence implies, while the frozen classification AGREEMENT_INSUFFICIENT is recorded separately in §1 and §4 D — no substitution (N9, c).
- **§4 A–D** — TRUE; the gate quote on a SUBSET is verbatim; the C2 F1 quote is verbatim with a correct ellipsis; the C10 conditioning is correctly reported. In §4 B, the parenthetical "(C3/C5-T)" as "the historical scientific evidence for cell 306" is unsourced in the document; the governing record of cell 306's standing evidence is the C2 adjudication (Condition 2: refined registry, Γ and margin "stand as published") (N10, c). It changes nothing: the statement is that this evidence is untouched and not re-adjudicated.
- **§5** — Outcome "C of the instruction" refers to a user instruction not in the repository (unverifiable label; the substance is verified). K5 PARTIAL, r5, open {306–309}, no r6 — TRUE. "certified four … as the SAME block-uniform statements" — loose for D_lo (STRONGER) (N9). "within the frozen factor 2" — TRUE. "What remains open" — TRUE.
- **§6** — historical verdicts and reviews unchanged — TRUE (items 38, 39).

## Load-bearing BLOCKERS

none

## Non-blocking observations

- **N1 (b) latent non-fixture GRANT in a reviewer clone's object store.** `/private/tmp/claude-501/-Users-suzhe-ReBaseGuard/ea6191ae-93b1-4f9c-b9ba-6cd0430d32ee/scratchpad/q13/review_work/clone_q` (HEAD 445fd84e, detached; no seal) holds the unreachable commit 377bbcbb and the GRANT blob 47a7a8ea (ALLOW, fixture false, ad95eef7). It is not checked out and shows no activity after 11:27+0900. The Phase 15 entry claim ("the only non-fixture execution-permission record on the host is the primary's EXECUTION_COMPLETED") is true of on-disk records only, and the execution review's N1 did not list this clone. It is outside LIFECYCLE_SCOPE (other clones, dangling objects), and the GRANT is byte-reproducible from any clone at 445fd84e anyway, so no host-level exclusion is possible in principle. Reproduce: `git -C …/clone_q cat-file -p 47a7a8eaeaab3d71566382b00245823266c86c04`. The user may wish to delete this clone (this reviewer may not).
- **N2 (b) authorship independence.** N9's "independently written" is met in the frozen C11R sense (disjoint load-bearing graph, no consumed outputs), not as organisational independence: same programme and author lineage.
- **N3 (b) prior exposure.** The author lineage saw original magnitudes in C11. Mitigated: rules, policy and grid selector were frozen and deterministic before the run, and no value was chosen by hand.
- **N4 (b) "comparator started once" rests on the wrapper, the log and file birth times.** A pre-load refusal leaves no artifact, and the quarantine atime is uninformative (relatime). There is no contrary evidence.
- **N5 (b) incomplete comparison provenance.** `provenance.inputs` lists only the quarantine. The runs, table, policy, gate and contract the comparator read are bound by `result.seal` and the verification steps, not by provenance.
- **N6 (d) tau adds no information beyond Abar in value.** The same weight certifies both. The binding box lies outside the atom window, so the independent tau (1.3265× the original) is exactly the K_e bound. This is sound, but it is weak corroboration of tau's Khat_e-specific tightness.
- **N7 (c) forensic record of `p15_lifecycle.py`.** It is listed in the Phase 15 manifest (created 06:47:07Z, after the comparison commit) and reads the runs artifact directly, but its output is recorded nowhere. The commit message's "lifecycle COMPARED" is therefore not backed by a forensic output. I derived COMPARED independently from the frozen transition table (item 10).
- **N8 (c) timing label.** The brief's "entry at 06:23Z" does not match the forensic entry outputs, which are stamped 06:33–06:34Z.
- **N9 (c) adjudication wording.**
  - "the SAME block-uniform statements" for D_lo, which is STRONGER (§5, commit message).
  - The first gate quote in Q10 is truncated without an ellipsis.
  - "as the DEPENDENCY_FINDING requires" (Q1) is loose.
  - The label N9_REMAINS_OPEN is not a member of the gate's `permitted_N9_classifications`. It is the implied N9 status, and the frozen class AGREEMENT_INSUFFICIENT is recorded alongside it. None of these weakens N9 or changes a conclusion.
- **N10 (c) §4 B "(C3/C5-T)".** This attribution of cell 306's historical scientific evidence is unsourced. The C2 adjudication (Condition 2) is the governing record.

## N9 agreement

I agree with **N9_REMAINS_OPEN**. The frozen comparison, which I re-derived exactly, gives AGREEMENT_INSUFFICIENT: C_T AGREES (1.1764), tau AGREES (1.3265), Abar STRONGER (0.8667), D_lo AGREES (0.5980, STRONGER statement). D1 and D2 have no independent statement (NOT_IMPLEMENTED), and the frozen gate states that N9 then remains OPEN whatever the other four yield and forbids concluding otherwise. Consequently F1 stays live, the C2 floor is unchanged, the two-certifier replacement route is not reached, K5 stays PARTIAL, r5 stays authoritative, and there is no r6. Nothing is adopted.

VERDICT: COMPARISON_ACCEPTED
