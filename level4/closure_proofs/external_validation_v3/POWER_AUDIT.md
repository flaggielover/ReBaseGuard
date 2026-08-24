# Frozen projected power audit

Every closure-relevant endpoint must have at least 40 effective blocks. The
event count is fixed at 240 with six-event moving blocks, yielding exactly 40.

| Task | Residual observations train/cal/eval | Calibration projection | Natural projection | Event projection | Gate |
|---|---:|---:|---:|---:|---|
| A — MetroPT-3 | 3,312 / 4,968 / 8,281 | projected 92 post-burn cycles including fresh-block consumption; 46 two-cycle blocks | 43 two-observed-day blocks | 40 | PASS |
| B — Online Retail II | 3,510 / 5,265 / 8,775 | projected 116 post-burn cycles including fresh-block consumption; 58 two-cycle blocks | 52 one-week blocks | 40 | PASS |

The first projection used 30/20/50 and omitted the mandatory post-alarm fresh
block. It was corrected outcome-blind to 20/30/50 before any policy result.
The actual gate is stricter than this projection: calibration must meet its
point tolerance, contain the target inside its dependence-aware 95% interval,
and retain at least 40 effective blocks. Natural scoring after burn-in must
also retain at least 40 complete task blocks. Failure is recorded as
`V3-TASK-UNUSABLE`; the task is not replaced.
