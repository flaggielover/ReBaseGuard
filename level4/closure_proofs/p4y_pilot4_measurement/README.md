# P4Y PILOT-4 — heavy-tail precision measurement feasibility gate

```text
STATUS = PILOT, NON-BINDING
BRANCH = p4y-pilot4-measurement   (never merged to main)
NOT production.  NOT a checkpoint.  NOT an allocation-rule pilot.
```

A measurement pilot with **no allocation rule in it**. It asks one question:
can the `t1p5` precision scale be measured stably and affordably enough to
serve as a production sizing and stopping instrument? If not:
`DO_NOT_FREEZE_P4Y`.

Pilot-3 stopped because it asserted a benchmark uncertainty from
`1/sqrt(2(n-1))` for a law in which one block in 8 000 carried 29 % of the
variance. Pilot-4 uses no normal-theory formula anywhere; its benchmark is
admissible only if it passes empirical stability criteria frozen in advance.

## Layout

| path | content |
|---|---|
| `PILOT4_PREREGISTRATION.md` | the frozen spec, committed with `results/` empty |
| `PILOT4_REPORT.md` | results and verdict |
| `src/p4y_pilot4/estimand.py` | the measurement object, defined precisely |
| `src/p4y_pilot4/blocks4.py` | base blocks and exact aggregation to larger sizes |
| `src/p4y_pilot4/design4.py` | frozen grids, thresholds, budget |
| `src/p4y_pilot4/addressing4.py` | inherited addressing, fresh campaign base |
| `run_measure.py` | master (benchmark) then reference (accuracy) |
| `build_gate4.py` | applies the frozen feasibility criterion |
| `verify_report4.py` | re-derives every reported figure from the JSON |
| `tests/` | aggregation identity, estimand, governance regression |

## Reproduce

```bash
python -m pytest tests -q
python run_measure.py master
python run_measure.py reference
python build_gate4.py
python verify_report4.py
```
