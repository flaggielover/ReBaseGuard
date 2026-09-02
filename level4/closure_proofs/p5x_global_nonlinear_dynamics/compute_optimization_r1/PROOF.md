# P5X Compute Optimization R1 — proof of the drift-explicit resolvent bound

Everything here is proved from the frozen model. Nothing imports an empirical
monotonicity, and in particular nothing uses the statement
`sup_e E[tau|e] = E[tau|0]`, which P5 records as open.

Notation: frozen CUSUM `k = 1/2`, `h = 5`; innovations `z_t ~ iid N(-e, 1)`;
`S^+_t = max(0, S^+_{t-1} + z_t - k)`, `S^-_t = max(0, S^-_{t-1} - z_t - k)`;
`tau = inf{t >= 1 : max(S^+_t, S^-_t) >= h}` (inclusive, tested after the
update); `K_e` the killed pre-alarm kernel of `P5X-T1`. Take `e >= 0`
throughout; `e < 0` follows by the reflection symmetry `P5-T3`.

---

## L-R1.0 — the quantity to be bounded

`K_e` is a positive operator, so `‖K_e^n‖_inf = ‖K_e^n 1‖_inf = sup_x P_x(tau > n)`,
and (`PROOF.md` `L1.4` of the parent namespace)

```text
‖(I - K_e)^{-1}‖_inf = sup_x E_x[tau] .
```

## L-R1.1 — from a block bound to a resolvent bound

**Claim.** If `q_n := inf_x P_x(tau <= n) > 0` for some `n >= 1`, then
`‖(I - K_e)^{-1}‖_inf <= n / q_n`.

**Proof.** `‖K_e^n‖ = sup_x P_x(tau > n) <= 1 - q_n =: beta < 1`, and
`‖K_e^m‖ <= 1` for every `m >= 0` since `K_e` is sub-Markov. Writing
`j = in + r` with `0 <= r < n`,

```text
sum_{j>=0} ‖K_e^j‖ = sum_{i>=0} sum_{r=0}^{n-1} ‖K_e^{in+r}‖
                   <= sum_{i>=0} n ‖K_e^n‖^i  <=  n sum_{i>=0} beta^i = n/(1-beta) = n/q_n ,
```

using `‖K^{in+r}‖ <= ‖K^n‖^i ‖K^r‖ <= beta^i`. The Neumann series converges and
its norm is bounded by that sum. `[]`

This is the same inequality R-A′ used; only the *supply* of `q_n` changes.

## L-R1.2 — one-sided domination

**Claim.** For every state `x = (x^+, x^-)` and every `n`,
`P_x(tau <= n) >= P^{minus}_{x^-}(sigma <= n)`, where `sigma` is the hitting
time of `h` by the **minus arm alone**, started at `x^-`.

**Proof.** The minus-arm recursion inside the two-sided detector is exactly the
stand-alone recursion (the two arms share the innovation stream but do not
interact), and `{sigma <= n} subset {tau <= n}` pathwise because
`max(S^+_t, S^-_t) >= S^-_t`. `[]`

Under drift `-e` with `e >= 0` the minus arm is the arm **aligned** with the
drift: its increment is `V_t := -z_t - k`, and `-z_t ~ N(e, 1)`, so
`V_t ~ N(e - k, 1)`. (For `e < 0` use the plus arm; by `P5-T3` the two cases are
mirror images.)

## L-R1.3 (M1) — `H_t` is nondecreasing in the starting state

Let `H_t(x) := P(sigma <= t | S^-_0 = x)` for the one-sided recursion
`S_t = max(0, S_{t-1} + V_t)`.

**Claim.** `x <= y` implies `H_t(x) <= H_t(y)` for every `t >= 0`.

**Proof.** Couple the two chains on the same innovation stream `(V_t)`. The map
`s -> max(0, s + v)` is nondecreasing in `s` for each fixed `v`, so by induction
`S_t(x) <= S_t(y)` pathwise for all `t`. Hence
`{sigma(x) <= t} = {max_{s<=t} S_s(x) >= h} subset {max_{s<=t} S_s(y) >= h}`,
and the probabilities are ordered. `[]`

**Consequence (the envelope is a bound, not a sample).** Partition `[0, h)` into
`cells` intervals with left endpoints `x_0 = 0 < x_1 < ... `. If
`lower_t[j] <= H_t(x_j)` for all `j`, then for every `y in [x_j, x_{j+1})`,
`H_t(y) >= H_t(x_j) >= lower_t[j]`. So a step function built from left-endpoint
values is a genuine pointwise lower envelope of `H_t` on the continuum. No state
is sampled in the sense of being *assumed* representative.

**Consequence (the recursion preserves the envelope).** With `r(x) := P(x + V >= h)`
the one-step alarm probability and `p(x, j) := P(max(0, x+V) in cell_j, x + V < h)`,

```text
H_t(x_i) = r(x_i) + E[ H_{t-1}(S_1) ; no alarm ]
         >= r(x_i) + sum_j p(x_i, j) * min_{y in cell_j} H_{t-1}(y)
         >= r(x_i) + sum_j p(x_i, j) * lower_{t-1}[j]  =:  lower_t[i] ,
```

by induction from `lower_0 = 0`. Every `r(x_i)` and `p(x_i, j)` is an exact
Gaussian expression evaluated in outward-rounded interval arithmetic, and the
implementation additionally asserts that each row's total mass encloses `1`, so
no probability can leak. `[]`

## L-R1.4 (M2) — `H_t(0)` is nondecreasing in the drift, for the aligned arm

**Claim.** Let `mu_1 <= mu_2` and let `H_t(x; mu)` be as above with
`V ~ N(mu, 1)`. Then `H_t(x; mu_1) <= H_t(x; mu_2)`.

**Proof.** Couple `V_t^{(i)} = xi_t + mu_i` with a common `xi_t ~ N(0,1)`. Then
`V_t^{(1)} <= V_t^{(2)} `pathwise, and `s -> max(0, s+v)` is nondecreasing in
both arguments, so by induction `S_t^{(1)} <= S_t^{(2)}` pathwise; the hitting
times satisfy `sigma^{(2)} <= sigma^{(1)}` pathwise, and the claim follows. `[]`

With `mu = |e| - k`, `H_t(0; e)` is nondecreasing in `|e|`.

> **What this is, and what it is not.** This is a coupling statement about a
> **one-dimensional, one-sided** random walk with stochastically ordered
> increments. It is *not* a statement about the two-sided alarm time `tau`,
> whose monotonicity in `e` is unproved (`DEFECT_REGISTER.md` `D3`), and it is
> *not* the open claim `sup_e E[tau|e] = E[tau|0]`. Nothing below uses either.

**Consequence (validity on the declared cell).** For a cell
`e in [e_lo, e_hi]` with `0 <= e_lo`, evaluating the minorant at `e_lo` gives a
lower bound on `H_t(0; e)` valid for **every** `e` in the cell, hence a `q_n`
valid for the whole cell.

## L-R1.5 — the bound, assembled

Combining `L-R1.2`, `L-R1.3`, `L-R1.4`: for every `e in [e_lo, e_hi]` and every
`t >= 1`,

```text
inf_x P_x(tau <= t)  >=  H_t(0; e)  >=  H_t(0; e_lo)  >=  lower_t[0] ,
```

so by `L-R1.1`, for every `t` with `lower_t[0] > 0`,

```text
‖(I - K_e)^{-1}‖_inf  <=  t / lower_t[0] ,
and therefore   C_opt := min_t  t / lower_t[0]   is a valid bound for the cell.
```

Taking the minimum over `t` is legitimate because each `t` gives an
independently valid bound.

## L-R1.6 — the five obligations of brief §5, checked

| obligation | discharge |
|---|---|
| 1. the new minorant is rigorous | `L-R1.3`: left-endpoint step function is a pointwise lower envelope by state monotonicity, propagated by an induction that only ever replaces a value by a smaller one; all arithmetic outward-rounded; row mass balance asserted |
| 2. the resolvent upper bound is rigorous | `L-R1.1`, an exact Neumann-series estimate; no approximation |
| 3. monotone in the required variables | `L-R1.3` in the state (`M1`), `L-R1.4` in the drift (`M2`); both proved by pathwise coupling |
| 4. cannot underestimate the true certified error | the enclosure is `|g - ghat| <= C delta`; a **smaller valid** `C` still satisfies the inequality because `C_opt >= ‖(I-K_e)^{-1}‖` is proved. Underestimation would require `C_opt` to fall below the true resolvent norm, which `L-R1.5` forbids |
| 5. preserves interval containment | every step is an inequality in the safe direction and every arithmetic operation is an outward-rounded Arb ball; the final bound is read at the conservative endpoint (`lower_t[0].lower()`, then `t / that`) |
| 6. valid on the exact declared cell | `L-R1.4` transports `e_lo` to the whole `[e_lo, e_hi]`; the implementation takes `e_lo` as an exact rational and the sub-cells tile the cell exactly |
| 7. no unproved global monotonicity | `M1` and `M2` are proved here; `D3`'s two-sided claim and P5's `sup_e A(e) = A(0)` are **not used**, and no P5/P7 empirical monotonicity enters |

## L-R1.7 — consistency with the already-certified `e = 0` value

At `e = 0` the substitution `k -> k - |e|` is the identity, so the minorant
reduces exactly to the configuration certified as `N-01`
(`closure/04_ARB_CERTIFICATE.md`), which asserts `H_250(0) >= 0.19` and hence
`C <= 250/0.19 = 1315.789...`. The `min_t` rule can only improve on that, since
`t = 250` is in its range; the self-test asserts
`C_opt(e = 0) <= 1315.79` as an external consistency check against an
independently replayed certificate.
