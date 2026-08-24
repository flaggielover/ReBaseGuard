# Frozen projected power audit

Every closure-relevant endpoint must have at least 40 effective blocks. The
event count is fixed at 240 with six-event moving blocks, yielding exactly 40.

| Task | Residual observations train/cal/eval | Calibration projection | Natural projection | Event projection | Gate |
|---|---:|---:|---:|---:|---|
| A — MetroPT-3 | 4,968 / 3,312 / 8,281 | >=103 cycles at ARL 32; >=51 two-cycle blocks | 43 two-observed-day blocks | 40 | PASS |
| B — Online Retail II | 5,265 / 3,510 / 8,775 | >=146 cycles at ARL 24; >=48 three-cycle blocks | 52 one-week blocks | 40 | PASS |

The actual gate is stricter than this projection: calibration must meet its
point tolerance, contain the target inside its dependence-aware 95% interval,
and retain at least 40 effective blocks. Natural scoring after burn-in must
also retain at least 40 complete task blocks. Failure is recorded as
`V3-TASK-UNUSABLE`; the task is not replaced.
