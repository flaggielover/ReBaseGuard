# SR midpoint / whole-cell refinement — derivation

Phases 2, 3 and 5. Derived from the SR raw-variable recurrence, not transferred
from CUSUM; the SR source terms differ and the difference is load-bearing.

---

## 1. What the frozen certificate actually asks for

`assembly.py` fixes the evaluation semantics, and they are NOT uniform:

```text
    k = 0 at e0                 -> R_interval
    k = 1 at e0                 -> D_interval
    k = 2 UNIFORMLY ON THE CELL -> R2_interval,  M_R2 = mag(R2_interval)
```

and `ledger.py` consumes them through the frozen order-2 Taylor cover

```text
    R(e) in R_interval + Delta*D_interval + [-rho^2 M_R2/2, +rho^2 M_R2/2]
    W_cover_exact = rho * mag(D_interval) + rho^2 * M_R2 / 2
```

> **The cover is frozen at order 2 in `e`.** Raising the Taylor order is not
> available: it would change the certificate structure. The only freedom is how
> tightly `R(e0)`, `D(e0)` and `sup_cell |R''|` are bounded.

This also identifies a defect in the previous SR checkpoint: `sr_propagate`
computes all three with whole-cell envelopes, whereas `R_interval` and
`D_interval` are MIDPOINT quantities. The current bound is therefore valid but
conservative in a way the frozen semantics never asked for.

## 2. What refinement actually refines: the ERROR, not the value

The validated CUSUM refinement (`refine.py`) does not refine values. It refines
the whole-cell ERROR bounds `epsF/epsD/epsH`, using

  * `epsF_mid`, `epsD_mid` — errors of a SECOND propagation performed at `e0`;
  * `sup|Dhat|`, `sup|Hhat|` — sups of the computed CANDIDATES.

```text
    epsF_cell <= epsF_mid + rho * ||D(.,e0)||   + (rho^2/2) * supH
    epsD_cell <= epsD_mid + rho * supH
    supH      <= sup|Hhat| + epsH_cell
    ||D(.,e0)|| <= sup|Dhat| + epsD_mid
```

> **Consequence for sequencing.** Refinement is meaningless without candidates:
> in a pure sup-norm envelope there is no "value", everything is error. The
> patch-resolved candidate layer (Phase 8) is a PREREQUISITE for refinement, not
> a parallel task. This reorders the remaining SR blockers.

## 3. The SR closure equation (SR-specific, derived here)

The SR order-2 equation carries two terms the g-variable form does not
(`SR_DERIVATION.md` sections 4-5):

```text
    (I - K) H_r = K'' F_r + 2 K' D_r + S_r'' + 2 h_1' + e h_1''
```

so the SR whole-cell error closure is

> ```
>   epsH_cell = C ( deltaH_cell + k2 epsF_cell + 2 k1 epsD_cell + epsS2_cell
>                   + 2 eps_h1' + |e| eps_h1'' )
> ```

The two extra terms `2 eps_h1'` and `|e| eps_h1''` are **constants of the
iteration** — they do not depend on `epsF/epsD/epsH` — so they shift the fixed
point without changing the contraction. Omitting them would silently understate
the SR bound, which is why `sr_refine` requires them explicitly rather than
defaulting them to zero.

## 4. Contraction — proved, and quantified for SR

Substituting the first two lines into the third, the map in `supH` has derivative

> ```
>   kappa' = C * rho * ( 2 k1 + k2 rho / 2 )
> ```

`refine.py` reports only `rho*C*2*k1` and explicitly declines to rely on it;
`kappa'` above is the complete constant, including the curvature channel.

Measured over **all 315 compact SR cells**, using each cell's own frozen
`C_upper`, `rho` and `k1(e0)`, `k2(e0)`:

```text
    kappa  = rho * C_upper * 2 k1     min 0.255052   max 0.500000   (0 cells >= 1)
    kappa' = C rho (2k1 + k2 rho/2)   min 0.268867   max 0.513371   (0 cells >= 1)
    fixed-point amplification 1/(1 - kappa')            <=  2.0550
```

`kappa` is capped at **exactly 1/2**, and that is by construction, not luck: the
frozen step rule is `s = 1/(4 a_upper C_upper)` (`build_spec.py:97`) with
`a_upper = k1 = sqrt(2/pi) = 0.79788456`, giving

```text
    kappa = rho * C * 2 k1 = 2 k1 / (4 a_upper) = 1/2
```

and it is the same identity that makes `rho * C_upper = 0.3133` invariant.

> **The SR refinement iteration provably contracts on every compact SR cell**,
> geometrically at rate <= 0.5134, so the refined fixed point is at most 2.055x
> its midpoint-driven input instead of the crude `C^3` tower.

Validity does not depend on this: as in `refine.py`, every iterate is seeded
with the crude bound and intersected with it, so refinement can only tighten and
a failure to contract simply leaves the crude bound standing.

## 5. Per-object midpoint expansion

With `s = e - e0`, `|s| <= rho`, integral remainder, for each object `X`:

| object | midpoint value | 1st derivative | remainder majorant | notes |
|---|---|---|---|---|
| `F_r` | `F_r(e0)` | `D_r(e0)` | `(rho^2/2) sup_cell|H_r|` | order-2 form |
| `D_r` | `D_r(e0)` | `H_r(e0)` | `rho * sup_cell|H_r|` | mean value on `D` |
| `H_r` | `H_r(e0)` | — | closure equation, section 3 | whole cell |
| `h_j` | `h_j(e0)` | `h_j'(e0)` | `rho * sup|h_j''|` | Leibniz chain |
| `S_0` | `rho_1(e0)` | `rho_1'(e0)` | `rho * sup|rho_1''|` | closed form, exact |
| `S_j` | `K_z h_j (e0)` | `S_j'(e0)` | `rho * sup|S_j''|` | operator chain |
| `W_(r,j)` | `K^j S_r (e0)` | Leibniz | `rho * sup|W''|` | finite powers |
| assembly | frozen rationals | same coefficients | linear in the above | no `+e` term |

Every entry uses the SAME exact frozen assembly coefficients `c_(m,t) = 1/t - 1/m`;
only the objects change.

## 6. Ownership (Phase 3)

Refined values live in DERIVED nodes and never overwrite the frozen DAG:

```text
    F:r:k0            unrefined, frozen semantics       (never mutated)
    F:r:k0:refined    derived node, consumes the above + midpoint evidence
```

Each refined node carries its own frozen ownership 4-tuple
`(primitive_certificate, propagation_path, destination_quantity, derivative_order)`,
so `depgraph.Charge` uniqueness still forbids double counting, and the refined
node's `propagation_path` differs from the unrefined one by construction. Nested
evidence (midpoint, order-3, n-step corroboration, patch certificates) is bound
by source hash recursively. **No new top-level work ID**: the SR universe stays
at 8,849 and the global universe at 17,978.

## 7. Order-3 adjudication (Phase 5)

Because the cover is frozen at order 2 (section 1), order-3 evidence can only
enter as NESTED auxiliary evidence tightening `sup_cell |H_r|` — exactly the role
Aux3 played for CUSUM. The question is whether it is needed.

What is established:

* the refinement iteration contracts at `<= 0.5134` on every compact cell, so the
  refined bound is within `2.055x` of its midpoint-driven input — **the tower is
  removed by the iteration itself, without any order-3 evidence**;
* the residual then depends on `epsF_mid`, `epsD_mid`, `deltaH_cell` and the
  candidate sups, none of which exist yet;
* a cheap proxy (derivatives of the frozen `C_upper(e)` profile) gives
  `tower(C^2)/|C''| ~ 1.8x - 9x` and `tower(C^3)/|C'''| ~ 1.6x - 1450x, but this
  proxies the variation of the RESOLVENT CONSTANT, not of `R`. It cannot see the
  renewal cancellation that the cancellation-preserving backend exists to
  exploit, so it is an indicator, not evidence.

> **Verdict: `NOT_ESTABLISHED`.**
>
> It is not `ORDER3_LIKELY_REQUIRED`: the contraction result removes the specific
> `C^3` blow-up that motivated the earlier "likely needed" reading, and it does so
> without order-3 evidence. It is not `ORDER2_LIKELY_SUFFICIENT` either: the
> refined fixed point is driven by midpoint errors and candidate sups that do not
> yet exist, so its magnitude is unmeasured.
>
> The adjudication is blocked on the candidate layer, not on more derivation.
> Deciding it from cheap proxies would be guessing, and the previous checkpoint's
> `LIKELY_NEEDED` is downgraded to `NOT_ESTABLISHED` accordingly.

The third-derivative machinery is derived in `SR_DERIVATION.md`-style form should
it be needed:

```text
    (I - K) F_r''' = 3 K' F_r'' + 3 K'' F_r' + K''' F_r + S_r''' + 3 h_1'' + e h_1'''
    K''' f = - int_l^u ( w^3 - 3w ) f(q) phi(w) dz ,     w = z + e
```

`He_3(w) = w^3 - 3w`, and the `z^3` moment comes from the same exact panel
recursion, so order 3 needs no new object or operator class. Binomial
coefficients `(1,3,3,1)` and the raw-variable term `3 h_1''` are asserted in the
tests.
