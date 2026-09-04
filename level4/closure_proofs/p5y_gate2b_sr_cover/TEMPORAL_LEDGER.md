# P5Y Gate-2B temporal ledger

Non-binding. Ordering is checkable with `git ls-tree` on the named anchor
commit, never by inspecting the working tree.

| anchor | meaning | evidence |
|---|---|---|
| `T0` | preregistration frozen | `GATE2B_PREREGISTRATION.md`, committed with **no** file under `results/` |
| `T1` | code/config hashes frozen | `GATE2B_SOURCE_MANIFEST.json`, same commit; 15/15 pre-T2 structural tests green |
| `T2` | first result-bearing evaluation | creation of `results/sr_cover.json` |
| `T3` | all cover measurements complete | same artifact (one deterministic run) |
| `T4` | final report | `GATE2B_RESULT.md` |

Cost calibration (0.397 s per minorant evaluation at `cells = 200`) was measured
**before** `T0` on the historical R1 **CUSUM** minorant, so it produced no SR
result and did not touch the frozen grid.
