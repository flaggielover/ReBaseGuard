# P4ZA Phase 3 — what K7 actually measured

The expansion is derived first, from the frozen estimator, and only then
checked against P4Z's stored ladder.

## 1. The frozen Route-B object

The estimand is `Gamma = -g_m'(0)` with `g_m(e) = E_e[A_m]`.  The frozen
convention is a **central** difference,

```text
D(h) = -( g_m(h) - g_m(-h) ) / (2h)
```

followed by the per-batch Richardson combination `R = (4 D(h/2) - D(h)) / 3` at
the frozen pair `(h, h/2) = (0.05, 0.025)`.

## 2. The expansion

Taylor about `0`, assuming `g_m` is five times differentiable in a neighbourhood:

```text
g_m(±h) = g_m(0) ± h g' + (h^2/2) g'' ± (h^3/6) g''' + (h^4/24) g'''' ± (h^5/120) g^(5) + ...
```

The central combination kills every **even** derivative:

```text
g_m(h) - g_m(-h) = 2h g' + (h^3/3) g''' + (h^5/60) g^(5) + ...
```

so

```text
D(h) = Gamma + a h^2 + b h^4 + O(h^6),     a = -g'''/6,   b = -g^(5)/120
```

Only even powers of `h` survive.  This is the structure the frozen Richardson
convention assumes.

## 3. The Richardson relation, and the residual

With a factor-2 pair,

```text
R(2h, h) = (4 D(h) - D(2h)) / 3
         = Gamma + (4a h^2 - 4a h^2)/3 + (4b h^4 - 16 b h^4)/3 + O(h^6)
         = Gamma - 4 b h^4 + O(h^6)
```

The `h^2` term cancels exactly and the residual is `-4 b h^4`.

**Consequence for two *adjacent* Richardson pairs.**  Writing `R_1 = R(2h, h)`
and `R_2 = R(h, h/2)`,

```text
R_1 - R_2 = -4b h^4 + 4b (h/2)^4 = -4b (h/2)^4 (16 - 1) = 15 * residual(R_2)
```

so

```text
residual( R(h, h/2) ) = ( R(2h, h) - R(h, h/2) ) / 15
```

This is the correct, derived truncation estimate: **the adjacent-pair
difference divided by fifteen.**

## 4. What P4Z's `T_B` actually computed

P4Z froze

```text
T_B = | R(0.2, 0.1) - R(0.05, 0.025) |
```

Two things are wrong with that as a residual estimate for the frozen pair, and
both inflate it:

1. **The pairs are not adjacent.**  They are separated by a factor of 4 in `h`,
   not 2.  Under the `h^4` model the frozen pair's own residual is
   `(0.025/0.1)^4 = 1/256` of the difference between those two Richardson
   values, so the raw difference overstates the residual by a factor of about
   **255**.
2. **The divisor 15 was never applied.**  Even for adjacent pairs the raw
   difference is 15 times the residual.

So `T_B` as frozen is not the truncation residual of the frozen Richardson
value; it is a *sensitivity of the Richardson value to the coarsest rung of the
ladder*.  As a diagnostic of "is the whole ladder inside the asymptotic
regime?" that is a legitimate quantity.  As "how wrong is `R(0.05, 0.025)`?" it
is not, and `K7`'s 2 % limit was applied to it as though it were.

## 5. Why `h = 0.2` can be outside the regime while `h = 0.05` is inside

The expansion above is an asymptotic statement: it is accurate once `a h^2`
dominates `b h^4`, i.e. once `h^2 << |a/b|`.  Nothing guarantees a particular
numerical `h` is small enough — that depends on the size of `g^(5)/g'''` at the
operating point.

For a high-threshold detector the map `g_m(e)` is built from a stopped
expectation whose stopping distribution shifts with `e`.  At `h = 0.2` the two
shifted runs stop at materially different times on a large fraction of paths,
and the higher derivatives of `g_m` are not negligible against the third.  At
`h = 0.05` the shift is a tenth of the CUSUM slack `k = 1/2` and a much smaller
fraction of paths change their stopping behaviour.

This is why the diagnosis must be *measured*, not assumed, and why the P4ZA
ladder is calibrated below the frozen steps before it is frozen.

## 6. What P4Z's ladder shows, tested against the derivation

If `a h^2` dominated, successive CRN-paired differences would shrink by exactly
`4` and the implied order `p = log2(ratio)` would be `2`.  Measured on P4Z's
own 20-block ladder, with each difference's own batch standard error:

| cell | `D(.2)-D(.1)` | `D(.1)-D(.05)` | `D(.05)-D(.025)` | p (coarse) | p (fine) |
|---|---|---|---|---|---|
| frozen/cusum@5/gaussian m=1 | −4.1653 ± 0.0427 | −2.0106 ± 0.0254 | −0.7396 ± 0.0570 | 1.05 | 1.44 |
| frozen/sr@520.886/gaussian m=1 | −4.7419 ± 0.0473 | −2.5151 ± 0.0538 | −0.7956 ± 0.0617 | 0.91 | 1.66 |
| frozen/sr@520.886/laplace m=1 | −3.5586 ± 0.0333 | −1.4355 ± 0.0578 | −0.4009 ± 0.0339 | 1.31 | 1.84 |
| frozen/cusum@5/logistic m=1 | −3.3972 ± 0.0307 | −1.3781 ± 0.0466 | −0.4420 ± 0.0466 | 1.30 | 1.64 |

The standard errors are 7 to 100 times smaller than the differences, so the
departure from `p = 2` at the coarse rungs is **real and not sampling noise**.
The implied order rises monotonically toward 2 as `h` falls, which is the
signature of higher-order terms still contributing at the coarse rungs rather
than of a genuinely non-quadratic map.

## 7. Where the ladder actually points

The frozen Richardson value is close to the independent RB-SCORE estimate,
while a naive geometric extrapolation of the raw central differences overshoots
it:

| cell | `D(0.025)` | `R(0.05,0.025)` | RB-SCORE | P4X Route A |
|---|---|---|---|---|
| frozen/cusum@5/gaussian m=1 | 15.7136 | 15.9601 | 15.8615 | 15.8925 |
| frozen/sr@520.886/gaussian m=1 | 16.9808 | 17.2460 | 17.2914 | 17.2943 |
| frozen/sr@520.886/laplace m=1 | 15.9416 | 16.0752 | 16.0609 | 16.1327 |
| frozen/cusum@5/logistic m=1 | 14.4857 | 14.6331 | 14.5768 | 14.5600 |

`R(0.05, 0.025)` sits within 0.09 % to 0.62 % of RB-SCORE, and the 20-block
ladder's own relative standard error is about 0.7 %, so those gaps are at the
level of the ladder's noise.  The Richardson step is doing its job at the frozen
rungs; it is the *coarse* rungs that are outside the regime.

## 8. One consequence that is not about P4Z's estimator

`RB-MAP` and the historical plain Route B estimate the **same** function
`g_m(e)`, without bias, by construction.  The `h`-expansion is therefore a
property of `g_m` — of the frozen scientific object — and not of either
estimator.  Any finite-difference truncation seen here is inherited by the
frozen protocol itself, and would be seen by P4 and P4X equally.

That is a statement about the frozen convention, and P4ZA neither repairs nor
relaxes it.  It is recorded because a successor that silently attributed the
effect to its own estimator would be wrong.

## 9. What follows for the P4ZA ladder

* Drop `h = 0.2`: demonstrably outside the regime at these operating points.
* Calibrate **below** the frozen steps before freezing, to establish where
  `p -> 2`, rather than assuming it.
* Estimate the truncation residual from **adjacent** Richardson pairs, divided
  by 15, as derived in Section 3 — not from a raw difference across a factor-4
  gap.
* Round the residual outward, and keep every scientific threshold unchanged.
