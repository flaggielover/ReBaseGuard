# P5X Compute Optimization R2 — profiling, redundancy, order and SR audit

```text
CAMPAIGN = P5X Compute Optimization R2 - Symbolic Residual and SR Cost Reduction
KIND     = certified-computation optimization under P5X
NOT      = P5R; not a theorem revision; not a scope reduction
```

Written before any R2 optimization is implemented. R1 (`9e19c70`) is the
baseline and is not modified.

---

## 1. Worktree isolation

```text
worktree = /Users/suzhe/ReBaseGuard-p5x-opt      branch = p5x-compute-opt-r1
HEAD     = 9e19c706b65ba354de7123fbe670c121acf1a861   (R1 result)   clean
```

`ra_certifier`, `drift_minorant` and `rebaseguard_certify` all resolve **inside**
this worktree; only the Python interpreter comes from the main tree. No other
process holds it (`/Users/suzhe/ReBaseGuard-p9` is a separate checkout on
`p9-research`). `WORKTREE_ISOLATION = PASS`.

## 2. A structural finding that precedes all profiling

**Only one certified path exists.** `ra_certifier.py` implements
`R_{CUSUM, m=1}(e)`, first moment, and nothing else. There is no `m > 1` path,
no SR path and no second-moment path anywhere in the P5X namespace.

Consequently the multipliers used in every projection so far — `x11` for
`m in {1,2,3,5}`, `x(25/11)` for second moments, `x2.5` cover and `x5-8`
certificate cost for SR — are **structural estimates that have never been
measured**, and the brief's requested profiles of "CUSUM m=3/m=5" and
"SR m=1/3/5" cannot be produced by measurement. This audit therefore
(a) profiles the one path that exists, exactly, and (b) times each **primitive**
so that the missing costs can be composed from measured primitives and operator
counts rather than guessed. That is recorded as the honest limit of R2's
profiling, not worked around.

## 3. Measured profile (cProfile, full production configuration)

`N = 120`, candidate degree `12`, `256` bits, subdivision depth `3`.

| bucket | `e = 0.25` | share | `e = 4` | share |
|---|---|---|---|---|
| `poly_bi_primitives` (`bi_mul`/`bi_pow`/`bi_add`…) | `198.4 s` | `49.8%` | `177.3 s` | `48.4%` |
| `bernstein_subdivide` (`_bernstein_max_abs`, `_split_*`) | `122.8 s` | `30.8%` | `114.2 s` | `31.1%` |
| `bernstein_param` (`_parameterize_triangle`, `_affine_to_unit_square`) | `20.5 s` | `5.1%` | `18.3 s` | `5.0%` |
| `bernstein_transform` (`_power_to_bernstein`) | `12.2 s` | `3.1%` | `11.1 s` | `3.0%` |
| `kernel_integrate_z` | `6.7 s` | `1.7%` | `6.8 s` | `1.9%` |
| `candidate_solve_numpy` | `0.5 s` | `0.1%` | `0.6 s` | `0.2%` |
| `kernel_phi_multiply` | `0.4 s` | `0.1%` | `0.4 s` | `0.1%` |
| `kernel_substitute` | `0.4 s` | `0.1%` | `0.5 s` | `0.1%` |
| `hermite_taylor_coeffs` / `reward_build` / `cheb_to_power` | `~0.05 s` | `~0.0%` | `~0.05 s` | `~0.0%` |
| unaccounted | | `9.1%` | | `10.2%` |

Per-primitive wall time, measured separately:

| primitive | one call |
|---|---|
| `_max_abs_on_reachable` | **`129.72 s`** |
| `_kernel_polynomials` | `2.10 s` |
| `solve_candidates` (pair, numpy) | `0.76 s` |
| `reward_rho1` / `reward_drho1` | `0.04` / `0.03 s` |
| `chebyshev_payload_to_power` | `0.01 s` |
| `phi_taylor_coefficients` | `< 0.01 s` |

A certification makes **2** `_max_abs_on_reachable` calls and **3**
`_kernel_polynomials` calls, i.e. `~259 s` against `~6 s`.

**Top cost centres.**
1. **`_max_abs_on_reachable`, the Bernstein continuum range bound — `~85–89%`**
   of CPU once the `poly_bi_primitives` it drives are attributed to it.
2. **Bernstein subdivision at depth 3** — `30.8%` on its own.
3. `_integrate_z` — `1.7%`. Everything else is noise.

The cost is essentially **independent of `e`** (`398.3 s` vs `366.5 s`), as
Device 1 of R-A′ predicts: the symbolic structure does not depend on the drift.

**This overturns the R1 report's expectation.** R1 concluded that "the per-cell
symbolic residual" was the bottleneck and named the Taylor order and candidate
degree as the levers. The measurement shows the residual *assembly* is `~2%`;
the *range bound* is the bottleneck. Any optimization aimed at the kernel
assembly would have been worthless.

## 4. Redundant-work audit

Audited for mathematical independence first, then weighed against the profile.

| object | independent of | genuinely reusable? | measured value of caching |
|---|---|---|---|
| Hermite/Taylor coefficients `b_i(e)` | state, mode, candidate | yes, across the 3 kernel calls | `< 0.01 s` — **worthless** |
| `_substitute_candidate(cand, mode)` | `phi` coefficients, `z_weight` | yes: 18 calls yield only 8 distinct results (`down`/`up` repeat across regimes; `g_hat` repeats between `K_e ghat` and `(d_e K_e) ghat`) | `~0.2 s` — **worthless** |
| Chebyshev-to-power conversion | everything downstream | yes | `0.01 s` — **worthless** |
| reward polynomials | candidate | partially | `0.07 s` — **worthless** |
| `_integrate_z` limit power tables | candidate, `phi` coefficients | yes: only 4 distinct affine forms (`ell`,`beta`,`alpha`,`upper`), recomputed in all 18 calls | `~4–5 s`, `~1.2%` — **marginal** |
| `_affine_to_unit_square` `r_powers`/`t_powers` | polynomial coefficients | **yes**: they depend only on `(r_lo, r_hi, t_lo, t_hi)` and the degrees, and the same 4 parameter sets recur across the 2 residual polynomials | inside the `~50%` bucket — **the only caching that matters** |
| `_power_to_bernstein` binomial ratios `C(k,i)/C(deg,i)` | polynomial coefficients | **yes**: depend only on the degree, recomputed `O(deg^2)` times per call, 8 calls per certification | inside `bernstein_transform` — **worth taking** |
| exact rational model constants | everything | yes | negligible |
| first/second-moment shared operators | see §7 | yes in principle | not measurable — no second-moment path exists |

**Verdict.** Every "obvious" cache (Hermite coefficients, substitutions,
transforms of the candidate) is worth `< 1%`. Only caching **on the Bernstein
path** can matter. This is exactly the kind of conclusion that guessing would
have got wrong.

## 5. Taylor-order audit — a negative result

Measured at the benchmark cell, CUSUM `m = 1`, `e = 1/4`
(`results/r2_sensitivity.json`):

| `N` | residual degree | certified truncation allowance | Bernstein residual | `C * delta` |
|---|---|---|---|---|
| `30` | `55` | `1.19e+07` | `1.773e+04` | `2.64e+09` |
| `40` | `65` | `4.73e+06` | `6.968e+03` | `1.05e+09` |
| `50` | `75` | `5.57e+05` | `7.467e+02` | `1.23e+08` |
| `60` | `85` | `2.47e+04` | `2.910e+01` | `5.45e+06` |
| `80` | `105` | `4.68e+00` | `4.081e-03` | `1.03e+03` |
| `120` (production) | `169` | `1.93e-10` | `1.026e-05` | `1.27e-02` |

**The Taylor order is NOT over-resolved.** The Cramér remainder
`0.4333 (11/2)^{N+1} / sqrt((N+1)!)` falls off a cliff only past `N ~ 100`: at
`N = 80` the truncation allowance is still `4.68`, which alone would blow the
enclosure by five orders of magnitude. Interpolating the measured decay
(`~0.55` per unit `N` in this range), the smallest `N` meeting even a generous
`1e-7` allowance is `N ~ 108-112`.

So the available headroom is `120 -> ~110`, worth `(110/120)^3 ~ 1.3x` at best —
and it would spend the entire truncation safety margin to get it. **Rejected.**
The R1 report's suggestion that the Taylor order was a lever is, on measurement,
wrong; recorded here rather than quietly dropped.

## 6. Candidate-degree and residual-degree audit

The residual degree is `169` at `N = 120`, i.e. `N + 2 * candidate_degree + 25`.
The candidate degree `12` contributes `~24` of that, so halving it to `6` would
reduce the degree only `169 -> 145` (`~14%`) while degrading the candidate and
therefore inflating the Bernstein residual directly. The dominant term is `N`,
and `N` is not reducible (§5). **Both degree levers are rejected.**

## 7. Adaptive-order verdict

An adaptive rule `N(e, m, D) = min{N : certified remainder <= alpha * budget}` is
**deterministic and safe** — but it is also **useless here**, for a reason that
is itself a result of R-A′'s design: Device 1 recentres the expansion so that the
expansion variable is the *unshifted* innovation `z` with `|z| <= 11/2`
**independently of `e`**. The remainder therefore does not depend on `e` at all
(confirmed in R1: identical to every digit at `e = 0, 0.26, 6.5, 12`). The rule
collapses to a single integer per detector, and §5 shows that integer is
`~110` against the current `120`.

`ADAPTIVE_ORDER_VERDICT = FEASIBLE BUT NOT WORTH IMPLEMENTING` (`<= 1.3x`,
spending the whole truncation margin).

For SR the same formula gives a *larger* `N`, because the expansion radius is
`c_SR = 6.7555` rather than `11/2`: `(6.7555/5.5)^{N+1}` grows the remainder, so
SR would need roughly `N ~ 135-145` for the same allowance — one of several
reasons SR is intrinsically dearer.

## 8. First/second-moment sharing

No second-moment path exists, so this is an audit of what *would* be shareable,
established from `PROOF.md` `L2` rather than measured:

| object | shared between first and second moments? |
|---|---|
| `_substitute_candidate(cand, mode)` | **yes** — it is independent of `z_weight`, so `K_e`, `K_{z,e}` and `K_{z^2,e}` all reuse one substitution |
| `phi` coefficient list `b_i(e)` | **yes**, identical |
| `_integrate_z` limit power tables | **yes**, identical |
| resolvent `C` | **yes**, identical |
| sub-cell geometry `h`, `n_sub` | **yes**, identical |
| candidate basis / Chebyshev-to-power | **yes** for the shared `ghat`; the pair functions need their own candidates |
| Bernstein range bound | **no** — one per residual polynomial, and the pair functions have `O(m^2)` of them |

**Verdict.** The shareable objects are exactly the ones the profile shows to be
worth `< 2%`. The `O(m^2)` growth of the second-moment cost sits entirely in the
**unshareable** Bernstein bound. So second-moment work will scale with the number
of pair functions almost undiminished by sharing:
`SECOND_MOMENT_SHARING_VERDICT = REAL BUT ECONOMICALLY MARGINAL`.

## 9. SR cost decomposition

Reconstructed from `sr_derivative/certificate/` (`GAMMA_CERTIFICATE.md`,
`STATUS.md`, `TAYLOR_RESIDUAL_BLOCKER.md`) and from the frozen recurrence.

| category | finding |
|---|---|
| **A. intrinsic mathematical difficulty** | the barrier is higher (`c_SR = 6.7555` vs `5.5`), so (i) the aligned chart must climb further, giving a worse resolvent — by softplus domination `C_SR/C_CUSUM = 3.86x` at `e = 0`, `2.17x` at `0.25`, `1.53x` at `0.5`, `1.27x` at `1` — and (ii) the `z`-expansion radius is `6.7555`, pushing the required Taylor order from `~110` to `~140` |
| **B. current implementation overhead** | **there is no SR certifier at all** in P5X. The `5-8x` figure is inherited from the `Gamma_SR` certificate, which is a *different computation* |
| **C. state/barrier geometry** | CUSUM's reachable set collapses onto axes plus a triangle `p+m <= 4`, which the 4-patch Bernstein cover exploits. The SR chart never resets to `0`, so no such collapse occurs; the `Gamma_SR` certificate needed `1210` symmetry-reduced state cells |
| **D. softplus-specific symbolic cost** | **the decisive one.** CUSUM's `q(x,z) = max(0, p + z - k)` is *piecewise affine in `z`*, so `ghat(q(x,z))` is a polynomial in `z` and the `z`-integration is symbolic. SR's `q(x,z) = log(1 + exp(y + z - 1/2))` is **transcendental in `z`**, so `ghat(q_SR(x,z))` is not a polynomial and the entire `_substitute_candidate` / `_multiply_by_phi` / `_integrate_z` chain **does not apply**. The `Gamma_SR` certificate had to use adaptive partitioning of the continuation interval instead: `96,295` innovation intervals for the `a` equation, `50,947` for `b` |
| **E. conservative bound inflation** | the historical `TAYLOR_RESIDUAL_BLOCKER.md` records an earlier SR architecture that failed precisely on remainder inflation; the successful one pays for tightness with interval count |

**The R1/R-A′ pipeline cannot be applied to SR at all.** The projected
`~2.9e4` SR CPU-hours therefore rests on extrapolating a method that does not
exist for the P5X target. The honest statement is that **SR cost is unknown and
its certifier is unbuilt**.

### SR-specific minorant verdict

The softplus domination `log(1 + e^v) >= max(0, v)` is rigorous and gives an SR
resolvent bound from the CUSUM one-sided minorant with `h -> log A`, preserving
the exact SR recurrence and the corrected domain `b_SR = log(1+A)` of erratum
`D1`. That is a genuine, one-sided, enclosure-preserving improvement and it does
reduce the SR *cover*. But it addresses the resolvent, which after R1 costs
`0.1 s` and is **not** the bottleneck; it does nothing about (D), which is.

`SR_MINORANT_VERDICT = VALID AND WORTH KEEPING, BUT NOT AN R2 CANDIDATE` — it
optimizes the part of SR that is already free. An SR campaign needs a *new
certifier architecture*, not an optimization, and that is out of R2's remit.

## 10. Candidate ranking

| # | candidate | class | expected speedup | math risk | impl. complexity | cert. risk | CUSUM | SR | 2nd moments | reusable |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Bernstein subdivision depth reduction** under a frozen acceptance ladder | `CERTIFIED_BOUND_REFACTOR` | `~1.8x` measured | low | very low | low — a looser depth is still a valid bound, and the ladder escalates on failure | yes | yes | yes | yes |
| 2 | **Memoised Bernstein basis tables** (`r_powers`/`t_powers` per `(r_lo,r_hi,t_lo,t_hi,deg)`, binomial ratio tables per degree) | `PURE_IMPLEMENTATION_CACHE` | `~1.3-1.5x` estimated | none — bit-identical output | low | none | yes | yes | yes | yes |
| 3 | state-patch x `z`-panel re-architecture (shrink the expansion radius, hence `N`, hence the degree) | `SCIENTIFIC_METHOD_CHANGE`? no — certified-method change | potentially `~30x` | medium | **high** | medium | yes | **enables SR** | yes | yes |
| 4 | Taylor order reduction | `CERTIFIED_ADAPTIVE_ORDER` | `<= 1.3x` | low | low | medium (spends the truncation margin) | yes | yes | yes | yes |
| 5 | kernel-path caching (substitutions, coefficients, limit powers) | `PURE_IMPLEMENTATION_CACHE` | `< 1.02x` | none | low | none | yes | n/a | yes | yes |
| 6 | SR softplus-domination minorant | `SR_SPECIFIC_CERTIFIED_BOUND` | reduces SR cover, not SR per-cell cost | low | medium | low | no | yes | yes | yes |

**Selected for R2: candidates 1 and 2**, per the two-candidate cap. They are the
only two that attack the measured `~85-89%` bottleneck at low risk. Candidate 3
is the genuinely large lever and is **explicitly deferred to R3** with its
analysis recorded here: it is a re-architecture, not an optimization, and
choosing it under a two-candidate cap would be a kitchen-sink refactor.
Candidates 4, 5 and 6 are rejected on measurement, not on taste.

No selected candidate is `SCIENTIFIC_METHOD_CHANGE` or `SCIENTIFIC_SCOPE_CHANGE`.

---

## 11. Sub-component measurement inside the bottleneck (decisive)

At `N = 120`, residual degree `145`, one residual polynomial pair:

| routine | CPU | note |
|---|---|---|
| `_parameterize_triangle` (x2) | `0.19 s` | negligible |
| **`_affine_to_unit_square`, low region** | **`38.43 s`** | `411 -> 9045 -> 17956` terms |
| **`_affine_to_unit_square`, high region** | **`59.56 s`** | `3471 -> 10731 -> 21316` terms |
| `_power_to_bernstein` (both) | `8.42 s` | |
| `_bernstein_max_abs`, depth 0 (both) | `0.01 s` | |

**`_affine_to_unit_square` is `~96%` of the Bernstein cost of the two main
regions, hence roughly `80%` of the entire certification.** The routine
substitutes `r -> r_lo + (r_hi-r_lo) rho` by building power tables and then
doing, for every one of the `~3500` coefficients `(i,j)`, a
`bi_mul(r_powers[i], t_powers[j])` producing `(i+1)(j+1)` terms — an
`O(deg^4)` dictionary-based loop, `~1.8e7` 256-bit ball multiplications with
Python dict overhead.

This also **falsifies the caching hypothesis of §4**: memoising `r_powers` and
`t_powers` addresses only their construction, which is `O(deg^2)`; the cost is
the `O(deg^4)` product loop, which is per-coefficient and cannot be cached.
Candidate 2 is therefore re-specified below as an **algorithmic** replacement,
not a cache — decided on the measurement, before any R2 code was written.

## 12. Depth measurement at production order

| depth | Bernstein residual | patches | CPU (one call) |
|---|---|---|---|
| `0` | `1.289015e-05` | `4` | `73.62 s` |
| `3` (R1 production) | `1.0257899e-05` | `256` | `129.72 s` |

Depth `3` buys a `26%` tighter residual for `1.76x` the cost. At the gate that
tightness is worth nothing: `C * delta` moves from `2.26e-3` to `2.85e-3`
against a budget of `0.19`. Depth is pure overhead here.
