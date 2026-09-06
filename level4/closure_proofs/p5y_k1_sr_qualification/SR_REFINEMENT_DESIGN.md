# SR refinement design, and the order-3 assessment

Phases 8 and 9. Required because the n-step resolvent alone is not sufficient
(`SR_NSTEP_RESOLVENT.md` section 10, re-measured with frozen `rho` in
`SR_RESOLVENT_GOVERNANCE.md` section 3).

## 1. The measured gap, with frozen geometry

Whole-cell `W_cover = rho |D| + rho^2 M_R2 / 2` against `B_cover = 1/20`, m = 2,
using each cell's own frozen `C_upper` and `rho`:

| cell | e0 | C_upper | rho | rho·\|D\| | rho²·M_R2/2 | utilisation |
|---|---|---|---|---|---|---|
| 0 | 2.60e-4 | 1205.94 | 2.60e-4 | 1.91e2 | 4.78e1 | **4.78e3** |
| 100 | 0.0691 | 674.57 | 4.64e-4 | 1.30e2 | 3.25e1 | **3.24e3** |
| 200 | 0.2284 | 216.17 | 1.45e-3 | 5.99e1 | 1.50e1 | **1.50e3** |
| 275 | 1.005 | 17.92 | 1.75e-2 | 1.57e1 | 4.10e0 | **3.97e2** |
| 292 | 2.019 | 6.59 | 4.75e-2 | 1.96e1 | 5.71e0 | **5.06e2** |
| 313 | 6.240 | 2.00 | 1.57e-1 | 1.75e6 | 1.34e6 | **6.18e7** |

Every sampled cell is over budget, by 400x at best. The linear term `rho|D|`
dominates the curvature term by about 4x throughout, so **`M_R2` is not the only
thing that needs refining** — `D` needs it too.

## 2. Why the tower is loose (and it is the tower, not the science)

The chain bounds each object by `C x (operator norm) x (previous bound)`:

```text
    |F_r|  <= C ( |S_r| + |e| |h_1| )                       ~ C
    |D_r|  <= C ( k1 |F_r| + |S_r'| + |h_1| + |e| |h_1'| )  ~ C^2
    |H_r|  <= C ( k2 |F_r| + 2 k1 |D_r| + ... )             ~ C^3
```

Measured exponent `d log M_R2 / d log C = 2.97`. Each step assumes every factor
attains its worst case at the same state and the same drift simultaneously. The
true `R''` has no reason to be that large: it is one derivative of a bounded
scalar, not a product of three suprema.

## 3. The repair: certify midpoints, bound only the variation

The frozen cover already evaluates at a midpoint and carries a Taylor remainder
(`ledger.taylor_enclosure`). The refinement applies the same idea *inside* the
object chain rather than only at the end:

```text
   for X in {F_r, D_r, H_r}:
       X_mid   = certified value of X at the cell midpoint e0        [tight solve]
       X_cell  = X_mid  +  [-1,1] * rho * sup_{e in cell} |X'|       [tower, x rho]
```

Because `rho * C_upper = 0.3133` is invariant (governance section 3), *every*
variation term carries a factor `rho`, which converts one power of `C` into the
constant `0.3133`. Formally, refining at order `k` replaces `C^k` by
`|X^{(k)}(e0)| + 0.3133 * C^{k}` — the gain is real only when the midpoint value
is genuinely smaller than the tower, which is the empirical question below.

### Derived, not overwritten

Refined objects are NEW DAG nodes (`F:r:k0:refined`, ...) that consume the
unrefined node plus a midpoint certificate. The frozen DAG nodes are never
mutated and never monkey-patched, and each refined node carries its own
`(primitive_certificate, propagation_path, destination_quantity, derivative_order)`
ownership key, so `depgraph.Charge` uniqueness still forbids double counting.

## 4. SR-specific midpoint equations (derived from the SR recurrence)

Not transferred from CUSUM. At the midpoint `e0`, solve the same raw-variable
systems as tight linear problems rather than bounding them:

```text
    (I - K_{e0}) F_r(e0) = S_r(e0) + e0 h_1(e0)
    (I - K_{e0}) D_r(e0) = K'_{e0} F_r(e0) + S_r'(e0) + h_1(e0) + e0 h_1'(e0)
    (I - K_{e0}) H_r(e0) = K''_{e0} F_r(e0) + 2 K'_{e0} D_r(e0) + S_r''(e0)
                           + 2 h_1'(e0) + e0 h_1''(e0)
```

with the operator identities of `SR_DERIVATION.md` section 3, which remain exact:
`K' = -(K_z + e K)`, `K'' = K_z2 + 2e K_z + (e^2-1) K`.

## 5. Order-3 auxiliary evidence — assessment

Differentiating `(I - K) F_r = S_r + e h_1` three times (Leibniz, with
`(I-K)^{(k)} = -K^{(k)}` for `k >= 1`):

> ```
>   (I - K) F_r''' = 3 K' F_r'' + 3 K'' F_r' + K''' F_r
>                    + S_r''' + 3 h_1'' + e h_1'''
> ```

and the third operator derivative stays inside the frozen machinery, because
`d^3/de^3 phi(z+e) = -He_3(z+e) phi(z+e)` with `He_3(w) = w^3 - 3w`:

```text
    K''' f = - int_l^u ( w^3 - 3w ) f(q) phi(w) dz ,   w = z + e
```

which needs a `z^3` moment — already produced to arbitrary order by the exact
panel recursion `sr_local.centred_gaussian_moments`. So order 3 requires **no new
object class and no new operator class**, exactly as order 2 did.

**Assessment: LIKELY NEEDED, and the architecture is prepared but not built.**

The reasoning is quantitative rather than optimistic. Refining `H_r` to order 2
leaves a residual variation term `rho * sup|F'''| ~ rho * C^4 = 0.3133 * C^3`,
which is the *same order* as the unrefined `C^3` it was meant to remove. So
order-2 midpoint refinement alone does not close the gap **unless** the midpoint
third derivative is much smaller than its norm tower — which is precisely what
Aux3 measured on the CUSUM side, where higher-order auxiliary evidence
"dramatically tightened whole-cell curvature certificates".

Whether the same holds for SR is an **empirical question that cannot be settled
without the midpoint solves**, and those are the deferred heavy numerics. It is
recorded here as `NOT_ESTABLISHED` for SR, not inherited from CUSUM.

Governance, if it is built: order-3 evidence enters **only** as nested auxiliary
evidence under the existing curvature obligation, exactly as Aux3 did. No new
top-level work ID, no change to the 17,978-unit universe, no change to `m`,
detector scope, budgets or cover geometry.

## 6. Phase-7 diagnosis

```text
    NSTEP_HELPS_BUT_REFINEMENT_REQUIRED
```

The n-step resolvent removed 8-10 orders of magnitude of pure artefact
(`7.03e10 -> C_upper in [2, 1206]`) and made the problem finite and structured.
It does not by itself fit `B_cover` on any cell under the frozen geometry.
Refinement is mandatory, and the dominant target is the **linear** term
`rho |D|`, not the curvature term.
