# Method notes for the implementation namespace

Diagnostic and design documentation. Non-result-bearing. Nothing here
reinterprets the frozen specification; where a construction is chosen, the
frozen clause that authorises it is quoted.

## 1. Why the interval-`e` residual is not the whole-cell certificate

ERROR_ALGEBRA section 3 requires

    epsH_r <= C*(deltaH_r + k2*epsF_r + 2*k1*epsD_r + epsS2_r)

with "All quantities on this right-hand side ... uniform cell bounds, not the
midpoint versions used for R_interval and D_interval", and adds that "A
state-only dyadic candidate may be constant in e over the cell; its interval-e
residual must bound the true operator throughout the cell."

The literal reading -- substitute an Arb ball for `e` in the frozen
recentred-Hermite/Bernstein residual machinery -- is rigorous but produces
nothing usable. Measured on this host, at the frozen order 120 and 256 bits:

```text
detector cell   rho          residual at exact e0     residual with e = [left,right]
CUSUM    0      2.54e-04     3.6901e-06               1.45567e+42
CUSUM    325    9.62e-02     1.9616e-05               2.28918e+60
```

The cause is structural, not a tuning failure. The frozen construction expands
`phi(z+e)` to order 120 and integrates against `z` over a window of half-width
`11/2`, so the intermediate coefficients reach `(11/2)^121 ~ 1e89` and the
result is small only through massive cancellation. Interval arithmetic cannot
preserve that cancellation: any positive width on the Hermite coefficients is
amplified by those z-powers. Reducing the Taylor order would repair the
conditioning but is a degree change, which the frozen precision policy forbids
(`DEGREE_ADAPTATION_ALLOWED = false`).

## 2. The construction actually used: mean-value extension

Every candidate in the DAG is a state-only polynomial, fixed once the cell's
exact midpoint is chosen, and therefore constant in `e` across the cell. So for
a residual `r(x;e)` built from those candidates,

```text
r(x;e) - r(x;e0) = int_{e0}^{e} d_s r(x;s) ds ,     |e - e0| <= rho
sup_{x, e in cell} |r(x;e)|  <=  sup_x |r(x;e0)|  +  rho * Env
Env >= sup_{x, e in cell} |d_e r(x;e)|
```

and because the candidates do not depend on `e`, `d_e r` contains only
DIFFERENTIATED OPERATORS applied to fixed candidates. `Env` is therefore a
finite sum of (certified operator norm) x (certified candidate sup norm). This
is exactly the device ERROR_ALGEBRA section 2 authorises: "Use certified
operator norm bounds j_k over the whole cell; rigorous whole-line absolute
Gaussian moments are admissible. Do not use sampled operator norms."

The resulting `delta_cell` bounds the residual simultaneously at every `e` in
the cell. It is a whole-cell certificate, not a midpoint sample, not a finite
difference, and not a Monte-Carlo or grid maximum.

Per-object envelopes (`k_i` and `j_i` are the certified operator norms,
`sup` denotes the certified Chebyshev sup norm of a candidate):

```text
h_j^(k)      Env = sum_i C(k,i) k_(i+1) sup|hhat_(j-1)^(k-i)|
S_r^(k)      Env = sum_i C(k,i) j_(i+1) sup|hhat_r^(k-i)|
F_r          Env = k_1 sup|Fhat_r|                       (+ 2 sup|phi'|  for r=0)
D_r          Env = k_1 sup|Dhat_r| + k_2 sup|Fhat_r|     (+ 2 sup|phi''| for r=0)
H_r          Env = k_1 sup|Hhat_r| + k_3 sup|Fhat_r|
                   + 2 k_2 sup|Dhat_r|                   (+ 2 sup|phi'''| for r=0)
W_(r,j+1)^(k) Env = sum_i C(k,i) k_(i+1) sup|What_(r,j)^(k-i)|
```

The `r = 0` extra terms exist because the `S_0` source is kept in closed form and
so is genuinely `e`-dependent inside the residual.

### 2.1 The closed-form leaves need an envelope too

`h_1^(k)` and `S_0^(k)` carry no equation defect: they are exact closed forms.
But they are evaluated AT `e0`, so they are fixed functions of `x` while the
true objects move with `e`. Their whole-cell errors therefore carry the same
mean-value term as everything else, using

```text
h_1^(k+1) = -S_0^(k)          Env(h_1^(k))  = 2 sup|phi^(k)|
d_e S_0^(k) = S_0^(k+1)       Env(S_0^(k))  = 2 sup|phi^(k+1)|
```

Omitting these would have made the curvature chain silently midpoint-only. They
are included.

## 3. Certified operator norms

Under `e`-free state limits, differentiation under the integral has no boundary
term, so `||d_e^i K_e|| <= int_R |phi^(i)|` and

```text
k_0 = 1
k_1 = 2 phi(0)                       = 0.797884560803...
k_2 = 4 phi(1)                       = 0.967882898077...
k_3 = 2 phi(0) + 8 phi(sqrt 3)       = 1.510013000133...
k_i <= sqrt(i!)                        (Cauchy-Schwarz, int He_i^2 phi = i!)
```

each taken as the minimum of the closed form and the Cauchy-Schwarz bound. The
first three are exactly the values the frozen ERROR_ALGEBRA names.

For the z-weighted operator, `|z| = |y - e|` gives
`||d_e^i K_(z,e)|| <= M_i + |e| k_i` with

```text
M_0 = 2 phi(0)      M_1 = 1      M_2 = 8 phi(1) - 2 phi(0) = 1.137881235...
```

`M_2` independently reproduces the `1.13788` constant already frozen in the
raw-variable certifier, which is a useful external check on this derivation.

Finally `J_i = K_(z,e)^(i) + e K_e^(i) + i K_e^(i-1)` gives
`j_i <= jz_i + e_max k_i + i k_(i-1)` with `e_max` the exact supremum of `|e|`
on the declared cell.

Pointwise suprema reuse the FROZEN Cramer constant already binding in
`ra_certifier.taylor_remainder`: `sup|phi^(n)| <= 1.086 sqrt(n!) / sqrt(2 pi)`.

## 4. Truncation allowance at derivative order two

The frozen series truncates `phi` at order `N = 120`. For derivative order `i`
the Lagrange remainder of the degree-`(N-i)` Taylor polynomial of `phi^(i)` is

```text
sup|phi^(N+1)| * R^(N-i+1)/(N-i+1)!  =  eps_z * (N+1)!/((N+1-i)! R^i)
                                    <= eps_z * (N+1)^i        for R >= 1
```

with `eps_z = taylor_remainder(N, 11/2)`. At `i = 1` this reproduces the frozen
`(order+1)*eps_z` allowance exactly; `i = 2` is the new case and is covered by
the same rule. No new constant and no precision escalation is introduced.

## 5. Arb scalar bounds are radius-zero

Arb order comparisons are certified, so `ball >= ball` is FALSE whenever the
radius is positive -- even for the same object. Every certified scalar bound
(delta, envelope, operator norm, eps node) is therefore normalised through
`intervals.tight_upper`, which returns a radius-zero Arb upper endpoint.
Quantities that genuinely carry two-sided information -- `R_interval`,
`D_interval`, `R2_interval` -- are NOT normalised and stay balls.

## 6. Threading and CPU accounting

CPU is accounted with `process_time()`, which sums every thread of the process.
Left at their defaults, FLINT and OpenBLAS ran the workers at ~156% CPU across
15 threads, which both violates the frozen `oversubscription_allowed: false`
policy and silently inflates measured CPU-seconds. Every measurement in
`benchmarks/` was taken with one FLINT thread and one BLAS thread per worker
(`intervals.pin_single_thread`), verified at 100% CPU and 1 thread per process.
