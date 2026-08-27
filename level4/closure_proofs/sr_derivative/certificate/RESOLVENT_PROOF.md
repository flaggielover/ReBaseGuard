# SR monotone block-resolvent certificate

## Status

This is a new certificate component for the optional rigorous `Gamma_SR > 2`
upgrade. It does **not** by itself certify `Gamma_SR > 2`; it replaces the
previously unusable one-step resolvent bound with a much sharper rigorous route.

## One-sided domination

For the plus SR chart write

```text
Y_t = log(1+R_t^+).
```

While the chart is live,

```text
Y_t = softplus(Y_{t-1} + Z_t - 1/2).
```

For every fixed innovation `z`, the map

```text
y -> softplus(y+z-1/2)
```

is strictly increasing. Therefore, under a common innovation sequence, a chart
started from a larger log-state remains no smaller pathwise. Its probability of
hitting the threshold within any fixed horizon is consequently nondecreasing in
the starting state.

The symmetric two-chart stopping time is no later than the plus-chart hitting
time. Hence any uniform lower bound for plus-chart absorption is also a lower
bound for absorption of the exact two-chart killed kernel.

## Exact cell lower envelope

Partition the live interval

```text
[0, log(1+A))
```

into exact equal cells. For a source cell, evaluate transition probabilities at
its exact left endpoint. Pathwise monotonicity makes the resulting finite-state
Bellman recursion a lower envelope over the entire source cell; the grid is not
being used as a point-sampled approximation.

For destination interval `[a,b)` with `a>0`, the transition

```text
y' = softplus(y+z-1/2)
```

satisfies

```text
log(expm1(a)) - y + 1/2 <= z
z < log(expm1(b)) - y + 1/2.
```

The first destination cell has lower innovation endpoint `-infinity`, and the
alarm reward is

```text
P[z >= log(A)-y+1/2].
```

All Gaussian CDF values and all matrix arithmetic are evaluated with Arb
outward rounding. Every transition row plus its alarm reward must enclose one.

## Resolvent consequence

If the Arb recursion proves that the probability of plus-chart absorption by
step `n`, starting from zero, is at least an exact rational `q_safe>0`, then for
the exact killed two-chart kernel `K`,

```text
sup_s K^n 1(s) <= 1-q_safe.
```

Grouping the Neumann series into blocks gives

```text
||(I-K)^-1||_inf <= n/q_safe.
```

The initial target is `n=250`, `q_safe=19/100`, which would give

```text
||(I-K)^-1||_inf <= 250/(19/100) = 25000/19 < 1316.
```

This replaces the earlier crude one-step bound of approximately `7.0e10`.

## Implementation

Producer:

```text
certificate/certify_sr_resolvent.py
```

Expected artifact after execution in a `python-flint` environment:

```text
results/sr_monotone_contraction.json
```

Independent replay auditor:

```text
certificate/audit_sr_resolvent.py
```

The auditor does not import the producer. It reconstructs all transition rows
with scalar/list Arb arithmetic, checks their mass balance, replays the full
250-step lower-envelope recursion, and independently derives the exact
`25000/19` resolvent bound. Its machine-readable output is
`results/sr_monotone_contraction_audit.json`.

Until that script has actually run successfully under Arb, this document records
a rigorous proof architecture and executable producer, not a completed numerical
certificate. The repository must continue to label the overall SR Arb upgrade
`OPEN` until the residual and propagation stages also close.
