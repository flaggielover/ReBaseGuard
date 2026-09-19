# K5 lower front — order-3 information beyond e = 0 (Campaign A) and the m = 5 tail (Campaign B)

Additive namespace. Start frontier `p5y-postk1-frontier` @ `7cb01e38` (coverage map r3 adopted). No frozen, adopted or
historical artifact is modified; AWS SR/PS1 is not touched; `main` is untouched.

| phase | where | state |
|---|---|---|
| A0 reconstruction, blocker map | `phase_a/` (`LOWER_FRONT_BLOCKER_MAP.json`, `LOWER_FRONT_BLOCKER_AUDIT.md`) | done |
| A1 gates (frozen before any forecast) | `config/FEASIBILITY_GATES_A.json` | frozen |
| A2 route comparison / forecasts | `phase_b/ROUTE_COMPARISON.md`, `evidence/forecast_r1/` | done: TC STRONG, D MARGINAL, G/H INFEASIBLE |
| A3 theorem TC + successor | `theorem/THEOREM_TC.md`, `TC_SUCCESSOR_SPEC.md`, `code/tc_*.py` | pre-freeze; review r1 NOT_READY (B1, B2), fixes applied |
| checkpoints | `checkpoints/` | resume aids only, never evidence |
