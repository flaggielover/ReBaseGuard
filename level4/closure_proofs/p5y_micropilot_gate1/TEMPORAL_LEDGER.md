# P5Y Gate-1 temporal ledger

Non-binding. Ordering is enforced by git and by `GATE1_SOURCE_MANIFEST.json`.

| anchor | meaning | evidence |
|---|---|---|
| `T0` | preregistration frozen | `GATE1_PREREGISTRATION.md` committed before any `results/` file exists |
| `T1` | code/config hashes frozen | `GATE1_SOURCE_MANIFEST.json`, same commit as `T0`; pre-T2 identity tests green (11/11) |
| `T2` | first result-bearing execution | first file written under `results/` |
| `T3` | all pilot outcomes complete | `results/` complete |
| `T4` | final report | `GATE1_RESULT.md` |

`T0` and `T1` are the SAME commit and that commit contains **no** file under
`results/`, which is the checkable property (the P5X `D5`-`D9` lesson: assert
against `git ls-tree <anchor>`, never against the working tree).
