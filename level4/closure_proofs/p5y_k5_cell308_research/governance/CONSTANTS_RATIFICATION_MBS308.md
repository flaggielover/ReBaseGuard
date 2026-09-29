# Cell-308 successor MB-S r1: non-holder ratification of the untraceable constants (review R3 / DEF-3, T6 M1) — ratifierMBS
CONSTANTS_RATIFIED_WITH_CHANGES

Scope: items 4, 5, 10, 11, 13-16, 18-25, 27, 28, 30, 31 of REVIEW_IMPLEMENTATION_MBS308 s10. The code was read as it
stood on 2026-09-29 22:0x-22:14Z (successor worktree `/Users/suzhe/ReBaseGuard-c308mbs`; `mbs308_driver.py` sha256
7bc2a619…, `mbs308_guard.py` 48903487…, `mbs308_host.py` 21b82c3f…, `mbs308_launch.py` a3310ed8…, `mbs308_state.py`
6a09062c…; the four helper hashes equal the driver's HELPER_SHA256; unchanged during my decoy run). Evidence keys (H*, D*,
Q) are defined in the Evidence section below. **Γ column:** no item can change Γ. Γ comes from MB r1's byte-identical
science on pinned inputs. These constants decide only whether the one evaluation starts, how long it may run, and
whether it is killed, resumed or closed INDETERMINATE. A cap hit is a failure, never a dropped rung. A served checkpoint
is a verified, byte-identical record.

| # | constant (file) | current value | ruling | derivation rule / rationale | evidence | Γ? |
|---|---|---|---|---|---|---|
| 4 | EVAL_CAP application (state `AwakeCap`, driver) | per attempt; CLOCK_UPTIME_RAW; from the marker (attempt 1) or the resume start; hit → SIGALRM → TimeoutError → INDETERMINATE | **ratified** | (a) A resumed attempt recomputes only jobs with no verified checkpoint, so its work is at most the uninterrupted evaluation's. A per-attempt cap therefore never fails a resumed evaluation that would have passed uninterrupted. A cumulative cap would charge a lost attempt's work twice. (b) Awake time: during sleep the computation is frozen, so sleep time is not compute time. UPTIME_RAW (mach_absolute_time) stops in sleep and MONOTONIC_RAW (mach_continuous_time) does not; their difference is MB r1's channel K. (c) Bounded: at most (1 + MAX_RESUMES) × 8 h = 32 h awake, inside the 168 h DEADLINE. The user's MBS-8 text must state this (the review's D10 note). | H2: MONOTONIC_RAW − UPTIME_RAW = 0 and kern.sleeptime 0 (no sleep since boot), so consistent. The sleep exclusion itself rests on the clocks' documented semantics and is not exercised, as the review said. Q: a full 5-block decoy at 5 workers is 1.94 h awake. C. | completion only |
| 5 | AwakeCap poll (state) | min(5 s, max(0.01 s, cap/20)); 5 s in production | **ratified** | Hit latency ≤ poll. 5 s / 28 800 s = 0.017 % of the cap, and the rule is ≤ 0.1 %. The cap/20 term keeps the relative latency ≤ 5 % for the tests' 2 s caps (0.1 s). Cost: one thread wake-up every 5 s. | C; H2 (clock reads are cheap and local) | completion only (hit latency) |
| 10 | MEM_CAP_BYTES (driver) | 3 GiB (provisional) | **set-by-rule-at-freeze (R-MEM)**; provisional 3 GiB **ratified** only for the pre-freeze build and as the *measurement* cap of the official decoys | Frozen value = R-MEM output. The provisional cap must not cut off the rule's own input: an official decoy with any watchdog event is not a valid R-MEM input (R-MEM step 1). On this host: 3 GiB + 4 × 95.6 MB + 55.5 MiB = 3.41 GiB ≤ 8 GiB − 1.80 GiB wired = 6.2 GiB, so it is safe for measurement. R-MEM on tonight's dev inputs gives **1 GiB** (max(3 × 95.6 MB, 1 GiB)). That is a dev figure; the frozen-ladder rungs RLR d6/d8, C2B N40/N80 and C1B d8-12 are unmeasured. | D1, D0, H1 | completion only (a kill → INDETERMINATE) |
| 11 | memory-cap freeze rule (protocol s8) | max(3 × largest official-decoy per-job peak RSS, 1 GiB) | **changed-to R-MEM** (made stricter, not looser) | Changes: (i) P is the *true* peak. Per job it is the larger of ru_maxrss and the watchdog's ps peak. The 2 s ps watchdog saw 73.8 MB while the C2B job's ru_maxrss was 95.6 MB, so sampling under-reads. (ii) The factor adapts to the observed spread: k = max(3, 2s). (iii) Round up to 256 MiB. (iv) A host upper-bound feasibility check, which fails the qualification rather than silently lowering k. (v) Decoys with a watchdog event are invalid. Why factor 3: the same job varied ≤ 1.09× from run to run (D0 vs D1), and 3 leaves ≥ 2× beyond that for decoy-to-target variation at identical rungs. Why a 1 GiB floor: it is ≥ 10× the interpreter-plus-science baseline (VER job 40.8 MB) and absorbs allocator noise. | D1, D0, H1 | completion only |
| 13 | MEM_POLL_S (driver) / Ctx default | 2.0 s | **ratified** (re-checked by R-MEM step 6 at qualification) | Cost: 1.9 ms CPU per `ps -o pid=,rss=` call, i.e. 0.1 % of one core at 2 s. Overshoot past the cap before the kill ≤ g × 2 s = 98 MB at the highest growth rate observed (g = 49.2 MB/s). That is ≤ 10 % of the 1 GiB floor, but borderline, hence the step-6 re-check. Sampling can only under-read a peak, so the poll never causes a spurious kill. | H2 (ps latency and CPU), D1 (growth rate) | completion only |
| 14 | FREE_MEM_MIN_BYTES (driver) | 2 GiB (vm_stat free + inactive + speculative + purgeable) | **set-by-rule-at-freeze (R-FREE)**; provisional 2 GiB **ratified** (it equals R-FREE's output on tonight's inputs) | Headroom at start must hold the worst admissible state: one worker at the kill line, four at peak, plus the driver: 1 GiB + 4 × 95.6 MB + 55.5 MiB = 1.41 GiB, so the 2 GiB floor applies. The rule also requires attainability to be shown at qualification. Tonight, with the user's apps open, this host has **1.54-1.70 GiB**, so the gate refuses (as the review's NOTE 10 said). | H1, D1 | start gate only |
| 15 | EXCL_CPU_PCT (driver) | 25 % | **ratified** as the frozen value, with the single bounded exception of R-EXCL-PCT | WORKERS 5 on hw.ncpu 6 (2 P + 4 E cores) leaves one spare core. Compute processes read about 99 % (the decoy workers' median was 99.1 %). Idle user apps read ≤ 21.4 % and the hosting app ≤ 17.6 %. 25 % separates the two groups with margin on both sides. It is also ≤ half a worker's reading, so a process computing like a worker is always refused. | H3, D1, H1 | start gate only |
| 16 | EXCL_ALLOW (driver) | **39** macOS process names in the code as read. The review says 41; the list may have been edited. | **changed**: set-by-rule-at-freeze (R-ALLOW). Provisional for tonight's build: the 39 ∪ {`spotlightknowledged.updater`, `cloudd`, `BackgroundShortcutRunner`, `modelcatalogd`} | All 35 members that are running are Apple system binaries under /System, /usr/libexec, /usr/sbin or /sbin (H4), so they are **ratified as members**. The other 4 (kernel_task, mdworker, hidd, spindump) are not printed or not running now. **But** each of three snapshots had at least one Apple OS daemon above 25 % that is not on the list. The gate as built refuses on processes the operator cannot quit, and a start-time snapshot of on-demand OS daemons protects nothing over an 8 h run. User apps (Perplexity, Electron, …) and the hosting app stay **off** the list: the operator quits them, and builder gap 8 stands. | H3, H4 | start gate only |
| 18 | MAX_RESUMES (state) | 3 (attempt ≤ 4) | **ratified** | An interruption is either transient (host reset, app death, power loss; independent across attempts) or deterministic (it repeats every attempt). A cap or watchdog kill is a failure (D5), not an interruption. With transient probability p per attempt, P(never completing) = p⁴: ≤ 6.3 % even at a pessimistic p = 0.5, and ≤ 0.4 % at p = 0.25. A fifth attempt would gain ≤ 3 pp at p = 0.5, ≤ 0.3 pp at p = 0.25, and nothing against a deterministic cause, which shows by attempt 2. Each extra attempt costs up to 8 h awake and lengthens the no-update window. | Q (a decoy-sized evaluation is 1.94 h awake, so four attempts fit in the window); C | completion only |
| 19 | DEADLINE_S (state) | 7 days after the marker | **ratified** | Lower bound: 4 × 8 h = 32 h of awake work, plus up to about 3 days for the operator to notice an interruption over a weekend (resume is operator-launched), is about 4.3 days. Upper bound: the no-automatic-install window (marker to deadline) should stay a bounded exposure, about one Rapid-Security-Response cadence. A platform change is terminal anyway (DR2 b). 7 days satisfies both. | H1 (SU keys; build 25F84), Q | completion only |
| 20 | CKPT_FAIL_LIMIT (state) | 2 consecutive verification failures of one job | **ratified** | Git objects and refs are written atomically (tmp + rename, fsync configured). A checkpoint that fails verification therefore signals a defect or corruption, not a normal torn write. One such failure is recomputed (never served); a second consecutive one stops before computing. Non-blocking note (the review's D4 note): as implemented, a bad blob that is not rewritten before the next interruption is counted again. Counting once per distinct failing blob id would match the rule's letter and remove that double count (builder's choice). Under either counting, 2 is the right value. | C | completion only |
| 21 | Lock retries (state `Lock.acquire`) | 4 | **ratified** | Breaking a stale lock needs 2 passes: move aside, then O_EXCL create. 4 passes tolerate one vanish race and one concurrent breaker. Beyond that the right answer is the clean LOCK_RACE refusal: nothing is written and the operator re-runs `recover`. | C | lifecycle only |
| 22 | Worker parent-death watch (state) | 1 s | **ratified** | An orphaned worker lives ≤ 1 s after the driver dies. That is ≤ 1 CPU-s and ≤ about 49 MB of growth at the highest observed rate, far below the seconds a `status` plus a launchd bootstrap of a resume take, so no orphan competes with a resume. Cost: one wake-up per second per worker. | D1 (worker ≈ 99 % CPU, growth rate); C | lifecycle only |
| 23 | MIN_FREE_DISK (host) | 2 GiB on the repository volume | **ratified** | The campaign's writes (checkpoints, result, journal, logs) are MB-scale: MB r1's whole 5-block decoy record is 1.6 MB, so even 4 attempts need ≪ 100 MB. The rest of the margin is for macOS swap growth, which comes in 1 GiB swapfile steps: tonight 3 GiB was allocated with 1.8 GB used, and a full disk invites jetsam kills. 2 GiB = one swapfile step plus ≥ 10× the artifact need. | Q (file sizes), H1 (swap; 170 GB free) | start gate only |
| 24 | MEMORY_PRESSURE_NORMAL gate (host) | `kern.memorystatus_vm_pressure_level` = 1 required | **ratified** | Encoding: 1 normal, 2 warn, 4 critical (dispatch levels). Starting at warn or critical means starting into compression and swap. The gate is start-only: after the marker the level is only recorded. | H1 read **2** (memorystatus_level 41, 1.8 GB swap used); H2 read **1** six minutes later. This confirms both the encoding and the variability. | start gate only |
| 25 | lowpowermode gate (host) | 0 required | **ratified** | Low Power Mode lowers clocks, so the evaluation runs slower and risks EVAL_CAP. The gate costs nothing. | H1 (`pmset -g`: lowpowermode 0, AC Power) | start gate only |
| 27 | SU_GATING_KEYS (host) | AutomaticallyInstallMacOSUpdates, CriticalUpdateInstall (missing = enabled) | **ratified** | These are the two keys whose automatic installation can change the pinned OS build (macOS updates and Rapid Security Responses). AutomaticDownload only downloads. ConfigDataInstall installs security data files, which change neither `sw_vers -buildVersion` nor the Python framework bytes. The platform re-check at every resume is terminal on any change. This host is not DEP- or MDM-enrolled and has no /Library/Managed Preferences, so the user keys are authoritative (the review's NOTE 6, checked). Tonight **all four keys are 1**, so `execute` refuses until the user sets the two gating keys to 0 (user action). Gating all four would be stricter and harmless (builder's option). | H1, H2 | start gate only |
| 28 | caffeinate supervisor (host) | poll 0.2 s / spawn-failure backoff 0.5 s / respawn delay 0.05 s / stop join 10 s / terminate wait 5 s | **ratified** | Gap after a caffeinate death ≤ poll + respawn delay + spawn ≈ 0.25 s. The host's idle-sleep timer is 60 s (`pmset -g`: sleep 1), a ≥ 200× margin. The 0.5 s backoff bounds a failing spawn loop to 2 attempts per second. Stop join 10 s ≥ one backoff plus one spawn; terminate wait 5 s, then SIGKILL (shutdown only). Lid-close sleep is outside caffeinate's reach and is recorded by channels K/S/L, not by these timings. | H1 (sleep timer); C (I spawned no caffeinate) | completion only (sleep prevention) |
| 30 | launchctl print timeout (host) | 30 s | **ratified** | Measured latency is 2.9-9.2 ms, a ≥ 3000× margin; the timeout only bounds a hung launchd query. Its consequence (None = "not running") must never boot out a live job, but that is R2 / DEF-2, not this value. | H2 | launch / wait only |
| 31 | launcher waits (launch) | bootstrap wait 15 s / wait poll 2 s / preflight timeout 1900 s | **ratified**; 1900 s is recorded **as a rule**: PRE_CAP_S + 100 s | 1900 = PRE_CAP 1800 + 100, so the driver's own PRE_CAP refusal always comes before the launcher's kill. The driver's alarm interrupts a blocking subprocess at once (the exception kills the child), and the longest measured preflight-path subprocess is 1.56 s. If PRE_CAP changes, this value follows. The 15 s bootstrap wait is ≫ launchd's RunAtLoad start: launchctl answers in ms, and the builder's synthetic launches passed 6/6. The 2 s wait poll costs about 4 ms per call (0.2 % of a core) and only delays cleanup. | H2, C | launch only |

## Written rules (to be applied at the freeze from the official qualification evidence; never from any target run)

**R-MEM (MEM_CAP).**
1. *Inputs.* The OFFICIAL decoy runs of the MB-S qualification: the real driver's `decoy` under the launchd launcher,
   frozen ladder, WORKERS 5, the decoy cells of the qualification plan. Each runs with the provisional cap (3 GiB) and
   MEM_POLL_S 2 s. A decoy with any memory-watchdog event is **not a valid input**. It is re-run with the provisional
   cap doubled, within the step-5 bound.
2. P = max over every job of every valid official decoy of max(`job_maxrss_bytes` [ru_maxrss of the job's fresh worker],
   `worker_peak_rss_bytes` [watchdog ps]). D = the driver's own peak RSS in those runs (the qualification records
   ru_maxrss of RUSAGE_SELF).
3. s = max over each (kind, rung) that appears in two or more valid runs of (largest peak / smallest peak). s = 1 if no
   rung appears twice.
4. **MEM_CAP = roundup_256MiB(max(k × P, 1 GiB)), k = max(3, 2s).**
5. *Feasibility (host readings at qualification).* MEM_CAP + (WORKERS − 1) × P + D ≤ hw.memsize − W_idle, where W_idle
   is vm_stat "wired down" × page size in the prepared idle state. If violated, the qualification **fails on memory**.
   k, WORKERS and the floor are never reduced silently.
6. *Poll re-check.* g = the highest RSS growth rate seen by a ≤ 0.5 s qualification sampler. Require
   g × MEM_POLL_S ≤ 0.1 × MEM_CAP; otherwise MEM_POLL_S = max(0.5 s, 0.1 × MEM_CAP / g).

Tonight, on dev inputs (D1): P = 95.6 MB, D = 55.5 MiB, s = 1.09, k = 3, so MEM_CAP = 1 GiB. Feasibility: 1.41 GiB ≤ 6.2
GiB, pass. Poll: 98 MB ≤ 102 MB, pass (borderline).

**R-FREE (FREE_MEM_MIN).** FREE_MEM_MIN = max(2 GiB, roundup_256MiB(MEM_CAP + (WORKERS − 1) × P + D)), with the R-MEM
values. It is measured as the driver's own `free_memory_bytes` (vm_stat free + inactive + speculative + purgeable).

*Attainability.* The qualification records ≥ 10 readings, 30 s apart, of the prepared host (AC power, the operator's
apps quit, the hosting app idle). At least 3 consecutive readings must reach FREE_MEM_MIN. Otherwise it records
GATE_UNATTAINABLE: `execute` cannot start on this host, and the value is never reduced silently.

**R-EXCL-PCT (EXCL_CPU_PCT).** EXCL_CPU_PCT = 25. There is exactly one exception. If the hosting app that runs the
launcher, which cannot be quit, exceeds 25 in any prepared-state reading, then EXCL_CPU_PCT = min(50,
roundup_5(1.25 × its maximum reading)). The ceiling of 50 is half the median official-decoy worker reading (about 99),
so a process computing like a worker is always refused. Any other process above the threshold must be quit (or pass
R-ALLOW); it is never a reason to raise the threshold.

**R-ALLOW (EXCL_ALLOW).** The frozen list = the current 39 names ∪ the basename (`comm.rsplit('/')[-1]`, as
`busy_processes` computes it) of every process that meets both conditions:
- (a) it exceeds EXCL_CPU_PCT in any prepared-state qualification reading (≥ 10, 30 s apart) or in this ratification's
  H3 readings;
- (b) its executable path lies under `/System/`, `/usr/libexec/`, `/usr/sbin/`, `/sbin/` or `/Library/Apple/`
  (SIP-protected OS locations).

Never added: anything under `/Applications`, `/Users`, `/opt`, `/usr/local`, `/Library/Frameworks`, `/usr/bin` or
`/bin` (tools a user can invoke), any Python interpreter, or the hosting app. Each addition is recorded with its path
and reading.

*Recommended (builder's option; completion only):* implement (b) as a path test in `busy_processes` instead of a name
list. A basename can be reused by a user binary; a path under a SIP location cannot.

## Evidence (all taken tonight by me unless stated; host readings strictly read-only)

* **H1**: 2026-09-29T22:02:11Z (`sysctl`, `vm_stat`, `pmset -g`, `pmset -g batt`, `defaults read`, `df`, `sw_vers`).
  - Hardware: hw.memsize 8 GiB; hw.ncpu 6 (perflevel0 2, perflevel1 4); Mac17,5; build 25F84.
  - Memory: memory pressure level 2, memorystatus_level 41, swap 1798.81M used of 3072M.
  - vm_stat: page size 16 KiB; free + inactive + speculative + purgeable = 1.61 GiB; wired 117 937 pages = 1.80 GiB.
  - pmset: lowpowermode 0; sleep 1 (minute); AC Power, charged.
  - SoftwareUpdate: AutomaticallyInstallMacOSUpdates / AutomaticDownload / CriticalUpdateInstall / ConfigDataInstall
    all 1.
  - Disk: data volume has 170 GB available.
* **H2**: 2026-09-29T22:08:10Z.
  - Clocks: MONOTONIC_RAW − UPTIME_RAW = −2e-7 s; kern.sleeptime / kern.waketime 0.
  - Latencies, median / max: `ps -o pid=,rss= -p …` 2.3 / 3.6 ms, with 1.9 ms child CPU per call; `launchctl print
    gui/501` 3.8 / 9.2 ms; `launchctl print` of an absent campaign label 2.9 / 4.8 ms (rc 113); `ps -A -o
    pid=,ppid=,pcpu=,comm=` 13 / 17 ms; `vm_stat` 1.4 / 4.5 ms; `pmset -g` 6 / 11 ms; `pmset -g log` 1.56 s.
  - memory pressure level 1.
  - No `/Library/Managed Preferences`; `profiles status -type enrollment`: DEP No, MDM No.
* **H3**: three `ps -A -o pid=,ppid=,pcpu=,rss=,comm=` snapshots, 22:04:46Z / 22:05:06Z / 22:05:26Z.
  - Above 25 %: spotlightknowledged.updater 70.3 (`/usr/libexec`); cloudd 30.5 (`/System/…/CloudKitDaemon.framework`);
    BackgroundShortcutRunner 32.9 and 52.2 (`/System/…/WorkflowKit.framework/XPCServices`); modelcatalogd 27.7
    (`/System/…/ModelCatalogRuntime.framework`). None is in EXCL_ALLOW, so the gate as built refuses at all three.
  - Below 25 %: largest user app 21.4 (Perplexity); hosting app (Claude Code CLI) ≤ 17.6; WindowServer ≤ 23.9
    (allow-listed).
* **H4**: path class of the 39 EXCL_ALLOW names on this host. 35 are running, all under /System, /usr/libexec,
  /usr/sbin or /sbin. kernel_task, mdworker, hidd and spindump are not listed by a non-root `ps` at that moment.
* **D1**: my dev decoy (ledger NONTARGET_DRIFT_VALIDATION 22:08:36Z).
  - Run: `mbs308_driver.py decoy --cell 297 --first-blocks 1 --dev-ladder --workers 2 --out <scratch>`, from the
    successor worktree with the pinned interpreter, 22:08:58Z-22:10:59Z; rc 0.
  - Timing: stage 1 116.7 s, wall 119.5 s, worker CPU 155.9 s.
  - Per-job ru_maxrss: RLR d4 73.8 MB, C1B d4 70.7 MB, C2B N20 95.6 MB, VER d4 40.8 MB.
  - Watchdog (2 s ps): worker peak 73.8 MB, no events, cap 3 GiB.
  - My independent 0.5 s ps sampler: driver peak 55.5 MiB; worker peak 83.2 MiB; highest RSS growth 49.2 MB/s; compute
    worker pcpu median 99.1 %.
  - Host during the run: vm available 1.54-1.70 GiB; assessment CLEAN, sleep gap 0, thermal max 1.
  - Output (decoy values) is kept only in my scratch and is never juxtaposed with any tail-cell number.
* **D0**: the builder's dev decoy, same configuration, figures as printed in BUILD_REPORT s3: C2B 87.5 MB, RLR 72.3 MB,
  C1B 70.3 MB, VER 40.3 MB. Same-job run-to-run spread against D1 ≤ 1.09×.
* **Q**: MB r1's official **pre-grant** qualification decoys at r3 (`p5y_k5_cell308_mb_r1/qualification/`). I read
  resource fields only (wall, CPU, per-rung wall, host assessment); no science value was read.
  - QC02, decoy 297, all 5 blocks, 5 workers, frozen ladder: wall 6977 s (1.94 h); worker CPU 23 591 s; largest single
    rung wall 3380 s (RLR); file 1.6 MB.
  - QC03, decoy 316, blocks 0-2, 1 worker: 11 672 s.
  - Both host assessments CLEAN, sleep gap 0.
  - MB r1 recorded no RSS.
* **C**: code reading of the successor as stated in the header.

## Non-holder statement and disclosure

I read none of the MBS-2 files (no REVIEW_EXECUTION_INTERRUPTION*, no audit/EXECUTION_INTERRUPTION_*, no
REVIEW_SUCCESSOR_GOVERNANCE_308*, no INCIDENT_INDEPENDENCE_REVIEW_MBS308*, no COORDINATOR_EXPOSURE_DISCLOSURE, nothing
under `p5y_k5_cell308_mb_r1/{review,adjudication,postexec}/`). BUILD_REPORT section 9 was filtered out of every read.

**One inadvertent exposure, disclosed.** A routine `git log --oneline -5` in the successor worktree displayed the
one-line subject of MB r1's postexec commit 21e99cf0. That subject carries a qualitative chronology and no per-job
runtime, memory, host or science figure. No ruling here uses it, and I do not repeat it.

Nothing evaluated cells 305-309 or any drift in [6/5, 13/5] or its mirror; my only computation was the decoy above
(cell 297; the driver's guard refuses the band). I made no git writes, edited no code file, changed no system setting
and spawned no caffeinate. Every host reading was read-only; `memory_pressure(1)` was deliberately not run, because it
can apply pressure, and sysctl was used instead.

Items 1-3, 6-9, 12, 17, 26, 29 and 32 were traced to (a)-(c) by the review and are outside this ratification.

**Changes requested of the builder** (all completion-only, none blocking any other condition):
1. Adopt R-MEM, R-FREE, R-EXCL-PCT and R-ALLOW in the protocol's s8 text. Freeze MEM_CAP_BYTES, FREE_MEM_MIN_BYTES,
   EXCL_CPU_PCT and EXCL_ALLOW as the rule outputs, with the inputs recorded in the qualification.
2. Tonight's provisional EXCL_ALLOW = the 39 ∪ {spotlightknowledged.updater, cloudd, BackgroundShortcutRunner,
   modelcatalogd}.
3. Record the launcher's preflight timeout as PRE_CAP_S + 100 s.
4. Optionally: the path-class test for R-ALLOW (b), and per-blob counting for CKPT_FAIL_LIMIT (the review's D4 note).

Ledger (agent `ratifierMBS`): REVIEW 2026-09-29T22:02:02Z (reading); NONTARGET_DRIFT_VALIDATION 22:08:36Z (dev decoy
297); REVIEW (this ratification, logged on writing).
