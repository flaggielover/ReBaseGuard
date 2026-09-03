# P4X — Successor Feasibility and Closure-Boundary Audit

```text
CLASSIFICATION      = PRE_SUCCESSOR_FEASIBILITY_AND_SCOPE_AUDIT
BINDING             = NO      (this is not a P4X checkpoint; nothing is frozen here)
P4_ORIGINAL_VERDICT = PARTIAL (immutable; not reopened, not amended, not reinterpreted)
P4X_CAMPAIGN_STATUS = NOT_OPENED
NOVELTY_STATUS      = NOT_ESTABLISHED
LEVEL4_GLOBAL_CLOSURE = NO
```

This namespace answers one question and creates no scientific claim:

> Can the scientific gap left by historical `P4 = PARTIAL` be closed by a
> finite, well-defined, affordable successor campaign **without changing the
> original scientific meaning**?

It reads the historical P4 artifacts, reconstructs the obligation table, audits
the three failed gates, classifies each one, builds the claim dependency graph,
computes the smallest open cut set, prices four routes, and returns a decision.

## Documents

| file | content |
|---|---|
| `AUDIT.md` | the audit itself — sections 1-21 of the charter |
| `HISTORICAL_OBLIGATION_TABLE.md` | exact reconstruction of P4's theorem, scope, assumptions, gates and statuses, read from the frozen artifacts |
| `DRAFT_SUCCESSOR_SCOPE.md` | a **draft, non-binding** P4X specification. Not executed. Not frozen. No checkpoint. |
| `results/audit_results.json` | the machine-readable audit record; authoritative where prose disagrees |
| `tests/` | focused tests over the reconstruction, the classification, the assumption map, the dependency graph and the governance test |

## What this namespace must never do

* modify, reopen, amend or reinterpret `../p4_theory_generalization/`, or any
  `P1`-`P9`, `P8R`, `P9R`, `P5X` namespace;
* relabel historical `P4` as anything other than `PARTIAL`;
* weaken, rewrite or regenerate any frozen P4 gate;
* create a binding P4X checkpoint, freeze a P4X protocol, or run production
  numerics;
* claim novelty, or claim Level-4 global closure.
