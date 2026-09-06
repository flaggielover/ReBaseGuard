# P5Y K1 — SR raw-variable derivation

Written BEFORE implementation, from the frozen sources only. Every equation on
this page is mapped to the implementation object it becomes. Nothing here
restates a CUSUM formula: the CUSUM path is hard-wired to the CUSUM state square
(`11/2`, `1/2`) and a recentred Hermite expansion of `phi(z+e)`; SR is a
two-chart softplus system. They share the Arb backend and the frozen error
algebra and nothing else.

Authoritative sources (read, not inferred):

| fact | source |
|---|---|
| recurrence, operators, targets | `p5x/compute_optimization_r3_sr_symbolic/EXACT_SR_TARGET.md` |
| assembly coefficients, no leading `+e` | `p5y_k1_cover_ledger_implementation/code/assembly.py` |
| derivative error propagation | `p5y_k1_cover_ledger_implementation/code/depgraph.py` |
| cover / curvature consumption | `p5y_k1_cover_ledger_implementation/code/ledger.py` |
| object list (19/cell) | `p5y_k1_cover_ledger_implementation/code/universe.py` |
| panel primitives | `p5x/.../sr_local.py`, `p5y_k1_task1r_budget_harness/code/harness.py` |

---

## 0. Frozen constants

```text
A      = 4581762885148045 / 8796093022208           exact runtime rational
b_SR   = log(1 + A)                                 state domain upper limit (erratum D1)
c_SR   = log A + 1/2                                alarm margin  == spec.SR_TERMINAL_EXPR
y      = (y^+, y^-) in [0, b_SR]^2,  y_0 = (0,0)    two charts, symmetric, no head start
z      = raw - e,  raw ~ N(0,1),  so z ~ N(-e, 1)
```

`spec.SPLICE_EXACT["SR"] == "log(4581762885148045/8796093022208)+1/2"` — the
splice point is `c_SR`. Not modified here.

## 1. Base renewal / resolvent equation

Update and continuation region (frozen, tested on the PRE-update `v`):

```text
v^+ = y^+ + z - 1/2 ,   v^- = y^- - z - 1/2
q_SR(y,z) = ( softplus(v^+) , softplus(v^-) ) ,  softplus(u) = log(1+e^u)
alarm iff max(v^+, v^-) >= log A
continuation interval  ( l(y), u(y) ) = ( y^- - c_SR ,  c_SR - y^+ )
```

The three frozen panel operators, all integrating `z` over `(l(y), u(y))`:

```text
(K_e   f)(y) = int_l^u        f(q_SR(y,z)) phi(z+e) dz
(K_z,e f)(y) = int_l^u  z     f(q_SR(y,z)) phi(z+e) dz
(K_z2,e f)(y)= int_l^u  z^2   f(q_SR(y,z)) phi(z+e) dz
```

Source / reward objects:

```text
h_1 = 1 - K_e 1 ,        h_j = K_e h_{j-1}        (j = 2,3,4)
S_0 = rho_{1,e} ,        S_j = K_{z,e} h_j        (j = 1..4)
rho_{1,e}(y) = phi(u+e) - phi(l+e) - e ( 1 - Phi(u+e) + Phi(l+e) )
rho_{2,e}(y) = [ (u+e)phi(u+e) + 1 - Phi(u+e) ] - 2e phi(u+e) + e^2 (1 - Phi(u+e))
             + [ -(l+e)phi(l+e) + Phi(l+e) ] + 2e phi(l+e) + e^2 Phi(l+e)
```

`l, u` depend on `y` only. **They do not depend on `e`.** Every `e`-derivative
below therefore differentiates the integrand only — there is no boundary term.
This is the single structural fact that makes the derivative system close.

## 2. Raw-variable coordinate transformation  (the key step)

`EXACT_SR_TARGET.md` §4 states the target in the *g-variable*:

```text
g_r = (I - K_e)^{-1} S_r
R_{SR,m}(e) = e + (1/m) sum_{r<m} [ g_r(y_0) - sum_{t=r+1}^{m-1} (K_e^{t-r-1} S_r)(y_0) ]
                + sum_{t=1}^{m-1} (1/t) sum_{i=1}^{t} (K_e^{i-1} S_{t-i})(y_0)
```

The K1 implementation is *raw-variable*: `assembly.assemble` **refuses** a
leading-`e` argument, because "the unknown is F = R itself and the e-linear
content of the reward has already cancelled". Define

```text
    F_r := g_r + e
```

Then `(1/m) sum_{r<m} F_r = e + (1/m) sum_{r<m} g_r`, because the sum has exactly
`m` terms — the leading `+e` is reproduced exactly and must not be added again.

Applying `(I - K_e)` to `F_r = g_r + e` and using `K_e 1 = 1 - h_1`:

```text
    (I - K_e) F_r = S_r + e (1 - K_e 1) = S_r + e * h_1
```

> **RAW-VARIABLE RESOLVENT EQUATION**
> ```
>     (I - K_e) F_r  =  S_r + e * h_1              r = 0..4
> ```
> This is why `h_1` is a first-class object class and why the source of the
> `F` equation is not `S_r` alone.

### Reduction of the tail sums to the frozen coefficient table

Collect the two `g`-form tail sums with `W_{r,j} := K_e^j S_r`:

```text
term2 = -(1/m) sum_{r<m} sum_{t=r+1}^{m-1} K^{t-r-1} S_r
      = -(1/m) sum_{t=1}^{m-1} sum_{r<t} W_{r,t-r-1}
term3 = sum_{t=1}^{m-1} (1/t) sum_{i=1}^{t} K^{i-1} S_{t-i}
      = sum_{t=1}^{m-1} (1/t) sum_{r<t} W_{r,t-r-1}         [r = t-i]
term2 + term3 = sum_{t=1}^{m-1} ( 1/t - 1/m ) sum_{r<t} W_{r,t-r-1}
```

which is exactly `assembly.coefficients`, `c_{m,t} = 1/t - 1/m`. Hence

> **RAW-VARIABLE ASSEMBLY (all orders k = 0,1,2)**
> ```
>   R_m^{(k)} = (1/m) sum_{r<m} F_r^{(k)}(y_0)
>             + sum_{t=1}^{m-1} c_{m,t} sum_{r<t} W_{r,t-r-1}^{(k)}(y_0)
> ```

Independent confirmation (not assumed — checked against frozen artifacts):

```text
m = 1 :  R_1 = F_0                              == Gate-2C  "R1e = F0e"
m = 2 :  c_{2,1} = 1 - 1/2 = 1/2
         R_2 = (F_0 + F_1)/2 + (1/2) W_{0,0}
             = (F_0 + F_1 + S_0)/2              == Gate-2C  "R2e = (F0e+F1e+S0_exact)/arb(2)"
```

## 3. Operator `e`-derivatives — the algebra closes

Since `l, u` are `e`-free, `d/de` acts on `phi(z+e)` only, and
`d^k/de^k phi(z+e) = (-1)^k He_k(z+e) phi(z+e)` (probabilists' Hermite):

```text
He_1(w) = w ,  He_2(w) = w^2 - 1
```

Therefore, writing `K, K_z, K_z2` for the frozen triple:

> ```
>   K_e'  = -( K_z,e + e K_e )
>   K_e'' =    K_z2,e + 2 e K_z,e + ( e^2 - 1 ) K_e
>   K_z,e'= -( K_z2,e + e K_z,e )
> ```

**Consequence (Phase 5 answer).** `K'` and `K''` are exact finite combinations of
the *frozen* operator triple. The order-2 SR system needs **no new operator
class and no third-order auxiliary evidence**: the frozen structure is closed
under the two differentiations K1 requires. `S_j'' = K_z'' h_j + 2 K_z' h_j' +
K_z h_j''` does reach a `z^3` moment, but `z`-moments are produced to arbitrary
order by the *same* exact panel recursion (`sr_local.centred_gaussian_moments`,
`N_k`), so this is a larger `kmax` on an existing primitive, not a new object
class and not a new top-level obligation.

## 4. First derivative

Differentiate the raw-variable resolvent equation once:

```text
(I - K_e) F_r' = K_e' F_r + S_r' + h_1 + e h_1'
```

with `D_r := F_r' = dF_r` (the frozen `dF_0..dF_4` object class). Note the
`+ h_1` term: it comes from `d/de (e h_1)` and is *absent* in the g-variable
formulation. Omitting it is the most likely silent SR defect, so it is asserted
in the tests.

Chain sources:

```text
h_1' = -K_e' 1                       (since h_1 = 1 - K_e 1)
h_j' = K_e' h_{j-1} + K_e h_{j-1}'
S_0' = rho_{1,e}'                    closed form, below
S_j' = K_z,e' h_j + K_z,e h_j'
W_{r,j}' : Leibniz on K^j S_r        (recurrence in section 6)
```

`rho_{1,e}` differentiates in closed form using `phi'(w) = -w phi(w)`,
`Phi'(w) = phi(w)`. With `U = u+e`, `L = l+e`:

```text
rho_1  = phi(U) - phi(L) - e ( 1 - Phi(U) + Phi(L) )
rho_1' = -U phi(U) + L phi(L) - ( 1 - Phi(U) + Phi(L) ) - e ( -phi(U) + phi(L) )
rho_1''=  (U^2 - 1) phi(U) - (L^2 - 1) phi(L) + 2 ( phi(U) - phi(L) )
          - e ( -U phi(U) + L phi(L) )
```

## 5. Second derivative / curvature

```text
(I - K_e) F_r'' = K_e'' F_r + 2 K_e' F_r' + S_r'' + 2 h_1' + e h_1''
```

with `H_r := F_r''`. The `2 h_1'` term is the order-2 analogue of the `+h_1`
above (Leibniz on `e h_1`). This matches the frozen propagation in
`depgraph.py` term-for-term:

```text
epsF_r = C ( deltaF_r + epsS_r )                              <-> section 2 equation
epsD_r = C ( deltaD_r + k1 epsF_r + epsS1_r )                 <-> section 4 equation
epsH_r = C ( deltaH_r + k2 epsF_r + 2 k1 epsD_r + epsS2_r )   <-> this equation
    C  = || (I - K_e)^{-1} ||,   k1 = || K_e' ||,   k2 = || K_e'' ||
```

`epsH_r` is required **uniformly on the cell** (not at the centre `e_0`), which is
what makes `M_R2` a whole-cell object.

## 6. Finite-power recurrences for m > 1

`W_{r,j} = K_e^j S_r`, needed for `j = 0 .. 3` at `m = 5`. Exactly the frozen
Leibniz recurrence of `depgraph.py`:

```text
W_{r,0}    = S_r
W_{r,j+1}  = K_e   W_{r,j}
W'_{r,j+1} = K_e   W'_{r,j} + K_e'  W_{r,j}
W''_{r,j+1}= K_e   W''_{r,j} + 2 K_e' W'_{r,j} + K_e'' W_{r,j}
```

matching `epsW_next,{0,1,2} <= l_{0,1,2} + k0 epsW_{0,1,2} + ...`.

Required index set (from `assembly.coefficients` over m in {1,2,3,5}):
`W_{r,t-r-1}` for `t < m`, `r < t` — i.e. `(r,j)` with `r+j <= 3`.

## 7. The exact K1 target `M_R2`  — NOT the P5X `M_2`

Two different quantities carry similar names. The K1 obligation is:

```text
   ledger.py :  R(e) in R_interval + Delta * D_interval + [ -rho^2 M_R2/2 , +rho^2 M_R2/2 ]
                W_cover_exact = rho * mag(D_interval) + rho^2 * M_R2 / 2
   assembly.py: M_R2 = mag(R2_interval) >= sup_{e in cell} | R''_{D,m}(e) |
```

> **`M_R2` is the whole-cell bound on the SECOND `e`-DERIVATIVE of `R_{D,m}`.**
> It is *not* `sup_e E_e[Rbar^2]`. That object is the P5X theorem-consumer
> scalar `M_2` (`EXACT_SR_TARGET.md` §5), which feeds `P5X-T4/T6/T9` and is
> **not** a K1 cover obligation. `S_{D,m}(e) = E_e[Rbar^2] - R_{D,m}(e)^2` and the
> pair functions `G_{r,r'}` are likewise P5X-level and are NOT required by the K1
> certificate. Implementing `M_2` in place of `M_R2` would leave every K1 cover
> obligation undischarged while appearing to succeed.

So the SR curvature obligation is `R2_interval` assembled at `k = 2` from
`H_r = F_r''` and `W''_{r,j}`, uniformly over the cell, then
`M_R2 = mag(R2_interval)`.

## 8. Object map — equations to implementation

| frozen object | count/cell | equation | module symbol |
|---|---|---|---|
| `h_1..h_4` | 4 | §1, §4, §5 chain | `sr_objects.h_chain` |
| `S_0..S_4` | 5 | `S_0=rho_1`, `S_j=K_z h_j` | `sr_objects.s_chain` |
| `F_0..F_4` | 5 | `(I-K)F_r = S_r + e h_1` | `sr_resolvent.solve_F` |
| `dF_0..dF_4` | 5 | `(I-K)D_r = K'F_r + S_r' + h_1 + e h_1'` | `sr_resolvent.solve_D` |
| dependency bundle | 1 | h/S derivatives + `W_{r,j}` orders 0,1 | `sr_objects.dependency_bundle` |
| curvature (per m) | 4 | `(I-K)H_r = K''F_r + 2K'D_r + S_r'' + 2h_1' + e h_1''` | `sr_resolvent.solve_H` |
| assembly (per m) | 4 | §2 with `c_{m,t}=1/t-1/m` | `assembly.assemble` (frozen, reused) |
| far-field | 1 | inherited `SR_FAR_FIELD = PASS` | not recomputed |

19 objects + 1 + 4 + 4 = 28 per cell; 28 * 316 + 1 = **8,849** SR top-level
obligations, machine-confirmed against `universe.work_ids()`.

## 9. Numerical route (justified, not copied)

Panel/patch enclosure follows the Task1R repair, which is the only SR path with
a PASS verdict:

* bivariate Taylor models in `(alpha, zeta)` / `(beta, zeta)` with rigorous
  remainder; **truncate the patch-local variable at EVERY product**, never once
  at the end (the Task-1 late-re-expansion defect);
* softplus enclosure by `softplus_local_enclosure` at degree 8, coefficients
  expanded at an interval centre so inclusion isotonicity gives a valid Lagrange
  remainder;
* `N_k` by the exact centred Gaussian moment recursion, with the sharp
  `|N_k| <= 2 phi_max h^{k+1}/(k+1)` tail (a factor `(k+1)` better than the
  superseded `|N_k| <= h^k N_0`);
* candidates as LOW-degree (<= 12) dyadic/Chebyshev objects; a high-degree
  closed form may be retained only as a certification reference and must never
  be handed to the kernel path (the Gate-2C degree-120/121 blow-up);
* asymmetric `P1` rule/check thresholds (the Gate-2F repair of the Gate-2E
  knife edge);
* all arithmetic Arb, outward rounded, at the frozen 256 bits.
