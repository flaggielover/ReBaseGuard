# P5X R8 — Binding SR Certification: FROZEN specification

`CERTIFIED_RESOLVENT_BOUND_REPAIR` + `CERTIFIED_STABLE_BASIS_RANGE_BOUND`.
Not a scientific method change, detector change, theorem change or scope change.

**Frozen at Checkpoint J, before any binding gate is run.** Historical results
remain permanently binding: `R4 = FAIL`, `R5 = FAIL`, `R6 = PASS`,
`R7 centred B2 = FAIL`, historical SR full-cell prototype `= FAIL`. The B2 basis
audit is feasibility evidence only; R8 is the first binding attempt.

---

## 0. DISCLOSED DEVIATION FROM THE R8 BRIEF §8 — grid `1024x1024`, not `256x256`

The brief fixes the binding grid at `256 x 256`, justified by the audit's
`8.166205e-3`. **A pre-freeze scan shows that number was measured at an
unrepresentative cell.** The audit probed only the historical worst cell
(`zeta ~ 0.023`); the worst cell over the *domain* is mid-domain, and is roughly
`2.4x` larger:

| grid | worst-over-domain bound | worst cell | full sweep |
|---|---|---|---|
| `256` | **`2.006807e-02`** — exceeds `1e-2` | `(102,102)` | `5.2 min` |
| `512` | **`1.001361e-02`** — still exceeds `1e-2` | `(204,204)` | `20.3 min` |
| **`1024`** | **`5.009432e-03`** — `1.996x` margin | `(393,393)` | `84.8 min` (`14.1 min` on 6 cores) |
| `2048` | `2.499559e-03` | `(819,819)` | `331 min` |

Confirmed by a dense `40x40 = 1600`-cell scan at `1024`: worst `5.009432e-03`,
median `4.1739e-03`, p99 `4.9900e-03` — a tight distribution, so the scan is
representative.

Freezing `256 x 256` would freeze a specification already measured to fail
`B2-Q7`. That is the exact error recorded three times in this campaign (`D11`,
`Q4`/`D13`, and the Checkpoint-I resolvent), and the campaign's pre-freeze rule
exists to prevent it. This change is made **before** Checkpoint J and **before**
any binding result; it is not post-result tuning. The threshold `<= 1e-2` is
**not** weakened, and `1024` is frozen here permanently.

## 1. B1 — one-sided resolvent

### Proofs

**`B1-L1` (pathwise domination).** The minus chart evolves autonomously:
`y^-_t = softplus(y^-_{t-1} - z_t - 1/2)` depends only on `y^-_{t-1}` and `z_t`.
Couple both processes on the same innovation sequence. Then
`tau = inf{t : max(v^+_t, v^-_t) >= log A}` and
`tau^- = inf{t : v^-_t >= log A}`. For every `t`, `v^-_t >= log A` implies
`max(v^+_t, v^-_t) >= log A`, so `{tau^- <= t} subset {tau <= t}` for all `t`,
hence `tau <= tau^-` **pathwise**. ∎ *(Set inclusion under a coupling; no
distributional or monotonicity assumption.)*

**`B1-L2`.** Taking expectations of `B1-L1` from a state `x = (x^+, x^-)`:
`E_x[tau] <= E_{x^-}[tau^-]`, and the right side does not depend on `x^+`. ∎

**`B1-L3` (one-sided kernel exact).** The minus-chart kernel is
`(K^-_e f)(y) = int_{l^-(y)}^{infinity} f(softplus(y - z - 1/2)) phi(z+e) dz`
with `l^-(y) = y - c_SR`, obtained from the frozen two-chart definition by
deleting the plus-chart alarm condition. The state domain is `[0, b_SR]` with
the `D1`-corrected `b_SR = log(1+A)`. `softplus > 0` strictly, so no atom is
created. ∎

**`B1-L4` (certified iteration).** Let `V_n(P) >= sup_{y in P} P_y(tau^- > n)`
over a uniform grid. `V_0 = 1`. Using (i) the **widest** continuation set over
each cell, `l^-_P = y_lo - c_SR` (a superset, hence an upper bound on survival);
(ii) monotonicity of `softplus` in `y` (increasing) and in `z` (decreasing) to
enclose the image interval, with outward cell-index rounding; and (iii)
`mass_s >= int_{z_a}^{z_b} phi(z+e) dz` computed in Arb and rounded **up**, the
recursion `V_{n+1}(P) = min(V_n(P), sum_s (max over image) mass_s + tail V_n(0))`
is a valid upper bound at every `n`. The `min` is valid because
`P_y(tau^- > n)` is non-increasing in `n`. ∎

**`B1-L5` (transfer).** If `q := max_P V_{n_0} <= 1/2` then
`P_y(tau^- > j n_0) <= q^j`, so
`E_y[tau^-] = sum_{n>=0} P_y(tau^- > n) <= n_0/(1-q)` uniformly in `y`. With
`B1-L2` this bounds `sup_x E_x[tau]` for the **two-sided** process. ∎

No empirical monotonicity is load-bearing: only `softplus` monotone in each
argument (elementary calculus) and `n -> P(tau > n)` non-increasing (a
probability fact).

### Frozen B1 algorithm and parameters

```text
state domain    [0, b_SR],  b_SR = log(1+A)  (D1-corrected)
grid            G1 = 1024 uniform cells
z partition     Z1 = 1024 uniform sub-intervals on [-c_SR, 8]
tail            z > 8 mapped to cell 0, mass = 1 - Phi(8+e), rounded up
masses          Arb at 256 bits, outward-rounded UP.  Over an e-cell the
                supremum is attained at e* = clip(-(z_a+z_b)/2, e_lo, e_hi),
                since d/de int_{z_a}^{z_b} phi(z+e)dz = phi(z_b+e) - phi(z_a+e)
                vanishes exactly there and is a maximum
sweep rounding  each sweep multiplied by (1 + 2^-40); over n_max sweeps this
                inflates C by <= 4e-9 relative, and is included
stopping        first n_0 with q = max_P V_{n_0} <= 1/2 ;  C = n_0/(1-q)
n_max           4000
drifts          e = 1/4 exact, e = 0 exact, and the cell [24/100, 26/100]
```

### Binding B1 criteria (all must pass)

```text
B1-Q1  stopping-time domination proof                     PASS
B1-Q2  one-sided kernel correspondence                    PASS
B1-Q3  finite rigorous C_SR obtained
B1-Q4  C_SR(e = 1/4) <= 1000
B1-Q5  C_SR(e = 0)   <= 3000
B1-Q6  runtime <= 30 minutes
B1-Q7  no empirical monotonicity
B1-Q8  protected scientific semantics unchanged
```

## 2. B2 — dual representation

### Proofs

**`B2-P1` (exact conversion).** `x^i = sum_{k>=i} [C(k,i)/C(n,i)] B_k^n(x)` on
`[0,1]`; tensorising, `beta = M c M^T` with `M[k][i] = C(k,i)/C(n,i)`. Exact
rational linear algebra, evaluated in Arb. Measured: `max|beta| = 1.898676`
against `max|c| = 2.012154e10`, improvement `1.059767e10`; equality verified at
four random points to 16 digits; `max` coefficient radius `2.5e-110`.

**`B2-P2` (degree elevation).**
`beta^{(N)}_k = sum_i beta_i C(n,i)C(N-n,k-i)/C(N,k)` is an identity, so the
polynomial is unchanged. Used only to sharpen derivative hulls: `Mx` falls from
`10.2467` (degree 16) to `1.2046` (degree 32) against a true sampled `1.1670`.
Frozen at `N = 32`; higher degrees are forbidden in the binding result.

**`B2-P3` (cell restriction).** de Casteljau subdivision gives the exact
Bernstein coefficients of the same polynomial on a sub-box. Measured overshoot
against sampled truth on the historical worst cell: `1.000x` (sharp).

**`B2-P4` (range).** Convex-hull property: `min beta <= p <= max beta` on the
box. Derivative hulls use `partial_x` coefficients `N(beta_{i+1,j} - beta_ij)`.

**`B2-P5` (`K_e ghat` range, with the corrected `w^-` term).** With
`u(zeta^+) = 1/2 - log(w^+)`, `l(zeta^-) = log(w^-) - 1/2`,
`w^{+/-} = 1/A + zeta^{+/-}`, `zeta'^+ = w^+ E^+`, `zeta'^- = w^- E^-`,
`E^+ = e^{z-1/2}`, `E^- = e^{-z-1/2}`:

```text
d(K_e ghat)/dzeta^+ = int ghat_x(q) E^+ phi dz  -  ghat(q(.,u)) phi(u+e) / w^+
d(K_e ghat)/dzeta^- = int ghat_y(q) E^- phi dz  -  ghat(q(.,l)) phi(l+e) / w^-
```

**The second boundary term uses `w^-`, not `w^+`** — this is the correction the
B2 audit flagged as open. Both formulas were verified against central finite
differences at five points including strongly off-diagonal ones
`(0.023, 0.700)` and `(0.700, 0.023)`: relative agreement `<= 6.5e-13`.
The weights are closed form,
`int E^+ phi = e^{-e}[Phi(u+e-1) - Phi(l+e-1)]`,
`int E^- phi = e^{e}[Phi(u+e+1) - Phi(l+e+1)]`.

Hence, with `G = max|ghat|` and `Mx, My` the elevated derivative hulls,

```text
|d K_e ghat/dzeta^+| <= Mx int E^+ phi + G phi(u+e)/w^+
|d K_e ghat/dzeta^-| <= My int E^- phi + G phi(l+e)/w^-
```

and the oscillation of `K_e ghat` over a cell of half-width `h` is at most
`2h` times their sum (mean value theorem).

**`B2-P6` (cell bound).** `r = ghat - rho_1 - K_e ghat`, so
`|r(zeta)| <= |r(zeta_c)| + osc(ghat) + osc(rho_1) + osc(K_e ghat)`, with
`r(zeta_c)` the exact R6 centre value, `osc(ghat)` the sharp Bernstein hull
width, `osc(rho_1)` its Arb enclosure width, and `osc(K_e ghat)` from `B2-P5`.

`K_e` is **never** applied to a Bernstein basis image (that route measured
`1.9324e6` in the audit and is rejected).

### Binding B2 criteria (all must pass)

```text
B2-Q1   exact monomial/Bernstein equality
B2-Q2   exact degree elevation preserves the candidate
B2-Q3   rigorous cell restriction
B2-Q4   rigorous ghat hull
B2-Q5   rigorous derivative hulls
B2-Q6   rigorous K_e ghat range enclosure (with the corrected w^- term)
B2-Q7   worst-cell residual enclosure <= 1e-2          [threshold UNCHANGED]
B2-Q8   historical worst cell improves by >= 1e6 over 6.736713e4
B2-Q9   grid fixed at 1024 x 1024                      [see §0 disclosure]
B2-Q10  mean runtime <= 10 ms/cell
B2-Q11  z_panels = 0
B2-Q12  softplus_approximations = 0
B2-Q13  R6 fast kernel unchanged
B2-Q14  no empirical monotonicity used as a rigorous bound
```

## 3. `R8_LOCAL_CERTIFICATION_GATE = B1_GATE AND B2_GATE` (binding conjunction)

## 4. SR full-cell prototype criteria, frozen here

```text
F1   finite certified enclosure
F2   consistent with existing MC evidence (MC is DIAGNOSTIC ONLY and may only
     refute: the certified interval must contain the MC point estimate within
     its stated standard error)
F3   half-width <= 0.2
F4   z_panels = 0
F5   softplus_approximations = 0
F6   no empirical monotonicity
F7   CPU <= 2 hours
F8   protected tree unchanged
F9   candidate and scientific target unchanged
F10  every scalar-certifier input traces to a binding B1/B2 output
```

Target: `R_{SR,1}(e) = e + g_0(x_0)` on `e in [24/100, 26/100]`, `m = 1`,
convention A, `D1`-corrected domain, enclosure
`e + ghat(x_0) +/- C_SR * delta`.

## 5. Frozen prediction — including a predicted `F3` FAILURE

```text
C_SR(1/4)  180 .. 260        C_SR(0)  1300 .. 2200
B1 gate    PASS              B1 runtime  < 5 min
B2 worst residual  4.5e-3 .. 6.0e-3      B2 gate  PASS
B2 wall    80 .. 100 min single-core
R8_LOCAL_CERTIFICATION_GATE  PASS
SR full-cell prototype       **PREDICTED FAIL on F3**
```

This prediction is recorded **before** the run, from a pre-freeze measurement,
and R8 is frozen and executed anyway because the binding evidence is worth
having: it would be the first time SR certification machinery passes end to end.

**Why `F3` is predicted to fail.** A `46x46` point sample gives the true
`sup |r| = 2.472122e-05` (at `zeta ~ 0.0222`). The certified `delta` at
`G = 1024` is `5.009432e-03` — **`202.6x` looser than the truth**. Hence

```text
C_SR * delta_certified  =  200 * 5.009e-3  =  1.00     F3 needs <= 0.2   FAIL
C_SR * sup|r|_true      =  200 * 2.472e-5  =  0.0049   would pass with 40x margin
```

The looseness is structural, not numerical. At the worst cell the bound splits
as `ghat_osc = 1.384e-3` (the **sharp** Bernstein hull — genuine, irreducible at
this grid), `Ke_osc = 2.445e-3` (mean-value with near-sharp derivative hulls —
close to genuine) and `rho1_osc = 1.175e-3` (raw interval width, the only clearly
loose term, worth ~22%). Bounding `osc(ghat)` and `osc(K_e ghat)` **separately**
discards the cancellation between them: `r` is a difference of two quantities of
size `~1.84` that agree to `~2e-5`, and the frozen recipe cannot see that.

Grid refinement cannot rescue it either: `delta ~ 5.13/G`, so `delta <= 1e-3`
needs `G ~ 5130`, i.e. `2.6e7` cells at `4.85 ms` = `35` CPU-hours, which
violates `F7 <= 2 hours`. **`F3` and `F7` are jointly unreachable under the
frozen §6 recipe**, and the fix — bounding `osc(r)` directly rather than as a
sum of separate oscillations — is a *new* B2 refinement that requires its own
pre-result audit and is therefore out of scope for R8.

Named risks to the rest: (i) the dense scan probed `1600` of `1048576` cells, so
the full sweep may find a worse cell; (ii) `C_SR` over the *e-cell* may exceed
the point values.
