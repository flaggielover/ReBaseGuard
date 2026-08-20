# ReBaseGuard Phase-4C SR Certification Feasibility Report

## 1. Executive verdict

Rigorous computer-assisted certification of

```text
Gamma_SR > 2
```

for the frozen symmetric two-chart Shiryaev-Roberts detector is **feasible**.
The Phase-4C verdict is **GREEN**, but it is not a Level-4 proof and it does not
authorize final certificate generation.

All eight feasibility conditions are met:

1. the exact continuum operator has been independently derived and tested;
2. two independent continuum approximations reproduce the Phase-4B scale;
3. a rigorous compact reachable enclosure removes the problematic square
   corner;
4. reflection symmetry and genuine two-dimensionality are proved;
5. Arb transition and residual prototypes refine normally;
6. Arb certifies a continuum block contraction with resolvent at most
   `1263.6364`;
7. a pessimistic coupled error budget projects a lower bound `8.52`; and
8. a primary proof architecture and independent fallback/auditor are specified.

The principal qualification is that raw interval boxes lose cancellation and
are unusable as the final residual method. The final proof must use local
Taylor/Bernstein or equivalent polynomial residual models.

## 2. Frozen detector definition

The detector remains exactly

```text
delta = 1,
A = 520.3125 = 8325/16,
m = 1,

R_t^+ = (1+R_(t-1)^+) exp(Z_t-1/2),
R_t^- = (1+R_(t-1)^-) exp(-Z_t-1/2),

tau_SR = inf{t>=1:max(R_t^+,R_t^-)>=A}.
```

Both charts update from the same innovation and the inclusive boundary is
tested after the update. Phase-4C did not change `delta`, recalibrate `A`, or
inspect alternative detector parameters.

## 3. Exact operator derivation

Write

```text
Y^+=log(1+R^+),  Y^-=log(1+R^-),  y=(y_+,y_-).
```

The raw recursion gives

```text
R'^+ = exp(y_+ + z - 1/2),
R'^- = exp(y_- - z - 1/2),
```

and therefore

```text
q_+(y,z)=softplus(y_+ + z - 1/2),
q_-(y,z)=softplus(y_- - z - 1/2).
```

The exact continuation interval is

```text
ell(y)<z<u(y),
ell(y)=y_- - log(A) - 1/2,
u(y)=log(A) - y_+ + 1/2.
```

Both signs proposed in Phase-4B are correct. Direct raw-recursion, endpoint,
quadrature, and reflection tests independently validate these formulas.

For any bounded function `f`, define

```text
(Kf)(y)=integral_ell^u f(q(y,z)) phi(z) dz,
(K_z f)(y)=integral_ell^u z f(q(y,z)) phi(z) dz.
```

## 4. Affine state reduction

Let `x=T_t` and

```text
H(y,x)=E[Z_tau T_tau | Y_t=y,T_t=x].
```

On continuation, the next cumulative state is `x+z`; on absorption the reward
is `z(x+z)`. Substitution proves

```text
H(y,x)=a(y)x+b(y),

a=Ka+r_a,
b=Kb+K_z a+r_b,
```

with exact alarm-tail moments

```text
r_a(y)=phi(u)-phi(ell),

r_b(y)=Phi(ell)-ell phi(ell)+Phi(-u)+u phi(u).
```

Thus both `zx` and `z^2` absorption terms are present. At reset,
`y=(0,0)`, `x=0`, hence

```text
Gamma_SR=b(0,0).
```

## 5. Reachable state domain

The exact naive live domain is the open square

```text
0<=Y^+,Y^-<L,  L=log(1+A)=6.25634967... .
```

It is invariant but unnecessarily large. Phase-4C proves the identity

```text
R'^+R'^-=exp(Y^++Y^--1),
```

which is independent of `z`. Let `C` be the fixed point

```text
exp(C)=(1+A)(1+exp(C-1)/A),
exp(C)=(1+A)/(1-(1+A)/(eA)).
```

Convex endpoint maximization at fixed product proves the following compact
enclosure for every nonreset live state:

```text
exp(-1) <= R^+R^- <= 303.73145983...,
Y^++Y^- <= C = 6.7161439552...,
Y^+,Y^- >= 0.0007067857... .
```

The reset point `(0,0)` is added separately. Arb independently verifies all
inequalities in [analytic_structure.json](analytic_structure.json).

This removes more than half the naive square by area at practical grid
resolution and, more importantly, excludes its upper-right corner. The
minimum continuation width improves from approximately `0.996` on the square
to the rigorous reachable bound

```text
u-ell >= 6.79271523... .
```

The enclosure is sufficient for proof coverage; it is not claimed to be an
exact characterization of the reachable-set closure.

There is no one-dimensional state reduction. The two-observation map
`(z_1,z_2)->(Y_2^+,Y_2^-)` has a rigorously nonzero Jacobian at a continued
path, proving that the reachable set has two-dimensional interior. Sum/difference
coordinates may improve patch layout but do not reduce dimension.

## 6. Symmetry

Reflection maps

```text
(y_+,y_-,z,x)->(y_-,y_+,-z,-x).
```

It swaps the two softplus transitions, maps `ell` to `-u`, and preserves the
terminal reward. Therefore

```text
a(y_+,y_-)=-a(y_-,y_+),
b(y_+,y_-)= b(y_-,y_+).
```

In particular, `a=0` on the diagonal. A final proof may compute on one
half-domain and reflect. The feasibility solvers intentionally retained both
halves so antisymmetry/symmetry errors could serve as independent checks; the
observed errors were below `6.1e-14`.

## 7. Approximate continuum solution

Two ordinary floating-point pathways were implemented outside the TCB.

The first uses full-square bilinear collocation and Gauss-Legendre integration:

| Nodes per axis | Approximate `Gamma_SR` |
|---:|---:|
| 41 | 17.16094 |
| 61 | 17.23072 |
| 81 | 17.25528 |
| 101 | 17.26655 |
| 121 | 17.27275 |

Second-order grid extrapolation gives `17.28675`.

The second uses direct tensor-Chebyshev collocation of the exact nonlinear
operator. Degree 16 gives

```text
Gamma_SR = 17.28681883,
independent-grid residual_a = 5.21e-7,
independent-grid residual_b = 8.07e-6,
collocation condition number = 1912.
```

The coefficient symmetry is exact after formal symmetrization. The solution is
smooth on the reachable enclosure: approximately `a in [-0.612,0.612]` and
`b in [10.26,17.29]`. The strongest full-square curvature occurs in the
unreachable upper-right region. The strongest measured reachable curvature is
near a one-chart boundary and remains moderate.

These calculations construct candidates only. Their small residuals are not
proof bounds.

## 8. Comparison with Phase-4B Monte Carlo

The Phase-4B estimate was

```text
17.27208470 with SE 0.02802695.
```

The finest bilinear value differs by `0.00066`. The independently extrapolated
and spectral values near `17.2868` differ from Monte Carlo by `0.0147`, or
`0.53` Monte Carlo standard errors. They are statistically and numerically
consistent. No convention discrepancy was found.

The exact-dyadic degree-16 candidate used by the interval/error-budget
prototype has reset value

```text
304112932968465 / 17592186044416
=17.286818829715287... .
```

## 9. Interval prototype

The prototype uses python-flint/Arb at 192 bits, exact dyadic degree-16
coefficients, Arb softplus/log/exp, analytic Arb Gaussian tails, and
positive-measure interval partitions in `z`. Five representative regions were
checked: reset, plus boundary, minus boundary, symmetry diagonal, and strongest
reachable curvature.

Transition widths shrink essentially linearly. For example, at maximum
softplus curvature the plus-transition width fell from `0.12500001` to
`0.03125001` when state/innovation widths were quartered.

Raw interval residual widths also decrease monotonically:

| Region | `b` width at 1/8 | at 1/16 | at 1/32 |
|---|---:|---:|---:|
| reset neighborhood | 14.4200 | 6.2993 | 2.9112 |
| one-chart boundary | 13.7078 | 5.6942 | 2.6115 |
| symmetry diagonal | 2.2696 | 1.0989 | 0.5409 |
| reachable curvature | 9.1146 | 4.1718 | 2.0038 |

This is normal refinement, not dependency explosion. But raw boxes discard the
cancellation between the candidate and its Bellman image, so they would require
an impractical grid. They are rejected as the final residual architecture.

## 10. Transition enclosure analysis

For `s(t)=softplus(t)`,

```text
s'(t)=sigma(t),
s''(t)=sigma(t)(1-sigma(t))<=1/4.
```

Consequently:

- `q_+` increases in `y_+` and `z`;
- `q_-` increases in `y_-` and decreases in `z`;
- each target coordinate is globally 1-Lipschitz in its active source
  coordinate and in `z`;
- the transition is globally convex in each affine softplus argument; and
- no cross-source dependency exists before candidate composition.

On the reachable continuation domain, Arb bounds the sigmoid slope between
approximately `0.000707` and `0.998082`; its worst second derivative is the
exact global value `1/4`. The continuation endpoints are affine and their
uncertain strips contract directly with state-cell width.

The viable enclosure mechanism is therefore local polynomial/Taylor expansion
of softplus and the composed Chebyshev candidate, with an Arb remainder and
Bernstein range evaluation. Degree 4–8 local models on adaptively subdivided
patches should preserve the residual cancellation seen by the spectral solve.
Global composition into one high-degree polynomial is not recommended.

## 11. Block contraction analysis

Four routes were assessed.

**A. Uniform one-step extreme observation.** Valid but useless: its resolvent
is about `6.97e10`.

**B. Analytic multi-step block sum.** If over `n` observations

```text
sum Z_i >= log(A)+n/2
```

then the plus chart must alarm; the reflected event forces the minus chart.
At the best tested integer `n=9`, Arb certifies

```text
q=0.000337323860868...,
||(I-K)^-1|| <= 26680.5911.
```

This is rigorous but unnecessarily conservative.

**C. Two-dimensional cellwise survival propagation.** It should approach the
two-sided ARL scale and may improve the resolvent, but it duplicates difficult
2D geometry and is not necessary for feasibility.

**D. One-sided monotone SR minorant.** This is the recommended route. The
one-sided plus-chart hitting probability is pathwise nondecreasing in its
starting state. A 200-cell left-endpoint step lower envelope is therefore a
continuum bound, not sampled-grid inference. Since a plus-chart hit forces
two-chart absorption, Arb proves

```text
P(hit by 139 | any live state) > 0.11,
||K^139||_infinity <= 0.89,
||(I-K)^-1||_infinity <= 139/0.11
                         = 1263.63636364.
```

Every Arb transition row was independently checked to contain total mass one.

## 12. Resolvent bound feasibility

Let `R=1263.6364` and `c_z=||K_z||<=E|Z|=sqrt(2/pi)=0.797885`. If
`epsilon_a` and `epsilon_b` are global residual bounds, triangular propagation
gives

```text
||a-a_hat|| <= R epsilon_a,

||b-b_hat||
  <= R epsilon_b + R^2 c_z epsilon_a.
```

The squared-resolvent coefficient makes `epsilon_a` the controlling quantity.
The degree-16 diagnostic residuals would imply only `0.674` total `b` error if
they were rigorous.

A deliberately pessimistic target budget is

```text
epsilon_a <= 5e-6,
epsilon_b <= 1.5e-3,
additional feasibility reserve = 0.5.
```

It yields

```text
a-induced b error = 6.3702,
direct b error    = 1.8955,
projected lower   = 17.2868-6.3702-1.8955-0.5
                  = 8.5211 > 2.
```

With the other targets fixed, feasibility fails only near
`epsilon_a=1.01e-5` or `epsilon_b=0.00666`. This leaves meaningful room above
the observed candidate residual scales.

## 13. Candidate approximation strategy

Four architectures were compared.

| Architecture | Continuum rigor | Main risk | Expected cost | Verdict |
|---|---|---|---|---|
| Validated spectral residual with local Taylor/Bernstein bounds | Direct global residual plus resolvent | preserving nonlinear composition cancellation | moderate | **Primary** |
| Cellwise interval affine Bellman iteration | direct enclosure by monotone/set-valued updates | wrapping over many iterations and 2D cell count | moderate-high | **Fallback** |
| Verified collocation/interval linear system | requires interpolation-remainder proof | interval inverse at condition ~1900 and projection error | moderate | not recommended |
| Global raw interval boxes | formally simple | demonstrated cancellation loss | prohibitive | rejected |

The primary architecture is:

1. construct a degree-16 or modestly higher tensor-Chebyshev candidate in
   ordinary floating point;
2. quantize coefficients exactly to dyadics and impose symmetry exactly;
3. cover the rigorous reachable half-domain by adaptive patches;
4. on each patch, use Arb local Taylor models for softplus, Gaussian factors,
   and candidate composition;
5. integrate the local `z` polynomial exactly or with certified Arb remainder;
6. use Bernstein coefficients to bound both residuals;
7. certify the one-sided monotone block contraction independently; and
8. propagate the triangular residual errors to an interval for `b(0,0)`.

The fallback must remain separately implemented cellwise interval Bellman
iteration, using interval transitions and affine `a,b` enclosures rather than
the spectral residual evaluator.

## 14. Expected rigorous error budget

The feasibility center is the exact dyadic candidate value `17.28681883`.
Candidate approximation error is not separately trusted: once coefficients are
fixed, the residual theorem absorbs all approximation error.

| Budget item | Pessimistic allowance |
|---|---:|
| global `a` residual | `5e-6` |
| propagated `a` contribution to `b` | `6.3702` |
| global `b` residual | `0.0015` |
| propagated direct `b` contribution | `1.8955` |
| geometry/symmetry error | `0` after formal proof |
| Gaussian tail error | included in Arb residual |
| contraction uncertainty | included through safe `q=0.11` |
| extra feasibility reserve | `0.5` |
| expected lower endpoint | `8.5211` |

The scientifically necessary target is only two. A plausible final enclosure
is therefore very wide, for example approximately `[8,27]`; no effort should be
spent tightening it after the lower endpoint exceeds two.

## 15. Reusable CUSUM certification machinery

The following infrastructure can be reused substantially unchanged:

- pinned python-flint/Arb backend and precision context;
- rational/dyadic serialization and ball records;
- Gaussian density, CDF, mass, and tail-moment enclosures;
- Chebyshev candidate serialization;
- multivariate polynomial and Bernstein range machinery;
- residual-to-resolvent propagation pattern;
- certificate schema, hashes, CLI/audit orchestration, and failure gates;
- full-replay philosophy and test harness.

The old CUSUM certificate and its artifacts are not inputs to the new numerical
claim and remain read-only.

## 16. New SR-specific proof work

The final proof requires genuinely new code for:

- the softplus SR transition and its local polynomial remainder;
- the curvilinear reachable-domain patch cover;
- half-domain/reflection patch bookkeeping;
- variable continuation endpoints and endpoint-strip handling;
- cancellation-preserving local residual integration;
- the one-sided SR monotone contraction matrix; and
- SR-specific certificate/auditor invariants.

Approximately 1,500–2,500 lines of proof/generation code and 800–1,200 lines of
independent auditor/tests are expected. Candidate construction code is outside
the TCB.

## 17. Trusted computing base

The recommended minimal TCB is:

- CPython control flow and exact integer/rational serialization;
- python-flint `0.9.0` and FLINT/Arb `3.6.0` outward-rounded arithmetic;
- exact dyadic candidate coefficients;
- local polynomial/Taylor remainder logic;
- Bernstein range evaluation;
- monotone contraction construction; and
- compact residual/resolvent/audit orchestration.

NumPy, SciPy, Monte Carlo, bilinear refinement, and spectral collocation remain
candidate-building diagnostics outside the TCB. No new numerical library is
needed.

## 18. Independent audit architecture

The eventual auditor should reconstruct from compact exact artifacts:

1. `A=8325/16`, `delta=1`, and all operator formulas;
2. the Arb reachable constants and patch coverage;
3. symmetry of exact dyadic coefficients;
4. every local softplus/Gaussian polynomial remainder;
5. every Bernstein residual bound;
6. the one-sided monotone transition matrix, row masses, and 139-step hit bound;
7. the resolvent and triangular error propagation;
8. the final interval for `b(0,0)` and the strict test `lower>2`; and
9. all artifact SHA-256 values.

The auditor need not trust or reproduce the floating-point candidate solve.
It may accept arbitrary exact coefficients because the independently rebuilt
residual bound validates them. The unavoidable trusted components are Arb,
the exact arithmetic/runtime, and the small mathematical audit implementation.

## 19. Estimated engineering/compute cost

Estimated full-certification effort is four to eight focused engineering days:

- 1–2 days for Taylor/Bernstein transition and integration envelopes;
- 1–2 days for reachable patch generation and residual subdivision;
- 1 day for contraction/certificate integration;
- 1–3 days for the independent auditor, regression tests, and refinement.

Expected proof-generation compute is approximately 4–24 workstation hours,
depending on adaptive patch count and Taylor degree. A preliminary target is
5,000–30,000 half-domain patches at 192–256 Arb bits. Full independent replay
should be of comparable order. No cluster or paid external compute appears
necessary.

These estimates are uncertain by roughly a factor of two because the global
Taylor/Bernstein residual has not yet been implemented.

## 20. Mathematical risks

The three leading risks are:

1. **Coupled `a` error.** It is amplified by `R^2||K_z||`; the global
   `a` residual must remain below roughly `1e-5`.
2. **Patch-boundary cancellation.** A poorly designed Taylor model could repeat
   the raw-box failure even though the underlying transition is well behaved.
3. **Curvilinear coverage/audit complexity.** The reachable enclosure and
   half-domain must be covered without gaps or trusting floating geometry.

Secondary risks are adaptive patch count, polynomial degree growth near a
single-chart boundary, and the moderate spectral condition number. No
mathematical inconsistency, noncompactness, empty continuation strip, or
unusable contraction was found.

## 21. Final recommendation

Classify Phase-4C **GREEN**. Rigorous SR certification is scientifically and
computationally credible, and the large diagnostic margin survives a
pessimistic resolvent/error budget.

Do not begin final certification automatically. The next separately approved
phase should implement the cancellation-preserving local Taylor/Bernstein
residual certificate, retain cellwise interval Bellman iteration as an
independent fallback, stop refinement immediately when the audited lower
endpoint exceeds two, and preserve all protected Level-3 and Phase-4B
artifacts unchanged.

Final regression status is: 90 tests passed; the Phase-4A and Phase-4B audits
passed; the protected Level-3 certificate passed a fresh full Arb replay; and
the independent Phase-4C audit passed every feasibility, protection, and stop-
gate check.

SR OPERATOR FORMULATION:
PASS

APPROXIMATE CONTINUUM GAMMA:
17.28681883 (degree-16 spectral candidate; non-rigorous)

CONSISTENT WITH MC 17.27:
YES

RIGOROUS COMPACT DOMAIN:
PASS

SYMMETRY REDUCTION:
PASS

INTERVAL PROTOTYPE:
PASS (raw boxes rejected; cancellation-preserving Taylor/Bernstein bounds required)

BLOCK CONTRACTION:
PASS

RESOLVENT FEASIBILITY:
PASS

EXPECTED CERTIFIABLE LOWER BOUND:
Approximately 8.5 under the pessimistic prototype budget

RECOMMENDED PROOF ARCHITECTURE:
Exact-dyadic spectral candidate plus local Arb Taylor/Bernstein continuum residual certificate and certified one-sided monotone block contraction

FALLBACK ARCHITECTURE:
Independently implemented cellwise interval affine Bellman iteration on the rigorous reachable enclosure

ESTIMATED FULL CERTIFICATION EFFORT:
4-8 engineering days plus approximately 4-24 workstation compute hours

SR CERTIFICATION VERDICT:
GREEN

BEGIN FULL CERTIFICATION:
NO

LEVEL-3 STATUS:
UNCHANGED

PHASE-4B STATUS:
UNCHANGED

TOP 3 RISKS:
1. Squared-resolvent amplification of the global a-residual
2. Loss of Bellman residual cancellation at Taylor/patch boundaries
3. Exact curvilinear reachable-domain coverage and independent replay complexity

TOP 3 REASONS FOR THE VERDICT:
1. Independent continuum solvers reproduce Gamma near 17.29 and agree with Phase-4B Monte Carlo
2. Arb proves a compact reachable enclosure and a usable 1263.64 resolvent over the full continuum
3. A degree-16 candidate and pessimistic coupled error budget leave a projected lower endpoint near 8.5
