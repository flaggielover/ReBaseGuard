# P5X R3 — SR architecture audit, candidate bases, geometry and cost model

---

## 1. Why the current SR certificate is expensive — measured, not heuristic

From `sr_derivative/results/sr_residual_global_{a,b}.json` and
`sr_monotone_contraction.json` (the artifacts of the successful `SR-GAMMA-CERTIFIED`
architecture):

| term | measured value |
|---|---|
| **A. state patches** | `1210` live fundamental cells, from a `grid = 64` partition of `[0, log(1+A)]^2`, symmetry-reduced |
| **B. innovation intervals** | residual `a`: `96,295` total, mean `79.6` per patch, range `[62, 94]`; residual `b`: `50,947`, mean `42.1`, range `[37, 48]`. Built from `32` initial partitions per patch with adaptive depth `2` |
| **C. approximation degree** | exact-dyadic candidate of degree `16`; per-patch Bernstein bound |
| **D. transcendental evaluation** | one interval `softplus` (and `exp`/`log`) evaluation per innovation interval per patch — `~147,000` transcendental interval evaluations for the two equations |
| **E. residual / range bound** | per-patch polynomial Bernstein plus `direct_remainder`, `integration_remainder`, `reward_remainder` terms |
| **F. resolvent** | monotone block contraction, `200` cells, `n = 250`, `192` bits — **cheap**, as in CUSUM after R1 |
| **G. second-moment multiplier** | not built; the `b` equation above is the `Gamma` chain's second component, not P5X's `S_{SR,m}` |
| `m` dependence | not built at all |

**The cost centre is B×D**: roughly `1.5e5` interval evaluations of a
transcendental composed integrand, each contributing only a *first-order*
enclosure. The partitioning is fine because interval evaluation of
`ghat(q_SR(y,z))` over a `z`-interval is first-order accurate: halving the panel
halves the error, so reaching `eps_a = 4.5e-6` needs many narrow panels.

This is the precise sense in which "SR costs `5-8x` CUSUM": it is not the same
work done slower, it is **a different, lower-order method**, forced by the fact
that `q_SR` is transcendental in `z` while `q_CUSUM` is piecewise affine.

## 2. The R3 candidate architecture

Per state patch `Y` and innovation panel `Z`:

```text
1  localize     u = y + z - 1/2   over  Y x Z   (an interval of half-width h_y + h_z)
2  approximate  softplus(u) by a degree-d local polynomial P(u) with a RIGOROUS
                remainder interval E_d, so softplus(u) in P(u) + E_d on Y x Z
3  compose      ghat(q_SR) -> ghat(P^+ + E^+, P^- + E^-), a polynomial in z of
                degree <= 16 d plus an enclosed composition remainder
4  integrate    against phi(z+e) in CLOSED FORM using centred truncated Gaussian
                moments N_k = int_Z (z - z_c)^k phi(z+e) dz, computed by the exact
                stable recursion
5  remainder    every step keeps an explicit outward-rounded interval
6  assemble     sum over panels, add the certified tail, then the usual Bernstein
                range bound over the patch
```

The gain is one of **order**: step 4 is exact, so the panel error is
`O(h^{d+1})` rather than `O(h)`. The question R3 must answer with measurement is
whether the higher per-panel cost is repaid by the far smaller panel count.

## 3. Softplus structure audit (§8) — the reason to be hopeful

```text
softplus'(u)   = sigma(u) in (0,1)          => softplus is 1-Lipschitz, increasing
softplus''(u)  = sigma(1-sigma) in (0, 1/4] => convex, second derivative <= 1/4
softplus'''(u) = sigma(1-sigma)(1-2sigma),  |.| <= 1/(6 sqrt 3) = 0.09623
softplus^{(n)} = sigma^{(n-1)}, a polynomial in sigma with Eulerian coefficients
```

Two consequences that matter:

* **derivative bounds are absolute constants, independent of `u`.** This is the
  opposite of the Gaussian case in R-A′, where `|phi^{(n)}| ~ sqrt(n!)` forced
  `N = 120`. Here a *low* degree suffices, and the required degree does not grow
  with the domain;
* the exact Taylor coefficients about a point are computable rigorously and
  cheaply with `arb_series`. Measured at `u = 0.3`, order 6:
  `0.854355, 0.574443, 0.122229, -0.006066, -0.004754, 0.000586` — decaying by
  roughly an order of magnitude every two terms.

Stable evaluation forms are adopted where they help rigor:
`softplus(u) = u + log(1 + e^{-u})` for `u >= 0` and `log(1 + e^u)` for `u < 0`,
which avoids overflow in `exp` at the `|u| ~ 6.8` extremes of the SR range.

## 4. Competing local approximation bases (§5), ranked

| basis | degree needed | remainder tightness | composition cost | Gaussian-integration compatibility | interval dependency | patch reuse | proof burden | stability |
|---|---|---|---|---|---|---|---|---|
| **A. Taylor about panel centre** | low (`~4-8`) | good, and the remainder is an explicit derivative bound | cheap (`arb_series`) | perfect — polynomial in `z`, closed-form moments | low if centred | coefficients depend on the panel centre, so reuse only across equal centres | **low** — one classical remainder theorem | good with centred moments |
| B. Chebyshev / minimax | slightly lower than A | best per degree | needs a rigorous sup-norm bound, which is the whole difficulty | perfect | low | same | **high** — certifying a minimax remainder rigorously is its own project | good |
| C. Bernstein enclosure of `softplus` on each `u`-panel | n/a (it is an enclosure, not an expansion) | first-order in the panel width — i.e. the method the current certificate already uses | very cheap | poor — it gives an interval, not a polynomial, so the closed-form integral is lost | none | good | low | excellent |
| D. rational enclosure | very low | excellent | poor — a rational in `z` destroys the closed-form Gaussian moments | high | poor | poor | high | fragile |

**Selected for feasibility: A** (the only basis that combines low degree, a cheap
rigorous remainder and closed-form Gaussian integration), with **C as the
declared fallback** — it is exactly the incumbent method, so falling back to it
is a null change rather than a new risk.

B and D are rejected on proof burden and integration incompatibility
respectively, before any measurement.

### A finding that outranks all four

There is a **fifth** route that removes the need to approximate `softplus` in the
kernel composition at all. In the multiplicative variable `xi = e^y` the frozen
recurrence is exactly

```text
xi' = 1 + xi * e^{z - 1/2}        (alarm iff xi * e^{z-1/2} >= A)
```

so a candidate expressed as a polynomial in `xi` composes to terms
`xi_+^i xi_-^j e^{(i-j)(z-1/2)}`, and `int e^{cz} phi(z+e) dz` has a **closed
form** by completing the square. The `z`-integration would then be exact with
**no panels and no polynomial approximation of any transcendental**. The
obstruction is that the integration limits are affine in `y = log xi`, not in
`xi`, so the two representations do not share a single polynomial variable; on a
*small state patch* that mismatch is confined to two thin boundary strips.

This is recorded as the **strongest identified SR lever** and is explicitly
**not** implemented or claimed in R3: it is a second architecture, and R3's remit
is one feasibility gate, not two. It is the natural R4 subject.

## 5. State-patch geometry (§6)

`y in [0, log(1+A)]` per chart. The frozen rule for R3's feasibility work:

* **uniform** patches on a `grid` power of two, matching the incumbent `grid = 64`
  so the two architectures are directly comparable;
* softplus has **no kinks** — it is real-analytic everywhere — so, unlike CUSUM,
  there is no reset-kink alignment requirement and no need for adaptive patching
  driven by the nonlinearity. This is a genuine SR advantage that the incumbent
  architecture does not exploit;
* the **alarm boundary** is `y^+ = c_SR - z`, which is a moving line in `z`, not a
  fixed feature of the `y`-partition; it is handled in the `z`-geometry (§6), not
  by patch alignment;
* patch geometry is **independent of `e`** (the limits and `q_SR` contain no `e`
  in the `z`-formulation), so a patch layout is reusable across every `e`-cell of
  the cover — a large structural saving;
* patch geometry is **independent of `m`** (the `m`-dependence lives in the
  backward functions `h_j`, `S_j`, not in the geometry), so it is reusable across
  all four windows.

## 6. Innovation-panel geometry and tails (§7)

The `z`-integral runs over the **live** region `(l(y), u(y))`, which is already
finite: `|z| <= c_SR = 6.7555`. There is therefore **no infinite tail in the
kernel** — the alarm truncates it exactly, and this is a property of the frozen
model, not an approximation.

Where tails do appear is in the **reward** `rho_{1,e}`, `rho_{2,e}`, which contain
`phi` and `Phi` at `u+e` and `l+e`; those are evaluated in closed form by Arb's
`erf`, so they are exact enclosures with no truncation at all.

The panel layout inside `(l(y), u(y))`:

```text
core panels  : a uniform subdivision of [ l_max(Y) , u_min(Y) ] , the sub-interval
               alive for EVERY y in the patch Y
boundary strips: [ l_min(Y), l_max(Y) ] and [ u_min(Y), u_max(Y) ] , each of width
               exactly the patch width, where the alarm status varies across Y;
               enclosed conservatively by |integrand| <= sup|ghat| times the
               Gaussian mass of the strip
```

Both strips have width equal to the `y`-patch width (`log(1+A)/grid`), so their
contribution is `O(patch width)` and shrinks with the patch count. No part of the
real line is dropped, and no finite window is substituted for an infinite one.

## 7. Scientific-neutrality classification (§9)

| element | class |
|---|---|
| local Taylor enclosure of `softplus` with rigorous remainder | `CERTIFIED_LOCAL_APPROXIMATION` |
| closed-form centred Gaussian moments replacing interval quadrature | `CERTIFIED_KERNEL_REFACTOR` |
| core/boundary-strip split of the `z`-integral | `CERTIFIED_TAIL_DECOMPOSITION` |
| reuse of R1's drift-explicit resolvent for SR by softplus domination | `CERTIFIED_BOUND_REFACTOR` |

None is `SCIENTIFIC_METHOD_CHANGE` or `SCIENTIFIC_SCOPE_CHANGE`: the detector
recurrence, state domain, stopping convention, targets and theorem interface of
`EXACT_SR_TARGET.md` are all untouched.

## 8. Pre-result cost model (§12)

```text
CPU  ~  (#state patches) x (#z panels per patch) x (local polynomial cost)
        x (moment multiplier) x (m multiplier)
```

| term | incumbent | R3 candidate |
|---|---|---|
| state patches | `1210` | `1210` (same grid, for comparability) |
| `z` panels per patch | `79.6` (residual `a`) | `n_z`, to be measured; the design target is `O(10)` |
| per-panel cost | one interval evaluation of a transcendental composed integrand | one `arb_series` softplus expansion + one polynomial composition + `deg` centred Gaussian moments |
| moment multiplier | — | `~2` for first moment with derivative equation |
| `m` multiplier | — | operator-count driven, see the CUSUM lane |

**The model refuses to predict a speedup from degree alone.** The candidate wins
only if `(#panels reduced) x (per-panel cost ratio) < 1`, and the per-panel cost
ratio is exactly what the feasibility gate measures. A plausible-looking degree
reduction with a `20x` more expensive panel would be a loss, and the gate is
designed to expose that.
