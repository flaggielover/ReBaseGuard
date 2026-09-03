# P5X R7 — pre-freeze sanity audit

`CERTIFIED_RESIDUAL_BOUND_REPAIR` + `CERTIFIED_RESOLVENT_BOUND_REPAIR`.
Not a scientific method change, not a scope change, not a detector change, not a
theorem change.

**No Checkpoint J was created and no binding gate was run.** The R7 brief §3
requires each proposed certification algorithm to demonstrate non-vacuous
scaling in a cheap, explicitly non-binding probe *before* freezing, and §7
forbids freezing a `B2` bound that stays above `1e2` on a point residual of
`~1e-5`. `B1` passed its probe. **`B2-b` failed its probe**, so it is not frozen,
and per §7 no alternate `B2` route is chosen here.

All numbers on this page are **PRE-FREEZE DIAGNOSTIC, NON-BINDING**.

---

## 1. `B1` — one-sided reduction: **PASSES** the sanity probe

### Domination (to be proved formally if frozen)

The minus chart evolves autonomously, `y^-_t = softplus(y^-_{t-1} - z_t - 1/2)`,
so on the *same* innovation sequence both stopping times are defined and

```text
tau   = inf{ t : max(v^+_t, v^-_t) >= log A }
tau^- = inf{ t : v^-_t >= log A }
```

Every `t` with `v^-_t >= log A` also has `max(v^+_t, v^-_t) >= log A`, so
`{tau^- <= t} subset {tau <= t}` for every `t`, giving `tau <= tau^-` pathwise
and hence `E_x[tau] <= E_{x^-}[tau^-]`. This is a stopping-time set inclusion
under a coupling on the same `z`, not an assumption.

### Probe result — non-vacuous, and stable in resolution

One-dimensional value iteration on `[0, b_SR]`, `q = max_P V_n`, stop at
`q <= 1/2`, `C <= n_0/(1-q)`:

| `e` | grid | `n_0` | `q` | `C_one-sided` |
|---|---|---|---|---|
| `0.25` | `512 x 512` | `105` | `0.497019` | **`208.8`** |
| `0.25` | `1024 x 1024` | `98` | `0.497810` | **`195.1`** |
| `0.24` | `512 x 512` | `112` | `0.497822` | `223.0` |
| `0.26` | `512 x 512` | `98` | `0.498397` | `195.4` |
| `0` | `512 x 512` | `783` | `0.499742` | **`1565.2`** |

* **Non-vacuous**: `q` leaves `1` immediately and decays monotonically, unlike
  the two-sided Phase-2 method which sat at exactly `1.0` for all `4000` sweeps.
* **Right physical scale**: `195-223` against the Monte-Carlo two-sided
  `E_{x_0}[tau] = 129.6`. A one-sided bound must exceed the two-sided value, and
  a factor `~1.6` is the expected size of that slack.
* **Resolution-stable**: `208.8 -> 195.1` on doubling the grid, a `7%` change —
  convergence, not a grid artifact.
* Well inside the brief's frozen limits `B1-Q4 <= 1000` (`e = 0.25`) and
  `B1-Q5 <= 3000` (`e = 0`).

**Why the one-sided reduction cures the adversarial defect.** In two dimensions
the image *box* always contained a safe cell, so `max`-over-box modelled an
opponent keeping the state away from the boundary forever. In one dimension the
image is an interval on a line the walk must cross, so the `max` cannot hide.

`B1` is ready to be frozen. It is not frozen here because the R7 gate is
conjunctive and `B2` has not passed.

## 2. `B2-b` — centred / mean-value residual: **FAILS** the sanity probe

### Probe result

Historical worst cell `[1/64, 2/64]^2`, `e = 1/4`, `192` bits:

| quantity | value |
|---|---|
| residual at the cell centre (exact point) | `2.399034e-05` |
| **true** variation of `r` over the cell (9x9 samples) | `1.242636e-05` |
| direct interval enclosure (Phase 2) | `6.736713e+04` |
| dependency factor | `5.421e+09` |
| gradient enclosure `d(K_e ghat)/dzeta^+`, midpoint | `-9.812551e-01` |
| gradient enclosure, **radius** | **`7.753508e+07`** |
| resulting mean-value bound | **`1.211486e+06`** |
| improvement over the direct enclosure | **`0.056x` — i.e. `18x` WORSE** |

`B2-Q3` wanted `<= 1e-2`. The probe is eight orders above it, and worse than the
bound it was meant to repair. **Not frozen.**

### Root cause, measured not assumed

Three candidate explanations were tested and two were eliminated.

**Eliminated — endpoint decoupling.** `w^+ = e^{1/2-u}` and `w^- = e^{l+1/2}`
exactly, so `G_k = sum_{i-j=k} c_ij e^{-iu+jl}`; combining with the R5 exponent
identity collapses every exponent to `-jD - (u+e)^2/2` with `D = u - l in
[0.996, 13.51]`. This `D`-form was implemented and verified to agree with the
direct path exactly at points. Its cell enclosure is `7.403457e+04` against the
direct `6.736712e+04` — **`0.91x`, no improvement**. Endpoint decoupling is not
the cause.

**Eliminated — cross-`k` cancellation.** Measured `max_k |G_k I_k| / |sum| =
5.76`. Mild, and far too small to explain `5.4e9`.

**Confirmed — coefficient cancellation in the monomial basis.** The candidate is
tame in value (`max |ghat| = 1.85` over `[0,1]^2`) but its monomial coefficients
reach `2.012e10`. That is *intrinsic*: a degree-`n` polynomial on `[0,1]` has
monomial coefficients growing like `~4^n`, and `4^16 ~ 4e9`. Interval evaluation
of `sum_{i,j} c_ij F_ij(zeta)` cannot cancel `289` signed terms of size `~1e10`
that sum to `~1`.

**Why the centred form does not rescue it.** Every derivative order carries the
*same* coefficients: `d/dzeta sum c_ij F_ij = sum c_ij F'_ij`. So the gradient
enclosure inherits the identical inflation — measured radius `7.75e7` against a
true gradient of `-0.98`, a factor `~8e7` — and multiplying by `h = 7.8e-3` does
not recover it. Taylor models of any order fail for the same reason.

### Classification

`BASIS_DEPENDENCY` (R7 brief §22).

This is a **basis-imposed conflict**, and it is worth stating sharply: R4's
panel-free closed form requires the candidate expanded in the **monomial basis
in `zeta`**, because the grouping by `k = i - j` is exactly what makes the
`z`-integral collapse to `2(2n+1)` special-function calls. That same basis is
the one whose range cannot be enclosed without catastrophic cancellation. The
property that bought the `1255x` panel-free speedup is the property that blocks
the certified range bound.

### Candidates for a future `B2` audit — none chosen here

1. **Bernstein-basis candidate.** Write `ghat = sum beta_ij B_i(zeta^+)B_j(zeta^-)`
   with `|beta| = O(max|ghat|)`. Then `K_e ghat = sum beta_ij K_e[B_i (x) B_j]`
   has no coefficient cancellation; the inflation would be confined to enclosing
   each fixed basis image `K_e[B_i (x) B_j]`, which is a separate and possibly
   easier problem. This is the most promising direction and is *not* the
   already-ruled-out grid refinement.
2. **Degree reduction.** Coefficients fall like `4^n`: degree 8 gives `~6e4`.
   But `rho_1` then fits only to `9.7e-4`, which bounds the achievable point
   residual from below.
3. **Exact-rational / much higher precision coefficient handling.** Attacks the
   symptom, not the `~1e9` structural inflation; likely insufficient alone.
4. **Subdivided candidate.** Breaks the closed form, since `K_e` evaluates
   `ghat` at the updated state, which can land in any piece — this reintroduces
   panels and is forbidden.

Grid refinement remains ruled out by the Phase-2 measurement (linear in cell
width; `~3.4e10` cells per side needed).

## 3. Status

```text
B1  pre-freeze sanity  PASS      C_one-sided 195-223 (cell), 1565 (e=0)
B2  pre-freeze sanity  FAIL      mean-value bound 1.21e6, 18x worse than direct
CHECKPOINT J           NOT CREATED   (brief: not until BOTH probes pass)
R7 BINDING GATE        NOT RUN
```

Historical statuses are untouched: `P5 = PARTIAL`, `R4 = FAIL`, `R5 = FAIL`,
`R6 = PASS`, Phase-2 SR prototype `= FAIL`. Nothing is re-described as
"almost passing".
