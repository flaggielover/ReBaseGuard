# Proof of the Priority-4 theorems

Nothing below is deferred to "standard regularity conditions".  Every analytic
step names the hypothesis of `THEOREM.md` Section 2 that licenses it.

## 1. The stopped change of measure

Fix `m >= 1` and `|e| <= d0`.

By (A1), `{tau = n} ∈ F_n` and `A_m 1{tau = n}` is a Borel function of the
first `n` coordinates.  Under `Q_e` those coordinates are iid with density
`f_e(z) = f(z + e)`; under `Q_0` they are iid with density `f`.  By (A3) the
two laws have the same support up to a Lebesgue-null set for `|e| <= d0`, so on
`F_n` the finite-dimensional density ratio exists and equals

```text
L_n(e) = prod_{t=1}^{n} f(Z_t + e) / f(Z_t).
```

Hence, for each fixed `n`,

```text
E_e[A_m 1{tau = n}] = E_0[A_m 1{tau = n} L_n(e)].                     (1.1)
```

On `{tau = n}` we have `L_n(e) = L_tau(e)`.  Summing (1.1) over `n` requires
that the series converge absolutely, which is (A6) at the pair `(e, 0)`
together with (A5): for `|e| <= d`,

```text
sum_n E_0[|A_m| 1{tau = n} L_tau(e)]
   = E_0[|A_m| L_tau(e)]
  <= E_0[|A_m|] + |e| E_0[G] < infinity,
```

using `|A_m| L_tau(e) <= |A_m| L_tau(0) + |A_m||L_tau(e) - L_tau(0)|` and
`L_tau(0) = 1`.  By (A2) the events `{tau = n}` exhaust the space up to a null
set, so dominated summation gives

```text
g_m(e) = E_e[A_m] = E_0[A_m L_tau(e)],     |e| <= d.                  (1.2)
```

Note that (1.2) is where the *whole* difficulty of the random denominator
disappears: `A_m` is carried intact inside the expectation, so the reciprocal
`1/w` -- which is a bounded, path-dependent random variable with
`1/m <= 1/w <= 1` -- is never differentiated and never separated from the
numerator.  It contributes no singularity, because `w >= 1` by (A2), and no
extra term, because it does not depend on `e`.

## 2. Differentiation at zero

Write, for `0 < |e| <= d`,

```text
(g_m(e) - g_m(0)) / e = E_0[ A_m (L_tau(e) - L_tau(0)) / e ].         (2.1)
```

By (A6) the integrand is bounded in absolute value by `G ∈ L^1(Q_0)`, uniformly
in `e ∈ [-d, d] \ {0}`.  By (A4), for `Q_0`-a.e. `omega` the integrand
converges pointwise to `A_m(omega) * (-S_tau^psi(omega))` as `e -> 0`.  By
(A5) that limit is integrable.  Dominated convergence applied along an
arbitrary sequence `e_k -> 0` therefore gives

```text
g_m'(0) = -E_0[A_m S_tau^psi] = -Gamma_{D,m,f},                       (2.2)
```

which is (G1a).

Two remarks on why (A6) is stated as a Lipschitz difference-quotient bound
rather than as a dominated pointwise derivative.

* The classical formulation requires `e -> A_m L_tau(e)` to be differentiable
  at *every* point of a neighbourhood, a.s., with a common integrable
  dominator.  Step (2.1) uses no derivative except at `0`, so the classical
  hypothesis is strictly stronger than what the proof consumes.
* It is strictly stronger in a way that matters.  For the Laplace family
  `log f(z) = -|z|/b - log(2b)` and `e -> log f(z + e)` fails to be
  differentiable at `e = -z`.  For each fixed `e` this is a null event, but
  the union over `e` in any neighbourhood has full measure, so "a.s.
  differentiable on a neighbourhood" is false.  The difference quotient is
  nevertheless bounded, because `log f` is `(1/b)`-Lipschitz, and (A4) holds
  because `Q_0(Z_t = 0 \text{ for some } t <= tau) = 0`.  So Laplace satisfies
  (A4) and (A6) and fails the classical hypothesis.

## 3. The reuse map and the rho scaling

By (A7), `E_e[e_{j+1}] = rho(e + E_e[A_m]) + (1 - rho)(E[U] - mu)
= rho(e + g_m(e))`, so `F_{rho,m}(e) = rho(e + g_m(e))`.  The identity
`e -> e` has derivative `1`.  Adding (2.2),

```text
F'_{rho,m}(0) = rho (1 + g_m'(0)) = rho (1 - Gamma_{D,m,f}),
```

which is (G1b).  The `rho` dependence is exactly linear, and this step uses no
property of `f`, of the detector, or of `m` whatsoever.

## 4. Theorem G1' at a general base point

Fix `e0` with `|e0| < d0` and repeat Sections 1-2 with `Q_{e0}` as the base
measure.  The density ratio of `Q_e` to `Q_{e0}` on `F_n` is

```text
L_n(e; e0) = prod_{t=1}^{n} f(Z_t + e) / f(Z_t + e0),
```

and, at `e = e0`, its derivative is `sum_{t <= tau} s(Z_t + e0)`.  Under
`Q_{e0}` the shifted residual `Z_t + e0` is exactly the raw innovation `eps_t`,
so the derivative is `-sum_{t <= tau} psi(eps_t)`, giving

```text
g_m'(e0) = -E_{e0}[A_m sum_{t <= tau} psi(eps_t)]
```

and `F'_{rho,m}(e0) = rho(1 - Gamma_{D,m,f}(e0))`.  No normalising correction
appears because `L(.; e0)` is a genuine density ratio and hence already has
`E_{e0}[L] = 1`.

## 5. Corollary G2

**(a)** Let `tau ≡ n` be deterministic.  Then `w = min(m, n)` is deterministic
and `A_m` is an average of `w` coordinates, each with the same law.  By
linearity and `E_e[Z_t] = E[eps] - e = -e`,

```text
g_m(e) = E_e[A_m] = -e,     hence     F_{rho,m}(e) = rho(e - e) = 0
```

for every `e` in the neighbourhood.  Only `E|eps| < infinity` and `E[eps] = 0`
are used, and the conclusion is exact rather than first order.

**(b)** Absolute continuity of `f` with `E|eps| < infinity`,
`E|eps psi(eps)| < infinity` and `z f(z) -> 0` give, by integration by parts on
`[-M, M]` and letting `M -> infinity`,

```text
E[psi(eps)] = -integral f'(z) dz = -[f]_{-inf}^{+inf} = 0,
E[eps psi(eps)] = -integral z f'(z) dz = -[z f]_{-inf}^{+inf} + integral f = 1.
```

At `e = 0` the residuals are the innovations and are independent, so for
`s != t`, `E[Z_s psi(Z_t)] = E[Z_s] E[psi(Z_t)] = 0`, while
`E[Z_t psi(Z_t)] = 1`.  Therefore

```text
Gamma = E[A_m S_tau^psi]
      = (1/w) sum_{r=0}^{w-1} sum_{t=1}^{n} E[Z_{n-r} psi(Z_t)]
      = (1/w) sum_{r=0}^{w-1} 1 = 1,
```

because for each of the `w` reused indices exactly one of the `n` score terms
is the diagonal one, and the reused indices are distinct.  Hence
`F'_{rho,m}(0) = rho(1 - 1) = 0`, which is the derivative of the identically
zero map found in (a).  The two computations are independent and agree.

## 6. Theorem G3

Fix a path with `1 <= tau < infinity`.

*On `{tau >= m}`*: `w = m`, so `A_m = B_m` and the indicator in `Q_{m,f}`
vanishes; (G3a) reads `A_m S = B_m S`.

*On `{tau < m}`*: `w = tau`, and the last `tau` residuals are the whole stopped
path, so `sum_{r=0}^{tau-1} Z_{tau-r} = T_tau`.  Then `A_m = T_tau/tau` and
`B_m = T_tau/m`, whence

```text
A_m S_tau^psi - B_m S_tau^psi = (1/tau - 1/m) T_tau S_tau^psi,
```

which is exactly `Q_{m,f}`.  The two events partition the space, proving
(G3a); integrating and using (A5) gives (G3b).

For the sign: on `{tau < m}` we have `0 < tau < m` so `1/tau - 1/m > 0`, and
`Q_{m,f}` has the sign of `T_tau S_tau^psi`.  If `psi(z) = c z` for a constant
`c > 0` then `T_tau S_tau^psi = c T_tau^2 >= 0` for every path.  An affine
location score integrates to a Gaussian density, but an affine score with a
nonzero intercept does not itself make `T_tau S_tau^psi` nonnegative on every
path.  Moreover, proving that all-path sign preservation forces linearity
requires additional regularity and a separate functional argument.  The
result proved here is therefore the exact decomposition, Gaussian
sufficiency, and explicit non-Gaussian failure below; no iff characterisation
is asserted.

The explicit Laplace counter-path is the prefix `Z = (5, -1, -1, -1)` with
`tau = 4`, `m = 5`: `T_tau = 2`, `S_tau^psi = (1 - 1 - 1 - 1)/b = -2/b`, so
`Q_{5} = (1/4 - 1/5) * 2 * (-2/b) = -1/(5b) < 0`.  Since `psi = sign/b` is
locally constant off the origin and the Laplace density is positive, every
residual prefix in a neighbourhood of that point, with the same alarm
behaviour, has the same strict sign; the event has positive probability
whenever the detector can stop at `tau = 4` after such a prefix.

## 7. Theorem G4

Let `J` be the pathwise sign reversal `(Jz)_t = -z_t`.  If `f` is even, `Q_0`
is `J`-invariant.  If the detector is reflection equivariant, `tau(Jz) =
tau(z)` and `A_m(Jz) = -A_m(z)`.  Hence, when `A_m ∈ L^1(Q_0)`,

```text
E_0[A_m] = E_0[A_m ∘ J] = -E_0[A_m],
```

so `E_0[A_m] = 0` and `F_{rho,m}(0) = rho(0 + 0) = 0`.  Zero is a fixed point.

With a fixed point in hand and `F_{rho,m}` continuously differentiable near
zero, the standard scalar linearisation argument applies: if
`|F'_{rho,m}(0)| < 1` pick `q` strictly between them, then `|F_{rho,m}(x)| <=
q|x|` on a small interval, so iterates converge to `0`; if `|F'_{rho,m}(0)| >
1` the same estimate applied to the local inverse gives repulsion.  At
magnitude exactly one the first-order term controls nothing.  Substituting
(G1b) gives the P3 classification with `Gamma_{D,m,f}`, and, when
`Gamma != 1`, the critical reuse fraction `rho_c = 1/|1 - Gamma|`.

Neither `Q_0`'s `J`-invariance nor the detector's equivariance was used in
Sections 1-6.  If `f` is not even the argument gives nothing, and indeed the
conclusion is false in general: for a standardised skew-normal family the
measured `E_0[A_1]` is of order one.

## 8. Discharge lemmas

**L1.**  Let `c_D` alarm in one step from every live state.  The hypothesis
`p > 0` requires the innovation law to reach `c_D`, i.e. `f` must put mass
above `c_D + delta0`.  All six theorem-supported families have support `R` and
satisfy this; a compactly supported innovation law with `a < c_D` would not,
and L1 would have to be replaced.  For the two-sided
CUSUM with allowance `k` and inclusive threshold `h`, a live state has
`S^+ >= 0`, so `Z >= h + k` forces `S^+ >= h`.  For the two-chart SR with
inclusive threshold `A`, a live state has `R^+ >= 0`, so
`Z >= 1/2 + log A` forces `R^+ = (1 + R^+_{prev}) e^{Z - 1/2} >= A`.  In both
cases, conditionally on `F_{n-1}` and on `{tau > n-1}`,

```text
Q_e(tau <= n | F_{n-1}) >= Q_e(Z_n >= c_D) >= p,
```

so `Q_e(tau > n) <= (1-p)^n` by induction.  Positivity and uniformity of `p`
on `|e| <= d0` follow from `f > 0` on a right half line and continuity of
`e -> integral_{c_D + e}^{infinity} f`.

**L2.**  `|A_m| <= max_{t <= tau} |Z_t|` because `A_m` is an average of `w`
of the `Z_t`.  Then

```text
E[max_{t <= tau} |Z_t|^r] <= sum_{n >= 1} E[1{tau >= n} |Z_n|^r].
```

`{tau >= n} = {tau <= n-1}^c ∈ F_{n-1}` is independent of `Z_n`, so each term
is `Q(tau >= n) E|Z|^r`, and the sum is `E|Z|^r E[tau]`.

**L3.**  If `sup|psi| <= M` then `z -> log f(z)` is `M`-Lipschitz, so
`e -> log L_tau(e) = sum_{t<=tau} (log f(Z_t+e) - log f(Z_t))` is
`M tau`-Lipschitz.  With `|log L_tau(e)| <= M d tau` on `[-d, d]` and
`|e^x - e^y| <= e^{max(x,y)}|x - y|`,

```text
|L_tau(e) - L_tau(e')| <= e^{M d tau} M tau |e - e'|,
```

so (A6) holds with `G = M |A_m| tau e^{M d tau}`.  By Hölder with exponents
`(1+eta, q)`, `q = (1+eta)/eta`,

```text
E[G] <= M (E[|A_m|^{1+eta}])^{1/(1+eta)} (E[(tau e^{M d tau})^q])^{1/q}.
```

L2 bounds the first factor by `(E|Z|^{1+eta} E[tau])^{1/(1+eta)}`.  For the
second, `E[(tau e^{M d tau})^q] = E[tau^q e^{q M d tau}]` is finite whenever
`q M d < log(1/(1-p))` by L1.  Shrinking `d` achieves this.  Finally
`|A_m S_tau^psi| <= M |A_m| tau <= G`, so (A5) holds too.

**L4.**  Assume `|psi(z)| <= M0 + M1|z|` with `M1 > 0`, and put

```text
W = sum_{t <= tau} (M0 + M1 delta + M1 |Z_t|).
```

Three elementary bounds hold pathwise on `[-delta, delta]`, and no constant is
absorbed silently:

```text
(i)   |log L_tau(e)| <= sum_{t<=tau} |e| sup_{|u|<=delta} |psi(Z_t + u)|
                     <= delta W,
(ii)  |d/de log L_tau(e)| <= sum_{t<=tau} |psi(Z_t + e)| <= W,
(iii) |A_m| <= max_{t<=tau} |Z_t| <= sum_{t<=tau} |Z_t| <= W / M1.
```

(iii) uses `M1|Z_t| <= M0 + M1 delta + M1|Z_t|`.  From (i) and (ii), `L_tau` is
`W e^{delta W}`-Lipschitz on `[-delta, delta]`, so with (iii),

```text
G := |A_m| W e^{delta W} <= W^2 e^{delta W} / M1
                         <= C_delta e^{2 delta W} / M1,
C_delta := sup_{x >= 0} x^2 e^{-delta x} = 4 / (delta^2 e^2).
```

It remains to bound `E[e^{2 delta W}]`.  Write `V = M0 + M1 delta + M1|eps|`.
Splitting on `{tau = n}`, on which `W = sum_{t<=n}(M0 + M1 delta + M1|Z_t|)`,
and applying Cauchy-Schwarz,

```text
E[e^{2 delta W}] = sum_n E[1{tau=n} e^{2 delta W}]
                <= sum_n Q(tau = n)^{1/2} (E[e^{4 delta V}])^{n/2}
                <= C^{1/2} sum_n ( (1-p) E[e^{4 delta V}] )^{(n-1)/2}
                   (E[e^{4 delta V}])^{1/2},
```

using L1's `Q(tau = n) <= C (1-p)^{n-1}` and the independence of the `n`
coordinates under `Q_0`.  The series is geometric with ratio
`((1-p) E[e^{4 delta V}])^{1/2}`.  If `E[e^{a|eps|}] < infinity` for some
`a > 0`, then `E[e^{4 delta V}] -> 1` as `delta -> 0` by dominated convergence,
so the ratio tends to `(1-p)^{1/2} < 1` and the series converges for all
sufficiently small `delta`.  Fixing such a `delta` makes `G` integrable, which
is (A6); and `|A_m S_tau^psi| <= |A_m| W <= G` gives (A5).

**L5.**  Immediate: a finite product of terms each differentiable at `e = 0`
is differentiable at `e = 0`, with the stated derivative by the product rule
and `L_tau(0) = 1`.

## 9. F1 -- the uniform counterexample, in closed form

Let `eps ~ U[-a, a]`, `f = 1_{[-a,a]}/(2a)`, and let
`tau = inf{t : |Z_t| >= c}` with `0 < c < a`.  For `|e| < a - c` the alarm
region in innovation coordinates is `{u : u >= c + e} ∪ {u : u <= e - c}`
intersected with `[-a, a]`, i.e. `[-a, e-c] ∪ [e+c, a]`.  Then

```text
Q_e(|Z| >= c) = ((e - c + a) + (a - e - c)) / (2a) = 1 - c/a,
```

which does not depend on `e`, and

```text
integral_{|z| >= c} z f(z + e) dz
   = (1/(2a)) ( integral_{-a}^{e-c} (u - e) du + integral_{e+c}^{a} (u - e) du )
   = (1/(2a)) ( (c^2 - (a+e)^2)/2 + ((a-e)^2 - c^2)/2 )
   = (1/(2a)) (-2ae) = -e.
```

Hence `g_1(e) = -e / (1 - c/a) = -e a/(a - c)` and `g_1'(0) = -a/(a-c)`.  The
interior a.e. score of a flat density is `0`, so `E_0[A_1 S_tau^psi] = 0` and
the identity `g_1'(0) = -Gamma` fails by exactly `a/(a-c)`; at `a = 1`,
`c = 1/2` the defect is `2`.  Hypothesis (A3) is the one that fails: the
supports of `Q_e` and `Q_0` differ by a set of positive Lebesgue measure for
every `e != 0`, so no density ratio `L_tau(e)` exists and step (1.1) is not
available.  The failure is structural, not a domination failure.

## 10. F2 -- the Cauchy counterexample

Let `eps` be standard Cauchy and use the frozen two-sided CUSUM.  From the
reset state, `tau = 1` exactly on `{|Z_1| >= h + k}`, so

```text
E_0|A_1| = E|Z_tau| >= E[|Z_1| 1{|Z_1| >= h+k}]
        = 2 integral_{h+k}^{infinity} z / (pi (1 + z^2)) dz = infinity.
```

Thus `g_m(0)` is not defined and (A5) fails.  The same failure invalidates
(A7) if the fresh reference is a sample mean.

A sharp point here, because it is a trap.  The *right-hand side* of (G1a) need
not look sick.  Cauchy has finite Fisher information and
`E[eps psi(eps)] = 1` converges absolutely, because `psi(z) = 2z/(1+z^2)`
damps the tail exactly enough.  So under the non-selective control `tau = 1`
the gain is a perfectly finite `1`, while `E_e[A_1] = E[eps] - e` is already
undefined.  Computing `Gamma` alone and finding a finite number is therefore
**not** evidence that the theorem applies: the left-hand side has to exist too,
and integrability of `A_m` must be checked separately from integrability of
`A_m S_tau^psi`.
Because Student-`t` with `nu = 1.5` has a finite mean and a bounded score, it
*is* covered by L1-L3; the dividing line is the first moment, not the second.

## 11. A closed-form non-Gaussian instance with unbounded horizon

Let `eps` be Laplace with density `f(z) = e^{-|z|/b}/(2b)`, so `psi = sign/b`
and `sup|psi| = 1/b`, and let the detector be the memoryless rule
`tau = inf{t : |Z_t| >= c}` with `c > 0`.  Take `m = 1`, so `A_1 = Z_tau`.

*The gain.*  Conditionally on `tau = n`, the residuals `Z_1,...,Z_{n-1}` are
iid from the law of `Z` restricted to `|z| < c` and `Z_n` from the law
restricted to `|z| >= c`, independently.  The inner law is symmetric and `psi`
is odd, so `E[psi(Z) | |Z| < c] = 0` and the cross term vanishes:

```text
Gamma_1 = E[Z_tau psi(Z_tau)] + E[Z_tau] E[tau - 1] E[psi(Z) | inner]
        = E[|Z|/b : |Z| >= c].
```

Under the Laplace law `|Z|` is exponential with mean `b`, and the exponential
law is memoryless, so `E[|Z| : |Z| >= c] = c + b` and

```text
Gamma_1 = (c + b)/b.
```

*The map.*  For `|e| < c` and `z >= c` we have `z + e > 0`, and for `z <= -c`
we have `z + e < 0`, so the two tail integrals are elementary:

```text
integral_{z >= c} z f(z+e) dz  = ( e^{-c/b}(c+b)/2 ) e^{-e/b},
integral_{z <= -c} z f(z+e) dz = -( e^{-c/b}(c+b)/2 ) e^{+e/b},
Q_e(|Z| >= c) = e^{-c/b} cosh(e/b).
```

Dividing,

```text
g_1(e) = -(c + b) tanh(e/b),        |e| < c,
g_1(0) = 0,     g_1'(0) = -(c + b)/b = -Gamma_1.
```

The identity of Theorem G1 therefore holds here **in closed form, with no
truncation and no numerics**: `tau` is unbounded with a geometric tail, and the
infinite sum over `n` has been carried out exactly by memorylessness.  With the
unit-variance normalisation `b = 1/sqrt(2)` and `c = 2`,

```text
Gamma_1 = 1 + 2 sqrt(2),
rho_c   = 1 / (Gamma_1 - 1) = 1 / (2 sqrt(2)) = sqrt(2)/4,
```

so `rho = 1/4` is locally attracting and `rho = 1/2` is locally repelling.  The
Arb layer encloses these numbers rigorously; the derivation above is the proof.
