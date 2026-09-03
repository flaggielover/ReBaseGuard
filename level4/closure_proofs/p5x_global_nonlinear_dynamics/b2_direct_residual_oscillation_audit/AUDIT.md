# P5X — B2 Direct-Residual Oscillation Feasibility Audit

`PRE_FREEZE_CERTIFICATION_ARCHITECTURE_AUDIT`. Not R9. **No binding checkpoint
was created and no binding gate was run.**

```text
ANSWER   NO -- not at a usable cost.
         The direct residual gradient is exact and pointwise tiny, but its
         rigorous enclosure stays ~89x too wide, and width (S1) and cost (S2)
         are never simultaneously satisfiable.
S1 WIDTH  FAIL at every grid that satisfies S2
S2 COST   FAIL at every grid that satisfies S1
READY TO FREEZE  NO
BLOCKER   DR-B4 (cross-term cancellation not representable), with
          DR-B2 (kernel derivative) and DR-B3 (moving boundary) as the carriers
```

---

## 1. Exact residual and its exact gradient

```text
r = ghat - rho_1 - K_e ghat

dr/dzeta^+ = ghat_x - (K^{E+} ghat_x) + [ ghat(q(.,u)) - u ] phi(u+e) / w^+
dr/dzeta^- = ghat_y - (K^{E-} ghat_y) + [ ghat(q(.,l)) - l ] phi(l+e) / w^-
```

with `E^+ = e^{z-1/2}`, `E^- = e^{-z-1/2}`, `w^{+/-} = 1/A + zeta^{+/-}`.

**The two boundary contributions are combined algebraically before any interval
evaluation.** From `rho_1 = phi(u+e) - phi(l+e) - e[(1-Phi(u+e)) + Phi(l+e)]`:

```text
d rho_1/du = -(u+e) phi(u+e) + e phi(u+e) = -u phi(u+e)
d rho_1/dl =  (l+e) phi(l+e) - e phi(l+e) =  l phi(l+e)
du/dzeta^+ = -1/w^+ ,  dl/dzeta^- = 1/w^-       (R8-corrected w^-)
```

so `rho_1`'s moving-limit term `+u phi(u+e)/w^+` merges with the kernel's
boundary term `-ghat(q(.,u)) phi(u+e)/w^+` into the single bracket above.

**Validation.** Central finite differences with a step sweep:

| `h` | relative difference |
|---|---|
| `1e-5` | `2.115e-06` |
| `1e-6` | `2.115e-08` |
| `1e-7` | `2.115e-10` |
| `1e-8` | `2.115e-12` |

Perfect `O(h^2)` decay — the discrepancy is the *reference's* truncation, not the
formula. Checked at five points including strongly off-diagonal
`(0.023, 0.700)`, `(0.700, 0.023)` and near-boundary `(0.95, 0.05)`.
**`DIRECT_RESIDUAL_POINT_GRADIENT = PASS`, error `2.115e-12`.**

## 2. Diagnostic scale (25x25 sample, non-rigorous)

```text
max |r|         = 1.220534e-05
max |dr/dzeta^+| = 7.574454e-03
max |dr/dzeta^-| = 1.050208e-02
max ||grad r||_1 = 1.807654e-02
```

## 3. Control: does combining help? **No.**

On the R8 worst cell `(385,382)` at `G = 1024`, evaluating the combined gradient
in the monomial representation:

| term | value | radius |
|---|---|---|
| `ghat_x` | `+1.160293` | `6.386840e+02` |
| `K^{E+} ghat_x` | `+0.577736` | `5.684120e+04` |
| boundary bracket | `-0.566589` | `5.513317e+04` |
| **combined `dr/dzeta^+`** | `+1.596754e-02` | **`1.126131e+05`** |

Naive three-box sum of radii: `1.126131e+05`. **Combining gain `1.0000x`.**
Algebraic combination is worthless here because each term is *already* destroyed
by the monomial basis before any subtraction happens.

## 4. Bernstein-bounded direct gradient — the real test

Using the stable representation throughout: sharp de Casteljau cell restriction
for `ghat_x`; elevated degree-32 hulls for the kernel term; and an exact
structural refinement for the boundary term.

**Exact structural fact used.** At `z = u`, `zeta'^+ = w^+ e^{u-1/2} =
w^+ e^{1/2 - log w^+ - 1/2} = 1` **exactly**; likewise `zeta'^- = 1` at `z = l`.
So `ghat(q(.,u))` lives on the *edge* `zeta^+ = 1`, whose Bernstein hull is the
boundary control row:

| hull | width |
|---|---|
| `ghat` full | `1.2409` |
| `ghat` edge `zeta^+ = 1` | **`0.2895`** |
| `ghat` edge `zeta^- = 1` | `0.8849` |
| `ghat_x` elevated (deg 32) | `1.0295` |
| `ghat_y` elevated (deg 32) | `0.6668` |

Result on cell `(385,382)`:

| component | width |
|---|---|
| `ghat_x` (sharp cell hull) | `1.742e-07` — essentially exact |
| `K^{E+} ghat_x` (positivity on the global hull) | **`0.6033`** |
| boundary bracket (edge hull) | `0.0738` |
| **`dr/dzeta^+` total** | **`6.771029e-01`** |
| `K^{E-} ghat_y` | **`0.5033`** |
| boundary bracket (minus) | `0.4441` |
| **`dr/dzeta^-` total** | **`9.473938e-01`** |

Against the true sampled values: **`89x` and `90x` too wide**.

## 5. Width vs cost — they never both close

Exact `F3` requirement, using the R8 enclosure formula and
`C_SR([0.24,0.26]) = 216.963` with the `e`-cell contribution `0.01`:

```text
required_delta_for_F3 = (0.2 - 0.01) / 216.963 = 8.757254e-04
```

| grid | `delta_new` | vs R8 `5.0109e-3` | `F3` | cells | SR `m=1` CPU-h | cost class |
|---|---|---|---|---|---|---|
| 256 | `6.3579e-03` | `0.79x` (**worse**) | FAILS | `65536` | `76` | `COST_STRONG` |
| 1024 | `1.5986e-03` | `3.13x` | FAILS | `1048576` | `1216` | `COST_WEAK` |
| 4096 | `4.0881e-04` | `12.26x` | **MEETS** | `1.68e7` | `19457` | `COST_FAIL` |
| 16384 | `1.1136e-04` | `45.00x` | MEETS | `2.68e8` | `311311` | `COST_FAIL` |

`S1` needs grid `>= 4096`; `S2` (`<= 500` CPU-h) needs grid `<= ~650`. **No
overlap.** Per the audit's own binding pre-freeze rule, the repair is **not
frozen**.

At the R8 grid the direct route gives `1.5986e-03` against R8's `5.0108623e-03`
— a real `3.13x` improvement, but `1.83x` short of `F3` and at `2.4x` the cost
ceiling.

## 6. Where the loss enters — `DR-B4`

`ghat_x` is enclosed essentially exactly (`1.7e-07`). The loss is in
`K^{E+} ghat_x` (`0.6033`) and `K^{E-} ghat_y` (`0.5033`), plus the minus-chart
boundary bracket (`0.4441`).

The kernel term is an *average of `ghat_x` over the image of the cell*, and the
image under the live `z`-range covers essentially the whole domain. Any
hull-based bound must therefore use `ghat_x`'s range over `[0,1]^2`, giving
`~1.03 x int E^+ phi = 0.60`. But the true value `0.578` cancels against
`ghat_x(zeta) = 1.160` and the boundary bracket `-0.567` to leave `1.6e-2`.

**That cancellation is between values of the same function at *different points*
— `zeta` versus its image `q(zeta,z)`.** No interval architecture that bounds
each factor by a range over a set can represent it. This is `DR-B4`, carried by
`DR-B2` (kernel derivative) and `DR-B3` (moving boundary).

## 7. What would close it

At grid `650` (the largest grid meeting `S2`, `~490` CPU-h) the requirement is
`2h(w_+ + w_-) <= 8.63e-4` with `h = 7.7e-4`, i.e.
`w_+ + w_- <= 0.56` against the current `1.624`. **A `2.9x` tightening of the
gradient enclosure would make the whole architecture viable**, and it must come
from the two kernel terms, since `ghat_x` is already exact and the plus-chart
boundary bracket is only `0.074`.

The only mechanism that could deliver it is one that keeps `ghat_x(zeta)` and
`int ghat_x(q(zeta,z)) E^+ phi dz` **correlated** — for instance a rigorous
bound on `ghat_x(zeta) - ghat_x(q(zeta,z))` as a function of the displacement
`zeta -> q(zeta,z)`, using a Lipschitz/second-derivative bound on `ghat_x`
together with the closed-form displacement, rather than bounding the two
evaluations independently. That is a genuinely different construction and would
need its own audit; nothing in it is established here.

## 8. Invariants

`z_panels = 0`, `softplus_approximations = 0` throughout. The R6 fast kernel,
the `xi` transform, the candidate, the R8 `w^-` correction and the R8 Bernstein
representation are all reused unchanged. `B1` was not touched;
`C_SR([0.24,0.26]) = 216.963` is used as given.
