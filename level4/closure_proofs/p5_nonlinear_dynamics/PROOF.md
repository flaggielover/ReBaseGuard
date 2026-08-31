# P5 proofs

Notation and conventions are exactly those of `DEFINITION_AUDIT.md`. Fix a
detector `D in {CUSUM(k=1/2,h=5), SR(A=520.886133602749)}`, a window `m >= 1`
and a reuse fraction `rho in [0,1]`.

**The common probability space.** This is the device that makes everything
below work. Within a cycle the simulator draws `raw_1, raw_2, ... ~ iid N(0,1)`
*whose law does not depend on `e`*, and feeds the detector `z_t = raw_t - e`.
So one probability space `(Omega, F, P)` carrying `omega = (raw_1, raw_2, ...)`
and an independent `F ~ N(0,1/m)` serves **every** entering error `e`
simultaneously; `e` enters only through the deterministic functionals
`tau(e, omega)`, `w(e, omega)`, `Rbar(e, omega)`. Write `F_t = sigma(raw_1, ..., raw_t)`.

---

## Proof of T1 (raw-mean representation)

Within cycle `j` the entering error `e_j` is a constant. Every element of the
reuse window is `z_{tau-r} = raw_{tau-r} - e_j`, and the frozen window mean uses
the truncated denominator `w_j`, so

```
zbar_j = (1/w_j) sum_{r<w_j} (raw_{tau_j-r} - e_j)
       = (1/w_j) sum_{r<w_j} raw_{tau_j-r}  -  (1/w_j) * w_j * e_j
       = Rbar_j - e_j .
```

Substituting into the frozen update `e_{j+1} = rho (e_j + zbar_j) + (1-rho) fresh_j`
gives `e_{j+1} = rho Rbar_j + (1-rho) fresh_j`. The cancellation is exact and
uses only that `e_j` is constant over the cycle and that the window denominator
equals the number of summands. `[]`

*Remark.* The cancellation would fail for the Stage-A convention with a fixed
denominator `m` on a truncated window; P5's identity is specific to the frozen
Stage-D convention A audited in `DEFINITION_AUDIT.md` §2.6, and this is checked
path-by-path in `tests/test_correspondence.py::test_window_denominator_is_truncated`.

## Proof of T2 (rho-factorisation)

`fresh_j` is independent of `(tau_j, raw_1, raw_2, ...)` with mean `0` and
variance `1/m`. Taking conditional expectation and variance of T1 given
`e_j = e`:

```
E[e_{j+1}|e]   = rho E[Rbar|e] + (1-rho) * 0                    = rho R(e)
Var(e_{j+1}|e) = rho^2 Var(Rbar|e) + (1-rho)^2 Var(fresh)       = rho^2 S(e) + (1-rho)^2/m .
```

Both are finite by T5. The identification `R'(0) = 1 - GammaTilde` follows from
P1/P2, whose conclusion is `d/de E[e_{j+1}|e]|_{e=0} = rho(1-GammaTilde)` for
every `rho`, and from the fact that `M = rho R` for every `rho`. `[]`

## Proof of T3 (symmetry)

Let `sigma: Omega -> Omega` be `raw_t -> -raw_t`; `sigma` preserves `P`
(the `raw_t` are iid symmetric). Under `sigma` and the substitution `e -> -e`,

```
z_t = raw_t - e   -->   -raw_t + e = -(raw_t - e) = -z_t .
```

*CUSUM.* `S^+ = max(0, S^+ + z - k)`, `S^- = max(0, S^- - z - k)`, both started
at `0`. Replacing `z -> -z` interchanges the two recursions verbatim, so
`(S^+_t, S^-_t) -> (S^-_t, S^+_t)`. The alarm test `max(S^+_t, S^-_t) >= h` is
symmetric in the pair, so `tau` is unchanged and the alarm arm is flipped.

*SR.* `y^+ = log(1+exp(y^+ + z - 1/2))`, `y^- = log(1+exp(y^- - z - 1/2))`, both
started at `0`, with the symmetric inclusive test on
`max(y^+_{t-1}+z_t-1/2, y^-_{t-1}-z_t-1/2) >= log A`. Same interchange.

Hence `tau` and `w` are invariant while `Rbar -> -Rbar`, so the conditional law
of `Rbar` given `-e` equals that of `-Rbar` given `e`. Taking mean and variance
gives `R(-e) = -R(e)`, `S(-e) = S(e)`, `A(-e) = A(e)`. `[]`

## Proof of T4 (uniform geometric stopping bound)

*CUSUM.* `S^+_t >= 0` always, and if `z_t >= 1` then
`S^+_t = max(0, S^+_{t-1} + z_t - 1/2) >= S^+_{t-1} + 1/2`. So from any
state `S^+ >= 0`, ten consecutive steps with `z >= 1` give `S^+ >= 5 = h`, i.e.
an alarm. Symmetrically ten consecutive steps with `z <= -1` alarm the minus arm.
Under `z ~ N(-e, 1)`:

```
e <= 0  =>  P(z >= 1)  = Phi(-1-e) >= Phi(-1),
e >= 0  =>  P(z <= -1) = Phi(-1+e) >= Phi(-1).
```

Partition time into blocks of ten steps. Each block, independently of the past
(the `z`'s are iid and the sufficient condition holds from *any* reachable
state), forces an alarm with probability at least `p_0 = Phi(-1)^10 = 1.0105e-8`.
Hence `P(tau > 10i) <= (1-p_0)^i` and

```
E[tau|e] <= 10 / p_0 = 9.8959e8      for every e in R.
```

*SR.* `y^+_{t-1} >= 0` always, and the plus-arm alarm test is
`y^+_{t-1} + z_t - 1/2 >= log A`, so a single step with `z_t >= log A + 1/2`
alarms from any state; symmetrically for the minus arm. With
`c = log A + 1/2 = 6.755531`, the same case split gives
`p_0 >= Phi(-c) = 7.1156e-12` per step, whence

```
E[tau|e] <= 1 / Phi(-c) = 1.4054e11    for every e in R.       []
```

These constants are deliberately crude: they are worst-case block bounds valid
for every `e`, not estimates of `sup_e A(e)` (measured at `465.1` for CUSUM and
`472.3` for SR, both attained at `e = 0`). Only finiteness and
`e`-independence are used below.

## Proof of T5 (uniform moment bound)

Fix `p >= 1`. Since `w >= 1` and `u -> u^{2p}` is convex, Jensen gives

```
Rbar^{2p} = ( (1/w) sum_{r<w} raw_{tau-r} )^{2p}  <=  (1/w) sum_{r<w} raw_{tau-r}^{2p}
                                                  <=  sum_{t=1}^{tau} raw_t^{2p} ,
```

the last step because the window `{tau-w+1, ..., tau}` is a subset of
`{1, ..., tau}` and all terms are non-negative and `1/w <= 1`.

`{tau >= t} = {tau <= t-1}^c in F_{t-1}` and `raw_t` is independent of `F_{t-1}`,
so by Tonelli

```
E[ sum_{t=1}^{tau} raw_t^{2p} | e ] = sum_{t>=1} P(tau >= t | e) E[raw^{2p}]
                                    = E[tau|e] * (2p-1)!! ,
```

finite by T4. Hence `E[Rbar^{2p}|e] <= (2p-1)!! C_D` for all `e`. For `e_{j+1}`,
convexity gives `(a+b)^{2p} <= 2^{2p-1}(a^{2p}+b^{2p})` and
`E[fresh^{2p}] = (2p-1)!!/m^p`, which yields the stated bound. For `p = 1` the
cross term vanishes exactly (`fresh` independent, mean zero), giving the sharper

```
E[e_{j+1}^2 | e] = rho^2 E[Rbar^2|e] + (1-rho)^2/m <= rho^2 C_D + (1-rho)^2/m . []
```

*Why this is the whole mechanism.* The bound is **independent of `e`**. No
Foster–Lyapunov function, no outer-drift inequality and no compact-set
decomposition is needed: T1 already makes the next state an average of at most
`m` standard normals. Any drift condition one could verify would be a weaker
consequence of this.

## Proof of T6 (Feller by a.s. local constancy)

Fix `e`. For fixed `omega`, every pre-alarm detector statistic is a finite
composition of continuous maps applied to `(raw_1 - e, ..., raw_t - e)` and is
therefore continuous in `e`. Under `P`:

* `tau(e, omega) < infinity` a.s. by T4;
* for each `t`, `P(S_t = h) = 0` (resp. `P(y_{t-1}+z_t-1/2 = log A) = 0`): the
  law of each statistic restricted to `(0, infinity)` is absolutely continuous,
  and the threshold is strictly positive. Summing over the a.s. finitely many
  `t <= tau` gives: a.s. every pre-`tau` comparison is strict and the terminal
  one is strict.

On that full-measure event there are finitely many strict inequalities in
continuous functions of `e`, so there is `eps(omega) > 0` with
`tau(e', omega) = tau(e, omega)` and the same alarm arm for `|e'-e| < eps`.
Since `Rbar(e', omega) = (1/w) sum raw_{tau-r}` involves no `e` at all, and
`w` is unchanged, `Rbar(e', omega) = Rbar(e, omega)`, hence
`e_{j+1}(e', omega, F) = e_{j+1}(e, omega, F)`.

For bounded continuous `h`,

```
| E[h(e_{j+1})|e'] - E[h(e_{j+1})|e] |  <=  2 ||h||_inf * P( eps(omega) <= |e'-e| ) --> 0
```

as `e' -> e`, because `eps > 0` a.s. So `P` is Feller. `[]`

## Proof of T7 (uniform ergodicity, uniqueness, all moments)

Write `B := sup_e E[e_{j+1}^2|e] <= rho^2 C_D + (1-rho)^2/m` (T5), and
`R* := sqrt(2B)`, `C := [-R*, R*]`.

**Step 1 — one-step return to `C` from anywhere.** Chebyshev:

```
P(|e_{j+1}| > R* | e)  <=  B / R*^2  =  1/2      for every e,
so   inf_{e in R} P(e, C) >= 1/2 .
```

**Step 2 — minorisation on `C`.** Let `c_D` be the one-step alarm margin from
the reset state: the plus arm alarms at `t = 1` iff `z_1 >= c_D`, with

```
c_CUSUM = h + k = 5.5,        c_SR = log A + 1/2 = 6.755531 .
```

Because `z_1 = raw_1 - x`, this is `raw_1 >= x + c_D`. Put

```
J := ( R* + c_D + 0.1 ,  R* + c_D + 0.6 )      (length 1/2).
```

For every `x in C` and every `u in J` we have `u > R* + c_D >= x + c_D`, so the
event `{raw_1 = u}` alarms at `t = 1`; then `w = min(m, 1) = 1` for **every**
`m`, so `Rbar = raw_1 = u`. Also `z_1 > 0` keeps the minus arm at its reset
value, so the alarm is the plus-arm one and `tau = 1` exactly. Therefore, for
every `x in C` and every Borel `A`,

```
P(x, A)  >=  Integral_J phi(u) * Q_u(A) du ,      Q_u := law of rho*u + (1-rho)*F .
```

* If `rho = 1` then `Q_u = delta_u`, so
  `P(x,A) >= Integral_{J cap A} phi(u) du >= phi(sup J) * Leb(J cap A)`, i.e.
  `P(x, .) >= delta * nu(.)` with `nu = Uniform(J)` and
  `delta = phi(sup J)/2 > 0`.
* If `rho < 1` then `Q_u` has the density
  `q_u(y) = sqrt(m)/((1-rho) sqrt(2 pi)) * exp(-m (y - rho u)^2 / (2 (1-rho)^2))`,
  and for `y, u in J`, `|y - rho u| <= |y-u| + (1-rho)|u| <= 1/2 + (1-rho) sup J`,
  so `q_u(y) >= q_min > 0` with `q_min` explicit. Hence
  `P(x, .) >= delta * nu(.)` with `nu = Uniform(J)` and
  `delta = phi(sup J) * q_min / 4 > 0`.

(For `rho = 0` the statement is trivial: `P(x,.) = N(0,1/m)` for every `x`.)

**Step 3 — two-step Doeblin condition on the whole line.** For every `e in R`
and Borel `A`,

```
P^2(e, A)  =  Integral P(e, dx) P(x, A)
           >= Integral_C P(e, dx) * delta * nu(A)
           =  P(e, C) * delta * nu(A)
           >= (delta/2) * nu(A)  =:  delta' * nu(A) .
```

So the *entire state space* is a small set for `P^2`. Doeblin's theorem (the
Markov–Dobrushin contraction: `P^2` is a `(1-delta')`-contraction in total
variation on probability measures) gives a unique `P^2`-invariant probability
measure `pi` and `sup_x ||P^{2n}(x,.) - pi||_TV <= 2 (1-delta')^n`.

`pi P` is also `P^2`-invariant, hence `pi P = pi`: `pi` is `P`-invariant, and any
`P`-invariant law is `P^2`-invariant, hence equals `pi`. Uniqueness follows. For
odd `n = 2k+1`,
`||P^{n}(x,.) - pi||_TV = ||Integral P(x,dy)(P^{2k}(y,.) - pi)||_TV <= sup_y ||P^{2k}(y,.)-pi||_TV`,
giving the stated `2(1-delta')^{floor(n/2)}` bound for all `n`.

**Step 4 — moments.** By invariance and Tonelli, for every `p >= 1`,

```
E_pi[ e^{2p} ] = Integral E[ e_{j+1}^{2p} | e_j = x ] pi(dx)
              <= sup_x E[ e_{j+1}^{2p} | x ]
              <= 2^{2p-1} (2p-1)!! ( rho^{2p} C_D + (1-rho)^{2p} m^{-p} ) < infinity .
```

In particular `E_pi[e^2]` and `E_pi[e^4]` are finite. Chebyshev gives the tail
bound, and uniform ergodicity plus the uniform moment bound rule out divergence
from any initial state. `[]`

**Step 5 — symmetry of `pi`.** By T3 the kernel commutes with `e -> -e`:
`P(-e, -A) = P(e, A)`. Hence if `pi` is invariant so is its reflection; by
uniqueness `pi` is symmetric, so `E_pi[e] = 0` (the first moment is finite by
Step 4). `[]`

*Remark (independence of T6).* Step 3 alone gives existence, so T7 does not
require the Feller property. T6 is retained because it is the structural reason
the kernel is well behaved and because it supplies the alternative
Krylov–Bogoliubov route (tightness from T5 plus Feller from T6).

*Remark (constants).* `delta'` inherits `C_D` through `R*` and is astronomically
small, so the TV rate in T7(2) is qualitative only. The *measured* mixing is
reported separately (`STATIONARY_DYNAMICS.md` §4): integrated autocorrelation
times of 1–3 cycles.

---

## Proofs of the skeleton results

Hypotheses (H1)–(H3) are stated in `THEOREM.md` and audited in
`NONLINEAR_MAP.md` §3–§4. (H1) is T3, hence exact. (H2) and (H3) are measured;
(H3) is used in the restricted form

```
(H3a)  s is continuous and strictly decreasing on (0, E],  E := 2 ,
       s(0+) = GammaTilde - 1 = 1/rho_c ,   s(E) < 1 ;
(H3b)  R_max := sup_e |R(e)| < E ,
```

which is all the `rho in (0,1]` analysis needs, because `1/rho >= 1` and, by
(H3b), `s(e) = |R(e)|/e <= R_max/e < 1` for every `e > E`. The measured values
are `R_max in [0.91, 1.59] < 2 = E` in all eight `(D,m)` cells, and `s` is
strictly decreasing on `(0, 2.2]` in all eight (`NONLINEAR_MAP.md` §4).

## Proof of T8 (unique fixed point)

By (H1)+(H2), `R(e) = -s(e) e` with `s(e) > 0` for `e != 0` and `R(0) = 0`.
`f_rho(e) = e` reads `-rho s(e) e = e`, i.e. `e (1 + rho s(e)) = 0`. For
`rho > 0` and `e != 0` the bracket is `> 1 > 0`, so `e = 0`. `[]`

## Proof of T9 (period-2 branch, flip bifurcation)

*Characterisation.* `{e, -e}` with `e > 0` is a 2-cycle of `f_rho` iff
`f_rho(e) = -e`, i.e. `-rho s(e) e = -e`, i.e. `rho s(e) = 1`.

*Existence and uniqueness.* By (H3a) `s` is a continuous strictly decreasing
bijection from `(0, E]` onto `[s(E), 1/rho_c)`, and by (H3a)+(H3b)
`s(e) < 1 <= 1/rho` for `e > E`. So for `rho in (rho_c, 1]` the level
`1/rho in [1, 1/rho_c)` is attained exactly once, at
`e*(rho) = s^{-1}(1/rho) in (0, E)`; for `rho <= rho_c` we have
`1/rho >= 1/rho_c > s(e)` for all `e > 0` and there is no solution.

*Monotone branch, continuous emergence.* `s^{-1}` is continuous and strictly
decreasing, so `rho -> e*(rho) = s^{-1}(1/rho)` is continuous and strictly
increasing, with `e*(rho) -> s^{-1}(1/rho_c) = 0` as `rho -> rho_c+`.

*Multiplier.* `R` odd and differentiable implies `R'` even. Hence

```
(f_rho o f_rho)'(e*) = f_rho'(f_rho(e*)) f_rho'(e*) = f_rho'(-e*) f_rho'(e*)
                     = rho^2 R'(-e*) R'(e*) = rho^2 R'(e*)^2 >= 0 ,
```

attracting iff `rho |R'(e*)| < 1`.

*Local branch interpretation.* At `rho = rho_c`,
`f_rho_c'(0) = rho_c R'(0) = -1`; the
fixed point `0` stays unique for all `rho` (T8); a branch of 2-cycles exists
for `rho > rho_c` only and emerges from `0` with amplitude `-> 0`. That is a
supercritical-side period-two branch at the local flip boundary. The assumptions
used here do not prove the branch attracting or verify a standard smooth
nondegeneracy coefficient, so the full attracting-supercritical-flip label is
left to the finite-grid numerical evidence. `[]`

## Proof of T10 (noise-floor invisibility)

`V_{D,m,rho}(e) = rho^2 S(e) + (1-rho)^2/m`. `S` is continuous at `0` with
`S(0) > 0` (measured; also `S(0) > 0` because `Rbar` is non-degenerate). As
`rho -> rho_c+`, `e*(rho) -> 0` by T9 and

```
V_{D,m,rho}(e*(rho)) -> rho_c^2 S(0) + (1 - rho_c)^2/m  >  0 ,
```

which is strictly positive because `rho_c < 1` in all eight frozen cells
(`rho_c in [0.061, 0.109]`). Hence `SNR(rho) = e*(rho)/sqrt(V) -> 0`. `[]`

*Interpretation.* At the boundary the deterministic period-two branch has
amplitude exactly `0` while the chain's per-cycle noise standard deviation is
`>= (1-rho_c)/sqrt(m) >= 0.40`. This establishes only the stated SNR limit. A
vanishing branch amplitude does not by itself exclude a kink, derivative
change, or other feature in a functional of the stochastic kernel. The result
is consistent with P7's negative operational finding and supplies a useful
interpretation, not a proof of that finding.

## Proof of T11 (identification of P7's effective gain)

By T7 the invariant law `pi` exists, is unique, has finite second moment, and is
symmetric, so `E_pi[e] = 0`. In stationarity,

```
Cov(e_{j+1}, e_j) = E_pi[ e_j E[e_{j+1} | e_j] ]  -  E_pi[e_{j+1}] E_pi[e_j]
                  = rho E_pi[ e R(e) ]
                  = -rho E_pi[ e^2 s(e) ]                (using R(e) = -s(e) e)
```

and `Var_pi(e_j) = E_pi[e^2] > 0` (else `pi = delta_0`, impossible since
`Var(e_1|0) = rho^2 S(0) + (1-rho)^2/m > 0`). Dividing,

```
ACF1 = -rho * sbar ,   sbar := E_pi[e^2 s(e)] / E_pi[e^2]  =  Gamma_eff - 1 ,
```

which is `ACF1 = rho (1 - Gamma_eff)` with `Gamma_eff = 1 + sbar`. `[]`

*Corollary (why `Gamma_eff << GammaTilde`).* `sbar` is a weighted average of `s`
against the probability measure `e^2 pi(de)/E_pi[e^2]`, which by T7 has `O(1)`
dispersion. Since `s` is strictly decreasing with `s(0+) = GammaTilde - 1` (H3a),
`sbar < GammaTilde - 1` strictly whenever `pi` charges `{e != 0}` — always. The
measured stationary dispersion sits where `s = O(1)` rather than `s ~ 10-16`,
which is exactly P7's 5x–25x overshoot of `lambda` over the measured `ACF1`.
