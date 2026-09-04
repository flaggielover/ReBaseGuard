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

## T1 re-freeze (pre-T2)

A first attempt to launch `m1_raw_2cell.py` aborted at **import time** with
`ModuleNotFoundError: rebaseguard_certify` — one missing `sys.path` entry. No
computation ran, nothing was written under `results/`, and no threshold, cell,
degree, rule or metric changed. `T2` ("first result-bearing execution") had
therefore not been reached, so the fix is a pre-T2 correction, recorded here
rather than silently applied. `GATE1_SOURCE_MANIFEST.json` carries the new hash
and the reason.
