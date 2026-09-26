# C12-R1 — qualification review (cell 306 under floor r2)
QUALIFICATION_REJECTED

**Reviewer:** fresh, independent, read-only. I wrote no part of C12 or C12-R1.
**Worktree:** /Users/suzhe/ReBaseGuard-k5c11rd, branch p5y-k5-tail-c11rd-d1d2-extension, HEAD 2e7bc7d6.

**Verdict in one line.** One blocker (B1 below). The three B1-repair barriers of C12's review are sound: I found no path to a second evaluation, and no path to an evaluation outside the marker. However, one seal precondition that is checkable before the marker is not checked: the result's temporary path, which the repository ignores. Through it, the single evaluation can become unsealable, or its full result can be diverted outside the sealed record while the driver prints `SEALED`. Both effects are reproduced below on decoy targets.

In this review, "D" means code/c12r1_cell306.py, "V" code/c12r1_verify.py, "G6" code/c12r1_r6_from_adjudication.py, "GR" code/c12r1_grant.py, "P" protocol/C12R1_PROTOCOL.md and "C2F" p5y_k5_tail_c2_closure/code/c2_d5_forecast.py.

## Reviewed commits

* **Freeze.** 5cfe336ac471f24ddd1d02f30fbe173f617fe31a, whose parent is eba56027.
  * It adds exactly six files: code/c12r1_cell306.py, c12r1_verify.py, c12r1_r6_from_adjudication.py and c12r1_grant.py, plus protocol/C12R1_PROTOCOL.md and C12R1_FREEZE.json.
  * C12R1_FREEZE.json's self-hash verifies, and all five of its `frozen_files_sha256` entries verify against the files.
  * Its `input_pins_sha256`, `input_blobs` and `lineage` are identical to D's `PINS`, `BLOBS` and `LINEAGE`.
* **Qualification.** 2e7bc7d6aa890a7b849639f4fe4b699614f4ad08, whose parent is 5cfe336a.
  * It adds exactly four files under evidence/qualification/: C12R1_QUALIFICATION.json, PREFLIGHT.json, REHEARSE_305.json and REHEARSE_306.json.
  * The report records `review_mode` false, `state` freeze, HEAD = freeze_commit = 5cfe336a, `dry_run` false, pass true, 115/115 and `failed` [].
* **History.** The branch reflog is linear (…eba56027 → 5cfe336a → 2e7bc7d6), with no amend.
  * `git log --all` finds nothing under the C12-R1 review/, authorization/, adjudication/, evidence/execution/ or evidence/coverage/ paths, no C12 result and no `*K5_COVERAGE_MAP_R6*`.
  * `refs/c12r1/*` and `refs/c12/*` are empty.

## Commands run (read-only; every output went to …/scratchpad/c12r1_qual_review/)

1. Git reads:
   * `status --porcelain --ignored --untracked-files=all` printed 0 lines before and after every step;
   * `show --stat`, `log --all -- <paths>`, `reflog`, `rev-parse <commit>:<path>` for all 27 pins at the working tree, HEAD and 5cfe336a, and at 8e2defab/4547bcd4/2c24a989/5a94568a for the historical bindings;
   * `for-each-ref refs/c12r1 refs/c12`, `worktree list`, `check-ignore -v --no-index`, `config --get` (gpgsign, hooksPath, sparse).
2. `python3.14 -I -S -B c12r1_cell306.py preflight --out …/PREFLIGHT.json` printed PREFLIGHT PASS (exit 0).
3. `… rehearse --cell 306 --out …/REHEARSE_306.json` and `… rehearse --cell 305 …` both exited 0 with "reproduces C2 exactly = True".
   * Every field matched, including `per_supply_records_G_C1_C2`.
   * Wall time was about 0.03 s per rehearsal.
   * Runs 2-3 are identical to the committed PREFLIGHT/REHEARSE files apart from utc, wall and rss.
4. `python3.14 -I -S -B c12r1_verify.py --review --out …/VERIFY_REVIEW.json` printed QUALIFICATION PASS (115/115, exit 0) in 55 s.
   * Every section (S, R, A, B, X, F, G, L-checks) and the sandbox provenance match the committed report.
   * The driver, verifier, r6 and grant hashes also match.
   * The only difference is that the leak scan now also lists the committed qualification JSON.
   * The real execute inside it refused with GRANT_MISSING.
   * It left its I1-only qdir at $TMPDIR/c12r1rev9gbgqt_t.
5. The refusal probe `python3.14 -I -S -B c12r1_cell306.py execute` in the real worktree printed `C12R1 REFUSED GRANT_MISSING` (exit 2).
   * Afterwards `git for-each-ref refs/c12r1` was empty, `git status --porcelain --ignored --untracked-files=all` was empty, and no authorization/ or evidence/execution/ directory existed.
6. Probe scripts, kept in …/probe/:
   * `modprobe.py` (I1 only; the in-process equivalent of `rehearse --cell 306`) checked `sys.path` and whether any module is imported during evaluation.
   * `barrier1_probe.py` and `tmp_probe.py` are decoy-only probes in my own sandboxes.
     * Each sandbox is built with V's own `make_decoy_sandbox` from 5cfe336a. Its three I2 files are replaced by synthetic decoys, and the script asserts `DECOY: true` before anything else.
     * The sandboxes were deleted afterwards.
     * The output is saved in probe/TMP_PATH_PROBE.json.
7. Value-free checks that printed labels and booleans only:
   * I2 statuses, directions, classes, statements, domains and independence lists;
   * whether the D1/D2 comparison values equal the sealed run values;
   * whether r5, the manifest and ADOPTED_TAIL_INPUTS agree on the 305/306 record hashes;
   * a hashed leak scan of my outputs.

## Requirement-by-requirement findings

**1. Sandboxes come from the freeze commit, never HEAD: HOLDS.**
* V:793-794 build sandbox A and sandbox B at `pre["freeze_commit"]` = `D.freeze_commit()` (D:251-253), and V:220-223 check out exactly that commit.
  * Sandbox B is the freeze commit plus one synthetic decoy commit (V:254-275).
* My rerun at HEAD 2e7bc7d6 records A_commit = B_parent = 5cfe336a and `both_from_the_freeze_commit` true.
* The copies in B05 (V:401-404) and X03 (V:489-495) are copies of sandbox B.
* The freeze is derived as "the last commit touching code/ or protocol/". A later commit there would redefine it. That is inert, though: barrier 1 and D's grant chain (HEAD^^^ = freeze, D:574) would both refuse.

**2. The verifier fails closed on a grant, an accepted review, a marker, a sealed result, or evaluation evidence: HOLDS.**
* The checks are in V:105-129:
  * HEAD must be the freeze commit, or (with --review) its qualification-evidence child;
  * none of review/, authorization/, adjudication/, evidence/execution/ or evidence/coverage/ may exist on disk or in `git log --all`;
  * no ref may exist under refs/c12r1/ or refs/c12/;
  * `D.check_not_evaluated()` must pass. It covers C12-R1's and C12's result paths in the tree, on disk and in history.
* The committed tests are B02v, B03v, B04v, B06v, B07v, B08v and B09v.
* My additional decoy-sandbox probes all ended in `VERIFY REFUSED`. They ran at the (decoy) freeze state, where the HEAD test passes, so the specific test was exercised in each case:
  * C12-R1's own result on disk;
  * an uncommitted grant;
  * an adjudication file;
  * an r6 under evidence/coverage;
  * a grant present only in a side branch's history;
  * an empty evidence/execution directory.

**3. Verification after later governance commits is structurally incapable of evaluating Γ(5,306;S_I2): HOLDS.**
* **The only non-decoy path.** V's only path to a non-decoy `execute` is `real_runs` (V:190), in the real worktree. That execute can pass `check_grant` only when both of these hold:
  * a committed grant exists on disk;
  * HEAD^^^ = freeze (D:559-575).
* **Barrier 1 is exclusive with both conditions.** Barrier 1 requires HEAD ∈ {freeze, child of freeze} (V:111-115), and it refuses when authorization/ exists (V:116-119). Both tests use the same `freeze_commit()`, so each is structurally exclusive with the grant check.
* **Sandbox A** has real inputs, but no grant or review is ever planted in it. Its CLI `execute` stops at REPO_NOT_QUALIFIED (A20).
* **Sandbox B** holds decoys only. The in-process flows override PINS with the decoy hashes (V:445-446), so a real I2 file there would stop at PIN_MISMATCH.
* **The F controls** never call `supply`, `prepare_target` or `evaluate_target` on real I2 constants (V:622-680). `supply` is called only with synthetic sets, and every real `i2_set` call is on a mutated input that refuses.
* **C12's rejected verifier is inert in every C12-R1 state.** Its driver requires C12's own review to carry the acceptance token (c12_cell306.py:502-507), and that preserved review is the rejection.

**4. Every seal/execution precondition checkable without the target runs before the marker and before evaluation: DOES NOT HOLD. See B1.**
* **The order holds for everything D does check** (D:643-672; V's static order check):
  * identity, then prior evaluation;
  * a clean tree and no locks;
  * the grant chain, then bindings, then governance state;
  * committer/author identity, a private index, a writable-directory probe and the branch ref;
  * consumer, control, the CONTROL_FAILED exit and every I2 check;
  * only then the CAS marker (D:669), and then the evaluation (D:672).
* **Two gaps.**
  * The temporary path that `write_result` actually writes, `evidence/execution/C12R1_CELL306_RESULT.tmp` (D:627), is gitignored (`.gitignore:60 *.tmp`), so it is invisible to `check_clean` (D:283). The write probe uses a different name (D:303), and `check_not_evaluated` checks only the .json path (D:278).
  * `write_result` (D:682) and non-`Refusal` sealer failures (D:683-687) sit outside the post-marker handler (D:671-675).

**5. The driver verifies the qualified worktree, git dir, common dir and branch before consumption: HOLDS.**
* `check_identity` (D:257-268) is the first statement of `run_execute` (D:644) and of `run_seal_only` (D:694), and GR calls it first (GR:27).
* git runs with a fully replaced environment (D:90-91, 212-217), so an inherited GIT_DIR or GIT_WORK_TREE cannot redirect it.
* A copied worktree, even one keeping the `.git` file that points at the real git dir, fails the path test.
* The tests are X01, X02 and X02b (wrong worktree, detached HEAD, another branch), X03 and B05 (copies), and A20 (a real-input sandbox).

**6. The applicable notes N2-N7 of the C12 review are incorporated: HOLDS, with residuals.**
* **N2.** The control now also compares C2's per-supply records for G, C1 and C2 (D:517-518), and F05b perturbs the G record and is detected.
  * The comparison is at float precision, because C2 recorded floats (C2F:219).
* **N3.**
  * `BaseException` is caught around the evaluation (D:674), including SystemExit (X10) and the wall cap.
  * The alarm is cancelled before the write (D:676), which closes C12's "wall cap between evaluation and write" case.
  * The residual is B1.
* **N4.** seal-only verifies the self-hash and status/marker consistency and names the real status (D:692-716). A CONTROL_FAILED seal failure is now handled (D:661-665).
* **N5.** The chain freeze → qualification → review → grant is derived from git and compared with the grant (D:570-583). The review and qualification commits must each contain only their own files (D:576-580).
* **N6.** It is largely addressed:
  * X12 covers schema, exactly_once, driver sha and a wrongly named freeze;
  * X12b covers a rejected review, X12c an extra file in the grant commit, and X12d HEAD ≠ grant;
  * G03-G12 cover the r6 refusals.
  * The remaining gaps are listed under NOTES.
* **N7.** G6 compares committed and working-tree bytes (G6:50-59), requires a clean tree (G6:87-88), and refuses an `--out` equal to r5 or not named `K5_COVERAGE_MAP_R6*` (G6:85-86).
  * The residual about r5's flags, primary and zone fields is moot: r5's own PASS entry for 305 carries the same fields.

**7. tail_forecast_r2.py and every other non-supply input are pinned: HOLDS.**
* tail_forecast_r2.py is pinned by sha256 and blob edec817e (D:109-110, D:161). It is executed from pinned bytes (D:365), and it must bind the pinned tct_rule (D:366-367).
* The rest of the consumer chain is pinned transitively:
  * tc_rule through `tct_rule.FROZEN`;
  * the loader and theorem through the adapter's PINS;
  * cells.json and the record manifest through the adapter, cross-checked against D (D:378-380).
* All 27 pins verify by sha256 and blob at the working tree, HEAD and 5cfe336a, with 0 mismatches. The C11RD blobs equal those at 8e2defab and 4547bcd4, and C11R's blob equals the one at 2c24a989.
* Every consumer and non-supply input blob is unchanged since 5a94568a. The intervening commits touched only other C2 files.
* After `load_consumer`, `sys.path[0]` is the m5 tail code directory. During the evaluation path nothing is imported: the set of newly imported modules is empty (I checked on the I1 control). So an ignored `.pyc` there cannot shadow anything.
* Floor soundness evidence (G07) is not pinned; see note N10.

**8. Cell 306 only: HOLDS.**
* `cell_inputs` refuses any cell outside {305, 306} (D:389-390).
* `execute` takes no `--cell` (D:733-734), and rehearse accepts only 305/306 (D:742-743).
* The target is always `TARGET_CELL` (D:526).
* The tests are A02 (307/308/309), A02b, F06 and F06b.
* G6 moves only (5, 306) (G02) and refuses any other adopted set (G04).

**9. The adversarial tests exist and pass on decoys: HOLDS.** The committed report and my rerun both give 115/115:
* A00 and A00b: a freeze-commit sandbox passes;
* B01 and X04(Q), B02 and X04(R), B03, B03s, B04 and X08: qualification, review, grant and consumed states;
* B05 and X03: copies;
* X01, X02 and X02b: wrong branch or worktree;
* A07-A07e, X06, X07 and X07b: planted results and markers;
* X09 and X10: seal failure and a post-marker SystemExit;
* X05: exactly one decoy run, which is sealed.

  B06v refuses for a different reason than its label says (note N2).

## C12 review items re-checked

* **S_I1 = C2's adopted supply.**
  * `supply` builds {G} and then {C1, C2}, in that order (D:487-492, D:421-428). This is C2F:197-204.
  * It then calls C2F's own `combine` and `direct` from pinned bytes. The argument order is (Abar, tau, C_T, D_lo, D1, D2).
  * The atom crosscheck against `_atom_independent` is kept (D:477).
  * The control reproduces Γ, A, provenance (C2 on all three fields), H, M, pass and the G/C1/C2 per-supply records.
* **S_I2 = Lemma G + the I2 set, never mixed.**
  * S_I2 = min{G, I2} (D:524-532). The I2 set is taken from C11R `result.per_target[C_T, tau, Abar, D_lo]` and C11RD `per_target[D1, D2]`, and must equal `C11RD_RUNS.targets` (D:456).
  * `supply` refuses a foreign tag or a duplicate name (D:485-490; F01-F01c).
  * Value-free check:
    * all four C11R targets are CERTIFIED with the expected directions (AGREES/STRONGER, statements EQUIVALENT/STRONGER, domain EQUAL);
    * D1 and D2 are UPPER_BOUND, STRONGER, EQUIVALENT, EQUAL;
    * the comparison values equal the sealed run values;
    * both `independence_violations` are [], and N9_VERDICT is N9_CLOSED;
    * the runs are for cell 306, and the C11R drift domain is cell 306 (F04c positive).
* **Decision table.** D:540-553 matches gate G12 and P §4:
  * base = Γ(S_I1) < 0;
  * F1′ = base ∧ Γ(S_I2) < 0, with (a)-(c) enforced by refusal before consumption;
  * F2 is fixed NOT_SATISFIED and is not re-evaluated;
  * Γ = 0 fails (C2F:89);
  * a closure disagreement is recorded under `scientific_closure`.
* **The ADOPTED_TAIL_INPUTS substitution.**
  * D:393-402 binds TCT_INPUTS_306's record hash = the adopted record_sha256 = the manifest entry, with the manifest sha pinned.
  * I confirmed that r5's `k1_record_sha256` for 305 and 306 equals both of them.
  * The exact control now also covers C2's per-supply records, so the Lemma-G input is checked (float precision, note N11).
* **Bindings.** sha256 and git blob for all 27 inputs, including the seven that C12's N1 listed as sha-only.
* **Exactly-once and sealing.**
  * The marker is created by CAS on non-existence (D:669), after every check.
  * seal-only never computes (static check; D:692-716). X09 shows UNSEALED → no second evaluation → seal-only seals.
  * The grant chain is derived. GR evaluates nothing and requires review ← qualification ← freeze.
  * No commit.gpgSign, no hooksPath, no active hooks, and no sparse checkout are configured.
* **The r6 generator.** It parses the adopted set from the committed adjudication and requires:
  * EXECUTION_ACCEPTED and ADJUDICATION_ACCEPTED;
  * the marker, the self-hash and status TARGET_EVALUATED with one evaluation;
  * the control reproduced, and both passes.

  It moves only (5, 306) and never writes r5 (G02-G12).
* **Scope, leaks and caps.**
  * The leak scan found 0 hits for the original and the independent D1/D2 renderings in the namespace, and the planted decoy was detected.
  * Wall cap: 900 s per invocation, against about 0.03 s per evaluation.
  * This machine only, with zero new real addresses.

## BLOCKERS

**B1 — The result's temporary path is an unchecked, gitignored seal precondition. A planted object there makes the one evaluation unsealable, or diverts the full result outside the sealed record while the driver prints SEALED.**

* **Mechanism.**
  * `write_result` writes `path.with_suffix(".tmp")` = `…/evidence/execution/C12R1_CELL306_RESULT.tmp` and then `os.replace`s it onto the .json (D:622-629).
  * That name matches `.gitignore:60 *.tmp`, and `git status --porcelain --untracked-files=all` (D:283) omits ignored paths.
  * The pre-marker checks never look at it:
    * `check_not_evaluated` tests only the .json path (D:278);
    * `check_seal_preconditions` probes `.c12r1_write_probe` (D:302-309);
    * `check_clean` cannot see ignored paths.
  * `write_result` (D:682) runs outside the post-marker handler (D:671-675), and so does a non-`Refusal` sealer failure.
* **Reproduction.** This used decoy inputs only, in my own sandbox built by V's `make_decoy_sandbox` from 5cfe336a, driven in-process exactly like V's X flows (script probe/tmp_probe.py; output probe/TMP_PATH_PROBE.json):
  1. Build the synthetic governance chain to the grant state with V's `build_state(sb, "G", drv_sha)`.
  2. Point D's identity at the sandbox, and override PINS/BLOBS with the decoy hashes.
  3. **(a)** Create an empty directory at `evidence/execution/C12R1_CELL306_RESULT.tmp`. `git status --porcelain --untracked-files=all` is still empty. Call `run_execute(drv_sha)`. The outcome:
     * every guard passes and the marker is created;
     * the decoy target is evaluated once;
     * `write_result` raises an uncaught `IsADirectoryError`, so no result is written and nothing is sealed;
     * `seal-only` then refuses SEAL_ONLY ("no written result").
     The one evaluation is consumed with no record and no possible seal.
  4. **(b)** Instead, create a symlink at the same path pointing outside the repository, and call `run_execute(drv_sha)`. The outcome:
     * it returns 0 and prints `C12R1 SEALED … (status TARGET_EVALUATED …)`;
     * the full result JSON, including the Γ fields, is written to the outside file;
     * `C12R1_CELL306_RESULT.json` is now a symlink, and the "seal" commit records it as mode 120000, a link path, not the result.
  * I confirmed with `git check-ignore -v --no-index` that the same path is ignored in the real repository. The real driver runs the same `check_clean` and `write_result` code, so the gap is present in the frozen driver as it stands.
* **Why it blocks.**
  * It violates requirement 4: whether the temporary path is free and regular is a precondition that can be checked without the target, and it is not checked before the marker.
  * It realises two of the failure classes this review was asked to find: "evaluated before sealing is guaranteed" (a) and "seen before it is sealed" (b).
  * It falsifies the frozen claims "after the marker exists, EVERY failure … is recorded and sealed" (D:9-12) and "every exception … is recorded and sealed" (P:50).
  * What it does **not** do:
    * it allows no second evaluation and no evaluation outside the marker;
    * it needs a pre-planted ignored object in the campaign namespace, so normal operation does not trigger it. The real worktree currently has zero ignored paths.
* **Required fix (a re-freeze and re-qualification).**
  * Before the marker, refuse if `os.path.lexists()` holds for either the .tmp or the .json path. Alternatively, make `check_clean` include `--ignored`.
  * Write the result with `O_CREAT|O_EXCL|O_NOFOLLOW`.
  * Bring `write_result` and every sealer failure under the post-marker record/seal handling.
  * Add decoy tests for a directory at the .tmp path and for a symlink there.

## NON-BLOCKING NOTES

* **N1 — Protocol overstatements.**
  * P §1 barrier 1 (and the freeze message) say that the verifier refuses on a qualification review, grant or adjudication "for this campaign or for C12". For C12, only `refs/c12/` and C12's result path are checked, and C12's own review necessarily exists.
  * P §1 barrier 2 says that "no real I2 or original D1/D2 value exists" in sandbox B's working tree. Its sparse checkout (V:53-69) still contains:
    * the C11R and C11RD reviews and the N9 adjudication;
    * C11RD_EXECUTION.log and C11RD_LAUNCH_JOURNAL.jsonl;
    * the floor rule, which states C11R's exact C_T supremum.

    Safety is unaffected, because PINS route the driver only to the three decoy files. The claim should still be narrowed to "the three I2 input files".
* **N2 — B06v's label does not match its refusal.**
  * B06v is labelled "planted result", but it refuses on the HEAD test because it runs at the grant state. No committed test plants C12-R1's own result at the freeze state.
  * My decoy probe shows that the verifier does refuse there (evidence/execution exists).
* **N3 — Review mode does not bind its own code.**
  * `--review` requires neither a clean tree nor that the working-tree driver and verifier bytes equal the freeze.
  * The in-process X flows load the working-tree driver (V:84-89, V:439), while the CLI tests run the sandbox's frozen copy.
  * My run: the tree was clean, and all hashes equal C12R1_FREEZE.json.
* **N4 — Other post-marker residuals, all fail-closed and allowing no second evaluation.**
  * A SIGALRM or SIGINT in the microsecond window between `update-ref` and `try` (D:669-671).
  * A non-`Refusal` OSError from the sealer (D:683-687). The result is already written, so seal-only recovers.
  * Object-store writability and a future `commit.gpgSign` are not probed. The private-index `write-tree` writes no new object.
* **N5 — Exactly-once is local to the common ref store.** Deleting the marker (forbidden) together with an unsealed result file would re-enable `execute`. This is inherent, and the protocol forbids it.
* **N6 — N6 coverage still missing:**
  * a grant naming the wrong qualification or review commit;
  * code changed after the freeze;
  * r6 with the result not at HEAD.

  The code paths for the first two exist (D:573-575).
* **N7 — r6 generator.**
  * `--out` is not confined to evidence/coverage/: only the name and non-existence are checked, so r6 can be emitted outside the repository.
  * It does not check the result's `cell` = 306, or that the marker points at the grant commit. The execution review should check both.
* **N8 — The interpreter flags are not enforced.** D does not enforce `-I -S -B` (`sys.flags`). The grant names the exact command.
* **N9 — Grant generator.**
  * GR does not require `QUAL_REL` in the qualification commit (D does), and it commits with the inherited environment.
  * Both fail closed downstream in `check_grant`.
* **N10 — G07 soundness evidence is not pinned by the driver.** Examples are C11R_RUNS.json (blob a5351603), C2's CELL_306_ADOPTION.md and the C11RD theory.
  * The adoption adjudication should verify them and restate the floor's residuals, as C12's note N11 required.
  * P §3 step 8 does not list them.
* **N11 — The Lemma-G check is float-level.** The control compares G, C1 and C2 at float precision (C2's record is float). Exactness of the C_upper substitution rests on the verbatim extraction bound to the record hash. The execution reviewer should recheck it exactly.
* **N12 — S_I2 atoms exist in memory before the marker.** S_I2 atom constants are computed in `prepare_target` before the CAS (C12's N9). They are never output.
* **N13 — `--review` leaves a temp directory.** It leaves its qdir (I1-only files) in $TMPDIR (…/T/c12r1rev9gbgqt_t).

## Confirmation

* **Nothing modified.** `git status --porcelain --ignored --untracked-files=all` printed 0 lines before and after every step, and HEAD is still 2e7bc7d6.
  * I ran no git write command in /Users/suzhe/ReBaseGuard-k5c11rd and created no ref; `refs/c12r1/*` and `refs/c12/*` are empty.
  * I ran `execute` once, only as the permitted refusal probe (GRANT_MISSING). I never ran `seal-only`.
  * I wrote only in …/scratchpad/c12r1_qual_review/, and in my own decoy sandboxes there, which I then deleted. The verifier itself wrote to $TMPDIR.
* **Nothing computed under a real S_I2.** I did not compute, estimate or inspect any Γ, atom constant or margin under a supply containing a real C11R or C11RD constant.
  * I did not call `prepare_target` or `evaluate_target` on real inputs, and did not reconstruct them.
  * Every Γ I caused to be evaluated was either the historical I1 control (305/306) or a synthetic decoy.
* **No D1/D2 values.** I printed, wrote and quoted no D1/D2 value, original or independent. The checks printed labels and booleans only, and the leak scan printed counts.
* **Other exclusions.** I did not open C11R's quarantine. I used no AWS/Vultr tool, no network and no session transcript.
