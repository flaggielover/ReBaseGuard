# P4Y PILOT-3 — heavy-tail Stage-1 sizing closure pilot

```text
STATUS = PILOT, NON-BINDING
BRANCH = p4y-pilot3-heavy-stage1   (never merged to main)
NOT P4Y PRODUCTION.  NOT A BINDING CHECKPOINT.
NOT PERMISSION TO RUN THE 96-CELL SCIENTIFIC CAMPAIGN.
```

Pilot-2 closed every governance question but one. Pilot-3 answers only that
one: how to size the initial production allocation for the frozen heavy-tail
class without systematically underestimating the requirement.

The repair under test: enforce a minimum heavy-tail reference block count,
and size Stage 1 from a one-sided UPPER confidence bound on `relSE_ref`
instead of its point estimate — whose median sits below the truth for a
heavy-tailed scale, which is precisely what Pilot-2 measured.

Everything after Stage 1 is Pilot-2's staged rule and auditor, imported
read-only and unchanged. P4X is absent from this branch. Pilot-1's and
Pilot-2's namespaces are present, imported read-only, and unmodified.

## Layout

| path | content |
|---|---|
| `PILOT3_PREREGISTRATION.md` | the frozen spec, committed with `results/` empty |
| `PILOT3_REPORT.md` | results, comparison, verdict |
| `src/p4y_pilot3/ucb.py` | the one-sided upper-bound constructions |
| `src/p4y_pilot3/sizing.py` | Stage-1 sizing; one rounding, at the logical total |
| `src/p4y_pilot3/strata3.py` | frozen strata, grids, mixture, thresholds, budget |
| `src/p4y_pilot3/projection3.py` | P4Y cost projection on the real 8:40 mixture |
| `src/p4y_pilot3/addressing3.py` | Pilot-2's addressing, fresh campaign base |
| `run_phase3.py` | benchmark / design / validation |
| `build_report3.py` | the frozen selection and acceptance criteria |
| `verify_report3.py` | re-derives every reported figure from the JSON |
| `tests/` | UCB, sizing, and the inherited governance regression battery |

## Reproduce

```bash
python -m pytest tests -q
python run_phase3.py benchmark
python run_phase3.py design
python run_phase3.py validation
python build_report3.py
python verify_report3.py
```
