# P5Y Gate-2C temporal ledger

Non-binding. Ordering is checkable with `git ls-tree` on the named anchor
commit, never by inspecting the working tree.

| anchor | meaning | evidence |
|---|---|---|
| `T0` | preregistration frozen | `GATE2C_PREREGISTRATION.md`, committed with **no** file under `results/` |
| `T1` | code/config hashes frozen | `GATE2C_SOURCE_MANIFEST.json`, same commit; 13/13 pre-T2 structural tests green |
| `T2` | first result-bearing execution | creation of `results/m2_assembly.json` |
| `T3` | all pilot outcomes complete | same artifact (one deterministic run) |
| `T4` | final report | `GATE2C_RESULT.md` |

Pre-T2 corrections, all before any computation and all disclosed: one
`sys.path` ordering fix in `m2_assembly.py`, and three test refinements that
made assertions stricter (matching executable code with comments and docstrings
stripped, rather than raw text). No threshold, drift, `m` value, tolerance,
repeat count or decision rule was touched.
