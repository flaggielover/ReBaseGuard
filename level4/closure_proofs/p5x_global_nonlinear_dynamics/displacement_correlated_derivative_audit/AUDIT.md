# P5X — Displacement-Correlated Derivative Certification Audit

`PRE_FREEZE_CORRELATED_RANGE_CERTIFICATION_AUDIT`. Not R9. **No binding
checkpoint created, no binding gate run, SR prototype not rerun.**

```text
ANSWER  NO.  The correlated form is exact but its enclosure is WORSE than the
        existing range-based bound at every order and every grid.
CORRELATION_CLASS  FAIL   (0.417x plus / 0.846x minus, target 2.9x)
FAILURE            DC-B (displacement region too large), amplified by
                   DC-A (Hessian bounds too wide)
READY TO FREEZE    NO
```

---

## 1. Exact displacement map

Under the `xi`/`zeta` representation, with `w^{+/-} = 1/A + zeta^{+/-}`:

```text
q_plus (zeta,z) = w^+ e^{ z - 1/2}          Delta_+ = w^+ e^{ z-1/2} - zeta^+
q_minus(zeta,z) = w^- e^{-z - 1/2}          Delta_- = w^- e^{-z-1/2} - zeta^-
```

`q_plus` is strictly increasing in `z`, `q_minus` strictly decreasing, so each
attains its range at the live-region endpoints. At `z = u`, `q_plus = w^+
e^{1/2 - log w^+ - 1/2} = 1` **exactly**; at `z = l`, `q_minus = 1` exactly.

**Measured at the R8 hard cell** (`zeta^+ = 0.376465`):

```text
q_plus  sweeps [0.052263, 1.000000]     Delta_+ in [-0.324202, +0.623535]
q_minus sweeps [0.052263, 1.000000]     sup |Delta_+| = 0.623535
```

**The displacement is `O(1)`, not small**, and the segment `zeta -> q` sweeps
essentially the whole state domain. Path-local hulls therefore coincide with
global hulls — the refinement §7 hoped for does not exist here.

## 2. Mass identity and the exact correlated decomposition

```text
M(zeta,e) = int_l^u E^+ phi dz = e^{-e} [ Phi(u+e-1) - Phi(l+e-1) ]
```

Closed form vs 40000-point Simpson: relative gap `8.851e-20`.
**`M = 0.585594605986783712`, so the mass defect `1 - M = 0.414405` is NOT
small.** The weight does not integrate to 1 and cannot be treated as one.

```text
ghat_x(zeta) - K^{E+} ghat_x  =  (1-M) ghat_x(zeta)
                                 + int [ ghat_x(zeta) - ghat_x(q) ] W dz
```

Verified exactly: LHS `0.565742618697716182`, RHS `0.565742618697716146`,
relative gap `6.417e-17`. **`CORRELATED_DERIVATIVE_IDENTITY = PASS`.**

## 3. Term ledger at the hard cell `(385,382)`

| form | terms | sum | largest intermediate |
|---|---|---|---|
| original | `ghat_x = +1.160293`, `K = +0.594550`, `bdry = -0.565907` | `-1.646567e-04` | **`1.160293`** |
| correlated | `(1-M)ghat_x = +0.480832`, `displ = +0.084911`, `bdry = -0.565907` | same | **`0.565907`** |

The correlated form **does** halve the largest intermediate (`2.05x`). It does
not help the *enclosure*, because the cost of bounding the displacement integral
exceeds what the reduction buys.

## 4. Displacement moments — exact, and the sign changes

```text
int Delta_+ W dz = w^+ e^{1-2e}[Phi(u+e-2) - Phi(l+e-2)] - zeta^+ M
```

Closed form vs quadrature: relative gap `2.503e-18`. No `z`-panels.

```text
signed:  int Delta_+ W = +0.022738     int Delta_- W = -0.101608
absolute: int |Delta_+| W = 0.119450   int |Delta_-| W = 0.128267
```

`Delta_+` changes sign inside the live region (negative for small `z`, positive
near `z = u`), so the signed moment is `5.3x` smaller than the absolute one. A
first-order Lipschitz bound needs the **absolute** moment; only a second-order
form can exploit the signed one.

## 5. Bernstein Hessian — converged, and large

| quantity | deg 16 | deg 32 | deg 64 | deg 128 |
|---|---|---|---|---|
| `ghat_xx` hull width | `523.29` | `13.92` | `13.66` | `13.63` |
| `sup |ghat_xx|` | — | `12.750653` | `12.750650` | **`12.750648`** |
| `sup |ghat_xy|` | — | `0.1937` | `0.1937` | `0.1937` |
| `sup |ghat_yy|` | — | — | — | `5.0794` |
| `sup |ghat_xxx|` | — | — | — | **`400.389`** |

Elevation converges by degree 32, so `12.75` is the **true** supremum, not a
hull artifact. The derivative ladder is

```text
sup|ghat_x| = 1.2046  ->  sup|ghat_xx| = 12.7506  ->  sup|ghat_xxx| = 400.389
                     10.6x                        31.4x
```

**Each derivative order costs about `10-30x`, while each order of the expansion
buys only a factor `|Delta| ~ 0.1-0.6`.** The Taylor expansion in the
displacement therefore diverges.

## 6. Measured bounds

| route | `dr/dzeta^+` width | tightening | `dr/dzeta^-` width | tightening |
|---|---|---|---|---|
| R8 range-based (current best) | **`0.677`** | — | **`0.947`** | — |
| first-order correlated | `1.6224` | **`0.4173x`** | `1.1189` | **`0.8464x`** |
| second-order correlated | `25.807` | **`0.0262x`** | — | — |

First order: `12.7506 x 0.119450 + 0.1937 x 0.128267 = 1.5479`, against the
direct range bound `1.0295 x 0.5856 = 0.6033`. Second order: the exact
first-order term collapses to `0.3096` using the signed moments, but the
remainder `0.5 x 400.389 x 0.126992 = 25.42` destroys it.

Both are **worse** than simply bounding `ghat_x`'s range. `CORRELATION_FAIL`.

## 7. Grid ladder (best correlated form)

`required_delta_F3 = 8.757254e-04`.

| grid | `delta_new` | R8 at same grid | `S1` | SR `m=1` CPU-h |
|---|---|---|---|---|
| 256 | `1.0721e-02` | `6.3579e-03` | FAIL | `76` |
| 512 | `5.3664e-03` | — | FAIL | `304` |
| 640 | `4.2955e-03` | — | FAIL | `475` |
| 1024 | `2.6893e-03` | `1.5986e-03` | FAIL | `1216` |

Worse than R8 at every grid. `S2` alone would pass at grid `<= 640` (`475`
CPU-h), but `S1` fails there by `4.9x`, so the two never hold together — the
same structural impasse as the previous audit, now for a different reason.

## 8. Why it fails — `DC-B` with `DC-A`

The kernel evaluates `ghat_x` at `q(zeta,z)`, and as `z` ranges over the live
region `q` sweeps essentially the entire domain. So:

* `|Delta|` is `O(1)`, not a small perturbation — **`DC-B`**;
* the path region equals the global region, so path-restriction gains nothing;
* the derivative ladder grows `~10-30x` per order — **`DC-A`**;
* hence every Taylor order multiplies the bound by `~10-30 x |Delta| ~ 3-19`,
  i.e. **the expansion diverges**.

A displacement-correlated expansion is only useful when the displacement is
small relative to the scale on which the function varies. Here it is not, and no
amount of elevation, path-restriction or moment exactness changes that.
Both the mass identity and the correlated identity are *exact* — the failure is
not algebraic but structural.

## 9. Invariants

`z_panels = 0`, `softplus_approximations = 0` throughout. The candidate, R6
kernel, `xi` transform, R8 `w^-` correction, Bernstein representation and
`C_SR = 216.963` are all reused unchanged; `B1` untouched; no refit.

Per-cell cost was **not separately benchmarked**: the Hessian hulls are
candidate-global (computed once) and the displacement moments are two extra
closed-form `Phi` differences, so the per-cell work is R8's `~5 ms` plus a small
constant. Since the width failure is decisive at every grid, §28's stop-early
rule applies and precise cost measurement would not change the verdict.
