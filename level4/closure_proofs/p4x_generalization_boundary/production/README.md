# P4X production campaign

```text
CHECKPOINT          = P4X_CHECKPOINT_A (commit 756bf68), ACTIVE and BINDING
P4_ORIGINAL_VERDICT = PARTIAL   (immutable, never modified by this campaign)
NOVELTY_STATUS      = NOT_ESTABLISHED
LEVEL4_GLOBAL_CLOSURE = NO
```

Execution of the frozen Checkpoint-A specification.  Nothing in this namespace
is a design decision: the estimator, the sample-size rule, the block-size rule,
the caps, the gates and the verdict semantics all come from
`../checkpoint_a/results/checkpoint_a.json`.

## Phases

| phase | content |
|---|---|
| P0 | isolation, then reproduction of the frozen anchors |
| P1 | obligations needing no new simulation: C1, C4, C5, C7 (pre-reading), C6 |
| P2-P5 | C2 correspondence production, cheapest configurations first by cost, the pre-registered high-risk configuration scheduled so it never delays a cap decision |

## Scripts

| script | purpose |
|---|---|
| `run_anchors.py` | re-runs the frozen estimators with the frozen seeds and compares against the recorded artifact |
| `run_p1_zero_compute.py` | C1, C4 (CUT-2), C5 (CUT-3), C7 pre-production reading |
| `run_c6_lean_arb.py` | re-verifies the inherited Lean spine and Arb certificates |
| `run_c2_production.py` | stage-1 correspondence production |
| `run_c2_stage2_adjudicate.py` | stage-2 precision top-up and gate adjudication |
| `run_finalize.py` | C1-C7 ledger, cost ledger, binding verdict |

## Results

| file | content |
|---|---|
| `PRODUCTION_RESULT.md` | the readable production report |
| `production_results.json` | the authoritative C1-C7 ledger and binding verdict |
| `c2_cell_ledger.json` | every one of the 96 theorem-supported cells, in full |
| `cost_ledger.json` | CPU and wall accounting against both caps |
| `anchors.json` | frozen anchor reproduction |
| `p1_zero_compute.json` | C1, C4, C5 and the pre-production C7 reading |
| `c6_lean_arb.json` | Lean and Arb re-verification |
| `c2_stage1.json`, `c2_stage2_plan.json`, `c2_stage2.json` | the two-stage precision acquisition |

`production_results.json` is authoritative where it and the prose disagree.

## Invariants this campaign preserves

* the frozen 3 % accuracy criterion and the `|z| <= 4` criterion are unchanged;
* no variance-reduction method is used;
* Route Q arbitrates nothing and rescues nothing;
* top-up decisions read a route's own achieved standard error and nothing else;
* no threshold, budget, estimator or scope was changed after any result;
* every failed cell is reported, never aggregated away;
* the historical Priority-4 tree is byte-identical throughout.
