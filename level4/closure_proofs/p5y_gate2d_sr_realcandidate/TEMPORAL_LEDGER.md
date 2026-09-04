# P5Y Gate-2D temporal ledger

| anchor | meaning | evidence |
|---|---|---|
| `T0` | preregistration frozen | `GATE2D_PREREGISTRATION.md`, committed with **no** file under `results/` |
| `T1` | code/config hashes frozen | `GATE2D_SOURCE_MANIFEST.json`, same commit; 20/20 pre-T2 tests green |
| `T2` | first result-bearing execution | creation of `results/sr_realcandidate.json` |
| `T3` | all frozen precision cells complete | same artifact |
| `T4` | final report | `GATE2D_RESULT.md` |

Pre-T0 calibration (disclosed in the preregistration, float and one timing
probe, producing no rigorous claim): degree-16 Chebyshev tails per chart, the
genuine candidate's coefficient mass, and the cost of one rigorous
`acb.integral` (`0.0244` CPU-s).

Pre-T2 corrections, before any result-bearing computation: two test-authoring
fixes (an `arb`-to-`float` exact comparison, and a blunt integer-literal scan
replaced by an AST check that every `run_cell` precision comes from the frozen
grid). No threshold, patch, degree, precision, tolerance, repeat count or cap
changed.
