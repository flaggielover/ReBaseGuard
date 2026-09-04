# P5Y Gate-2A temporal ledger

Non-binding. Ordering is checkable with `git ls-tree` on the named anchor
commit, never by inspecting the working tree (the P5X `D5`-`D9` standing rule).

| anchor | meaning | evidence |
|---|---|---|
| `T0` | preregistration frozen | `GATE2A_PREREGISTRATION.md`, committed with **no** file under `results/` |
| `T1` | code/config hashes frozen | `GATE2A_SOURCE_MANIFEST.json`, same commit as `T0`; 15/15 pre-T2 structural tests green |
| `T2` | first result-bearing run | creation of `results/sr_precision.json` |
| `T3` | all precision cells complete | same artifact (single run covers the whole grid) |
| `T4` | final report | `GATE2A_RESULT.md` |
