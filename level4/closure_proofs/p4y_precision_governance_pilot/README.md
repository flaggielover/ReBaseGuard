# P4Y pre-freeze pilot — precision governance only

```text
STATUS   = PILOT, NON-BINDING
BRANCH   = p4y-prefreeze-pilot   (never merged to main)
P4Y_BINDING_CHECKPOINT_CREATED = NO
P4Y_PRODUCTION_RUN             = NO

P4_ORIGINAL_VERDICT     = PARTIAL   (immutable)
P4X_SUCCESSOR_VERDICT   = FAIL      (immutable, governance failure)
P4X_SCIENTIFIC_FAILURES = NONE      (immutable)
```

This namespace repairs the two governance defects the failed P4X successor
exposed, and calibrates the smallest honest precision-allocation mechanism
that could later be frozen in a P4Y checkpoint.  It does not create that
checkpoint.

P4X is failed immutable history.  It is **not present on this branch** —
`level4/closure_proofs/p4x_generalization_boundary/` does not exist here — so
the pilot cannot read, alter, repair, relabel or overwrite it.

## Layout

| path | content |
|---|---|
| `PILOT_PREREGISTRATION.md` | the frozen pilot spec; fixed before any design or validation replicate |
| `PILOT_REPORT.md` | results, comparison and recommendation |
| `src/p4y_pilot/shard.py` | exact shard partition — the G2 repair |
| `src/p4y_pilot/blocks.py` | worker-free logical block identity and lazy block pools |
| `src/p4y_pilot/rules.py` | the predeclared candidate allocation rules — the G1 repair |
| `src/p4y_pilot/stats.py` | Clopper–Pearson bounds, chi-square inflation |
| `src/p4y_pilot/config.py` | frozen cells, inherited constants, budgets |
| `run_calibration.py` | fixes `r*_pilot` per cell in its own seed namespace |
| `run_pilot.py` | design and validation phases |
| `tests/` | shard-sum, RNG/block identity, estimator non-drift, rule semantics |

## Reproduce

```bash
python -m pytest tests -q          # 130 tests, no simulation beyond a few
python run_calibration.py          # ~0.07 CPU-hours
python run_pilot.py design
python run_pilot.py validation
```

The frozen Priority-4 package is imported read-only from
`../p4_theory_generalization/src`; the pilot writes nothing outside this
directory.
