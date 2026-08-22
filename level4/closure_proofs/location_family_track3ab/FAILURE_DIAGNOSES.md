# Track-3A/3B failure and boundary diagnoses

## No active scoped blocker

The new variance-aware numerical gate passed, the conditional Lean spine
compiled, and the axiom audit is clean.  There is no remaining blocker to the
scoped Track-3A/3B theorem requirement.

## Historical Track-3 failure remains failed

Historical Track 3 remains `LOCATION-FAMILY-THEOREM-PARTIAL`.  Its primary t3
replication-relative result remains

```text
4.605351% > 3% — FAILED
```

The retained-seed forensic replay classifies that discrepancy as ordinary
sampling variance amplified by the heavy-tailed stopped-gain integrand.  It
does not retroactively change the frozen decision.  The later experiment used
a new protocol, new master seed, substantially higher precommitted precision,
and two new independent replications.

## Analytic boundary is visible, not hidden

The concrete infinite t3 stopping process still has human-proved measurability,
a.s.-finiteness, tail, integrability, stopped change-of-measure, and domination
obligations.  Lean checks the consequence under an explicit derivative bridge;
it does not discharge those concrete obligations end to end.

This is the intended closure boundary, not an omitted or silently asserted
machine proof.

## No Arb certificate

Arb was deliberately not started.  Track 3A/3B closes the theorem requirement,
not a rigorous numerical inequality certificate or distribution-class
instability claim.  Any future certified t3 gain inequality is a separate
track.

## Git history event

During the numerical checkpoint push, `origin/main` was externally
force-rewritten to content-equivalent commits.  The push was rejected rather
than overwritten; the numerical commit was safely rebased onto the equivalent
frozen-protocol tree and then fast-forward pushed.  Protocol, source, outcome,
and historical hashes remained unchanged.  This was a provenance event, not a
scientific or implementation failure.
