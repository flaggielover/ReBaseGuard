# P5X R4 — the xi reformulation: derivation, invariance, kernel, conditioning

---

## 1. The transformation, derived rather than assumed

Set `xi = exp(y)` on each chart. From the **frozen** update
`y' = log(1 + exp(v))`, `v = y + z - 1/2` (plus chart):

```text
xi' = exp(y') = exp( log(1 + exp(v)) ) = 1 + exp(v) = 1 + exp(y + z - 1/2)
    = 1 + xi * exp(z - 1/2) .
```

Minus chart, with `v^- = y^- - z - 1/2`:

```text
xi^{-}' = 1 + xi^{-} * exp(-z - 1/2) .
```

**Verified numerically to full precision** (`results/r4_gate.json`, self-test
`S1`): `exp(softplus(v))` and `1 + xi e^{z-1/2}` agree as balls at
`(y,z) = (0.7, 1.3), (0, -2.5), (6.2, 0.4)`.

*Identification.* `xi = 1 + R` where `R` is the classical Shiryaev-Roberts
statistic: `R' = xi' - 1 = xi e^{z-1/2} = (1+R) Lambda`, `Lambda = e^{z-1/2}` the
likelihood ratio. The frozen log-domain code is exactly the classical SR
recursion, and `xi` is its natural coordinate.

## 2. Transformed domain — exact

`exp` is a strictly increasing bijection `[0, log(1+A)] -> [1, 1+A]`, so

```text
y in [0, log(1+A)]   <=>   xi in [1, 1+A] ,     1+A = 521.88613360274905517...
```

is **exact**, with the corrected `D1` endpoint carried through. Reset `y = 0`
maps to `xi = 1`; the domain's right endpoint `y = log(1+A)` maps to `xi = 1+A`.

## 3. Transformed alarm — exact

```text
alarm  <=>  v >= log A  <=>  e^v >= A  <=>  xi e^{z-1/2} >= A  <=>  xi' - 1 >= A  <=>  xi' >= 1+A .
```

Every step is an equivalence (`exp` strictly increasing). So in `xi`-space the
alarm is exactly "the updated state reaches the right endpoint of the domain".
Checked numerically on both sides of the boundary (self-test `S2`).

## 4. Transformed live region — exact, closed form

```text
live  <=>  xi^{+} e^{z-1/2} < A  and  xi^{-} e^{-z-1/2} < A
      <=>  z <  1/2 + log A - log xi^{+}  =  c_SR - log xi^{+}
      and  z >  log xi^{-} - c_SR
      <=>  z in ( l(xi), u(xi) ) ,   l = log xi^{-} - c_SR ,  u = c_SR - log xi^{+} .
```

Identical to the frozen `(y^- - c_SR, c_SR - y^+)` under `y = log xi`. The limits
are **affine in `log xi`**, not in `xi` — recorded, because it is the reason the
residual is not a polynomial in a single variable.

## 5. Reset / atom analysis — load-bearing

`xi' = 1 + xi e^{z-1/2} > 1` **strictly** for every finite `z`, and `xi' -> 1`
only as `z -> -infinity`. So:

* the transition kernel has **no atom at `xi = 1`**, and none anywhere: it is
  absolutely continuous, exactly as the `y`-space kernel is (`softplus(v) > 0`
  strictly, `-> 0` only as `v -> -infinity`);
* `xi = 1` is attained only by the **initial condition** `y_0 = 0`, which is a
  deterministic start, not a kernel atom — the same object in both coordinates;
* the transformation therefore **neither creates nor destroys an atom**.

This contrasts with CUSUM, whose `max(0, .)` does create a reset atom. The audit
is recorded because silently converting a mixed kernel into a pure density would
be a scientific error; here there is nothing mixed to convert.

## 6. The xi-space kernel

**As used for certification** (integration in `z`, the frozen variable):

```text
(K_e f)(xi) = int_{l(xi)}^{u(xi)} f( 1 + xi^{+} e^{z-1/2} , 1 + xi^{-} e^{-z-1/2} ) phi(z+e) dz .
```

**As a density in `xi'`** (recorded for completeness; the certification never
needs it, which is why the singularity below is harmless). Solving
`xi' = 1 + xi e^{z-1/2}`:

```text
z = 1/2 + log(xi' - 1) - log xi ,        dz/dxi' = 1/(xi' - 1) ,
p(xi' | xi) = phi( 1/2 + log(xi'-1) - log xi + e ) / (xi' - 1) ,
```

a **lognormal** density in `xi' - 1`. The `1/(xi'-1)` factor is integrable: as
`xi' -> 1^+`, `log(xi'-1) -> -infinity` and `phi` decays like
`exp(-(log(xi'-1))^2/2)`, which beats `1/(xi'-1)`; the density tends to `0`. The
certified route integrates in `z` and never touches this singularity.

## 7. The closed form that eliminates the panels

Let `f` be a polynomial of bidegree `(n,n)` in `(xi^+, xi^-)`,
`f = sum_{i,j} c_{ij} (xi^+)^i (xi^-)^j`. Writing `E = e^{z-1/2}`,

```text
f( 1 + xi^{+}E , 1 + xi^{-}/E )
  = sum_{i,j} c_{ij} sum_{a<=i} C(i,a) (xi^{+})^a E^a  sum_{b<=j} C(j,b) (xi^{-})^b E^{-b}
  = sum_{k=-n}^{n}  G_k(xi) * E^{k} ,
G_k(xi) = sum_{a-b=k} [ sum_{i>=a, j>=b} c_{ij} C(i,a) C(j,b) ] (xi^{+})^a (xi^{-})^b .
```

so the `z`-dependence is a **finite sum of pure exponentials** `E^k = e^{k(z-1/2)}`
with integer `k in [-n, n]`. And every such integral is closed form:

```text
int_{l}^{u} e^{kz} phi(z+e) dz  =  e^{k^2/2 - k e} [ Phi(u+e-k) - Phi(l+e-k) ] ,
```

by completing the square (`e^{k zeta} phi(zeta) = e^{k^2/2} phi(zeta-k)`, `zeta = z+e`).
Hence

```text
(K_e f)(xi) = sum_{k=-n}^{n} G_k(xi) e^{-k/2} e^{k^2/2 - k e}
              [ Phi(u(xi)+e-k) - Phi(l(xi)+e-k) ] .
```

**`2(2n+1)` special-function evaluations per state, no `z`-panels, no softplus
approximation.** Verified against a 40,000-point Simpson quadrature at
`n = 3`, `xi = (3.5, 2.25)`, `e = 1/4`: relative gap `4.30e-18`, using `14` `Phi`
evaluations and `0` panels.

## 8. First-moment integral table

| integral | exact form? | special function | certification route |
|---|---|---|---|
| `int_l^u e^{kz} phi(z+e) dz` | **yes** | `Phi` (Arb `erf`) | direct ball evaluation |
| `(K_e f)(xi)`, `f` polynomial in `xi` | **yes** | `2(2n+1)` `Phi` | §7 sum |
| `rho_{1,e} = phi(u+e) - phi(l+e) - e(1 - Phi(u+e) + Phi(l+e))` | **yes** | `phi`, `Phi` | unchanged from `P5X-T1` |
| `h_1 = 1 - K_e 1` | **yes** | `2` `Phi` (`k = 0` only) | §7 with `f = 1` |
| `h_j = K_e h_{j-1}` | **yes** | as §7 | `h_{j-1}` is polynomial in `xi` after one step only if kept polynomial; otherwise re-expanded per patch |
| `S_j = K_{z,e} h_j` | **yes** | see §9 | `z`-weighted variant |

## 9. Second-moment / weighted integrals

The `z`- and `z^2`-weighted kernels need
`int_l^u z^p e^{kz} phi(z+e) dz` for `p = 1, 2`. These are obtained from the
`p = 0` case by differentiating in `k`, which stays closed form:

```text
d/dk [ e^{k^2/2 - ke}(Phi(u+e-k) - Phi(l+e-k)) ]
  = (k - e) * (that)  -  e^{k^2/2-ke} [ phi(u+e-k) - phi(l+e-k) ] ,
```

giving `int z e^{kz} phi(z+e) dz` exactly, and a second differentiation gives the
`z^2` case. So **every operator P5X needs — `K_e`, `K_{z,e}`, `K_{z2,e}` — is
closed form in `xi`-space**, using only `phi` and `Phi`.

`XI_SECOND_MOMENT_EXTENSION = DIRECT_WITH_SPECIAL_FUNCTIONS`.

## 10. Drift dependence

`e` enters in exactly two places, both benign:

* a **Gaussian shift** inside `Phi(u+e-k)` and `Phi(l+e-k)`;
* a **multiplicative exponential factor** `e^{-ke}` (from `e^{k^2/2 - ke}`).

It does **not** enter `l`, `u`, `q_xi` or `G_k`. So `e` can remain an **exact
rational** throughout the symbolic layer, and no interval-valued `e` is needed —
the same discipline R-A′ Device 2 established for CUSUM.

## 11. Conditioning audit

| site | finding |
|---|---|
| `xi` near `1` | `G_k` is a polynomial; no singularity. The `1/(xi'-1)` factor appears only in the density form of §6, which certification does not use |
| `xi` near `1+A` | `u(xi) = c_SR - log xi` approaches `c_SR - log(1+A) = 0.498082 > 0`, so the live interval stays non-degenerate |
| `log(xi'-1)`, small `xi'-1` | not evaluated on the certified path |
| large `A` | enters only through `c_SR` and the domain endpoint; `Phi` arguments stay in `[-c_SR-|e|, c_SR+|e|]` |
| Jacobian singularity | integrable (§6), and unused |
| Gaussian-tail cancellation | `Phi(u+e-k) - Phi(l+e-k)` can cancel when both are near `1`; mitigated by evaluating the difference through `erf` at 192+ bits, and the measured relative gap was `4.3e-18` |
| overflow | `e^{k^2/2}` reaches `e^{128} ~ 4e55` at `k = 16`; representable, and it multiplies a `Phi`-difference that is correspondingly tiny. Measured at `k = +-8`: relative gaps `1.0e-14` and `3.1e-14`, still far inside any budget |

## 12. Scientific-neutrality lemmas

| lemma | statement | status |
|---|---|---|
| `L-R4.1` | `y <-> xi = e^y` is a bijection on `[0, log(1+A)] <-> [1, 1+A]` | **PROVED** — `exp` is strictly increasing and continuous, with inverse `log`; endpoints computed in §2 |
| `L-R4.2` | pathwise recurrence correspondence is exact | **PROVED** — §1, an algebraic identity valid for every `(y, z)`; verified numerically |
| `L-R4.3` | alarm decisions are identical pathwise | **PROVED** — §3, a chain of equivalences; verified on both sides of the boundary |
| `L-R4.4` | stopping times are identical | **PROVED** — `tau` is the first index at which the alarm predicate holds, and `L-R4.3` makes the predicate identical at every index on every path; the innovation sequence is untouched |
| `L-R4.5` | convention-A rewards are identical | **PROVED** — `w = min(m, tau)` depends only on `tau` (`L-R4.4`), and `Rbar` is a function of the `raw_t`, which the coordinate change does not touch |
| `L-R4.6` | the first-moment target is invariant | **PROVED** — `R_{SR,m}(e) = e + E_e[A_m]` is an expectation of a functional of `(raw_t, tau)`, both invariant by `L-R4.4`/`L-R4.5` |
| `L-R4.7` | the second-moment target is invariant | **PROVED** — same argument applied to `E_e[Rbar^2]` |
| `L-R4.8` | the transformed kernel, including any reset atom, is exact | **PROVED** — §5: there is no atom in either coordinate; the kernel is absolutely continuous and §7 gives it exactly |
| `L-R4.9` | no empirical monotonicity is required | **PROVED** — the only monotonicity used is that `exp` and `log` are increasing |
| `L-R4.10` | the theorem consumer interface is unchanged | **PROVED** — R4 changes only how `R_{SR,m}`, `S_{SR,m}` are computed; `R_max`, `s_min`, `M_2` and `X1`-`X6` are untouched |

**Classification: `CERTIFIED_COORDINATE_CHANGE`** (with the closed-form kernel of
§7 a `CERTIFIED_KERNEL_REFACTOR` on top). Neither is a
`SCIENTIFIC_METHOD_CHANGE` nor a `SCIENTIFIC_SCOPE_CHANGE`, so R4 proceeds.

## 13. Cost model: does R4 remove the ~128 z-panels?

| term | R3 (measured) | R4 (structural) |
|---|---|---|
| state patches | `1210` | `1210` (unchanged) |
| `z`-panels per patch | **`128`** | **`0`** |
| per-panel work | softplus `arb_series` + degree-96 composition + 97 centred moments, `3.911 ms` | — |
| per-patch work | `128 x 3.911 ms = 500 ms` | `2(2n+1) = 66` `Phi` + `(n+1)^2 = 289` monomials + `289` multiply-adds |
| softplus approximations | `2` per panel = `256` per patch | **`0`** |
| binomial re-expansion | — | candidate-only, precomputed **once**, reused for every patch and every `e` |

The panel dimension is removed **exactly**, not reduced. Whether the remaining
per-patch cost is small enough is what the gate measures; the model refuses to
claim a speedup from the panel count alone.

---

## 14. The production variable: `zeta = (xi - 1)/A`

The `xi` domain `[1, 1+A]` has dynamic range `521`, so a degree-16 power-basis
polynomial in `xi` would have coefficients spanning `521^16 ~ 1e43` — the
conditioning risk flagged in §11. The fix is an affine rescaling, chosen **before
the gate is run**, not after seeing a conditioning failure:

```text
zeta = (xi - 1)/A  in  [0, 1] .
```

`zeta` is exactly `R/A`, the classical SR statistic normalised by its threshold.
Under this change:

| object | form |
|---|---|
| domain | `zeta in [0,1]`, **exactly** (endpoints `y=0 -> zeta=0`, `y=log(1+A) -> zeta=1`) |
| recurrence | `zeta' = (1/A + zeta) E`, `E = e^{z-1/2}` (plus chart); `zeta'^- = (1/A + zeta^-)/E` |
| alarm | `zeta' >= 1`, **exactly** |
| live region | `z in (l, u)`, `u = 1/2 - log(1/A + zeta^+)`, `l = log(1/A + zeta^-) - 1/2` |
| reset | `zeta_0 = 0` |

*Check of the live region against §4:* `1/A + zeta = xi/A`, so
`u = 1/2 - log xi + log A = c_SR - log xi`. Identical.

**The key structural gain.** The map is affine in `zeta` and *multiplicative* in
`E`, so for `f = sum_{i,j} c_{ij} (zeta^+)^i (zeta^-)^j` of bidegree `(n,n)`:

```text
f( (1/A+zeta^+)E , (1/A+zeta^-)/E )
   = sum_{i,j} c_{ij} (1/A+zeta^+)^i (1/A+zeta^-)^j E^{i-j}
   = sum_{k=-n}^{n} G_k(zeta) E^k ,
G_k(zeta) = sum_{i-j=k} c_{ij} (1/A+zeta^+)^i (1/A+zeta^-)^j .
```

**No binomial expansion at all** — the `E`-exponents are simply `k = i - j`.
Combining with §7:

```text
(K_e f)(zeta) = sum_{k=-n}^{n} G_k(zeta) e^{-k/2} e^{k^2/2 - k e}
                [ Phi(u+e-k) - Phi(l+e-k) ] .
```

Per state patch, at production degree `n = 16`:

| work item | count |
|---|---|
| powers `(1/A+zeta^{+/-})^i`, `i <= 16` | `2 x 16 = 32` ball multiplications |
| products `c_{ij} P_i Q_j` accumulated into `G_k` | `(n+1)^2 = 289` |
| `Phi` evaluations | `2(2n+1) = 66` |
| `exp` factors `e^{k^2/2-ke-k/2}` | `33` (drift-dependent, patch-independent) |
| **`z`-panels** | **`0`** |
| **softplus approximations** | **`0`** |

This is the exact same certified object as R3's target, computed without any
discretisation of `z`. `zeta` is the frozen production variable for R4.
