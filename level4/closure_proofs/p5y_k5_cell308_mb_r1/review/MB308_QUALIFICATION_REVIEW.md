# Independent qualification review of the cell-308 MB campaign r1, freeze r3 (reviewer reviewQUAL3)
QUALIFICATION_ACCEPTED

## 0. Basis

* **Reviewer.** reviewQUAL3. I am fresh: I wrote none of the reviewed material and reviewed none of it before. Brief 23
  (research `49804600`, `ledger/briefs/23_reviewQUAL_R3.txt`); its text matches the brief I received.
* **Object.** Worktree `/Users/suzhe/ReBaseGuard-c308mb`, branch `p5y-k5-cell308-mb-r1`, HEAD `7eb057bb` (official r3
  qualification), whose only parent is the r3 freeze `c46434a3`. The chain
  `a7fe3028 -> 3a05aef7 -> 29b68d5e -> d031dad8 -> c46434a3 -> 7eb057bb` is linear.
* **What I ran** (each ledgered in the research ledger, class REVIEW, agent reviewQUAL3):
  * `mb308_qualify.py --review` at `7eb057bb`: PASS on every case and gate Q1-Q12, 243 s, verifier sha256
    `48d48049…`;
  * the same review mode on `qualification/r2_failed/` (a can-fail check): FAIL on Q12 exactly as r2 failed;
  * `mb308_driver.py preflight`: `MB308 PREFLIGHT PASS`, exit 0, on AC;
  * an independent leak scan with my own tokeniser (counts only);
  * read-only object-store, power-log and file checks.
* **Not run.** `--heavy` (not needed, see §7), `execute` and `seal-only`.
* **Not done.**
  * Nothing computed for cells 305-309 beyond the review mode's own committed-305 reproduction and its record-token scan.
  * No drift in the band or its mirror evaluated.
  * No decoy value read beyond runtime and status.
  * No ref created or moved. No git add or commit. No power or system setting changed.
  * This is the only file I wrote in the worktree. Scratch lives in the session scratchpad `reviewQUAL3/`.
  * After both review runs, `git status --porcelain --ignored --untracked-files=all` was empty and every ref was
    unchanged.

## 1. Theorem integrity: PASS

* **Copy.** `theory/THEOREM_MB.md` equals the research r1 blob at `bfa9ad3c` (Q1: sha256 and blob).
* **Review corrections.** r1 applies REVIEW_THEOREM_MB_R1's C1-C6:
  * C1: S_i admissible on E ∩ B_i;
  * C2: the dominance premise M = mag(H_final);
  * C3: the D14 A0 slot min(Ā′_eff, C_R);
  * C4: the quasi-convexity argument; the endpoint-only rule is invalid;
  * C5: E = [e0 − ρ, e0 + ρ] as a premise;
  * C6: the per-piece refusal as a consumer obligation.
  N3 became Lemma DM. I checked DM's proof myself: D = τ_a/Λ ≥ τ_a,lo/Ā′ whenever Ā′ ≥ sup_B Λ, which M-U gives.
* **Code equals the text.**
  * **Geometry.**
    * `mb308_guard.partition/hull`: N = ⌈width/(1/100)⌉, which gives 11.
    * b_i = ⌊2^20·lo(E_i)⌋/2^20.
    * `stage1.plan` cross-checks against rlr307_stage1 and requires strictly increasing b_i ≥ 0.
  * **Envelope.** `stage1.envelope` is Ū_i = min_{j≤i} U_j over the declared b_j only.
  * **Members.** `supply.dvm` uses Ā′ = min(Ā, Ū_i) through the frozen `atom_constants_r2`, with no D_lo refresh.
  * **D14-M and DM.** `supply.d14m`:
    * Ā′ = min(Ā_B, Ū_i);
    * D_lo′ = max(D_lo, τ_a,lo/Ā′), refused if below D_lo;
    * pinned `assemble` gives A0_SUPPLY = min(Ā′_eff, C_R);
    * Lemma G from the same C_R;
    * S_I1 is always present and the combination is a componentwise min.
  * **Consumer.** `consumer._geometry` holds the C5 identities and x_lo > 0.
    * The C6 per-piece check runs at each piece's inner end with that piece's triple.
    * G-R3b is checked per r and per block.
    * The primary is `tpt.penalty_blocked` with pieces cut at every tile end and at e0.
  * **Pinning and exactness.**
    * Every member is cross-checked exactly by rlr307_independent and by F2.
    * Floats are refused at the exact layers (`q`, `_exact`).

## 2. Closure criterion: PASS

* **The decision.** `consumer._stage2` sets Γ_dec = g_hi + max(P_B, P_hi) and closes iff Γ_dec < 0 in `Fraction`. Then
  `driver.decide` applies it. Γ_dec = 0 does not close. This is the K5 criterion, unchanged.
* **The two failure paths cannot close.**
  * **Independent side.** P_hi is absent only when F2 is absent, and F2 absence is a refusal in execute
    (`check_bindings`, `load_science(allow_uncommitted=False)`: F2_MISSING). An F2 refusal, P_lo > P_B, G-T2 below
    the independent lower bound, dominance failure or a G-R3b mismatch each raise IndependentCheckFailed, which is
    INDETERMINATE.
  * **Primary side.** Any exception in the primary is TARGET_EVALUATION_FAILED, which is INDETERMINATE.
  * **Weakening only.** Missing Stage-1 certificates only weaken S_i: S_I1 is always a member.

## 3. Only route MB, exactly once; controls and tripwires: PASS WITH NOTE

* **Tripwires.** `consumer.tripwires` stubs:
  * `penalty_closed`, `penalty_c5t`, both Riemann sums, `tpt.evaluate`, `tptb_tail.evaluate_bundle` / `_evaluate`;
  * F2's `p5_c5t_closed_form` / `tpt_endpoint_only`;
  * in control mode additionally `penalty_blocked`, `independent_penalty`, `transport_gate` and F2 `tptb`.

  It proves the stubs armed (`verified_armed`) and firing (`verified_fires`), and refuses otherwise.
* **Static checks.** QC11 checks by AST that:
  * Stage 2 names no other route;
  * the control path names no penalty;
  * the target control and Stage 1 run only inside `run_execute` / `evaluate_target` after the grant.
* **C-A and C-B.** They compare only; they emit equality booleans and member names. The committed 305 rehearsal record
  (QC01) contains exactly that, with both tripwire flags true.
* **Note (C7(a), "C-B on 308").** Brief 23 forbids me to run C-B on 308. I verified it by code identity instead: the
  same `control_cb` and `CON.public` runs as for 305, with the guard's reproduction context for 308 admitting only
  the cover and its three points. It runs once, before the marker, inside `execute`; CONTROL_FAILED consumes nothing.
* **Exactly once.** The marker is created by compare-and-swap from the zero id; a prior ref under the namespace, a
  result anywhere or an emergency file each refuse (QC10 T10, T11, T13, X02).

## 4. Admission rule D5, budgets, stricter alarm reading: PASS

`stage1.pointwise` implements D5 as frozen:

* **Admission.** An upper rung is admitted only if it is VERIFIED and L_other ≤ U.
* **INCONSISTENT.** L_other > U for any certified upper rung, verified or not, gives INCONSISTENT. So does any
  REFUTED rung.
* **Not admitted.** A missing other-implementation lower rung gives ALARM_UNAVAILABLE. UNDECIDED rungs are not
  admitted. C1b uppers with d > 6 are NOT_INDEPENDENTLY_VERIFIED and never admitted.
* **Consequence.** `driver.stage1` raises Inconsistent, which is INDETERMINATE.
* **What is admitted.** The admitted U is the verified claim itself: `a0core.c2bx_rung` sets both `record.U` and the
  certificate's `claim_w_atom` from the same `w_atom`, and `c2b_verify` requires `W_at_atom_equals_claim`.
* **Budgets.** `VERIFY_BUDGET` equals protocol D14 (vd_pl max_depth 12, max_boxes 10^6; vd_verify max_boxes 200 000,
  min_width 2^-40). Both are operation counts. The verifiers run serially (`workers=1`).
* **Tests.** QC05 exercises every branch:
  * both cross alarms;
  * both refutations;
  * UNDECIDED;
  * ALARM_UNAVAILABLE;
  * "d8 never admitted";
  * a same-implementation L > U, which is not an alarm.

## 5. Independence and exact comparison: PASS WITH NOTE

* **Imports.** F2 (`mb_independent.py`) imports only `__future__`, `fractions` and `re`. F3 (`tuple_independent.py`)
  imports stdlib only. QC11 checks both by AST.
* **Freeze before reading.**
  * F2 recorded its sha256 `32aa83a8…` in the ledger before any primary read (ledger line 129; INDEPENDENT_REPORT
    timeline) and stayed byte-identical afterwards.
  * F3 recorded `47ae88dc…` at its freeze (line 151), with the reading record before it; its harness refuses a module
    whose hash differs.
  * Both pins are current on the research branch; all 19 research-namespace pins match.
* **Verifiers.**
  * `vd_pl` and `vd_verify` are stream VERIFY's own implementations. Their measured shared surface is boilerplate
    plus the layout-fixed mesh loops (protocol §6).
  * Their `Q` is re-pointed to the formal guard, and the identity is checked in `mb308_pinned`.
* **Exact comparisons.** Every primary-vs-independent comparison is exact (`==`, or the one-sided `P_lo ≤ P_B`):
  * the ladder;
  * each member;
  * the envelope;
  * S_i;
  * the G-R3b tuple and every block polynomial;
  * G-T2's gated side;
  * F2's bracket.

  The only tolerance, `transport_gate`'s loose upper side, is recorded as `informational_loose_upper_side` and never
  gates.
* **Note.**
  * The freeze-before-read evidence is ledger and mtime process evidence, not git facts (incident review N2).
  * The RLR block certificates are single-implementation, disclosed as in 307; Lemma Lad and assembly are
    cross-checked.

## 6. Qualification gates Q1-Q12 and cases: PASS

* **Official r3 report.**
  * `pass` true, `review_mode` false, freeze `c46434a3`, 16 cases, no missing `pass`.
  * All eight record sha256 values match the committed bytes. `target_evaluations` is 0.
  * My review run reproduces every case and gate, heavy cases re-verified from the committed records.
* **Can the gates fail? Evidence.**
  * The same review mode on the r2 records FAILS Q12:
    * projection 28 495 s, needed 42 743 s;
    * per-job C1B:10, RLR:6, RLR:8;
    * TIMING_AMBIGUOUS for both decoys (no provenance).

    That is r2's failure reproduced through the r3 decision function.
  * QC04: every compared pair has more than 0 leaves (17 to 189), and each pair's planted one-leaf mutation is
    detected.
  * QC05: 1980/1980 exact block equalities; all 10 mutants rejected, 8 of them only by the two-sided comparison.
  * QC07: 29/29 E4 controls; T1-T10 plants detected, including C5, C6, tiling, common-mode G-R3b and tripwires.
  * QC06: byte identity for the 5 certificates, plus the FD, direction-swap and D5 verifier controls.
  * QC08: both planted wrong bounds flagged.
  * QC09: band, mirror and straddle refusals before work. Sandbox arming refuses no marker, a dropped pair, an extra
    band pair and a marker not naming the grant; it arms with exactly 37 pairs.
  * QC10: 42/42 flows.
  * QC12:
    * 0 tail hits over 52 files and 0 of 309 record tokens;
    * planted controls fire;
    * the one timing-key exemption is an r1 runtime (§13(b));
    * the one geometry exemption is the manifest guard field.
  * QC13: builder ledger lines have pre-grant classes and 0 target.
  * Q8: 21 frozen files, 54 external pins, 0 mismatches, bindings and lineage OK.
* **The r2 repair (§13).** QC04 strips exactly {seconds, wall_seconds, cpu_seconds} (plus job-level `cpu_cap`), with
  non-vacuity and a planted control. QC12's exemptions are narrow and counted. Both still pass on the r3 records.
* **The r3 repair (§14).** `_q12_core` is r2's `q12_caps` body plus the timing conjunct only (AST diff of the two
  functions): `pass = caps_pass and timing_clean`. `_decoy_jobs`, the LPT model and every threshold are unchanged,
  so r3's Q12 is strictly stronger.

## 7. The r3 repair and its conditions: PASS

**(a) D1: PASS.**

* **Protocol.** The frozen `MB308_PROTOCOL.md` (`09ac4884…`) contains the substituted citation exactly once.
  Reversing that one substitution to `DELTA_REVIEW_CITATION_PENDING` gives exactly `64c29109…`, so no other byte
  changed. The citation names research `1571040d` and `2afbbf4c…` (the delta review's sha256 at that commit), and
  `4b38eef2` / `d39e25ef…` for the first review. All four match the object store.
* **Manifest.** Replacing only the protocol entry of the frozen `MB308_FREEZE.json` (`8799cdac…`) with the sha256 and
  blob of the `64c29109` bytes, and re-serialising with the writer's format, gives exactly `04e2899a…`.
* **Other files.** Host `6702a9be`, driver `411252b2`, qualifier `48d48049`, flows `54c9c8ee` and cases `57c78b41`
  at the freeze equal the review hashes.
* **Commit scope.** `c46434a3` touches exactly those 7 files and 10 renames. All renames are R100, and every r2
  record's blob is identical in `r2_failed/`. `r1_failed/` is untouched.
* **Driver diff r2 to r3 (my own read).** Environment only: the host import and pin, `require_ac`, `close_host`,
  `keep_awake -i -m -s`, the sampler before the marker, and decoy provenance. The cap lines are byte-identical in
  r1, r2 and r3.

**(b) Q12 on the official records: PASS.** I re-assessed both decoys from their stored raw readings, twice: in the
official report and in my review run.

| decoy | status | samples | largest spacing | sleep gap | thermal_level_max | ThermalEvent | load max (1 min) | Stage-1 wall |
|---|---|---|---|---|---|---|---|---|
| QC02 297, 5 blocks, 5 workers | CLEAN | 116 | 60 s | 0 ms | 2 | 0 | 154.84 | 6971.9 s (+0.9 s Stage 2) |
| QC03 316, blocks 0-2, 1 worker | CLEAN | 194 | 60 s | 0 ms | 2 | 0 | 154.84 | 11669.1 s |

* **Channels.** Each run has power AC at the start, at every sample and at the end; `kern_us` unchanged; power-log
  events empty. Each host interval covers its walls (floored raw span + 1 s ≥ walls).
* **Controls.** 14/14 behave as declared:
  * per-job: `eval_cap_ok` true and failing keys exactly {RLR:8};
  * EVAL-only: no failing per-job key;
  * combined: both reasons;
  * each timing plant: its own status with the caps passing;
  * the fixture parse is exactly [Sleep, DarkWake, Wake].
* **Caps (runtime only).** Projection 17 545.8 s against EVAL_CAP 28 800 s (1.5× needs 26 319 s). Per-job maximum
  walls against caps:
  * RLR 8: 4093.1 s against 8700 s;
  * RLR 6: 1702.2 s against 4200 s;
  * C2b N80: 1121.7 s against 2700 s;
  * every other job is under 1/5 of its cap.

**(c) O7: PASS.** The wall-clock span `end.epoch_s − start.epoch_s` minus the raw-clock span is +0.36 s for QC02 and
+0.12 s for QC03. At every sample the difference stays within 0.82 s, i.e. integer-second quantisation. No wall-clock
step.

**(d) Preconditions and O conditions: PASS WITH NOTE.**

* **Recorded preconditions.** AC true, thermal-pressure level 0 true, sleep channels available true.
* **Power log.** My read-only copy covers 2026-09-22 to now. From 07:01Z to 10:19Z it has only `Assertions` entries:
  no Sleep, Wake, DarkWake, ThermalEvent, clamshell or battery line.
* **Keep-awake.** The qualifier's caffeinate (pid 4592, `-i -m -s`) created PreventSystemSleep at 07:03:09Z and held
  it for 3:14:42, i.e. the whole run.
* **Whole run.** The qualifier's own record is CLEAN (194 samples, spacing at most 62 s, AC throughout).
* **Note.** The start snapshot's 1-minute load was 5.72; the coordinator's ledger says about 2.1. The thermal level
  was 1 five seconds after the start and 2 through most of the heavy window. Both are recorded and non-gating (O3
  foresaw this). They can only lengthen runtimes, and the runtimes match r1's (RLR 8: 297 at 3379.7 s against r1's
  3366-3380 s; 316 block 0 at 4093.1 s against r1's 4150 s).

**(e) F3 is binding, and Q12 passed for the right reason: PASS.** §14 pre-declares that any r3 Q12 FAIL stops the
campaign. Here `caps_pass` is true on runtimes whose host provenance is CLEAN and covering, `timing_clean` is true,
and the controls pass. It is not a pass by exemption or omission.

## 8. Exactly-once mechanics, grant chain and guard: PASS

* **Refusals before the marker.** `run_execute` refuses, in order, on:
  * interpreter flags;
  * identity (worktree, git dir, common dir, branch);
  * a prior evaluation (any ref under `refs/p5y-k5-cell308-mb-r1/`, a result anywhere, the emergency file);
  * `lstat` of the guarded paths;
  * a dirty tree, including ignored objects in the namespace, and git locks;
  * `check_grant`;
  * pins and lineage;
  * r5 / r6 state;
  * seal preconditions;
  * CPU caps;
  * AC (`require_ac`, before the marker, HOST_NOT_ON_AC → exit 2);
  * the controls and geometry.
* **`check_grant`.** HEAD is the grant commit and changes only the grant. The chain is
  freeze → qualification → review → grant, as named, and `HEAD^^^` is the freeze. The review commit changes only this
  file, whose line 2 must pass `verdict_ok`. The qualification commit holds qualification files only, with an
  official PASS at the freeze. The grant binds the driver sha256 and the manifest sha256.
* **After the marker.** The marker is created by CAS, then `after_marker` runs:
  * it never raises;
  * the EVAL_CAP alarm, then the record, then `close_host` (never raises);
  * pending blob and ref, else the emergency file;
  * seal from memory through a private index;
  * `O_EXCL|O_NOFOLLOW` materialisation;
  * exit codes 0 / 3 / 4 / 5 / 6 / 7 as documented.
* **Tests.** QC10 exercises every branch: X01-X03, C01-C02, T01-T23 (T23 is the planted battery reading →
  HOST_NOT_ON_AC, marker unchanged, evaluator not called), the tamper set T22 and P01-P11.
* **Guard.** DECOY by default. `arm_target` requires the marker to name the grant commit at HEAD and the admitted set
  to equal the guard's own D1/D2 derivation from `CELL308`: 11 tiles, 11 hulls, 11 points and the cover with its
  three points, 37 pairs. Every worker re-arms from git.
* **The 37-pair set is acceptable** as the disclosed deviation from a hash-bound authorization file. It is a pure
  function of the guard bytes, which are pinned by sha256 in `HELPER_SHA256` inside the driver whose sha256 the grant
  binds. Arming requires exact set equality, and a dropped or extra pair is refused (QC09).
* **My own trace of the armed target path.** Decoys cannot exercise it, so I traced every guard call statically:
  * `c1b_certpw` (e_c ± e_r = the hull exactly, as rlr307_stage1 passes centre and radius);
  * C1b / C2b / vd_pl / vd_verify at b_i points;
  * `tpt._check` and `_check_blocks` (the cover, whole tiles);
  * `tptb_tail._guards` and `check_blocks` (the cover, e0 − ρ .. e0 + ρ, the three points, tiles);
  * F3's adapter (the label and the cover).

  Every object presented lies in the 37-pair set. No split piece such as [lo(E_5), e0] reaches the guard: `_pieces`,
  `band_at` and `independent_penalty` do not call it. F2's research band guard is off only when the formal guard is
  ARMED.

## 9. Caps: PASS

* **Unchanged.** EVAL_CAP 8 h, PRE_CAP 1800 s, workers 5 and the per-job caps are byte-identical in the r1, r2 and
  r3 drivers.
* **The §3.2 rule.** I recomputed it from the pre-freeze "used" runtimes: every frozen per-job cap, the
  13 110.8 s projection and EVAL_CAP = max(6 h, ⌈7.28 h⌉) = 8 h.
* **Q12 re-derivation.** Q12 re-derives from the official runtimes (§7(b)).
* **Risk of a cap hit.** Low.
  * **EVAL_CAP (wall).** It is 1.64× the projection. The projection assumes every job of every block at the largest
    observed wall.
  * **Per-job caps.** They are CPU-time limits, at least 2.1× the largest observed wall, and CPU time ≤ wall for these
    single-threaded jobs.
  * **Conservative measurement.** The official walls were measured with 7-10 CPU-bound processes on 6 cores at
    thermal level 2. The execution runs only the 5 Stage-1 workers.
  * **The target lies between the decoys.** 297 lies wholly below the band and 316 wholly above it. The costliest
    kind (RLR 8) is dearer at 316 than at 297.
* **Residual risk and its consequence.** The main residual risk is a lid-close sleep during the 5-8 h evaluation,
  which only the operator conditions prevent. A cap hit is INDETERMINATE, never a closure.
* **PRE_CAP.** Its margin is very large: the 305 rehearsal takes about 1 s.

## 10. Provenance, pins and lineage: PASS

* **Q8.** In my review run: 21 frozen files and 54 external files, each with sha256 and git blob at HEAD; 0
  mismatches, 0 unlisted, 0 absent; driver sha OK.
* **Bindings.** `check_bindings` passes, covering pinned modules, F2, F3, the consumer inputs and `HELPER_SHA256`,
  including `mb308_host.py 6702a9be…`.
* **Research pins.** All 19 research-namespace pins equal the research-branch HEAD blobs.
* **Lineage.** The lineage check (20 commits and roles) passes in preflight.
* **Manifest.** The manifest's `external_files` also pin the QC06 A0 certificates committed at `fc4eeeee`.

## 11. Quarantine, incident-review conditions, C4: PASS WITH NOTE

* **Leak scans.**
  * QC12 (review run): 0 tail hits and 0 record-token hits.
  * My own scan: the sanctioned 70 patterns plus 464 tokens I built from the committed cell-308 records (C2
    forecast cell and supplies, REGISTRY_C1/C2 rows, TCT_INPUTS_308). It finds 0 token hits in the 52 namespace files.
    Its one pattern hit is the known r1 runtime inside `record/seconds/…` (§13(b)).
* **Ledger.** 212 lines; the only flagged line is the required C2 QUARANTINE_RULE_BREACH record (0 proxies).
  Every line has 0 target evaluations. Since the r3 freeze there are only the coordinator's two INFRASTRUCTURE lines
  and my REVIEW lines.
* **Decoys and the band.** 297 is wholly below the band and 316 wholly above it (checked as booleans on cells.json).
* **C1-C9.**
  * QC13 checks the C1-C8 files by path and the incident review's verdict line and date (before the freeze).
  * C3 wording is in protocol §2.
  * C7(b): runtime and status only enter Q12.
  * C9 holds by §2-§3.
* **C4.**
  * **The record.** `ledger/USER_RULING_C4.md` at research `0aeaec23` records verbatim, before any qualification
    review, "C4 = ACCEPTED FOR CLOSURE-ONLY EVALUATION, WITH THE DOCUMENTED RESULT-CHASING / INCIDENT-INDEPENDENCE
    LIMITATION PRESERVED", with points 1-8.
  * **Correctly ruled.** It is explicit, closure-only, conditional on every remaining gate, and not a substitute for
    any of them. Point 7's stop rule was honoured at r2.
  * **Two caveats.**
    * The ruling names incidents 01-03 and the limitation. It names H4.3b, I-a…I-e, E1′ and the review only through
      "reviewer condition C4", whose text lists them.
    * It was given while r2 was running. Its authorization is not tied to r2, and the user separately authorized r3
      (protocol §14).
  * **What the grant must carry** is set out in G3.
* **Note.** The band-bracketing A0 validation drifts 11/10 and 27/10 are used again by QC04 and QC06. 27/10 lies
  nearer the band than decoy 316. They are not C7(b) decoys: they are stream-A0 validation drifts, disclosed in E1′
  ("the A0 tables at the band-bracketing drifts"), and ledgered NONTARGET_DRIFT_VALIDATION. QC04's ladder records at
  11/10 hold certified values and are latent proxies (see E6).

## 12. Temporal integrity: PASS

The order in the object store (commit times, +0900):

| step | commit | time |
|---|---|---|
| freeze r1 | `a7fe3028` | 05:38 |
| r1 FAIL | `3a05aef7` | 08:59 |
| freeze r2 | `29b68d5e` | 09:10 |
| C4 ruling | `0aeaec23` | 11:29 |
| r2 FAIL | `d031dad8` | 13:59 |
| assessment | `2fa80954` | 14:02 |
| addendum a1 | `64dc4cce` | 14:06 |
| brief 21 | `947e5000` | 14:28 |
| REPAIR_REJECTED | `4b38eef2` | 15:16 |
| brief 22 | `44b2c74c` | 15:32 |
| DELTA_ACCEPTED | `1571040d` | 15:53 |
| freeze r3 | `c46434a3` | 15:56 |
| r3 qualification | `7eb057bb` | 19:22 |
| brief 23 | `49804600` | 19:24 |

* **No qualification review before this one.** Brief 20 was never sent.
* **Load-bearing elements.** Theorem `bfa9ad3c`, F2 `a7014669`, F3 `0292d654`, the A0 review `e042c8d1` and the
  incident review `f42fef40` are ancestors of the freeze (lineage). No target evaluation exists.

## 13. Other findings

* **N-a.** The frozen `config/QUALIFICATION_CASES.json` still carries `"status": "BUILDER DRAFT (not frozen)"`. It is
  a stale label in a frozen, manifest-pinned file; it changes no gate. It cannot be edited after the freeze;
  documents citing the file should say it is frozen at `c46434a3`.
* **N-b.** The user's r3 authorization exists only as the coordinator's paraphrase ("r3 as specified, cool host", in
  brief 21 and protocol §14). There is no verbatim record.
* **N-c.** Thermal level 0 at start, lid open and low-power mode off are operator conditions. The driver enforces AC
  only; it records the thermal level in `environment.host_at_start`.
* **N-d.** `check_seal_preconditions` writes an unreferenced probe blob and a trial commit object before the marker.
  This is the 307 design and harmless.

## GRANT CONDITIONS

* **G1. Scope and bindings.** The grant is committed alone. It is the direct child of the review commit, which is the
  direct child of `7eb057bb` and adds only this file. It adds only `authorization/MB308_GRANT.json`, which binds:
  * schema `rebaseguard.p5y.k5.cell308-mb-r1.grant.v1`, cell 308, route MB, `exactly_once: true`,
    `closure_only: true`;
  * freeze `c46434a399eca18a709616a4a4d51918d1a30298`;
  * qualification `7eb057bbbcb3c8d18afc852c1d90f0b3fc0fefc8`;
  * this review's commit;
  * driver sha256 `411252b2a9fa601cc5c1ba34abaf08482cf95a06e2ce7e4d5e5a5bd9e1f56dcb`;
  * input-manifest sha256 `8799cdac9c6fa80fe106ec626848f4f75ec41800567ddfb2230d39c86831b36a`.
* **G2. Nothing changes.** No file under `code/`, `protocol/`, `theory/`, `tests/`, `config/`, `errata/` or
  `evidence_prefreeze/` changes after this review. Any needed change means STOP: no same-round repair and no r4 with
  the same caps without a new recorded user decision (§14).
* **G3. The C4 ruling.** The grant records:
  * the user's value verbatim;
  * the file `level4/closure_proofs/p5y_k5_cell308_research/ledger/USER_RULING_C4.md`, git blob
    `1fdd233ecb2649dbf3a4837dd36497bd25357144`, sha256 `dd1d6317…cbbfa`, research commit `0aeaec23`;
  * points 1-8 verbatim, as grant conditions;
  * the incident review's C4 text verbatim. That review is
    `reviews/INCIDENT_INDEPENDENCE_REVIEW_MB308.md`, blob `297baf9f…`, sha256 `24e1398a…`, commit `f42fef40`. Its C4
    names incident 01 and residue, incidents 02-03, H4.3b, I-a…I-e with E1′, and the review. The grant states that
    the ruling was given on that condition;
  * conditions C1-C9 verbatim;
  * protocol §11's liabilities verbatim;
  * "temporal and parametric independence only";
  * result-chasing MEDIUM–HIGH.
* **G4. The r3 record.** The grant cites:
  * the user's r3 authorization as recorded in protocol §14 and brief 21 (N-b);
  * the repair reviews: `4b38eef2` (`d39e25ef…`, rejected) and `1571040d` (`2afbbf4c…`, DELTA_ACCEPTED under D1);
  * the §14 pre-declared consequences.
* **G5. This review's conditions.** The grant names E1-E8 and notes N1-N8 of this review. The adjudication carries
  G3's text.

## EXECUTION CONDITIONS

* **E1. The one run.**
  * Exactly one `python3.14 -I -S -B level4/closure_proofs/p5y_k5_cell308_mb_r1/code/mb308_driver.py execute`, from
    the qualified worktree root on this host, with the grant commit at HEAD.
  * A clean tree, including ignored objects in the namespace (e.g. no `.DS_Store`).
  * Only `preflight` (read-only) may run before it.
  * Until the SEAL line is printed, nothing else runs: no qualifier, decoy, rehearsal or review run, no other agent
    compute, and no other process that commits, checks out or runs campaign code.
* **E2. Host conditions (review r3 E1; operator-enforced except AC).**
  * AC connected throughout.
  * The lid open for the whole run: lid-close sleep cannot be prevented, and it would waste the one evaluation.
  * Thermal-pressure level 0, read immediately before launch.
  * `lowpowermode` 0.
  * The 1-minute load near idle.
  * No other heavy work.

  The operator records these readings before launch, and the execution review compares them with
  `environment.host_at_start`.
* **E3. Provenance never changes the result (review r3 E2).** Host provenance never changes the status, the outcome
  or exactly-once. There is no rerun and no reinterpretation on host grounds. An EVAL_CAP hit is the pre-declared
  INDETERMINATE.
* **E4. The execution review checks.**
  * The exit code and sealed status.
  * One seal commit adding only the result path, and the marker naming the grant.
  * The controls:
    * every C-A field match true;
    * C-B `reproduces_exactly`;
    * tripwires `verified_armed` and `verified_fires` in control mode and in target mode.
  * `admitted_pairs`: 37, equal to the guard's set; `blocks_planned`: 11.
  * Per block: RLR record status; pointwise status, admitted rungs and alarm fields; the supply F2 status EQUAL.
  * The Stage-2 gates: C5, G-R4(N5), C6 (pieces checked), G-R3b and G-R3b_blocks, the G-T2 exact side, dominance,
    and the F2 bracket P_lo ≤ P_B.
  * Every job's `cpu_cap` has effective equal to declared.
  * The evaluation wall is below EVAL_CAP.
* **E5. Rung exceptions.** For every `RUNG_EXCEPTION`, the execution review reads the recorded error and confirms it
  was raised inside a pinned certifier. A guard refusal, import error, MemoryError or OSError is an execution failure
  (INDETERMINATE by design), never a silently dropped rung.
* **E6. The host record (review r3 E3/E4).** The execution review reports:
  * the sealed host assessment: status, reasons, samples, largest spacing, sleep gap, `thermal_level_max`,
    ThermalEvent entries and load maximum;
  * `seal_preconditions.host_power`;
  * `environment.caffeinate_pid`, or a disclosure if it is absent;
  * `environment.host_at_start`.

  It discloses any sleep.
* **E7. After the marker.**
  * Never `execute` again; recovery goes through `seal-only` only.
  * Nobody checks out the grant commit to call Stage-1 internals or to arm the guard.
  * Lost result information is never recomputed without a new independent governance process.
* **E8. The adjudication.**
  * It applies protocol §8 verbatim: strict Γ_dec < 0 in exact rationals; Γ_dec = 0 is not closed.
  * Closure is not adoption, not a floor-r2 change, not r6, and not K5 or P5Y closure.
  * Neither it nor any handover places any of the following next to a cell-308 quantity: a decoy value, a
    validation-drift value (including the QC04 ladder records at 3 and 11/10), or a qualification value.

## NOTES

* **N1. Load and thermal during the official run** (§7(d)). The start load was 5.72, not "near idle", and the thermal
  level was 1-2 in the heavy window. Both are non-gating and could only lengthen the measured runtimes; the runtimes
  match r1's.
* **N2. C7(a) "C-B on 308"** is verified by code identity with the 305 rehearsal, not by a run (§3).
* **N3. Freeze-before-read evidence for F2 and F3** is ledger process evidence, not git facts (§5).
* **N4. Validation drifts.** 11/10 and 27/10 bracket the band, and 27/10 lies nearer the band than decoy 316.
  They are disclosed A0 validation drifts, not C7(b) decoys (§11).
* **N5. The stale label** in `config/QUALIFICATION_CASES.json` (N-a).
* **N6. The r3 authorization** exists only as a paraphrase (N-b).
* **N7. Q12's margins are thin, but the execution's are not.** Q12's own thresholds passed with about 6 % headroom on
  RLR 8 (2 × 4093.1 s against 8700 s) and about 9 % on the projection (17 545.8 s against 19 200 s). The execution's
  own limits leave more room: a per-job CPU cap at least 2.1× the largest observed wall, and EVAL_CAP 1.64× the
  projection.
* **N8. `--heavy` was not run.**
  * The committed heavy records are bound by sha256 into the official report, which is itself in the qualification
    commit.
  * Review mode re-verifies them, including their host provenance from the raw readings.
  * QC04 already establishes determinism.
  * A recomputation would add 4-5 h on a hot host, and nothing to Q12, which by rule reads the official runtimes.

## Verdict and reason

The science is as reviewed and correctly implemented (§1-§5):

* the criterion is the unchanged K5 criterion, strict and exact, with max(P_B, P_hi);
* nothing but route MB can run on the target, with tripwires proven armed;
* D5 is frozen as specified;
* the independent layers are compared exactly.

The official r3 qualification passed every case and gate, and it passed for the right reason (§6-§7):

* Q12's caps hold on runtimes whose host provenance is CLEAN and covering, re-assessed from the raw readings;
* the power log independently shows no sleep or battery;
* the wall clock tracked the raw clock;
* the 14 controls behave as declared;
* review mode fails on the r2 records as it must.

The r3 freeze satisfies D1 byte for byte (§7(a)). The exactly-once machinery and the grant chain are sound (§8). The
caps are unchanged and adequate (§9). The pins are complete and current (§10). The quarantine holds (§11). The order
of events is correct (§12).

No blocker was found. The notes are disclosures, not defects of the gates. The campaign may proceed to the grant under
G1-G5, and to exactly one execution under E1-E8.
