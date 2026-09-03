# P4X-R0 — variance-reduction and cost-calibration pilot

```text
CLASSIFICATION   = PRE_FREEZE_COST_AND_PRECISION_PILOT
BINDING          = NO
CHECKPOINT_A     = NOT CREATED
P4_ORIGINAL_VERDICT = PARTIAL   (immutable; not reopened, not amended)
P4X_CAMPAIGN     = NOT OPENED
NOVELTY_STATUS   = NOT_ESTABLISHED
LEVEL4_GLOBAL_CLOSURE = NO
```

This is **not** Checkpoint A, not a production run, not a successor result, and
not closure evidence.  It answers one question:

> How much precision can be bought, at what cost, before any P4X binding
> production scope is frozen?

Hard budget 4 CPU-hours.  Measured spend **0.545 CPU-hours**.

## Documents

| file | content |
|---|---|
| `PILOT_REPORT.md` | what was measured and what it means |
| `PRECISION_POLICY.md` | the proposed pre-result precision rule and its cost projections |
| `DRAFT_CHECKPOINT_A.md` | a **draft, not-active** future Checkpoint A |

## Scripts

| script | purpose |
|---|---|
| `run_sizing.py` | pre-pilot cost sizing, so the budget is respected by construction |
| `run_pilot.py` | the five-method comparison, scaling ladders and tail diagnostics |
| `run_bias_checks.py` | admissibility checks for every non-baseline method |
| `run_tail_sweep.py` | tail index of both routes over all 24 (layer, detector, family) |
| `run_precision_policy.py` | the precision rule and the three-tier production projection |
| `run_cut2_cut3_cost.py` | CUT-2 and CUT-3 cost, from existing artifacts only |
| `src/r0_methods.py` | the candidate estimators |

## Results

| file | content |
|---|---|
| `results/sizing.json` | per-configuration cost and straggler overhead |
| `results/pilot.json` | five methods x four configurations, variance ratios, ladders |
| `results/bias_checks.json` | pathwise and distributional admissibility |
| `results/tail_sweep.json` | measured tail index, both routes, 24 configurations |
| `results/cost_calibration.json` | seconds per 1e6 paths, both routes |
| `results/precision_policy.json` | the rule and the three cost tiers |
| `results/cut2_cut3_cost.json` | CUT-2 = NONE, CUT-3 = NEGLIGIBLE |

## What this namespace must never do

* modify, reopen or reinterpret `../../p4_theory_generalization/`, or any
  `P1`-`P9`, `P8R`, `P9R`, `P5X` namespace;
* relabel historical `P4` as anything other than `PARTIAL`;
* create a binding P4X checkpoint or freeze a P4X protocol;
* choose any threshold or sample rule from an observed pass/fail outcome;
* claim novelty, or claim Level-4 global closure.
