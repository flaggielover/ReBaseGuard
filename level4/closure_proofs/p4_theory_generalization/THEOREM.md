# Priority-4 theorem: general location-family truncated-window derivative

Priority 4 asks which part of the closed Gaussian mechanism is Gaussian.  The
answer is one line of the proof.  Everything else survives, and this file
states exactly what "everything else" is.

## 0. Relation to the already closed results

Two things are already closed and are **not** re-proved here.

* **P1/P2** proved, for the frozen *Gaussian* CUSUM and Gaussian SR, the
  truncated-window identity `F'_{rho,m}(0) = rho(1 - E_0[A_m T_tau])` with the
  exact window `w = min(m, tau)`, for every `m >= 1`.
* **Track 3 / Track 3A-3B** proved, for a general regular location family, the
  stopped-score identity `d/de E_e[H_tau]|_0 = E_0[H_tau S_tau]` and applied it
  to the **single** terminal observation `H_tau = Z_tau`, i.e. to `m = 1` only.

Neither result implies the other's scope.  Priority 4's theorem is the
intersection that neither campaign covered: **a general location family and a
general truncated window `m >= 1` and a general stopping rule, in one
statement, together with an explicit account of which hypotheses are needed and
which failure modes are real.**

## 0.1 Which generality level is actually reached

Three levels of generality were attempted.  This is what each one delivers, and
where each one is used.

**Level A — symmetric differentiable location family.**  Delivers everything
below *plus* the fixed point at the origin (G4), and is therefore the level at
which the Priority-3 stability map applies unchanged.  Symmetry buys exactly
one thing and nothing else.

**Level B — general differentiable location family, score formulation.**  This
is the campaign's main result: G1, G1', G2 and G3 hold with no symmetry
assumption at all.  The score `psi = -f'/f` is what replaces the Gaussian
`T_tau`, and the two integration-by-parts identities `E[psi] = 0`,
`E[eps psi(eps)] = 1` are what make Corollary G2 family free.  This level is
where the campaign's numerical correspondence, its failure modes, and its
discharge lemmas live.

**Level C — general dominated parametric family.**  The interchange argument
of `PROOF.md` §2 never uses the location structure: it needs only a family
`L_tau(e)` of stopped likelihood ratios with `L_tau(0) = 1`, a derivative at
zero, and a Lipschitz bound.  Level C is therefore *reached*, and it is what
the Lean bridge `hasDerivAt_stoppedMean` and the finite-support Arb witness
formalize and instantiate.

But Level C is deliberately **not** promoted to the headline statement, for two
reasons.  First, at Level C the object `S_tau` is an abstract score with no
`-f'/f` interpretation, so Corollary G2 disappears — there is no integration by
parts and no reason for a non-selective rule to be neutral.  Second, the
concrete discharge lemmas L1-L5 are statements about a location family and a
detector; without them Level C is a theorem whose hypotheses nobody can check.
Level C is the right level for the *formal spine* and the wrong level for the
*scientific claim*.

## 1. Model

Fix a base density `f` on `R`.  One monitoring cycle observes

```text
X_t = mu + eps_t,      eps_t iid with density f,      t = 1, 2, ...
```

against a reference `R` fixed at the start of the cycle.  The reference error
and the residual are

```text
e   = R - mu,
Z_t = X_t - R = eps_t - e,
```

so under `Q_e` the residual coordinates are iid with density

```text
f_e(z) = f(z + e).
```

This is the frozen residual convention of the closed core.  The **parameter
score** for it and the **conventional location score** are

```text
s(z)   = d/de log f(z + e)|_{e=0} = f'(z)/f(z),
psi(z) = -f'(z)/f(z) = -s(z).
```

`tau` is the alarm time of a fixed detector, `F_n = sigma(Z_1,...,Z_n)`, and

```text
w   = min(m, tau),
A_m = (1/w) sum_{r=0}^{w-1} Z_{tau-r},
T_tau = sum_{t=1}^{tau} Z_t,
S_tau^psi = sum_{t=1}^{tau} psi(Z_t).
```

The alarm-causing increment is included, the denominator is the *random* `w`,
and the next reference mixes the reused block with an independent fresh
reference `U`:

```text
e_{j+1} = rho (e + A_m) + (1 - rho)(U - mu),
F_{rho,m}(e) = E_e[e_{j+1}] = rho (e + g_m(e)),   g_m(e) := E_e[A_m].
```

## 2. Hypotheses

**(A1) Parameter-free path functional.**  For every `n`, `{tau = n} ∈ F_n`, and
on `{tau = n}` both `A_m` and `T_tau` are Borel functions of `(Z_1,...,Z_n)`.
The detector recursion, threshold, inclusivity and tie rule are expressed in
residual coordinates and do not depend on `e`.

**(A2) Almost sure finiteness.**  `tau < infinity` `Q_e`-a.s. for `|e| <= d0`.

**(A3) Local common support and absolute continuity.**  `f > 0` Lebesgue-a.e.
on a set invariant under translation by `|e| <= d0`, and `f` is locally
absolutely continuous, so `f'` exists a.e. and `psi = -f'/f` is defined a.e.

**(A4) Differentiability of the stopped likelihood at zero.**  With

```text
L_tau(e) = prod_{t=1}^{tau} f(Z_t + e) / f(Z_t),
```

for `Q_0`-a.e. `omega` the map `e -> L_tau(e)(omega)` is differentiable **at
`e = 0`** with

```text
d/de L_tau(e)|_{e=0} = -S_tau^psi.
```

**(A5) Integrability.**  `A_m ∈ L^1(Q_0)` and `A_m S_tau^psi ∈ L^1(Q_0)`.

**(A6) Locally Lipschitz stopped likelihood with integrable constant.**  There
are `d ∈ (0, d0]` and `G ∈ L^1(Q_0)` with, `Q_0`-a.s.,

```text
|A_m| * |L_tau(e) - L_tau(e')| <= G * |e - e'|   for all e, e' ∈ [-d, d].
```

**(A7) Fresh reference.**  `U` is independent of the stopped cycle with
`E[U] = mu` for every `e` in the neighbourhood, and enters affinely with
coefficient `1 - rho`.  If `U` is formed as a sample mean of fresh
observations, this forces `E[eps] = 0`: the location parametrisation must be
aligned with what the fresh estimator targets, and a family with a nonzero
innovation mean would need either a recentring or a different fresh estimator.
All families used in this campaign are centred, and `E|eps| < infinity` is
therefore already required by the *definition* of the map, before any
derivative is taken.

> **(A6) is deliberately weaker than the hypothesis used by P1 and P2.**  Those
> campaigns assume an integrable dominator for the pointwise `e`-derivative of
> the integrand, which presupposes that `e -> L_tau(e)` is differentiable at
> *every* `e` in a neighbourhood, almost surely.  That hypothesis is false for
> the Laplace family: `e -> log f(z + e)` fails to be differentiable exactly at
> `e = -z`, and although each single `e` is a null event, the union over a
> neighbourhood is everything.  (A6) asks only for a Lipschitz difference
> quotient, which Laplace satisfies, and it still yields the same conclusion.
> See `ASSUMPTION_AUDIT.md`.

## 3. Theorem G1 (general truncated-window derivative)

Assume (A1)-(A7).  Then `g_m` is differentiable at `0`,

```text
g_m'(0) = -Gamma_{D,m,f},     Gamma_{D,m,f} := E_0[A_m S_tau^psi],   (G1a)
```

and `F_{rho,m}` is differentiable at `0` with

```text
F'_{rho,m}(0) = rho (1 - Gamma_{D,m,f}).                             (G1b)
```

`D` denotes the detector, `m` the window length, `f` the innovation density.

**Gaussian reduction.**  For `f = phi` we have `psi(z) = z`, hence
`S_tau^psi = T_tau` and `Gamma_{D,m,phi} = E_0[A_m T_tau]`, which is exactly
the closed P1 and P2 identity.  The reduction is an equality of estimands, not
a re-derivation of their Monte Carlo values.

## 4. Theorem G1' (at a general base point)

For `e0 ∈ (-d0, d0)`, if (A1)-(A7) hold with `Q_0` replaced by `Q_{e0}` and the
score evaluated at the *unshifted* innovations `eps_t = Z_t + e0`, then

```text
F'_{rho,m}(e0) = rho (1 - Gamma_{D,m,f}(e0)),
Gamma_{D,m,f}(e0) = E_{e0}[A_m sum_{t=1}^{tau} psi(eps_t)].
```

G1 is the case `e0 = 0`.  G1' is what an asymmetric family needs, because for
an asymmetric family `0` is not a fixed point (Section 7).

## 5. Corollary G2 (a non-selective stopping rule is exactly neutral)

Two statements, one elementary and one via the theorem.  Their agreement is the
point.

**(a) The map collapses.**  If `tau ≡ n` is **deterministic** and
`E|eps| < infinity` with `E[eps] = 0`, then for every `m >= 1` and every `e` in
the neighbourhood

```text
g_m(e) = E_e[A_m] = E_e[Z] = E[eps] - e = -e,
F_{rho,m}(e) = rho(e + g_m(e)) = 0.
```

The conditional-mean reuse map is **identically zero**: no selection, no
feedback, one-step collapse to the origin, for every regular location family,
symmetric or not.

**(b) The score formula agrees.**  Assume `f` is absolutely continuous with
`E|eps psi(eps)| < infinity` and `z f(z) -> 0` as `|z| -> infinity`.  Then
integration by parts gives the two family-free identities

```text
E[psi(eps)] = -integral f'(z) dz = 0,
E[eps psi(eps)] = -integral z f'(z) dz = integral f(z) dz = 1,
```

and hence, for every `m >= 1` and every such `f`,

```text
Gamma_{det(n),m,f} = 1   exactly,    F'_{rho,m}(0) = rho(1 - 1) = 0.
```

Note that the constant `1` in `E[eps psi(eps)] = 1` is an integration-by-parts
constant, not a variance.  In the Gaussian case `psi(z) = z` makes it look like
`E[eps^2] = 1`, which is a coincidence of the model's normalisation.

**Consequence.**  `Gamma - 1` is exactly the stopping-selection effect.  The
reuse window, the random denominator and the innovation law contribute nothing
to the multiplier on their own; every bit of the feedback comes from the
stopping rule's selection of *which* residuals get reused.  This is invisible
from the Gaussian core, where `E_0[A_m T_tau]` mixes the selection effect with
the Gaussian second-moment normalisation.

Statement (b) is also the campaign's strongest implementation control: it is a
cell of the numerical grid whose answer is known in advance, for every family
and every `m`, and any sign, normalisation or window error would break it.

## 6. Theorem G3 (random denominator: identity generalises, sign does not)

Put `B_m = (1/m) sum_{r=0}^{w-1} Z_{tau-r}`.  Pathwise, on `{tau >= 1}`,

```text
A_m S_tau^psi = B_m S_tau^psi + 1{tau < m} (1/tau - 1/m) T_tau S_tau^psi.  (G3a)
```

so, when the terms are integrable,

```text
Gamma_{D,m,f} = E_0[B_m S_tau^psi] + E_0[Q_{m,f}],
Q_{m,f} := 1{tau < m} (1/tau - 1/m) T_tau S_tau^psi.                       (G3b)
```

**The identity (G3a) is fully general.**  The nonnegativity `Q_m >= 0` proved
in P1 is **not**.  Since `1/tau - 1/m > 0` on `{tau < m}`, the sign of
`Q_{m,f}` is the sign of `T_tau S_tau^psi`, and

```text
Q_{m,f} >= 0 pathwise for all paths  <=>  T_tau S_tau^psi >= 0 for all paths.
```

For `psi(z) = z` this is `T_tau^2 >= 0` and holds automatically.  Thus the
centred Gaussian score is a sufficient structural reason for pathwise
nonnegativity.  Priority 4 does **not** claim the converse without additional
regularity and an all-path functional argument: the proof below establishes
Gaussian sufficiency and explicit non-Gaussian failure, not an iff
characterisation.  Concretely, for Laplace innovations (`psi = sign/b`) the
residual prefix

```text
Z = (5, -1, -1, -1),   tau = 4 < m = 5
```

has `T_tau = 2 > 0` and `S_tau^psi = -2/b < 0`, hence
`Q_{5,Laplace} = (1/4 - 1/5)(2)(-2/b) = -1/(5b) < 0`, and every residual path
in a neighbourhood of it has the same strict sign.  Whether the *expectation*
`E_0[Q_{m,f}]` is negative for a given family and detector is a separate
question and is measured, not assumed (`NUMERICAL_CORRESPONDENCE.md`).

## 7. Theorem G4 (symmetry: needed for the fixed point, not for the derivative)

Assume additionally that `f` is even, that the detector is reflection
equivariant (`tau(-Z) = tau(Z)` and `A_m(-Z) = -A_m(Z)` pathwise), and that
`A_m ∈ L^1(Q_0)`.  Then `E_0[A_m] = 0`, so `F_{rho,m}(0) = 0` and `0` is a
fixed point; combined with G1 the P3 classification applies verbatim with
`Gamma_{D,m,f}` in place of the Gaussian gain:

```text
lambda_{D,m,f}(rho) = rho (1 - Gamma_{D,m,f}),
rho_c(D,m,f) = 1 / |1 - Gamma_{D,m,f}|   when Gamma != 1,
attracting for 0 <= rho < rho_c, first-order boundary at rho_c,
repelling for rho > rho_c.
```

**Symmetry is used only here.**  It is not used by G1, G1', G2 or G3, and it is
not needed for the exact `rho` scaling.  Corollary G2(a) sharpens this: under a
*non-selective* stopping rule the origin is a fixed point for an asymmetric
family too.  Asymmetry moves the fixed point only through the interaction of
the innovation law with the stopping rule's selection.  Conversely, for an asymmetric `f`,
`E_0[A_m] != 0` in general, `0` is **not** a fixed point, and the P3 stability
map has nothing to classify at `0`; the correct object is G1' evaluated at a
solution of `F_{rho,m}(e*) = e*`.  This is a real restriction of scope, not a
technicality: the measured `E_0[A_1]` for the standardised skew-normal family
is of order one, not of order the Monte Carlo error.

## 8. Sufficient conditions that discharge (A2), (A4), (A5), (A6)

**L1 (geometric stopping tail).**  Let `c_D` be a residual value that alarms in
one step from every live state: `c_D = h + k` for the two-sided CUSUM,
`c_D = 1/2 + log A` for the two-chart SR.  If

```text
p := inf_{|e| <= d0} Q_e(Z_1 >= c_D) > 0,
```

then `Q_e(tau > n) <= (1 - p)^n` for all `n` and all `|e| <= d0`.  `p > 0`
requires the innovation law to reach `c_D`, i.e. `f` must put mass above
`c_D + d0`; uniformity over the compact `e` neighbourhood then follows by
dominated convergence.  All six theorem-supported families have support `R` and
satisfy this.  A compactly supported innovation law with `a < c_D` would not,
and L1 would have to be replaced.  In particular `E[tau] < infinity`
and `E[e^{c tau}] < infinity` for `c < log(1/(1-p))`.

**L2 (window moment).**  Because `{tau >= n} ∈ F_{n-1}` is independent of
`Z_n`, for every `r >= 1`

```text
E[|A_m|^r] <= E[max_{t <= tau} |Z_t|^r]
           <= sum_{n>=1} E[1{tau >= n} |Z_n|^r]
            = E|Z|^r E[tau].
```

So a single innovation moment of order `r` plus `E[tau] < infinity` controls
the whole reuse window, for every `m`.

**L3 (bounded score).**  If `sup_z |psi(z)| <= M < infinity` then
`e -> log L_tau(e)` is `M tau`-Lipschitz on any interval, so

```text
|L_tau(e) - L_tau(e')| <= M tau exp(M d tau) |e - e'|   on [-d, d],
```

and (A6) holds with `G = M |A_m| tau exp(M d tau)`.  With L1, L2 and
`E|eps|^{1+eta} < infinity` for some `eta > 0`, Hölder with `q = (1+eta)/eta`
gives

```text
E[G] <= M (E|Z|^{1+eta} E[tau])^{1/(1+eta)} (E[(tau e^{M d tau})^q])^{1/q}
      < infinity   whenever  M d q < log(1/(1-p)),
```

so shrinking `d` discharges (A5) and (A6).  **Only a `1 + eta` moment is
required; finite variance is not.**

**L4 (light tails, at most linear score).**  If `|psi(z)| <= M0 + M1|z|` with
`M1 > 0` and `E[e^{a|eps|}] < infinity` for some `a > 0`, put

```text
W = sum_{t <= tau} (M0 + M1 d + M1 |Z_t|).
```

Then, pathwise on `[-d, d]`, `|log L_tau(e)| <= d W`,
`|d/de log L_tau(e)| <= W` and `|A_m| <= W / M1`, so `L_tau` is
`W e^{dW}`-Lipschitz and

```text
G := |A_m| W e^{dW} <= W^2 e^{dW} / M1 <= C_d e^{2dW} / M1,
C_d = sup_{x>=0} x^2 e^{-dx} = 4/(d^2 e^2).
```

Splitting on `{tau = n}` and applying Cauchy-Schwarz with L1's geometric tail,
`E[e^{2dW}]` is bounded by a geometric series with ratio
`((1-p) E[e^{4d(M0 + M1 d + M1|eps|)}])^{1/2}`, which tends to
`(1-p)^{1/2} < 1` as `d -> 0`.  Fixing such a `d` gives (A5) and (A6).
`PROOF.md` Section 8 carries out every step.

**L5 ((A4) pointwise).**  (A4) holds whenever `z -> log f(z)` is differentiable
at each of the finitely many residuals `Z_1,...,Z_tau`.  For a `C^1` positive
density this is every `z`.  For Laplace it is every `z != 0`, and
`Q_0(exists t <= tau : Z_t = 0) = 0`.

**Coverage.**  L3+L1+L2 discharge Student-`t` (any `nu > 1`, including the
infinite-variance `nu = 1.5`), logistic, Laplace and any bounded-score family
with a `1+eta` innovation moment.  L4+L1+L2 discharge Gaussian, Laplace,
logistic and the skew-normal.  P1 and P2 already discharged the Gaussian case
for the frozen CUSUM and SR by their own exponential-moment route; that closed
argument is used, not replaced.

## 9. Failure modes (proved, not conjectured)

**F1 -- moving support breaks (A3), and the identity is false.**  Let `eps` be
uniform on `[-a, a]` and let the detector be the memoryless rule
`tau = inf{t : |Z_t| >= c}` with `0 < c < a`.  The a.e. interior score is
identically zero, so the right-hand side of (G1a) is exactly `0`.  But an
elementary computation gives, for `|e| < a - c`,

```text
Q_e(|Z| >= c) = 1 - c/a   (constant in e),
g_1(e) = -e a / (a - c),
g_1'(0) = -a / (a - c) != 0.
```

With `a = 1, c = 1/2` the identity fails by exactly `2`.  The obstruction is
not domination or integrability: `Q_e` and `Q_0` are not mutually absolutely
continuous on any single coordinate, so the change of measure that (G1a) rests
on does not exist.

**F2 -- no first moment breaks the map itself.**  Let `eps` be standard Cauchy.
For the frozen CUSUM, `tau = 1` exactly on `{|Z_1| >= h + k}`, so

```text
E|A_1| >= E[|Z_1| 1{|Z_1| >= h + k}] = infinity.
```

`g_m(e)` is therefore undefined and (A5) fails.  The same first-moment failure
also breaks (A7): a fresh reference formed as a sample mean is not unbiased for
`mu`.  Note the trap: whether the *right-hand side* `E_0[A_m S_tau^psi]`
happens to converge is detector dependent.  Under the non-selective control
`tau = 1` it converges to exactly `1`, because `psi(z) = 2z/(1+z^2)` damps the
Cauchy tail; under the frozen CUSUM it does not.  A finite `Gamma` is therefore
not evidence that the theorem applies -- integrability of `A_m` has to be
checked separately.  The boundary is the **first** moment:
Student-`t` with `nu = 1.5` (infinite variance, finite mean) is inside the
theorem; `nu = 1` is outside it.

## 10. Scope

This is a conditional theorem for regular one-dimensional location families and
a fixed residual-path stopping rule.  It is **not** distribution free, not
detector universal, not valid for moving support, and not a global or nonlinear
stability result.  Every concrete detector must separately satisfy (A1), (A2)
and the discharge lemmas; Section 8 does this for the frozen two-sided CUSUM
and the frozen two-chart SR, and for no other detector.
