# Independent execution review — cell-307 RLR campaign (r1)
EXECUTION_ACCEPTED

## Reviewer statement

I am an independent, fresh, read-only execution reviewer. I did not write, freeze, qualify, review, grant, run, seal or
post-check anything in this campaign. I ran no `execute`, no `seal-only`, no `rehearse`, no `decoy-stage1`, no
certifier call and no consumer call on any cell. I created no ref and no commit, and I modified no repository file.
This file is the only file I wrote in the repository. Scratch files are under `/private/tmp/rlr307-exec-review/`, and
every Python run used `python3.14 -I -S -B` (afterwards: no `__pycache__`/`.pyc` in the namespace or in the certifier
directory).

* Worktree: `/Users/suzhe/ReBaseGuard-c307`, branch `p5y-k5-cell307-rlr-r1`, HEAD `2c50f534` at review time.
* NS = `level4/closure_proofs/p5y_k5_cell307_rlr_r1`.
* This review quotes no Γ, supply or rung value. It also quotes no number of any other tail cell and no decoy value.

**Evidence I produced.**
* `manifest_check.py`: every pin in `RLR307_FREEZE.json`, checked against the worktree, the grant commit and HEAD.
* `recon.py`: a reconstruction written from THEOREM_RLR307 §1. It reads the sealed blob from the object store and
  obtains κ2 by loading the pinned certifier only (no certification).
* A read-only `git fsck --unreachable --no-reflogs` (no `--lost-found`), plus reflog, ref and history queries.

## Chain and bindings (verified)

| commit | role | parent | changes |
|---|---|---|---|
| `cd5016f1` | freeze r2 | `0a0db965` (r1 failure evidence) | 4 frozen files (verifier repair) |
| `978d9965` | qualification | `cd5016f1` | `qualification/` only; `pass: true`, `review_mode: false`, freeze = `cd5016f1`, Q1–Q12 all true |
| `c91991c6` | qualification review | `978d9965` | the review only; line 2 `QUALIFICATION_ACCEPTED`, the token appears once, no REJECTED token |
| `5390b06d` | grant | `c91991c6` | `authorization/RLR307_GRANT.json` only |
| `b26c64a7` | seal | `5390b06d` | adds only `evidence/execution/RLR307_CELL307_RESULT.json` |
| `2c50f534` | post-execution checks | `b26c64a7` | ledger append and `postexec/` |

## The 11 checks

**1. Correct frozen commit: PASS.**
* `git log -1 -- NS/{code,protocol,theory,tests,config}` gives `cd5016f1` at the grant and at HEAD.
* The freeze tree `ef024c70` equals the grant's `freeze_tree`.
* The driver sha256 at the grant (the seal's parent), in the worktree and in the result is `69160c31…b0d9`. That is
  the grant's `driver_sha256` and the manifest's `driver.sha256`.
* All 42 manifest pins verified: 6 certifier, 15 consumer/input, 17 frozen files and 4 helpers. Each sha256 was
  checked in the worktree, at `5390b06d` and at HEAD, and each git-blob prefix where one is given. 0 mismatches.
* All 18 files under the frozen directories at the freeze are listed in the manifest. No frozen-directory file has
  changed since the freeze.

**2. Correct grant: PASS.**
* The chain is exactly freeze → qualification → review → grant (`HEAD^^^` = freeze at the grant).
* The grant binds all of the following:
  * `cell: 307`, `route: RLR`, `m: 5`, `detector: CUSUM`;
  * `closure_only: true`, `exactly_once: true`, `executions_authorized: 1`;
  * adoption, floor change, r6 and K5/P5Y closure all NOT AUTHORIZED;
  * the three chain commits;
  * driver sha256 `69160c31…`;
  * input-manifest sha256 `34309e57…e854f`, which equals the manifest file at the grant and now.
* It carries C1–C6, N4, N7 and the qualification-review conditions verbatim (G2).
* The result's `grant.grant_sha256` equals the sha256 of the grant file.

**3. Correct input set: PASS.**
* The result's `input_sha256` has the same 15 consumer/input keys as the manifest's `consumer_and_input_pins`, and
  every sha256 is equal.
* `input_sha256.certifier` equals the manifest's `certifier_pins` (6/6).
* `input_sha256.helpers` equals the manifest's `helper_sha256` and the driver's `HELPER_SHA256` (4/4).
* Every pinned file still hashes to its pin (check 1).

**4. Exactly-once semantics: PASS.**
* There are exactly two refs under `refs/p5y-k5-cell307-rlr-r1/` and none under `refs/rlr-tail/`:
  * `target-consumed` → commit `5390b06d`;
  * `pending-result` → blob `04161112`.
* `git log --all -- <result path>` returns exactly one commit, `b26c64a7`. Of the 83 unreachable commits, none has any
  path under `evidence/execution/`.
* The record has `target_evaluations: 1`, `target_evaluated: true` and `status: TARGET_EVALUATED`.
* The rerun was refused before anything:
  * `POSTEXEC_CHECKS` shows a second `execute` with exit 2 and `REFUSED CONSUMED: a ref exists under
    refs/p5y-k5-cell307-rlr-r1/`. That refusal comes from `check_not_evaluated`, the third check, before the grant,
    bindings, consumer, certifier or seal preconditions.
  * No trial commit object has the seal or HEAD as its parent, so that run never reached `check_seal_preconditions`.
* `seal-only` printed "nothing computed". The branch reflog has no entry between `b26c64a7` and `2c50f534`.

**5. Consumed marker: PASS.** `refs/p5y-k5-cell307-rlr-r1/target-consumed` is a commit ref to
`5390b06dc92c2580b92d743ca82629473e28ca90`, the grant.
* Positive evidence that it existed and named the grant at HEAD during Stage 1: all 30 rungs certified drifts inside
  the quarantined band.
* That is possible only after `rlr307_guard.arm_target` succeeded in each spawned worker. `arm_target` requires the
  marker = the grant = HEAD. Without arming, the guard refuses and the rung would have been recorded as an exception.

**6. No duplicate target calculation: PASS.**
* There is exactly one result and one seal.
* There is no emergency file (`rlr307-cell307-emergency-result.json`) in
  `/Users/suzhe/ReBaseGuard/.git/worktrees/ReBaseGuard-c307/`.
* The branch reflog shows one grant → seal update, at 11:05:43Z (empty message, see note 5), and nothing in between.
* Exactly one trial commit object (`fe6435d3`, "never referenced") has the grant as parent. It was created at
  08:47:13Z, 2 s after `started_utc`, and its tree equals the grant tree. So exactly one `execute` passed every check
  up to the seal preconditions at the grant.
* The Stage-1 rungs appear exactly once per (block, degree): 30 keys, 10 blocks × {4, 6, 8}, each count 1.

**7. Result sealing: PASS.**
* The seal commit's diff against its parent (the grant) is `A` of the result path only, mode 100644.
* The committed blob, the pending-ref blob and `git hash-object` of the worktree copy are all `041611126a32…`.
* The blob id recomputed from the bytes matches.
* The worktree copy is byte-identical to the sealed bytes: it reserializes identically.
* The self-hash `sha256` field verifies: sha256 of the sorted-key body without the field.
* The seal message says it was committed from in-memory bytes.

**8. Exact arithmetic: PASS.** Each of the following is an exact-rational string matching `^-?\d+(/\d+)?$`:
* every consumed rung input (τ, C_T, Ā, C_R, τ_a,lo/up, Ŝ2_up, T_N,up, D_lo, D1, D2, L1_up, L2_up, Λ_lo) and every
  rung/block supply and G-term, on all 30 rungs and all 10 blocks;
* the cell maxima;
* Stage 2's `A_exact`, `Gamma_exact`, `H_exact` and `M_after_exact`;
* the control's evaluated fields.

In addition:
* `Gamma_exact` parses as an exact `Fraction`.
* `stage1.independent_checks` = `{all_equal: true, rungs: 30}`.
* Every composition layer passed the driver's in-run equality checks, since any failure there raises
  INDEPENDENT_CHECK_FAILED and none was raised.
* The κ check is true for both constants.

**9. Output reproducibility without recomputation: PASS.** `recon.py` rebuilt everything from the sealed record.
* **Inputs.** It used my own D14 code, κ1 = 7978845609/10¹⁰ (equal to the pinned `c1b_certpw.KAPPA1`) and κ2 =
  pinned `c1b_certpw.KAPPA2`, an exact `Fraction` read after loading only. It used my own ladder key lists (Lemma
  Lad), which equal the pinned `LADDER_KEYS_MIN`/`MAX`.
* **Geometry.**
  * The cell-307 cover interval from `cells.json` equals REGISTRY_C2's `e_lo`/`e_hi`.
  * The C2 rule gives N = 10, which equals REGISTRY_C2's `sub_blocks`.
  * The sub-blocks tile the cell, and each outward 2^-20 hull contains its sub-block and is dyadic.
  * `blocks_planned` equals my ten blocks field by field.
  * Each rung's `drift`/`drift_radius` equals its hull's centre and radius, and its `degree` equals its key.
* **Results.**
  * (d) D14 recomputed on all 30 rungs from their own inputs equals `A0/A1/A2_SUPPLY` and `G0/G1/G2`: 30/30.
  * (a) The ladder composition of each block (min of the 11 upper keys, max of the 3 lower keys, over its certified
    rungs) equals the block record: 10/10. `certified_degrees` also match. D14 on the composed inputs equals the
    block supplies: 10/10.
  * (b) The componentwise maximum over the 10 blocks equals `cell.A{0,1,2}_SUPPLY_max`, with `n_blocks` = 10.
  * (c) S_RLR = (A0_I1, min(A1_I1, A1_cell), min(A2_I1, A2_cell)), with S_I1 = the control's `A_exact`, equals
    Stage 2's `A_exact` exactly. The recorded provenance (A0 I1, A1 RLR, A2 RLR) is consistent with which term
    attains each minimum. S_RLR ≤ S_I1 componentwise.
* **Control.** Its `A_exact`, `Gamma_exact`, `H_exact`, `M_after_exact`, `pass` and `provenance` equal the committed
  cell-307 entry of `C2_D5_FORECAST.json`, which I read myself.
* **Consistency.** `pass` is True exactly when Γ < 0 (checked on the exact rational).
* **Scope limit.** Γ itself is consumer output. It was not and may not be recomputed here. Its validity rests on the
  frozen consumer, which was reproduced exactly by the control and QC08. See note 6.

**10. Closure-only scope: PASS.**
* `git diff --name-only 7f45e048 HEAD` outside NS is empty. No commit since `7f45e048` (11 commits) touches a path
  outside NS.
* The r5 blob is `f978eeb6` at HEAD and at `7f45e048`, and it is the pinned one. The floor-r2 config blob is unchanged.
* No `K5_COVERAGE_MAP_R6` path exists in any ref's history.
* The result's scope is `CLOSURE_ONLY`. It has no adoption field, and `governance_state_before` records r6 absent.

**11. Mechanical outcome follows the frozen table: PASS.** The sealed status is TARGET_EVALUATED, Stage 1 is CERTIFIED
(10/10 blocks, 30/30 rungs), the independent checks are all equal, and the consumer reports `pass: True` (Γ(5, 307;
S_RLR) < 0 in exact rationals). Protocol §8 row 1 (manifest `outcome_table` "TARGET_EVALUATED + pass True") maps
this to the recorded **CELL307_CLOSED_UNDER_RLR**. `target.decision` and the top-level `mechanical_outcome` agree. I
state the recorded mechanical outcome only. The scientific adjudication is a separate later step, and closure is not
adoption.

## Condition E3 of the qualification review

| item | finding |
|---|---|
| exit code and sealed status | `EXECUTION_STDOUT.txt` is exactly the line printed at driver l. 831 (`RLR307 SEALED b26c64a7… (status TARGET_EVALUATED; one target evaluation; result not printed)`), which is followed by `return 0` for TARGET_EVALUATED. So the exit code is 0 (deduced from the unique print site; see note 2). Sealed status: TARGET_EVALUATED |
| one seal commit, result path only, marker names the grant | yes (checks 4–7) |
| control `field_matches` all true | 7/7 true, `reproduces_C2_exactly: true`, and independently confirmed against the committed file (check 9) |
| `independent_checks.all_equal` | true (30 rungs) |
| `blocks_planned` = the ten hull blocks of cell 307 | yes, recomputed field by field (check 9) |
| evaluation wall time < EVAL_CAP | 8309.233 s < 21600 s (EVAL_CAP_S = manifest `caps.evaluation_s`); no timeout |
| every `RUNG_EXCEPTION` | none: all 30 rungs are `RUNG_RETURNED` with `status: CERTIFIED`, and no rung log contains an error, refusal or traceback token. The N4 classification question did not arise |

**E1/E2, as far as the record allows.**
* The single execute ran from the qualified worktree:
  * the result's `identity` (worktree, git dir, common dir, branch) equals the driver's qualified constants;
  * `seal_preconditions.branch_head` = `grant_commit` = `5390b06d`;
  * Python was 3.14.5, the same as the qualification record, and the driver enforces `-I -S -B` and a clean tree
    before the marker;
  * `caffeinate` was attached.
* The only execute that reached the seal preconditions at the grant is the one above (the single trial commit, check
  6). Nothing was committed between the grant and the seal.
* `preflight` leaves no trace, so "only preflight ran before it" cannot be proven positively. Nothing in the ledger,
  refs, reflogs, object store or git dir indicates any other run at the grant. The grant was committed at 08:41:52Z
  and the launch was at 08:47:11Z.

**Ledger.**
* Lines 1–22 are byte-identical to the grant's ledger.
* The single `TARGET_EXECUTION` line (line 33) matches the record: cell 307, CUSUM, m 5, `new_target_evaluations: 1`,
  grant `5390b06d`, marker, seal `b26c64a7`, TARGET_EVALUATED, 10 hull blocks, ladder 4/6/8, the control counted
  separately. It was appended after the seal, as protocol §12 requires.

## Blockers

None.

## Notes (non-blocking)

1. **Refusal probe.** The post-execution checks ran `execute` a second time as the brief §23 refusal probe. That is
   in literal tension with E4 ("never `execute` again"), as in C12-R2's note 2. It was refused at the ref check,
   before any binding, consumer or certifier load, and it created no object (check 4). No effect.
2. **Exit code.** The execution's exit code is not recorded as its own field. It is deduced from the unique print
   site.
3. **Per-supply comparison.** The control's `per_supply_records_G_C1_C2` comparison is float-based, because C2's
   committed per-supply record stores floats. The load-bearing comparisons (`A_exact`, Γ, H, M, `pass`, provenance)
   are exact, and I re-verified them.
4. **Unreachable objects.** The unreachable trial commit `fe6435d3` and the object-store probe blob remain loose, as
   designed.
5. **Reflog message.** The seal's branch-reflog entry has an empty message (`update-ref` without `-m`). Cosmetic.
6. **Shared surface.** As protocol §6 discloses, the certified rung inputs come from one implementation, the pinned
   certifier. Γ comes from the frozen consumer, which is not re-implemented. This review re-derives every composition
   layer above the certifier and below the consumer. It does not re-certify inputs or recompute Γ, which is
   forbidden and by design.
7. **N6.** `cpu_seconds_workers` is not cited (N6).
8. **Next step.** The adjudication applies §8 verbatim and carries C1–C6, N4 and N7. Closure is not adoption, not a
   floor-r2 change, not r6 and not K5/P5Y closure.
