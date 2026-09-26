# C12 — qualification review (cell 306 under floor r2)
QUALIFICATION_REJECTED

**Reviewer:** fresh, independent, read-only. I did not write any part of C12.
**Worktree:** /Users/suzhe/ReBaseGuard-k5c11rd, branch p5y-k5-tail-c11rd-d1d2-extension, HEAD aac6dae9.

## Reviewed commits

* **Freeze.** b9ffc87fd7f42a922a688facae7e0b6987239c91 (parent 3fadb422). It adds exactly five files: code/c12_cell306.py,
  code/c12_verify.py, code/c12_r6_from_adjudication.py, protocol/C12_PROTOCOL.md and protocol/C12_FREEZE.json.
* **Qualification.** aac6dae9fda929b9458e0dd41ebe9e9af3da18b5 (parent b9ffc87f). It adds exactly four files under
  evidence/qualification/: C12_QUALIFICATION.json, PREFLIGHT.json, REHEARSE_305.json and REHEARSE_306.json.
* **Frozen code bytes.** C12_FREEZE.json `frozen_files_sha256` verifies against the four code/protocol files. The
  driver's sha256 is c045e990…ac03. C12_FREEZE.json's self-hash verifies.

In the review below, "D" means code/c12_cell306.py, "V" code/c12_verify.py, "G6" code/c12_r6_from_adjudication.py,
"C2F" p5y_k5_tail_c2_closure/code/c2_d5_forecast.py and "P" protocol/C12_PROTOCOL.md.

## Commands run (all read-only; outputs only in this scratch directory)

1. Git reads: `git status --porcelain --ignored --untracked-files=all` (0 lines, before and after every step), `git show --stat`,
   `git diff --name-only 3fadb422 aac6dae9`, `git log --all -- <paths>`, `git rev-parse <commit>:<path>` for every pinned file
   at HEAD, b9ffc87f and 5a94568a, `git for-each-ref`, `git reflog`, `git worktree list`.
2. `python3.14 -I -S -B c12_cell306.py preflight --out …/PREFLIGHT.json`, which printed PREFLIGHT PASS (exit 0).
3. `python3.14 -I -S -B c12_cell306.py rehearse --cell 306 --out …/REHEARSE_306.json`: exit 0, reproduces C2 exactly.
4. `python3.14 -I -S -B c12_cell306.py rehearse --cell 305 --out …/REHEARSE_305.json`: exit 0, reproduces C2 exactly.
5. `python3.14 -I -S -B c12_verify.py --dry-run --out …/VERIFY_DRY.json`: 70/71. The single failure is "HEAD is the freeze
   commit of code/ and protocol/", as expected at aac6dae9.
6. Small read-only Python snippets that printed only structure, key names, booleans and counts:
   * pin, blob and self-hash checks;
   * registry-pin identity with C2's recorded registry hashes;
   * a boolean check that the Lemma-G supply built from ADOPTED_TAIL_INPUTS equals C2's recorded G supply;
   * a value-free leak scan for D1/D2 renderings over all C12 files and my outputs (0 hits).

**Reproduction of the committed evidence.** Runs 2-4 reproduce the committed PREFLIGHT/REHEARSE files exactly, apart from
utc, wall and rss. Run 5 reproduces every section of C12_QUALIFICATION.json (S, R, N, F, G, L) exactly, apart from T, and
the driver, verifier and r6-generator hashes are equal.

## Q1 — Freeze and temporal integrity

* **Freeze before any I2 Γ.** code/ and protocol/ were committed at b9ffc87f, and aac6dae9 touches none of them
  (`git diff --name-only b9ffc87f aac6dae9` lists only the four evidence/qualification files).
  * Nothing in the repository shows that any I2 Γ existed before the freeze. `git log --all` finds no path under
    evidence/execution and no C12_CELL306_RESULT, and no ref exists under refs/c12.
  * At b9ffc87f no qualification review and no grant exist, so none of V's sandbox execute controls could get past
    GRANT_MISSING or REVIEW_MISSING (see B1 for why this matters later).
  * The reflog shows only b9ffc87f → 96bd5406 → aac6dae9 (N10).
* **Only evidence/qualification/ files in aac6dae9.** Yes: 4 files, 419 insertions.
* **HEAD at qualification.** C12_QUALIFICATION.json:273 and :280 record T_temporal HEAD = freeze_commit = b9ffc87f. Line
  287 records dry_run false, and lines 282-289 record 71/71 and pass true. The section counts are S6 + T4 + R4 + N21 + F27
  + G6 + L3 = 71.
* **No consumed ref, result or r6.**
  * `refs/c12/cell306-target-consumed` does not exist (rev-parse rc=1), in the common ref store shared by every worktree.
  * No result exists, in the tree, in `git log --all`, or on disk in any /Users/suzhe/ReBaseGuard* worktree or in the temp
    directories.
  * No K5_COVERAGE_MAP_R6* exists anywhere: in the tree, in `git log --all -- '*K5_COVERAGE_MAP_R6*'`, or on disk in any
    worktree.

## Q2 — Faithful implementation of floor r2 and G00-G14

* **S_I1 is exactly C2's adopted supply.**

  | element | C2 (C2F) | C12 (D) |
  |---|---|---|
  | Lemma G supply | C2F:197 | D:339 |
  | C1/C2 blocks, argument order (Abar, tau, C_T, D_lo, D1, D2) | C2F:198-203 | D:61, D:351-358, D:401-407 |
  | combine insertion order G, C1, C2 (tie-break and provenance identical) | C2F:196-204 | D:414-419 |
  | `direct` call | C2F:205 | D:423 |

  * The pinned registries are the ones C2 consumed: C2_D5_FORECAST.json `registry_c1_sha256` and `registry_c2_sha256`
    equal D's pins (D:109-112).
  * κ is equal between the consumer and C2's copy (D:299-300).
  * The rehearsal reproduces C2's provenance, which is C2 on all three fields.
* **S_I2 is built only from Lemma G and the I2 six-constant set** (D:456, D:361-389). The values come from C11R
  `result.per_target[C_T,tau,Abar,D_lo].independent_value` and C11RD `per_target[D1,D2].independent_value`, and each of
  those must equal `C11RD_RUNS.targets[k].value` (D:384).
* **No mixing path.**
  * `supply` refuses any set whose tag differs from the requested implementation, and any duplicate name (D:412-417).
  * The tags are assigned only inside D (D:357, D:389).
  * G is common to both supplies, as floor r2 §4 defines.
* **Decision table.** D:465-477 matches P §3 and floor r2 §3/§10.
  * base = Γ(S_I1) < 0.
  * F1′ = base ∧ Γ(S_I2) < 0. Conditions (a)-(c) are preconditions enforced by refusal before consumption (D:564,
    D:579).
  * F2 is fixed NOT_SATISFIED.
  * The floor is satisfied iff base ∧ F1′.
  * Γ = 0 fails, because `pass` means Γ < 0 (C2F:89).
* **F2.** It is not re-evaluated, which floor r2 §10.2 and G12 permit. C2's publication of the F2 failure at 306 exists
  (C2_ADJUDICATION.md:478). Floor r2 binds it, and D pins floor r2.
* **G00-G14 as enforced.**
  * G00-G02: D:232-288.
  * G03: freeze ordering; see B1 for the verifier's defect.
  * G04-G06: D:74-145, D:361-398.
  * G07: deferred to the adjudication (N11).
  * G08: D:410-419.
  * G09: D:343-348, D:401-407.
  * G10: D:430-444, run at D:567 before D:579.
  * G11: D:581-584.
  * G12: D:465-477.
  * G13: G6.
  * G14: D:59, D:319-320, D:630-639.

## Q3 — The record substitution

* **Fields carried.** ADOPTED_TAIL_INPUTS.json carries exactly what C2's cell path reads from the record:
  * C_upper (C2F:173);
  * auxiliary_evidence.candidate_suprema and .midpoint_eps (C2F:176), the only keys `tct_rule.sigmas` and
    `tail_enclosure_crosscheck` read;
  * eps_cell_refined H:0-4 and m[1,2,3,5].R2_interval, which is everything `derived_identity_gate` indexes
    (tct_rule.py:293, :307);
  * per-m R_interval, D_interval, R2_interval and M_R2 (C2F:205 uses m["5"]).

  It is a verbatim extraction from manifest-checked records (tct_adopted_inputs.py:43-67).
* **Bound to the record hash.** D:326-332 requires TCT_INPUTS_306.k1_record_sha256 = adopted.record_sha256 = the manifest
  entry `k4_records/aux5_CUSUM_306_256.json`, with the manifest sha pinned. I confirmed that the entry matches.
* **Is the field-by-field control sufficient?**
  * It is sufficient for every input that is active under S_I1:
    * the consumer modules;
    * R, the loader and cover;
    * meas, and aux through the Taylor bounds, which are independent of A;
    * the m = 5 intervals;
    * the I1 supply.
  * It is **not** end-to-end for the Lemma-G branch. At 306 the provenance is all C2, so C_upper does not reach S_I1's
    Γ, but G does enter S_I2.
  * I checked, printing booleans only, that G computed from the adopted C_upper equals C2's recorded
    `supplies['306'].G` in all three fields (and the same at 305). The extraction is verbatim. So the substitution is
    correct, but the verifier does not prove it (N2).
* **Not re-running the 310-cell replay gate is acceptable.**
  * The gate (C2F:178-184) validates the off-host store against the sealed consumption, and C2 recorded it PASS.
  * `direct` for 306 reads only cell 306's record fields, which are hash-bound to the same manifest, plus the cover and
    TCT inputs.
  * The composed K5-B row passes whenever the direct Γ < 0 (k5b_check.py:175-189). C2's consumption at m = 5 recorded
    306 via "direct".

## Q4 — Bindings (N5/N6)

* **sha256 and git blob, both:** tail_forecast_r2 (edec817e), tct_rule (98f6eee4), the adapter (0516a15b),
  deflated_consume (a0a836fa), c2_d5_forecast.py (18403dbe), ADOPTED_TAIL_INPUTS (0ba3c6dc), TCT_INPUTS_306 (ad0f8039),
  C2_D5_FORECAST (a191557f), REGISTRY_C1 (f6d84bdb), REGISTRY_C2 (1a3adfd3), C11R comparison (5269c2aa), C11R statements
  (58b4066f), C11RD comparison (7151f57a = the blob at 8e2defab), C11RD runs (30e2dfd0 = the blob at 4547bcd4) and r5
  (f978eeb6). All are verified at HEAD and b9ffc87f. Every consumer file and non-supply input (and both I1 registries and the control artifact) is unchanged since 5a94568a.
* **Transitively sha-pinned:**
  * frozen tc_rule, through the pinned tct_rule.FROZEN, loaded with its own pin (D:301);
  * the loader and theorem, through the pinned adapter's PINS (consumption_adapter.py:28-31, 69-72);
  * cells.json and the record manifest, whose adapter constants must equal D's pins (D:307-309).
* **sha256 only, with no git-blob binding:** cells.json, the record manifest, TCT_INPUTS_305 and the four C11R/C11RD
  review files (N1). sha256 of the bytes is the stronger binding, so N5's "bind explicitly" is met in substance.
* **Driver used.** A cell-306-only driver reuses `direct`, `combine`, `_atom_independent`, `atom_constants_r2` and
  `atom_constants_generic`. It never calls C2F `main` or `requirement()`, and no margin is computed on any supply. N6 is met.

## Q5 — Exactly-once and sealing

* **Grant checks.** D:481-508 checks:
  * a clean tree (untracked files included, ignored files not);
  * HEAD is the last commit touching the grant, and the grant is the only file in the HEAD commit;
  * the schema and `exactly_once`;
  * the driver sha;
  * the three commits are ancestors;
  * no code/ or protocol/ diff since the grant-named freeze commit;
  * the review file exists, its last commit equals the grant's review commit, and its line 2 is the acceptance token.

  Gaps (N5): `freeze_commit` is not pinned to b9ffc87f, and the qualification commit's content and the review's position
  are not checked.
  **Missing, and part of B1:** the precondition of `seal()`, that HEAD is on a branch (D:514-516), is checked only after
  the evaluation.
* **Consumption order.** The consumed ref is created by CAS on non-existence (`update-ref … 0{40}`, D:581) strictly before
  the one evaluation (D:584). Every I2 check runs earlier, in `prepare_target` (D:579).
* **Failures after consumption** are sealed as TARGET_EVALUATION_FAILED (D:586-600). Exceptions: SystemExit and other
  BaseExceptions are not caught (N3). An UNSEALED result exits 4, which leads to seal-only (D:594-598, D:603-613).
* **Printing.** The driver prints only the status and commit ids (D:577, 597, 599, 609, 612, 636, 647, 660).
* **Double evaluation or early viewing: YES, through the frozen verifier.** See **B1**.
  * Exactly-once is enforced by a ref local to the repository's ref store. V builds a `git clone --shared` sandbox at the
    real HEAD, and refs/c12/* are not cloned.
  * At the qualification-review commit, V's control N05c becomes a complete, grant-valid `execute`. At the grant commit,
    control N08 does.
  * In either case the sandbox evaluates Γ(5,306;S_I2) and writes it to a sandbox file before (or besides) the real
    sealed evaluation.

## Q6 — Negative controls

* **Present and non-vacuous.** Each fires with its own code, and the sandbox baselines N00/N00b pass first:
  * altered inputs: N01, N03;
  * wrong blob: N03b;
  * wrong cells: N02-N02d, F06/F06b;
  * wrong statements, classes, status, domain and binding: F03-F03j, F04/F04b with the positive F04c;
  * missing reviews: N05, N05b, N05c;
  * mixed supplies: F01-F01c;
  * premature artifacts: N07-N07c, N12;
  * control mismatch: F05, with the positive rehearsal;
  * missing or invalid grant: N08, N09, N10;
  * dirty tree: N11;
  * r6: G01-G06 with the positive G02;
  * leak scan with a decoy: L.
* **Refusal progression.** The execute refusals progress through DIRTY_TREE, GRANT_MISSING, GRANT_INVALID and
  REVIEW_MISSING. That shows each earlier check passed, so none is vacuous.
* **N04 tests the pin, not the statement check.** Its PIN_MISMATCH fires before any statement logic. The statement logic
  is covered in-process (F03b, F03c, F03h).
* **Gaps** (N6), listed below.
* **Wrong reason.** No control refuses for the wrong reason at b9ffc87f. N05c and N08 are, however, the controls that
  stop being refusals in later states (B1).

## Q7 — Fail-closed behaviour

* **Refusals before consumption** never compute Γ(S_I2). They compute at most the I1 control, which is historical.
  * After `prepare_target`, the S_I2 atom constants exist in memory before the CAS (N9). They are never written or
    printed.
* **The verifier at b9ffc87f / aac6dae9** computes no Γ or atom constant under S_I2:
  * `supply` is called only with synthetic sets;
  * every `i2_set` call uses a mutated input that refuses;
  * `prepare_target` and `evaluate_target` are never called.

  The sandbox execute controls are safe at these commits. **That stops being true** at the qualification-review commit
  and the grant commit (B1).

## Q8 — The r6 generator

* **Mechanical.** It parses the adopted set from the adjudication (G6:98-103).
* **Refusals.** It refuses unless all of the following hold:
  * the result is at HEAD with status TARGET_EVALUATED, one evaluation, the self-hash, the control reproduced, and both
    passes (G6:80-93);
  * the consumed ref exists;
  * EXECUTION_ACCEPTED, CELL306_ADOPTED with the set exactly [306], and ADJUDICATION_ACCEPTED (G6:95-104);
  * r5's pin holds and no r6 exists.
* **Moves only (5, 306)** (G6:131-149). G02 confirms that other m values are unchanged and that 307-309 stay open.
* **r5.** It reads r5, and writes only to `--out`.
* **Weaknesses** (N7):
  * it reads the working-tree result and reviews, not the committed bytes;
  * it has no guard against `--out` being r5's path.

## Q9 — Scope

* **Cells 307-309** are refused at three layers (D:319-320, D:630-639; REHEARSAL_CELLS = (305, 306)). Nothing evaluates
  them.
* **Cell 305** is evaluated only as a historical I1 rehearsal. It decides nothing.
* **r5** is byte-identical (blob f978eeb6) and never written by D.
* **Historical verdicts.** `git diff --name-only 3fadb422 aac6dae9` lists only the nine C12 files, so historical verdicts
  are untouched.

## Q10 — Resource caps

* **Wall cap.** A 900 s SIGALRM per invocation (D:68, D:624-628).
* **Measured.** Each driver run takes about 1 s wall (0.4 s user). The verifier takes about 20 s.
* **Hosts.** No host other than this machine, and zero new real addresses.

The caps are reasonable. See N3 for the cap's behaviour if it fired after consumption.

## BLOCKERS

**B1 — The frozen verifier becomes a second, unguarded target evaluator at the campaign's own next two commits. This
breaks exactly-once and the rule that "the verifier evaluates no target".**

* **Mechanism.**
  * V:470 builds the sandbox at the real HEAD (`Sandbox(tmp, report["T_temporal"]["HEAD"])`).
  * V:189-192 makes it a full, sparse, **detached** `git clone --shared`. It carries every pinned input, including the
    C11R/C11RD files (V:44-60), and no refs/c12/*.
  * The N controls then run the real driver's `execute` in that sandbox (V:224-230).
  * The only thing stopping a sandbox `execute` from evaluating the target is the absence of a valid grant and
    qualification review. N00/N00b prove that bindings, governance, consumer and control all pass there.
  * The committed N05c result "REFUSED REVIEW_MISSING" (C12_QUALIFICATION.json:163-168) proves that a verifier-authored
    grant passes every grant check before the review check (D:483-501).
* **State R: HEAD = the commit preserving this review (P §2 step 3).**
  * Line 2 of the review is the acceptance token.
  * N05c's `write_grant` (V:235-241) names R as freeze, qualification and review commit. D:504 therefore matches R, and
    D:506 passes.
  * `execute` then runs the control, `prepare_target`, the CAS on the *sandbox's* ref, and `evaluate_target`.
  * `write_result` writes Γ(5,306;S_I2) into the sandbox. `seal` then fails with SEAL_NO_BRANCH because the sandbox HEAD
    is detached, and the driver exits 4 UNSEALED.
* **State Gr: HEAD = the grant commit (P §2 step 4).**
  * N08 ("execute without a grant", V:307) runs `execute` with no setup. The sandbox's checked-out tree contains the
    **real** grant and review, and every check in D:481-508 passes.
  * The same full evaluation follows.
  * If the real execute had already consumed the ref but ended UNSEALED, this is a genuine **second evaluation**. The
    sandbox cannot see the real refs/c12 ref or the uncommitted result.
* **Effect.**
  * With `--keep-sandbox` (V:476-477) the target's value stays readable in /tmp, unsealed, before or independently of
    the real seal.
  * Without it, the value is computed and written, then deleted.
  * Either way V's docstring guarantee (V:1-2, "no Gamma under any supply that contains an I2 constant is computed …
    in the sandbox") and P §2 ("The verifier evaluates no target") are false in states the protocol itself passes
    through.
  * Reviewers in this programme are routinely told to re-run `c12_verify.py --dry-run` at later HEADs, as this brief
    did. Such a re-run in state R or Gr would trigger the evaluation.
* **Reproduction.** By code reading only. Executing it would compute the forbidden quantity.
  1. Create a commit R adding `review/C12_QUALIFICATION_REVIEW.md` with the acceptance token on line 2.
  2. Run `c12_verify.py --dry-run --out X`.
  3. Control N05c reports exit 4 ("C12 UNSEALED …") instead of 2, and the sandbox held evidence/execution/C12_CELL306_RESULT.json.
  4. Likewise at a grant commit Gr, with N08.
* **Required fix (needs a re-freeze and re-qualification), for example both of:**
  * (a) V builds its sandbox at the freeze commit (`T_temporal.freeze_commit`), never at HEAD. V also refuses to run at all
    when HEAD's tree contains `authorization/` or the qualification review, or when refs/c12/* exists.
  * (b) D checks every seal precondition before consumption, in `check_grant`: HEAD is a symbolic ref to the campaign
    branch, and the repository's common dir is the canonical one. A detached or foreign clone is then refused with
    nothing evaluated.

  A CLI control should demonstrate that a sandbox at a state carrying a valid grant and review refuses *before*
  `prepare_target`.

## NON-BLOCKING NOTES

* **N1 — sha-only bindings.** cells.json, the record manifest, TCT_INPUTS_305 and the four C11R/C11RD review files are
  bound by sha256 only, with no git-blob entry in D BLOBS or C12_FREEZE `input_blobs`. The sha256 binding is stronger. The
  execute clean-tree check covers the difference between committed and working-tree bytes.
* **N2 — the control does not exercise Lemma G.** At 306, S_I1's provenance is all C2, so the substituted C_upper is not
  checked by the control, yet G enters S_I2. My boolean check found the G supply equal to C2's recorded
  `supplies['306'].G`.
  * The execution reviewer should repeat this.
  * A successor control should also compare C2's per-supply records.
  * P §1's "end-to-end proof" is overstated for this one input.
* **N3 — unrecorded failures after consumption.**
  * `except Exception` (D:586) does not catch SystemExit, which C2's frozen `direct` raises on a TC-T crosscheck mismatch
    (C2F:82). That path leaves the consumed ref with no result written or sealed, and exits 1, which is undocumented.
  * A WALL_CAP between the evaluation and `write_result` exits 2, labelled "nothing evaluated".
  * Both are fail-closed. Execute cannot rerun and no Γ is revealed. But "failures after consumption are sealed" is not
    universal.
* **N4 — seal-only is loose.**
  * seal-only (D:603-613) seals whatever result file is on disk without checking the self-hash or status. Its commit
    message always says TARGET_EVALUATED.
  * A CONTROL_FAILED result whose seal failed (D:576 is unwrapped) cannot be sealed by seal-only, because there is no
    consumed ref. The campaign stops anyway.
* **N5 — what the grant author and grant reviewer must ensure.** The grant must name:
  * `freeze_commit` = b9ffc87f…;
  * `qualification_commit` = aac6dae9…;
  * the review-preservation commit;
  * `driver_sha256` = c045e990…ac03.

  D does not pin these itself. After a re-freeze, the values change accordingly.
* **N6 — control coverage gaps.**
  * Invalid-grant variants with no CLI control: schema or `exactly_once` wrong, a grant commit carrying other files, code
    changed after the freeze, a review-commit mismatch, and a qualification review whose line 2 is wrong.
  * r6 refusals with no control: self-hash mismatch, missing consumed ref, result not at HEAD, missing execution review.
* **N7 — r6 generator hardening.** It should:
  * compare the working-tree result and reviews with `git show HEAD:<path>`;
  * require a clean tree;
  * refuse an `--out` equal to r5 or not named K5_COVERAGE_MAP_R6*.

  Also, r6's 306 entry keeps r5's flags, primary and zone fields.
* **N8 — I2 domain and independence checks rest on the pinned bytes.**
  * I2 domain exactness is checked from C11R's statements table (D:392-398). D1/D2 rely on the C11RD comparison's
    `domain: EQUAL` label. I confirmed that the C11RD runs' statements carry drift_domain [680769/400000, 17885921/10000000].
  * `independence_violations` is not asserted by D. It is [] in both pinned comparisons.
* **N9 — S_I2 atoms before the CAS.** S_I2 atom constants are computed in `prepare_target` before the CAS. A CAS failure
  (D:581-582) refuses after them. They are never output, and no Γ is computed.
* **N10 — the qualification commit was amended.** 96bd5406 → aac6dae9 (reflog). The trees are identical (1553312…). Only
  the message's check counts changed.
* **N11 — G07's residuals are deferred.** They are deferred to the adoption adjudication (P §4). The adjudicator must restate:
  * N10 open;
  * STRONGER-direction blindness;
  * implementation-only independence;
  * C_T exact versus rounded;
  * original-value exposure.
* **N12 — exactly-once is per ref store.** The ref lives in the shared common dir, which is good across worktrees. Any
  plain clone made before the seal could still run `execute`. Procedure: run D only in this worktree family.
* **N13 — the freeze statement is an attestation.** The no-inspection statement (P §7) cannot be verified. Nothing
  contradicts it:
  * the reflog is clean;
  * no result file exists in any worktree or temp directory;
  * the only pre-freeze verifier dry-run directories hold I1-only file names.

## Confirmation

* **Nothing modified.** `git status --porcelain --ignored --untracked-files=all` printed 0 lines before and after every
  step. I ran no git write command and no `execute` or `seal-only` mode. I created no refs/c12/* (none exist). I wrote only
  in …/scratchpad/c12_qual_review/.
  * The verifier's own dry-run left its usual temp directory in $TMPDIR and removed its sandbox.
* **Nothing computed under S_I2.** I did not compute, estimate or inspect any Γ, atom constant or margin under any supply
  containing a C11R or C11RD constant. I did not call `prepare_target` or `evaluate_target`, or reconstruct them.
* **No D1/D2 values.** I printed, wrote and quoted no D1/D2 value, original or independent. The leak scan reported counts
  only.
* **Other exclusions.** I did not open C11R's quarantine. I used no AWS/Vultr tool, no network and no session transcript.
