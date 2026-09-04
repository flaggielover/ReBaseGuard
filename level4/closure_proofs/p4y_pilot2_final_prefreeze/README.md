# P4Y FINAL PRE-FREEZE PILOT (PILOT-2)

```text
STATUS  = PILOT, NON-BINDING
BRANCH  = p4y-pilot2-final   (never merged to main)
THIS IS NOT P4Y PRODUCTION.  NOT A P4Y CHECKPOINT A.
NOT PERMISSION TO RE-RUN THE 96-CELL SCIENTIFIC CAMPAIGN.

P4_ORIGINAL_VERDICT     = PARTIAL   immutable
P4X_SUCCESSOR_VERDICT   = FAIL      immutable
P4X_SCIENTIFIC_FAILURES = NONE      immutable
P4Y_PILOT1_VERDICT      = NEEDS_ONE_MORE_PRE-FREEZE_PILOT   immutable
```

Pilot-2 removes the two governance uncertainties Pilot-1 left, and nothing
else: an endpoint frozen mechanically before any result-bearing byte exists,
and a cap measured at production-representative block counts (48–1784, every
stratum an actual P4X stage-1 allocation).

P4X is failed immutable history and is **not present on this branch**.
Pilot-1's namespace `p4y_precision_governance_pilot/` is present but is
**imported read-only** and never modified.

## Layout

| path | content |
|---|---|
| `PILOT2_PREREGISTRATION.md` | the frozen spec — committed with `results/` empty |
| `PILOT2_REPORT.md` | results, comparison, verdict |
| `src/p4y_pilot2/addressing.py` | injective logical addressing, no modulo compression |
| `src/p4y_pilot2/strata.py` | frozen cells, strata, kappa pair, cap grid, budgets |
| `src/p4y_pilot2/rule.py` | the staged rule; cap-independent trajectory recording |
| `src/p4y_pilot2/audit.py` | the independent disposition auditor — the endpoint |
| `src/p4y_pilot2/project.py` | P4Y CPU projection against the frozen acceptance limits |
| `run_phase.py` | calibration / design / validation |
| `build_report.py` | the frozen selection and acceptance criteria |
| `verify_report.py` | re-derives every reported figure from the JSON |
| `tests/` | addressing, rule + auditor, leakage, shard/identity, non-drift |

## Reproduce

```bash
python -m pytest tests -q
python run_phase.py calibration
python run_phase.py design
python run_phase.py validation
python build_report.py
python verify_report.py
```

The frozen Priority-4 package and Pilot-1's verified shard/block modules are
imported read-only; Pilot-2 writes nothing outside this directory.
