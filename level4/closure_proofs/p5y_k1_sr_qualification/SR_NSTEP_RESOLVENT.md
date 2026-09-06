# SR n-step resolvent — derivation, survival interpretation, and governance

Resolves blocker 1 of `RESULTS.md`. Written before implementation; every claim
here is either proved on this page or explicitly marked EXPLORATORY.

---

## 1. The operator, domain and norm

```text
X        = C([0, b_SR]^2)  with  ||f||_inf = sup_{y in [0,b_SR]^2} |f(y)|
b_SR     = log(1 + A) = 6.2574494292271356...      state domain (erratum D1)
c_SR     = log A + 1/2 = 6.7555314643214731...     alarm margin
(K_e f)(y) = int_{l(y)}^{u(y)} f(q_SR(y,z)) phi(z + e) dz
l(y) = y^- - c_SR ,  u(y) = c_SR - y^+
q_SR(y,z) = ( softplus(y^+ + z - 1/2), softplus(y^- - z - 1/2) )
```

`K_e` maps `X` into itself and is a **positive** operator: `phi > 0` and the
domain of integration does not depend on `f`, so `f >= 0` implies `K_e f >= 0`.
`softplus` maps into `[0, b_SR]` on the continuation region, so `q_SR` stays in
the domain and the composition is well defined.

## 2. The positivity identity  ||T||_inf = ||T 1||_inf

> **Lemma 1.** Let `T` be a positive bounded operator on `X`. Then
> `||T||_inf = ||T 1||_inf`, where `1` is the constant function.

*Proof.* For any `f` with `||f||_inf <= 1` we have `-1 <= f <= 1` pointwise, so by
positivity `-T1 <= Tf <= T1`, hence `|Tf(y)| <= (T1)(y) <= ||T1||_inf` for every
`y`. Taking the supremum over such `f` and over `y` gives `||T|| <= ||T1||_inf`.
Conversely `f = 1` is admissible and gives `||T|| >= ||T1||_inf`. []

`K_e` is positive, and products of positive operators are positive, so Lemma 1
applies to every `K_e^j`. **This turns an operator-norm computation into a single
function evaluation** and is the reason the whole scheme is affordable:

```text
    a_j := ||K_e^j||_inf = ||K_e^j 1||_inf
```

## 3. Survival interpretation

> **Lemma 2.** `(K_e^n 1)(y) = P_y(tau > n)`, the n-step survival probability
> from state `y`, where `tau` is the frozen inclusive stopping time.

*Proof.* Induction. `n = 0` is trivial. `(K_e 1)(y) = int_{l(y)}^{u(y)} phi(z+e) dz
= P(l(y) < z < u(y))` which is exactly the probability that the alarm test
`max(v^+, v^-) >= log A` FAILS at this step, i.e. `P_y(tau > 1)`; the frozen
continuation interval was derived from that test. For the step, condition on the
first innovation: `K_e^{n+1} 1 (y) = int_{l(y)}^{u(y)} (K_e^n 1)(q_SR(y,z)) phi(z+e) dz`,
and `q_SR(y,z)` is the post-update state, so the inner factor is
`P_{q_SR(y,z)}(tau > n)` by the inductive hypothesis. The Markov property gives
`P_y(tau > n+1)`. []

Combining Lemmas 1 and 2:

```text
    a_j = q_j = sup_{y in [0,b_SR]^2} P_y(tau > j)
```

so `||K_e^n||_inf` is exactly the **worst-case n-step survival mass**, which is
what Phase 2 asked for, and it is a *scalar maximum of one certified function*,
not a generic operator norm.

## 4. Why the one-step bound is hopeless, structurally

At the reset state `y_0 = (0,0)` the continuation interval is the widest possible,
`(-c_SR, c_SR)`, so

```text
    k0 = ||K_e|| = Phi(c_SR + e) - Phi(-c_SR + e)  =  1 - 1.42e-11   at e = 0
```

This is not a defect of the bound: a single step really almost never alarms,
because `c_SR = 6.7555` is 6.76 standard deviations away. The contraction is a
**many-step** effect. Any scheme resting on `1 - ||K||` is therefore doomed, and
`||K^n|| <= ||K||^n` inherits the same defect (`k0^n ~ 1 - 1.42e-11 n`), which is
why `sr_operators.resolvent_bound` rejects `k0^n` programmatically.

## 5. The finite geometric decomposition

> **Theorem.** Let `P_n = sum_{j=0}^{n-1} K^j` and suppose `q_n = ||K^n|| < 1`.
> Then `(I - K)` is invertible and
> ```
>     (I - K)^{-1} = P_n (I - K^n)^{-1}
>     ||(I - K)^{-1}||  <=  ||P_n 1||_inf / (1 - q_n)
> ```

*Proof.* The algebraic identity `P_n (I - K) = (I - K) P_n = I - K^n` is the
telescoping sum, valid in any unital algebra. Since `q_n < 1`, the Neumann series
`(I - K^n)^{-1} = sum_{i>=0} K^{ni}` converges absolutely in operator norm and is
a genuine two-sided inverse of `I - K^n`. `K` commutes with `K^n` and hence with
`(I - K^n)^{-1}`, so

```text
   [P_n (I-K^n)^{-1}] (I - K) = P_n (I - K) (I-K^n)^{-1} = (I - K^n)(I-K^n)^{-1} = I
```

and symmetrically on the other side. Therefore `(I-K)^{-1} = P_n (I - K^n)^{-1}`.
Taking norms, `||(I-K)^{-1}|| <= ||P_n|| * ||(I-K^n)^{-1}|| <= ||P_n||/(1 - q_n)`,
and `P_n` is positive (a sum of positive operators) so Lemma 1 gives
`||P_n|| = ||P_n 1||_inf`. []

**Sharper form actually used.** `P_n 1 = sum_{j<n} K^j 1 = sum_{j<n} P_y(tau > j)
= E_y[tau ^ n]`, so

```text
    C_n := ||E_.[tau ^ n]||_inf / (1 - q_n)     and    ||(I-K)^{-1}|| <= C_n <= n/(1-q_n)
```

Note `||P_n 1||_inf` is computed as the sup of ONE function, which is strictly
sharper than `sum_j a_j` (the maxima of the `K^j 1` need not coincide).

**Sharpest possible constant.** By Lemmas 1 and 2, the exact value is
`||(I-K)^{-1}||_inf = sup_y sum_{j>=0} P_y(tau > j) = sup_y E_y[tau]` — the
worst-case mean time to alarm. `C_n` decreases monotonically to it as `n` grows,
so the scheme is not merely a bound but a convergent approximation from above.

## 6. What must be numerically certified

Only two scalars per drift, both suprema of explicitly certified functions:

```text
    q_n            = sup_y (K^n 1)(y)          must be certified < 1
    ||P_n 1||_inf  = sup_y sum_{j<n} (K^j 1)(y)
```

Both come from the SAME iteration `s_0 = 1, s_{j+1} = K s_j`, accumulating
`sum_j s_j` alongside. Requirements are in `SR_NSTEP_CERTIFIER.md` and
`code/sr_nstep.py`: Arb outward rounding, whole-domain enclosure (not a point
grid), monotonicity used only where proved, and an explicit interpolation
envelope. Because `s_j in [0,1]` for every `j` — a proved invariant, since
`s_j` is a probability — the iteration is self-stabilising and each step can be
intersected with `[0,1]` for free.

## 7. How the bound enters F / F' / F'' propagation

Unchanged in form; only the supplied constant changes. The frozen error algebra
(`depgraph.py`) is

```text
    epsF_r = C ( deltaF_r + epsS_r )
    epsD_r = C ( deltaD_r + k1 epsF_r + epsS1_r )
    epsH_r = C ( deltaH_r + k2 epsF_r + 2 k1 epsD_r + epsS2_r )
```

and the raw-variable value chain in `sr_propagate.resolvent_system` uses the same
`C`. Substituting `C_n` for the one-step constant multiplies the F/D/H bounds by
`(C_n/C_1)^{1,2,3}` respectively; `M_R2` scales like `C^3` (measured exponent
**2.97**, section 9).

## 8. EXPLORATORY n / q_n / C_n table

Float dynamic programme, `code/sr_survival_explore.py`, 48x48 state grid, 40-node
Gauss-Legendre in `z`, bilinear interpolation, 4.24 CPU-seconds total.
**These are estimates used only to choose `n`. They are NOT a certificate.**

| e | n=8 | n=16 | n=32 | n=64 | n=128 | n=256 | C_n at best n |
|---|---|---|---|---|---|---|---|
| 0.00 | 2885 | 942.8 | 618.4 | 524.3 | 487.4 | **471.0** | 471 (still falling) |
| 0.25 | 827.2 | 260.9 | 167.2 | 140.8 | 131.0 | **127.1** | 127 |
| 0.50 | 173.5 | 60.65 | 41.73 | 36.89 | 35.77 | **35.67** | 35.7 |
| 1.00 | 20.49 | 11.88 | 11.02 | 11.00 | 11.00 | **11.00** | 11.0 |
| 2.00 | 4.644 | 4.616 | 4.616 | 4.616 | 4.616 | **4.616** | 4.62 |

with the corresponding worst-case survival `q_n = sup_y P_y(tau > n)`, e.g. at
`e = 0.25`: `q_8 = 0.9903`, `q_32 = 0.8213`, `q_128 = 0.3601`, `q_256 = 0.1199`.

**Gain.** `7.03e10 -> ~127` at the central drift: between **eight and ten orders
of magnitude**, and the constant is now within a factor ~1.1 of its theoretical
floor `sup_y E_y[tau]`.

## 9. Drift dependence, and whether `n` can be global

`C` varies by a factor of **~100 across the drift range** (471 at `e=0` down to
4.62 at `e=2`), and the useful `n` varies with it:

```text
    e >= 2.0   n = 8    already gives q_n = 8.5e-3
    e =  1.0   n = 16   gives q_n = 0.128
    e =  0.5   n = 32   gives q_n = 0.419
    e =  0.25  n = 128  gives q_n = 0.360
    e =  0.0   n >= 256 gives q_n = 0.577   (and C_n has not yet converged)
```

> A single global `n` would have to be the worst case (`e -> 0`, `n >= 256`) and a
> single global `C` would have to be `~471` everywhere, discarding a factor of
> 100 at large drift. **`n` and `C` must be cell-local.**

This is governance-permitted: see `SR_RESOLVENT_GOVERNANCE.md`. `C` is a *nested
supporting constant* consumed inside the existing `F/dF/curvature` obligations,
not a top-level work ID. Making it cell-local changes no top-level obligation,
no detector scope, no cover geometry and no budget — the 17,978-unit universe is
untouched. What it does require is that each cell's certificate BINDS its own
`(n, q_n, ||P_n 1||, C_n)` into the scientific hash, so a constant certified for
one cell can never be silently reused on another. `ResolventCertificate` in
`code/sr_nstep.py` enforces exactly that.

## 10. Is the n-step resolvent alone enough?  NO — measured

### 10a. Where C actually comes from (governance correction)

`config/cells.json` already carries a per-cell `C_upper`, and the validated CUSUM
implementation reads it directly (`cusum_layer2.py:130`, `self.C = F(cell["C_upper"])`).
**`C` is frozen cover geometry, not a producer output.** SR consumes it the same
way, via `ResolventCertificate.from_frozen_cell`. The n-step machinery of sections
1-9 is therefore independent CORROBORATION, and a good one: the frozen constants
dominate the survival-theory estimates at every drift with a 1.4x-2.6x margin.
Full detail in `SR_RESOLVENT_GOVERNANCE.md`.

### 10b. Measured whole-cell width, with each cell's own frozen rho

An earlier probe used an artificial `rho = 1e-3` for all cells and reported that
large-drift cells fit inside `B_cover`. **That was an artefact of the fixed rho.**
The frozen geometry holds `rho * C_upper = 0.3133` invariant, so large-drift
cells have proportionally larger `rho`. With the real per-cell values, m = 2:

| cell | e0 | C_upper | rho | rho·\|D\| | rho²·M_R2/2 | utilisation |
|---|---|---|---|---|---|---|
| 0 | 2.60e-4 | 1205.94 | 2.60e-4 | 1.91e2 | 4.78e1 | **4.78e3** |
| 100 | 0.0691 | 674.57 | 4.64e-4 | 1.30e2 | 3.25e1 | **3.24e3** |
| 200 | 0.2284 | 216.17 | 1.45e-3 | 5.99e1 | 1.50e1 | **1.50e3** |
| 275 | 1.005 | 17.92 | 1.75e-2 | 1.57e1 | 4.10e0 | **3.97e2** |
| 292 | 2.019 | 6.59 | 4.75e-2 | 1.96e1 | 5.71e0 | **5.06e2** |
| 313 | 6.240 | 2.00 | 1.57e-1 | 1.75e6 | 1.34e6 | **6.18e7** |

**No sampled cell fits inside `B_cover`**; the best is 397x over. The dominant
term is the *linear* one `rho |D|`, about 4x the curvature term throughout,
because `|D|` inherits `C^2` from the norm tower.

Phase-7 diagnosis: **`NSTEP_HELPS_BUT_REFINEMENT_REQUIRED`**.

The residual gap is a norm-tower artefact, not a property of the true `R''`: the
chain bounds every object by `C x (operator norm) x (previous bound)`, as if every
derivative attained its worst case simultaneously at the same state and drift.
The repair is midpoint certification with only the *variation* carrying the
tower, designed in `SR_REFINEMENT_DESIGN.md`.
