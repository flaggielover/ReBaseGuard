# P5X Compute Optimization R1 — scientific-neutrality audit

```text
CAMPAIGN            = P5X Compute Optimization R1 — Drift-Explicit Resolvent Reduction
KIND                = certified-computation optimization under P5X
NOT                 = P5R; not a new theorem campaign; not a scope change
CLASSIFICATION      = CERTIFIED_BOUND_REFACTOR
SCIENTIFIC_TARGET_CHANGED = NO
SCIENTIFIC_SCOPE_CHANGED  = NO
```

Written before any optimized benchmark result. R-A′ remains the reference
implementation and its `PASS` at half-width `0.014176477298268092` is untouched.

---

## 1. What dominates the runtime

In `certified_method_repair_ra/ra_stop_gate.py` the cost is

```text
runtime  =  n_sub  x  (3 certified solves + 2 Bernstein continuum bounds) ,
n_sub    =  ceil( (e_hi - e_lo) / (2 h) ) ,     h = 1 / (4 a C) ,   a = 2 phi(0) ,
```

so `n_sub` is **directly proportional to `C = ||(I - K_e)^{-1}||_inf`**, the only
quantity in the frozen sub-cell rule that is not a universal constant. Halving
`C` halves the campaign. `C` also enters the enclosure through `C delta`,
`G_0`, `G_1` and `S_2`, so it is the single dominant scalar of the whole method.

## 2. Why R-A′'s bound is conservative

R-A′ proved `C` from scratch by **block forcing**: from any live state,
`S^+_n >= G_n - nk`, so `{G_n >= h + nk}` alone forces an alarm within `n` steps.
That demands a run of `n` innovations whose *sum* clears `h + nk` and credits the
chain with nothing it does in between. It is rigorous, self-contained and
drift-explicit — and it is crude. Measured here:

| `|e|` | block forcing (R-A′) | monotone minorant | ratio |
|---|---|---|---|
| `0` | `5323.418` | `1232.836` | `4.32x` |
| `0.24` (cell worst case) | `1224.397` | `220.708` | `5.55x` |
| `0.5` | `150.885` | `61.364` | `2.46x` |
| `1` | `19.557` | `16.938` | `1.15x` |
| `2` | `5.759` | `5.732` | `1.00x` |

The gap is large exactly where the cover is expensive — near the origin — and
closes by `|e| ~ 1`, where the cover is already nearly free. That is the whole
economic content of this optimization.

## 3. What the optimization is

Replace the block-forcing bound by the **one-sided monotone Bellman minorant**
that `closure/04_ARB_CERTIFICATE.md` claim `N-01` already certifies at `e = 0`,
made drift-explicit. Under drift `-e` with `e > 0` the minus arm has increment
`-z - k ~ N(|e| - k, 1)`, so the entire drift dependence is the substitution
`k -> k - |e|` in the transition and reward arguments of that minorant. Then

```text
q_n := inf_x P_x(tau <= n)  >=  H_n(0)  >=  lower_n[0] ,
C  <=  min_t  t / lower_t[0] .
```

`PROOF.md` in this directory proves the two monotonicity facts it rests on and
the resolvent inequality itself.

## 4. Neutrality, item by item

| element | R-A′ | R1 | identical? |
|---|---|---|---|
| detector | frozen CUSUM `k = 1/2`, `h = 5`, inclusive post-update test | same | **yes** |
| window `m` | `1` | same | **yes** |
| drift `e`, benchmark cell | `[0.24, 0.26]` | same | **yes** |
| Fredholm equation | `g = K_e g + rho_{1,e}` | same | **yes** |
| derivative equation | `d_e g = K_e d_e g + (d_e K_e) g + d_e rho_{1,e}` | same | **yes** |
| kernel `K_e` | `int_{l(x)}^{u(x)} f(q(x,z)) phi(z+e) dz` | same | **yes** |
| reward `rho_{1,e}` | recentred, `N = 120`, Hermite coefficients | same | **yes** |
| state space | `[0,5]^2`, reachable set `p=rt, m=r(1-t)`, `r in [0,1],[1,4]`, axis tails | same | **yes** |
| stopping convention | frozen `tau`, convention A, `w = min(m, tau)` | same | **yes** |
| `R(e)`, `S(e)` definitions | `R = e + g(x_0;e)`; `S` per `P5X-T2` | same | **yes** |
| candidate degree / precision / Bernstein depth | 12 / 256 bits / depth 3 | same | **yes** |
| enclosure meaning | outward-rounded Arb ball containing the true value for every `e` in the cell | same | **yes** |
| theorem consumer interface | `R_max`, `s_min`, `M_2` scalars into `X1`–`X3` | same | **yes** |
| stop-gate semantics | half-width `<= 0.2` `->` PASS | same | **yes** |
| **`||(I-K_e)^{-1}||` bound** | block forcing | monotone minorant | **NO — this is the only change** |
| `n_sub`, `h` | derived from `C` by the frozen formula | same formula, different `C` | derived |

The certified **numbers** change, because a different (tighter, still rigorous)
upper bound is substituted for one scalar. The certified **object** does not.
Both methods produce a valid enclosure of the same `R_{CUSUM,1}` on the same
cell, so both must contain the true value and therefore must overlap;
`§13` of the campaign brief checks that empirically.

## 5. Classification, argued

| candidate class | verdict |
|---|---|
| `CERTIFIED_COMPUTE_ONLY` | **too weak.** The optimization does not merely run the same arithmetic faster; it substitutes a different rigorous bound, so the certified interval changes |
| **`CERTIFIED_BOUND_REFACTOR`** | **yes.** One rigorous upper bound on one scalar is replaced by a tighter rigorous upper bound on the same scalar. Estimand, operator, kernel, reward, state space, stopping convention, enclosure semantics and gate semantics are all unchanged |
| `SCIENTIFIC_METHOD_CHANGE` | **no.** No equation, no probability model, no discretisation of the *target* and no theorem input changes |
| `SCIENTIFIC_SCOPE_CHANGE` | **no.** Detector, window, cell, `e`-range `[0, 12]` and the `0.2` threshold are all unchanged. In particular this campaign does **not** shorten `[0,12]` |

Neither stop condition of brief §4 is triggered, so the campaign proceeds.

## 6. What this optimization is explicitly *not* allowed to smuggle in

* it does **not** use `sup_e E[tau|e] = E[tau|0]`, which `p5_nonlinear_dynamics/LIMITATIONS.md` §3 records as **open**;
* it does **not** use any P5 or P7 empirical monotonicity of `A(e)`;
* it does **not** use monotonicity of the *two-sided* alarm time in `e`, which is the unproved statement recorded as `DEFECT_REGISTER.md` `D3`;
* the only monotonicity it uses is `M1` (in the starting state) and `M2` (in the drift, for a **one-sided** random walk with stochastically ordered increments) — both proved from scratch in `PROOF.md`, both elementary coupling arguments about a one-dimensional walk.

`drift_minorant.py` records `empirical_monotonicity_used: false` in every
artifact it emits, and a test asserts it.
