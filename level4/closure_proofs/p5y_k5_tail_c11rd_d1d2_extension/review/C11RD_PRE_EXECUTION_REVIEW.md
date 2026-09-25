# C11RD pre-execution review
NOT_READY

Reviewer: fresh, independent, read-only. Worktree `/Users/suzhe/ReBaseGuard-k5c11rd`, branch
`p5y-k5-tail-c11rd-d1d2-extension`, freeze commit `71495747504670dbe90ec0ee2f7dd4702fd47001`, entry
HEAD `7375b9cdb1d770ba836335164f205e26b445035e`. Date 2026-09-25.

## Scope and what I ran

I read everything the brief listed, in its order: protocol/C11RD_FREEZE.md and .json, the statement
audit, the derivation, the architecture, independence and cost docs, all calibration, validation and
rehearsal evidence, and all eight code files, line by line. I spot-checked the audit against the
original certifier and producer chain at 7375b9cd (S1 taboo_certify.py lines 1-407 in full; S2, S3,
S4 and S8 at the cited lines; file hashes S1-S5 and S8). I also read C11R's frozen `c11r_schema.py`,
`c11r_equiv.py` and the relevant parts of `c11r_compare.py`, plus the F_H record in C11R's sealed runs
and C11R's statement table. Both are permitted, blob-bound inputs.

I executed:
* The frozen validation, `python3 -I -S -B code/c11rd_validate.py --out <review>/review_validation.json`.
  Result: VALIDATION_CLASS = PASS, 23/23. It is identical to the committed evidence except for timings
  and V18's `files_scanned`: 31 files now vs 28 at freeze time, because the three validation-evidence
  files were written after that run. Both runs had zero hits. The worktree was clean afterwards
  (`git status --porcelain --ignored --untracked-files=all` empty).
* Recomputed sha256 of the 8 code files, 7 documents and the C7 primitive, plus the git blob ids of
  all 8 input bindings.
* Checked that V18's 17 hashes equal `value_patterns` of the two disclosed values. I also ran a broader
  leak scan over all 31 files at the freeze commit: decimal renderings anywhere, leading significant-
  digit substrings of 5 or more digits, and scientific notation, with a positive control.
* Git history and scope checks: diff 7375b9cd..71495747, rev-list over all refs and reflog, r6
  search, main and origin refs.
* Three small NON-TARGET checks of my own (drifts 1.038-1.042, 5/2 and [2.5, 2.5454] only), described
  under items 3 and 5.

I did not compute anything at a drift in [1.5, 2.5], did not run c11rd_runs.py in --mode real, did
not run c11rd_compare.py, and started no C11R runner. I opened no quarantine, C11R comparison,
REGISTRY_C2 or original cell or denominator artifact. I wrote only under `scratchpad/c11rd_review/`.
I also listed and grepped the author's scratch directory `scratchpad/c11rd/` as extra diligence on
"no target magnitude computed": every test and calibration script there uses e = 5/2 or e = 1.
Target-block strings appear only in freeze prose and in the V17 allowlist.

## Findings per item

### 1. Statement reconstruction — PASS
The audit's citations are accurate at 7375b9cd:
* S1 line 55 (K, C), lines 94-109 (window, atom cut, images, He weights), 115-128 (float_h1), 136-155
  (Ops, origin piece removed), 200-249 (certify_block / block_artifact), 261-281 (closed_h1,
  taboo_proposals) and 284-349 (certify_cell: residuals, env terms, propagation, D1 = min(a, b),
  D2, and the statement string at line 348).
* S2 lines 81-113 (9 sub-blocks, per-sub-block taboo block then cell artifact) and 161-165 (cell D1/D2
  = max).
* S3 lines 82-98 (kernel_norm: 2 phi(0), 4 phi(1)) and 136-141. S4 line 40 (H = 5). S8 lines 60-63.
* The hashes of S1-S5 and S8 match the audit table.

C11RD's statement records are the same statements as the original's:
* Freeze A-B and `c11rd_runs.statements` use kernel `Khat_e`, convention `atom_removed`, direction
  `UPPER_BOUND`, C11R's state-set string R, and drift domain exactly [680769/400000, 17885921/10000000].
* Aggregation is `max_over_sub_blocks` over an exact 4-way tiling (verified equal to freeze D).
* Dependencies are `C_T_independent, tau_independent`. These normalise to the original's {C_T, tau}
  (SAME), and route `independent_derivative_propagation` is the one C11R's frozen schema reserved.
* The statement table's original D1/D2 records carry the same kernel, convention, direction, domain
  and dependencies. V19 (strings equal to the frozen schema) and V20 (32-case battery through C11R's
  own `c11r_equiv.compare`, honest case EQUIVALENT) confirm this mechanically.

### 2. Derivation — PASS except one false step (B-1)
* Lemma 0 (invariance of R) is correct.
* Lemma 1 (arms, middle, image bands, l0) is correct.
* Lemma 2 is correct: differentiation under the integral; the windows are e-free in z;
  int|phi'| = 2 phi(0); int|phi''| = 4 phi(1), which I re-derived.
* Lemma 3 is correct: the induction gives sum_{n<N} Khat^n 1 <= w - Khat^N w; sup_R w = A because
  B >= 0; uniqueness holds.
* Lemma 4 is correct in the interior. The endpoint remark is incomplete (N-1).
* Theorem 5 is correct. I re-derived e0 = -Ghat r0, e1 = Ghat(Khat' e0 - r1) and
  e2 = Ghat(2 Khat' e1 + Khat'' e0 - r2). The atom bounds tau(...) and the sup bounds C_T(...) follow.
  Theorem 5 is pointwise in e, so the candidates need no consistency between D_k(e). The corollary and
  the |c0| + |c1| de + |c2| de^2 atom bound are correct.
* Lemma 6 is correct: Lagrange remainder, rho = max|v| over the TM range, unimodality bound.
* Section 7 (TM arithmetic) is correct. Section 8's e-centre invariant is correct and necessary: were
  the centre to differ between boxes, the maximum would bound residuals of different functions.

**The false step is the "Half-open convention" paragraph of section 1 (lines 49-53).** It says a value
on a band line s' = j is band j's, and that the true residual at s = k + 1 is "band k + 1's formula at
its lower edge". For k = 3 this fails. Interior points with s = 4 lie only in band-3 boxes, because
band 4 is axis-only. Their middle-piece images lie on the line s' = 3, which the stated convention
assigns to band 3's polynomial, but every band-3 box evaluates the middle with band 2's polynomial
(`c11rd_kernel.py:177-182`, tag `('M', k - 1)`; `:243`). So under the stated convention no box encloses
the true residual on the interior line s = 4.

I confirmed this numerically at the non-target drift e = 5/2. I used a synthetic candidate that is 1
on band 3 and 0 elsewhere, and evaluated it at the interior point (2, 2):
* the band-3 box encloses Khat D = 0.34138 (band 2's value on the middle);
* the stated convention's true value is 0.50000.

The certificate is nonetheless SOUND under the opposite, upper-closed convention: band 0 = [0, 1],
band k = (k, k + 1] for k = 1..3 (axis points included), band 4 = axis points with s in (4, 5]. Under
it:
* every x in R has a closed box whose formula is exactly its residual (the formula of the band with
  s in (k, k + 1]);
* the middle image s' in (k - 1, k] is band k - 1's, which is exactly what the code uses;
* arm endpoints are measure-zero;
* D(a) is band 0's constant.

The bound is therefore sound, but the frozen soundness argument states the opposite convention and
is false at one step. See B-1.

### 3. Implementation soundness — PASS (no path to a bound below the true sup found)
* `c11rd_tm`:
  * floor rounding with the ulp error added per coefficient (`fx_round`, `scale`, `__mul__`);
  * truncated terms by ceil|v|; cross remainder B(a) r_b + r_a B(b) + r_a r_b;
  * `compose` adds rad·r^j for the derivative enclosures and the Lagrange term with r bounding |dX|,
    remainder included;
  * `phi_sup_on` rounds toward 0, giving an upper bound;
  * `centred_moments` uses rho = max(|A|, |B|) over the box, width |B - A| and Mj from
    sup|He_{J+1}| · sup phi;
  * the Hermite recurrence and the Phi derivative shift are correct;
  * a negative remainder raises.
* `c11rd_kernel`:
  * pieces match Lemma 1 exactly, including the partial arm piece [s - 1, k], alarm-window ends
    m - C and C - p, and exclusion of the atom window for band 0;
  * arm images m' = (Mb0 - yc) + dM - v and p' = (Pb0 + yc) + dP + v are correct;
  * middle expansion and He shift are correct;
  * sources: h_1' = phi(al) - phi(au) and h_1'' = au phi(au) - al phi(al) are correct;
  * the e-Taylor residuals match freeze F;
  * boxes refuse band-straddling.
* `c11rd_certify`: `lam_k` = max over ALL leaves whether or not the tolerance was met; `merge` takes
  the max; atom bounds are exact; `propagate` matches Theorem 5; sub-blocks tile exactly.
* `c11rd_runs.certify_block`: per-sub-block candidates, cell values = max. The premise is A from the
  blob-bound F_H, and kappa = the C7 upper ends. F_H itself is a certified, premise-free, whole-block,
  atom-removed Khat_e supersolution w = 3429/500 - (1113/1000) m with positive margin and w_min > 0,
  exactly Lemma 3's hypothesis.
* My check (a), a non-target end-to-end sign audit: at e = 1.04 and e ≈ 2.5433 the float chain's
  atom values D1(a), D2(a), D3(a) agree to 5-6 digits with finite differences in e of D0(a), D1(a),
  D2(a) from independent solves at e ± 0.002. So the whole derivative system (kernel-derivative signs,
  source signs, chain structure) differentiates the actual d. The rigorous residual check alone cannot
  show this, because it is self-consistent.
* My check (b): the rehearsal's NT sub-block-1 bounds dominate the float |d'(a)| and |d''(a)| at that
  sub-block's ends and centre (0.052585 <= 0.053087; 0.106968 <= 0.113596).

### 4. Independence — PASS (disclosure honest; see N-8)
* No module imports the original graph, statically or at runtime. V16 checks this on all C11RD modules
  plus C7, and runs a fresh `-I -S -B` interpreter that imports every certifier module, with return
  code and module-count checks so the test is not vacuous.
* No certifier module names REGISTRY_C2, the quarantine, a comparison, or an adjudication or review.
* No original propagation code or matrices are used. The inequalities are the same mathematics and
  are disclosed in the independence audit section 2.
* No numeric literal outside a structural allowlist (V17).
* The only external code is C7's `c7_gaussian`, which imports only `fractions`.
* The disclosure (the author saw the values; they appear nowhere; no design choice references them)
  is consistent with everything I found.

### 5. Manufactured validation (23 tests) — PASS (reproduced 23/23); notes N-2, N-3
Coverage of the instruction's list:

| Required | Test |
|---|---|
| Gaussian moments | V01 (finite closed forms; whole-line even moments) |
| Polynomial test functions | V02, V03 (against C11's independent exact full kernel), V11 |
| Finite differences | V04 (kernel in e, rigorous FD tolerances with kappa3 = 1.6 >= 1.512 and kappa4 = 3 >= 2.802, both re-derived) |
| Scalar-drift collapse | V05, plus V20 `scalar_drift` -> WEAKER |
| Block-uniform enclosure | V06 (36 random (s, theta, e) points against an independent float residual) |
| Atom vs atom-removed | V07 |
| K_e vs Khat_e | V03, V08 |
| Premise dependency | V09 (7 tamper controls + monotonicity) |
| Zero | V10 |
| Symmetric | V11 |
| Sign cases | V12 |
| Kink-crossing boxes | V13 (refusals; continuity) |
| Tiny drift intervals | V14 |
| Invalid bounds rejected | V15 |

Most tests compare against independent references or carry positive/negative controls, so they can
fail. Weaknesses:
* V15(c)/(d) refuse through a validation-local `verify_claim` (N-2).
* No test pins the band-line convention, because V13 uses a globally continuous candidate (N-3).

### 6. Non-target calibration — PASS
All runs are at NT = [5/2, 3233337/1250000] or LOW = [1, 1 + 108337/1250000]. The scratch scripts
confirm the same. The decisions follow from the recorded evidence:
* TM order 6 comes from the C1/C2 order study.
* Physically uniform theta splits come from C2.
* 4 sub-blocks come from C4/C5, where the LOW r2 floor is e-truncation that only a narrower sub-block
  reduces (11.7x at quarter width vs the predicted 16x).
* The tolerances were set before C3.

I found no sign of target-magnitude influence. The sub-block choice is justified. Its margin is thin
at LOW (lam2 = 4.97e-4 vs the 5e-4 tolerance); see N-7 for the cost implication.

### 7. Prospective freeze — PASS on consistency with the code, except B-1
* Items A-V are all present, and the numbers agree with the code:
  * `frozen_parameters` match what the runner reads;
  * sub-block list D equals `CE.sub_blocks`;
  * 168 initial boxes; worst case 13,664 evaluations and 7.6 h;
  * caps: 5 workers, 43,200 s, 2 GiB;
  * schema I fields match the runner's record.
* All 8 code sha256s recompute equal. All 7 document hashes equal. The C7 sha256/blob equals. All 8
  input blobs equal (and the F_H runs blob equals the one at seal 5ff4cc5b).
* The validation manifest's freeze sha (4e3bd6c0...) is the committed freeze.
* The rehearsal ran on a pre-final freeze file (c3f6e5f1...). I diffed it against the committed one:
  it differs only in U-step and guard prose and in document hashes, as its manifest discloses.
* The inconsistency is B-1: the frozen derivation (hash-bound in `document_sha256`) asserts band-line
  semantics under which the code's cover is incomplete.

### 8. Execution architecture — PASS (notes N-6, N-7, N-10, N-11)
* The R0 barrier comes first and uses only builtin `sys`/`posix`. It checks the -I/-S/-B flags, that
  the code directory holds exactly the 8 files, and that the C7 directory holds no cache and no
  stdlib-named entries. V23 tests it with controls.
* The loaded-module check runs after the imports, before the lock and before the artifact.
* R1 checks the code and C7 hashes.
* R2 checks: ALLOW, code hashes, cell-306 block, max_executions 1, host/runtime, freeze commit
  ancestor, freeze file byte-identical, not shallow.
* R3 requires a clean namespace, including ignored and untracked files.
* R4 requires no runs artifact on disk and none ever committed (`--all --reflog --full-history`), then
  takes an O_EXCL permanent lock.
* R5 checks the premise and R6 the target.
* The spawn workers re-run the barrier (the rehearsal proves the flags propagate).
* Caps are checked every 30 s. The log prints counters and timings only, which I confirmed in the
  rehearsal log. There is no automatic retry.
* NOT_CERTIFIED writes no values.
* Comparator:
  * U1 checks seal lineage and exactly one EXECUTION_ACCEPTED line;
  * U2 has the comparator check its own and all frozen hashes (with a V21 control);
  * U3 recomputes exactly and checks tiling and the atom = band-0 constant;
  * U4 checks statement before number;
  * U5 is blob-bound, and its schema `magnitudes[k].value` matches C11R's loader;
  * U6 treats exact equality as INVALID;
  * U7 does a leak check at the freeze commit;
  * U8 reads C11R's classes from `result.per_target[k].CLASS`, which matches C11R's writer.
  * The output is created with exclusive create, and any refusal before U5 writes nothing.

### 9. Comparison rule — PASS
`classify_numeric` is C11R's factor-2 rule verbatim: V20(b) evaluates the table's literal rule strings
on a 72-point boundary grid. The precedence equals C11R's `numeric_phase`. Statement precedes number.
C_T, tau, Abar and D_lo are read from C11R's accepted comparison (blob `5269c2aa`) and never
recomputed. `factor == 2` is enforced from the table.

### 10. No target leakage, no historical mutation — PASS
* `git diff 7375b9cd..71495747` touches only the C11RD namespace (0 paths outside it). 71495747 is
  the only commit on any ref or reflog that touches the namespace.
* No runs artifact or lock was ever committed. There is no coverage-map r6, and r5 is untouched.
  main = c123b9bb and origin/main = 1cb45382, matching the freeze's record.
* Leak scans:
  * V18's 17 hashes equal `value_patterns` of the two disclosed values;
  * V18 passes on all 31 files;
  * my broader scan (renderings anywhere, 5+-digit leading substrings, scientific notation, with a
    positive control) found nothing in any of the 31 files at the freeze commit.

## BLOCKERS

**B-1. The frozen soundness proof states the wrong band-line convention, so the cover-completeness
step is false as written.** Location: `theory/D1_D2_DERIVATION.md:49-53`, bound by hash in
`protocol/C11RD_FREEZE.json` `document_sha256` and cited as the theory in freeze F; the same
convention appears in `code/c11rd_float.py:16-17`.

* **What the text says.** The paragraph assigns a value on band line s' = j to band j and argues the
  true residual at s = k + 1 is band k + 1's formula at its lower edge.
* **Why it fails.** For k = 3 that box does not exist in the interior (band 4 is axis-only). The only
  boxes containing interior s = 4 points (band 3) evaluate the middle image on s' = 3 with band 2's
  polynomial (`code/c11rd_kernel.py:177-182, 243`). Under the stated convention the true residual on
  the interior line s = 4 is enclosed by NO box. I demonstrated this at the non-target drift e = 5/2:
  computed 0.34138 vs 0.50000 for the stated convention.
* **Why the bound is still sound.** The code does not implement a convention at all; it evaluates
  closed boxes. Its cover is complete exactly for the upper-closed convention (band 0 = [0, 1],
  band k = (k, k + 1], band 4 = axis points with s in (4, 5]). Theorem 5 needs only one single-valued
  candidate with ||r_k|| <= lam_k, and D(a) is the same under both conventions.
* **Why it blocks anyway.** It makes the freeze's soundness argument false and inconsistent with what
  the code certifies. Qualification should not rest on a frozen proof with a false step.
* **Repair (prospective, documentation-only, no certifier change, no target information needed).**
  1. Restate the convention as upper-closed, with the corrected completeness argument: for s in
     (k, k + 1] the band-k formula is exact; the extra values sit on lower edges.
  2. Align `c11rd_float.py`'s docstring. This is recommended; that module is untrusted.
  3. Preferably add a manufactured test with a band-discontinuous candidate at interior points on
     s = 1, 2, 3, 4 (N-3).
  4. Re-freeze the document hash (and code hashes if code changes), re-run the validation, and
     re-review.

## NON-BLOCKING NOTES

**N-1.** `theory/D1_D2_DERIVATION.md:87-89`. The endpoint remark proves that (I - Khat_e)^(-1) exists
near E but not that it equals the Neumann series (the probabilistic d). One line closes it:
w >= 1 + Khat w with w <= C_T gives Khat^N w <= (1 - 1/C_T)^N w, so r(Khat_e) <= 1 - 1/C_T on E, and
upper semicontinuity of the spectral radius keeps r < 1 nearby. The original statement has the same
endpoint reading, so this is not a statement difference.

**N-2.** `code/c11rd_validate.py:553-560, 570-577`. V15(c) and (d) refuse through the
validation-local `verify_claim`, not production code (the "test that raises its own refusal"
pattern). V15(a), (b) and (e) do exercise production code, and the production counterpart of (c)/(d)
(comparator U3 exact recomputation) is exercised by V21. Consider pointing (c)/(d) at
`c11rd_compare.recompute`.

**N-3.** `code/c11rd_validate.py:479-491`. V13's continuity test uses a globally continuous
candidate, so it cannot distinguish band-line conventions. This is the gap through which B-1 went
unnoticed.

**N-4.** `code/c11rd_float.py:111-114, 205-208`. `band_of` and the `nodes` comment follow the
lower-closed convention. The module is untrusted and affects tightness only; align it with B-1's
repair.

**N-5.** `code/c11rd_certify.py:3` cites "Theorem 4"; the derivation numbers it Theorem 5.

**N-6.** `code/c11rd_runs.py:172, 195-208`. The lock lives in this worktree only, and R4's history
check sees only committed paths. The host binding is platform plus Python version. A second worktree
or clone on another darwin/3.14.5 host could run under the same grant. This matches C11R's accepted
design. The authorization should bind the worktree path and the host identity, or consume the grant
in a shared location.

**N-7.** Cost and cap. LOW4 had lam2 = 4.97e-4 against the 1/2000 tolerance. Where r2 is
e-truncation-dominated, (s, theta) bisection cannot reduce it (calibration C4; theory section 8). The
run then heads toward the depth-2 worst case of 13,664 evaluations: 7.6 h at 10 s per evaluation, or
9.9 h at 13 s, against a 12 h cap on a shared 6-core host. A cap hit gives NOT_CERTIFIED and consumes
the execution; soundness is unaffected. The authorization should require an otherwise idle host
(`caffeinate -i`, as the cost model says).

**N-8.** `docs/D1_D2_STATEMENT_AUDIT.md:17`; `docs/C11RD_INDEPENDENCE_AUDIT.md:12`. The author read
REGISTRY_C2.json, which carries original per-sub-row values, for structural facts that C11R's
statement table already provides (`drift_domain.sub_block_bounds`; D1/D2 `aggregation.artifacts`,
which I verified). This is disclosed honestly, the certifier never reads it (V16 data scan), and the
design (equal tiling) cannot exploit per-sub-row information. Future campaigns should take structure
from S7 only.

**N-9.** The U7 detector matches only decimal tokens, not scientific notation or rationals. My broader
scan closes this for the present freeze; consider widening U7.

**N-10.** `code/c11rd_compare.py:339-342`. The comparator's "runs once" check is on disk only
(`lexists`). An R4-style history check of `evidence/comparison/` would harden it.

**N-11.** `code/c11rd_runs.py:245`. The memory cap monitors the worker PIDs captured at pool start. A
worker that the pool replaces after a crash would not be counted.

**N-12.** The committed V18 evidence scanned 28 files (the evidence files were written afterwards). My
rerun scanned all 31 with zero hits.

## Commands I ran (all read-only in the worktree; outputs only under scratchpad/c11rd_review)

```
cd /Users/suzhe/ReBaseGuard-k5c11rd && git rev-parse HEAD && git status --short && git log --oneline -5
git diff --stat 7375b9cd 71495747 ; git diff --name-only 7375b9cd 71495747 | grep -v '^level4/closure_proofs/p5y_k5_tail_c11rd_d1d2_extension/'
git merge-base 7375b9cd 71495747 ; git rev-list --count 7375b9cd..71495747
cat protocol/C11RD_FREEZE.md protocol/C11RD_FREEZE.json ; cat -n docs/*.md theory/*.md code/*.py   (namespace dir)
shasum -a 256 code/*.py docs/*.md theory/*.md protocol/C11RD_FREEZE.md evidence/calibration/C11RD_CALIBRATION.json
shasum -a 256 level4/closure_proofs/p5y_k5_tail_c7_e2_lambda309/code/c7_gaussian.py
git rev-parse 71495747:<each input_bindings path> ; git rev-parse 5ff4cc5b:<C11R_RUNS.json path>
git show 7375b9cd:<S1..S5, S8 paths> | shasum -a 256 ; git show 7375b9cd:<S1> | cat -n ; sed -n on S2/S3/S4/S8 cited lines
sed/Read of c11r_schema.py 25-110, c11r_equiv.py 1-200, c11r_compare.py 414-532 and 786-800 (code only)
python3 -I -S -B -c "<print F_H record structure from C11R_RUNS.json>"
python3 -I -S -B -c "<print C11R statement-table D1/D2 records and comparison rule>"
cat evidence/calibration/C11RD_CALIBRATION.json evidence/calibration/logs/*.log evidence/*/MANIFEST.json evidence/*/*.log
cd <namespace> && python3 -I -S -B code/c11rd_validate.py --out /private/tmp/claude-501/-Users-suzhe-ReBaseGuard/ea6191ae-93b1-4f9c-b9ba-6cd0430d32ee/scratchpad/c11rd_review/review_validation.json
python3 -I -S -B -c "<compare review_validation.json with committed C11RD_VALIDATION.json modulo timings>"
shasum -a 256 protocol/C11RD_FREEZE.json evidence/validation/* evidence/rehearsal/*
python3 -I -S -B -c "<rehearsal summary: status, code hashes = freeze, per-sub-block lam>"
cd code && python3 -I -S -B -c "<CE.sub_blocks == freeze D; target; c11r_fh_premise(); kernel_norms(); sys.version>"
cd code && python3 -I -S -B - <<EOF  <value_patterns('<D1_disclosed>') | value_patterns('<D2_disclosed>') hashed == V.ORIGINAL_PATTERN_SHA256>  EOF
   (the two disclosed values are REDACTED here; the command printed only True/17)
cd <repo> && python3 -I -S -B - <<EOF  <leak scan of all 31 files at 71495747: renderings, 5+-digit substrings, sci-notation, positive control; prints counts only>  EOF
git --no-replace-objects rev-list --all --reflog --full-history -- <namespace> ; ... -- <namespace>/evidence/runs | wc -l
git diff --name-only 7375b9cd 71495747 -- . ":(exclude)<namespace>" | wc -l ; git ls-tree -r --name-only 71495747 | grep -i r6 ; git rev-parse main origin/main ; git worktree list
ls scratchpad/c11rd ; grep -rlE "<target-block rationals and 1.70-1.78 decimals>" scratchpad/c11rd ; grep -nE ... on its t_*.py, calib*.py, patch_v2.py, make_freeze.py
python3 -I -S -B -c "<diff scratchpad/c11rd/freeze_used_by_rehearsal.json against the committed freeze, key by key>"
cd code && python3 -I -S -B - <<EOF  <(a) float FD check of D1..D3 at the atom, e = 1.04 and e = 2.5433348, eps = 0.002; (b) rehearsal NT sub-block-1 bounds vs float |d'(a)|, |d''(a)|>  EOF
cd code && python3 -I -S -B - <<EOF  <(c) band-3 box at interior (2,2), s = 4, e = 5/2, band-indicator candidate vs closed forms>  EOF
cd <repo> && git status --porcelain --ignored --untracked-files=all | wc -l   (0 before and after)
```
