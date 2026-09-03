# P4X precision policy — proposed, not frozen

```text
STATUS              = PROPOSED
BINDING             = NO
P4_ORIGINAL_VERDICT = PARTIAL   (immutable)
```

The pilot's key output is **not a new pass threshold**.  The frozen 3 %
accuracy criterion and the frozen `|z| <= 4` consistency criterion are
inherited unchanged.  What the pilot produces is a *rule* mapping a desired
statistical precision to a required sample size and CPU cost.

## 1. The rule

```text
target relative SE per route:

    r* solves   1.96 * sqrt(2) * r*  =  0.03
    r* = 0.010823

required sample size:

    N_required = N_reference * (relSE_reference / r*)^(1/kappa)

    kappa = 0.5              when the estimator's per-path tail index alpha >= 2
    kappa = 1 - 1/alpha      when alpha < 2
```

**`r*` is forced, not chosen.**  `0.03` is the frozen accuracy criterion,
inherited unchanged from Track 3 through the frozen Priority-4 protocol.  The
requirement that it be attained with 95 % probability when the two routes
genuinely agree fixes `r*` at 1.08 %.  Nothing in this derivation refers to any
observed discrepancy.

## 2. Inputs, and what is deliberately not an input

| the rule reads | the rule never reads |
|---|---|
| the frozen 3 % accuracy criterion | whether a historical cell passed or failed |
| the measured tail index `alpha` of each estimator's per-path summand | the observed Route-A minus Route-B discrepancy |
| the measured reference relative SE | the sign or direction of any disagreement |
| measured CPU per path | any production estimate |

Feeding the rule the observed discrepancies would change nothing, because they
are not among its arguments.  The rule can be evaluated — and its full cost
table produced — before a single production path is drawn.  It is evaluated
that way here.

`alpha` is a property of the estimator and of the innovation law, fixed before
any production run.  For `t1p5` it is not even an empirical choice: Student-`t`
with `nu = 1.5` has tail index exactly `1.5`, the frozen Priority-4 protocol
already records this family as having infinite variance, and the sweep measures
`1.47-1.53` on both routes at all four layer/detector combinations.

## 3. Minimum block size

`t1p5`'s block means are not usable at the frozen campaign's block size.  The
ladder measures a block mean of `2.106` with block SD `8.11` at `n = 20 000`,
against `4.095` with block SD `1.00` at `n = 320 000`.

```text
MINIMUM_BLOCK_SIZE = 250 000 paths   for any cell with alpha < 2
                   =  20 000 paths   otherwise (the frozen convention)
```

This is a rule about the estimator's sampling distribution, not about any
outcome.  It is the single most effective lever the pilot found, and it costs
nothing: it reorganises a path budget rather than enlarging it.

## 4. Cost projection

Three tiers, on two independent axes: which reference standard error, and which
convergence rate.

| tier | reference relative SE | rate | rationale |
|---|---|---|---|
| **median** | fresh, independently seeded pilot measurement | `kappa = 0.5` | the rate the last rung of every pilot ladder supports |
| **conservative** | the frozen campaign's own measurement | `kappa = 0.5` | assumes the frozen campaign's unlucky standard error is the truth |
| **worst case** | the frozen campaign's own measurement | `kappa = 1 - 1/alpha` | additionally assumes the stable-law rate holds all the way; applies only where `alpha < 2`, i.e. only to `t1p5` |

```text
P4X_PROJECTED_PRODUCTION_CPU_MEDIAN        =  1.13 CPU-hours
P4X_PROJECTED_PRODUCTION_CPU_CONSERVATIVE  =  2.91 CPU-hours
P4X_PROJECTED_PRODUCTION_CPU_WORST_CASE    = 36.81 CPU-hours
```

for all 96 theorem-supported cells across both routes.  The four windows of a
configuration share their paths, so cost is charged once per
`(layer, detector, family, route)`.

Exactly **one** `(configuration, route)` is cost-significant:

| configuration | route | median | conservative | worst case |
|---|---|---|---|---|
| `frozen / sr@520.886 / t1p5` | B | 0.093 h | 1.75 h | **33.7 h** |

Everything else is bounded by a few CPU-minutes, because the five
finite-variance families already meet `r*` at their historical path counts or
come within a small multiple of it.

**No cell requires Route-Q arbitration.**  The audit's proposed arbitration
clause is inadmissible (Route Q is a different detector — see
`PILOT_REPORT.md` §7) and the projection above is computed without it.  The
worst-case tier is affordable, so the clause is not needed.

## 5. What the policy does when a cell is genuinely unaffordable

Retained for completeness, though the projection does not trigger it:

```text
a (configuration, route) whose projected WORST-CASE cost exceeds the
per-configuration allowance is declared PRECISION_LIMITED and reported as a
documented limitation of the successor campaign.

The declaration is made from projected cost alone, before the production
estimate for that cell exists.  It may never be made after seeing a result.

PER_CONFIGURATION_ALLOWANCE = 40 CPU-hours
```

At a 40-hour allowance the single cost-significant configuration (33.7 h worst
case) is inside the allowance and no cell is precision-limited.

## 6. Estimator plan

```text
P4X_BEST_ESTIMATOR_PLAN =
    retain the frozen Route-B estimator unchanged (CRN central difference,
    per-block Richardson, h = 0.05 / 0.025);
    retain the frozen Route-A score estimator unchanged;
    adopt NO variance-reduction method -- all four candidates were measured
    and rejected;
    buy precision with block size first and path count second;
    enforce MINIMUM_BLOCK_SIZE = 250 000 for alpha < 2 cells.
```

Rejections, with measured cause, are in `PILOT_REPORT.md` §6.  In brief:
reflection-antithetic is exact but increases variance 300-1000x; the Corollary-G2
control variate has exactly zero variance and so carries no information; coarse
`h` is inadmissibly biased for `skewnormal4` (+4.9 and +33.0 baseline SEs) and
its `t1p5` benefit rests on bias evidence the pilot cannot resolve.

## 7. Governance properties

| requirement | how it is met |
|---|---|
| fixed before production | the whole cost table is computable, and is computed here, with no production data |
| estimator-based | inputs are the tail index, the reference SE and CPU per path |
| independent of observed pass/fail direction | discrepancies are not arguments of the rule |
| attainable under measured compute | worst case 36.81 h against a recommended 60 h cap |
| compatible with original P4 scientific meaning | the 3 % accuracy and `|z| <= 4` criteria are inherited unchanged; `r*` is derived **from** the 3 % criterion rather than replacing it |

The threshold risk the feasibility audit flagged is engineered out rather than
argued away: the pilot buys the precision at which the **unchanged** frozen
criterion becomes attainable, instead of moving the criterion to fit the
estimator.
