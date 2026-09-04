# P5Y Gate-2C-bis temporal ledger

Non-binding. Ordering checkable with `git ls-tree` on the named anchor commit.

| anchor | meaning | evidence |
|---|---|---|
| `T0` | preregistration frozen | `GATE2CBIS_PREREGISTRATION.md`, committed with **no** file under `results/` |
| `T1` | code/config hashes frozen | `GATE2CBIS_SOURCE_MANIFEST.json`, same commit; 16/16 pre-T2 tests green |
| `T2` | first result-bearing execution | creation of `results/m2b_assembly.json` |
| `T3` | all outcomes complete | same artifact |
| `T4` | final report | `GATE2CBIS_RESULT.md` |

A pre-T0 float calibration of degree-12 Chebyshev tails informed the
preregistration and is disclosed in it; it produced no rigorous claim.

Pre-T2 corrections, all before any result-bearing computation, all disclosed:
three test-authoring fixes (an `ast.Name` attribute error, a non-parseable source
split replaced by a proper AST lookup, and one over-blunt substring match). No
threshold, degree, drift, tolerance, repeat count, cap or decision rule changed.
