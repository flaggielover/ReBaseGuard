# P4Z production-layer notes — decisions taken before any result was seen

Companion to `CAMPAIGN_GOVERNANCE.md`.  Everything here was fixed before the
first result-bearing byte and is recorded so that a reader can tell which
choices were made blind.

## 1. The Mac as a result-bearing host

```text
P4Z_NUMERICAL_HOST  = LOCAL_MAC
AWS_CPU_USED_BY_P4Z = 0
campaign isolation  = MAC_ONLY
```

The AWS node's CUSUM Aux4 campaign was verified alive read-only before, during
and after this work.  No P4Z process ran there, nothing in its authoritative
worktree was modified, and its branch head did not move.

Full runtime identity is in `MAC_RUNTIME.md` and
`production/mac_runtime_contract.json`.

## 2. Three cost-model corrections, all conservative

**The full-run CPU projection over-counts the FD ladder.**  `_project_cpu`
scales a configuration's Stage-0 CPU by `200/20 = 10`, but the FD ladder runs a
fixed 20 blocks and is never scaled.  So the projection charges the ladder ten
times over.  This makes kill gate `K4` (budget exclusion) fire *earlier* than
the true cost warrants, which is the safe direction, and it is left uncorrected
because changing the driver after blocks exist would invalidate the producer
hash and discard the run.  Actual cost is accounted from measured CPU-seconds,
never from this projection.

**The `T_B` truncation term widens the uncertainty and so makes the `z` gate
easier, not harder.**  That is the statistically correct direction — attributing
a known deterministic Route-B truncation residual to Monte Carlo noise inflates
`z` spuriously, which is finding F-06 in a different place.  The guard against
`T_B` masking a genuine disagreement is kill gate `K7`: if the Richardson value
drifts by more than 2 % relative between the `(0.2, 0.1)` and `(0.05, 0.025)`
pairs, RB-MAP is declared unusable on that configuration and its cells are
`INCONCLUSIVE`, never `PASS`.  The 3 % relative gate compares point estimates
only and is untouched by `T_B`, so no cell can pass on `rel` by widening its
uncertainty.

**Statistics are rounded away from zero before comparison.**  Every gate is a
`<=`, so rounding the statistic up and using the limit exactly makes a PASS
strictly harder.  At 12 decimal places this changes no decision that is not
already at the threshold to within `1e-12`; the direction is on the record.

## 3. Why one worker on a six-core machine

Measured, before Stage-0: total CPU-seconds **inflate** with worker count on
this chip — ×1.45 at two workers, ×1.78 at four — because the extra work lands
on efficiency cores.  CPU-hours are the capped resource, so parallelism spends
the budget that gates the campaign in order to buy wall time.  Frozen at one
worker.  See `MAC_RUNTIME.md` for the table.

## 4. What Stage-0 is permitted to see

Stage-0 reads precision, stability and cost.  It does not read a discrepancy, a
`z`, the sign of a disagreement, whether a cell is close to passing, or whether
the campaign would close.  That exclusion is enforced by the frozen Stage-0
design and checked by `tests/test_production_governance.py`.

## 5. Scope, and what a successor may and may not claim

The frozen scope is 96 theorem-supported cells in 24 configurations, and it may
not be narrowed after results.  The *historically unresolved residue* is a
different and smaller object: the 8 cells in 4 configurations that P4X's own
precision precondition could not adjudicate.

These two must not be conflated in any verdict.  A campaign that discharges the
8-cell residue has supplied successor evidence for exactly those cells.  It has
**not** re-adjudicated all 96, and it has not repaired historical P4, which
remains `PARTIAL`.  A cell reported `INCONCLUSIVE` is reported as
`INCONCLUSIVE`; it is never counted as a pass and never dropped from the
denominator.
