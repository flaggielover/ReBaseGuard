# Lean correspondence and analytic-boundary audit

**Compile:** PASS  
**Axiom audit:** PASS  
**Classification:** conditional algebraic/stopped-score proof spine  
**Main source SHA-256:** `64f687d3cfb05448a2c2b05d8965d4f922104bcf1797c42e8e69bc47fb927f2d`

## 1. Formal target map

| Target | Lean declaration | Machine-checked content |
|---|---|---|
| L1 | `SRState`, `reset`, `srStep`, `reflectState`, `srStep_reflection` | raw two-chart update and sign/state-swap equivariance |
| L2 | `alarmed`, `alarmed_iff_chart`, `alarmed_reflection`, `alarmed_at_inclusive_plus` | inclusive after-update chart alarm and reflection symmetry |
| L3 | `StoppedRecord`, `firstAlarmFrom`, `firstAlarm`, `firstAlarm_reflection` | first alarm on a finite residual list and record reflection |
| L4 | `reflected_alarm_preserves_time`, `reflected_alarm_negates_terminal_and_total`, `reflected_terminal_product` | alarm-time preservation, terminal/stopped-sum negation, product invariance |
| L5 | `reuseMean`, `reuseMean_zero`, `reuseMean_one`, `reuseMean_odd` | exact rho scaling, endpoints, and oddness consequence |
| L6 | `derivative_of_terminalMean`, `derivative_spine_of_dominated` | `rho(1-Gamma)` derivative algebra using the existing stopped-integral bridge under explicit hypotheses |
| L7 | `gamma_gt_two_abs_derivative`, `gamma_gt_two_full_reuse_instability` | `Gamma>2 -> |1-Gamma|>1` at full reuse |
| L8 | `authoritativeA`, `runtimeA`, positivity theorems, `authoritativeA_ne_historical` | exact authoritative decimal and runtime rational are admissible; old `520.3125` is distinct |

The formal finite-path recursion starts at reset, updates both charts from the
same residual, and tests the inclusive alarm predicate on the post-update
state.  `firstAlarm_reflection` proves that reflecting every residual negates
the terminal statistics and swaps the terminal chart state while preserving
the first alarm time.

## 2. Reused Level 1--3 infrastructure

`derivative_spine_of_dominated` imports
`RebaseguardLean.IntegralBridge` and calls the already proved theorem
`hasDerivAt_integral_stoppedIntegrand_zero`.  The reused interface provides:

- the pointwise derivative of
  `Z_tau exp(-e T_tau-e^2 tau/2)`;
- a dominated differentiation-under-the-integral theorem at zero; and
- the exact derivative `-integral Z_tau T_tau` under its explicit
  measurability, integrability, and uniform-domination hypotheses.

Track 2 adds the SR finite-path symmetry and stopped-record algebra, then wraps
that abstract derivative in the frozen affine mean map.

## 3. Explicit analytic boundary

The Lean result is a conditional formal proof spine over explicit analytic
hypotheses.

> The Lean theorem formalizes the algebraic/stopped-score consequence under
> explicit analytic hypotheses; the concrete SR tail, measurability,
> integrability, and domination obligations remain human-proved.

The Lean file does not instantiate:

- the infinite product Gaussian residual probability space;
- the concrete SR filtration and stopping-time measurability;
- almost-sure finiteness or the SR forcing/geometric-tail calculation;
- concrete exponential moments of `tau` and `T_tau`;
- the event-by-event stopped change-of-measure identity; or
- the explicit integrable dominator for the concrete stopped SR variables.

Those obligations are discharged in the human proof in `THEOREM.md`.  This is
not described as an end-to-end Lean formalization of the infinite SR process.

## 4. Axiom audit

`lean/AxiomAudit.lean` prints axioms for nine headline declarations.  The exact
retained output is `results/axiom_audit.txt`.  Every declaration depends only
on:

```text
propext
Classical.choice
Quot.sound
```

These are standard Lean/Mathlib logical dependencies.  The Track-2 Lean source
contains no `sorry`, `admit`, or project-specific `axiom` declaration.

## 5. Rigor and scalar-inequality boundary

Lean proves the implication `Gamma_SR>2 -> |F'_1(0)|>1` algebraically.  It does
not prove the premise `Gamma_SR>2` for the concrete SR process.  The current
Monte Carlo lower bound remains `CONFIRMATORY NUMERICAL ONLY`; the rigorous SR
local-instability certificate remains `OPEN` until the separate Arb gate
succeeds.

