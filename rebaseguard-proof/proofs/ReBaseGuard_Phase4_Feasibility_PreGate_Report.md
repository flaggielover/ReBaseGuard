# ReBaseGuard Phase-4 Feasibility Pre-Gate Report

## 1. Executive verdict

Both pre-gate questions are resolved.

The discrepancy `18.7401` versus `15.87` is **finite discretization bias** in
the historical cross-check. Its transition rule sends every off-grid next
state to the componentwise lower grid point. This systematically moves the
CUSUM state away from its alarm boundary: at the published 12-cell resolution
the same finite chain has ARL `2099.53`, rather than the correct scale near
`465`. The historical result remains reproducible and is preserved unchanged.
A separately implemented reachable-geometry solver converges toward `15.87`;
second-order extrapolation gives the diagnostic point estimate

```text
Gamma = 15.8868236 (non-rigorous point estimate).
```

The independently certified continuum theorem is unaffected. Its full replay
audit still returns `PASS` and certifies

```text
Gamma in [3.924348200582897128..., 27.849382127546703281...].
```

The score identity does survive removal of CUSUM structure. It is an arbitrary
stopping-time likelihood-ratio identity, provided the stopping rule is the same
path functional throughout the parametric family and the stopped likelihood
and terminal statistic satisfy the stated integrability conditions. CUSUM is
used to verify regularity, reflection symmetry, and the detector-specific
witness `Gamma>2`; it is not used in the score differentiation itself.

**Level-3 theorem:** UNCHANGED.  
**Level-4 detector-independent route:** GREEN.  
**Second-detector feasibility gate:** GO, but no second detector is implemented
in this pre-gate.

## 2. Gamma discrepancy reproduction

All four numerical pathways use `k=0.5`, `h=5`, `m=1`, initial state `(0,0)`,
and `T_t=sum_{j=1}^t Z_j`.

| Object | Result | Status |
|---|---:|---|
| Certified continuum enclosure | `[3.9243482, 27.8493821]` | rigorous proof |
| Historical finite Arb, 12 cells/96 bins | `18.7401484450398286...` | exactly reproduced |
| External-referee Monte Carlo | `15.8743`, SE `0.0404` | diagnostic |
| Local MC, seed 1729, one million paths | `15.84294`, SE `0.04029` | diagnostic |
| Local MC, seed 20260818, one million paths | `15.84931`, SE `0.04030` | diagnostic |
| Combined local MC | `15.84612`, SE `0.02849` | diagnostic |
| Refined Bellman, 80 axis cells | `15.8707561` | diagnostic |
| Refined Bellman, second-order extrapolation | `15.8868236` | diagnostic point estimate |
| Continuum candidate value | `15.8868652` | candidate center, not a proof by itself |

The two local Monte Carlo seeds differ by only `0.0064`. Their combined result,
the external result, the refined Bellman sequence, and the continuum candidate
are statistically/numerically compatible. Each is decisively incompatible
with `18.7401`: the gap from either one-million-path local run exceeds 70 of
that run's Monte Carlo standard errors.

The exact diagnostic data, environment, seeds, hashes, refinement tables, and
path traces are stored in `diagnostics/phase4_pregate.json`.

## 3. Convention matrix

Source references below are to `src/rebaseguard_certify/` unless otherwise
stated.

| Convention | Direct MC/oracle | Historical finite Arb | Refined diagnostic | Continuum certificate |
|---|---|---|---|---|
| Alarm after update | Yes; `model.py:54-62`, `diagnostics.py:81-87` | Continuation limits use post-update crossing; `bellman.py:49-56` | Same exact limits; `refined_bellman.py:144-152` | `proofs/derivation.md`, Fredholm equations |
| `tau` starts at 1 | Yes; `model.py:87` | First-step Bellman equation | First-step Bellman equation | Yes |
| Crossing increment is `Z_tau` | Stored from the firing step; `diagnostics.py:89-91` | Absorbing tail integrates the current `z` | Same | Same |
| Terminal reward | `z*(T+z)`; `model.py:65-79` | `r_a` supplies `zx`; `r_b` supplies `z^2`; `bellman.py:71-88` | Same decomposition; `refined_bellman.py:186-200` | Exactly `z(x+z)` |
| `T_tau` definition | Current `z` added at `diagnostics.py:83` before storage | Affine state variable is current pre-step `x`; absorbing reward adds current `z` | Same | `T_tau=sum_{t<=tau}Z_t` |
| Threshold comparison | Inclusive `>=h`; `model.py:58-61` | Continuation is open `ell<z<u`; endpoints have zero Gaussian mass | Same | Same |
| Overshoot | Preserved in terminal state and reward | Full Gaussian tails, no clipping of reward | Full Gaussian tails | Full Gaussian tails |
| Both arms use same `z` | Yes; `model.py:55-56` | `next_p` and `next_m` use the same midpoint; `bellman.py:57-58` | Same exact destination; `refined_bellman.py:58-61` | Same transition map |
| Tie handling | Up arm first; `model.py:58-61` | Not separately coded | Not separately coded | Ties are unreachable for live states and have probability zero |
| Initial state | Exactly `(0,0)`; `model.py:85` | `b_values[0,0]`; `bellman.py:89` | Explicit `(0,0)` index; `refined_bellman.py:224` | `Gamma=b(0,0)` |
| Minimum dwell/history | None | None | None | None; `m=1` |
| Reuse window | `m=1` terminal observation | Solver targets `m=1` | Solver targets `m=1` | Certified theorem fixes `m=1` |
| Reachable geometry | Produced pathwise | Full square allocated, but reachable rows form a closed block | Axes plus `p+m<=4`; `refined_bellman.py:40-55` | Exact axes/triangle complex |
| State approximation | None | Componentwise floor after midpoint; `bellman.py:23-26,56-61` | Piecewise-linear interpolation on exact transition curves | No state-grid proof assumption |
| Reward approximation timing | None | Tail reward evaluated before the finite continuation solve | Same | Exact tail formulas |
| Continuation/absorption | Post-update `>=h` | `ell<z<u` versus complementary tails | Same | Same |
| Gaussian tail signs | Direct normal draws | `phi(u)-phi(ell)` and full second-tail formula; `bellman.py:71-78` | Same; `refined_bellman.py:186-193` | Same, outward-rounded Arb |

The deterministic tie rule is defensive only. Before alarm, both post-update
arms cannot simultaneously exceed `h=5`: if both are positive their sum is the
prior sum minus `2k`, which is below the required value for a double crossing.

## 4. Direct Monte Carlo validation

The scalar oracle returns the two updated arms, updated cumulative sum, alarm
direction, and reward. A separate replay routine in `pathwise.py` independently
reimplements the formulas and does not call the oracle. Fixed positive,
negative, reset-heavy, and overshoot paths agree at every step.

Unit tests additionally cover:

- zero-state resets;
- positive and negative boundary crossings;
- exact equality at the threshold;
- a crossing missed by `1e-6`;
- large overshoot; and
- reflected paths, including equality of `Z_tau*T_tau`.

The two one-million-path simulations report:

| Statistic | Seed 1729 | Seed 20260818 |
|---|---:|---:|
| `Gamma` | 15.84294 | 15.84931 |
| SE | 0.04029 | 0.04030 |
| ARL = `E[tau]` | 465.3634 | 465.7907 |
| `E[T_tau^2]` | 464.6911 | 465.5933 |
| `E[T_tau^2]-E[tau]` | -0.6723 | -0.1974 |
| `E[Z_tau]` | 0.00020 | 0.00161 |
| `E[T_tau]` | -0.00855 | 0.03245 |
| Up-alarm fraction | 0.50018 | 0.50040 |
| Up-minus-down gap | 0.00036 | 0.00079 |

Wald's second identity, reflection balance, and zero terminal/cumulative means
are all satisfied to Monte Carlo precision. Monte Carlo remains diagnostic and
is not used in the certified inequality.

## 5. Bellman implementation audit

Let `s=(p,m)` be a live state, `x=T_t`, `q(s,z)` the post-update state, and
`C(s)={ell<z<u}` the continuation increments. Write

```text
H(s,x)=E[Z_tau T_tau | s,x]=a(s)x+b(s).
```

On absorption, the current increment is the terminal increment and

```text
Z_tau T_tau = z(x+z) = zx+z^2.
```

On continuation, first-step conditioning gives

```text
H(q(s,z),x+z)
  = a(q(s,z))x + z a(q(s,z)) + b(q(s,z)).
```

Matching the coefficient of `x` and the constant term therefore yields

```text
a(s) = integral_C a(q(s,z)) phi(z) dz
       + integral_A z phi(z) dz
     = K a(s) + r_a(s),

b(s) = integral_C [b(q(s,z))+z a(q(s,z))] phi(z) dz
       + integral_A z^2 phi(z) dz
     = K b(s) + K_z a(s) + r_b(s).
```

With `ell=m-h-k` and `u=h+k-p`, the full absorbing-tail moments are

```text
r_a = phi(u)-phi(ell),
r_b = u phi(u)+1-Phi(u)+Phi(ell)-ell phi(ell).
```

At the initial state `x=0`, hence

```text
Gamma=H((0,0),0)=b(0,0).
```

The historical solver implements both reward pieces correctly:
`reward_a` is used in the `a` solve, while `reward_b + kernel_z*a_values` is
used in the `b` solve. There is no `zx`/`z^2` omission, sign error, or one-step
reward shift. The continuum derivation uses the same equations.

## 6. Root cause of the 18% discrepancy

The root cause is the historical destination projection

```text
index = floor(next_state * cells / h).
```

For an active axis state this replaces almost every off-grid active CUSUM value
by a smaller value. The finite chain is therefore systematically farther from
the threshold and much too persistent. Arb rigorously encloses the solution of
that finite chain, but it does not turn the biased finite chain into the
continuum process.

Three ablations isolate the mechanism:

1. **Unreachable square states:** deleting 108 of the 169 states at the
   published resolution leaves exactly the same Arb ball for `Gamma`.
2. **Increment bins:** at 12 state cells, increasing 24, 48, 96, 192, and 384
   bins stabilizes near `18.73`; it cannot explain the gap.
3. **State refinement:** retaining the floor rule moves the value slowly
   downward and the ARL slowly toward its proper scale:

| Historical state cells | Gamma | Finite ARL |
|---:|---:|---:|
| 4 | 21.06623 | 24707.1 |
| 8 | 19.68953 | 4310.5 |
| 12 | 18.74015 | 2099.5 |
| 16 | 18.07653 | 1447.8 |
| 20 | 17.72277 | 1161.9 |
| 24 | 17.47045 | 1011.8 |
| 32 | 17.08884 | 827.1 |

This is classification **D. FINITE DISCRETIZATION BIAS**, specifically a
large one-sided piecewise-constant state-projection bias. It is not a Monte
Carlo bug, convention mismatch, Bellman reward bug, or continuum-formulation
issue.

## 7. Corrected finite Bellman result

The corrected diagnostic solver uses only the exact reachable state complex
and piecewise-linear interpolation along the exact one-dimensional transition
curves. On each interpolation segment it integrates Gaussian mass, first
moment, and second moment analytically. Its sparse float64 solve is explicitly
non-rigorous and outside the proof trusted base.

| Axis cells | Reachable nodes | Gamma | Finite ARL |
|---:|---:|---:|---:|
| 5 | 17 | 12.50343 | 267.79 |
| 10 | 49 | 14.90961 | 399.20 |
| 20 | 161 | 15.63264 | 447.42 |
| 40 | 577 | 15.82264 | 460.84 |
| 60 | 1249 | 15.85826 | 463.39 |
| 80 | 2177 | 15.87076 | 464.29 |

The maximum row-mass error is `2.3e-16`; antisymmetry of `a` and symmetry of
`b` hold within `4e-14`. Second-order extrapolation from the last two stored
levels gives

```text
Gamma_point = 15.8868235772.
```

This agrees with the independently constructed continuum candidate
`15.8868651641` and with both Monte Carlo sources. The point estimate is not a
new certificate; the wide certified continuum interval remains the proof.

## 8. Impact on the certified Level-3 theorem

| Claim or artifact | Impact | Reason |
|---|---|---|
| Historical finite cross-check | Affected | Its point estimate has large finite-state bias |
| Continuum residual certificate | None | Does not use the historical finite transition matrix |
| Global block contraction | None | Analytic/monotone continuum proof, independently replayed |
| Resolvent propagation | None | Independently replayed with original Arb artifacts |
| Exact score identity | None | Analytic likelihood-ratio argument |
| `Gamma>2` | None | Certified lower endpoint remains `3.9243...` |
| `F_1'(0)<-1` | None | Follows from unchanged identity and certificate |
| Interior `rho_c` | None | Mixed-reuse scaling remains valid |

The historical solver SHA-256 remains
`5731eb539d73d0f0ca578c22ebc48be14220c9cb61e71d2ac816b9c85dc48343`.
The certificate SHA-256 remains
`85e68c7dde306f2e6ce464203def22089e9b935d1cfca4b4944cef191d80545e`.
The final full replay audit returned `PASS`, including artifact hashes,
continuum residual, block contraction, resolvent propagation, and
`Gamma_lower>2`.

## 9. Score-proof dependency table

| Proof step | Required assumptions | CUSUM required? | Symmetry required? |
|---|---|---:|---:|
| Define `Q_e: Z_t~N(-e,1)` | Gaussian location parameterization | No | No |
| Fixed-path likelihood product | iid observations; common dominating measure | No | No |
| Stop likelihood at `tau` | `tau` is a parameter-invariant stopping rule; stopped likelihood is UI | No | No |
| Make terminal window measurable | `tau>=m` or an explicit padding convention | No | No |
| Write `F(e)=e+E_e[W]` | Reuse-update definition | No | No |
| Differentiate under expectation | local domination/uniform integrability | No | No |
| Identify stopped Gaussian score `-T_tau` | Gaussian mean `-e` convention | No | No |
| Convert expectation to covariance | stopped score has mean zero | No | No |
| Expand terminal-window covariance | finite integrable sum | No | No |
| Replace covariance by raw `E[Z*T]` | `E[T_tau]=0`; optional stopping suffices | No | No |
| Obtain `E[Z_{tau-r}]=0` | reflection symmetry or another centering argument | No | Yes, as used here |
| Establish `F(0)=0` | `E[W]=0`, supplied by detector symmetry or explicit centering | No | Yes/suitable replacement |
| Prove exponential tail for this detector | detector-specific escape argument | Yes, for this verification | No |
| Prove `Gamma>2` at `(0.5,5,1)` | certified CUSUM continuum equations | Yes | Used by certificate reduction |
| Mixed-reuse scaling | linear mixture; fresh term independent with mean zero | No | No |

Two points sharpen the old proof. First, `E[L_tau]=0` is a stopped-score
normalization/martingale fact, not a reflection-symmetry fact. Second, for
centered Gaussian increments, optional stopping gives `E[T_tau]=0`; therefore
`Cov(Z_{tau-r},T_tau)=E[Z_{tau-r}T_tau]` even if the terminal observation has a
nonzero mean. Symmetry is essential for a zero fixed point in the uncentered
reuse map, not for the derivative covariance identity.

## 10. Gaussian arbitrary-stopping-time theorem

**Theorem (Gaussian stopped-reuse derivative).** Let the canonical observations
have law `Q_e` under which `Z_t` are iid `N(-e,1)`. Let `tau` be any fixed
stopping-time functional of the observation path with `tau>=m` almost surely.
Assume a geometric/exponential tail strong enough that, for some `c>0`,

```text
Q_0(tau>n) <= C exp(-cn),
```

and hence the stopped likelihood and the terminal statistic below are locally
uniformly integrable. Define

```text
W_bar_tau,m = (1/m) sum_{r=0}^{m-1} Z_{tau-r},
F(e) = e + E_e[W_bar_tau,m].
```

Then

```text
F'(0)
  = 1 - Cov_0(W_bar_tau,m,T_tau)
  = 1 - (1/m) sum_{r=0}^{m-1} Cov_0(Z_{tau-r},T_tau).
```

No CUSUM recursion or reflection symmetry is used in this identity.

**Proof.** On `F_t`, the Gaussian likelihood ratio is

```text
M_t(e)
 = product_{j<=t} phi(Z_j+e)/phi(Z_j)
 = exp(-e T_t - t e^2/2).
```

The exponential tail supplies uniform integrability of `M_{tau∧n}(e)` for
sufficiently small `|e|`; therefore optional stopping and passage to the limit
give `E_0[M_tau(e)]=1` and

```text
E_e[G_tau]=E_0[G_tau M_tau(e)]
```

for the integrable stopped statistics used here. A direct sufficient
domination argument is available: decompose by `{tau=n}`, apply
Cauchy-Schwarz, use `T_n~N(0,n)`, and combine
`Q_0(tau=n)^(1/2)<=C^(1/2)e^{-cn/2}` with the normal exponential moment
`E[e^{2 delta |T_n|}]<=2e^{2 delta^2 n}`. For sufficiently small `delta`, the
resulting geometric series remains summable after multiplication by the
polynomial factors in `tau`, `W_bar`, and `T_tau`. This justifies both the
stopped change of measure and differentiation below.

Consequently

```text
F(e)=e+E_0[W_bar_tau,m exp(-eT_tau-tau e^2/2)].
```

Since

```text
d/de M_tau(e)|_{e=0} = -T_tau,
```

dominated differentiation yields

```text
F'(0)=1-E_0[W_bar_tau,m T_tau].
```

Differentiating `E_0[M_tau(e)]=1` at zero gives `E_0[T_tau]=0`; equivalently,
this follows from optional stopping of the centered Gaussian random walk.
Hence

```text
E_0[W_bar_tau,m T_tau]=Cov_0(W_bar_tau,m,T_tau).
```

Linearity of covariance gives the stated sum. QED.

If the stopping rule is reflection-equivariant, then
`E_0[W_bar_tau,m]=0` and thus `F(0)=0`. Without symmetry the derivative theorem
still holds, but zero need not be a fixed point. A parameter-dependent detector
rule is outside the theorem unless its explicit derivative contribution is
added.

## 11. Exponential-family score formulation

**Theorem (general stopped-score identity).** Let `P_theta` be a regular iid
one-parameter family with density `f_theta`, reference parameter `theta_0`, and
one-observation score

```text
ell(z)=partial_theta log f_theta(z)|_{theta_0}.
```

Let `tau` be a parameter-invariant stopping-time functional and suppose the
stopped likelihood is differentiable in `L1`, with all products below
uniformly integrable. Put

```text
L_tau=sum_{t=1}^tau ell(Z_t).
```

For an `F_tau`-measurable statistic `G_theta` that is also differentiable under
the expectation,

```text
d/dtheta E_theta[G_theta]|_{theta_0}
  = E_0[dot G_theta]
    + Cov_0(G_theta0,L_tau).
```

If `G` has no explicit parameter dependence, only the covariance remains.

**Proof.** The stopped likelihood ratio is

```text
M_tau(theta)=product_{t<=tau} f_theta(Z_t)/f_theta0(Z_t).
```

By the stated `L1` differentiability,

```text
dot M_tau(theta_0)=M_tau(theta_0)L_tau=L_tau.
```

Differentiate
`E_theta[G_theta]=E_0[G_theta M_tau(theta)]`. This gives

```text
E_0[dot G_theta]+E_0[G_theta0 L_tau].
```

Differentiating `E_0[M_tau(theta)]=1` gives `E_0[L_tau]=0`, converting the last
term to covariance. QED.

For a canonical exponential family
`f_theta(z)=h(z)exp(theta s(z)-A(theta))`, the score is
`ell(z)=s(z)-A'(theta_0)`. The sign and any direct derivative term are dictated
by the chosen parameterization. In the ReBaseGuard Gaussian error
parameterization, `ell(z)=-z`, so `L_tau=-T_tau`, while the explicit leading
term `e` contributes `+1`. This is exactly why the specialization is
`1-Gamma`; that form must not be copied unchanged to other parameterizations.

## 12. Role of symmetry

| Question | Is reflection symmetry required? |
|---|---|
| A. Derive the stopped-score covariance identity | No |
| B. Express covariance as a raw product | Not if the other factor has mean zero; optional stopping gives `E[T_tau]=0` here |
| C. Prove `E[Z_{tau-r}]=0` | Yes for the current argument, or another centering mechanism is needed |
| D. Prove `E[L_tau]=0` | No; likelihood normalization/optional stopping gives it |
| E. Make zero a fixed point | Yes for the uncentered symmetric monitor, or explicitly center the update |

A one-sided detector may therefore retain the stopped-score theorem while
having nonzero terminal means and a nonzero reference fixed point. Its local
analysis must center at the actual fixed point or use a centered reuse
statistic; it must not be rejected merely for lacking reflection symmetry.

## 13. Strongest detector-independent theorem currently justified

**Theorem A — general stopped-score derivative.** Under the regularity,
parameter-invariant stopping-rule, and uniform-integrability assumptions of
Section 11, the derivative of a stopped expectation equals its explicit
derivative plus covariance with the stopped path score.

**Corollary B — Gaussian monitor.** For any sufficiently integrable stopping
time on iid `N(-e,1)` innovations,

```text
F'(0)=1-(1/m)sum_r Cov_0(Z_{tau-r},T_tau).
```

If the monitor/reuse statistic is reflection-equivariant, zero is a fixed
point. If `E_0[tau]<infinity`, `E_0[T_tau]=0`, so the covariance may be written
as the corresponding raw product even without reflection symmetry.

**Corollary C — mixed reuse.** If an independent fresh component has mean zero
and the reuse fraction is `rho`, then

```text
F_rho'(0)=rho F_1'(0).
```

This uses linearity and fresh-block independence, not CUSUM.

**Corollary D — local stability witness.** For any detector satisfying the
preceding assumptions and having a centered fixed point, a detector-specific
witness `Gamma>2` implies `F_1'(0)<-1` and

```text
rho_c=1/|F_1'(0)| in (0,1).
```

No claim is made that `Gamma>2` holds for every detector.

## 14. Claims that remain detector-specific

The following parts do not generalize merely from the score theorem:

- the value or sign of `Gamma`;
- the witness `Gamma>2`;
- the CUSUM reachable state geometry and affine Bellman reduction;
- the continuum contraction, residual, and resolvent certificate;
- reflection symmetry and the uncentered zero fixed point;
- verification of an exponential stopping tail for a proposed detector; and
- any claimed stability threshold until that detector has its own witness.

For the current two-sided CUSUM, a simple uniform one-step escape event already
gives a geometric tail: from every live state, `Z>=h+k` forces an up alarm and
`Z<=-(h+k)` forces a down alarm. Thus the regularity needed by the Gaussian
theorem is secure here, independently of more elaborate regeneration prose.

## 15. Level-4 route verdict

**LEVEL-4 ROUTE GREEN.**

The general theoretical spine is real: stopped-score differentiation requires
standard likelihood and stopping-time regularity, not a CUSUM recursion. The
detector-specific burden moves to three transparent checks:

1. the stopping rule is the same path functional throughout the parameter
   family and has adequate integrability;
2. symmetry or explicit centering supplies the fixed point to be studied; and
3. a separate analytic or certified numerical witness establishes the needed
   covariance magnitude.

This is a substantive detector-independent theorem, while preserving honest
detector dependence of the instability witness.

## 16. Recommendation for second-detector feasibility gate

**GO.** A second-detector gate is worthwhile now that the numerical discrepancy
is resolved and the theorem is detector-independent. That gate should begin by
checking its stopping-rule parameterization, tail regularity, and centering;
only then should it construct a detector-specific `Gamma` witness. It should
not reuse the historical floor projection or treat a finite approximation as
proof. No Shiryaev-Roberts or other detector has been implemented here.

## Reproducibility and final audit

Pinned environment:

```text
CPython 3.14.5
numpy 2.5.2
scipy 1.18.0
python-flint 0.9.0
FLINT 3.6.0
pytest 9.1.1
```

Commands:

```text
make test
.venv/bin/python scripts/run_phase4_pregate_diagnostics.py --samples 1000000
make pregate-audit
make audit
```

The test suite contains 44 passing tests. The independent pre-gate audit and
the protected full continuum replay returned `PASS`. The historical finite
solver is unchanged, the corrected
solver is a separate diagnostic module, and no proof-critical quantity has
been replaced by ordinary floating-point arithmetic.

Γ DISCREPANCY:
RESOLVED

ROOT CAUSE:
Finite discretization bias from the historical solver's componentwise floor projection of off-grid next states, which greatly inflates finite-chain persistence.

CORRECT Γ POINT ESTIMATE:
15.8868236 (non-rigorous refined-Bellman extrapolation; consistent with Monte Carlo and the continuum candidate)

CERTIFIED CONTINUUM THEOREM AFFECTED:
NO

LEVEL-3 THEOREM STATUS:
UNCHANGED

CUSUM USED IN SCORE IDENTITY:
NOT ESSENTIAL

GAUSSIAN ARBITRARY-STOPPING-TIME IDENTITY:
PROVED

EXPONENTIAL-FAMILY GENERALIZATION:
PROVED

STRONGEST GENERAL THEOREM:
For any parameter-invariant stopping time with a differentiable, uniformly integrable stopped likelihood, the derivative of a stopped expectation is its explicit derivative plus covariance with the stopped path score; the Gaussian 1-Gamma formula and mixed-reuse scaling are corollaries.

LEVEL-4 ROUTE:
GREEN

SECOND DETECTOR GATE:
GO

TOP 3 FINDINGS:
1. The value 18.7401 solves a severely over-persistent floor-projected finite chain (ARL 2099.5), not the continuum CUSUM (ARL about 465).
2. The corrected point estimate is about 15.8868, while the certified continuum enclosure and all Level-3 implications remain unchanged.
3. CUSUM is not used in stopped-score differentiation; it is used only for regularity, symmetry/centering, and the detector-specific Gamma>2 witness.
