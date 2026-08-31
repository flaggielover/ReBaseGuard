# Priority-3 stability-map theorem

Priority 3 proves nothing about detectors. It proves what the two already
closed detector-specific derivative theorems imply about local stability, once
their multiplier is intersected with the admissible reuse domain.

## 1. Imported statements

Both imports are closed and are treated here as immutable hypotheses.

**(P1)** Level-4 Priority 1, frozen Gaussian two-sided CUSUM with `k=1/2`,
inclusive threshold `h=5`, reset state, ordinary `tau=inf{t>=1: alarm}`,
Stage-D window `w_m=min(m,tau)` with denominator `w_m` and the terminal
alarm-causing increment included:

```text
F'_{rho,m}(0) = rho (1 - GammaTilde_m),
GammaTilde_m  = E_0[A_m T_tau].
```

**(P2)** Level-4 Priority 2, reset symmetric two-chart Shiryaev-Roberts with
natural threshold `A=520.886133602749`, both charts updated before an
inclusive comparison, no head start, the same window and stopping conventions:

```text
F'_{rho,m}(0) = rho (1 - GammaTilde_m^SR),
GammaTilde_m^SR = E_0[A_m T_tau].
```

Write `D` for the detector family and set

```text
lambda_{D,m}(rho) := F'_{rho,m}(0) = rho (1 - GammaTilde_{D,m}).
```

Both theorems also establish that sign-reversal symmetry centres the map, so
`e=0` is a fixed point of the conditional-mean reference map.

## 2. Admissible domain and the meaning of rho

The reuse fraction enters as

```text
e_{j+1} = rho * (reused stopped estimate) + (1-rho) * (fresh centered estimate),
```

so the admissible domain is `rho in [0,1]`, unchanged from Stage C, Stage D
and the D4 phase map. `rho=0` is not a special convention: it is the pure-fresh
map, its multiplier is exactly `0`, and it is locally attracting by the very
same criterion that governs every other reuse fraction.

## 3. First-order classification

For a continuously differentiable scalar map with fixed point `0` and
multiplier `lambda`:

```text
|lambda| < 1   ->  the fixed point is locally attracting
|lambda| > 1   ->  the fixed point is locally repelling
|lambda| = 1   ->  linearization is inconclusive
```

Because `rho >= 0`,

```text
|lambda_{D,m}(rho)| = rho * |1 - GammaTilde_{D,m}| = rho * d_{D,m},
d_{D,m} := |1 - GammaTilde_{D,m}|.
```

`|lambda|` is therefore linear and, when `d_{D,m} > 0`, strictly increasing in
`rho` on `[0,∞)`. This monotonicity is what makes a single threshold — rather
than a union of intervals — the correct description of the stable region.

## 4. Critical reuse fraction

**Theorem (boundary).** If `d_{D,m} > 0` then, on `rho >= 0`,

```text
rho_c(D,m) = 1 / d_{D,m},
|lambda_{D,m}(rho_c)| = 1 exactly,
```

and

```text
0 <= rho < rho_c   ->  locally attracting
rho = rho_c        ->  first-order boundary, linearization inconclusive
rho > rho_c        ->  locally repelling.
```

In the regime both campaigns actually measure, `GammaTilde_{D,m} > 1`, so
`d_{D,m} = GammaTilde_{D,m} - 1` and

```text
rho_c(D,m) = 1 / (GammaTilde_{D,m} - 1).
```

**Intersection with the admissible domain.** For `GammaTilde > 1`,

```text
rho_c <= 1  <=>  GammaTilde >= 2.
```

Hence:

- `GammaTilde > 2`: the boundary is strictly interior, and full reuse is
  locally repelling;
- `GammaTilde = 2`: the boundary is exactly full reuse, `rho_c = 1`;
- `1 < GammaTilde < 2`: `rho_c > 1`, so every admissible reuse fraction is
  locally attracting and no accessible boundary exists.

## 5. Audit of the remaining gain regimes

The `GammaTilde > 1` formula is not applied outside its domain. The absolute
value form is used throughout, and each regime is labelled explicitly.

| regime | `d = |1-GammaTilde|` | boundary | reading on `[0,1]` |
|---|---|---|---|
| `GammaTilde > 2` | `> 1` | `rho_c = 1/(GammaTilde-1) < 1` | interior boundary |
| `GammaTilde = 2` | `= 1` | `rho_c = 1` | attracting on `[0,1)`; boundary at full reuse |
| `1 < GammaTilde < 2` | `< 1` | `rho_c > 1` | attracting throughout `[0,1]` |
| `GammaTilde = 1` | `= 0` | none; `lambda ≡ 0` | attracting throughout, no `rho_c` |
| `0 < GammaTilde < 1` | `< 1` | `rho_c = 1/(1-GammaTilde) > 1` | attracting throughout `[0,1]`; the `GammaTilde>1` formula does not apply |
| `GammaTilde = 0` | `= 1` | `rho_c = 1` | attracting on `[0,1)`; boundary at full reuse |
| `GammaTilde < 0` | `> 1` | `rho_c = 1/(1-GammaTilde) < 1` | interior boundary again |

No regime is assumed before measurement. The `GammaTilde = 1` case is the only
one in which `rho_c` is undefined rather than merely inaccessible, and it is
reported as such.

## 6. Empirical gains and reportable classifications

For a detector whose gain is a Monte Carlo estimate `Ghat` with batch standard
error `SE`, the reported 95% interval is `Ghat -/+ z95 * SE`. Because
`rho >= 0`, the induced magnitude interval is the exact image

```text
[ rho * min_{G in I} |1-G| , rho * max_{G in I} |1-G| ],
```

where the minimum is `0` when `I` contains `1`. If that interval contains `1`,
the linearized classification at `rho` is *not* determined by the evidence, and
Priority 3 downgrades the cell to `INCONCLUSIVE` rather than reporting the
point-estimate class as robust. In particular, every cell placed exactly at an
estimated `rho_c` is uncertainty sensitive by construction.

When the whole gain interval lies strictly above one, the critical fraction
inherits the monotone transform

```text
rho_c in [ 1/(G_hi - 1), 1/(G_lo - 1) ],
SE(rho_c) = SE(GammaTilde) / (GammaTilde - 1)^2   (delta method).
```

## 7. What this theorem does not say

- It is a statement about the **first-order local** behaviour of the
  deterministic conditional-mean reference map at `e = 0`. It is not a
  statement of global stability, of convergence from arbitrary initial
  conditions, or of uniqueness or existence of a stationary law.
- It is per detector family and per window length. It is not a
  detector-universal law, and nothing here extends beyond the two frozen
  Gaussian specializations and the two exact finite-support witnesses.
- The classification of a cell is only as strong as the gain feeding it. A
  theorem-supported classification computed from a Monte Carlo gain is not an
  interval certificate, and this campaign never labels it as one.
