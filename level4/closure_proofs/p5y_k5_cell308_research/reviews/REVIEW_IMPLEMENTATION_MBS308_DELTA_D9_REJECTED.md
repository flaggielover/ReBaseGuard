# Cell-308 MB-S implementation delta reviewD9: pre-repair immutable candidate
DELTA_REJECTED

Reviewer: reviewD9 (fresh non-holder; no MB r1 run observation supplied)
Date: 2026-10-02

## Candidate and scope

Candidate reviewed: successor commit `9aaaed66e9d00f5b3b2460836ca81ed98fb1446e` (parent
`99616c54a36ee4e94c11097e5ef633016a5eaa5d`), branch
`p5y-k5-cell308-mbs-r1`, clean worktree. The review was limited to brief 58 and reviewF8
sections 4, 5, 8, 9 and 11: D-1 through D-5, G8-1..G8-5, O8-1/O8-3 and T-1..T-3.
No target, measurement, official qualification, freeze, apply, grant, marker, pending,
seal, or host-setup operation was performed.

## Blocking finding

D-1/F8-2 was not operationally repaired. `code/mbs308_measure.py` appended the durable
history record at the fixed namespace path `level4/closure_proofs/p5y_k5_cell308_mbs_r1/ledger/MBS308_SERIES_HISTORY.jsonl`
(line 594) before calling `preflight` (line 595). `preflight` treated every untracked
namespace path as `NAMESPACE_NOT_THE_COMMITTED_BYTES`; this history path was neither
tracked nor ignored. Therefore the first official designation refused immediately after
writing its `started` record, and no official series could run or be re-measured.

## Evidence

The scoped implementation checks and the reported target-free suites did not expose this
ordering defect. Direct source inspection and `git check-ignore`/`git ls-files` established
that the history path was untracked and not ignored. This finding blocked acceptance of
D-1 and consequently the candidate.
