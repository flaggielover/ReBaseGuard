# Lean correspondence

## What Lean proves

`lean/SRPriority2.lean` independently defines the reset two-chart raw SR step,
inclusive alarm, finite first-alarm record, reflection, truncated window,
fixed-denominator comparison, and short correction. Key declarations are:

- `srStep_reflection`
- `alarmed_reflection`
- `firstAlarm_reflection`
- `direct_eq_fixed_add_short`
- `shortCorrection_nonneg`
- `integral_decomposition`
- `m_one_reduction`
- `derivative_spine_of_dominated`
- `attraction_criterion`
- `repulsion_criterion`

The derivative theorem consumes explicit measurability, integrability,
positive-neighborhood, and domination hypotheses through the generic
`RebaseguardLean.IntegralBridge` interface.

## Concrete obligations outside Lean

Lean does not construct the infinite Gaussian product space or machine-check
the concrete SR forcing tail, stopped exponential moment, stopped likelihood
change of measure, or local domination. Those SR-specific obligations are
proved analytically in `PROOF.md` and recorded individually in
`ASSUMPTION_DISCHARGE.md`. Gaussian numerical correspondence checks neither
proves nor replaces them.

The file imports no historical SR theorem and no Priority-1 campaign theorem.

## Axiom audit

Seven declarations were audited. Each depends only on:

```text
propext
Classical.choice
Quot.sound
```

There is no `sorryAx`, `admit`, or project-specific scientific axiom.
