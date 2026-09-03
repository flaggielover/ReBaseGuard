# P5X B2 Basis Feasibility Audit — Stable-Basis Residual Certification

`PRE_FREEZE_CERTIFICATION_ARCHITECTURE_AUDIT`. Not R8, not a binding repair,
not a scientific method change. **No Checkpoint J was created and no binding
gate was run.**

```text
ANSWER  YES -- a stable-basis certification exists, at BASIS_ROUTE_STRONG,
        with the R6 fast kernel, the xi transform and the candidate untouched.
ARCHITECTURE  CASE 1 (MONOMIAL_FAST + BERNSTEIN_CERTIFIED)
              -- but only after rejecting the naive basis-image sub-route,
                 which is CASE 2 and was measured and discarded.
```

| | value |
|---|---|
| `max |monomial coefficient|` | `2.012154e+10` |
| `max |Bernstein coefficient|` | **`1.898676`** |
| **coefficient-scale improvement** | **`1.059767e+10`** |
| old direct residual enclosure | `6.736713e+04` |
| failed R7 centred residual | `1.211486e+06` |
| **new stable-basis enclosure (64x64)** | **`3.427093e-02`** |
| **new stable-basis enclosure (256x256)** | **`8.166205e-03`** |
| improvement over old direct | **`1.966e+06 x`** (64x64) |
| improvement over failed centred | **`3.535e+07 x`** (64x64) |
| per-cell runtime | `4.7 - 5.1 ms` (band `STRONG`) |
| `z_panels` / `softplus` on the certified path | `0` / `0` |

---

## 1. The candidate is reused exactly

The degree-16 candidate from the failed SR prototype is reused verbatim
(`solve_candidate_cheb` at `e = 1/4`, `cond = 4.050e5`, `max|c_ij| =
2.012154e10`). **No refit.** The only change is the representation used for
rigorous range certification.

## 2. Coefficient scale — the decisive first measurement

Exact tensor conversion `beta = M c M^T` with `M[k][i] = C(k,i)/C(n,i)`:

```text
max |c_ij|  = 2.012154e+10          max |beta_ij| = 1.898676
beta signed range = [-1.898676, -0.657779]      median |beta| = 1.2064
max radius of any beta = 2.5e-110   (conversion is numerically exact at 400 bits)
```

`max|beta| = O(||ghat||_inf)` with `max|ghat| = 1.85`, exactly the audit
expectation of §4. Equality with the monomial form verified at four random
points to 16 digits. **All `beta` are negative**, so by the convex-hull property
`ghat` is sign-definite on `[0,1]^2` — used in §5 below.

## 3. `ghat` range on the historical worst cell — the hull is SHARP

Restriction to `[1/64, 2/64]^2` by exact de Casteljau subdivision (`3.46 ms`):

| method | enclosure | width |
|---|---|---|
| A monomial interval | `[-1.844807, -1.826029]` | `1.8779e-02` |
| **B Bernstein hull** | `[-1.8390060, -1.8313223]` | **`7.6837e-03`** |
| C sampled 9x9 (diagnostic) | `[-1.8390060, -1.8313223]` | `7.6837e-03` |

**Overshoot `1.000x`** — the convex hull reproduces the true range exactly here.

## 4. The load-bearing question: certifying `K_e ghat`

### `B-B1` basis images — TESTED AND REJECTED (this is `CASE 2`)

`K_e ghat = sum_ij beta_ij K_e[B_i (x) B_j]` has no coefficient cancellation in
`beta`, but each `B_i^16` expanded into monomials carries coefficients up to
`2.0180e+06`, so each basis image is itself inflated:

```text
worst single |K_e[B_i (x) B_j]| radius   1.9479e+05
recombined K_e ghat enclosure radius     1.9324e+06     (value -1.835237)
```

Worse than the monomial route's `6.736713e4`. **`K_e` maps the Bernstein basis
back into a representation with the same catastrophic cancellation.** This
sub-route is discarded.

### `B-B2` positivity — works, but weak

`K_e` integrates against a non-negative measure and all `beta < 0`, so
`min(beta) S <= K_e ghat <= max(beta) S` with `S = K_e 1 = Phi(u+e) - Phi(l+e)`:

```text
width = (max beta - min beta) * S = 1.241073        residual enclosure 1.249120
                                                     BASIS_ROUTE_WEAK  (5.393e4 x)
```

### `B-B3` centred form with Bernstein-bounded derivatives — **this is the route**

```text
d(K_e ghat)/dzeta^+ = int ghat_x(q(zeta,z)) E(z) phi(z+e) dz
                      + ghat(q(zeta,u)) phi(u+e) * (-1/w^+) ,   E = e^{z-1/2}
```

`ghat_x` is bounded by the **Bernstein derivative hull**: the derivative of a
Bernstein form has coefficients `n(beta_{i+1,j} - beta_ij)`, all `O(1)` because
`beta` is `O(1)`. The weight integrals are closed form by the R6 machinery,
`int E phi = e^{-e}[Phi(u+e-1) - Phi(l+e-1)] = 0.778601` and
`int E^- phi = 1.282142`.

**Degree elevation** (§14 — exact, does not change the function, no refit)
sharpens the derivative hull dramatically:

| elevated degree | `Mx` | `My` | `K_e` width | residual enclosure |
|---|---|---|---|---|
| 16 | `10.2467` | `2.2712` | `1.7150e-01` | `1.795505e-01` |
| **32** | **`1.2046`** | **`0.5217`** | `2.6224e-02` | **`3.427093e-02`** |
| 64 | `1.1798` | `0.5200` | `2.5889e-02` | `3.393544e-02` |
| 128 | `1.1732` | `0.5198` | `2.5805e-02` | `3.385162e-02` |
| 256 | `1.1701` | `0.5197` | `2.5765e-02` | `3.381205e-02` |

True sampled maxima (diagnostic): `|ghat_x| = 1.1670`, `|ghat_y| = 0.5196`. At
elevated degree 32 the hull is within `3%` of sharp and further elevation buys
nothing. **Elevation is candidate-global — computed once (`9 ms`), not per
cell.**

## 5. Enclosure and cost across resolutions

| grid | `ghat` hull | `K_e` width | **residual enclosure** | band | ms/cell | full-grid |
|---|---|---|---|---|---|---|
| 64x64 | `7.68e-03` | `2.62e-02` | **`3.427093e-02`** | `PROMISING` | `4.88` | `20.0 s` |
| 128x128 | `3.66e-03` | `1.27e-02` | `1.652181e-02` | `PROMISING` | `4.75` | `77.8 s` |
| **256x256** | `1.79e-03` | `6.32e-03` | **`8.166205e-03`** | **`STRONG`** | `5.13` | `336.1 s` |
| 512x512 | `8.82e-04` | `3.15e-03` | `4.071526e-03` | `STRONG` | `4.72` | `1236 s` |

The `<= 1e-2` target is met at `256x256` in `5.6` minutes. The mechanism is the
basis change (`1.97e6 x` at unchanged `64x64`); the `4x` refinement contributes
only the last factor `4.2` and is **not** the primary repair.

## 6. Audit lemmas

| | status |
|---|---|
| `A1` exact equality with `ghat` | **PASS** — exact linear conversion; verified at 4 points to 16 digits; `beta` radii `2.5e-110` |
| `A2` rigorous restriction to a cell | **PASS** — de Casteljau subdivision; measured overshoot `1.000x` |
| `A3` rigorous range bound of `ghat` on the cell | **PASS** — convex-hull property, sharp |
| `A4` rigorous bound of `K_e ghat` on the cell | **PASS** — via `B-B3`: positivity of `K_e`, Bernstein derivative hull, mean-value form. **NOT** via basis images |
| `A5` no scientific candidate change | **PASS** — same coefficients, no refit, same target, same `e = 1/4`, same worst cell |
| `A6` R6 kernel semantics unchanged | **PASS** — the R6 evaluator is used verbatim for the exact cell-centre value |
| `A7` `z`-panels zero | **PASS** — instrumented counter `0` |
| `A8` softplus approximations zero | **PASS** — instrumented counter `0` |
| `A9` no empirical monotonicity | **PASS** — only the Bernstein convex-hull theorem, non-negativity of the kernel measure, the mean-value theorem, and exact degree elevation |

## 7. Architecture classification

**`CASE 1`.** `MONOMIAL_FAST + BERNSTEIN_CERTIFIED` are compatible and solve the
range problem: the R6 monomial closed form supplies the exact cell-centre value
(`~1e-54` relative), and the Bernstein form supplies every rigorous range and
derivative bound. Both are proved representations of the same polynomial.

`CASE 2` was real and is what kills the *naive* reading of the Bernstein idea —
applying `K_e` to Bernstein basis images. That was measured (`1.93e6`) and
rejected. The working architecture never applies `K_e` to a basis image; it uses
Bernstein only to bound `ghat` and its derivatives, and lets `K_e` act through
positivity and the closed-form weight integrals.

## 8. Known implementation detail for the eventual gate

The `zeta^-` boundary term must use `w^- = 1/A + zeta^-`, not `w^+`. On the
diagonal probe cell used throughout this audit the two coincide, so the measured
numbers are unaffected; a general-cell implementation must carry both.

## 9. `B1` compatibility

The `B1` one-sided resolvent route is untouched and unaffected. It consumes only
`C_SR`, a scalar bound on `sup_x E_x[tau]`, and is independent of how the
residual is bounded. Nothing in this architecture changes the SR recurrence, the
stopping time, or the state domain that `B1` reasons about.
