# Symmetric SR stopped-score derivative theorem

## 1. Statement

Fix `A>1`.  On the canonical residual path space, let the coordinates under
`Q_e` be iid `N(-e,1)`.  Starting from `R_0^+=R_0^-=0`, define

```text
R_t^+ = (1+R_{t-1}^+) exp(Z_t-1/2),
R_t^- = (1+R_{t-1}^-) exp(-Z_t-1/2),
tau   = inf {t>=1 : max(R_t^+,R_t^-) >= A},
T_tau = sum_{t=1}^tau Z_t.
```

The alarm boundary is inclusive and the terminal observation is included.  At
matched reuse length `m=1`, let `U~N(0,1)` be independent of the stopped path
and put

```text
E_next = rho(e+Z_tau)+(1-rho)U,
F_rho(e) = E_e[E_next],       0<=rho<=1.
```

Then `tau` is almost surely finite in a neighborhood of zero, all expectations
below are finite, `F_rho` is differentiable at zero, and

```text
Gamma_SR := E_0[Z_tau T_tau],
F'_rho(0) = rho(1-Gamma_SR).
```

Moreover, reflection of the residual path swaps the charts, preserves `tau`,
negates both `Z_tau` and `T_tau`, and therefore makes `F_1` odd.  In particular
`F_rho(0)=0`.  If `Gamma_SR>2`, then

```text
F'_1(0)=1-Gamma_SR < -1,
|F'_1(0)|>1,
```

so zero is a locally linearly repelling fixed point of the deterministic
conditional-mean iteration `e_{j+1}=F_1(e_j)`.

The theorem holds for every admissible `A>1`.  The code-correspondence instance
uses the authoritative Stage D value `A=520.886133602749`.

## 2. Canonical path functional and measurability

Use `Omega=R^N` with its product Borel sigma-field and coordinate maps `Z_t`.
For any finite prefix, the chart states are obtained by finitely many
compositions of addition, multiplication, and the exponential function.
They are therefore Borel functions of that prefix.  For every `n>=1`,

```text
{tau=n}
  = {max(R_s^+,R_s^-)<A for every s<n}
    intersect {max(R_n^+,R_n^-)>=A}
```

is a finite intersection of Borel cylinder events.  Thus `tau` is a stopping
time and is measurable as an extended-natural-valued map.

On `{tau<infinity}` the terminal variables can be written as pointwise sums

```text
Z_tau = sum_{n>=1} Z_n 1{tau=n},
T_tau = sum_{n>=1} (sum_{t=1}^n Z_t) 1{tau=n}.
```

Only one summand is nonzero.  Hence `Z_tau` and `T_tau` are measurable wherever
`tau` is finite.  Section 3 proves that this event has probability one for all
`e` in a neighborhood of zero, completing the stopped-variable measurability
needed below.

Crucially, these functions of the residual coordinates contain no `e`.  The
parameter changes `Q_e`; it does not change the chart or stopping functional.

## 3. Uniform geometric tail from the SR recursion

Put

```text
b_A = log(A)+1/2.
```

Every live chart state is nonnegative.  If `Z_t>=b_A`, then

```text
R_t^+
  = (1+R_{t-1}^+)exp(Z_t-1/2)
  >= 1*exp(log A)
  = A.
```

If `Z_t<=-b_A`, the same calculation gives `R_t^->=A`.  The inclusive
threshold therefore makes `|Z_t|>=b_A` a one-step forcing event from every
live state.

Fix any finite `eta>0`.  For `|e|<=eta`, let

```text
p_eta = inf_{|e|<=eta} Q_e{|Z_1|>=b_A}.
```

The Gaussian tail probability is continuous and strictly positive in `e`, so
compactness gives `p_eta>0`.  Write `q_eta=1-p_eta<1`.  Survival through time
`n` implies that none of the first `n` forcing events occurred.  Independence
therefore gives the uniform bound

```text
sup_{|e|<=eta} Q_e{tau>n} <= q_eta^n.                 (3.1)
```

Consequences of (3.1) are:

- `tau<infinity` almost surely;
- `E_e exp(c tau)<infinity` uniformly near zero whenever
  `0<c<-log(q_eta)`; and
- every polynomial moment of `tau` is finite uniformly near zero.

No state drift, minorization of a compact set, or imported CUSUM bound is used.

## 4. Stopped Gaussian moment bounds

Under `Q_0`, let `T_n=sum_{t=1}^n Z_t`, so `T_n~N(0,n)`.  For `a>=0`,

```text
E_0 exp(a|T_n|)
  <= E_0 exp(aT_n)+E_0 exp(-aT_n)
  = 2 exp(a^2 n/2).                                  (4.1)
```

Combining Cauchy--Schwarz, (4.1), and (3.1) gives

```text
E_0[exp(a|T_n|) 1{tau=n}]
  <= sqrt(2) exp(a^2 n) q_eta^((n-1)/2),             (4.2)
```

where the harmless exponent in (4.2) is deliberately loose.  For all
sufficiently small positive `a`, the right side is summable.  Hence
`E_0 exp(a|T_tau|)<infinity` for some `a>0`.

Similarly,

```text
E_0[Z_n^2 1{tau=n}]
  <= (E_0 Z_n^4)^(1/2) Q_0{tau=n}^(1/2)
  <= sqrt(3) q_eta^((n-1)/2).
```

Summing proves `E_0 Z_tau^2<infinity`.  Together with a sufficiently small
exponential moment of `tau`, these bounds and another Cauchy--Schwarz step give

```text
E_0[|Z_tau| exp(a|T_tau|+c tau)] < infinity           (4.3)
```

for some positive `a,c`.  Shrinking the parameter neighborhood when needed,
(4.3) also integrates

```text
g = |Z_tau| (|T_tau|+eta tau)
      exp(eta|T_tau|+eta^2 tau/2).                   (4.4)
```

In particular `Z_tau`, `T_tau`, and `Z_tau T_tau` are integrable.  These are
exactly the concrete SR moment facts required by the stopped differentiation
bridge; they are consequences of the derived forcing event and Gaussian
exponential moments.

## 5. Exact mixed-reference reduction and rho scaling

The physical observation and residual conventions are

```text
X_t=mu+epsilon_t,
e=R_j-mu,
Z_t=X_t-R_j=epsilon_t-e ~ N(-e,1).
```

At `m=1`, the reused physical reference is the terminal observation
`X_tau=R_j+Z_tau`.  Its error is exactly `e+Z_tau`; there is no truncation or
window denominator.  Taking the conditional expectation of the frozen affine
reuse rule and using independence and `E[U]=0` gives

```text
F_rho(e)
  = E_e[rho(e+Z_tau)+(1-rho)U]
  = rho(e+E_e[Z_tau])
  = rho F_1(e).                                      (5.1)
```

This is a structural identity, not a numerical approximation.

## 6. Stopped likelihood identity

For a deterministic prefix `z_1,...,z_n`, the `Q_e` density relative to `Q_0`
is

```text
prod_{t=1}^n phi(z_t+e)/phi(z_t)
  = exp(-e T_n-e^2 n/2).                             (6.1)
```

The event `{tau=n}` and the variable `Z_n 1{tau=n}` are measurable with
respect to the first `n` coordinates.  Applying (6.1) separately on every
such event gives

```text
E_e[Z_n 1{tau=n}]
  = E_0[Z_n 1{tau=n} exp(-eT_n-e^2n/2)].             (6.2)
```

The geometric/Gaussian bounds in Sections 3--4 make both series of absolute
values summable for all sufficiently small `|e|`.  Summing (6.2) over `n`
therefore proves the stopped identity

```text
L_e := exp(-eT_tau-e^2 tau/2),
E_e[Z_tau]
  = E_0[Z_tau exp(-eT_tau-e^2 tau/2)].               (6.3)
```

This event-by-event proof does not assume an optional-stopping theorem for an
unbounded likelihood martingale.

## 7. Differentiation at zero

For a fixed stopped record, the derivative of the integrand in (6.3) is

```text
d/de [Z_tau exp(-eT_tau-e^2 tau/2)]
  = Z_tau (-(T_tau+e tau))
      exp(-eT_tau-e^2 tau/2).                        (7.1)
```

For `|e|<=eta`, its absolute value is bounded by (4.4).  After choosing `eta`
small enough, Section 4 proves that bound integrable.  Dominated
differentiation applied to (6.3) now gives

```text
d/de E_e[Z_tau] at e=0
  = E_0[-Z_tau T_tau]
  = -Gamma_SR.                                       (7.2)
```

Differentiating the exact map reduction (5.1) and using (7.2) yields

```text
F'_rho(0)
  = rho(1-Gamma_SR),
```

which proves the derivative claim with the sign dictated by
`Z_t=epsilon_t-e`.

## 8. Reflection, oddness, and the fixed point

Let `J(z)_t=-z_t`.  Induction in `t` on the raw recursion gives

```text
R_t^+(Jz)=R_t^-(z),
R_t^-(Jz)=R_t^+(z).
```

Thus the maximum chart value and its first inclusive crossing time are
preserved.  On a finite stopped path,

```text
tau(Jz)=tau(z),
Z_tau(Jz)=-Z_tau(z),
T_tau(Jz)=-T_tau(z),
(Z_tau T_tau)(Jz)=Z_tau T_tau(z).                    (8.1)
```

The reflection pushforward of `Q_e` is `Q_{-e}`.  Hence, writing
`G(e)=E_e[Z_tau]`, (8.1) gives `G(-e)=-G(e)`.  Therefore

```text
F_1(-e)=-e+G(-e)=-(e+G(e))=-F_1(e).
```

Exact ties, a null event under the continuous Gaussian law, map to exact ties
and do not affect `tau` or these signed terminal statistics.  Rho scaling then
makes every `F_rho` odd, so `F_rho(0)=0`.

## 9. Local instability consequence and rigor boundary

If `Gamma_SR>2`, then `F'_1(0)<-1`.  From the definition of derivative, choose
`lambda` with `1<lambda<|F'_1(0)|`.  For all sufficiently small nonzero `e`,

```text
|F_1(e)-F_1(0)|/|e| > lambda > 1.
```

Since `F_1(0)=0`, the deterministic conditional-mean iteration expands
sufficiently small nonzero errors in magnitude to first order.  This is the
precise local linear-instability conclusion.

The derivative theorem above is closed by analytic reasoning once numerical
and Lean correspondence gates pass.  A Monte Carlo lower confidence bound on
`Gamma_SR` is confirmatory only.  Until the separate Arb certificate succeeds,
the rigorous statement `Gamma_SR>2` and therefore a rigorous SR local-
instability certificate remain open.

## 10. Lean boundary

The existing Level 1--3 Lean infrastructure already supplies:

- the pointwise derivative of
  `Z exp(-eT-e^2 tau/2)` in `StoppedLikelihood.lean`;
- the dominated integral derivative interface
  `hasDerivAt_integral_stoppedIntegrand_zero` in `IntegralBridge.lean`;
- deterministic domination and abstract exponential-moment sufficient
  conditions in `Domination.lean`; and
- ordinary real derivative and affine-map algebra from Mathlib.

Track 2 will reuse that interface and formally add the finite two-chart
reflection, alarm symmetry, terminal-sign algebra, rho scaling, and derivative
consequence.

The concrete infinite SR construction, its filtration/stopping-time
measurability, (3.1), the Gaussian moment summations, identification (6.3), and
the domination instantiation remain human-proved.  Accordingly:

> The Lean theorem formalizes the algebraic/stopped-score consequence under
> explicit analytic hypotheses; the concrete SR tail, measurability,
> integrability, and domination obligations remain human-proved.

It is not an end-to-end Lean formalization of the concrete infinite SR process.
