# P5X human proofs — obligations `L1`, `L2`, `L3`, `L5`, `L6`

Written at the frozen Phase-1 stage, **before** any certified computation, and
using only the statements frozen at Checkpoint A. `L4`, `L7` and `L8` are not
discharged here and are not used by anything below; where the certified layer
needs the operative content of `L4` it obtains it by a self-certifying
supersolution instead, and `DEFECT_REGISTER.md` `D3` records that `L4`'s
monotonicity clause is *not* proved.

Notation is exactly `FROZEN_THEOREM.md` §1–§2. Throughout, `D` is one of the two
frozen detectors, `m >= 1`, `raw_1, raw_2, …` are iid `N(0,1)` on a probability
space that does **not** depend on `e`, `z_t = raw_t - e`, `F_t = sigma(raw_1,…,raw_t)`,
`tau` is the frozen inclusive alarm time, `w = min(m, tau)` and
`Rbar = (1/w) sum_{r<w} raw_{tau-r}`. `E_e` denotes expectation when the entering
error is `e`; `E_x` (or `P_x`) denotes the same law started from detector state
`x` rather than from the reset state `x_0 = (0,0)`.

---

## L1 — the two-dimensional reduction

### L1.1 Frozen claim

> the pre-alarm detector state is Markov on `E_D`; the alarm set from `x` is the
> complement of `(l(x), u(x))`; the reset state is `x_0 = (0,0)`; first-step
> conditioning gives `P5X-T1(b)` and the convention-A bookkeeping of `P5X-T1(c)`.

### L1.2 Assumptions used

(A1) `raw_t` iid `N(0,1)`, independent of `F_{t-1}`; `e` constant within a cycle.
(A2) The frozen detector recursions and the inclusive post-update alarm test of
`FROZEN_SCOPE.md` §1.
(A3) Convention A: `w = min(m, tau)`, denominator equal to the number of
summands, terminal increment included.
(A4) `P5-T4` (imported): `sup_x E_{x,e}[tau] <= C_D < infinity`, uniformly in `x`
and `e`.
(A5) All functions below are bounded Borel on `E_D`; `sup` norms are over `E_D`.

### L1.3 State space and alarm set

*CUSUM.* Before an alarm, `max(S^+_t, S^-_t) < h`, and each coordinate is a
`max(0, ·)`, so `x = (S^+, S^-) in [0, h)^2 = E_CUSUM` exactly, and `x_0 = (0,0)`
is the reset state. Given `x`, the next step alarms iff
`max(0, x^+ + z - k) >= h` or `max(0, x^- - z - k) >= h`, i.e. (since `h > 0`)
iff `z >= h + k - x^+ = u(x)` or `z <= x^- - (h+k) = l(x)`. Because
`0 <= x^+, x^- < h` we have `u(x) > k > 0 > -k > l(x)`, so `(l(x), u(x))` is a
nonempty open interval containing `0`, and the alarm set is exactly its
complement. The post-innovation map is `q_CUSUM(x,z)` as frozen.

*SR.* Before an alarm, `max(y^+ + z - 1/2, y^- - z - 1/2) < log A`, and the
stored state is `y' = log(1 + exp(y + z - 1/2))`. The alarm test from `x` is
`x^+ + z - 1/2 >= log A` or `x^- - z - 1/2 >= log A`, i.e. `z >= u(x)` or
`z <= l(x)` with `u(x) = (log A + 1/2) - x^+ = c_SR - x^+` and
`l(x) = x^- - c_SR`, exactly as frozen; and `q_SR` is as frozen. The stored
state satisfies `0 <= y' = log(1 + exp(v)) < log(1 + A)` whenever `v < log A`.

> **Defect.** The frozen square for SR, `E_SR = [0, b_SR)^2` with
> `b_SR = log A`, is therefore **too small**: live SR states occupy
> `[0, log(1+A))^2` and `log(1+A) > log A`. This is verified numerically in
> `DEFECT_REGISTER.md` `D1` (live states up to `6.25744933` against
> `log A = 6.25553146` and `log(1+A) = 6.25744943`). The correction is
> `b_SR := log(1 + A)`; nothing else in `P5X-T1` changes, because `l`, `u` and
> `q_SR` are stated for a general `x` and never used `x < log A`. CUSUM is
> unaffected. This defect is recorded, not silently repaired, and no SR
> certified work may start until it is adjudicated.

In both cases the pair `(x_t)` is a time-homogeneous Markov chain on `E_D`
killed at `tau`, because `x_{t} = q(x_{t-1}, z_t)` with `z_t` independent of
`F_{t-1}`, and the alarm decision at step `t` is a deterministic function of
`(x_{t-1}, z_t)`. The killed (sub-stochastic) kernel acting on bounded Borel `f`
is exactly `K_e`, and `K_{z,e}`, `rho_{1,e}`, `rho_{2,e}` are the corresponding
`z`- and `z^2`-weighted objects. The two displayed closed forms are the Gaussian
tail integrals: with `zeta = z + e ~ N(0,1)`,

```text
int_{z >= u} z phi(z+e) dz = int_{zeta >= u+e} (zeta - e) phi(zeta) dzeta
                           = phi(u+e) - e (1 - Phi(u+e)) ,
int_{z <= l} z phi(z+e) dz = -phi(l+e) - e Phi(l+e) ,
```

whose sum is the frozen `rho_{1,e}`; and

```text
int_{zeta >= a} (zeta-e)^2 phi = [a phi(a) + 1 - Phi(a)] - 2 e phi(a) + e^2 (1 - Phi(a)) ,
int_{zeta <= b} (zeta-e)^2 phi = [Phi(b) - b phi(b)] + 2 e phi(b) + e^2 Phi(b) ,
```

with `a = u + e`, `b = l + e`, whose sum is the frozen `rho_{2,e}`.

### L1.4 Invertibility — `P5X-T1(a)`

`K_e` is a positive operator, so its sup-norm is attained on the constant
function: `‖K_e^n‖_inf = ‖K_e^n 1‖_inf = sup_x P_x(tau > n)`. By the block
argument of `P5-T4` (which is valid *from any state*, since it only uses
`S^+ >= 0` resp. `y^+ >= 0` and the forcing of an alarm by a run of
innovations), there are `n_0` and `beta < 1`, uniform in `e` and `x`, with
`sup_x P_x(tau > n) <= beta^{floor(n / n_0)}`. Hence `sum_n ‖K_e^n‖ < infinity`,
the Neumann series `sum_n K_e^n` converges in operator norm, `I - K_e` is
invertible on bounded Borel functions, and

```text
‖(I - K_e)^{-1}‖_inf = ‖ sum_n K_e^n 1 ‖_inf = sup_x sum_n P_x(tau > n)
                     = sup_x E_x[tau]  <=  C_D  <  infinity .
```

Uniqueness among bounded functions is immediate from invertibility. `[]`

### L1.5 The backward functions

`(K_e 1)(x) = P_x(tau > 1)`, so `h_1 = 1 - K_e 1` is `x -> P_x(tau = 1)`.
Inductively, `(K_e h_{j-1})(x) = E_x[ 1{no alarm at step 1} h_{j-1}(x_1) ]
= P_x(tau = 1 + (j-1)) = P_x(tau = j)`, using the Markov property and the fact
that on `{no alarm at 1}` the remaining alarm time is the alarm time of the
chain restarted at `x_1`. So `h_j(x) = P_x(tau = j)` for all `j >= 1`. `[]`

### L1.6 Terminal-innovation identities — `P5X-T1(b)`

*Claim 1:* for `1 <= i <= t`, `E_x[ Z_i ; tau = t ] = (K_e^{i-1} S_{t-i})(x)`.

For `i = t`: `S_0 = rho_{1,e}` and `rho_{1,e}(y) = E_y[ z ; alarm at the next step ]`,
so `(K_e^{t-1} rho_{1,e})(x) = E_x[ 1{tau > t-1} rho_{1,e}(x_{t-1}) ]
= E_x[ Z_t ; tau = t ]`, since on `{tau > t-1}` the event `{tau = t}` is exactly
"the step from `x_{t-1}` alarms", and `Z_t` is the innovation of that step.

For `i < t`: `S_{t-i} = K_{z,e} h_{t-i}`, so
`(K_{z,e} h_{t-i})(y) = E_y[ z · 1{no alarm} · h_{t-i}(q(y,z)) ]
= E_y[ Z_1 ; tau = 1 + (t-i) ]`. Applying `K_e^{i-1}` and the Markov property at
time `i-1`,

```text
(K_e^{i-1} S_{t-i})(x) = E_x[ 1{tau > i-1} · E_{x_{i-1}}[ Z_1 ; tau = t-i+1 ] ]
                       = E_x[ Z_i ; tau = t ] .
```

*Claim 2:* `g_r(x) = E_x[ Z_{tau-r} ; tau >= r+1 ]` for `r >= 0`.
By L1.4, `g_r = sum_{n>=0} K_e^n S_r`. For `r = 0`,
`sum_n (K_e^n rho_{1,e})(x) = sum_{t>=1} E_x[Z_t ; tau = t] = E_x[Z_tau]`, which
is the claim since `{tau >= 1}` is sure. For `r >= 1`, Claim 1 with `i = n+1`,
`t = n+1+r` gives `(K_e^n S_r)(x) = E_x[ Z_{n+1} ; tau = n+1+r ]`; summing over
`n >= 0` and substituting `t = n+1+r` gives
`sum_{t >= r+1} E_x[ Z_{t-r} ; tau = t ] = E_x[ Z_{tau-r} ; tau >= r+1 ]`.
Absolute convergence holds because
`sum_n ‖K_e^n S_r‖ <= ‖S_r‖ sum_n ‖K_e^n‖ < infinity`
and `‖S_r‖ <= ‖K_{z,e}‖ <= E|z| <= sqrt(2/pi) + |e|`. `[]`

### L1.7 Convention-A bookkeeping — `P5X-T1(c)`

Since `w = min(m, tau)`,

```text
Rbar = 1{tau >= m} (1/m) sum_{r=0}^{m-1} raw_{tau-r}
     + sum_{t=1}^{m-1} 1{tau = t} (1/t) sum_{i=1}^{t} raw_i ,
```

a partition of the sample space into `{tau >= m}` and the `m-1` disjoint events
`{tau = t}`, `1 <= t <= m-1`. Now `raw_j = Z_j + e` and each of the two window
means averages exactly `w` terms, so `Rbar = e + A_m` with
`A_m = (1/w) sum_{r<w} Z_{tau-r}`; taking expectations, `R_{D,m}(e) = e + E_e[A_m]`.
Decomposing `E_e[A_m]` along the same partition,

```text
E_e[A_m] = (1/m) sum_{r=0}^{m-1} E_e[ Z_{tau-r} ; tau >= m ]
         + sum_{t=1}^{m-1} (1/t) sum_{i=1}^{t} E_e[ Z_i ; tau = t ] .
```

The second double sum is `sum_{t=1}^{m-1} (1/t) sum_{i=1}^{t} (K_e^{i-1} S_{t-i})(x_0)`
by Claim 1. For the first, split `{tau >= r+1}` into `{tau >= m}` and
`{r+1 <= tau <= m-1}` (the latter is empty when `r >= m-1`):

```text
E_e[ Z_{tau-r} ; tau >= m ] = g_r(x_0) - sum_{t=r+1}^{m-1} E_e[ Z_{tau-r} ; tau = t ]
                            = g_r(x_0) - sum_{t=r+1}^{m-1} E_e[ Z_{t-r} ; tau = t ]
                            = g_r(x_0) - sum_{t=r+1}^{m-1} (K_e^{t-r-1} S_r)(x_0) ,
```

the last step by Claim 1 with `i = t-r`, so that `t - i = r`. Substituting gives
exactly the frozen display of `P5X-T1(c)`. Every sum is finite and no term uses
more than `m-1` applications of `K_e`. `[]`

### L1.8 Dependencies, detector-specificity, certified input, non-claims

* **Depends on P5:** `P5-T4` for L1.4 (uniform finiteness, from any state);
  `P5-T1`'s cancellation `raw = Z + e` under convention A for L1.7. **Depends on
  P3:** nothing.
* **Detector-specific steps:** only L1.3 — the identification of `E_D`, of
  `(l, u)` and of `q`. Everything from L1.4 on is detector-generic and uses only
  "killed Markov chain on a compact set with scalar innovation and interval
  continuation set".
* **Certified numerical input still required:** none. `L1` is exact. The
  *values* `g_r(x_0)` are not computed here.
* **What L1 does NOT prove:** it gives no bound on `R`, no sign, no
  monotonicity, no smoothness in `e`, and no numerical value. It also does not
  assert that the collocation scheme of any implementation converges — that is a
  property of a certificate, not of the reduction.

---

## L2 — the pair recursion for second moments

### L2.1 Frozen claim

> pair recursion for `E_e[ Z_{tau-r} Z_{tau-r'} ; tau >= m ]` on the same
> square, `O(m^2)` backward functions.

### L2.2 Assumptions used

L1 in full, plus `P5-T5` (all even moments finite uniformly in `x` and `e`), so
every expectation below is absolutely convergent.

### L2.3 One additional operator

Define, alongside `K_e` and `K_{z,e}`,

```text
(K_{z2,e} f)(x) = int_{l(x)}^{u(x)} z^2 f(q(x,z)) phi(z+e) dz .
```

> **Incompleteness.** `FROZEN_THEOREM.md` §3 describes the pair functions as
> "built from `h` and `K_{z,e}`". The **diagonal** terms `r = r'` genuinely
> require the `z^2`-weighted operator `K_{z2,e}`, which cannot be assembled from
> `K_e` and `K_{z,e}`. The frozen *conclusion* — that `E_e[Rbar^2]` is
> determined by the same two-dimensional square through `O(m^2)` backward
> functions — is unaffected and is proved below; only the frozen enumeration of
> operators was incomplete. Recorded as `DEFECT_REGISTER.md` `D2`.

### L2.4 Off-diagonal pairs

Fix `r > r' >= 0` and put `G_{r,r'}(x) = E_x[ Z_{tau-r} Z_{tau-r'} ; tau >= r+1 ]`.
Condition on the first step from `x`.

* On the alarm event `tau = 1`: since `r >= 1`, `{tau >= r+1}` fails, so the
  contribution is `0`.
* On the continuation event, `tau = 1 + tau'` with the chain restarted at
  `x_1 = q(x,z)`. Then `tau - r = 1 + tau' - r` and `tau - r' = 1 + tau' - r'`,
  and `{tau >= r+1} = {tau' >= r}`. Three sub-cases:
  * `tau' >= r+1`: both indices exceed `1`, so
    `Z_{tau-r} = Z'_{tau'-r}` and `Z_{tau-r'} = Z'_{tau'-r'}`; contribution
    `(K_e G_{r,r'})(x)`;
  * `tau' = r`: then `tau - r = 1`, so `Z_{tau-r}` is the *current* innovation
    `z`, while `tau - r' = 1 + r - r' >= 2`, so `Z_{tau-r'} = Z'_{r-r'}`;
    contribution `E_x[ z 1{cont} · E_{x_1}[ Z_{r-r'} ; tau' = r ] ]`;
  * `tau' < r`: excluded by `{tau' >= r}`.

By L1.6 Claim 1, `E_y[ Z_{j} ; tau = t ] = (K_e^{j-1} S_{t-j})(y)`; with
`j = r - r'` and `t = r` this is `(K_e^{r-r'-1} S_{r'})(y)`. Hence

```text
G_{r,r'} = K_e G_{r,r'} + K_{z,e} K_e^{r-r'-1} S_{r'} ,
G_{r,r'} = (I - K_e)^{-1} K_{z,e} K_e^{r-r'-1} S_{r'} .
```

Note that the source reuses the *same* `S_{r'}` as the first-moment reduction.

### L2.5 Diagonal terms

With `G_{r,r}(x) = E_x[ Z_{tau-r}^2 ; tau >= r+1 ]` the same conditioning gives,
for `r = 0`, an alarm contribution `E_x[z^2 ; alarm] = rho_{2,e}(x)` and a
continuation contribution `K_e G_{0,0}`; for `r >= 1` no alarm contribution, a
`tau' = r` contribution `E_x[ z^2 1{cont} h_r(x_1) ] = (K_{z2,e} h_r)(x)`, and
`K_e G_{r,r}`. Hence

```text
G_{0,0} = (I - K_e)^{-1} rho_{2,e} ,
G_{r,r} = (I - K_e)^{-1} K_{z2,e} h_r        (r >= 1) .
```

### L2.6 Short-`tau` pair terms and the assembled second moment

For `1 <= i < j <= t` the same argument gives
`E_e[ Z_i Z_j ; tau = t ] = ( K_e^{i-1} K_{z,e} K_e^{j-i-1} S_{t-j} )(x_0)`, and
`E_e[ Z_i^2 ; tau = t ] = ( K_e^{i-1} K_{z2,e} h_{t-i} )(x_0)` for `i < t`,
`= ( K_e^{t-1} rho_{2,e} )(x_0)` for `i = t`. Since `Rbar = e + A_m`,

```text
E_e[ Rbar^2 ] = e^2 + 2 e E_e[A_m] + E_e[ A_m^2 ] ,
E_e[ A_m^2 ]  = (1/m^2) [ sum_{r<m} ( G_{r,r}(x_0) - short_{r,r} )
                        + 2 sum_{r > r'} ( G_{r,r'}(x_0) - short_{r,r'} ) ]
              + sum_{t=1}^{m-1} (1/t^2) sum_{i,j <= t} E_e[ Z_i Z_j ; tau = t ] ,
```

where `short_{r,r'} = sum_{t=r+1}^{m-1} E_e[ Z_{t-r} Z_{t-r'} ; tau = t ]` uses
the finite-depth expressions just listed. Every object is a backward function on
`E_D` obtained by at most `m-1` applications of `K_e`, `K_{z,e}` or `K_{z2,e}`,
plus one resolvent solve; there are `m(m+1)/2 = O(m^2)` of them. For `m = 1` the
sums collapse to `E_e[Rbar^2] = G_{0,0}(x_0) + 2 e g_0(x_0) + e^2`, which is the
frozen `P5X-T2` display. Finally `S_{D,m} = E_e[Rbar^2] - R_{D,m}^2`. `[]`

### L2.7 Dependencies, detector-specificity, certified input, non-claims

* **Depends on P5:** `P5-T5` for absolute convergence; L1 for every identity.
  **Depends on P3:** nothing.
* **Detector-specific steps:** none beyond L1.3.
* **Certified numerical input still required:** none for the identity;
  the *values* `s_min = inf_e S` and `M_2 = sup_e E[Rbar^2]` are certified
  scalars (`C2`), not proved here.
* **What L2 does NOT prove:** that `S > 0`, that `S` is bounded, or any value.
  It also does not claim the `O(m^2)` solves are affordable — that is a budget
  question answered by the certificate, not by this lemma.

---

## L3 — far-field forgetting, with an explicit majorant

### L3.1 Frozen claim

> far-field forgetting with an explicit decreasing majorant `B_D(e)`, valid for
> every `m` simultaneously,

together with the displayed inequality of `FROZEN_THEOREM.md` §4,
`|R_{D,m}(e)| <= sqrt(q(e)) ( 1 + sqrt( E_e[ Rbar^2 | tau > 1 ] ) )`,
`q(e) = P_e(tau > 1) <= Phi(a(e))`, `a(e) = c_D - |e|`.

### L3.2 Assumptions used

L1.3 (the alarm set), the frozen convention A, and `P5-T5`'s Jensen step. By
`P5-T3` (oddness of `R`) it suffices to treat `e > 0`.

### L3.3 The three elementary bounds

Let `e > c_D` and `a = c_D - e < 0`.

**(i) One-step alarm from the reset state.** From `x_0`, `(l, u) = (-c_D, c_D)`,
so `{tau > 1} = { e - c_D < raw_1 < e + c_D } subset { raw_1 > -a }`, whence
`q(e) = P(tau > 1) <= 1 - Phi(-a) = Phi(a)`.

**(ii) One-step alarm from *any* live state.** For every `x in E_D`,
`l(x) = x^- - c_D >= -c_D`, so `{ z <= -c_D } subset { alarm }`, and
`P_x(no alarm) <= P(z > -c_D) = P(raw_1 > e - c_D) = Phi(a) =: q'`.
Iterating with the Markov property, `P_x(tau > n) <= q'^n` for every `x` and
every `n >= 0`, hence

```text
E[ (tau - 1)^+ ] = sum_{n >= 1} P(tau > n) <= sum_{n >= 1} q'^n = q'/(1 - q') .
```

**(iii) Second moment on the continuation event.** By the Jensen step of
`P5-T5` — valid for every `m` because `w >= 1` and the window is a sub-multiset
of `{1,…,tau}` — `Rbar^2 <= sum_{t <= tau} raw_t^2`. Therefore

```text
E[ Rbar^2 1{tau>1} ] <= E[ raw_1^2 1{tau>1} ] + sum_{t >= 2} E[ raw_t^2 1{tau >= t} ]
                     =  E[ raw_1^2 1{tau>1} ] + sum_{t >= 2} P(tau >= t)
                     <= [ Phi(a) + |a| phi(a) ] + q'/(1-q')  =:  m_2(e) ,
```

using `{tau >= t} in F_{t-1}` and `raw_t` independent of `F_{t-1}` for the
middle equality, `{tau>1} subset {raw_1 > -a}` and
`E[raw^2 ; raw > s] = Phi(-s) + s phi(s)` (`s = -a > 0`) for the first bracket,
and (ii) for the tail.

### L3.4 The majorant

Because `E[raw_1] = 0`, on the partition `{tau = 1} , {tau > 1}` and using
`Rbar = raw_1` on `{tau = 1}` (there `w = min(m,1) = 1` for **every** `m`):

```text
R_{D,m}(e) = E[ raw_1 ; tau = 1 ] + E[ Rbar ; tau > 1 ]
           = - E[ raw_1 ; tau > 1 ] + E[ Rbar ; tau > 1 ] .
```

For the first term, `{tau>1} subset {raw_1 > -a}` with `-a > 0`, so
`0 <= E[ raw_1 ; tau > 1 ] <= E[ raw_1 ; raw_1 > -a ] = phi(a)`.
For the second, Cauchy–Schwarz applied to the pair `(|Rbar| 1_{tau>1}, 1_{tau>1})`
gives `| E[ Rbar ; tau>1 ] | <= sqrt( E[Rbar^2 1{tau>1}] · P(tau>1) )`. Hence

```text
| R_{D,m}(e) |  <=  B_D(e) := phi(a) + sqrt( q' · m_2(e) ) ,
q' = Phi(a) ,  m_2(e) = Phi(a) + |a| phi(a) + Phi(a)/(1 - Phi(a)) ,  a = c_D - |e| ,
```

for every `m >= 1` and every `|e| > c_D`, with `B_D` depending on `D` only
through `c_D`. The frozen displayed inequality follows from the same two steps
with the cruder first term `|E[raw_1;tau>1]| <= sqrt(E[raw_1^2]) sqrt(q) = sqrt(q)`
and `E[Rbar^2 1{tau>1}] = q · E[Rbar^2 | tau>1]`; it is therefore true, and
`B_D` is the sharper explicit majorant the frozen statement promised.

**Monotonicity.** For `|a| >= 1`, i.e. `|e| >= c_D + 1`, each of `phi(a)`,
`Phi(a)`, `|a| phi(a)` and `Phi(a)/(1-Phi(a))` is strictly decreasing in `|a|`,
so `B_D` is strictly decreasing in `|e|` on `[c_D + 1, infinity)` and
`B_D(e) -> 0` faster than any polynomial (indeed like `phi(|e| - c_D)` up to a
`sqrt(|e|)` factor). The restriction to `|e| >= c_D + 1` is `6.5` for CUSUM and
`7.7555…` for SR, both strictly inside the frozen `e_far = 12`.

**Values** (double precision, non-authoritative; the certified evaluation is
`C1`'s far-field scalar):

| `|e|` | `B_CUSUM` | `B_SR` |
|---|---|---|
| 8 | `3.62e-2` | `4.04e-1` |
| 10 | `3.23e-5` | `4.22e-3` |
| **12 = `e_far`** | **`5.37e-10`** | **`8.57e-7`** |

Both are far below the `2` that `P5X-T4` needs, so the frozen `e_far = 12`
closes the tail with an enormous margin.

### L3.5 Dependencies, detector-specificity, certified input, non-claims

* **Depends on P5:** `P5-T3` (oddness, to reduce to `e > 0`), the Jensen step of
  `P5-T5`, and convention A for `w = 1` on `{tau = 1}`. **Depends on P3:** nothing.
* **Detector-specific steps:** only the value of `c_D` (`11/2` vs `log A + 1/2`).
  The argument is otherwise identical for both detectors.
* **Certified numerical input still required:** an outward-rounded evaluation of
  `B_D(e_far)` and of the monotonicity range — three Gaussian tail values. This
  is the cheapest certified scalar in the campaign.
* **What L3 does NOT prove:** it says nothing about the **sign** of `R` in the
  far field, so it cannot contribute to `H2`; it says nothing for
  `|e| <= c_D`; and it does not bound `S` or any second moment of the stationary
  law.

---

## L5 — real-analyticity in `e`

### L5.1 Frozen claim

> `e -> R_{D,m}(e)` and `e -> S_{D,m}(e)` are real-analytic; hence
> interval-valued `e` is admissible and no separate modulus of continuity is
> required.

### L5.2 Assumptions used

L1 (the reduction), L2 (for `S`), `P5-T4`'s block bound uniform in `e`, and
boundedness of the state square.

### L5.3 Complexified operators

For `e = sigma + i theta in C` define `K_e`, `K_{z,e}`, `K_{z2,e}` by the same
integrals. Since
`|phi(z + sigma + i theta)| = phi(z + sigma) · exp(theta^2 / 2)`, we get the
pointwise domination `|K_e f| <= exp(theta^2/2) · K_sigma |f|`, hence

```text
‖K_e^n‖_inf  <=  exp(n theta^2 / 2) · ‖K_sigma^n‖_inf
             <=  exp(n theta^2 / 2) · beta^{floor(n/n_0)} ,
```

with `n_0, beta < 1` from `P5-T4`, uniform in `sigma`. Choose `theta_0 > 0` with
`exp(n_0 theta_0^2 / 2) · beta < 1`. Then `sum_n ‖K_e^n‖` converges uniformly on
the strip `Sigma = { |Im e| <= theta_0 }`, and likewise
`‖K_{z,e}‖, ‖K_{z2,e}‖ <= exp(theta_0^2/2) (sqrt(2/pi) + |sigma| + 1 + sigma^2)`
are locally bounded.

### L5.4 Holomorphy

For fixed bounded Borel `f` and fixed `x`, `e -> (K_e f)(x)` is an integral over
the **bounded** interval `(l(x), u(x))` of an integrand that is entire in `e` and
dominated locally uniformly on `Sigma`; by Morera/Fubini it is holomorphic, and
the bound in L5.3 makes the family uniformly bounded on compact subsets of
`Sigma`. Consequently each `h_j(x_0)`, each `S_j(x_0)`, each finite product
`K_e^{i-1}` applied to them, and each partial sum `sum_{n<N} K_e^n S_r (x_0)` is
holomorphic on `Sigma`; the partial sums converge uniformly on compacts of
`Sigma` by L5.3, so their limits `g_r(x_0)` are holomorphic (Weierstrass).
`P5X-T1(c)` writes `R_{D,m}` as a finite linear combination of such functions
plus `e`, so `R_{D,m}` is holomorphic on `Sigma`, hence real-analytic on `R`.
The same argument through L2 gives holomorphy of `E_e[Rbar^2]`, and
`S = E_e[Rbar^2] - R^2` is then real-analytic. `[]`

### L5.5 What the certificate actually uses — an honest separation

Real-analyticity is what licenses a *single low-degree polynomial candidate per
`e`-cell* with rapidly decaying approximation error. It is **not** what makes an
interval-valued `e` admissible: that follows from the strictly weaker,
order-theoretic fact that `phi(z + e)` admits an outward-rounded enclosure when
`e` ranges over an interval, which is used directly in the residual bound.
The frozen sentence "hence interval-valued `e` is admissible" is therefore true
but states a stronger reason than is needed; the certificate is not weakened by
this distinction, and the distinction is recorded so that a reader does not
believe the certificate rests on analyticity.

### L5.6 Dependencies, detector-specificity, certified input, non-claims

* **Depends on P5:** `P5-T4` (the `e`-uniform block bound). **Depends on P3:**
  nothing.
* **Detector-specific steps:** none; the argument uses only that the
  continuation set is a bounded interval and that `q` does not depend on `e`.
* **Certified numerical input still required:** none. `theta_0` is qualitative
  and no certified quantity depends on its size.
* **What L5 does NOT prove:** it gives no derivative bound, no radius of
  convergence of practical size, and no statement about how fast a polynomial
  candidate converges. It is a smoothness statement, not an approximation
  theorem.

---

## L6 — the stationary second-moment identity

### L6.1 Frozen claim

> `E_pi[e^2] = rho^2 E_pi[R^2 + S] + (1-rho)^2/m`.

### L6.2 Assumptions used

`P5-T7` (imported): for fixed `(D, m, rho)` there is a unique invariant
probability `pi` with finite moments of every order. `P5-T2` (imported):
`E[e_{j+1} | e_j = x] = rho R(x)` and `Var(e_{j+1} | e_j = x) = rho^2 S(x) + (1-rho)^2/m`.
`P5-T5` (imported): `sup_x E[Rbar^2 | x] < infinity`, so `R^2 + S` is a bounded
measurable function.

### L6.3 Proof

By invariance, if `e_j ~ pi` then `e_{j+1} ~ pi`, so `E_pi[e^2] = E[ e_{j+1}^2 ]`
with `e_j ~ pi`. Conditioning on `e_j` and using the conditional
variance/mean decomposition,

```text
E[ e_{j+1}^2 ] = E[ Var(e_{j+1} | e_j) ] + E[ ( E[e_{j+1} | e_j] )^2 ]
               = E_pi[ rho^2 S(e) + (1-rho)^2/m ] + E_pi[ rho^2 R(e)^2 ]
               = rho^2 E_pi[ R^2 + S ] + (1-rho)^2/m .
```

Every step is legitimate: `E_pi[e^2] < infinity` by `P5-T7`, and `R^2 + S` is
bounded by `P5-T5`, so all three expectations are finite and the tower property
applies without further conditions. `[]`

**Corollary (the form used by `P5X-T6`).** If `s_min <= S(e)` for all `e` and
`E[Rbar^2 | e] = R(e)^2 + S(e) <= M_2` for all `e`, then

```text
rho^2 s_min + (1-rho)^2/m  <=  E_pi[e^2]  <=  rho^2 M_2 + (1-rho)^2/m ,
```

for every `rho in [0,1]` and every `m`, with no further hypothesis.

### L6.4 Dependencies, detector-specificity, certified input, non-claims

* **Depends on P5:** `P5-T2`, `P5-T5`, `P5-T7`. This lemma is where `P5-T7` is
  *used* and it is used exactly at its adjudicated scope: fixed `(D, m, rho)`,
  constant policy. **Depends on P3:** nothing.
* **Detector-specific steps:** none.
* **Certified numerical input still required:** both constants `s_min` and
  `M_2` (`C2`). Without them the identity is exact but carries no number.
* **What L6 does NOT prove:** nothing about the shape, unimodality, tails or
  support of `pi`; nothing about higher moments (that is `L7`); and nothing
  about how tight the two bounds are — non-vacuousness is an empirical
  observation reported under `E4`, never a theorem.

---

## Summary of the Phase-1 outcome

| lemma | status | uses certified input? | defects found |
|---|---|---|---|
| `L1` | **PROVED** (exact) | no | `D1`: the frozen SR state square `b_SR = log A` is too small; correct value `log(1+A)`. CUSUM unaffected |
| `L2` | **PROVED** (exact) | no | `D2`: the frozen operator enumeration omits `K_{z2,e}`, needed for the diagonal pairs; the frozen conclusion is unaffected |
| `L3` | **PROVED** (exact, with the explicit `B_D`) | one trivial certified scalar `B_D(e_far)` | none; the frozen displayed inequality is true and `B_D` is sharper |
| `L5` | **PROVED** (exact) | no | none; the frozen "hence" clause overstates the reason, recorded as `D4` (non-defect clarification) |
| `L6` | **PROVED** (exact) | `s_min`, `M_2` for the corollary | none |

No lemma was found false. No proof required an assumption outside those frozen
at Checkpoint A, except that `L2` needs one operator (`K_{z2,e}`) beyond the
frozen enumeration — an incompleteness of the enumeration, not of the claim.
