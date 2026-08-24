# Frozen power audit

The primary reliability floor is **20 effective blocks** for every
closure-relevant endpoint and policy. It will not be lowered.

Chronological splits are 30% train, 20% calibration, and 50% evaluation after
the frozen preprocessing and causal-lag eligibility rules. Target ARL is a
predeclared 60 hours: 240 observations for 15-minute Task A and 60 observations
for hourly Tasks B/C. All tasks use `m = 20` detector observations.

| Task | Usable | Calibration | Evaluation | Projected calibration blocks | Projected evaluation cycles | Weekly time blocks | Event blocks |
|---|---:|---:|---:|---:|---:|---:|---:|
| A household | 133,503 | 26,701 | 66,751 | 25 | 256 | 99 | 20 |
| B metro | 40,575 | 8,115 | 20,288 | 25 | 253 | 120 | 20 |
| C Beijing | 34,523 | 6,905 | 17,261 | 21 | 215 | 102 | 20 |
| D load backup | 139,584 | 27,917 | 69,792 | 26 | 268 | 103 | 20 |

Projection conventions are conservative and outcome-blind: calibration cycle
blocks use four consecutive cycles; natural-stream endpoints use physical
seven-day blocks (672 observations at 15 minutes, 168 hourly); controlled
endpoints use 120 chronological events and a moving block of six events.

The actual gate is re-evaluated after deterministic preprocessing and
calibration. A primary failing an actual gate is unusable; no threshold, floor,
split, task, or block size may then be tuned to rescue it.
