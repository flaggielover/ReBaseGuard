# MB308 r2 official qualification: FAIL assessment (coordinator; not independent)

* **Run.** Freeze r2 `29b68d5e`. Official mode, heavy cases recomputed. 2026-09-29 00:11:03Z to 04:54:07Z.
* **Evidence commit.** `d031dad8` on `p5y-k5-cell308-mb-r1`. It contains the qualification files only, the same layout
  as r1's `3a05aef7`.
* **Result.** `QUALIFICATION FAIL`, `QUAL_EXIT=1`, `target_evaluations` 0.
* **Gates.** Every case and gate passed except **`Q12_caps`**: QC01–QC13, Q1 and Q8.
* **Status.** Only runtime and status fields are quoted here (incident review C7(b)). No certified decoy value was
  read.

## 1. What Q12 found

Protocol §3.2 requires two things of the frozen caps. EVAL_CAP must be at least ⌈1.5 × projection⌉. Every per-job
cap must be at least 2 × the official maximum wall time of its kind and rung. Both are measured on the official
QC02/QC03 runtimes.

| item | frozen cap (s) | official max wall r2 (s) | needed (s) | r1 official max wall (s) |
|---|---|---|---|---|
| EVAL_CAP | 28 800 | projection 28 495 | 42 743 | projection 18 072 (needed 27 108; passed) |
| C1b d10 | 1 800 | 2 431.0 (that job used 57.6 CPU-s) | 4 862 | 192.7 |
| RLR d6 | 4 200 | 3 471.2 | 6 943 | 1 803.2 |
| RLR d8 | 8 700 | 4 876.6 | 9 754 | 4 149.9 |

Every other per-job cap passed, and every job was CERTIFIED. No block had an alarm or an unadmitted C2b rung.

## 2. Cause: the host slept during the official run

The macOS power log (`pmset -g log`, local time +0900) shows two sleeps:

* **First sleep.** Clamshell sleep at 10:31:29, then dark wakes, "Dark Wake Thermal Emergency" sleeps and maintenance
  sleeps. Full wake at 10:58:43, on the lid and user activity. Asleep about 27 min (01:31–01:58Z).
* **Second sleep.** Clamshell sleep at 12:51:12, then maintenance sleeps. Full wake at 13:42:03, on the lid and user
  activity. Asleep about 51 min (03:51–04:42Z).

`caffeinate -i` prevents idle sleep only, not lid-close sleep. Wall time kept running through both sleeps and no CPU
was spent:

* The C1b d10 job on block 0 of 316 took 2 431 s of wall time for 57.6 CPU-s. It overlaps the second sleep.
* The RLR d6 jobs of 297 overlap the first sleep.
* RLR d8 on block 1 of 316 overlaps the first sleep.

The per-kind maxima feed the projection, so EVAL_CAP inherits the inflation.

Some inflation comes from the qualification's own load and is present in r1 too. While QC02 runs, 7 to 10 CPU-bound
processes share 6 cores.

**Correction to the coordinator's status report of 02:15Z.** That report put the slowdown down to CPU contention
(load average about 94). The load spike came right after the 10:58 wake. The main r2-specific cause is the two sleeps.

## 3. What this is not

* It is not a defect of the science, the criterion, the exactly-once machinery or the guard. Everything else passed:
  QC01–QC11 and QC13, the QC12 leak scans, QC04 determinism, QC08 and the Q8 manifest.
* It is not a target event: 0 target evaluations and no 308 value anywhere.
* The margin is thin even without the sleeps. r1 needed 27 108 s against a cap of 28 800 s. RLR d8 at r1's 4 149.9 s
  needs 8 300 s against a cap of 8 700 s. So the frozen caps leave little room for the one evaluation even on an
  awake host. That is the risk Q12 exists to catch.

## 4. Consequence

* By protocol §3.2 and line 148, caps never change after a freeze. Freeze r2 cannot be qualified, and re-running the
  same freeze to get a PASS would be qualification shopping.
* The campaign is stopped before the target. That follows the user's C4 ruling point 7 and protocol §10.
* Any continuation needs a new freeze (r3) with its own full official qualification and a fresh independent review.
  Whether to make one is put to the user.
