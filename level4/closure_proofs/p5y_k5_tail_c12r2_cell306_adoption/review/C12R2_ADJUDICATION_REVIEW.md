# C12-R2 — review of the cell-306 adoption adjudication
ADJUDICATION_ACCEPTED

| item | value |
|---|---|
| reviewer | an independent, fresh, read-only reviewer (Claude Opus 5.5 subagent). I did not write the adjudication, floor r2, the gate, the C12-R2 chain or any evidence it relies on. |
| date | 2026-09-27 |
| worktree | /Users/suzhe/ReBaseGuard-k5c11rd, branch p5y-k5-tail-c11rd-d1d2-extension |
| subject | level4/closure_proofs/p5y_k5_tail_c12r2_cell306_adoption/adjudication/C12R2_ADOPTION_ADJUDICATION.md (blob 6c4de3f1), line 2 `CELL306_NOT_ADOPTED` |
| magnitudes | This review contains no D1/D2 value, original or independent, and no D1/D2 ratio. The only Γ values quoted are the sealed ones and C2's published historical figures. |

## 1. Reviewed commits

| role | commit |
|---|---|
| floor r2 rule (PROPOSED on commit) | a15d083b009868e38a5bd5a808f38f19e6ab4b92 |
| floor r2 review preserved (REPLACEMENT_FLOOR_ACCEPTED) | 3fadb422 |
| N9 adjudication (N9_CLOSED); its accepting review | 7d67989d; fb237288 |
| C12-R1 status (the base for "nothing outside C12-R2 changed") | 13e06db05d59c84da1ce69f94ce189e37a76836f |
| C12-R2 freeze | 11f91daf50a077999023f733d8e870ad3813923a |
| C12-R2 qualification | 107a8b362e572eeab5c630e838edbe012cd3ae85 |
| C12-R2 qualification review (QUALIFICATION_ACCEPTED) | e19f4edd06ef2152d8285996db6d60b664c40f7d |
| C12-R2 grant | dec92e0983fe39bcf9834e62216daeab09f823a4 |
| C12-R2 seal (result blob 0ac46b3d2abe497084ddf7631d894bb819e6ddc6) | 276f4d416175086640c982ac4cda7c9cf703fccb |
| C12-R2 execution review (EXECUTION_ACCEPTED) | 1173670f04771e9d099182c519fc9a715aa89548 |
| mechanical floor application (operator; not authority) | 33b5f18365456dd3337d969b450210a650031f38 |
| adjudication (preserved alone) | 9c2cbf21317a0662df3b2bfb06452b4f6f5cf4d2 = HEAD |

## 2. Commands run (all read-only)

- `GIT_OPTIONAL_LOCKS=0` on every git command. Baseline and final: `git status --porcelain --ignored --untracked-files=all`
  → 0 lines; index mtime 17:25:17+09:00 (the time of commit 9c2cbf21) before and after; HEAD 9c2cbf21 before and after.
- `git log --oneline`, `git show --stat` / `--name-status` of 9c2cbf21, 33b5f183 and every commit in 13e06db0..HEAD;
  `git rev-list --parents 13e06db0^..HEAD` and `a15d083b^..HEAD` (linear, one parent each);
  `git diff --name-only|--name-status 13e06db0 HEAD` and `fb237288 HEAD`; `git log --diff-filter=MDRT fb237288..HEAD`.
- `git log --all -- <path>` for the floor r2 namespace, the result path, `*CELL306_RESULT*`, C12/C12-R1/C12-R2
  authorization and execution paths, `*COVERAGE_MAP_R6*`; `find` for any r6 on disk.
- `git rev-parse <rev>:<path>` for every floor r2 file at a15d083b, 3fadb422, 11f91daf, dec92e09, 276f4d41, HEAD, plus
  `git hash-object` of worktree copies; `git merge-base --is-ancestor` for a15d083b, 3fadb422, 7d67989d, fb237288
  against 11f91daf, dec92e09, 276f4d41, 9c2cbf21, and for the last commit of each multi-commit historical file against
  its verdict commit.
- `git for-each-ref refs/c12r2 refs/c12r1 refs/c12` (and a grep of all refs for `c12`); `ls` of the refs directory and
  of logs/refs/c12r2 (absent); `git ls-tree` of the result at 276f4d41 and HEAD; `cmp` of the pending-ref blob against
  the worktree result; `git cat-file -t` of b83cc6f5 and def4e453; `git log -1` of def4e453 and dec92e09 (same tree);
  listing of the worktree git dir (no emergency file).
- Reads (cat/sed/grep/Read): the full adjudication; floor r2 rule and gate (full), the floor review header and verdict
  line; C2_ADJUDICATION.md §K (lines 405-540); CELL_306_ADOPTION.md lines 120-135; ADJUDICATION_C10.md and C10 README
  margin lines; C10_GOVERNANCE.json `Q2_phase11_cell306`; the C12-R2 protocol §4-§5 and the C12 protocol's G07 row and
  verdict vocabulary; the C12-R2 execution review (section list, BLOCKERS, NOTES 1-8) and the qualification review
  (verdict line, BLOCKERS, NB list); the driver's `load_consumer`, `cell_inputs`, `supply`, `evaluate`, `decide` and
  `i2_set` header lines (read only, never run); c2_d5_forecast.py lines 85-92; the r6 generator's token checks (read
  only); the operator's c12r2_floor_r2_apply.py in full; the adjudicator's scratch helper history_check.py.
- python3.14 -I -S -B scripts in my scratch directory, each printing only keys, statuses, classes, booleans, hashes and
  the sealed Γ values:
  - selfhash.py: self-hash and canonical-serialization checks of the floor rule, the gate, the freeze and the sealed
    result;
  - struct.py: a masked tree of the sealed result, the grant and the freeze (every numeric-looking value masked);
  - sign.py: `fractions.Fraction` sign reads of C2's `cells['306'].Gamma_exact`, the sealed control and the sealed
    target, string equality and string sha256;
  - pins.py: the 32 frozen input pins and 5 frozen files against committed bytes at 11f91daf, dec92e09, 276f4d41, HEAD
    and the worktree, and against the sealed record's `input_sha256`;
  - hist.py: `git log --all`, HEAD blob and worktree blob for 49 historical and chain files;
  - leak.py: a boolean-only scan of the adjudication and the floor application for any decimal or rational rendering of
    any D1/D2 value (original or independent) or comparison ratio (0 hits; no value printed);
  - one-liners for the comparison classes/statements/domains (C11R, C11RD), C11RD runs statuses and drift-domain
    equality with the block, the D1/D2 `independent_value == runs value` equality (boolean), the registry cell-306
    `certified` flags and block bounds, r5's non-numeric keys and m = 5 open ranges, grant bindings, qualification counts.
- The operator's read-only script, once, into my scratch directory:
  `python3.14 -I -S -B c12r2_floor_r2_apply.py --out-json <scratch>/APPLY.json --out-md <scratch>/APPLY.md` →
  `FLOOR-R2 APPLICATION: checks 21/21; base True; F1' False; F2 False; criterion NOT_MET`, exit 0. I read it in full
  first: it runs only git read commands with `GIT_OPTIONAL_LOCKS=0`, reads committed bytes, and computes no Γ, atom
  constant or supply.

## 3. Findings

### 3.1 Commit scope — VERIFIED
- 9c2cbf21 has one parent, 33b5f183, and adds exactly one file:
  `level4/closure_proofs/p5y_k5_tail_c12r2_cell306_adoption/adjudication/C12R2_ADOPTION_ADJUDICATION.md` (blob 6c4de3f1,
  equal to the worktree copy). It is byte-identical to the adjudicator's own output file (`cmp`), so it was preserved
  verbatim.
- `git diff --name-only 13e06db0 HEAD` lists 18 paths, all added (status A), all inside the C12-R2 namespace. Per commit:
  11f91daf (protocol + 4 code files), 107a8b36 (4 qualification files), e19f4edd, dec92e09, 276f4d41, 1173670f (one file
  each), 33b5f183 (3 floor_application files), 9c2cbf21 (the adjudication). History 13e06db0..HEAD is linear.
- Since fb237288 only additions occurred, in floor r2, C12, C12-R1 and C12-R2 namespaces; no M/D/R/T anywhere.

### 3.2 Correct floor — VERIFIED
- r1 (C2_ADJUDICATION.md §K, commit ae4cbc2c): F1 "is available for as long as N9 … remains open, and lapses when N9 is
  closed". N9 is CLOSED: ADJUDICATION_C11RD_N9.md (blob c3e001a7, one commit 7d67989d) line 2 `N9_CLOSED`, the only such
  line; C11RD_ADJUDICATION_REVIEW.md (blob 3c716c70, one commit fb237288) line 2 is the accepting adjudication-review token, the only such
  line. So r1's F1 has lapsed (and historically it failed for 306 anyway: Γ under Lemma G alone +0.019116).
- C2 Condition 1 allows a replacement frozen before recomputation; C2 §K names this exact route (second certifier, then a
  two-implementation floor); C10 `Q2_phase11_cell306` says a future campaign may target 306 "YES, prospectively".
- Floor r2 rule K5_TAIL_ADOPTION_FLOOR_R2.json: blob 0ddfac30, file sha256 eb2b4196…, self-hash ba988b9e… verifies; gate
  CELL306_ADOPTION_GATE_R2.json: blob 89b86218, self-hash db7806fc… verifies. Both files are exactly the
  `indent=1, sort_keys=True` serialization plus newline.
- In force: `status_on_commit` requires a preserved REPLACEMENT_FLOOR_ACCEPTED review; FLOOR_R2_REVIEW.md (blob ad73021b,
  one commit 3fadb422, which adds only the review and its rerun JSON) has line 2 `REPLACEMENT_FLOOR_ACCEPTED`.
- Scope: `scope.operative_scope_of_this_campaign` = "cell 306 only"; `standing_floor` = r2 governs campaigns frozen after
  r2 is in force (C12-R2 is); 307-309 out of scope.
- No competing floor: across all refs the only floor files are the eight in the floor r2 namespace; nothing named
  r3/other exists.

### 3.3 Temporal ordering — VERIFIED
- Committer times (+09:00): a15d083b 00:22:36; 3fadb422 01:28:01; 11f91daf 14:44:23; dec92e09 15:40:36; sealed record
  started 06:41:48.398872Z (15:41:48+09:00), finished 06:41:50.383202Z; 276f4d41 15:41:50.
- a15d083b, 3fadb422, 7d67989d and fb237288 are ancestors of 11f91daf, dec92e09, 276f4d41 and 9c2cbf21.
- Floor r2 namespace: touched only by a15d083b and 3fadb422 in all refs; all 8 files have the same blob at
  3fadb422 (review files from there), 11f91daf, dec92e09, 276f4d41, HEAD and the worktree;
  `git diff 3fadb422 HEAD -- level4/closure_proofs/p5y_k5_tail_floor_r2/` is empty.
- The C12-R2 freeze pins the floor rule, gate and review (and 29 other inputs); all 32 pins match committed bytes at
  11f91daf, dec92e09, 276f4d41, HEAD and the worktree, blob prefixes match, and the sealed record's `input_sha256` equals
  the frozen pins key for key.

### 3.4 Correct evidence — VERIFIED
- **Sealed record.** refs/c12r2/cell306-pending-result → blob 0ac46b3d…; the result path has exactly one commit in all
  refs (276f4d41, parent dec92e09); the blob is identical at 276f4d41, 1173670f, 33b5f183, HEAD and in the worktree
  (`cmp` of the pending blob against the worktree file: identical); mode 100644; 19,937 bytes; sha256 bbe31d0a…;
  self-hash 9405f469… verifies. refs/c12r2/cell306-target-consumed → dec92e09 = `grant.grant_commit` =
  `seal_preconditions.branch_head`. Only these two refs exist under refs/c12r2, refs/c12r1, refs/c12; no reflog for
  them. Status TARGET_EVALUATED, `target_evaluations` 1. No C12 or C12-R1 authorization/execution path has any history.
  The probe blob b83cc6f5 and trial commit def4e453 (parent dec92e09, tree = the grant tree) exist, as the execution
  review recorded. No emergency file in the git dir.
- **Grant chain.** The grant binds freeze 11f91daf, qualification 107a8b36, review e19f4edd (verdict
  QUALIFICATION_ACCEPTED); its driver, verifier, r6 generator, grant generator and protocol hashes equal the frozen
  files; its freeze-record hash equals the freeze file's sha256. The qualification (at 11f91daf) passed 181/181 with 0
  real target evaluations, no refs, no result objects, no grant, no seal. The qualification review has line 2
  `QUALIFICATION_ACCEPTED`, "None." under BLOCKERS, notes NB1-NB12.
- **Execution review.** Line 2 `EXECUTION_ACCEPTED`, the only such line; one commit 1173670f (adds only that file; parent
  the seal); BLOCKERS "None."; NOTES 1-8, all non-blocking.
- **C2's committed control.** C2_D5_FORECAST.json: blob a191557f, one commit 5a94568a (2026-09-20). The sealed control's
  `Gamma_exact` equals C2's `cells['306'].Gamma_exact` as strings (both 1,531 chars, string sha256 148aac9a…), and the
  record has `reproduces_C2_exactly` true with all 7 `field_matches` true; supply "S_I1 = min{G, C1, C2}", provenance
  C2 on A0/A1/A2.
- **N9 comparisons.** C11R_COMPARISON.json (blob 5269c2aa, one commit 2c24a989; review 7375b9cd ends
  `VERDICT: COMPARISON_ACCEPTED`); C11RD_COMPARISON.json (blob 7151f57a, one commit 8e2defab; review 90265349 line 2
  `COMPARISON_ACCEPTED`); C11RD_RUNS.json (blob 30e2dfd0, one commit 4547bcd4, status CERTIFIED, cell 306).
- **F2 history.** C2_ADJUDICATION.md (blob cfc5b3ed, one commit ae4cbc2c, 2026-09-21) §K "Applying it", cell 306:
  "+0.029163 → does **not** close. **FAILS F2**", uniform-A margin 1.1277. CELL_306_ADOPTION.md (blob f5db4cd9; last of 5
  commits 87004e2b, an ancestor of ae4cbc2c) line 130: the same ×1.25 row, "+0.029163 — does not close". C10
  `Q2_phase11_cell306` (blob bc3fb1e6, last commit ec969db1 = C10's adjudication): `F2_passes` false; ADJUDICATION_C10.md
  line 157: "306 fails F2 on all three".

### 3.5 Exact sign of Γ(5, 306; S_I2) — POSITIVE (sign +1)
- `target.evaluated.Gamma_exact` in the sealed blob is a 1,484-character rational string, string sha256
  8ef2815cd478b43b05605e0ddefebd318568446194090327ffabc0e50b59e194, not starting with `-`.
- `Fraction(s)`: canonical (`str(Fraction(s)) == s`), `> 0` True, `== 0` False → sign **+1**. The sealed float
  0.005159101140006536 and the sealed `pass` false agree.
- Control Γ(5, 306; S_I1): sign **−1** (float −0.030469257709306738, `pass` true), equal to C2's committed string.
- No arithmetic was done beyond these sign reads and string comparisons.

### 3.6 Literal F1′ application, clause by clause — CORRECT
- (a) HOLDS. I1: REGISTRY_C1.json (blob f6d84bdb) and REGISTRY_C2.json (blob 1a3adfd3) cell-306 blocks `certified` true
  with e_lo 680769/400000, e_hi 17885921/10000000 (top-level `certified` true in both). I2: C11R C_T, tau, Abar, D_lo
  `target_status` CERTIFIED, statement domain EQUAL (C11R_N9_STATEMENTS drift domains are the block, "block-uniform");
  C11RD runs status CERTIFIED with D1 and D2 `drift_domain` equal to the block. Independence as defined (implementation
  and code) with `independence_violations` [] in both comparisons.
- (b) HOLDS. C_T AGREES/EQUIVALENT, tau AGREES/EQUIVALENT, Abar STRONGER/EQUIVALENT, D_lo AGREES/STRONGER (premises
  FEWER), D1 STRONGER/EQUIVALENT, D2 STRONGER/EQUIVALENT; all domains EQUAL; C11R `opposite_direction_pairs` []; C11RD
  `N9_VERDICT` N9_CLOSED; both comparisons accepted (7375b9cd, 90265349). C11RD `per_target[D1, D2].independent_value`
  equals the sealed runs' `targets[k].value` (boolean check only).
- (c) HOLDS. The five soundness documents (C11R_RUNS a5351603, D1_D2_DERIVATION.md 803f0145,
  C11RD_INDEPENDENCE_AUDIT.md 571c2d92, C2_ADJUDICATION.md cfc5b3ed, CELL_306_ADOPTION.md f5db4cd9) are pinned by
  sha256 and blob in the freeze and are unchanged; each was last changed inside its own campaign.
- (d) FAILS. Γ(S_I1) < 0 holds; Γ(S_I2) < 0 does not (sign +1). The rule's text requires both "SEPARATELY".
- F1′ = (a)∧(b)∧(c)∧(d) = FALSE. This is exactly floor r2 `disagreement.closure` ("Gamma(5, k; S_I1) < 0 but
  Gamma(5, k; S_I2) >= 0 … F1' FAILS … no adoption under F1'"). The adjudication records the disagreement (§6).

### 3.7 Literal F2 application from historical frozen evidence only — CORRECT
- F2 is classified FAIL from C2 §K's published ×1.25 Γ on S_I1 (+0.029163, "FAILS F2") and uniform-A margin 1.1277 <
  1.25, corroborated by CELL_306_ADOPTION.md line 130 and C10 `F2_passes` false.
- Floor r2 `known_historically` ("this rule does not revisit that") and gate G12 (a campaign that re-evaluates F2 must
  bind C2's procedure) permit relying on the published classification. The frozen C12-R2 decision table records F2 as
  "NOT_SATISFIED (C2 published FAIL on S_I1; not re-evaluated)"; the driver's `decide()` sets F2 as a fixed string and
  computes no degraded Γ. The adjudication did not re-run F2 and I did not either.

### 3.8 No recomputation, no supply substitution, no I1/I2 mixing, no threshold change — VERIFIED
- The only post-review commits are 33b5f183 (a read-only script plus its two outputs; I read the script in full) and
  9c2cbf21 (the adjudication text). My re-run of the script reproduces the committed JSON in every field except `HEAD`
  (committed 1173670f, the HEAD when it was generated; now 9c2cbf21).
- Supplies: control "S_I1 = min{G, C1, C2}" with provenance C2 on A0/A1/A2; target "S_I2 = min{G, I2}" with provenance
  I2 on A0/A1/A2. The frozen `supply()` refuses any set with a different `impl` tag and any duplicate; `i1_sets` tags
  I1, `i2_set` tags I2 and reads only C11R/C11RD `independent_value` (requiring the C11RD values to equal the sealed
  runs). The chosen supply for the base clause is S_I1, as floor r2 fixes it. No D′ mixed supply, alternative I2 supply
  or cross-implementation minimum appears anywhere after the seal.
- Threshold: floor r2 `quantity_compared.criterion` "strict sign: Gamma < 0 (exact rational arithmetic; Gamma = 0 or an
  incomplete evaluation fails)"; `numerical_agreement_threshold.adoption` "no ratio threshold"; c2_d5_forecast.py line
  89 `"pass": Gam < 0`. The adjudication applies it with no tolerance; since the sealed value is strictly positive, no
  boundary case arises. Factor 2, ×1.25, G00-G14 and the fail-closed list are byte-unchanged since a15d083b.

### 3.9 Adoption consequence — CORRECT
- base AND (F1′ OR F2) = TRUE AND (FALSE OR FALSE) = FALSE → cell (5, 306) NOT ADOPTED. Floor r2 `fail_closed` last
  item: "neither F1' nor F2 established: DO NOT ADOPT; the cell stays OPEN in the coverage map". The adjudication's line
  2 `CELL306_NOT_ADOPTED` is the C12 protocol's non-adopting token (C12_PROTOCOL.md line 70) and appears on no other
  line; `CELL306_ADOPTED` appears on no line of its own.
- The adjudication's remark that the frozen C12-R2 table `floor_satisfied = base AND F1′` is equivalent to floor r2's
  formula given F2's historical FAIL is correct, and the adjudication decides on floor r2's full formula.

### 3.10 Coverage consequence — CORRECT
- Cell 306 OPEN; r5 K5_COVERAGE_MAP_R5.json at blob f978eeb6b41188eabaf3c6d590c9178d711f1ce6 (one commit ae4cbc2c)
  remains authoritative: `per_m['5'].open_ranges` [[306, 309]], `open_count` 4, `union_open_ranges` [[306, 309]],
  `K5_COVERAGE_COMPLETE` false. No `*COVERAGE_MAP_R6*` exists in any ref's history or on disk. The frozen r6 generator
  requires line 2 exactly `CELL306_ADOPTED` (lines 10, 68-69, 126), so it must refuse; the adjudication says it must not
  be run. K5 PARTIAL. Cells 307-309 untouched.

### 3.11 Validity versus eligibility; no overclaim — VERIFIED
- §7 separates the two: the execution is scientifically valid (EXECUTION_ACCEPTED) and its positive Γ is a correct fact
  about I2's supply; adoption eligibility is not met. Non-adoption does not invalidate the execution, retract C2's I1
  closure, reopen N9 or assert that 306 is unclosable.
- §6 and §11.3 state explicitly that a positive Γ on an upper-bound supply is non-certification, not a certificate of
  non-closure, and correctly classify the outcome as a closure disagreement, not a SCIENTIFIC_DISAGREEMENT (floor r2
  reserves that for incompatible two-sided certificates; no opposite-direction pairs are recorded).
- "Scientific closure under I1: YES" matches floor r2's own definition (`adoption_vs_closure.scientific_closure`) and the
  sealed `floor_r2_table.scientific_closure` {S_I1: true, S_I2: false}.

### 3.12 Historical preservation — VERIFIED
Every file below has exactly the listed commits in `git log --all`, identical to its history on HEAD, and HEAD blob =
worktree blob; none is touched after 13e06db0 except the C12-R2 chain files, each of which has exactly one commit, its
own preserving commit.

| campaign | file (commits) |
|---|---|
| C2 | C2_ADJUDICATION.md, K5_COVERAGE_MAP_R5.json (ae4cbc2c); C2_D5_FORECAST.json, REGISTRY_C2.json (5a94568a); CELL_306_ADOPTION.md (5, last 87004e2b, ancestor of ae4cbc2c) |
| I1 registry | REGISTRY_C1.json (4ccee386) |
| C10 | ADJUDICATION_C10.md (ec969db1); REVIEW_C10_GOVERNANCE.md (7f255f3d); C10_GOVERNANCE.json and README.md (3 each, last ec969db1) |
| C11 | ADJUDICATION_C11.md (25475205) |
| C11R | ADJUDICATION_C11R_N9.md (118008f5); C11R_COMPARISON.json (2c24a989); C11R_RUNS.json (5ff4cc5b); C11R_N9_STATEMENTS.json (6, last dbd6cd89, ancestor of ee1a6a8a and 5ff4cc5b); reviews AUTHORIZATION/COMPARISON/EXECUTION/QUALIFICATION (9bd17be5/7375b9cd/22537709/445fd84e) |
| C11RD / N9 | ADJUDICATION_C11RD_N9.md (7d67989d); C11RD_ADJUDICATION_REVIEW.md (fb237288); C11RD_COMPARISON.json (8e2defab); C11RD_RUNS.json (4547bcd4); authorization/comparison/execution reviews (e320d8f5/90265349/db1c6118); pre-execution and qualification reviews (663f8fe7, 3c1eff11, 89330534, e27c2ffd); D1_D2_DERIVATION.md and C11RD_INDEPENDENCE_AUDIT.md (2 each, last ce5b8595, ancestor of 4547bcd4) |
| floor r2 | rule, gate, specification (a15d083b); review (3fadb422) |
| C12 / C12-R1 rejections | C12_QUALIFICATION_REVIEW.md (2cdfa467), C12_CAMPAIGN_STATUS.md (eba56027); C12R1_QUALIFICATION_REVIEW.md (e89402c1), C12R1_CAMPAIGN_STATUS.md (13e06db0) |
| C12-R2 | FREEZE and PROTOCOL (11f91daf); QUALIFICATION.json (107a8b36); QUALIFICATION_REVIEW (e19f4edd); GRANT (dec92e09); RESULT (276f4d41); EXECUTION_REVIEW (1173670f); FLOOR_R2_APPLICATION.json (33b5f183) |

### 3.13 Accuracy of the adjudication's factual statements — VERIFIED
I spot-checked every blob, commit, date, count and hash prefix the adjudication cites in §1-§5 (including driver
fab98a27 / 5c45b4de, verifier 3c748f11, r6 generator 1355f795 / 23a831c9, grant generator 83ec10cc, protocol c4b6f9ff /
874a5610, freeze f566e14b / 23deb827 / self-hash 6713660b, application files 84e050c9 / 1d7b114d / 686f6734, grant
fceeb3e7 / ef59ad21, qualification 574a92f0, reviews 79af9392 / 191d8a9d). All match. The D1/D2 leak scan of the
adjudication (and of the floor application) found 0 renderings of any D1/D2 value or ratio.

## 4. BLOCKERS

None.

## 5. Non-blocking NOTES

- **NOTE 1 — The 1.1555 margin is a different supply.** §3 item 11 and §11 reservation 2 list 1.1277, 1.1555 and
  1.171431 as "three unreconciled historical margins" (C10's own framing). C2 §K says 1.1555 is the margin "under the
  mixed supply" (D′), which floor r2 excludes from any S_I, and C10 says 1.171431 is imported from C8. Only 1.1277 and
  the ×1.25 Γ of +0.029163 are C2's S_I1 figures. The F2 classification rests on those, so nothing changes.
- **NOTE 2 — The frozen C12-R2 table is a narrower form.** It fixes F2 as NOT_SATISFIED and defines
  `floor_satisfied = base AND F1′`. The adjudication discloses this (item 14) and decides on floor r2's full
  `base AND (F1′ OR F2)`. The two coincide because F2 failed historically. Here the narrower form could only withhold
  adoption, and the full form withholds it too.
- **NOTE 3 — The operator's script is incomplete on F1′(a)/(c).** Its F1′(a) check does not read the I1 registry
  `certified` flags, and its F1′(c) check only tests pin presence. The adjudication discloses both gaps and checked the
  flags itself. I confirmed both registries' cell-306 blocks are `certified` true on the whole block. F1′ fails on (d)
  in any case.
- **NOTE 4 — Index mtime.** The adjudication's §2 and §12 report index mtime 16:28:51+09:00. That was its own session;
  the index now reads 17:25:17+09:00, the time of the operator's commit 9c2cbf21 made after the adjudication was
  written. It is not an adjudicator write. I ran no plain `git status`, and the mtime did not change during this review.
- **NOTE 5 — Authorization provenance is outside the repository.** This is inherited from execution-review NOTE 1: the
  user's authorization of the adjudication step is not in the repository. The adjudication discloses this.
- **NOTE 6 — Residual-disclosure placement.** The adjudication places the G07 residual disclosure in its own §10,
  citing C12's gate mapping (C12_PROTOCOL.md line 112, "carried into the adjudication's disclosure"). That matches the
  gate text. The residuals do not bear on the outcome, which follows from the sealed sign alone.

## 6. Resulting authoritative state (on preservation of this review)

- Cell (m = 5, k = 306): **NOT ADOPTED; OPEN.** Floor r2 eligibility NOT MET (base TRUE; F1′ FALSE on clause (d);
  F2 FALSE historically). A closure disagreement is recorded under floor r2 `disagreement.closure`.
- Coverage: r5 (K5_COVERAGE_MAP_R5.json, blob f978eeb6b41188eabaf3c6d590c9178d711f1ce6) remains authoritative;
  m = 5 open [306, 309]; K5_COVERAGE_COMPLETE false. **No r6** may be created; c12r2_r6_from_adjudication.py must not
  be run and would refuse. **K5 PARTIAL.**
- The C12-R2 execution (seal 276f4d41, EXECUTION_ACCEPTED 1173670f) stands as a scientifically valid, exactly-once
  evaluation: Γ(5, 306; S_I1) < 0 (C2's committed value) and Γ(5, 306; S_I2) > 0 (0.005159101140006536).
- C12-R2's exactly-once protocol is spent. The marker (refs/c12r2/cell306-target-consumed → dec92e09) and the pending
  ref (→ blob 0ac46b3d) stay in place. Floor r2 forbids any re-evaluation, parameter change or supply change in this
  campaign. Any future attempt on 306 needs its own instruction and its own prospective freeze.
- N9 CLOSED; C2's adoption of 305 and its I1 closure of 306 stand; cells 307-309 untouched; all historical verdicts
  unchanged.

## 7. Confirmation

- **Modified nothing.** I modified nothing in /Users/suzhe/ReBaseGuard-k5c11rd or its git dir. I ran no git write
  command and created or changed no file or ref.
  - HEAD is 9c2cbf21 before and after.
  - `git status --porcelain --ignored --untracked-files=all` printed 0 lines before and after.
  - The index mtime is unchanged at 17:25:17+09:00.
  - No `__pycache__` was created (every Python run used `-I -S -B`).
- **Recomputed nothing.** I recomputed no Γ, atom constant, margin or degraded Γ under any supply, and constructed or
  searched no supply.
  - I did not run c12r2_cell306.py in any mode, the verifier, the grant generator, the r6 generator or any consumer.
  - I did not re-run F2.
  - The only arithmetic was `Fraction` sign reads of committed exact rational strings, string and hash comparisons, and
    boolean equality checks.
- **Disclosed no D1/D2 value.** I printed, wrote and quoted no numeric value of D1 or D2, original or independent, and
  no ratio.
- **Nothing else was touched.** I did not open C11R's quarantine, and used no AWS or Vultr tool, no network and no
  session transcript.
- **Where I wrote.** Only in
  /private/tmp/claude-501/-Users-suzhe-ReBaseGuard/ea6191ae-93b1-4f9c-b9ba-6cd0430d32ee/scratchpad/c12r2_adj_review/:
  this file, selfhash.py, struct.py, sign.py, pins.py, hist.py, leak.py, APPLY.json and APPLY.md.
