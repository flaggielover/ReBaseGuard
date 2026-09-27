# C12-R2 — cell-306 adoption adjudication under floor r2
CELL306_NOT_ADOPTED

**Decision in one line.** Cell (m = 5, k = 306) is **not adopted**. The base clause holds, but F1′ fails on
clause (d): the one sealed, accepted evaluation gives Γ(5, 306; S_I2) **> 0**. F2 fails on historical frozen
evidence. So `base AND (F1′ OR F2)` is false. Cell 306 stays OPEN, r5 remains authoritative, no r6 may be created,
and K5 remains PARTIAL.

| item | value |
|---|---|
| adjudicator | an independent, fresh, read-only adoption adjudicator (Claude Opus 5.5 subagent). I did not write, freeze, qualify, grant, run, seal or review any part of C12-R2, floor r2, C2, C10, C11, C11R or C11RD. |
| date | 2026-09-27 |
| worktree | /Users/suzhe/ReBaseGuard-k5c11rd, branch p5y-k5-tail-c11rd-d1d2-extension |
| HEAD adjudicated | 33b5f18365456dd3337d969b450210a650031f38 (the operator's mechanical floor application; parent 1173670f) |
| rule applied | K5 tail adoption floor r2: rule a15d083b, preserved review 3fadb422 (REPLACEMENT_FLOOR_ACCEPTED) |
| magnitudes | This file contains no D1/D2 value, original or independent, and no D1/D2 ratio. The only Γ values quoted are the sealed ones and C2's published historical figures. |

## 1. Artifacts reviewed

All blob ids are at HEAD 33b5f183. Each equals the worktree copy (`git hash-object`), and each file listed has
exactly the commits named (`git log --all`).

**Floor r2** (level4/closure_proofs/p5y_k5_tail_floor_r2/):

| file | blob | commits |
|---|---|---|
| config/K5_TAIL_ADOPTION_FLOOR_R2.json | 0ddfac30 (sha256 eb2b4196…; self-hash ba988b9e… verifies) | a15d083b only |
| config/CELL306_ADOPTION_GATE_R2.json | 89b86218 (self-hash db7806fc… verifies) | a15d083b only |
| FLOOR_R2_SPECIFICATION.md | ed929934 | a15d083b only |
| review/FLOOR_R2_REVIEW.md (line 2 REPLACEMENT_FLOOR_ACCEPTED) | ad73021b | 3fadb422 only |

**C12-R2** (level4/closure_proofs/p5y_k5_tail_c12r2_cell306_adoption/, "NS"):

| role | commit | file | blob |
|---|---|---|---|
| freeze | 11f91daf50a077999023f733d8e870ad3813923a | protocol/C12R2_PROTOCOL.md, protocol/C12R2_FREEZE.json (self-hash 6713660b… verifies), code/ ×4 | c4b6f9ff, f566e14b; driver fab98a27 (sha256 5c45b4de…) |
| qualification | 107a8b362e572eeab5c630e838edbe012cd3ae85 | evidence/qualification/C12R2_QUALIFICATION.json (pass true, 181/181, real_target_evaluations 0) | 574a92f0 |
| qualification review | e19f4edd06ef2152d8285996db6d60b664c40f7d | review/C12R2_QUALIFICATION_REVIEW.md (line 2 QUALIFICATION_ACCEPTED; 0 blockers, NB1-NB12) | 79af9392 |
| grant | dec92e0983fe39bcf9834e62216daeab09f823a4 | authorization/C12R2_GRANT.json (sha256 ef59ad21…) | fceeb3e7 |
| seal | 276f4d416175086640c982ac4cda7c9cf703fccb | evidence/execution/C12R2_CELL306_RESULT.json (sha256 bbe31d0a…, 19,937 bytes) | 0ac46b3d2abe497084ddf7631d894bb819e6ddc6 |
| execution review | 1173670f04771e9d099182c519fc9a715aa89548 | review/C12R2_EXECUTION_REVIEW.md (line 2 EXECUTION_ACCEPTED; 0 blockers, 8 notes) | 191d8a9d |
| mechanical floor application | 33b5f18365456dd3337d969b450210a650031f38 | floor_application/c12r2_floor_r2_apply.py, C12R2_FLOOR_R2_APPLICATION.json, .md | 84e050c9, 1d7b114d, 686f6734 |

**Refs** (files backend; no reflog exists for them):
- `refs/c12r2/cell306-target-consumed` → commit dec92e0983fe39bcf9834e62216daeab09f823a4 (the grant).
- `refs/c12r2/cell306-pending-result` → blob 0ac46b3d2abe497084ddf7631d894bb819e6ddc6 (the result).
- No other ref exists under refs/c12r2, refs/c12r1 or refs/c12.

**I1 historical evidence:**
- level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/phase_d5/C2_D5_FORECAST.json, blob a191557f, one commit
  5a94568a (2026-09-20), `cells['306'].Gamma_exact`.
- level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/adjudication/C2_ADJUDICATION.md, blob cfc5b3ed, one commit
  ae4cbc2c (2026-09-21), §K "Applying it".
- level4/closure_proofs/p5y_k5_tail_c2_closure/phase_d/CELL_306_ADOPTION.md, blob f5db4cd9 (last commit 87004e2b,
  an ancestor of ae4cbc2c), line 130 (the ×1.25 row).
- level4/closure_proofs/p5y_k5_tail_c10_governance_provenance/evidence/phase5/C10_GOVERNANCE.json, blob bc3fb1e6,
  `Q2_phase11_cell306` (last commit ec969db1 = the C10 adjudication commit); C10's adjudication ADJUDICATION_C10.md
  (blob adc0d0e0, one commit ec969db1).
- I1 registries (cell-306 blocks, `certified` flags and block bounds only): REGISTRY_C1.json blob f6d84bdb,
  REGISTRY_C2.json blob 1a3adfd3.

**The N9 chain:**
- ADJUDICATION_C11RD_N9.md, blob c3e001a7, one commit 7d67989d, line 2 `N9_CLOSED` (exactly one such line).
- C11RD_ADJUDICATION_REVIEW.md, blob 3c716c70, one commit fb237288, line 2 `ADJUDICATION_ACCEPTED` (exactly one).
- C11R_COMPARISON.json, blob 5269c2aa, one commit 2c24a989; its review REVIEW_C11R_COMPARISON.md, blob a1d33960, one
  commit 7375b9cd, final line `VERDICT: COMPARISON_ACCEPTED`.
- C11RD_COMPARISON.json, blob 7151f57a, one commit 8e2defab; its review C11RD_COMPARISON_REVIEW.md, blob 7c7cad00,
  one commit 90265349, line 2 `COMPARISON_ACCEPTED`.
- C11RD_RUNS.json, blob 30e2dfd0 (sha256 prefix c28a8cea), one commit 4547bcd4, status CERTIFIED, cell 306.

**Other:** r5 K5_COVERAGE_MAP_R5.json blob f978eeb6 (one commit ae4cbc2c); the r6 generator
code/c12r2_r6_from_adjudication.py blob 1355f795 (read for the verdict vocabulary only; not run).

## 2. Commands I ran (all read-only)

- `git branch --show-current`, `git status --short` (once, at the start), `git log --oneline -15`.
  - The index mtime is 16:28:51+09:00, the time of commit 33b5f183. That is before this session began, and it was
    unchanged after every later step. So the one plain `git status` did not rewrite the index. Every later status
    ran as `GIT_OPTIONAL_LOCKS=0 git status --porcelain --ignored --untracked-files=all`, and printed 0 lines before
    and after the only script execution.
- `git log --all` per path for the floor r2 namespace, the C12-R2 namespace, all result, authorization and
  execution paths of C12, C12-R1 and C12-R2, `*CELL306_RESULT*` and `*K5_COVERAGE_MAP_R6*`.
- `git log --format='%H %ad | %cd' a15d083b^..HEAD`; `git rev-parse <c>^@` for every chain commit;
  `git merge-base --is-ancestor` for a15d083b, 3fadb422, 7d67989d and fb237288 against 11f91daf, dec92e09 and 276f4d41,
  and for the last commit of each multi-commit historical file against its verdict commit.
- `git rev-parse <rev>:<path>` for every floor r2 file at a15d083b, 3fadb422, 11f91daf, dec92e09 and HEAD, plus
  `git hash-object` of the worktree copies; `git diff 3fadb422 HEAD -- <floor r2>` (0 lines).
- `git for-each-ref refs/c12r2 refs/c12r1 refs/c12`; `git reflog show` for both refs (none);
  `git ls-tree` of the result at 276f4d41 and HEAD; `git show --stat` of dec92e09, 276f4d41, 1173670f and 33b5f183;
  `git cat-file -t` of the probe blob b83cc6f5 and trial commit def4e453; `git log -1` of def4e453.
- `git diff --name-only 3fadb422 HEAD` and `git diff --name-status 1173670f HEAD`.
- `stat`, `ls -A` and a symlink test on the result file and execution directory; a listing of the git dir for an
  emergency file.
- `sed`/`cat`/Read of: the floor rule, gate, specification and review; the C12-R2 protocol, freeze, grant, execution
  review and the relevant parts of the qualification review; C2 §K; C10 `Q2_phase11_cell306`, README lines 95-106,
  ADJUDICATION_C10 lines 150-160 and REVIEW_C10_GOVERNANCE lines 320-340; N9 adjudication §4-§5 (lines with long
  numerals filtered out); the driver's supply, evaluation and decision functions (lines 433-624) and constants;
  C2's `combine` and `direct` pass definition; the r6 generator's verdict parsing; the operator's apply script in
  full.
- python3.14 -I -S -B one-liners that parse committed JSON and print only keys, statuses, classes, statements,
  booleans, hashes and the sealed Γ values:
  - self-hash checks of the floor rule, the gate, the freeze and the sealed result;
  - the 32 frozen input pins (sha256 and blob) and the 5 frozen files;
  - the sealed result's non-numeric fields;
  - the sign of the three exact Γ strings with `fractions.Fraction` (C2's `cells['306'].Gamma_exact`, the sealed
    control, the sealed target), and exact string equality of the control with C2;
  - the pending, committed and worktree bytes of the result and their SHA-1 blob id;
  - the classes, statements and domains of both comparisons, and the statuses and drift domains of C11RD's runs;
  - the `certified` flags and block bounds of the I1 registry blocks for cell 306;
  - a boolean-only check that I2's four C11R constants satisfy the consumer precondition;
  - r5's non-numeric keys and m = 5 open cells.
- A read-only helper in my scratch directory (history_check.py) that runs `git log --all`, `git rev-parse` and
  `git hash-object` for 44 historical files.
- The operator's read-only script, once, into scratch:
  `cd …/floor_application && python3.14 -I -S -B c12r2_floor_r2_apply.py --out-json <scratch>/APPLY.json --out-md <scratch>/APPLY.md`
  → `FLOOR-R2 APPLICATION: checks 21/21; base True; F1' False; F2 False; criterion NOT_MET`, exit 0. Its output
  is identical to the committed C12R2_FLOOR_R2_APPLICATION.json in every field except HEAD (1173670f committed, 33b5f183
  now). I read the script in full first: it imports only argparse, hashlib, json, subprocess, sys, fractions and
  pathlib; it runs only git read commands with `GIT_OPTIONAL_LOCKS=0`; it writes only its two `--out` files.

I did not run c12r2_cell306.py in any mode, c12r2_verify.py, c12r2_grant.py, the r6 generator, c2_d5_forecast,
tct_rule, deflated_consume, tail_forecast_r2 or any certifier, comparator or runner.

## 3. Items 1-16

### 1. Floor r2 is the correct authoritative adoption rule for cell 306 — VERIFIED

- **C2 authorises a replacement.** C2 Condition 1 makes r1 the standard for K5 m = 5 tail adoptions,
  prospectively, and lets a successor replace it if the replacement is frozen before recomputation. C2 §K names this
  exact route for 306: close N9 with a second, independently written certifier, then freeze a floor requiring
  agreement between two implementations rather than F1. C10 Q2 confirms a successor may freeze a new prospective
  rule and may target 306 prospectively.
- **r1's F1 has lapsed.** By r1's own text, F1 lapses when N9 is closed. N9 is CLOSED (7d67989d, reviewed
  ADJUDICATION_ACCEPTED at fb237288).
- **r2 is in force.** Its status on commit was PROPOSED until a fresh review returned REPLACEMENT_FLOOR_ACCEPTED and
  that review was preserved alone. Both happened: 3fadb422 adds only the review and its rerun JSON.
- **Scope covers 306.** Its `scope.operative_scope_of_this_campaign` is cell 306 only, and
  `cell_306_future_adoption_criterion` is the governing criterion.
- **C12-R2 binds exactly this rule.** Its freeze pins the rule (blob 0ddfac30, sha256 eb2b4196…), the gate
  (89b86218) and the review (ad73021b), and its lineage lists a15d083b and 3fadb422. The sealed result names
  "r2 (rule a15d083b, review 3fadb422)".
- **No competing rule.** No later floor exists in any ref's history.

### 2. Floor r2 was frozen before the I2 target result — VERIFIED

| event | commit | committer date (+09:00) |
|---|---|---|
| floor r2 rule | a15d083b | 2026-09-27 00:22:36 |
| floor r2 review preserved | 3fadb422 | 2026-09-27 01:28:01 |
| C12-R2 freeze | 11f91daf | 2026-09-27 14:44:23 |
| grant | dec92e09 | 2026-09-27 15:40:36 |
| execution start (record) | — | 2026-09-27 15:41:48.398872 (06:41:48Z) |
| seal | 276f4d41 | 2026-09-27 15:41:50 |

- a15d083b and 3fadb422 are ancestors of 11f91daf, dec92e09 and 276f4d41.
- The history is linear: every commit from a15d083b to HEAD has one parent.
- Every floor r2 file has the same blob at 3fadb422, 11f91daf, dec92e09 and HEAD, and in the worktree.
  `git diff 3fadb422 HEAD -- level4/closure_proofs/p5y_k5_tail_floor_r2/` is empty. Across all refs, the namespace
  is touched only by a15d083b and 3fadb422.

### 3. The floor was not changed after the result was observed — VERIFIED

- No commit after 276f4d41 touches floor r2. `git diff --name-only 3fadb422 HEAD` lists only files in the C12,
  C12-R1 and C12-R2 namespaces. The two commits after the seal add only the execution review (1173670f) and the three
  floor_application files (33b5f183).
- Both config self-hashes still verify. The freeze pins still match byte for byte, and the sealed record's
  `input_sha256.floor_rule`, `floor_gate` and `floor_review` equal the frozen pins.

### 4. The I1 evidence is historical and committed — VERIFIED

- C2_D5_FORECAST.json is blob a191557f, with a single commit 5a94568a on 2026-09-20. That is seven days before floor
  r2 and before N9 closed.
- The sealed control's `Gamma_exact` equals C2's committed `cells['306'].Gamma_exact` **exactly, as strings**. Both
  are 1,531 characters, and the string sha256 is 148aac9a….
- Both parse with `fractions.Fraction` to the same canonical value: `str(Fraction(s)) == s`.
- The sealed control also records `reproduces_C2_exactly` true, with all 7 `field_matches` true. Its supply is
  "S_I1 = min{G, C1, C2}", with provenance C2 on A0, A1 and A2, which equals C2's own recorded provenance for 306.

### 5. The I2 evidence comes from the unique authorized execution — VERIFIED

- **One result commit.** `git log --all -- <result path>` returns exactly 276f4d41. No C12 or C12-R1 result path
  has any history, and `*CELL306_RESULT*` appears in exactly one commit across all refs.
- **The marker.** `refs/c12r2/cell306-target-consumed` points at dec92e09, the grant. The sealed record's
  `grant.grant_commit` and `seal_preconditions.branch_head` are also dec92e09.
- **Nothing else.** No other ref exists under refs/c12r2, refs/c12r1 or refs/c12.
- **The seal's parent is the grant** (NB10): `276f4d41^` = dec92e09.
- **The record.** It says `target_evaluations` 1, `target_evaluated` true and status TARGET_EVALUATED.
- **The grant chain.** The grant binds freeze 11f91daf, qualification 107a8b36 and review e19f4edd (verdict
  QUALIFICATION_ACCEPTED). Its hashes equal the frozen files: driver 5c45b4de, verifier 3c748f11, r6 generator
  23a831c9, grant generator 83ec10cc, protocol 874a5610, freeze record 23deb827.
- **Before the grant.** The qualification at 107a8b36 records 0 real target evaluations, no markers or pending refs,
  no result objects, no grant and no seal.
- **Accepted by review.** The execution review's object-store scan found exactly one result-schema blob (0ac46b3d)
  and exactly one trial commit (def4e453, parent dec92e09). I confirmed both objects still exist.

### 6. The I2 seal is valid — VERIFIED

- These are all the same bytes, blob 0ac46b3d2abe497084ddf7631d894bb819e6ddc6:
  - the pending-ref blob;
  - `HEAD:<result>`;
  - the blob at 276f4d41;
  - the worktree copy, by `git hash-object` and by Python SHA-1 of `blob 19937\0` + bytes.
- The `git cat-file` bytes of the pending ref and of HEAD are byte-identical to the worktree file.
- **Mode.** `ls-tree` gives `100644 blob 0ac46b3d…` at 276f4d41 and at HEAD. The worktree file is `-rw-r--r--` with
  nlink 1, and the execution directory is not a symlink and holds only this file. There is no emergency file in the
  git dir.
- **Self-hash.** The record's `sha256` (9405f469…) equals the sha256 of `json.dumps(body, sort_keys=True)` without
  it. The file is exactly the `indent=1, sort_keys=True` serialization plus a newline.
- **Input pins.** The record's `input_sha256` (32 keys) equals the frozen `input_pins_sha256`, and its
  `driver_sha256` equals the frozen driver hash.

### 7. The execution review was accepted — VERIFIED

- review/C12R2_EXECUTION_REVIEW.md: line 2 is exactly `EXECUTION_ACCEPTED`, and it is the only such line.
- It has one commit, 1173670f, which adds only that file. Its parent is the seal. Blob 191d8a9d equals the worktree
  copy.
- It reports 0 blockers and 8 non-blocking notes. I read all 8; §11 carries them over.

### 8. The exact sign of Γ(5, 306; S_I2) — POSITIVE (read from the sealed exact rational)

- **The sealed string.** `target.evaluated.Gamma_exact` is a 1,484-character rational `p/q`, string sha256
  8ef2815cd478b43b05605e0ddefebd318568446194090327ffabc0e50b59e194. Its first character is a digit, not `-`.
- **Parsed.** `Fraction(s)` is canonical (`str(Fraction(s)) == s`), `> 0` is True and `== 0` is False. So the sign is
  **+1**.
- **Other fields agree.** The sealed float is 0.005159101140006536, and the sealed `pass` is false.
- **Control, for completeness.** Γ(5, 306; S_I1) has sign **−1**. Its float is −0.030469257709306738, and `pass` is
  true.
- **No tolerance exists.** `quantity_compared.criterion` is "strict sign: Gamma < 0 (exact rational arithmetic;
  Gamma = 0 or an incomplete evaluation fails)", and `numerical_agreement_threshold.adoption` says there is "no ratio
  threshold". The consumer's own pass flag is `Gam < 0` (c2_d5_forecast.py line 89).
- **None was applied.** I used no tolerance. The sealed value is strictly positive, so no boundary case arises.

### 9. No I1/I2 constant mixing — VERIFIED

- **Control.** Supply "S_I1 = min{G, C1, C2}", provenance C2 on A0, A1 and A2. It holds only I1 sets: the REGISTRY_C1
  and REGISTRY_C2 blocks for 306, both `certified` true on [680769/400000, 17885921/10000000]. Lemma G is
  registry-free and is part of every S_I by the rule's own definition (`quantity_compared.supplies.S_I`).
- **Target.** Supply "S_I2 = min{G, I2}", provenance I2 on A0, A1 and A2. It holds only the I2 set:
  - C11R `per_target[C_T, tau, Abar, D_lo].independent_value`;
  - C11RD `per_target[D1, D2].independent_value`, required equal to the sealed runs' values.
- **Enforced in the driver.** The frozen `supply()` (D:556-565) refuses any set whose `impl` tag differs, and any
  duplicate. S_I1 and S_I2 are built by separate calls. The chosen supply for the base clause is S_I1, as floor r2
  fixes it (`cell_306_future_adoption_criterion.chosen_supply`).
- **No component crossed.** The per-field provenance shows that no field of either supply came from the other
  implementation, and none came from G.

### 10. F1′ applied literally, clause by clause — see §5 below. Result: F1′ FAILS (clause (d)).

### 11. F2 from historical frozen evidence only; never re-run — VERIFIED

- **The historical classification.** C2 §K "Applying it" (committed ae4cbc2c, 2026-09-21): for cell 306, "F2 — Γ at
  every constant × 1.25: +0.029163 → does not close. FAILS F2"; uniform-A margin 1.1277.
- **Corroboration.** CELL_306_ADOPTION.md line 130 gives the same ×1.25 row for 306 (+0.029163, "does not close").
  C10 `Q2_phase11_cell306` gives `F2_passes` false, with an imported uniform-A margin of 1.1714309…. That is the most
  favourable of three unreconciled historical margins (1.1277, 1.1555 and 1.171431), and C10's adjudication records
  that "306 fails F2 on all three".
- **Floor r2 does not revisit it.** `known_historically` reads: "C2 published that F2 fails for cell 306 on S_I1;
  this rule does not revisit that". Gate G12 requires any re-evaluation to bind C2's F2 procedure and to stop on a
  different result.
- **C12-R2 did not re-evaluate it.** Its frozen decision table records F2 as "NOT_SATISFIED (C2 published FAIL on
  S_I1; not re-evaluated)". Its driver computes no degraded Γ: `decide()` sets F2 to a fixed string.
- **Neither did this phase.** The operator's script reads F2 from these committed texts only. I ran nothing that
  degrades or evaluates anything.

### 12. No new scientific computation in this phase — VERIFIED

- The only commit after the execution review is 33b5f183. It adds a script that reads committed bytes and the sign of
  exact rational strings, plus its two outputs.
- I ran only git read commands, JSON parsing, string comparisons, `Fraction` sign reads of sealed strings, and one
  boolean precondition check on committed I2 constants (no value printed).
- No Γ, atom constant, margin, degraded Γ or supply was computed, by the operator's script or by me.

### 13. No new supply search — VERIFIED

- **Both supplies were fixed before the result.** S_I1 is fixed by floor r2. The S_I2 construction is fixed by floor
  r2 and frozen in C12-R2 (11f91daf, code/ and protocol/ trees unchanged at 276f4d41 and HEAD).
- **No new evidence exists.** No file outside the C12, C12-R1 and C12-R2 namespaces changed since 3fadb422, so no new
  registry, constant set or certifier output exists.
- **Nothing was reconstructed afterwards.** After the positive S_I2 result, no alternative I2 supply, D′ mixed supply
  or cross-implementation minimum was constructed. Floor r2 forbids it (`disagreement.never`, G08).

### 14. No threshold or gate weakened — VERIFIED

- **Unchanged since 3fadb422:**
  - the per-constant factor 2;
  - the F2 factor ×1.25;
  - the strict `Γ < 0`;
  - the chosen-supply restriction;
  - the fail-closed list;
  - G00-G14.
- **The C12-R2 decision table is floor r2's table or stricter.**
  - With F2 historically failed, "floor_satisfied = base AND F1′" is equivalent to `base AND (F1′ OR F2)`.
  - Its adoption row adds EXECUTION_ACCEPTED and an accepted adjudication.
- **This adjudication weakens nothing.** It applies the rule as frozen.

### 15. Evidence for cells 307-309 not used — VERIFIED

- **The record.** The sealed record is cell 306 only. The driver's `cell_inputs` refuses cells outside (305, 306),
  and the 305 path is an I1-only qualification rehearsal.
- **My reads.** From C2_D5_FORECAST.json I read only `cells['306']` and top-level key names. The C2 §K table and the
  C10 section cover 305/306 and 306 only.
- **The operator's script** reads `cells['306']` only.
- **Nothing downstream.** No file for 307-309 changed after 3fadb422, and none entered any determination here.

### 16. Historical verdicts not rewritten — VERIFIED

Each file below has exactly the listed commit(s) in `git log --all`, and its worktree blob equals HEAD.

| campaign | file | commit(s) |
|---|---|---|
| C2 | C2_ADJUDICATION.md; K5_COVERAGE_MAP_R5.json | ae4cbc2c |
| C2 | C2_D5_FORECAST.json; REGISTRY_C2.json | 5a94568a |
| C2 | CELL_306_ADOPTION.md | 5 commits, last 87004e2b, an ancestor of the verdict ae4cbc2c |
| C10 | ADJUDICATION_C10.md | ec969db1 |
| C10 | REVIEW_C10_GOVERNANCE.md | 7f255f3d |
| C10 | C10_GOVERNANCE.json; README.md | 3 commits each, the last being the adjudication commit ec969db1 |
| C11 | ADJUDICATION_C11.md | 25475205 |
| C11R | ADJUDICATION_C11R_N9.md | 118008f5 |
| C11R | REVIEW_C11R_AUTHORIZATION / _COMPARISON / _EXECUTION / _QUALIFICATION | 9bd17be5 / 7375b9cd / 22537709 / 445fd84e |
| C11R | C11R_COMPARISON.json; C11R_RUNS.json | 2c24a989; 5ff4cc5b |
| C11R | C11R_N9_STATEMENTS.json | 6 pre-result commits, last dbd6cd89, an ancestor of ee1a6a8a and 5ff4cc5b |
| C11RD / N9 | ADJUDICATION_C11RD_N9.md; C11RD_ADJUDICATION_REVIEW.md | 7d67989d; fb237288 |
| C11RD | authorization / comparison / execution reviews | e320d8f5 / 90265349 / db1c6118 |
| C11RD | pre-execution and qualification reviews | 663f8fe7, 3c1eff11, 89330534, e27c2ffd |
| C11RD | C11RD_COMPARISON.json; C11RD_RUNS.json | 8e2defab; 4547bcd4 |
| floor r2 | rule, gate, specification; review | a15d083b; 3fadb422 |
| C12 | C12_QUALIFICATION_REVIEW.md (QUALIFICATION_REJECTED); C12_CAMPAIGN_STATUS.md | 2cdfa467; eba56027 |
| C12-R1 | C12R1_QUALIFICATION_REVIEW.md (QUALIFICATION_REJECTED); C12R1_CAMPAIGN_STATUS.md | e89402c1; 13e06db0 |
| C12-R2 | qualification; qualification review; grant; seal; execution review | 107a8b36; e19f4edd; dec92e09; 276f4d41; 1173670f |
| C12-R2 | protocol and freeze | 11f91daf |

The multi-commit files were all last changed inside their own campaign, before or at its verdict. None was touched
afterwards.

## 4. Gate G00-G14 (CELL306_ADOPTION_GATE_R2.json)

| gate | status | basis |
|---|---|---|
| G00 floor r2 in force | PASS | a15d083b and 3fadb422 are ancestors of 11f91daf; the rule is byte-identical (0ddfac30) and its self-hash verifies |
| G01 N9 CLOSED | PASS | 7d67989d holds exactly one `N9_CLOSED` line, and fb237288 exactly one `ADJUDICATION_ACCEPTED` line; both blobs are unchanged |
| G02 entry state | PASS | r5 f978eeb6 byte-identical; union open [[306, 309]]; K5_COVERAGE_COMPLETE false; no r6 in any history, tree or disk; 307-309 untouched |
| G03 prospective freeze | PASS | 11f91daf pins 32 inputs, the consumer path, S_I1, the S_I2 construction and the decision table; qualification records 0 real target evaluations |
| G04 I1 inputs | PASS | pins registry_c1 f6d84bdb, registry_c2 1a3adfd3, c2_d5_forecast 18403dbe, deflated_consume a0a836fa and tct_rule 98f6eee4; also tail_forecast_r2 edec817e and every non-supply input (floor review N5 repaired) |
| G05 I2 inputs | PASS | C11R_COMPARISON 5269c2aa; C11RD_COMPARISON at 8e2defab (7151f57a); C11RD_RUNS at 4547bcd4 (30e2dfd0); all six statements EQUIVALENT or STRONGER with domain EQUAL; C11R's drift domain and C11RD's D1/D2 statements are exactly [680769/400000, 17885921/10000000] |
| G06 per-constant agreement | PASS | C_T, tau and D_lo AGREES; Abar, D1 and D2 STRONGER; no independence violations in either comparison; comparisons accepted (7375b9cd, 90265349) |
| G07 soundness evidence and residuals | PASS | the five soundness documents are pinned and unchanged; residuals restated in §10 below, since C12's protocol assigns that disclosure to the adjudication |
| G08 no mixing | PASS | item 9 |
| G09 validation and κ | PASS | both evaluations completed (validation precedes evaluation in `atoms()`); my boolean check of I2's C11R constants passes; κ is equal between consumer and C2 copy, enforced in `load_consumer` |
| G10 control | PASS | exact string reproduction of C2's `Gamma_exact`, before S_I2 (item 4) |
| G11 one sealed evaluation | PASS | items 5 and 6 |
| G12 decision by the table only | APPLIED | §5: base holds; F1′ fails; F2 fails historically; so do not adopt |
| G13 independent reviews and adjudication | PASS for the execution review; this document is the adoption adjudication, and it still needs its own review | — |
| G14 scope | PASS | item 15; r5 unchanged; historical verdicts untouched (item 16) |

The gate's fail-closed clause ("any failure stops the campaign without a decision") is not triggered. Every item up
to G11 passes, so the decision in G12 is reached on the merits, and it is non-adoption.

## 5. Floor r2, clause by clause

| clause | frozen text (floor r2) | finding | supporting committed artifact |
|---|---|---|---|
| chosen supply | S_I1 = C2's adopted supply (componentwise minimum over Lemma G and Lemma Dv′ r2 of the I1 registries), single-implementation, fixed before any evaluation | S_I1 = min{G, C1, C2}, I1 only; fixed by the rule itself | K5_TAIL_ADOPTION_FLOOR_R2.json `cell_306_future_adoption_criterion.chosen_supply`, `rule.chosen_supply_restriction`; sealed control `supply`/`provenance` |
| **base** | "only if the frozen K5-B certifies it (Gamma < 0 …) evaluated on the campaign's CHOSEN SUPPLY" | **HOLDS.** Γ(5, 306; S_I1) has sign −1 (−0.030469257709306738). It is C2's committed string exactly, so the control does not fail closed. | C2_D5_FORECAST.json a191557f `cells['306'].Gamma_exact`; C12R2_CELL306_RESULT.json 0ac46b3d `control` |
| **F1′(a)** | two independent implementations have each certified the six operator constants on the cell's whole drift block | **HOLDS.** I1: REGISTRY_C1 and REGISTRY_C2 blocks for 306, `certified` true on [680769/400000, 17885921/10000000]. I2: C11R C_T, tau, Abar and D_lo `target_status` CERTIFIED, domain EQUAL; C11RD runs status CERTIFIED, D1 and D2 drift domain equal to the block. Independence is code and implementation independence per C11R; no independence violations are recorded. | REGISTRY_C1 f6d84bdb; REGISTRY_C2 1a3adfd3; C11R_COMPARISON 5269c2aa; C11RD_RUNS 30e2dfd0; floor `independence` |
| **F1′(b)** | compared under the frozen N9 rule, every constant AGREES or STRONGER, every statement EQUIVALENT or STRONGER, in an independently reviewed and accepted comparison | **HOLDS.** C_T AGREES/EQUIVALENT; tau AGREES/EQUIVALENT; Abar STRONGER/EQUIVALENT; D_lo AGREES/STRONGER (lower bound, premises FEWER); D1 STRONGER/EQUIVALENT; D2 STRONGER/EQUIVALENT. The comparisons were accepted (7375b9cd; 90265349), and N9 is CLOSED (7d67989d / fb237288). I1's compared set is the REGISTRY_C2 block (floor review N2). | C11R_COMPARISON.json; REVIEW_C11R_COMPARISON.md; C11RD_COMPARISON.json; C11RD_COMPARISON_REVIEW.md; ADJUDICATION_C11RD_N9.md; C11RD_ADJUDICATION_REVIEW.md |
| **F1′(c)** | each implementation carries the soundness evidence in `soundness_evidence` | **HOLDS.** I1: C2's two-pass re-certification and the C2 adjudicator's independent re-derivation (CELL_306_ADOPTION.md f5db4cd9, C2_ADJUDICATION.md cfc5b3ed). I2: C11R's sealed runs and accepted chain; C11RD's theory, validation and accepted chain (C11R_RUNS a5351603, D1_D2_DERIVATION.md 803f0145, C11RD_INDEPENDENCE_AUDIT.md 571c2d92). All are pinned by sha256 and blob in the freeze and are unchanged. Residuals are disclosed in §10. | C12R2_FREEZE.json `soundness_*` pins; floor `soundness_evidence` |
| **F1′(d)** | "Gamma(5, k; S_I) < 0 holds for EACH of I = I1 and I = I2 SEPARATELY" | **FAILS.** I1: Γ(S_I1) < 0 holds (sign −1). I2: Γ(S_I2) < 0 does **not** hold: the sealed exact rational is strictly positive (sign +1; float 0.005159101140006536; `pass` false). | C12R2_CELL306_RESULT.json 0ac46b3d `target.evaluated.Gamma_exact` (sealed 276f4d41, EXECUTION_ACCEPTED 1173670f) |
| **F1′** | (a) and (b) and (c) and (d) | **FAILS.** This is a *closure disagreement* under `disagreement.closure`: "Gamma(5, k; S_I1) < 0 but Gamma(5, k; S_I2) >= 0 … F1' FAILS for that cell and the disagreement is recorded; no adoption under F1'". It is recorded in §6. | floor `rule.limbs.F1_prime`, `disagreement.closure` |
| **F2** | "Gamma < 0 still holds when every atom constant of the chosen supply is degraded uniformly … by the factor x1.25, i.e. the cell's uniform-A margin is >= 1.25" | **FAILS** (historical, not re-run). Γ at ×1.25 on S_I1 is +0.029163 (does not close); uniform-A margin 1.1277 < 1.25. The C10 corroboration also has `F2_passes` false. | C2_ADJUDICATION.md §K "Applying it"; CELL_306_ADOPTION.md line 130; C10_GOVERNANCE.json `Q2_phase11_cell306`; floor `known_historically` |
| **floor-r2 eligibility** | base AND (F1′ OR F2) | **NOT MET:** TRUE AND (FALSE OR FALSE) = FALSE | floor `rule.base`; gate G12; `fail_closed` "neither F1' nor F2 established: DO NOT ADOPT; the cell stays OPEN in the coverage map" |

**On the operator's mechanical application.** I verified it rather than relied on it. Its 21 checks reproduce, and
every conclusion above was reached from my own reads.
- Its F1′(a) row asserts I1 certification without checking the registry flags, which I checked.
- Its F1′(c) row checks only that the soundness files are pinned and unchanged, which is the right scope for (c).

Neither gap affects the outcome, because F1′ fails on (d) whatever (a)-(c) are.

## 6. Determinations

- **Scientific closure under I1: YES.** Γ(5, 306; S_I1) < 0: the exact rational has sign −1 and is C2's committed
  value. The frozen K5-B certifies cell 306 on I1's own supply. This is unchanged historical science (C2, 2026-09-20).
- **Scientific closure under I2: NO.** Γ(5, 306; S_I2) is strictly positive, so the frozen K5-B does **not** certify
  cell 306 on I2's own supply.
  - This is non-certification by that supply. It is not a proof that cell 306 fails to close. A positive Γ on an
    upper-bound supply is not a certificate of the opposite.
  - It is therefore not a two-sided contradiction (SCIENTIFIC_DISAGREEMENT). The comparisons record no
    opposite-direction pairs.
- **Closure disagreement recorded** (floor r2 `disagreement.closure`). Γ(S_I1) < 0 and Γ(S_I2) > 0. Under the rule,
  no re-evaluation, parameter change or supply change may follow in this campaign (`disagreement.never`).
- **F1′ eligibility:**
  - (a) holds;
  - (b) holds;
  - (c) holds;
  - (d) **fails**, on I2.

  So **F1′ fails.**
- **F2: fails**, on historical frozen evidence only (C2 §K), not re-run.
- **Base clause: holds.** Γ on the chosen supply S_I1 is < 0.
- **Floor-r2 eligibility: NOT MET.** base AND (F1′ OR F2) = TRUE AND (FALSE OR FALSE) = FALSE.
- **Adoption status of cell 306: NOT ADOPTED.** Cell (m = 5, k = 306) stays OPEN.

## 7. Scientific validity versus adoption eligibility

These are separate questions, with separate answers:
- **The C12-R2 execution is scientifically valid** (EXECUTION_ACCEPTED, 1173670f).
  - The one authorized evaluation of Γ(5, 306; S_I2) ran exactly once, at the grant, under the marker. It used the
    frozen consumer path on pinned inputs, and was sealed from memory before interpretation.
  - The control reproduced C2 exactly.
  - Its result, a strictly positive Γ on I2's supply, is a correct and trustworthy fact about that supply.
  - Nothing in this adjudication questions it.
- **Adoption eligibility under floor r2 is not met.** The floor asks for single-fault tolerance: closure under
  **each** implementation's own supply. A valid execution that shows I2's supply does not close fails that
  requirement.
  - Under the frozen rule, validity of the execution is necessary for adoption but not sufficient.
  - A valid negative outcome is still a negative outcome.
- **Neither answer changes the other.**
  - Non-adoption does not make the execution invalid.
  - It does not retract C2's finding that I1's supply closes cell 306.
  - It does not reopen N9 (N9_CLOSED stands as a trust condition on the constants, which the per-constant comparison
    established).
  - It is not a scientific finding that cell 306 is unclosable.

## 8. Coverage consequence

- Cell (m = 5, k = 306) **stays OPEN**.
- **r5 remains authoritative:** K5_COVERAGE_MAP_R5.json, blob f978eeb6, m = 5 open cells [306, 307, 308, 309], union
  open ranges [[306, 309]], `K5_COVERAGE_COMPLETE` false.
- **r6 must not be created.** The frozen r6 generator requires line 2 of this adjudication to be the adopting token,
  with an adopted cell set of exactly [306]. Neither is present, so the generator must refuse, and it must not be
  run.
- **K5 remains PARTIAL.**
- Cells 307-309 are unaffected and remain open. Nothing here concerns them.
- C12-R2's exactly-once protocol is spent. The marker and the pending ref must stay where they are. Floor r2 forbids
  any re-evaluation or supply change in this campaign after the disagreement. Any future attempt on 306 would need
  its own separate instruction and its own prospective freeze under C2 Condition 1.

## 9. Execution-review notes carried over

All 8 notes of review/C12R2_EXECUTION_REVIEW.md are non-blocking. None bears on the sign of the sealed Γ.
- **Post-seal `execute` and `seal-only` runs (NOTE 2)** were refusal and verification probes, not scientific
  executions.
  - Each extra `execute`, the operator's and the reviewer's, was refused `CONSUMED` (exit 2) before any write or
    evaluation.
  - Each `seal-only` found the seal and the worktree copy already in place and printed "nothing computed" (exit 0).
  - The reviewer's before and after snapshots were identical.
  - Exactly-once is unaffected: the real evaluation count is 1.
- **NB10.** The seal's parent is the grant. I also verified that `276f4d41^` = dec92e09.
- **The grant records the authorization only as generator text (NOTE 1).**
  - `authorization.source` is fixed text from the frozen c12r2_grant.py. The user's actual words, the time and the
    narrower chat scope are not in the repository.
  - The grant authorizes one `execute` only. It does not cover floor application, adoption or r6.
  - This adjudication was separately instructed by the caller.
- **Concurrent unrelated p5y-k4\* ref movement (NOTE 4).**
  - During the execution review, `refs/heads/p5y-k4-frozen-execution-r1` moved (5289b6ce → bc4ba08e), and
    `refs/heads/p5y-k4r1-nearzero-successor` and `refs/remotes/origin/p5y-k4-frozen-execution-r1` appeared.
  - All of it came from another worktree sharing the common git dir. It touched neither this branch nor refs/c12r2.
  - I observed no such effect on anything adjudicated here: the branch, the c12r2 refs and all bound blobs are as
    stated.
- **The leftover probe blob and trial commit (NOTE 8)** are to be retained until this adjudication and its review
  are final. They are the probe blob b83cc6f5 and the unreferenced trial commit def4e453 (parent dec92e09; tree =
  the grant tree). Both still exist (`git cat-file -t`: blob, commit).
- **The other notes, for the record.**
  - NOTE 3: the worktree index was rewritten about 57 s after the seal, by a stat refresh. Its content is correct.
  - NOTE 5: the operator's pre-freeze dry runs were in a scratch clone and evaluated no target.
  - NOTE 6: the qualification review's latent residuals were not triggered.
  - NOTE 7: the seal's reflog entry has an empty message.

## 10. G07 residual disclosure (carried into this adjudication per C12's gate mapping)

- **I1.**
  - N10 remains OPEN: REGISTRY_C2.json records no build host, toolchain or precision.
  - I1 was never independently re-implemented before C11R/C11RD.
  - The "six-constant agreement with I2" in I1's evidence list is at most conditional corroboration (floor review N1).
- **I2.**
  - The comparison cannot detect unsoundness in the STRONGER direction (N2).
  - Independence is at the implementation and code level, not independent authorship (N3). I2's author had seen the
    original D1/D2 values before C11RD's freeze (C11RD_INDEPENDENCE_AUDIT.md).
  - C11RD's propagation used the exact supremum of C11R's C_T, which is below the outward-rounded C_T record by about
    3.7e-97 (N1). S_I2 uses the outward-rounded record, which is the conservative choice.
- **Common-mode residual.** Both implementations share the frozen model, the kernel definition, the derivative
  theory, Lemma G, κ and the consumer.

None of these residuals affects this decision. Non-adoption follows from the sealed sign of Γ(S_I2), which F1′
requires to be negative whatever the soundness of either implementation.

## 11. Reservations

1. **This decision is final only after review.** It becomes effective only after an independent adjudication
   review returns ADJUDICATION_ACCEPTED and that review is preserved.
   - Until then, this document creates no coverage change. It would create none in any case, because it does not
     adopt.
2. **The historical F2 figures disagree, but not in any way that matters.** The committed record carries three
   unreconciled uniform-A margins for 306 (1.1277 in C2 §K, 1.1555, and 1.171431 in C8/C10). All are below 1.25, and
   C2 published the ×1.25 Γ for S_I1 directly as +0.029163. So F2's classification does not depend on which margin
   is right.
3. **Non-certification is not non-closure.** This adjudication does not assert that cell 306 is scientifically
   non-closable. I1's supply does close it, soundly as far as C2 established. The floor withholds adoption because
   that closure lacks single-fault-tolerant support. I2's supply does not reproduce it, and the historical
   degradation test also fails.
4. **The scope of item 12 is this phase.** The C12-R2 execution itself (2026-09-27 06:41:48Z-06:41:50Z) did compute
   exactly one Γ(S_I2) and one control Γ(S_I1). That was the authorized, sealed and accepted scientific step. Nothing
   was computed after it.
5. **The mechanical application is not authority.** It was prepared by the campaign operator and committed at
   33b5f183. I treated it as a claim, and my conclusions rest on the committed evidence above. Its conclusion
   (base TRUE, F1′ FALSE, F2 FALSE, NOT_MET) agrees with mine.
6. **The first `git status` of this session** ran without `GIT_OPTIONAL_LOCKS=0`. The index mtime (16:28:51+09:00)
   predates the session and never changed, so it wrote nothing.

## 12. Confirmation

- **I modified nothing in /Users/suzhe/ReBaseGuard-k5c11rd.** I ran no git write command, and created or modified no
  file or ref there.
  - HEAD is 33b5f183 before and after.
  - `GIT_OPTIONAL_LOCKS=0 git status --porcelain --ignored --untracked-files=all` printed 0 lines before and after the
    one script execution, and the index mtime is unchanged.
  - No `__pycache__` was created (every Python run used `-I -S -B`).
- **I computed nothing scientific.**
  - I recomputed no Γ and no atom constant under any supply.
  - I did not re-run F2, and constructed or searched no supply.
  - I did not run the C12-R2 driver in any mode, the verifier, the grant generator, the r6 generator or any consumer
    (c2_d5_forecast, tct_rule, deflated_consume, tail_forecast_r2).
  - The only arithmetic was reading the sign of sealed exact rational strings, and one boolean precondition check on
    committed constants, which printed booleans only.
- **I disclosed no D1/D2 value.** I printed, wrote and quoted no numeric value of D1 or D2, original or independent.
- **Nothing else was touched.** I did not open C11R's quarantine. I used no AWS or Vultr tool, no network and no
  session transcript.
- **Where I wrote.** Only in
  /private/tmp/claude-501/-Users-suzhe-ReBaseGuard/ea6191ae-93b1-4f9c-b9ba-6cd0430d32ee/scratchpad/c12r2_adjudication/:
  this file, history_check.py, APPLY.json and APPLY.md.
