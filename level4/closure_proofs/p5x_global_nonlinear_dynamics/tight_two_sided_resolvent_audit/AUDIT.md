# P5X — Tight Two-Sided SR Resolvent Feasibility Audit

`PRE_FREEZE_RESOLVENT_CERTIFICATION_AUDIT`. Not R9. **No binding checkpoint
created, no binding gate run, SR prototype not rerun, B2 and F3 untouched.**

```text
ANSWER  The true two-sided constant IS much smaller (134.88 vs the certified
        216.963), and a supersolution reaches C <= 141.361 POINTWISE.
        But the rigorous sign certificate costs 7.7 h on 6 cores for a merely
        useful C <= 180 -- 15.4x over the T2 budget.
T1 WIDTH  would PASS (141.361 <= 180) -- but only with a certificate failing T2
T2 COST   FAIL by 15.4x
T3 e-CELL not reached
READY TO FREEZE  NO      FAILURE  TC-C (sign certification too costly)
```

The existing one-sided certificate `C_SR <= 216.963` is **untouched and remains
the valid fallback**.

---

## 1. Exact two-sided Bellman problem

`h(x) = E_x[tau]` with `tau = inf{t >= 1 : alarm after the update at t}`. One
step always occurs, so on the live region

```text
h(x) = 1 + int_{l(x)}^{u(x)} h(q(x,z)) phi(z+e) dz  =  1 + (K_e h)(x)
i.e.  (I - K_e) h = 1 ,   h = 0 after the alarm,   h >= 1 everywhere.
```

Same frozen recurrence, same `xi`/`zeta` coordinates, same `D1`-corrected
domain `[0, b_SR]^2`, convention A, `x_0 = (0,0)`. `C_SR^2D = sup_x h(x)`.

## 2. Numerical reference (DIAGNOSTIC ONLY)

Sparse solve of `(I-K)h = 1` on a uniform `y`-grid with bilinear interpolation
and a per-state `160`-node Gauss-Legendre rule in `z`:

| `e` | `sup h` (G=96) | `sup h` (G=128) | argmax | MC scale |
|---|---|---|---|---|
| `0.24` | `134.7982` | **`134.8761`** | reset corner | — |
| `0.25` | `126.4761` | **`126.5465`** | reset corner | `~130` |
| `0.26` | `118.7694` | **`118.8332`** | reset corner | — |
| `0` | `463.9367` | **`464.4975`** | reset corner | `~472` |

Grid-converged to `~0.06%`, and consistent with the independent MC scale.

**The one-sided certificate carries `216.963 / 134.876 = 1.609x` slack** at the
worst `e` in the cell.

## 3. Shape

`sup h` is attained **at the reset corner**; `h` is monotone decreasing along
each axis; `h(far corner) = 18.31`; `max |dh/dy^+| ~ 41.1`. Not symmetric at
`e = 0.24` (`max |h - h^T| = 44.61`, relative `0.33`), as expected since the
detector symmetry is `h(x^+,x^-;e) = h(x^-,x^+;-e)` and `e != 0`. No property
is used rigorously.

## 4. Selected route — scaled supersolution

Rejected without deep work: constant shift (§12) because `1 - K1` is the
one-step alarm probability, measured `~4e-11` in the safe region, so `beta` buys
nothing there; multi-step and substochastic-matrix routes (§13, §14, §5E)
because the cheap probe below already settles cost.

**Theorem used.** If `H >= 1 + K_e H` on the live region with `H >= 0`, then
`E_x[tau] <= H(x)`. With `H = alpha * hhat + beta`:

```text
s := H - 1 - K H = alpha (hhat - 1 - K hhat) + (alpha - 1) + beta (1 - K 1)
                 = alpha * r_h + (alpha - 1) + beta * p_alarm
```

The `(alpha - 1)` term is the structural gain: it is a **uniform** positive
margin, independent of the alarm probability. Hence with a rigorous
`r_h >= r_min > -1`,

```text
alpha = 1/(1 + r_min)     and     C_SR^2D <= alpha * sup hhat .
```

Only a rigorous **lower** bound on `r_h` is needed — a sign/magnitude
certificate, not a tight two-sided enclosure (§22).

## 5. Candidate `hhat` and its pointwise residual

Chebyshev least-squares fit in `zeta`, converted to monomials **in Arb at 400
bits** (a float64 conversion destroys the polynomial: the transfer matrix has
entries to `1e12` and gave a spurious `r_min = -1.45e6`).

| degree | `max abs cheb coef` | `max abs mono coef` | `r_h` min | `r_h` max | `alpha` | `C <= ` |
|---|---|---|---|---|---|---|
| 12 | `63.46` | `2.713e+11` | `-0.101114` | `+0.058403` | `1.1125` | `149.953` |
| **16** | `63.85` | `3.672e+17` | **`-0.046031`** | `+0.017020` | **`1.0483`** | **`141.361`** |
| 20 | `68.10` | `2.960e+23` | `-0.319445` | `+0.010637` | `1.4694` | `198.189` |

**Degree 16 gives a pointwise `C <= 141.361`** — below the `150` breakthrough
line, and `1.53x` better than the one-sided `216.963`. Degree 20 is worse: the
monomial coefficients reach `3e23` and precision is lost even at 400 bits.

## 6. Why it cannot be certified inside budget

The sign certificate needs `inf r_h` over the whole domain, i.e. the pointwise
minimum minus the cell enclosure width. Using the R8 mean-value machinery, that
width is `2h_cell (Mx * int E^+ phi + My * int E^- phi)` with **converged**
Bernstein derivative sups (stable from elevated degree 64):

```text
Mx = sup |hhat_zeta+| =  54.92        My = sup |hhat_zeta-| = 898.59
enclosure width = 1182 / G    (zeta-uniform grid)
```

| target `C` | `alpha` | needed `r_min` | width budget | grid `G` | cells | CPU-h | 6-core wall | `T2` |
|---|---|---|---|---|---|---|---|---|
| 150 | `1.1123` | `-0.1010` | `0.0549` | `21513` | `4.63e8` | `642.8` | `107.1 h` | FAIL |
| 160 | `1.1865` | `-0.1572` | `0.1111` | `10636` | `1.13e8` | `157.1` | `26.2 h` | FAIL |
| **180** | `1.3348` | `-0.2508` | `0.2048` | `5772` | `3.33e7` | `46.3` | **`7.7 h`** | FAIL |
| 216.963 | `1.6089` | `-0.3784` | `0.3324` | `3556` | `1.26e7` | `17.6` | `2.9 h` | FAIL |

`T2` is `0.5 h` wall on 6 cores. Even reproducing the *existing* constant costs
`2.9 h`; a useful `C <= 180` costs `7.7 h`, **`15.4x` over budget**.

`My = 898.59` dominates: `h` varies steeply in the minus coordinate, which is
the chart that drives the alarm.

## 7. `F3` impact — tightening `C` alone does not close it

`required_delta = (0.2 - 0.01)/C`. Entries are "how many times too large the
existing certifier's `delta` is"; `<= 1.00` would meet `F3`.

| `C` | required `delta` | R8 B2 @1024 | direct-residual @1024 | direct-residual @4096 |
|---|---|---|---|---|
| `216.963` (current) | `8.757254e-04` | `5.72x` | `1.83x` | `0.47x` |
| `180` | `1.055556e-03` | `4.75x` | `1.51x` | `0.39x` |
| `150` | `1.266667e-03` | `3.96x` | `1.26x` | `0.32x` |
| `141.361` (pointwise best) | `1.344077e-03` | `3.73x` | `1.19x` | `0.30x` |
| `134.854` (true `sup h`) | `1.408933e-03` | `3.56x` | `1.13x` | `0.29x` |

Even with a **perfect** `C` equal to the true `sup h`, the best existing
certifier at an affordable grid is still `1.13x` short, and the grid that does
meet `F3` (`4096`) costs `19457` CPU-hours. **The `C` side is worth at most
`1.6x`; the binding constraint remains the residual certifier's cost.**

## 8. Classification and the recurring root cause

`TC-C` — sign certification too loose/costly. Not `TC-A`: the true constant is
excellent (`134.88`). Not `TC-B`: the supersolution approximation is fine
(`r_min = -0.046` pointwise).

The width `1182/G` is large because `Mx`, `My` must be **global** sups: the
mean-value bound on `d(K hhat)/dzeta` evaluates `hhat_zeta` at the *image* of
the cell, and the image of any cell under the live `z`-range covers essentially
the whole domain. **This is the same structural property that defeated the R7
centred form, the direct-residual form, and the displacement-correlated form.**
Four different bounding architectures, one obstruction.
