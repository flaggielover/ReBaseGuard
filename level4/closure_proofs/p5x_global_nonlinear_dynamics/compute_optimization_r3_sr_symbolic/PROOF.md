# P5X R3 — proof obligations `L-R3.1` … `L-R3.8`

All statements are about the exact frozen SR objects of `EXACT_SR_TARGET.md`.
Nothing below uses an empirical monotonicity.

Notation: a state patch is a closed box `Y = [y^+_lo, y^+_hi] x [y^-_lo, y^-_hi]`;
an innovation panel is a closed interval `Z = [z_c - h, z_c + h]`;
`v^{+} = y^+ + z - 1/2`, `v^{-} = y^- - z - 1/2`; `sp(u) = log(1 + e^u)`;
`sigma(u) = 1/(1+e^{-u})`.

---

## `L-R3.1` — the local softplus enclosure contains the exact softplus

**Claim.** For a panel on which `u = v^{+}` (or `v^{-}`) ranges over an interval
`U = [c-H, c+H]`, and for a degree `d`, the enclosure

```text
sp(u)  in  sum_{k<=d} a_k (u-c)^k  +  [-E_d, E_d] ,      E_d := |A_{d+1}| H^{d+1}
```

is valid for every `u in U`, where the `a_k` are outward-rounded balls containing
`sp^{(k)}(c)/k!` and `A_{d+1}` is a ball containing `sp^{(d+1)}(xi)/(d+1)!` for
**every** `xi in U`.

**Proof.** `sp` is real-analytic on `R`: `1 + e^u > 0` everywhere and `log` is
analytic on `(0, infinity)`. Taylor's theorem with Lagrange remainder gives, for
each `u in U`, some `xi` between `c` and `u` with
`sp(u) = sum_{k<=d} sp^{(k)}(c)(u-c)^k/k! + sp^{(d+1)}(xi)(u-c)^{d+1}/(d+1)!`,
and `|u-c| <= H`. Both `a_k` and `A_{d+1}` are obtained by evaluating the power
series of `sp` with `arb_series` at an argument whose constant term is the
**interval** `U`; by inclusion isotonicity of ball arithmetic the resulting
coefficient balls contain the corresponding derivatives divided by factorials at
every point of `U`, in particular at `c` and at the unknown `xi`. Hence the
displayed containment. `[]`

**Remark (why the degree stays low).** `sp' = sigma in (0,1)`,
`sp'' = sigma(1-sigma) in (0, 1/4]`, `sp''' = sigma(1-sigma)(1-2 sigma)` with
`|sp'''| <= 1/(6 sqrt 3)`, and in general `sp^{(n)} = sigma^{(n-1)}` is a
polynomial in `sigma in (0,1)` with Eulerian coefficients. Every derivative is
bounded by an absolute constant **independent of `u`**. This is the exact
opposite of the Gaussian situation in R-A′, where `|phi^{(n)}| ~ sqrt(n!)` forced
`N = 120`; here the required degree does not grow with the domain.

## `L-R3.2` — composition preserves containment

**Claim.** If `sp(v^{+}) in P^{+}(z) + E^{+}` and `sp(v^{-}) in P^{-}(z) + E^{-}`
on `Y x Z`, and `ghat` is the exact-dyadic candidate polynomial, then evaluating
`ghat` on those enclosures with ball arithmetic yields an interval containing
`ghat(q_SR(y,z))` for every `(y,z) in Y x Z`.

**Proof.** `q_SR(y,z) = (sp(v^{+}), sp(v^{-}))` by definition. Ball arithmetic is
inclusion-isotone: if `X ni x` and `Y ni y` then the computed `X op Y` contains
`x op y` for `op` in `{+, -, *}`. `ghat` is a finite composition of `+`, `-`, `*`
on its (exact dyadic) coefficients and its two arguments, so the computed value
contains the exact one pointwise. `[]`

## `L-R3.3` — the Gaussian integral of the enclosed integrand is rigorously enclosed

**Claim.** With the enclosed integrand written as
`sum_{k<=D} C_k (z-z_c)^k + [-E, E]` on `Z`, the panel contribution is enclosed by
`sum_k C_k N_k + [-E, E] * M_Z`, where `M_Z = int_Z phi(z+e) dz` and

```text
N_k = int_Z (z - z_c)^k phi(z+e) dz
N_k = (k-1) N_{k-2}  -  mu N_{k-1}  -  [ (z-z_c)^{k-1} phi(z+e) ]_{z in dZ} ,  mu := z_c + e ,
N_0 = Phi(z_hi+e) - Phi(z_lo+e) ,   N_1 = phi(z_lo+e) - phi(z_hi+e) - mu N_0 .
```

**Proof.** Linearity of the integral gives the first display, with
`|int_Z r(z) phi(z+e) dz| <= E * M_Z` for any `r` with `|r| <= E`. The recursion
is obtained by integrating
`d/dz[(z-z_c)^{k-1} phi(z+e)] = (k-1)(z-z_c)^{k-2} phi - (z-z_c)^{k-1}(z+e) phi`
over `Z` and writing `z + e = (z - z_c) + mu`. Every term is a Gaussian value at
an endpoint, evaluated by Arb's `exp`/`erf` as an outward-rounded ball. Because
the moments are **centred**, `|N_k| <= h^k M_Z`, so the recursion is numerically
stable for `h <= 1` and no cancellation is amplified. `[]`

## `L-R3.4` — tail handling is rigorous

**Claim.** No part of the `z`-domain is discarded and no infinite tail is
truncated.

**Proof.** The kernel integral runs over the **live** region
`(l(y), u(y)) = (y^- - c_SR, c_SR - y^+)`, which is a bounded interval because the
alarm test truncates it exactly; this is a property of the frozen model, not an
approximation, and `|z| <= c_SR = 6.7555` on it. The reward terms
`rho_{1,e}, rho_{2,e}` contain `phi` and `Phi` at `u+e` and `l+e` only, and Arb
evaluates those in closed form via `erf`, so they carry no truncation at all.
Hence there is no tail to bound. `[]`

## `L-R3.5` — the patch assembly covers the live domain with no gaps

**Claim.** A uniform `grid x grid` partition of `[0, log(1+A)]^2` covers every
reachable live SR state, with adjacent patches sharing boundaries.

**Proof.** By erratum `D1` (proved from the recurrence), every live state
satisfies `0 <= y^{+}, y^{-} < log(1+A)`. The closed boxes
`[i b/grid, (i+1) b/grid] x [j b/grid, (j+1) b/grid]`, `b = log(1+A)`,
`0 <= i, j < grid`, tile `[0,b]^2` exactly: their union is `[0,b]^2` and interiors
are disjoint. Shared faces are covered by both neighbours, which is conservative
for a supremum bound. `[]`

## `L-R3.6` — alarm-boundary handling is exact or conservatively enclosed

**Claim.** Splitting the `z`-range of a patch `Y` into a core
`[l_max(Y), u_min(Y)]` and two boundary strips
`[l_min(Y), l_max(Y)]`, `[u_min(Y), u_max(Y)]` is exhaustive and conservative.

**Proof.** `l(y) = y^- - c_SR` is increasing in `y^-` and `u(y) = c_SR - y^+` is
decreasing in `y^+`, so over the box `Y` each ranges over an interval whose
endpoints are attained at corners: `l_min = y^-_lo - c_SR`, `l_max = y^-_hi - c_SR`,
`u_min = c_SR - y^+_hi`, `u_max = c_SR - y^+_lo`. On the core, **every** `y in Y`
is alive, so the integrand is the true one. On a strip, some `y` are alive and
some have alarmed; bounding the contribution by
`sup_Y |ghat| * (Gaussian mass of the strip)` dominates both cases, since the
alarmed case contributes `0` to the kernel and the alive case is bounded by the
same product. The three regions exhaust `[l_min, u_max]`, and outside it no `y`
in `Y` is alive. Each strip has width exactly the patch width
`log(1+A)/grid`. `[]`

## `L-R3.7` — the residual enclosure targets the exact frozen SR equation

**Claim.** The assembled quantity is a rigorous enclosure of the residual of
`g = K_e g + rho_{1,e}` for the exact frozen `K_e`, `rho_{1,e}` of
`EXACT_SR_TARGET.md` §3.

**Proof.** `L-R3.1`–`L-R3.3` give a rigorous enclosure of
`int_{live} ghat(q_SR(y,z)) phi(z+e) dz` on each patch, `L-R3.6` shows the
patchwise `z`-decomposition is exhaustive and conservative, and `L-R3.5` shows the
patches exhaust the live state domain. The reward is evaluated exactly. The
residual is the difference of these exact objects with `ghat`, so its enclosure
targets the exact equation and nothing else. No step replaces an object of §3 by
a surrogate. `[]`

## `L-R3.8` — no empirical monotonicity is required

**Claim.** Every monotonicity invoked is proved.

**Proof.** Three are used, all elementary: `sigma` is strictly increasing
(`sigma' = sigma(1-sigma) > 0`), so its range on an interval is given by its
endpoint values; `sp` is strictly increasing for the same reason; and `l`, `u`
are affine and monotone in `y^-`, `y^+` respectively (`L-R3.6`). No statement of
P5 or P7, and in particular neither `sup_e E[tau|e] = E[tau|0]` nor the two-sided
`D3` claim, is used anywhere. `[]`

---

## Status

| lemma | status |
|---|---|
| `L-R3.1` local softplus enclosure | **PROVED** (Taylor + Lagrange, coefficients by interval `arb_series`) |
| `L-R3.2` composition containment | **PROVED** (inclusion isotonicity) |
| `L-R3.3` Gaussian integration | **PROVED** (exact centred-moment recursion) |
| `L-R3.4` tails | **PROVED** (there is no tail: the alarm truncates exactly) |
| `L-R3.5` patch cover | **PROVED** (uses erratum `D1`) |
| `L-R3.6` alarm boundary | **PROVED** (corner monotonicity + conservative strips) |
| `L-R3.7` exact target | **PROVED** given `L-R3.1`–`L-R3.6` |
| `L-R3.8` no empirical monotonicity | **PROVED** |

No load-bearing lemma failed, so the feasibility gate may be run once
Checkpoint E is pushed.
