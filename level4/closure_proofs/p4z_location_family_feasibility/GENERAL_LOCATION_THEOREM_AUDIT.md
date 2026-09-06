# P4Z Phase 2 — the general location-family target, from first principles

This document **does not change the theorem**.  It re-derives the frozen
statement under the frozen convention so that every mathematical object has a
named home in the implementation, and so that the one structural fact P4Z
exploits — the bounded-survival lemma — is visible as a consequence of the
frozen detectors rather than a new hypothesis.

Inherited unchanged from `p4_theory_generalization` at tree
`eede90383da44c250871b1bb97d12045c897c8d9`.

## 1. Model and convention

Fix a base density `f` on `R`.  One monitoring cycle observes
`X_t = mu + eps_t` with `eps_t` iid from `f`, against a reference `R` fixed at
the start of the cycle.  With

```text
e   = R - mu          reference error, the location parameter
Z_t = X_t - R = eps_t - e
```

the residual coordinates are iid under `Q_e` with density `f_e(z) = f(z+e)`.
The **parameter score** and the **conventional location score** are

```text
s(z)   = d/de log f(z+e)|_{e=0} = f'(z)/f(z)
psi(z) = -f'(z)/f(z) = -s(z)
```

This is the frozen residual convention; `configs/P4_PROTOCOL.json` records it
verbatim as `"Z_t = eps_t - e, f_e(z) = f(z+e), parameter score s = f'/f = -psi"`.

## 2. Objects

```text
tau        alarm time of a fixed detector, F_n = sigma(Z_1..Z_n)
w          = min(m, tau)                    the truncated window length
A_m        = (1/w) sum_{r=0}^{w-1} Z_{tau-r}   random denominator, alarm increment included
S_tau^psi  = sum_{t=1}^{tau} psi(Z_t)
g_m(e)     = E_e[A_m]
F_{rho,m}(e) = rho (e + g_m(e))
```

## 3. Regularity, quantifiers, and where each hypothesis is checked

| hypothesis | statement | who discharges it | implementation home |
|---|---|---|---|
| (A1) | parameter-free path functional; `{tau=n} ∈ F_n`; recursion in residual coordinates | frozen by construction | `detectors.py` |
| (A2) | `tau < inf` a.s. for `\|e\| <= d0` | L1 (geometric tail) | `Detector.forcing_increment` |
| (A3) | local common support, `f > 0` a.e. on a translation-invariant set, `f` locally absolutely continuous | family property | `Family.common_support` |
| (A4) | `e -> L_tau(e)` differentiable **at 0** with derivative `-S_tau^psi` | L5 | `Family.everywhere_differentiable_logdensity` |
| (A5) | `A_m ∈ L^1(Q_0)` and `A_m S_tau^psi ∈ L^1(Q_0)` | L2 + L3/L4 | `Family.finite_abs_moment_order` |
| (A6) | locally Lipschitz stopped likelihood with integrable constant | L3 (bounded score) or L4 (light tails) | `Family.score_bound` |
| (A7) | fresh reference independent, `E[U] = mu`, entering affinely; forces `E[eps] = 0` | family standardisation | `families.py`, each constructor |

Quantifiers, in full: for **every** `m >= 1`, for **every** base density `f`
satisfying (A3)–(A7), for the **fixed** detector `D` satisfying (A1)–(A2), at
the **single** point `e = 0` (G1) or at a base point `e0 ∈ (-d0, d0)` (G1').
Not distribution free, not detector universal, not global, not nonlinear.

## 4. The target

**Theorem G1a.**  `g_m` is differentiable at 0 and

```text
g_m'(0) = -Gamma_{D,m,f},      Gamma_{D,m,f} = E_0[ A_m S_tau^psi ]
```

**Theorem G1b.**  `F'_{rho,m}(0) = rho (1 - Gamma_{D,m,f})`.

`Gamma_{D,m,f}` is the estimand.  One real scalar per
`(layer, detector, family, m)`.  Nothing else is estimated.

**Interchange of derivative and stopped expectation** is exactly (A4)+(A6): the
stopped likelihood ratio `L_tau(e) = prod_{t<=tau} f(Z_t+e)/f(Z_t)` is
differentiable at zero a.s. with derivative `-S_tau^psi`, and
`|A_m| |L_tau(e) - L_tau(e')| <= G |e-e'|` with `G ∈ L^1`.  (A6) is
deliberately weaker than the dominated-pointwise-derivative hypothesis of P1
and P2, because that hypothesis is false for Laplace: `e -> log f(z+e)` fails
to be differentiable exactly at `e = -z`, and although each single `e` is null,
the union over a neighbourhood is everything.

**Symmetry** is used only by G4, to make `0` a fixed point.  G1, G1', G2 and G3
never use it.  For an asymmetric `f` the origin is not a fixed point and the
P3 stability map has nothing to classify there.

## 5. The bounded-survival lemma — a consequence, not a new hypothesis

This is the only mathematics P4Z adds, and it adds nothing to the theorem: it
is a property of the two frozen recursions, stated so that it can be used.

**Lemma.**  Let `(u, d)` be the pre-step charts and let `c_D` be the detector's
forcing increment, already defined by the frozen implementation and already
used by discharge lemma L1:

```text
CUSUM   c_D = h + k
SR      c_D = 1/2 + log A
```

Then the set of residuals that do **not** alarm at that step is an open
interval `I(u,d) = (L, U)` with `L < 0 < U` and `|L|, |U| <= c_D`:

```text
CUSUM   U = h + k - u,                    L = d - h - k
SR      U = log A + 1/2 - log(1 + e^u),   L = -(log A + 1/2 - log(1 + e^d))
```

*Proof.*  Both recursions are Markov in `(u,d)`, both alarm on `max(.) >=`
threshold tested after the update with an inclusive boundary, and both are
monotone in `z` on the up chart and anti-monotone on the down chart.  Solving
each chart's post-update value against its threshold gives the two endpoints
directly.  For CUSUM, `u >= 0` gives `U <= h+k` and `d >= 0` gives `|L| <= h+k`.
For SR, a live path has `u, d < log A`, and `log(1+e^u) >= log 2 > 0` gives
`U <= log A + 1/2`; symmetrically for `L`.  A live path also has `u < log A`,
so `U > 1/2 - log(1+e^{log A}) + log A > 0`. ∎

`tests/test_estimator_identity.py::test_alarm_bounds_agree_with_the_frozen_recursion_exactly`
checks the boundary convention against the frozen `Detector.step` path by path,
and `::test_survival_residuals_are_bounded_by_the_forcing_increment` checks the
bound.  Neither is a measurement.

**Corollary (the whole point).**  On `{tau = n}`, every residual
`Z_1, ..., Z_{n-1}` is bounded in absolute value by `c_D`.  The *only*
unbounded coordinate of `A_m` is the single alarm-causing increment `Z_tau`,
and the *only* unbounded coordinate of `S_tau^psi` — for a bounded-score family
— is `tau` itself, which has a geometric tail by L1.

This says exactly where the historical estimator's infinite variance comes
from, and exactly what has to be integrated out to remove it.

## 6. Corollary G2, and why it is the strongest available control

Under a deterministic `tau ≡ n` with `E[eps] = 0` and `E|eps| < inf`, the
conditional-mean map collapses: `g_m(e) = E_e[Z] = -e`, so `F_{rho,m} ≡ 0`.
Via the score, absolute continuity plus `z f(z) -> 0` gives the two family-free
integration-by-parts identities

```text
E[psi(eps)] = -int f'(z) dz = 0
E[eps psi(eps)] = -int z f'(z) dz = int f(z) dz = 1
```

so `Gamma_{det(n),m,f} = 1` **exactly**, for every `m` and every such `f`.
`Gamma - 1` is therefore exactly the stopping-selection effect.

The constant `1` in `E[eps psi(eps)] = 1` is an integration-by-parts constant,
not a variance; the Gaussian case makes it look like `E[eps^2] = 1` by an
accident of normalisation.

This is a grid cell whose answer is known in advance for every family and every
`m`, so any sign, normalisation or window error breaks it.  P4Z keeps it and
adds an exact algebraic form of it — see `CANDIDATE_ESTIMATORS.md` §2.4.

## 7. G3 and the random denominator

With `B_m = (1/m) sum_{r=0}^{w-1} Z_{tau-r}`, pathwise on `{tau >= 1}`,

```text
A_m S_tau^psi = B_m S_tau^psi + 1{tau < m}(1/tau - 1/m) T_tau S_tau^psi
```

The identity is fully general.  The nonnegativity of the correction proved in
P1 is **not**: its sign is the sign of `T_tau S_tau^psi`, which for the
centred Gaussian score is `T_tau^2 >= 0` and for Laplace can be strictly
negative — `Z = (5,-1,-1,-1)`, `tau = 4 < m = 5` gives `-1/(5b)`.  P4 claims
Gaussian sufficiency and explicit non-Gaussian failure, not an iff.

## 8. Proved failure modes

**F1, moving support.**  `eps ~ U[-a,a]`, memoryless rule `|Z| >= c` with
`0 < c < a`.  The a.e. interior score is identically zero, so the right-hand
side of G1a is exactly `0`, while `g_1'(0) = -a/(a-c) != 0`; at `a=1, c=1/2`
the identity fails by exactly `2`.  The obstruction is that `Q_e` and `Q_0` are
not mutually absolutely continuous on any single coordinate.

**F2, no first moment.**  Standard Cauchy under the frozen CUSUM:
`E|A_1| >= E[|Z_1| 1{|Z_1| >= h+k}] = infinity`, so `g_m(e)` is undefined and
(A5) fails.  A finite right-hand side is not evidence that the theorem applies:
under the non-selective control it converges to exactly `1` because
`psi(z) = 2z/(1+z^2)` damps the Cauchy tail.  The boundary is the **first**
moment: `t1p5` is inside, `nu = 1` is outside.

## 9. Object-to-artifact map

| object | frozen artifact |
|---|---|
| `f`, `psi`, `score_bound`, moment order, symmetry, support | `p4_theory_generalization/src/rebaseguard_p4_general/families.py` |
| detector recursions, thresholds `k=1/2`, `h=5`, `A=520.886133602749`, `c_D` | `.../detectors.py` |
| `tau`, `A_m` (`window_mean`), `B_m` (`fixed_window_mean`), `S_tau^psi` (`score_sum`), `T_tau` (`total`), G3 correction (`short_correction`) | `.../simulate.py` |
| `Gamma` Route A, Route B, Richardson, correspondence statistic | `.../estimators.py` |
| Route Q analytic identity | `.../quadrature.py` |
| grids, gates, seeds, FD steps | `.../configs/P4_PROTOCOL.json` |
| G1/G1'/G2/G3/G4, L1–L5, F1, F2 | `.../THEOREM.md`, `.../PROOF.md` |
| Level-C formal spine | `.../lean/GeneralLocationFamilyP4.lean` |
| three interval-certified objects | `.../certificates/certificate.json` |

## 10. What P4Z changes

Nothing above.  P4Z changes only *how* `Gamma_{D,m,f}` is computed, using §5.
