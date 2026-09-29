# Delta review of the MB308 freeze-r3 host-environment repair, condition F6 (reviewer reviewR3)
DELTA_ACCEPTED

## 0. Basis

* **Reviewer.** reviewR3, the same independent reviewer who wrote `reviews/REVIEW_R3_HOST_REPAIR.md`: research
  commit `4b38eef2`, sha256 `d39e25ef…f491`, REPAIR_REJECTED as submitted. Brief 22 (research `44b2c74c`).
  Brief 21's absolute rules still apply.
* **Candidate.** Formal worktree `/Users/suzhe/ReBaseGuard-c308mb`, HEAD `d031dad8`, UNCOMMITTED, r2 renames still
  staged. All seven final hashes match brief 22, at the start and at the end of this review:
  `mb308_host.py 6702a9be…`, `mb308_driver.py 411252b2…`, `mb308_qualify.py 48d48049…`,
  `test_mb308_flows.py 54c9c8ee…` (unchanged), `QUALIFICATION_CASES.json 57c78b41…`,
  `MB308_PROTOCOL.md 64c29109…`, `MB308_FREEZE.json 04e2899a…`.
* **Written.** This file; ledger lines (class REVIEW, agent reviewR3, one per run); scratch under
  `reviewR3/delta/`.
* **Not done.** Nothing written in the formal worktree. No ref created or moved; no git add or commit; no execute or
  seal-only. Nothing computed for cells 305–309 or in the band. No power setting touched.

## 1. What changed, checked against the first review

* **F4, bounded delta: PASS.**
  * **Driver.** `diff` against the reviewed copy (`r3dev/driver_26513c16.py`, whose sha256 I confirmed is
    `26513c16…`) is one line: the `mb308_host.py` entry of `HELPER_SHA256`, `b5db7e37…` → `6702a9be…`.
  * **Flows test.** `54c9c8ee…`, byte-identical.
  * **Qualifier, read in full against r2 and my first-review diff.** The only new edits are:
    * the docstring;
    * the preconditions (the thermal level replaces pmset-therm);
    * QC11 (branch-exact);
    * `_host_verdict` (N2);
    * the control fixtures and `q12_controls` (F1, N3).

    `_q12_core`, `q12_caps`, `_decoy_jobs`, `main` and every cap or threshold line are unchanged from the reviewed
    bytes.
  * **Host module.** Changes limited to K on the raw clock (N1) and the thermal-level and ThermalEvent recording
    (F2). `assess`'s gating logic is otherwise identical.
  * **Config, protocol, manifest.** The config changes the Q12_caps, QC10 and QC11 texts and the revision. The
    protocol changes the header and §14. The manifest was regenerated. My pre-freeze Q8 check from bytes: 21 frozen
    files, 0 mismatches, 0 unlisted, 0 absent; 54 external files, 0 changed; manifest fields changed against r2 are
    only `driver`, `helper_sha256` and the six frozen files plus `mb308_host.py`; helper pins equal the bytes.
* **F1, a specific per-job control: PASS.**
  * **The control.** `{all 0.10, RLR d8 0.55}` asserts `caps_pass` False, `eval_cap_ok` True, failing keys exactly
    `["RLR:8"]` and reason `["CAP_RULE_VIOLATED"]`.
  * **The other two.** The EVAL-only control asserts an empty failing-key set. The combined control asserts both
    reasons and `["RLR:8"]`.
  * **Result.** 14/14 controls, and M6 is now caught (§2).
* **F2, relevant thermal provenance: PASS.**
  * **Recorded.** `thermal_level()` reads `notifyutil -g com.apple.system.thermalpressurelevel` (integer; None if
    unparseable) in every snapshot and sample. `provenance` records `thermal_events` (ThermalEvent) from the same
    single log read.
  * **Never gates.** `assess` reports `thermal_level_max` and `thermal_level_unreadable`. My plants Q3–Q5: level
    None or 3 everywhere stays CLEAN, and the fields count correctly.
  * **Precondition.** The official precondition is `thermal_level() == 0`, which fails on None.
  * **Honest docstrings.** The host and qualifier docstrings and §14 call `pmset -g therm` a record only, not a
    cool-host check.
  * **Live parse.** On the live and scratch logs the ThermalEvent parser finds 3 entries. The L channel still finds
    exactly 51 Sleep, 46 DarkWake and 7 Wake entries, and never a ThermalEvent.
  * **Coordinator's decoy.** The F5 decoy recorded levels 0, 1, 2, 2 (disclosed), which shows the channel is live.
* **F3, pre-declared consequences: PASS.** §14 now states all of these, marked binding:
  * r3 does not address the sleep-free slowdown;
  * r1's headroom is the whole allowance (RLR d8 about +4.8 %, EVAL_CAP projection about +6.2 %);
  * any r3 official Q12 FAIL, whether the timing is CLEAN, CONTAMINATED or AMBIGUOUS, stops the campaign before the
    target (C4 point 7);
  * r3 is never re-run, and no r4 with the same caps is made, without a new explicit user decision recorded before
    it.

  §14 also carries my E2 wording ("host provenance never changes the status, the outcome or exactly-once") and the
  execution host conditions (E1). The r2 battery observation is added.
* **N1, raw clock for K: PASS.** `clocks()` stores `monotonic_raw_ns`, and `assess` and the spacing check use it.
  The controls and `_host_verdict` use the same key.
  * Awake, CLOCK_MONOTONIC_RAW − UPTIME_RAW moved +6.9 µs in 120 s.
  * Since boot, the wall clock runs 14.3 ppm slower than the raw clock (−11.06 s over 772 946 s), so there is no
    slew false-positive for K.
  * An old-format record (no raw key) is AMBIGUOUS (Q2).
* **N2, interval coverage: PASS.** `_host_verdict` gives AMBIGUOUS when the floored raw span + 1 s < stage 1 +
  stage 2 walls. My plants: the edge span + 1.0 is CLEAN, span + 1.1 and stage1 + stage2 over the span are
  AMBIGUOUS, and a non-numeric wall is AMBIGUOUS. There is a dedicated control.
  * **False-positive margin.** On the F5 decoy the setup margin is 0.59 s. Because the raw clock runs 14 ppm fast
    against wall time on this host, a 17 000 s run adds about +0.24 s to that margin. So a genuine run cannot trip
    it.
* **N3: PASS.**
  * A stored-vs-raw contradiction control exists (stored CLEAN over a raw log entry → AMBIGUOUS).
  * S is parsed from real-format `sysctl` text in every control.
  * The L control asserts the exact parse: `[Sleep, DarkWake, Wake]` overall and `[Sleep, DarkWake]` in its window.
  * `q12_controls` requires exactly 14.
* **N6, branch-exact QC11: PASS WITH NOTE.** I ran `qc11_static` over mutated driver copies in scratch:
  * `require_ac` moved from preflight to rehearse → caught;
  * `require_ac` removed from `run_execute` → caught;
  * snapshot and sampler both after `decoy()` → caught;
  * **only the sampler** moved after `decoy()` (the snapshot still before) → **not caught**. The check takes the
    minimum line over snapshots and samplers together.

  This is harmless at run time: a late sampler leaves a start-to-first-sample gap, which `assess` turns into
  AMBIGUOUS on any decoy longer than 180 s. The driver bytes are pinned in any case. Note N2 below.
* **F5, dev evidence on the final bytes: PASS.**
  * **Produced on the final bytes.** `r3f5/` was written 15:26–15:29 +0900, after the last candidate edit at 15:23.
    `f5_dev.json` records `verifier_sha256` `48d48049…` and the decoy `driver_sha256` `411252b2…`.
  * **Results.** `f5_dev`: all selected cases pass, QC10 42 flows / 0 failed. Controls 14/14. The decoy host record
    is CLEAN and carries `thermal_level` and `thermal_events`.
  * **My own reproduction.** See §3.

## 2. Mutations on the final bytes

Every source mutation asserts that its replacement string occurs exactly once, so none is vacuous. Unmutated: 14/14
controls pass.

| mutation | caught? | failing controls |
|---|---|---|
| M1 `assess` always CLEAN | yes | 8 |
| M2 `_host_verdict` ignored | yes | 11 |
| M3 projection → 0 | yes | EVAL control |
| M4 log parser never matches | yes | L fixture, stored-vs-raw |
| M5 K tolerance 1 h | yes | K, combined |
| **M6 per-job rule 2× → 1×** | **yes (was not caught in the first review)** | per-job, combined |
| M7 EVAL_CAP 1.5× → 1.0× | yes | EVAL control |
| M8 timing left out of `pass` | yes | 10 |
| M9 N2 coverage check disabled | yes | short-interval control |
| M10 stored-vs-raw check disabled | yes | stored-vs-raw control |
| M11 S parser always None | yes | 5 |
| M14 parser also counts `Wake Requests` | yes | L fixture |
| M12 per-job 2× → 1.9× | no | — |
| M13 EVAL_CAP 1.5× → 1.4× | no | — |
| M15 K-absent reason dropped | no | — |

* **M12 and M13.** Each control plants one point well past its threshold, so a small drift of a constant goes
  unseen. The constants are unchanged from r2's `_q12_core` (byte-identical lines) and are pinned by the freeze
  manifest, so this is a sensitivity limit, not a hole. Note N1.
* **M15.** The K-missing control drops the whole end clock, so the spacing check reports AMBIGUOUS too. The real
  code still returns AMBIGUOUS when only `uptime_raw_ns` is missing (my plant Q1). Note N1.

## 3. My own runs on the final bytes (each ledgered)

* **Dev qualification.** `--dev --only QC05,QC06,QC07,QC09,QC10,QC11,QC12 --record-scan`, `verifier_sha256`
  `48d48049…`: every selected case PASS.
  * QC10: 42 flows, 0 failed. T23 → `HOST_NOT_ON_AC`; X01 ok. The one traceback is the planted worker-bootstrap
    flow.
  * QC11: every key true.
  * QC12: 42 files; 0 tail hits; 0 of 309 record tokens; all planted controls fired.
  * The qualifier's own host record: CLEAN, 4 samples, thermal level at most 1, 0 unreadable, caffeinate `-i -m -s`.
* **Plants (Q0–Q12).** All as expected, including: only `uptime_raw_ns` missing → AMBIGUOUS; old-format clocks →
  AMBIGUOUS; stored status `"CLEAN "` → AMBIGUOUS.
* **Mutations.** §2.
* **QC11 guard mutations.** §1, N6.
* **Pre-freeze Q8 consistency.** §1.
* **Read-only host probes.** Thermal level, `notifyutil` on an unposted key, and the wall- versus raw-clock drift
  since boot.

## 4. Regressions looked for

None found.

* The flows test still asserts only the host status set, which the new keys satisfy.
* No stale key (`monotonic_ns`, `thermal_warning_recorded`, `thermal_unreadable`) is left in code, tests or config.
* The new integer field `thermal_level` and the hex citation that will enter §14 cannot hit the leak scans: every
  tail pattern and every record token contains `.` or `/`.
* ThermalEvent is matched by the log regex but filtered out of L by type (checked on the whole real log).
* One `pmset -g log` read serves both L and ThermalEvent, and an unreadable log still gives AMBIGUOUS.
* The worktree status hash and the campaign refs are unchanged, and `find -newer` shows no file written in the
  formal worktree.

## 5. The permitted post-verdict change: accepted, on one condition

I accept the coordinator's plan:

* commit this file on the research branch;
* replace ONLY the token `DELTA_REVIEW_CITATION_PENDING` in §14 (it occurs exactly once in `64c29109…`) with
  "commit <research commit>, sha256 <sha256 of this file>, <verdict token>";
* regenerate `MB308_FREEZE.json` with `code/mb308_manifest.py`;
* commit freeze r3.

**Condition D1.** At the freeze commit the following must hold, and the qualification review checks them:

* the frozen `MB308_PROTOCOL.md` equals `64c29109…` with exactly that one substitution and no other byte changed;
* every other frozen file equals the hash listed in §0;
* `MB308_FREEZE.json` differs from `04e2899a…` only in the protocol entry's `sha256` and `git_blob`;
* the r2 evidence moves unchanged into `qualification/r2_failed/`;
* the freeze commit touches exactly the seven candidate files and those ten renames, and nothing else.

## 6. Official-run and execution conditions (kept, amended)

The O and E conditions of the first review stand. The amendments are marked.

* **O1. Start state.** HEAD is the r3 freeze commit, which satisfies D1. The tree is tracked-clean and the namespace
  is clean including ignored files. There is no marker ref and no emergency file. No other campaign or agent compute
  is running on this Mac.
* **O2. Power and lid.** The lid stays open for the whole run. AC stays connected and is never unplugged.
  `lowpowermode` is 0.
* **O3. Cool start (amended).** The precondition requires thermal-pressure level 0 at start. Start after an idle
  cool-down. That is necessary but not sufficient: the coordinator's own short decoy climbed from level 0 to 2
  within about 2 minutes while the dev qualifier ran alongside it. The official QC02/QC03 window runs 7–10 CPU-bound
  processes. Level 0 at start does not guarantee r1 speed, and F3 governs the outcome.
* **O4. No other heavy work.** Load near idle at start; no interactive heavy use during the run.
* **O5. Same launch as r1.** Same interpreter and flags, same qualifier defaults, same launch path.
* **O6. Commit and apply F3.** Commit the evidence on its own. Report QC02/QC03 host status, `thermal_level_max` and
  load by status and runtime only. Apply F3 mechanically, with no retry.
* **O7. The qualification review (amended).** It runs `--review` on the committed records and checks D1. It also
  checks one thing the code does not: for each decoy record, the wall-clock span `end.epoch_s − start.epoch_s` must
  agree with the raw-clock span within a few seconds. A wall-clock step during a run would distort the
  `time.time()`-based job walls that Q12 reads, and no gate checks it (my plant Q11). The stored fields suffice for
  this check.
* **E1–E4.** Unchanged, and E1/E2 are now written into §14.
  * **E1:** the execution runs under the same host conditions, with thermal level 0 at start.
  * **E2:** host provenance never changes the status, the outcome or exactly-once.
  * **E3:** the execution review reports the sealed host record, now including `thermal_level_max` and the
    ThermalEvent entries.
  * **E4:** `caffeinate_pid` present, or disclosed.

## 7. Notes (none blocks the freeze)

* **N1. Single-point controls.** They are specific now, but each plants one point well past its threshold. Small
  drifts of a constant (M12, M13) and the K-absent reason (M15) are not seen. The constants are byte-identical to r2
  and are bound by the manifest, and the real code handles M15's case (Q1).
* **N2. The QC11 decoy-branch guard.** It checks the minimum line over snapshots and samplers together, so a lone
  late sampler passes it statically. At run time it is caught as uncovered samples.
* **N3. N2's coverage check when the stage walls are absent.** If a decoy record lacks `stage1_wall_seconds`, the
  required span becomes 0 (Q9). The pinned driver always writes it, so this is not reachable for official records.
* **N4. `notifyutil` returns 0 for a key nobody has posted.** I checked with an invented key. So "level 0" is
  meaningful only because this key is live on this host: I observed 1 and 2 today, and so did the coordinator.
* **N5. Decoys.** No decoy value was read. Decoy runs are quoted by status and runtime only. No tail figure appears
  in this file.

## Verdict

F1–F5 hold on the final bytes, and N1, N2, N3 and N6 are applied correctly.

* **M1–M8.** Every one is caught; M6, which escaped in the first review, is now caught.
* **Delta mutations.** M9–M11 and M14 are caught.
* **Regressions.** None.
* **Scope.** Environment only: the caps, Q12's thresholds and the concurrency are unchanged.
* **Honesty.** §14 carries the pre-declared F3 consequences.

The repair may be frozen as r3 under condition D1 (§5). The official run proceeds under O1–O7, and the grant and
execution under E1–E4.
