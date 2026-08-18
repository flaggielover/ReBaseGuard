# ReBaseGuard Certified Lemma Proof Report

## 1. Executive verdict

The central inequality is certified. For the specified two-sided Gaussian
CUSUM with `k=0.5` and `h=5`, the exact continuum expectation satisfies

```text
Gamma = E[Z_tau T_tau]
      in [3.924348200582897128..., 27.849382127546703281...].
```

The lower endpoint is strictly greater than two. The proof was independently
replayed from exact dyadic candidate coefficients and outward-rounded Arb
balls. Neither Monte Carlo nor convergence of a finite grid enters the proof.

## 2. Mathematical target

Let `Z_t` be iid standard normal, define

```text
S_t^+ = max(0,S_(t-1)^+ + Z_t - 0.5),
S_t^- = max(0,S_(t-1)^- - Z_t - 0.5),
tau = inf{t>=1: max(S_t^+,S_t^-)>=5},
T_t = sum_(j<=t) Z_j.
```

The sole proof target is `E[Z_tau T_tau]>2`.

## 3. Correction to the previous `E[Z_tau^2]` shortcut

The identity

```text
E[Z_tau T_tau] = E[Z_tau^2] + E[Z_tau T_(tau-1)]
```

does not permit the inference `E[Z_tau^2]>2 => E[Z_tau T_tau]>2`, because the
cross term has no previously established sign. This proof never uses that
shortcut. It certifies the full terminal functional directly.

## 4. Exact state reduction

At a live state `s=(p,m)` and current cumulative sum `x=T_t`, let `W` be the
future terminal increment and `Y` the future increment sum through the alarm.
The future is conditionally independent of `x`, so

```text
E[Z_tau T_tau | s,x] = E_s[W(x+Y)] = a(s)x+b(s),
a(s)=E_s[W],  b(s)=E_s[WY].
```

Thus `Gamma=b(0,0)`. Reflection of all future increments proves and the test
suite independently verifies

```text
a(p,m)=-a(m,p),  b(p,m)=b(m,p).
```

The reachable continuation complex is the two axes below `h` together with
the interior triangle `p>0,m>0,p+m<h-2k=4`. An interior entry from an axis has
sum equal to the previous active level minus `2k`; every further
interior-to-interior step decreases that sum by `2k`.

## 5. Integral and dynamic equations

Set

```text
ell=m-h-k,  u=h+k-p,
q(s,z)=(max(0,p+z-k),max(0,m-z-k)).
```

For standard normal density `phi`, define

```text
(Kf)(s)   = integral_ell^u f(q(s,z)) phi(z) dz,
(K_zf)(s) = integral_ell^u z f(q(s,z)) phi(z) dz.
```

The exact absorbing rewards are

```text
r_a=phi(u)-phi(ell),
r_b=u*phi(u)+1-Phi(u)+Phi(ell)-ell*phi(ell).
```

First-step conditioning gives

```text
a=Ka+r_a,
b=Kb+K_z a+r_b.
```

## 6. Validated numerical method

An ordinary degree-12 tensor Chebyshev collocation solve constructs candidate
functions. Its coefficients are rounded to exact dyadic rationals with a
common denominator `2^50`. At that point the ordinary solve leaves the proof
path.

The certifier converts the exact candidate to power polynomials, splits the
kernel at every reset regime, replaces `phi` by its degree-100 Maclaurin
polynomial with a rigorous uniform remainder, and symbolically integrates each
piece. The resulting residual is a bivariate Arb polynomial on each of the two
regions `p+m<=1` and `p+m>=1`.

The reachable triangle is parameterized by `p=r*t`, `m=r*(1-t)`. Tensor
Bernstein conversion bounds the residual on `0<=r<=1`, `1<=r<=4`, and the two
axis tails `4<=r<=5`. The Bernstein convex-hull property is a continuum bound,
not a sampled-grid estimate.

## 7. Interval arithmetic backend

All proof-critical arithmetic uses python-flint 0.9.0 and FLINT 3.6.0 Arb
real balls at 256 bits for the residual and 192 bits for the stored contraction
artifact. Inputs are constructed from integers and rational operations.
Transcendental Gaussian quantities use Arb `exp`, `erf`, `erfc`, square root,
and `pi`; every stored endpoint is outward-enclosed.

## 8. Kernel enclosure proof

The first analytic contraction certificate uses a Gaussian block-sum forcing
event. The sharper final certificate uses a separate one-sided monotone
Bellman minorant. For the one-sided hitting function `H_t(x)`, pathwise coupling
proves monotonicity in `x`. Left cell endpoints therefore define a lower step
envelope over the entire interval, not sampled evidence.

At `n=250`, 100 cells and Arb arithmetic give

```text
H_250(0) >= 0.196685089387733776... > q_safe=0.19.
```

A one-sided upper crossing forces absorption of the two-sided chart, even if a
down alarm occurs first. Hence, uniformly over every reachable state,

```text
||K^250||_infinity <= beta=0.81 < 1.
```

Writing `t=250j+r`, positivity and sub-Markovity give

```text
||(I-K)^(-1)||_infinity
 <= sum_(t>=0)||K^t||
 <= 250/(1-0.81)
 = 1315.7894736842105264...
```

Existence and uniqueness of bounded `a,b` follow from this convergent Neumann
series.

## 9. Reward enclosure proof

Absorbing first and second Gaussian moments use the exact formulas in Section
5. When their density and CDF terms are replaced by the validated Gaussian
polynomial, the uniform density error is propagated through every multiplier
and integration length. The certifier obtains

```text
||a_hat-Ka_hat-r_a||_infinity <= delta_a
  <= 8.463460226872628e-6,

||b_hat-Kb_hat-K_z a_hat-r_b||_infinity <= delta_b
  <= 2.061651600070381e-4.
```

## 10. Tail bounds

There is no numerical tail cutoff. Continuation increments always lie in the
finite exact interval `[ell,u]`, itself contained in `[-5.5,5.5]`. Absorbing
tails are handled by complete Gaussian moment identities. The degree-100
density approximation has the uniform Lagrange bound

```text
epsilon_phi <= 3.756034448959647e-7
```

on the entire continuation interval. Its contribution to `K`, `K_z`, `r_a`,
and `r_b` is included explicitly in `delta_a,delta_b`.

## 11. Continuum and discretization error

The finite candidate is not asserted to approximate the solution by any
empirical convergence argument. Instead, its exact rational residual is
bounded on the complete continuum by symbolic integration and Bernstein range
enclosures. With

```text
C=1315.7894736842105264...,
mu=||K_z||<=E|Z|=sqrt(2/pi),
```

the exact errors satisfy

```text
E_a=||a-a_hat|| <= C*delta_a
    <= 0.011136131877464,

E_b=||b-b_hat|| <= C*(delta_b+mu*E_a)
    <= 11.962516910658128.
```

This is the mandatory continuum enclosure.

## 12. Certified interval for Gamma

The exact dyadic candidate has

```text
b_hat(0,0)=15.8868651640648002043576525466...
```

and the propagated continuum error yields

```text
Gamma in [3.9243482005828971281857775466...,
          27.8493821275467032805295275466...].
```

The lower endpoint exceeds two by more than `1.9243`.

## 13. Independent cross-checks

Two seeded 200,000-path simulations give `Gamma` estimates `15.9619` and
`15.9010`, ARL estimates near `465`, reflection balance, and
`E[T_tau^2] approximately E[tau]`. These are labelled non-rigorous.

A separate finite cellwise Arb Bellman implementation—sharing neither the
spectral candidate nor symbolic residual path—gives `18.7401484450...` on its
coarse finite discretization. It is explicitly a cross-check rather than a
continuum certificate, and it lies inside the rigorous interval.

## 14. Reproducibility

The exact package versions are locked in `requirements.lock`. The commands are

```text
make test
make diagnostic
make proof
make audit
```

Both proof and audit exit nonzero if `Gamma_L<=2`. Environment, runtime, memory,
and SHA-256 values are stored in `results/reproducibility.json`.

## 15. Trusted computing base

The trusted base is CPython integer/rational serialization, python-flint,
FLINT/Arb arithmetic and transcendental functions, the symbolic polynomial and
Bernstein checker, the monotone contraction checker, and the small audit/hash
orchestration. NumPy, SciPy, Monte Carlo, collocation convergence, and the
finite Bellman cross-check are outside the proof trusted base.

## 16. Certificate audit

The full audit reloaded the exact candidate, recomputed the monotone block
contraction, rebuilt every residual polynomial, rechecked complete Bernstein
coverage, propagated the error, verified all artifact hashes, and compared the
independent Bellman result. It returned `PASS` with
`continuum_residual_replayed=true`.

## 17. Implication for `F_1'(0)`

Using the already proved identity `F_1'(0)=1-Gamma`, the certificate gives

```text
F_1'(0) in [-26.849382127546703281...,
             -2.924348200582897128...].
```

In particular, `F_1'(0)<-1`.

## 18. Implication for `rho_c`

With the proved mixed-reuse identity `F_rho'(0)=rho F_1'(0)`, the critical
reuse fraction exists strictly inside `(0,1)`:

```text
rho_c=1/|F_1'(0)|=1/(Gamma-1)
     in [0.03724480493627555...,
         0.34195654258978959...].
```

Thus `rho<rho_c` is locally stable and `rho>rho_c` is locally unstable.

## 19. Remaining limitations

The certified interval is deliberately wide because the scientific target is
only a strict lower bound above two. The proof is specific to `k=0.5`, `h=5`,
Gaussian innovations, and `m=1`. It does not provide a closed form for Gamma,
a global nonlinear bifurcation theorem, or certification for other parameter
values. Those limitations do not affect the stated lemma.

## 20. Final theory-gate implication

The previously open antecedent in the ReBaseGuard instability theorem is now
closed by a reproducible continuum certificate. Together with the existing
score and mixed-reuse identities, it establishes a strictly interior reuse
stability threshold for the fixed model.

CERTIFIED PROOF PASS
