# Independent review of the MB308 freeze-r3 host-environment repair (reviewer reviewR3)
REPAIR_REJECTED

## 0. Scope, basis, method

* **Reviewer.** reviewR3, fresh. I wrote none of the reviewed material. Brief: research `ledger/briefs/21_reviewR3REPAIR.txt`.
* **Basis.** Formal worktree `/Users/suzhe/ReBaseGuard-c308mb`, branch `p5y-k5-cell308-mb-r1`, HEAD `d031dad8`
  (r2 FAIL evidence on freeze r2 `29b68d5e`), plus the UNCOMMITTED r3 candidate. At the start of the review all seven
  candidate hashes matched the brief (verified with `shasum -a 256`):
  `mb308_host.py b5db7e37…`, `mb308_driver.py 26513c16…`, `mb308_qualify.py 8b874736…`, `test_mb308_flows.py 54c9c8ee…`,
  `QUALIFICATION_CASES.json 518783e5…`, `MB308_PROTOCOL.md 45efbbe0…`, `MB308_FREEZE.json 54e9f4ab…`.
  The staged renames move the ten r2 evidence files unchanged (0 insertions, 0 deletions) into `qualification/r2_failed/`.
* **What I wrote.** This file; 10 ledger lines (class REVIEW, agent reviewR3, one per run; three small scratch probes
  were recorded late, at 06:12:45Z, and their lines say so); and scratch under the session scratchpad `reviewR3/`.
  The hashes were identical again at the end of the review. Nothing in the formal worktree; no ref created, moved or deleted; no git add / commit / stash / checkout.
* **Hard rules kept.** No `execute`, no `seal-only`. Nothing computed for cells 305-309; no drift in the band or its
  mirror. Decoy results are quoted by status and runtime only. No power / sleep / system setting changed (read-only
  `pmset -g batt|therm|log`, `sysctl kern.*`, `notifyutil -g`).
* **Runs (each ledgered, class REVIEW, agent reviewR3).** (a) `mb308_qualify.py --dev --only
  QC05,QC06,QC07,QC09,QC10,QC11,QC12 --record-scan` (all selected cases PASS; QC10 42 flows, 0 failed); (b) the 12
  Q12 planted controls and `_q12_core` / `q12_caps` on the committed r2 records; (c) eight in-process mutations of the
  Q12 decision path; (d) 21 own plants against `assess` / `_host_verdict` / `_q12_core`; (e) a counts-only
  leak-collision check of the new host fields; (f) `mb308_driver.py decoy --cell 297 --first-blocks 1 --dev-ladder
  --workers 2` (status CERTIFIED, stage 1 118.1 s, host CLEAN). Plus read-only host probes and a pre-freeze Q8
  consistency check (manifest vs working-tree bytes). Before and after: `git status --porcelain --ignored` and
  `for-each-ref` of the formal worktree hash-identical; `find -newer` shows no file written there.

## 1. Scope: environment only — PASS

Driver diff (`git diff --numstat`: +36 / −7, 7 hunks). Every changed line, classified:

| hunk | change | class |
|---|---|---|
| docstring | 4 lines describing the host provenance | text |
| imports | `import mb308_host as HOST` | environment |
| `HELPER_SHA256` | `+ "mb308_host.py": b5db7e37…` (matches the bytes) | pin |
| `after_marker` | `close_host(common)` after `common.update(...)`, before `serialize` | recording only; never raises (catches BaseException); runs after `signal.alarm(0)` |
| `keep_awake` | body now `HOST.keep_awake()` (`caffeinate -i -m -s -w pid`, was `-i -w pid`) | environment |
| new `require_ac`, `close_host` | AC refusal (maps `HostRefusal` to `Refusal`, exit 2) / closes the provenance | environment |
| `run_execute` | `pre["host_power"] = require_ac()` before `keep_awake`; `awake["host_at_start"]`; sampler started immediately before the marker `update-ref`, stopped on marker failure; `common["_host"]` | pre-marker refusal + provenance |
| `main` preflight | `"host_power": require_ac()` | pre-marker refusal |
| `main` decoy | snapshot + sampler before `decoy()`, `out["host"] = provenance(...)` after | provenance |

Unchanged (no hunk): every scientific function, the ladder, `stage1` (spawn pool, one job per worker), the order of
the scientific steps, the marker, the seal, `after_marker`'s status / outcome / exit-code logic, `EVAL_CAP_S` 28 800,
`PRE_CAP_S` 1 800, `DECOY_CAP_S` 43 200, `RUNG_CPU_CAP_S`, `WORKERS` 5. The regenerated manifest differs from the r2
manifest only in the six expected frozen files plus the new `mb308_host.py`, in `driver` and in `helper_sha256`; its
`caps` field and all 54 external pins are unchanged. Pre-freeze Q8 check: 21 frozen files, 0 mismatches (sha256 and
blob id from bytes), 0 unlisted, 0 absent; helper pins equal the bytes. The science code never reads wall time for a
decision: the only `time.time()` uses are wall-second fields, and the verification budgets are operation counts.
The spawn start method means the new sampler thread is never forked into a worker.

## 2. No weakening of Q12 — PASS

* **Same cap rule.** `_q12_core` keeps r2's body verbatim: the same `Q12_KEYS`, 11 blocks, 5 workers, longest-first
  makespan, `EVAL_CAP_S >= ceil(1.5 x projection)`, per-job `cap >= 2 x official max wall`, all jobs CERTIFIED, no
  bad job. The r2 pass expression is renamed `caps_pass` character for character.
* **The timing gate can only subtract.** `pass = caps_pass and timing_clean`, and `q12_caps` adds `and controls
  pass`. So an r3 Q12 PASS implies the r2 Q12 logic passes on the same records. No other path sets `pass`. The early
  returns (missing record, missing job kind) still return `pass: False`.
* **No recomputation from r2.** No constant changed (§1). Run on the committed r2 records, `_q12_core` reproduces r2
  exactly: the projection is equal, `eval_cap_ok` is False and the same per-job keys fail (C1B:10, RLR:6, RLR:8).
  It now also reports `TIMING_AMBIGUOUS_297` / `_316`, because those records carry no provenance.
* **Environment choice is not easing.** The run conditions (awake, cool, idle) do not touch Q12. They do mean the
  caps' evidence transfers to the execution only if the execution runs under the same conditions (E-conditions).

## 3. Sleep prevention — PASS WITH NOTE

* **Coverage.**
  * The qualifier calls `HOST.keep_awake()` (`caffeinate -i -m -s -w <qualifier pid>`) as the first act of `main`.
    The decoy children run while it waits, so the assertion covers the whole official run.
  * `execute` calls it before the marker.
  * Decoy mode does not call it itself. That matters only for standalone decoys, which are never evidence (N4).
* **Confirmed live.** During my dev run the power log recorded `PID 65234(caffeinate) Created PreventSystemSleep`
  with `[System: PrevIdle PrevSleep …]` at 14:41:00 +0900, which is the pid the report stores.
* **`-s` needs AC.** `-s` holds only on AC power. AC is therefore required at the start, and at every sample of the
  decoy runs (§5).
* **Lid close is stated honestly.** The module docstring and §14 say lid-close sleep cannot be prevented by an
  assertion, and that detection binds. That is true for this host: no external display, and `pmset disablesleep`
  would need sudo and is excluded. The r2 log agrees: both r2 sleeps were `Clamshell Sleep`, one of them "Using AC".
* **Where detection binds.** For the qualification, detection binds through Q12. For the execution, only prevention
  and the operator conditions protect the one evaluation from being wasted (§8).
* **`keep_awake` failure is not a refusal.** If caffeinate cannot start, `keep_awake` returns
  `{"caffeinate": "unavailable (...)"}` and the run continues. That is acceptable (it is `/usr/bin/caffeinate`, and
  the sealed record shows it), but E4 makes the execution check it.

## 4. AC at preflight and before the marker — PASS WITH NOTE

* **Driver.** `run_execute` calls `require_ac()` after `check_cpu_caps` and long before the marker `update-ref`. A
  non-AC reading raises `Refusal("HOST_NOT_ON_AC")`, which `main` maps to exit 2. `preflight` calls it too.
* **T23 (dev run).** T23 plants `Now drawing from 'Battery Power'` at the `pmset` text layer. Result:
  `{"refused": "HOST_NOT_ON_AC"}`, marker unchanged, evaluator calls 0.
* **T23 can fail.** Without the check, the stub evaluation would run: exit 0, not the refusal, so the case would fail.
* **X01 records AC.** X01 now requires `seal_preconditions.host_power == "AC Power"` and a host assessment in the
  sealed record.
* **QC11 static guards.** All six are true.
* **Note.** Two of them are loose: `ac_required_in_preflight` and `decoy_host_provenance_recorded` only count calls
  anywhere in `main`, not in the right branch or bracket. Code reading and my dev decoy confirm the placement.
* **Qualifier official preconditions.**
  * `host_on_ac` works.
  * `host_sleep_channels_available` works (the kern-times parse plus one `pmset -g log` read).
  * `host_no_thermal_warning_recorded` does **not** detect a hot host on this machine (§5 T, F2).

## 5. The sleep channels on this host — PASS (K, S, L, power); FAIL on the thermal field (F2)

Checked read-only on this host (Mac17,5, macOS 25.5, +0900).

* **K (CLOCK_MONOTONIC − CLOCK_UPTIME_RAW).**
  * **Since boot** (2026-09-20) it is 24 134.8 s, which is plausible for this week's sleeps.
  * **Awake, 120 s:** the difference moved by −111 µs (−0.9 ppm).
  * **The flaw.** CLOCK_MONOTONIC is frequency-adjusted: since boot it lags CLOCK_MONOTONIC_RAW by 11.06 s, about
    14 ppm on average. CLOCK_MONOTONIC_RAW − UPTIME_RAW moved by only +6.9 µs in the same 120 s.
  * **Size of the risk.** The 2 s tolerance over a 17 000 s run allows about 118 ppm of slew, so a false result is
    unlikely. It would fail closed. N1 recommends the RAW clock.
  * **Missed sleeps.** A sleep longer than 2 s cannot hide from K. A sleep between the last sample and the end
    snapshot is caught, because K spans [start, end]: the K control plants its gap only at the end.
* **S (`kern.sleeptime` / `kern.waketime`).**
  * **Parse.** Live, both keys parse.
  * **Values.** They equal the last maintenance sleep and the final wake of the r2 day (13:41:35 / 13:42:02 +0900).
    The log stamps are 13:41:33 Sleep and 13:42:03 Wake.
  * **Rule.** Any change fails. Display sleep does not touch them.
* **L (`pmset -g log`).**
  * **Parser against the whole log.** The log has 47 550 lines, from 2026-09-22 on. The parser counts 51 Sleep,
    46 DarkWake and 7 Wake entries, identical to an independent per-type count. It does not count
    `Wake Requests` (51 lines), `WakeDetails`, `WakeTime`, `HibernateStats`, `ThermalEvent`, or `Notification`
    (display on / off).
  * **r2 window** (00:11:03–04:54:07Z): 20 entries, from Sleep at 01:31:29Z to Wake at 04:42:03Z.
  * **Addendum a1's sleep-free RLR d8 window** (to 01:31:15Z): 0 entries.
  * **Timezone.** `%z` handles +0900.
  * **Window bounds.** The window is [t0 − 1, t1 + 1]. An entry 1 s after t1 is counted and one 2 s after is not
    (tested).
* **Power.** Parsed live as `AC Power`. The second r2 sleep was logged "Using Batt": the host lost AC during r2. r3
  catches that, because AC is required at every sample.
* **Samples.** One every 60 s; a gap over 180 s fails. `//` floors, so 180.9 s passes and 181 s fails. A sampler
  that dies, raises or returns junk gives AMBIGUOUS (my plants P6–P8). Clock anomalies also give AMBIGUOUS: uptime
  ahead of monotonic time, floats, or samples out of order (P13–P15).
* **Not detected.** A process stop without a system sleep is not detected. It can only lengthen wall times, which
  fails Q12.
* **T (thermal): FAIL.**
  * **Seven reads, 05:36–05:51Z.** `pmset -g therm` printed only its three "Note: No … recorded" lines. The OS
    thermal-pressure level (`notifyutil -g com.apple.system.thermalpressurelevel`, read-only) read **1**: not
    nominal, and Moderate in OSThermalNotification.h. Load was 1.4–5 over the same reads.
  * **The level moves; `pmset -g therm` does not.** At about 05:58Z and at 06:03:48Z the level read **0**, while
    `pmset -g therm` printed the same text throughout.
  * **Consequence.** The recorded thermal field, and the official precondition built on it, cannot see the state
    that addendum a1 names as the likely cause of the sleep-free slowdown.
  * **Also missed.** The power log's `ThermalEvent` lines are not recorded.
  * **Soundness is unaffected.** Throttling only lengthens runtimes. But the user asked for *relevant* thermal
    provenance and a cool host, and this check is presence-as-detection (F2).

## 6. Fail-closed semantics — PASS WITH NOTE

* **Only CLEAN passes.** `assess` returns CLEAN only if every reason list is empty. A seen sleep, or a non-AC
  reading, gives CONTAMINATED; anything missing, unparseable, out of order or uncovered gives AMBIGUOUS.
* **Re-assessed from raw readings.** `_host_verdict` re-runs `assess` on the stored `start` / `samples` / `end` /
  `events`. If the stored status differs, or is absent, the result is AMBIGUOUS. A record without provenance, or with
  a non-dict `host`, is AMBIGUOUS. `timing_clean` requires both 297 and 316 to be CLEAN.
* **My 21 plants** all behaved as designed:
  * 2.000 s gap → CLEAN (tolerance); 2.001 s → CONTAMINATED;
  * stored CLEAN over a raw log event → AMBIGUOUS; stored assessment missing → AMBIGUOUS; `host = {}` → AMBIGUOUS;
  * empty samples over 13 min, a junk sample, a sampler error entry → AMBIGUOUS;
  * `kern_us` absent, or with an extra key → AMBIGUOUS; only `waketime` changed → CONTAMINATED;
  * events given as a string → AMBIGUOUS;
  * uptime 3 s ahead, float clocks, reversed samples, unreadable end power → AMBIGUOUS;
  * `"AC Power "` → CONTAMINATED;
  * thermal warnings → still CLEAN (recorded, not gating, as designed).
* **Is the interval right?** Yes. Each decoy's interval opens before `decoy()` and closes after it, so it is a
  superset of every job wall Q12 reads. My dev decoy shows this: interval 118.9 s ⊇ stage 1 118.1 s + stage 2 0.5 s.
  The record's `wall_seconds` of 120.7 s also includes the closing log read.
* **Note: nothing checks that the interval covers the jobs.** A planted 2-minute host interval vouching for jobs of
  up to 2 175 s still passes (P21). Coverage rests on the pinned driver's code order, not on the data. N2.

## 7. The 12 planted controls — FAIL on one control (F1); otherwise PASS

* **Same path.** All 12 run through `_q12_core`, Q12's own decision function. `q12_caps` requires all 12 to be ok
  and exactly 12 to exist. Run on the candidate: 12/12 ok. The clean control passes. Each K / S / L / battery /
  unavailable / missing / uncovered / no-provenance control fails with caps passing. Both violation controls fail on
  `CAP_RULE_VIOLATED`. The combined control reports both reasons.
* **Can they fail?** I mutated the decision path in-process:

  | mutation | caught by the controls? |
  |---|---|
  | M1 `assess` always CLEAN | yes, 8 controls fail |
  | M2 `_host_verdict` ignored | yes, 9 |
  | M3 projection → 0 | yes |
  | M4 log parser never matches | yes |
  | M5 K tolerance 1 h | yes |
  | M7 EVAL_CAP multiplier 1.5 → 1.0 | yes |
  | M8 timing left out of `pass` | yes, 8 |
  | **M6 per-job rule 2× → 1×** | **no: all 12 still ok** |

* **Why M6 slips through.** The control `genuine_per_job_cap_violation_clean_host` plants RLR d8 at 0.6 × cap with
  everything else at 0.25 × cap. That also breaks EVAL_CAP: the projection is 21 465 s, so 32 198 s would be needed,
  against 28 800. The control therefore fails on EVAL_CAP whatever the per-job rule says, and it asserts only the
  aggregate reason. It does not show that a genuine per-job violation stays detectable, which is one of the user's
  required demonstrations.
* **The fix is small.** For example, all jobs at 0.10 × cap and RLR d8 at 0.55: `eval_cap_ok` stays True and the only
  failing key is RLR:8 (projection 14 520 s). Checked. F1.
* **Smaller gaps.** No control plants a stored-vs-recomputed mismatch (my P3 shows the code handles it). The S
  control plants integers rather than `sysctl` text. The L control asserts only CONTAMINATED, not that
  `Wake Requests` / `Assertions` are skipped (my full-log check above shows they are). N3.

## 8. The execution side (protocol §14) — PASS WITH NOTE

§14's reading is acceptable. The user's rule covers load-bearing *timing* intervals. The execution has no timing
input to its verdict:

* Γ_dec is exact arithmetic, and the verification budgets are operation counts (`VERIFY_BUDGET`).
* The per-job caps are `RLIMIT_CPU`, which counts CPU time and not sleep.
* PRE_CAP fires before the marker, as a refusal.
* An EVAL_CAP hit, or any failure, gives `CELL308_EXECUTION_INDETERMINATE`.

A sleep can therefore waste the evaluation but cannot make it close falsely. That is already fail-closed.

A stricter rule would be worse, not safer. Consider "host provenance not CLEAN ⇒ INDETERMINATE", or a re-run. The
first discards a valid exact result. The second breaks exactly-once and creates a result-chasing lever: a NOT_CLOSED
run that happened to include a sleep could be "repeated". So what the execution must do is:

* never let host provenance change the status, the outcome or exactly-once;
* record the provenance (it does: `close_host` after `alarm(0)`, never raising, before `serialize`; worst-case
  added delay is bounded by the 60 s join plus the `pmset` timeouts);
* run under the same host conditions as the qualification (E1–E4).

The note: because detection cannot rescue the one evaluation, prevention and the operator conditions are the only
protection against wasting it (§3).

## 9. Interaction with the other gates — PASS

* **QC04.** The new `host` block sits at the top of the decoy record. QC04 compares only Stage-1 job views (status
  and record, timing stripped at every depth), and the serial and ladder children carry no host block. So there is
  no new compared field.
* **QC10.** 42 flows, against r2's 41. The one addition is T23; X01 is extended. 0 failed in my dev run.
* **QC11.** The six host guards pass. Two are loose (§4).
* **QC12.** The new fields are integers, ISO strings without fractions, and `pmset` text. A counts-only check:
  * 0 of the 317 record and geometry tokens are digit-only (each contains `.` or `/`);
  * 0 of the 70 tail patterns has a digit-only literal;
  * a synthetic 5-hour host record (300 samples, live clock magnitudes) gives 0 tail hits and 0 token hits.

  My dev `--record-scan` covered 42 namespace files, including `qualification/r2_failed/`: 0 tail hits, 0 token hits,
  and all planted controls fired. The r2 files keep the timing-key exemption, because the path's first part is still
  `qualification`.
* **Q8.** `mb308_host.py` is listed, and the helper pin is in both the driver and the manifest. The pre-freeze check
  in §1 is clean. The real Q8 needs the freeze commit, because blob ids are compared at HEAD.
* **QC13.** Code unchanged. The builder's r3 ledger lines are SYNTHETIC_VALIDATION or NONTARGET_DRIFT_VALIDATION with
  0 target. Mine are REVIEW.
* **Ordering note (pre-existing).** The official run computes QC12 before the decoy children finish. So the decoy
  records and the report, with their new host blocks, are first scanned by the qualification review's `--review` run
  (N5).

## 10. Honesty and residual risk — PASS WITH NOTE (F3)

* **No hidden easing.** The caps, the cap rule, the concurrency (the qualifier's spawn set and worker counts are
  untouched), the heavy cases and the thresholds are all unchanged. §14 says openly that the failure was not
  sleep-only, and that the sleep-free RLR d8 316 block-0 time fails Q12 by itself.
* **How thin the margin is.** From the committed r1 and r2 Q12 blocks (runtime only):
  * RLR d8 passes only if its official maximum stays at or below 4 350 s. That is **+4.8 %** over r1's 4 149.9 s;
    r2's sleep-free value was +15.9 %.
  * EVAL_CAP passes only if the projection stays at or below 19 200 s: **+6.2 %** over r1's 18 071.9 s.

  r3 therefore passes Q12 only if the heavy window runs essentially at r1 speed.
* **What §14 leaves unsaid.** It does not say that:
  * r3 does not address the slowdown component;
  * a Q12 FAIL on a CLEAN host is a genuine cap failure;
  * what follows any r3 FAIL.

  Without a rule declared now, a clean FAIL could be followed by "r4, same caps, cooler host". That is qualification
  shopping by another name, which the r2 assessment §4 itself warns against. F3 pre-declares the rule.

## 11. Other findings

* **r2 also lost AC.** The second r2 sleep is logged `Entering Sleep state due to 'Clamshell Sleep' … Using Batt`, and
  the maintenance sleeps after it also say Batt. The r2 assessment does not mention this. It is one more reason for
  r3's AC-at-every-sample rule.
* **The whole-run provenance is recorded, not gated.** The qualifier stores its own whole-run provenance in the
  report (my dev report: CLEAN, 4 samples, gap −1 ms). No other case is timing-sensitive, so recording it is right.
* **The flows start many caffeinates.** The in-process flow tests start one caffeinate per sandbox `execute`. The
  power log shows about 15 `PreventSystemSleep` assertions created 14:44–14:45 +0900 and released (`ClientDied`) when
  the qualifier exited. This is harmless.
* **Brief 21.** It was committed at research `947e5000` (05:28:02Z), before my first ledger line (05:41Z). Its text
  matches the brief I received.
* **Not in scope and not checked.** Launch QoS / App Nap effects on CLI children (a possible, unproven contributor to
  the sleep-free slowdown). O5 keeps the launch path the same as r1's.

## Verdict and reason

The core repair is sound, and I accept it on the merits:

* it is environment-only (§1);
* Q12 is strictly stronger (§2);
* the three sleep channels work on this host and fail closed (§5, §6);
* §14's reading of the execution side is right (§8);
* the other gates are unaffected (§9).

The candidate **as submitted** may not be frozen. Two of the user's explicit r3 requirements are not met as built:

* **Thermal provenance.** The user asked for *relevant* thermal provenance and a cool host. The only thermal channel,
  `pmset -g therm`, is blind on this host: it reported "no warning" while the OS thermal-pressure level was 1 and
  then 0 (§5). The official "no thermal warning" precondition is therefore presence-as-detection.
* **Per-job detectability.** The user asked for planted controls showing that genuine cap violations stay
  detectable. The per-job control is not specific: a weakened per-job rule (M6) passes all 12 controls (§7).

Both fixes touch the code that the 5-hour official qualification would rely on. The user asked for that code to be
independently reviewed before anything relies on it. So the fixes need a short delta review before the freeze;
waving them through as conditions is not enough.

Everything not named in F1–F3 stands as reviewed. The delta review may be confined to the F1–F4 lines and a re-run
of the controls, the mutations M1–M8 and the dev cases.

## FREEZE CONDITIONS (all before the r3 freeze; F1–F3 need the delta review, F6)

* **F1. A specific per-job control.** Replace the planted fractions of `genuine_per_job_cap_violation_clean_host` so
  that EVAL_CAP passes and exactly one per-job key fails. For example all jobs at 0.10 × cap and RLR d8 at 0.55; I
  checked that this gives projection 14 520 s, `eval_cap_ok` True, failing key RLR:8. The control must assert
  `caps_pass` False, `eval_cap_ok` True and the failing per-job set equal to `{RLR:8}`. Then mutation M6 (per-job
  2× → 1×) must fail the control set.
  * Recommended as well (N3): a stored-vs-recomputed mismatch control, and an exact parsed count (3) for the L
    fixture.
  * If the number of controls changes, `q12_controls`' `len(rows) == …`, §14 and `QUALIFICATION_CASES.json` must all
    state the new number.
* **F2. Relevant thermal provenance.**
  * **Record.** In `mb308_host.snapshot()` and `sample()`, record the OS thermal-pressure level, read-only via
    `/usr/bin/notifyutil -g com.apple.system.thermalpressurelevel`. Store it as an integer, or None if unreadable.
    `assess` reports the maximum level and the unreadable count per interval. Also record the power log's
    `ThermalEvent` entries within the interval.
  * **Gate the start only.** Thermal must not enter `assess`'s status or Q12's pass. Throttling can only fail Q12,
    so gating Q12 on it would add a decision rule the user did not ask for. The official preconditions require the level to be
    readable and 0 (nominal) at start. `pmset -g therm` may stay recorded, but §14 and the qualifier docstring must
    no longer present it as a cool-host check.
  * **If the host never reaches 0.** If the host cannot reach level 0 after a cool-down, that goes to the user. It is
    not lowered.
* **F3. Pre-declared consequences (§14 text).** §14 must state that:
  * r3 does not address the sleep-free slowdown;
  * r1's headroom (RLR d8 +4.8 %, EVAL_CAP projection +6.2 %) is the whole allowance;
  * any r3 official Q12 FAIL, whether with CLEAN timing (a genuine cap failure) or with CONTAMINATED / AMBIGUOUS timing,
    is a qualification FAIL that stops the campaign before the target (C4 point 7);
  * freeze r3 is never re-run, and no r4 with the same caps is made, without a new explicit user decision recorded
    before it.
* **F4. Bounded delta.** Measured against the reviewed hashes in §0, the frozen files may differ only by:
  * the F1–F3 edits (and N1 / N2, if adopted) in `mb308_host.py`, `mb308_qualify.py`, `QUALIFICATION_CASES.json` and
    `MB308_PROTOCOL.md`;
  * the `mb308_host.py` entry of the driver's `HELPER_SHA256`. The driver must otherwise stay byte-identical to
    `26513c16…`;
  * the regenerated `MB308_FREEZE.json`.

  `test_mb308_flows.py` stays `54c9c8ee…` unless a flow must change for F2, and then only for that. The 10 r2
  evidence files move unchanged, as staged.
* **F5. Dev evidence on the final bytes, before the freeze (ledgered).**
  * `--dev --only QC05,QC06,QC07,QC09,QC10,QC11,QC12 --record-scan` passes.
  * The Q12 controls pass, and their rows show F1's specificity fields.
  * One dev decoy record shows the thermal level and ThermalEvent fields.
  * The pre-freeze Q8 consistency (§1) is clean.
* **F6. Delta review before the freeze.** A fresh independent reviewer, or I if resumed, checks F1–F5 against this
  file. The check covers the delta lines and a re-run of M1–M8 on the final bytes, with M6 now caught. The freeze
  follows only on an accepting delta verdict. §14 then cites both review files, and each file's research commit and
  sha256.

## OFFICIAL-RUN CONDITIONS

* **O1. Start state.**
  * HEAD is the r3 freeze commit; the tree is tracked-clean, and the namespace is clean including ignored files.
  * No marker ref and no emergency file exist.
  * Nothing else of this campaign is running: no builder or reviewer dev runs, and no other agent's compute on this
    Mac.
* **O2. Power and lid, for the whole run.**
  * The lid stays open.
  * The AC adapter stays connected and is never unplugged (r2 lost AC).
  * `lowpowermode` is 0; I read 0 today. The display may sleep, because caffeinate holds the system.
* **O3. A cool start.** Start after an idle cool-down, with the thermal-pressure level at 0 (F2's precondition).
  Today it read 1 from 05:36 to 05:51Z, with light load, and 0 from about 05:58Z.
* **O4. No other heavy work.**
  * Quit or idle heavy apps (the log shows video wake-locks today).
  * The 1-minute load average at start is near idle; the start snapshot records it.
  * No interactive heavy use during the ~5 h.
* **O5. Same launch as r1.** Same interpreter and flags, same qualifier defaults (worker counts, concurrent heavy
  cases), same launch path. Only then are r3's runtimes comparable with r1's.
* **O6. Commit and stop.**
  * Commit the evidence on its own, in the r1 / r2 layout.
  * Report QC02 / QC03 host status, maximum thermal level and maximum load, by status and runtime only.
  * Apply F3 mechanically: no interpretation, no retry.
* **O7. The qualification review.** It runs `--review` on the committed records: Q12 re-derived from the stored raw
  readings, QC12 over the new host blocks. It checks F1–F6 and the reviewed-hash delta (F4).

## EXECUTION CONDITIONS (for the grant and the execution review)

* **E1. Same host conditions as the qualification.** The execution runs under O2–O4: AC (enforced before the
  marker), lid open, thermal level 0 at start, no other heavy work, `lowpowermode` 0. The caps' margin evidence comes
  from qualification runtimes measured under those conditions, and transfers to the execution only under them.
* **E2. Provenance never changes the result.** Host provenance never changes the status, the outcome or
  exactly-once. There is no re-run and no re-interpretation on host grounds. An EVAL_CAP hit is the pre-declared
  INDETERMINATE.
* **E3. The execution review reports the host record.** From the sealed record it reports: the host assessment
  status, reasons, samples, largest spacing, sleep gap, maximum thermal level (after F2) and maximum load, and
  `seal_preconditions.host_power`. It discloses any sleep.
* **E4. The execution review checks caffeinate.** `environment.caffeinate_pid` must be present. If it says
  "unavailable", that is disclosed; it does not invalidate the result.

## NOTES

* **N1. Use the RAW clock for K.** Channel K would be cleaner with CLOCK_MONOTONIC_RAW − CLOCK_UPTIME_RAW. That pair
  is unadjusted: +6.9 µs over 120 s here, against −111 µs for CLOCK_MONOTONIC, and an 11 s gap since boot.
  Optional; if adopted, it falls within F4.
* **N2. Cross-check the interval against the jobs.** Q12 could require each decoy's host interval to cover
  `stage1_wall_seconds + stage2_wall_seconds` (P21). QC11 could assert that the snapshot and sampler precede
  `decoy()` and that `provenance` follows it. Optional.
* **N3. Smaller control gaps.** There is no stored-vs-recomputed control, the S control never parses `sysctl` text,
  and the L control asserts only CONTAMINATED. All three are verified by me, but not by the gate.
* **N4. Standalone decoys.** Decoy mode does not start caffeinate itself. It is covered only when run under the
  qualifier. That is fine, because standalone decoys are never evidence.
* **N5. QC12 ordering.** The official QC12 runs before the decoy children finish (pre-existing ordering). The new host
  blocks are first scanned in the review run. By construction they cannot collide (§9).
* **N6. Loose static guards.** QC11's `ac_required_in_preflight` and `decoy_host_provenance_recorded` are
  presence counts over `main`.
* **N7. Counts only for decoys.** Decoy results are quoted here by status and runtime only. No decoy value was read.
  No tail figure appears in this file.
