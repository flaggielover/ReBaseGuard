# Cell-308 successor MB-S r1: review of the complete pre-measurement implementation, T1 cc723527 to T4 d4734231 (reviewF8, brief 57)
IMPLEMENTATION_REJECTED

Reviewer `reviewF8`, fresh and independent of builders 3-7, the coordinator editorR3C1, ratifier2 and every earlier
reviewer. Brief 57 (`ledger/briefs/57_reviewF8_premeasurement_implementation.txt`, sha256 `9f4573bf…2e9d`, verified
before anything else). Object: successor branch `p5y-k5-cell308-mbs-r1`, commits on `216c465f`: T1 `cc723527`, T2
`555f4cbf`, T3 `78a172cfc8d94f05f23a027f8decf4f9150e4c96` (builder6), T4 `d4734231dd0282d882552aa55964ffc21b9b6b5a`
(builder7). The verdict was not predetermined.

**The rejection is narrow.** Six of the eight sections are MET. Two are NOT MET, each on bounded points that need no
owner decision:

* **Section 4, on one rule (finding F8-2) and two small points (F8-3, F8-4).** After a designated series that ended
  `STEP1_RERUN_REQUIRED`, a second invocation of the measurement tool is not refused: it measures the whole series
  again at the provisional cap, designates it when it is clean, and the derivation of that evidence is `OK`. That is a
  clean run curing an event run, which owner supplement 2 (sections 6 and 7), the ratifier (item 4) and the protocol's
  own designation rule (v) exclude. Shown by a planted probe; nothing was measured.
* **Section 8, on one point of state (finding F8-1), not caused by the builders' bytes.** The research ledger at
  `98bef6d6` holds one line of class `INCIDENT` by a listed agent (the coordinator's record of the battery incident,
  written 35 s after T4 was committed). The verifier's own `ledger_check` fails on it, so QC13-S cannot pass at an
  official qualification of these bytes. It fails closed; it must be resolved in the successor before the freeze.

Everything else was reproduced on the committed bytes of T4: 216 / 216 suite tests, the dev decoy suite 4 / 4, the full
matrix 297 / 297 killed by assertion, my own 54 mutants 47 killed by assertion (five coverage gaps and one equivalent
mutant: section 9). No operational number changed. 0 target evaluations.

## 0. Reviewer, exposure, method

* **Exposure (MBS-2).** I hold no MB r1 run observation from any file I opened. My starting context carried the host
  tool's memory index (MEMORY.md; not a source; I opened none of its files and use nothing from it). **It carries MB
  r1 material, qualitatively:** the outcome label of MB r1's one execution with "consumed once, never rerun" and the
  successor's pre-freeze status; a lesson line that lid-close sleep and fanless thermal slowdown inflate wall times
  (not attributed there to a named run); a successor-lessons line (packed-refs.lock, timing-dependent kills, positive
  evidence for liveness, that subagents see the index). No per-job, progress, CPU, memory, host or science figure of
  the consumed run and no clock time. **It also carries one-line summaries of other tail-cell campaigns (cells 306,
  307, 309), some with figures; none concerns cell 308's target; I repeat none and used none.** From allowed files I
  saw resource figures of MB r1's PRE-GRANT qualification decoys and pre-freeze decoy costs (the ratification's
  evidence Q; MB r1 protocol section 3.2) and the headings of MB r1 protocol sections 13 and 14 (that two official
  qualifications failed before r3): qualification material, not observations of the consumed run; none is used.
* **Not opened:** `reviews/REVIEW_EXECUTION_INTERRUPTION*`, `audit/EXECUTION_INTERRUPTION_*`,
  `reviews/REVIEW_SUCCESSOR_GOVERNANCE_308*`, `reviews/INCIDENT_INDEPENDENCE_REVIEW_MB308*` and `…_MBS308*` (T6
  included), `ledger/COORDINATOR_EXPOSURE_DISCLOSURE*`, `ledger/USER_TEXTS_SUCCESSOR_308.md`,
  `governance/SUCCESSOR_GOVERNANCE_308.md`, `history/`, anything under `p5y_k5_cell308_mb_r1/{review,adjudication,
  postexec,evidence}/`, BUILD_REPORT sections 6 and 9 (section boundaries were located by line number only), any other
  agent's scratchpad, anything under `/Users/suzhe/.claude/`, `ledger/TAIL_FIGURE_PATTERNS.json` (used only through
  the scanner and the verifier, counts only). No `git log` on MB r1's branch; no commit subject of 21e99cf0 /
  afa93072 (hashes, author and date fields only). Names of MBS-2 files appeared in directory listings, in the
  configuration and in MB r1's verifier source; none was opened, by me or by a program on my behalf.
* **Read.** Brief 57; the three owner records in full and their provenance file (digests re-computed from the files
  and from the git blobs at 5c2394ba, 8fc2b038, 74f386a5: equal to the provenance table); the overnight directive,
  sections 2, 5, 8 (one page, for section 5 below), 9-11, 16; the ratification and ratifier2's readings in full;
  reviewQ6's rejection in full; the sequencing and the conformance reviews in full; briefs 54, 54-A, 54-B, 56, 56-A and
  the sent notes; both QC13-S record checks; BUILD_REPORT sections 17 and 18 in full; the protocol draft sections 1, 8,
  8.1-8.3, 9-11.3; in full: `code/mbs308_rrules.py`, `mbs308_derive.py`, `mbs308_measure.py`, `mbs308_qualify.py`,
  `tests/test_mbs308_cases.py`, `tests/test_mbs308_decoy.py`, `tests/mbs308_testlib.py`; the diffs `555f4cbf..T4` of the
  driver, state, manifest, repin, scratch, configuration and the state / child tests in full, and `T3..T4` of the
  driver, verifier, measurement tool and protocol on their own; the other test diffs by test, docstring and mutant
  definition; MB r1's frozen `code/mb308_qualify.py` (function by function against the carried code) and protocol
  section 3.2; the research ledger line of 2026-10-02T03:27:10Z (finding F8-1).
* **Method.** Committed bytes only: my own `git clone --bare --no-local` base store (made 03:30Z, holding T4 and
  research `98bef6d6`), a `--shared` checkout of T4 in my scratch, `git archive` trees of 216c465f, T2 and T3 for
  comparison. Nothing was run or edited in the successor worktree. No git write in any real repository, no real ref,
  no freeze manifest, marker, grant, pending result or seal, no official qualification, no designated measurement, no
  full-length decoy, no apply step outside the suites' own sandboxes, no system setting changed. The measurement tool
  was exercised only through the suites' recorders and synthetic payload.

### Re-run on the committed bytes of T4 (host on AC before and after every run; power log: no battery entry and no Sleep / Wake / DarkWake entry in my window; 97-105 GiB free)

| run | result | wall |
|---|---|---|
| `tests/test_mbs308_static.py` | 10 / 10 PASS | 5 s |
| `tests/test_mbs308_launch.py` (synthetic payload; no job or plist left) | 13 / 13 PASS | 16 s |
| `tests/test_mbs308_qualify.py` | 29 / 29 PASS | 29 s |
| `tests/test_mbs308_cases.py` | 28 / 28 PASS | 161 s |
| `tests/test_mbs308_disk.py` | 30 / 30 PASS | 212 s |
| `tests/test_mbs308_state.py` | 56 / 56 PASS | 465 s |
| `tests/test_mbs308_crash.py` | 50 / 50 PASS | 819 s |
| `tests/test_mbs308_decoy.py`, all four (decoy 297 block 0, dev ladder; NONTARGET_DRIFT_VALIDATION) | 4 / 4 PASS | 1011 s |
| `tests/test_mbs308_mutants.py`, full matrix, one run | **297 / 297 KILLED, every one by its target's own assertion** (test failed, exit 1, result verified, no `error` field: each of the 297 entries read); unmutated 134 / 134 targets PASS, no `error` field; 432 disk checks pass against 7 GiB; 431 phases cleaned, 175 sandboxes deleted (125.4 GiB in total); no survivor, none not run, no timeout; M33 killed by its deterministic run (165 s); peak scratch 1.496 GiB | 5508 s |
| my own mutants through the namespace's `run_matrix` | 54 mutants on 23 targets: **47 KILLED by assertion**, 7 SURVIVED (YF09, YG02, YG03, YG05, YS02 on two targets: coverage gaps G8-1 to G8-5; YF31: an equivalent mutant); the 23 unmutated targets PASS; peak scratch 0.907 GiB | 1231 s |
| negative controls for the repairs that live in `tests/` and `config/` (a throw-away checkout; the pre-repair state planted) | N1 (R1's tokens), N2a / N2b (the library's borrower record), N3 (the runner's per-phase check): each test FAILS by assertion, no `error` field | < 2 min |

No suite result carries an `error` field. The dev decoy suite: resume equivalence (2 served, 2 computed, 643 + 883
leaves equal), MBR1_REPRO tiny (192 + 43 leaves equal to MB r1's committed QC02 block-0 records), QS-RESUME-DECOY dev
(n 4, k 2, signal 9, 1548 certified leaves equal), the science cases' dev forms (every `dev_checks_ok` true, every
`pass` false); host CLEAN in every record. Its sampler record: set interval 0.25 s, 562 readings, 0 failed, largest
observed spacing 0.272 s. The only science any of my runs computed lies on decoy cover cell 297, block 0 (the dev
decoy; QC04's serial child and ladder pair at that block's own pointwise drift, which lies below the band; QC08's
Monte Carlo at the same drift).

## 1. The 82d59cc2 repairs (T4): MET

Each repair is made as the rejection asks, has a test that fails without it, and has a mutant killed by assertion (or,
where the repair lives in `tests/` or `config/`, which the runner does not mutate, a negative control that I repeated).
"Mine" are my own mutants (section 0); every one named here was killed by its target's assertion unless said.

| item | the repair, as I found it | test | builder's mutants | mine |
|---|---|---|---|---|
| R1 (F-1) | configuration r5: GOVERNANCE_ACCEPTED and ROUTE_ACCEPTED expect `DELTA_ACCEPTED`, ids, commits and paths kept, a `note` each | `qualify::t_qc13s_delta_review_tokens` | none (configuration) | N1 fails by assertion; `check_record` on the real ROUTE record: OK (the governance record: the coordinator's T4 check) |
| R2 (F-2, G-3) | a borrower register inside each base store; a store is deleted only with a register, every record valid, FINISHED and its owner positively dead, and no kept or recorded clone still borrowing; checked again before the deletion; the rule stated exactly in protocol 8.2, with its limit | `disk::t_base_store_borrowed_in_root_kept`, `…_cross_root_kept`, `t_borrower_records_and_library` | MD28-MD34 | in-root YF01; cross-root YF02-YF08, YF10; N2a, N2b; YF09 survives (G8-1) |
| R3 (F-3) | each deletion's record is written and fsync'd before the deletion; an unwritable log stops the pass (`DELETIONS_LOG_UNWRITABLE`) with the partial report | `disk::t_cleanup_records_before_deleting` | MD35 | YF20 (the log through a symlink), YF21 (the refusal swallowed), YF22 (delete first) |
| R4 (G-4) | a reading that falls after the start: the verifier's per-phase gate, the runner, and (follow-up) the science-phase gate | `disk::t_verifier_phase_gate_reading_falls`, `t_mutant_runner_reading_falls`, `t_verifier_science_gate_reading_falls`, `t_planted_reading_from_a_file` | MD37-MD39, MD41-MD43 | N3 |
| R5 (F-5) | a case naming no gate fails `config_consistency` and the aggregate by itself; `gates: null` no longer raises | `qualify::t_case_without_gate_not_ignored` | MQ37, MQ38 | YA02; my probe |
| R6 (ruling (a)) | `busy_processes` returns None on a failed `ps` or an output without a process row and `host_exclusive` is then false; a pidfile whose recorded process is not positively dead reads UNKNOWN and `no_other_campaign_job` refuses | `state::t_start_gates_fail_closed_on_no_reading` | M67-M71 (M43 re-expressed) | YF30, YF32-YF35; YF36 (the host report's reading of the same); YF31 is an equivalent mutant |
| R7 (F-7, note (e)) | an unreadable reading is UNKNOWN, never RECORDED; READY needs a positive reading; the report is embedded in the official record, the rule-input record and the designated evidence, and 8.1 names where the operator's actions are recorded | `disk::t_host_report_unreadable_never_ready`; `cases::t_host_report_structure_check`, `t_records_without_the_host_report_fail`, `t_official_run_embeds_the_host_report` | MQ39-MQ42, MB110-MB118 | YF36 |
| F-4 | the science-glue set is the committed header's carried list together with the working driver's; decided before `--classes` is read | `disk::t_repin_science_glue_refused` | MR05, MR06 | YP01 |
| G-1 | an empty `ps -o command=` reading is a failed reading | `launch::t_identity_command_empty_reading_unknown` | M72 | - |
| G-2 | the ladder and D of the decoy record | `state::t_decoy_record_ladder_and_driver_peak` | MM04, MM05 | YM01, YM02 |
| G-5 | re-verification before the deletion | `disk::t_cleanup_reverifies_before_deleting` | MD36 | YD01 |
| G-6 | the repository volume | `disk::t_verifier_checks_repository_volume` | MD40 | - |
| G-7 | `lock_read` never follows a symlink | `state::t_lock_read_never_follows_symlink` | M73 | - |
| G-8 | Q8-S and a commit-pin mismatch | `qualify::t_q8_commit_pin_mismatch` | MQ43 | - |
| G-9 | a raw-text-only match | `qualify::t_qc12s_raw_text_only_match` | MQ44 | YQ01 |
| G-10 | D, READING-2, READING-3, the step-5 sum | `qualify::t_rmem_formula_details` | MQ45-MQ48 | - |
| G-11 | PLATFORM_PINS after a failed reading; a science-glue hunk | `disk::t_repin_platform_failed_reading_refused`; F-4's | MR07, MR06 | YP01 |

* **Nothing else changed by T4, and no number.** T4 modifies 18 files, all in the namespace. In the driver exactly two
  places change: `busy_processes` / `host_preflight` (R6) and the place where D is read (below). No helper changed
  (the four pins are those of T3). The verifier's changes are R5, R7 with the embedding, and the leak scan's decoded
  pass; the measurement and derivation modules gain only the host-report embedding; the re-pin module F-4; the
  scratch module R2, R3 and the `file:` form. No module-level or class-level number differs between T3 and T4 (AST).
* **The two changes outside 82d59cc2** (D read last; QC12-S's decoded scan) are ruled in section 4: both accepted.
* **The `file:` reading facility: accepted.** It lives in the gate's module and is read from an environment variable
  at every probe, in production code; but a planted reading enters only through `min(real, planted)` or as a failed
  probe (`code/mbs308_scratch.py:140-172`), so it can only make a run refuse, never pass; the check records
  `planted: true`; the driver does not use the module and refuses any `MBS308_TEST*` variable.
* **The borrower register: accepted, with its stated limit.** Its costs fall on the safe side (a store without a
  register, or with a killed process's ACTIVE record, is never deleted by the tool). Its limit is the one 8.2 states:
  a clone made by something that writes no record, outside the cleaned root, protects the store only while the store
  has no register. My own checkout was such a clone; nothing of mine cleaned the root that holds its store.
* **The INVALID pidfile:** ruled in section 7 (accepted as it is).

## 2. Decision-dependent cases (T3 Part A): MET

* **MBS-6 (i).** Protocol section 10 carries the owner's words: an INDETERMINATE-class outcome of MB-S is final for
  route MB on cell 308, and no further route-MB cell-308 evaluation is authorized after it; the earlier "further
  successor" wording is gone; the reach of "do not reopen the changed-science branch" is stated with owner supplement
  1, section 9. The outcome table says the same. Checked against owner decisions section 2 and by
  `cases::t_protocol_owner_decisions_text`.
* **The carried cases match MB r1's frozen implementation.** MB r1's verifier (`code/mb308_qualify.py`; its worktree
  bytes equal the blobs at freeze r3 `c46434a3` and at 21e99cf0) was compared function by function with the carried
  code: `_decoy_jobs`, `_failing_job_keys`, `_leaves` identical; `lpt_makespan`, `_sysctl_text`, `_strip_timing`,
  `_compare`, `qc04_eval` differ in names and docstrings only; `_host_verdict`, `_synthetic_host`, `_synthetic_decoy`,
  `_q12_core`, `q12_caps`, `q12_controls`, the four children, `_serial_view`, `_ladder_view`, `_planted`, `qc02_eval`,
  `q1_theory` differ exactly as V1-V16 say. The constants `Q12_KEYS`, `Q12_BLOCKS`, `LADDER_DET_DRIFTS`,
  `TIMING_KEYS`, the pre-grant classes, the pattern pin, the theorem pin, the log fixture and the sha256 of the Monte
  Carlo and E4 pins are MB r1's. MB r1's four qualification test modules are not copied: they are executed from MB
  r1's committed bytes (sha256 and blob at 21e99cf0, checked at HEAD), the guard test bound to the successor's guard.
  The gate map keeps MB r1's memberships and adds some (QC02 also in Q2, Q7, Q12).
* **The deviations, each ruled.** V1 (launchd jobs), V2 (decoy 316 at WORKERS 5), V4 (the frozen cap and poll), V5
  (QC02 / QC03 also require the official configuration), V8 (three more Q12 controls), V15 (the three new cases):
  accepted, each required by R-MEM step 1, RC6 or owner supplement 1 section 3, and each makes a case stricter. V6
  (caps read from the driver's text), V9 (carried test modules executed from MB r1's pinned bytes), V10 (Q1 on MB r1's
  copy, also at HEAD), V11 (a local publication projection, identical to the driver's `jsonable` on JSON data), V13
  (MB r1's QC09 arming and QC10 flows replaced by QC09-S, QS-STATE, QS-CRASH): accepted, no criterion changes. V7 (no
  `eval_cap_required_s`): accepted and required by owner decisions section 4. V12 (dev forms) and V14 (science executes
  only in the qualified worktree): accepted; V14 is a safety interlock and the reason no test can launch the real
  driver's full decoys. V16: ruled in section 4. **V3, accepted, stated plainly:** the official decoys run one at a
  time, alone, before every other heavy phase, whereas MB r1's official run measured its walls with decoy 297, decoy
  316 (one worker), the serial child, both ladder children and E4 running together. R-MEM step 1 fixes WORKERS 5 for
  each official decoy, and two such decoys together are not that configuration; MB r1's own caps were derived
  (protocol 3.2) from decoys measured alone at 5 workers. So Q12's walls are now measured in the configuration of the
  execution and of the cap rule, not under MB r1's extra load: the thresholds (1.5 x the projection, 2 x per job) are
  unchanged, the margin MB r1's concurrency happened to add is not there. No accepted text prescribes that
  concurrency. One deviation is not in the list and is stricter: QC03 also requires at least three blocks in the
  record (`code/mbs308_qualify.py:2379`; MB r1's `all()` over the first three passed on fewer).
* **Q12 is a genuine pass / fail of the fixed caps.** `_q12_core` compares `EVAL_CAP_S >= ceil(1.5 x projection)` and
  every per-job cap `>= 2 x` the official maximum wall, fails closed on timing provenance and on the run
  configuration, and records no required, candidate or proposed cap (`cases::t_q12_never_states_a_candidate_cap`;
  the projection and the official maxima are recorded, as in MB r1). The fourteen carried controls and the three new
  ones run through the same decision function; the count is asserted (14 + 3).
* **The driver carries exactly the owner's section-4 values.** `section4_values` reads them from the driver's text
  (EVAL_CAP_S 28 800, one `AwakeCap(EVAL_CAP_S)` per attempt in `after_marker`, CLOCK_UPTIME_RAW and no other clock;
  RLR 1800 / 4200 / 8700; C2b 1800 / 1800 / 2700; every C1b and VER cap 1800; PRE_CAP_S 1800; WORKERS 5); the test
  checks the configuration's transcription against the owner record's own lines and nine planted mismatches. I read
  the constants in the driver as well: the same.
* **No vacuous pass.** My probe on the committed configuration: 28 cases, 28 BUILT, none pending, every case in a
  known gate, `config_consistency` passes; the aggregate passes with every case passing and fails for a missing, a
  non-boolean, a string or a null `pass`, a case that did not run, an unknown case, a case with `gates: []`, and in dev
  mode always. A case carrying a fail-closed status fails the qualification even with `pass` true.
* **QC01's cell-305 rehearsal is not runnable by any test.** The word `rehearse` occurs in no test invocation; the only
  caller of `run_qc01` is `science_phase`, behind `executes` (official / review mode AND the driver's own
  `check_identity`); the two tests that plant "this is the qualified worktree" replace `run_qc01` by a recorder or a
  refuser in a child process; dev mode never runs it; the one official invocation in the suites refuses on its
  preconditions in a sparse sandbox.

## 3. Section 11.2 option (a): MET

* **The measurement tool** (`code/mbs308_measure.py`). The official configuration: the same `run_decoy` the verifier
  uses for QC02 / QC03, decoy 297 every block and 316 blocks 0-2 from the configuration's plan, the launcher's own
  `launch`, the frozen ladder, WORKERS 5, one run at a time, the driver's then-current cap and poll (3 GiB, 2 s: step
  1). It records every rule input: each job's `ru_maxrss`, the watchdog's events and peak, D, the sampler record with
  its largest observed spacing, the run configuration, each run's host provenance, ten readings with free memory,
  wired pages, page size, power and every usable process with its executable path, `hw.memsize`, the hosting app with
  its ancestor chain, the commit, the driver sha256, the platform readings, the boot UUID and the embedded host
  report. Refusals before anything runs: not the qualified worktree or branch, tree not the committed bytes, a
  campaign ref, battery, thermal level not 0, memory pressure, low-power mode, platform differing from the pins, sleep
  channels unavailable, short disk, evidence already designated. Invalid evidence (never written into the
  repository): a reading not on AC; a run whose provenance is not CLEAN (K / S / L, battery, coverage) or with a
  ThermalEvent entry; a host that is not prepared (no decoy launched, no threshold raised); a run outside the official
  configuration; an invalid sampler record; a failed decoy; a watchdog event (`STEP1_RERUN_REQUIRED`, the next decoy
  not launched). A planted input without `dev` refuses; the dev form is never designated.
* **The derivation tool** (`code/mbs308_derive.py`) calls the four rule functions and nothing else decides: every
  status and value is the function's. The rule text in protocol section 8 is, whitespace aside, the ratification's
  "Written rules" at 3c2a7854 (compared by program at T2 and at T4); no rule number changed between T2 and T4 (AST).
  All five outputs are produced or all are null. The canonical forms are ratifier2's item 6 (`form_reasons`):
  MEM_CAP_BYTES and FREE_MEM_MIN_BYTES integers, multiples of 256 MiB, at least 1 GiB and 2 GiB; MEM_POLL_S "2" or
  "1/2"; EXCL_CPU_PCT one of 25, 35, 40, 45, 50; EXCL_ALLOW sorted distinct basenames.
* **The apply step** (`code/mbs308_repin.py apply`) is dry-run by default; it refuses a derivation that is not
  designated, not `OK`, carries a stop status or a failing check, is not in canonical form, is not reproduced from the
  evidence file, or belongs to other driver bytes; it rewrites exactly the value expressions of the five constants
  (every other top-level statement compared byte for byte, the result read back exactly), the protocol's table between
  its markers, and regenerates DRIVER_DIFF.md with the validated generator. Three files change, the third a generated
  artifact: stated so that "nothing but the five constants and the table" is read correctly.
* **R_RULES_OFFICIAL.** The official decoys are launched with no cap or poll argument, so they run with the frozen
  driver's constants; a run made with another cap or poll is an invalid input. B comes from the official records and
  the qualification's own ten readings through the same functions, with the 39 names as the base (never the frozen
  list). The pass condition is `B == A == driver` for each output, integers and the exact rational compared exactly,
  EXCL_ALLOW as sets of exact strings with no duplicates, every built-in check holding for A and for B, the committed
  derivation equal to its recomputation, the frozen driver text equal to the measured driver with the five outputs
  applied. **I searched the code for a tolerance, a subset, union, intersection or sticky list:** the only set
  operations are the rule's own union (`mbs308_rrules.py:504`), the reported differences of `compare`, and the
  generator's glue set; no `abs`, `isclose` or relative bound occurs in the rule, derivation, comparison or apply
  code. My probe: a superset, a subset, a name differing in case or by a trailing blank, one byte of MEM_CAP, a float
  in place of the integer or of the rational text each fail; the same set in another order passes.
* **One freeze; no constant after it; no target information.** The constants live in the driver's text; the manifest
  binds every namespace file, Q8-S compares, the grant binds the driver sha256 and the manifest, and R_RULES_OFFICIAL
  fails on any driver change beyond the five outputs. The measurement and derivation code reads no target record and
  copies no certified decoy value. That there is only one freeze COMMIT is a fact of history, checkable only after it.
* **Owner supplement 1, section 4, point by point.**

| point | checked now | only on the evidence |
|---|---|---|
| target-free | decoy cells 297 / 316 only, the guard refuses the band, the tool never imports the driver | the cells and `target_evaluations` of the actual record |
| prospective | preflight needs the committed tree and no campaign ref; the evidence names its commit | that evidence, derivation, apply and freeze are committed in that order |
| the intended official configuration | the code path, ladder, workers, launcher, one at a time; the two series differ by construction in cap and poll only (ratifier2, item 5) | each run's recorded configuration |
| all rule inputs recorded | yes (list above) | their presence in the record |
| peak RSS and the <= 0.5 s sampler | D, per-job peaks, watchdog peak, the sampler record with `max_spacing_ns` | the same |
| rules applied mechanically | derivation = rule functions; apply refuses anything not reproduced | the committed derivation equals its recomputation |
| all five outputs | yes | - |
| canonicalization unambiguous | `form_reasons`; MEM_POLL_S only 2 or 1/2 | - |
| no new tolerance | none found (search above) | - |
| qualification uses the actual frozen values | no measurement configuration exists; cap / poll checked against the frozen driver | the official records |
| qualification re-measures independently | its own readings and decoys; A is not an input of B | the official records |
| only one freeze | the tooling writes one manifest and binds it | the history |
| no operational constant after the freeze | Q8-S, the grant, R_RULES_OFFICIAL | the frozen and granted bytes |
| no cell-308 target information | no target read in the tools; QC12-S scans the evidence | the leak scan of the actual records |

Two points belong here although they are ruled in section 4: the hosting app of the two series is recorded and not
compared (F8-4), and the tool measures again after a watchdog series (F8-2).

## 4. Ratifier2's readings and owner supplement 2: NOT MET (F8-2; F8-3 and F8-4 with it)

Satisfied:

* **Observed spacing.** `sampler_reasons` (`code/mbs308_rrules.py:125`) requires a set interval of at most 0.5 s AND a
  stated largest observed spacing of at most 0.5 s (exactly 0.5 s is within; the integer `max_spacing_ns`, rounded
  up, is what is compared); otherwise the record is an invalid step-6 input: no g, no MEM_POLL_S, R-MEM not OK. The
  same function judges each run of either series. Mutants of the builder and mine (the boundary, the smallest instead
  of the largest spacing) are killed.
* **The configured interval, 0.25 s: accepted.** It implements the accepted requirement without altering the rule.
  The rule's sampler is "a <= 0.5 s qualification sampler"; a 0.25 s sampler is one. A set interval of 0.5 s cannot
  meet the corrected reading on a fixed-rate schedule (every spacing reported at 0.5 s exceeded it), so a shorter one
  is needed, and the owner allowed it (supplement 2, section 5). The value is one class constant of a pinned helper
  (`code/mbs308_state.py:1154`), so it is identical in both series and frozen with the bytes, as ratifier2 requires;
  the apply step cannot touch it. It was chosen on dev and synthetic evidence only. **g does depend on it** (a shorter
  interval sees a steeper rise), and I state the direction without predicting anything: against a slower admissible
  sampler it can only raise g, which can only make step 6's re-check harder, never easier. That dependence is a
  property of the rule's own definition of g (any admissible sampler gives its own g), not a change of the rule. My
  dev record at 0.25 s: 562 readings, none failed, largest spacing 0.272 s. No owner authority is needed.
* **First-observation semantics unchanged.** `RssSampler`'s sampling code is byte-identical between T2 and T4; only
  the interval constant, the docstring and the `max_spacing_ns` field of `stop()` changed.
* **Event runs inside one series.** An event run is never an input; it is cured only by a valid re-run of it at the
  doubled provisional cap; a clean duplicate of its cell cures nothing; no rule is applied until then (`r_mem`,
  `code/mbs308_rrules.py:275-315`); the step-5 bound of the re-run uses the valid runs' P and D and is reported as the
  owner's open point when no valid run exists. No tool can mark a run as a re-run and no cap-override facility exists
  in the driver, the tools or the CLI (searched), so in practice every event stops the derivation.
* **The three statuses, each reachable and each with mutants.**
  `QUALIFICATION_MEMORY_WATCHDOG_UNDER_FROZEN_CAP`: `r_mem(official=True)`, QC02 / QC03 through `decoy_failure`,
  R_RULES_OFFICIAL, lifted by the aggregate (a case carrying it can never pass); no re-run exists in the official
  series (a run claiming to be one is invalid), no doubled cap, no cure by a duplicate; after an event the later
  official decoys and MB r1's children are not launched. `MEM_POLL_S_NONCANONICAL_BRANCH`: the derivation stops with
  every output null, nothing is rounded (`poll["MEM_POLL_S"]` is null; the exact expression is reported under a key
  that says it is not an output), the apply step can write only `2.0` or `0.5`, the official case fails closed with B's
  MEM_POLL_S null. `STEP1_RERUN_REQUIRED`: the measurement stops after the event run, launches nothing more and
  reports the one re-run cap and its bound. **Reached by real events:** the first and the third by a real watchdog
  kill in `main()`'s real decoy branch (`state::t_decoy_failure_record_on_watchdog_event`, synthetic evaluator); the
  second on my own real dev decoy record passed through the adapters and the rule function with only its
  run-configuration fields planted (a dev fact, no prediction for the official ladder).
* **V16, accepted.** `main()`'s decoy branch (`code/mbs308_driver.py:1848-1879`) records a decoy that raises
  (`decoy_failed`, no stage 1, the same lifecycle fields) and re-raises the same exception. It lies inside `if a.mode
  == "decoy"` only; `decoy()` and every carried function are unchanged (RC1 / MBS-9 pass; the DRIVER_DIFF hunk is
  `main`, LIFECYCLE); `execute`, `resume`, `recover` and the seal are other branches. A band cell is still refused
  before any work; its refusal would now leave a record without any value. Without V16 no status could fire on a real
  event, as builder6 says.
* **builder6's own readings.** READING-11 (W_idle = the largest wired-down reading; feasibility only, conservative),
  READING-13 (a thermal event is a ThermalEvent power-log entry in the run; the level gates the start; unreadable
  fails closed; MB r1 r3's rule for Q12 kept), READING-14 (which processes a reading keeps; a process above the
  threshold that R-ALLOW cannot admit makes the series not prepared), READING-15 (a memory-watchdog event is a kill at
  the cap; the release of an already-broken pool is a failed decoy, not an event; an unknown entry counts as an
  event): each accepted as a reading; none changes a number, and each fails closed. I read `_MemWatch`: a kill at the
  cap always leaves a cap entry, the broken-pool entries follow it. READING-12 (the hosting app is the bundle of the
  nearest ancestor inside an application bundle, never an argument): accepted, with F8-4. Exactly ten readings in both
  series (the rule's minimum, one constant): accepted.
* **builder7's two changes outside 82d59cc2.** (i) **D read last: accepted.** The rule says "the driver's own peak
  RSS in those runs (the qualification records ru_maxrss of RUSAGE_SELF)"; `ru_maxrss` is the maximum up to the moment
  it is read, so reading it before the provenance collection under-reads the run's peak. On my dev record D is 107
  MiB while the sampler's driver peak during the computation is 56 MiB. It enters only left-hand sides (step 5, the
  re-run bound) and R-FREE's sum: nothing is loosened. Its consequence for exact agreement is in section 6. (ii)
  **QC12-S's decoded scan: accepted**, with one limit (O8-1 in section 9).

Not satisfied:

* **F8-2 (blocking). A memory-watchdog event in a designated series is cured by measuring again.** The protocol's
  rule says "(v) A memory-watchdog event is not a re-measurement case" (`protocol/MBS308_PROTOCOL_DRAFT.md:813`), and
  owner supplement 2 says a separate clean run does not erase the event run and only the rule's one re-run cures it.
  The tools do not hold that across invocations. `designate` (`code/mbs308_measure.py:521-559`) refuses only when
  designated evidence already exists (line 533); earlier invalid series are read from the `--work` directory of the
  call (`prior_invalid`, lines 399-407) and only listed (lines 468, 507); `evidence_reasons` and `derivation`
  (`code/mbs308_derive.py:485-545`) never look at them. My probe (planted records, the measuring function a recorder,
  as in the suite's own test; nothing launched): a first series ends `STEP1_RERUN_REQUIRED` and is kept as
  `INVALID_001_…`; a second call with the same `--work` is not refused, measures, and a clean series is DESIGNATED
  (rc 0), listing the event series; its derivation is `OK`, `stop_before_freeze` false, no fail-closed status; with
  another `--work` the event series is not even listed. An interrupted invocation leaves no series record at all (the
  record is written only at the end, line 555), so it is not listed either. No test and no mutant covers the rule.
* **F8-3.** ratifier2's observation on step 3 (for the reviewer of R_RULES_OFFICIAL) was not taken up: a job whose
  recorded peak is 0, or negative, is a valid input (`code/mbs308_rrules.py:205-208` accepts any integer) and its
  (kind, rung) is silently left out of s (`:339-340`, `min(v) > 0`). My probe: such a run gives status `OK`, s = 1.
  The text provides no such exception; a peak that is not positive is not a measurement. A real worker cannot report
  it, so this is a fail-open on a malformed record only.
* **F8-4.** ratifier2's note to READING-4: the hosting app "must be the same in both series and is recorded". It is
  recorded and not compared: R_RULES_OFFICIAL takes the official record's own paths
  (`code/mbs308_qualify.py:2647`) and the evidence's own (`code/mbs308_derive.py:513`). My probe: an official series
  hosted by another application passes with `EXACT_AGREEMENT` when the five outputs agree.
* **O8-2 (to ride with the repair; it fails closed today).** The distinct status is raised for QC02, QC03 and
  R_RULES_OFFICIAL. QS-RESUME-DECOY's official form also runs decoys of cell 297 under the frozen MEM_CAP
  (`tests/mbs308_resume_decoy.py`, untouched since T2): a watchdog kill there fails the case as
  `UNINTERRUPTED_RUN_FAILED` / `RESUMED_RUN_FAILED`, without the status; and those decoys are still launched after an
  event in an official decoy (they cure nothing: the aggregate has already failed).

## 5. The designation-rule proposal: ACCEPTED_AS_DESIGNATION_RULE

The proposal (protocol 11.2, step 1, (i)-(vi)): the unit is the whole series of one invocation; an invalid series
designates nothing, is kept and is listed; a later invocation measures the whole series again, never one decoy into an
existing series and never a choice among runs; once a series is designated the tool refuses (`ALREADY_DESIGNATED`); a
memory-watchdog event is not a re-measurement case; no limit on invalid series.

**Ruling: ACCEPTED_AS_DESIGNATION_RULE, as written.** It does not need the owner, for these reasons.

* **Against the rule text.** The ratified rules say what a valid input is and give one re-run (after a watchdog
  event, at the doubled cap). They say nothing on which series is the designated one. The proposal changes no rule
  text and no number, never uses an invalid record, and adds no tolerance: a spacing above 0.5 s is not accepted, the
  series that holds it is discarded whole.
* **Against ratifier2 (item 2).** Whether a decoy with an invalid sampler record may be measured again "must be fixed
  before the runs are made" in the designation and pass this review, "the owner if it needs a new rule". It is fixed
  before the runs, in the protocol and in the tool. It needs no new R-rule: R-MEM is applied, unchanged, to one
  complete valid series. What it adds is a procedure for the measurement, which is where the ratifier placed it.
* **Against the owner's texts.** Supplement 1 asks for measurements "in the exact intended official configuration"
  on a prepared host: a series on battery, across a sleep, on an unprepared host or with an invalid sampler record is
  not that, and restoring the host and measuring again is how the owner treats host conditions elsewhere (decisions
  section 22 C). Supplement 2 forbids a cure of a watchdog event by another clean run (rule (v) says so), an invented
  re-run limit (rule (vi) sets none) and any tolerance (none). No selection among valid outcomes is possible: the
  validity reasons are fixed in the tool before any derivation runs, none of them reads a rule output, the first valid
  series is designated, and a designated series that then stops in the derivation (`MEM_POLL_S_NONCANONICAL_BRANCH`,
  step 5, attainability) cannot be replaced.

**What the ruling does not cover: the rule as IMPLEMENTED is not yet the rule accepted.** Rule (v) is not enforced
(F8-2), and "kept and listed" in (ii) holds only for an invocation that ends and only when the same `--work` is given
again. The acceptance is of the text; the tools must be brought to it (D-1 in section 9) before any designated run.
One consequence to be kept in view by whoever runs the series: after `STEP1_RERUN_REQUIRED` nothing may be measured
again by this rule; the campaign stops and reports, as owner supplement 2 (section 7) and the directive (section 9)
say.

## 6. builder6's B4 analysis: MET

For each of the five outputs builder6's statement of when exact agreement is well-defined is correct. I checked each
against the rule text only; I predict no outcome and propose no way around a stop.

* **MEM_CAP_BYTES.** Well-defined (integers). Its list of dependences is right: P is a maximum of measured peaks; at
  or below the 1 GiB floor both series give 1 GiB, above it both `k x P` must fall in the same 256 MiB step; k exceeds
  3 only when s exceeds 3/2; in the official series the frozen cap is the kill line. I add nothing.
* **MEM_POLL_S (the arithmetic, from the rule text).** With c = 0.1 x MEM_CAP and the re-checked value 2 s: the
  re-check holds iff 2 g <= c, i.e. g <= c / 2 (output 2); otherwise the output is max(0.5, c / g), which is 0.5
  iff g >= 2c; so the unrounded-quotient branch is exactly c / 2 < g < 2c. With the re-checked value 0.5 s (a frozen
  1/2): the re-check holds iff g <= 2c and otherwise c / g < 0.5 gives the clip, so B is 1/2 for every g. With a
  frozen 2: B is 2 iff g <= c / 2, the official case fails closed for c / 2 < g < 2c, and B is 1/2 (not A) for
  g >= 2c. This is builder6's statement, boundary cases included (g = c / 2 is case (i), g = 2c is the clip); my probe
  of the rule function at c / 2, just above it, just below 2c, at 2c and beyond gives the same. At the 1 GiB floor
  the band's ends are 51.2 and 204.8 MiB per second, as stated.
* **FREE_MEM_MIN_BYTES.** Well-defined (integers); it inherits MEM_CAP's dependences and adds 4 x P and D with the
  same 256 MiB steps above the 2 GiB floor; attainability must hold in each series. **One property to add, which
  postdates the analysis:** since builder7's change D is the driver's peak including its end-of-run power-log read
  (107 MiB against 56 MiB on my dev record), so D now also varies with the size of the host's power log at the time
  of each series. It matters only above the floor and near a step, like every other term.
* **EXCL_CPU_PCT.** Well-defined (25, 35, 40, 45 or 50). The bins are right: a maximum in (25, 28] gives 35, in
  (28, 32] gives 40, in (32, 36] gives 45, above 36 gives 50; "exceeds" is strict.
* **(a) EXCL_ALLOW: exact set equality is mechanically well-defined under the accepted text. I find no genuine
  ambiguity and state no question for the owner.** Each series gives one set: the 39 names; the H3 names whose
  ratified reading exceeds that series' EXCL_CPU_PCT (all four at 25; the two with readings 70.3 and 52.2 at every
  higher value); and the basenames, as exact strings, of the processes of that series' own readings that meet (a)
  and (b) and no never-added class. Equality of two such sets is ordinary set equality; the comparison needs nothing
  the rule does not give. What the text does not fix is two inputs, fixed by the tools and identical in both series:
  exactly ten readings (the rule's minimum) and the identification of the hosting app (READING-12); both are choices
  of the kind ratifier2 left to a builder under review, and I accept them (the hosting app with F8-4). builder6's
  remark that an OS daemon busy in one series only breaks equality is a statement of consequence, correct, and already
  answered by the owner (supplement 2, section 8; directive, section 11): the comparison is implemented exactly and the
  measurements decide.

## 7. Grant binding and the final host preflight: MET

* **Three complete records, fixed order, exact bytes and digests.** `S1_OWNER_RECORDS` (`code/mbs308_driver.py:186`)
  names `original`, `supplement_1`, `supplement_2` by research path, commit, byte length and sha256. I re-computed
  all three from the ledger files and from the git blobs at 5c2394ba, 8fc2b038 and 74f386a5: 17291 / 18797 / 12941
  bytes and the three digests of `ledger/USER_OWNER_RECORDS_PROVENANCE.md`, equal to the driver's rows, the
  configuration's `owner_decisions.records`, QC13-S's three governance records and the table of protocol section 1.
  The manifest writer records them and refuses bytes git does not hold; Q8-S compares. The order is the directive's
  (sections 2 and 16).
* **`check_grant` refuses every planted deviation.** `check_s1_ruling` (`:889`) admits exactly the three keys of the
  field and the six keys of a record, re-hashes each complete text, compares each row with the driver's row in order,
  and checks the index digest. Besides the builder's 26 controls through `execute` (all refused in my run, the
  complete index accepted and sealed), I planted 62 of my own through the function compiled from the driver's text
  (the records read from my base store): in each record a byte changed and re-indexed, a trailing newline added, the
  last byte dropped, CR LF line ends, a Unicode re-normalisation, a half-length excerpt (re-indexed, and keeping the
  recorded digest), another path, an abbreviated commit, another record name; each record missing (re-indexed, and
  with the index of all three); every pairwise swap (of the entries, and of the texts under the labels in place); a
  fourth record (index of four; index of the first three; a new text); a duplicate appended; all three texts in one
  record; `records` as an object or a string; `bytes` as a float or a boolean; the text as a list; `reaffirms_c4` as 1,
  as a string, absent; the index digest in upper case or absent; an added key in the field or in a record; the field
  as a list or a string. **61 refused as GRANT_INVALID, none accepted.** One (a lone surrogate in a text) raises
  `UnicodeEncodeError` instead of the named refusal: before the marker, nothing consumed, never an acceptance (O8-3).
* **No paraphrase in any gate.** The gate compares bytes and digests; the refusal text names the requirement and
  quotes nothing of the rulings; no other key is admitted, so a paraphrase has no place in the field.
* **QC13-S names all three** (presence and sha256, on the research ref), and ratifier2's readings. My run of the
  verifier's `check_record` on the eight records whose files I may open: all OK (ROUTE_ACCEPTED with the corrected
  token, the M4 ledger line, the ratification, the liveness review, the three owner records, the readings); the six
  MBS-2 records resolve and lie on the ref and are OK by the coordinator's status-only check
  (`ledger/QC13S_RECORD_CHECK_T4.md`); IMPLEMENTATION_REVIEW_ACCEPTED is pending by design. QC13-S's LEDGER check is
  another matter: F8-1 in section 8.
* **Owner decisions section 14.** All seventeen items, in the record's order and wording, are mapped in
  `OWNER_SECTION14`, the host report and protocol 8.3; every gate or function named exists in the code (tested).
  Fifteen are gates or mechanisms; "required lid/sleep state" and "restart hazards controlled" are read-only recorded
  readings of `--host-report` with an operator line, because no accepted text makes them a gate (the conformance
  review listed exactly these two for the user). That meets the brief's criterion. One text point (T-2 in section 9):
  8.3 does not say when that report is taken before `execute` and where it is kept; for the qualification and the
  designated measurement it is embedded, for the execution it is not.
* **The gate on an INVALID pidfile: accepted as it is.** An invalid pidfile (unreadable as this user's regular file,
  not JSON, no identity) records no process, so there is no identity whose death could be shown or doubted. What
  excludes a second driver is not this gate: `execute` refuses on any campaign ref or journal, `resume` proceeds only
  when the journal's recorded process is positively dead (UNKNOWN is never DEAD) and holds the O_EXCL lock and the
  journal's compare-and-swap. Making the gate refuse on an invalid pidfile would add no protection and would turn a
  damaged secondary record into a state the frozen recovery machinery has no action for. The host report shows
  UNKNOWN for it, which is right.

## 8. Final-byte state at T4: NOT MET (one point of state: F8-1)

Verified on the committed bytes:

* **Pins.** Each of the four `HELPER_SHA256` values equals the sha256 of its file (`mbs308_repin.py helpers`: nothing
  stale). `PLATFORM_PINS` is text-identical to 216c465f's and equals this host's readings today (`platform`, dry run:
  no difference, nothing unreadable, nothing written).
* **Generated artifacts.** `mbs308_repin.py check` in my checkout: exit 0; the committed DRIVER_DIFF.md is reproduced
  from the committed driver and is not stale; 23 hunks, every class carried, no science-glue hunk. The configuration
  and the verifier agree (`config_consistency` passes: 28 cases, no pending case, no gate without a case, no case
  without a gate). The protocol's rule-output table equals the driver's five constants and says PROVISIONAL.
* **Nothing post-freeze in the tree or in history.** No `protocol/MBS308_FREEZE.json`, `evidence_prefreeze/`,
  `qualification/`, `authorization/`, `review/`, `evidence/`, `adjudication/` or `postexec/` path in the namespace at
  T4, and no commit on any ref ever touched one; no ref under `refs/p5y-k5-cell308-mbs-r1/` in the real repository.
  T3 and T4 touch only the namespace (T3: 4 files added, 17 modified; T4: 18 modified); BUILD_REPORT sections 1-17
  are untouched by T4 (insertions only) and sections 1-16 by T3.
* **Module-level and class-level constants, 216c465f to T4 (AST).** Driver: `HELPER_SHA256` changed (two helpers
  re-pinned); `S1_OWNER_RECORDS`, `S1_RECORD_KEYS`, `S1_RULING_KEYS` added; nothing else. Host: `PS_TZ`,
  `_ARGV_UNREADABLE` added (by T2; unchanged since). State: `RssSampler.INTERVAL_S` added at 0.5 (T2) and set to 0.25
  (T3: the one number a builder chose; ruled in section 4). Guard and launch: nothing. Between T2 and T4: no rule
  number of `mbs308_rrules.py` changed (names added: the three statuses, two commit references, a unit conversion, the
  broken-pool event name); the verifier's changed constants are case lists, required files and a test fixture; the
  scratch and re-pin modules gained names, no value changed. **T4 changed no number at all.** MEM_CAP_BYTES,
  MEM_POLL_S, FREE_MEM_MIN_BYTES, EXCL_CPU_PCT, EXCL_ALLOW, WORKERS, every cap, MIN_FREE_DISK, QUAL_MIN_FREE_BYTES,
  MAX_RESUMES and the deadline are as at 216c465f.
* **Mutants.** 297 declared, none removed since T2; five re-expressed because their fragment changed (M51 and MQ06
  at T3; M43, MM01 and MQ24 at T4; MM05 is new at T4), each with the same meaning and the same target: accepted.
* **Ledger agents.** The list holds every agent that built or reviewed these bytes (builders 2-7, reviewQ6, reviewF8,
  ratifier2, ratifierMBS, the coordinator's editor name, the qualification). The next builder and reviewer must be
  added when they exist.
* **The host incident (builder7's disclosure).** The power log agrees with it: the last AC entry before the interval
  is 01:55:22Z on 2026-10-02, the first battery entry 02:03:51Z, AC again from 02:26:52Z; no Sleep, Wake or DarkWake
  entry after 2026-10-01T10:57:33Z. builder7 discarded every matrix result written from 01:55:00Z and repeated those
  93 on AC; its suites ran before 00:47Z and after 02:27Z. builder6's final runs (ledgered from 16:54Z on 2026-10-01)
  lie in an interval in which every log entry is on AC (16:06:19Z to 01:55:22Z). One earlier battery entry, at
  16:05:53Z on 2026-10-01 (AC at the entries before and after it, 14:56:15Z and 16:06:19Z; charge 100 throughout), is
  disclosed by nobody; it falls in the pause of builder6's session, before any run it reports. I could not open
  builder7's kept reports (another scratchpad), so which of its results were kept rests on its statement. **It does
  not matter for the verdict: no result of mine relies on theirs.** Every suite and the whole matrix were run again by
  me, on AC, with no sleep (table in section 0). I find no evidence the build relies on that was produced on battery
  or during a sleep.

Not satisfied:

* **F8-1 (blocking before the freeze; not a defect of builder6's or builder7's bytes).** QC13-S checks that every
  research-ledger line of a listed agent has a pre-grant class (`code/mbs308_qualify.py:95-97`, `:1335-1357`,
  `PRE_GRANT_CLASSES`; the configuration's `ledger.agents`, line 116, lists `editorR3C1`). The research ledger
  committed at `98bef6d6` (the ref the case reads) holds, as line 418, one line by `editorR3C1` of class `INCIDENT`,
  written 2026-10-02T03:27:10Z: the record of the battery incident (0 target evaluations, no LEAK_FLAG). `INCIDENT` is
  not a pre-grant class. I ran the verifier's own `ledger_check` on the committed ledger, from my base store and from
  the real repository's ref: 115 lines of listed agents, `bad_line_numbers` [418], `pass` false. So QC13-S, and with
  it gates Q10 and Q11, cannot pass at an official qualification of these bytes; it fails closed. No test saw it: the
  suites plant their own ledger, and the coordinator's T4 check covers the records, not the ledger. The ledger is
  append-only and read by ref, so the remedy has to be in the successor (D-2 in section 9).

## 9. Bounded defects and their repairs

None needs an owner decision. Each repair needs a planted test that fails without it and a mutant killed by assertion.
The coordinator is kept out of implementation roles (T6 / M4), so the repairs are a non-holder builder's.

**Blocking**

| id | finding | where | repair |
|---|---|---|---|
| D-1 | F8-2: a designated series after a memory-watchdog event is measured again and designated; "kept and listed" depends on the `--work` argument and on the invocation ending | `code/mbs308_measure.py:399-407, 468, 507, 521-559`; `code/mbs308_derive.py:485-545`; `protocol/MBS308_PROTOCOL_DRAFT.md:804-815` | (a) `designate` refuses, before anything is measured, while an earlier series of this campaign had a memory-watchdog event (the texts provide one cure, at the doubled cap, and no facility for it exists: so it refuses and the campaign stops and reports); (b) the record of every series (started, invalid, designated) is kept at one place that no argument of the invocation chooses and is written when the series STARTS, so that an interrupted series and a series made with another `--work` are kept and listed too, and `ALREADY_DESIGNATED` no longer rests on a worktree file alone; (c) the derivation refuses evidence whose earlier series include an event series, so that R_RULES_OFFICIAL and the apply step inherit it; (d) protocol 11.2 step 1 says so |
| D-2 | F8-1: QC13-S's ledger check fails on the committed research ledger (line 418, `editorR3C1`, class `INCIDENT`) | `code/mbs308_qualify.py:95-97, 1335-1357`; configuration line 116 | the line cannot be removed (the ledger is append-only and read by ref), so the rule must say what it does with it: for instance a NAMED exception, bound to the exact line by its sha256 in the configuration and admitted only with 0 target evaluations, 0 proxies and no LEAK_FLAG, every other non-pre-grant line of a listed agent still failing; not a wholesale admission of the class. Whether this incident needs a review of its own before the freeze is for the authority of the incident conditions, which I may not read. Then the check re-run on the real ledger and recorded |

**Before the freeze, to ride with the repair**

| id | finding | where | repair |
|---|---|---|---|
| D-3 | F8-3: a job peak of 0 or below is a valid input and its (kind, rung) is silently left out of s | `code/mbs308_rrules.py:205-208, 339-340` | a job peak, the driver's peak and (when recorded) the watchdog's peak must be positive integers, else the run is an invalid input with a named reason; the `min(v) > 0` filter then has nothing to skip and goes |
| D-4 | F8-4: the hosting app of the two series is recorded, not compared | `code/mbs308_qualify.py:2647`; `code/mbs308_derive.py:513` | R_RULES_OFFICIAL requires the official series' hosting-app paths to equal the designated evidence's, exactly, and fails closed otherwise |
| D-5 | O8-2: no distinct status for a watchdog kill in QS-RESUME-DECOY's official decoys | `tests/mbs308_resume_decoy.py` (`run_case`); `code/mbs308_qualify.py:677-705` | the case reads the failed decoy's record (V16 writes it) and carries `QUALIFICATION_MEMORY_WATCHDOG_UNDER_FROZEN_CAP`, which the aggregate lifts; it already fails closed |

**Coverage gaps (my surviving mutants; the code is right in each case, by reading and by my probes)**

| id | mutant | no test fails when … |
|---|---|---|
| G8-1 | YF09 | a clone whose alternates file exists but cannot be read is taken not to borrow from the store |
| G8-2 | YG02 | a record of the grant's index carries another name, path or commit with the bytes and digest intact (my probe: the real code refuses each) |
| G8-3 | YG03 | a fourth record is appended with the index digest of the first three (the builder's fourth-record control re-indexes all four, so the digest check refuses it whatever the length check does; my probe: the real code refuses) |
| G8-4 | YG05 | `reaffirms_c4` is truthy but not `true` (only `false` is planted; my probe: 1 and "true" are refused) |
| G8-5 | YS02 (two targets) | step 6 gives a quotient between 0.5 s and 1 s as a canonical value: every planted control puts the quotient above 1 s (128/125), none near either end of the stop band. The derivation's form check would still refuse the value, but as `NOT_DERIVED`, without the distinct status |

YF31 survives as an equivalent mutant (a failed `ps` turned into an empty listing has no row and is still "no
reading").

**Observations (not blocking)**

* **O8-1 (the decoded scan's count arithmetic).** `tail_hits` returns `kept + max(0, n - full)`
  (`code/mbs308_qualify.py:1129`): a raw-text-only match and an escaped match inside a timing key cancel. My probe
  with a neutral planted pattern: a figure in a duplicated key (raw only) beside the same figure, JSON-escaped, in a
  timing key gives (0, 1): nothing counted. The campaign's writers produce neither a duplicated key nor an escaped
  digit, so this needs a hand-made file. Simplest: no exemption at all for a file whose raw and decoded counts differ.
* **O8-3.** A lone surrogate in a carried text makes `check_s1_ruling` raise `UnicodeEncodeError` instead of
  GRANT_INVALID (before the marker; nothing consumed; never accepted).
* **O8-4.** After a watchdog event in an official decoy the verifier still runs its remaining heavy phases; they can
  cure nothing (the aggregate has failed on the status).
* **Text points.** T-1: protocol 8.3 and `OWNER_SECTION14` still say of `no_other_campaign_job` "(a LIVE pidfile
  refuses)"; since R6 an UNKNOWN one refuses too (8.1 says it). T-2: 8.3 should say when the read-only host report is
  taken before `execute` and each `resume`, and where it is kept, since the two recorded-reading items of the owner's
  section 14 rest on it. T-3: section 1's order line still places "the user's explicit S1 ruling" after the
  qualification review, while the paragraph below it (and the record) has it given before the freeze and entering the
  grant afterwards; the conformance review noted the same.
* **READING-12's consequence.** A process of the agent's own tool chain that lies outside the application bundle is
  not "the hosting app": above the threshold in a reading it makes the series not prepared. That is the fail-closed
  side; it is said so that the series is started with the tool chain idle.

## 10. For the owner

**This review raises no question that needs the owner.** The designation rule is accepted as a designation rule
(section 5); exact agreement is well-defined for all five outputs and EXCL_ALLOW holds no ambiguity (section 6); every
defect found is bounded and repairable from accepted text (section 9).

Three facts, stated without a recommendation and asking nothing, so that they are known before the designated
measurement:

1. Under the accepted designation rule a series that is invalid for a reason other than a memory-watchdog event (a
   reading off AC, a sleep or a thermal event in a run, a host not prepared, a run outside the official
   configuration, a sampler record that is not valid, a failed decoy) is kept and listed, and the whole series may be
   measured again; the first valid series is the designated one; no limit is set. After a memory-watchdog event
   nothing is measured again: the campaign stops and reports.
2. builder6's analysis stands: exact agreement of the two series is defined for all five outputs and is decided by
   the measurements. Since builder7's change one more quantity varies between the series: D includes the driver's
   end-of-run power-log read.
3. Q12 now measures its runtimes with each official decoy alone on the host at 5 workers (the configuration of the
   execution and of MB r1's cap rule), not under the additional concurrent load of MB r1's official run; its
   thresholds are unchanged (section 2, V3).

## 11. What remains

**Before the designated measurements**

* D-1 to D-4 (and O8-2) repaired by a fresh non-holder builder, on top of T4; the rejection preserved; the affected
  suites and the whole matrix re-run on the final bytes; a fresh delta review of exactly those items. Sections 1, 2,
  3, 6 and 7 need no second review unless the repair touches them.
* The QC13-S record check re-run on the final bytes by a party allowed to let a program open the MBS-2 files,
  **including the verifier's `ledger_check` on the committed research ledger** (status only).
* Any re-pin (helpers, platform) before the series: afterwards the frozen driver must be the measured driver with
  exactly the five outputs applied. Today the pins equal the files and this host's readings.
* The decision brief and the MBS-10 reader check (owner supplement 2, section 12); the host prepared (on this
  unprepared host builder7's report read automatic OS installation and exclusivity USER_ACTION, thermal, memory
  pressure and free memory NOT_READY); the operator's ledger line for the run (protocol 8.1).
* A first real execution of the launchd decoy path. No real decoy has ever run under the launcher (builder6, 17.8
  item 1): the designated series would be its first execution. The tool's own dev form (`designate --dev`: decoy 297
  block 0, dev ladder, under launchd, in the qualified worktree, a DEV record under `--work`, never evidence) exists
  for that; whether to use it first is the coordinator's.

**Before the freeze**

* The designated evidence and its derivation committed (status `OK`, five outputs), the apply step through the tool
  (dry run, then `--write`), `repin check` clean, every suite and the matrix on the applied bytes.
* A dev run of QC12-S on the tree that holds the evidence. The scan covers `evidence_prefreeze/` with no exemption and
  the qualification records with the timing exemption only; through the verifier's own compiled patterns (counts
  only) I measured how often generic numeric texts match: 1 of the 1000 one-decimal texts from 0.0 to 99.9, none of
  10 000 two-decimal texts, of 3000 three-decimal texts, of 200 000 random integers, of 4536 UTC stamps. So a `ps`
  %cpu text of one particular value in a recorded reading would fail QC12-S (I did not print the value). In the
  designated evidence that is visible before the freeze; in the official record it would fail the qualification, as
  the rule says. Stated so that it does not come as a surprise.
* IMPLEMENTATION_REVIEW_ACCEPTED named in QC13-S (the accepting review's commit, path and line-2 token); the next
  builder and reviewer in the ledger agents; P_max and B re-measured on the final bytes (on T4, with the namespace's
  meter, I measured QS-DISK's peak at 2169 MiB and my base store at 460 MiB: the formula still gives 7 GiB).
* The final pre-freeze review (owner supplement 2, section 12), every S16 condition, then ONE freeze through
  `mbs308_manifest.py --freeze`.
* Text points T-1 to T-3 of section 9.

**Only checkable on the evidence** (owner supplement 1, section 4): the right-hand column of the table in section 3.

## 12. Integrity of this review

**New cell-308 target evaluations: 0.** Nothing evaluated a cell 305-309 or a drift in the band or its mirror; cell
309 untouched. The only science was the dev decoy suite on decoy cover cell 297, block 0, at the development ladder
(the block's pointwise drift lies below the band; the guard stayed DECOY); its decoy values stay in my scratch,
unread: I read status, count, resource and lifecycle fields only. Every other run used the synthetic evaluator, the
synthetic launchd payload or planted records, in sandboxes on my own `--no-local` base store. The designated
measurement tool, a full-length decoy, the apply step in a real worktree, a freeze and an official qualification were
not run; no authorization, grant, marker, pending result or seal exists; no system setting was changed; no git write
in any real repository; no launchd job and no plist was left. I was not interrupted: every report in section 0 is
from one uninterrupted run with its JSON report intact.

Ledger (agent `reviewF8`, `c308_quarantine.log_event`, target_evaluations 0, no LEAK_FLAG): INFRASTRUCTURE
2026-10-02T03:30:15Z; SYNTHETIC_VALIDATION 03:31:43Z; NONTARGET_DRIFT_VALIDATION 04:01:46Z; SYNTHETIC_VALIDATION
04:02:25Z; REVIEW at the end. This file was scanned with the research scanner's `_TAIL_RE`: 0 matches. My
sandboxes were deleted after the runs with the namespace's own tool (what it refused by design, the disk suite's
planted units, by hand at the end, with my checkouts and base store); the JSON reports, logs, probes and my mutant
definitions stay in `scratchpad/reviewF8/{reports,logs,probes,own}`.
