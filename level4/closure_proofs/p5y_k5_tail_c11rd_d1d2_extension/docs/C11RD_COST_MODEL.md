# C11RD — prospective cost and feasibility

No target science was executed for this estimate. Inputs: symbolic box counts of the frozen cover
and the non-target timings of `evidence/calibration/C11RD_CALIBRATION.json` (runs C3, C4, C5).

## Counts

* Drift sub-blocks: **4** (equal, exact rational tiling of cell 306's block).
* Initial state boxes per sub-block: bands 0–3: `4 s-strips x (4 + 8 + 12 + 16) theta-slices = 160`;
  band 4: `2 axes x 4 = 8`; **168**.
* Refinement: bisection in `(s, theta)` (4 children; band 4: 2), at most **2** levels. Worst case per
  sub-block: `160 x (1 + 4 + 16) + 8 x (1 + 2 + 4) = 3416` box evaluations.
* Per box evaluation: 12 kernel applications `Khat^(i) D_j` (i = 0..2, j = 0..3), 3 sources, 3
  residual Taylor models of order 6 in 3 variables.
* Derivative certificates: one per sub-block (lam0, lam1, lam2 and the propagated D1, D2 bounds); the
  cell values are the two maxima.
* Float proposals: 4 (one per sub-block; 1.9 s at LOW, about 5 s at NT).

## Timings (non-target)

| run | box evaluations | wall | CPU per evaluation |
|---|---|---|---|
| C3 NT, serial | 172 | 1038 s | ~6.0 s |
| C4 LOW, serial (stopped) | 550 | 3022 s | ~5.5 s |
| C5 LOW quarter, 4 workers (shared host) | 200 | 511 s | ~10.2 s |
| frozen runner, `--mode nontarget` on NT, 4 sub-blocks, 5 workers (a pre-hardening build of the same science path; the committed rehearsal repeats it on the frozen code, `evidence/rehearsal/`) | 672 | 1406 s | ~10.5 s |

Planning figure: **10 CPU-s per box evaluation** (the parallel figures, C5 and the runner rehearsal;
the serial ones are 5.5–6 s).

## Estimates for cell 306 (4 sub-blocks, 5 worker processes)

* Expected: 170–200 evaluations per sub-block (C3, C5 needed at most one refinement level on a few
  boxes) → 680–800 evaluations → 6,800–8,000 CPU-s → **about 25–30 min wall**.
* Worst case (every box refined to depth 2): 13,664 evaluations → 136,640 CPU-s → **about 7.6 h wall**
  (9.9 h at 13 s per evaluation).
* Wall-clock cap: **43,200 s (12 h)**, above the worst case. Hitting it ends the run as
  NOT_CERTIFIED (RESOURCE_CAP_WALL); the execution is consumed.
* RAM: about 30 MB resident per worker observed (C5), plus the parent; cap **2 GiB** total resident
  (checked every 30 s over the parent and all workers; exceeding it ends the run as NOT_CERTIFIED,
  RESOURCE_CAP_MEMORY). The host has 8 GiB.
* Arithmetic backend: CPython standard library only (`fractions`, integers); no external package.

## Host

The Mac host (6 cores, 8 GiB, CPython 3.14 framework build) suffices; no server compute is needed
and none is authorized (no AWS, no Vultr; SR/PS1 K1 untouched). The run should be started under
`caffeinate -i` so that idle sleep does not stretch the wall clock; this changes no setting.

## Retry policy

None automatic. The lock is taken before any science and never removed. A run ended by a cap
writes a NOT_CERTIFIED artifact (both targets INSUFFICIENT at comparison). A host fault that kills
the run before its artifact is written leaves the lock; a second execution needs a new,
independently reviewed authorization and is permissible only if no magnitude was ever written or
printed (the log carries counters and timings only). After a valid execution: never.
