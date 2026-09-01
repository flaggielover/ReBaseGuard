# P6 method candidates — baselines, families, oracles

**No winner is selected here, and none may be selected before the entry gate.**
This document defines the *space* P6 will search and the *ceiling* it will
measure against. Every policy is specified precisely enough to implement, and
every policy is labelled `implementable` / `oracle` / `diagnostic` per
`OBSERVABILITY_AUDIT.md` §7.

Decision variables, per `SAFETY_OBJECTIVES.md` §1:

```
u_j = ( rho_j in [0,1] ,  m_j in {1,2,3,5,...} ,  k_j >= 1 )
```

with `k_j = m_j` recovering the frozen model. Only the reference-update line
changes; the detector is frozen (`I1`).

---

## 1. Baseline family (frozen at the entry gate, then never changed)

| id | policy | `rho_j` | `m_j` | `k_j` | class | why it is in the set |
|---|---|---|---|---|---|---|
| `B0` | **fresh-only** | `0` | `m` | `m` | implementable | the "no reuse" reference. Note it is **not** a safe control: it already loses `65%..83%` of nominal ARL (`S4`, `X12`) |
| `B1` | fixed `rho = 0` at the campaign `m` | `0` | `m` | `m` | implementable | identical to `B0` in the frozen cost model; kept as a named row so tables match P7's "fresh" column (`S3`) |
| `B2` | **fixed-`rho` grid** | `rho in {0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.75, 1.0}` | `m` | `m` | implementable | the incumbent method. The grid **must** resolve `[0.10, 0.35]` because the ARL optimum lies there (`E2`, `S12`) |
| `B3` | **full reuse** `rho = 1` | `1` | `m` | — | implementable | the worst closed case (`S3`, `S5`, `S8`) and the *cheapest* in samples — the honest opponent |
| `B4` | fixed `m` sweep at fixed `rho` | `rho` fixed | `m in {1,2,3,5,8}` | `m` | implementable | isolates the `m` axis; `m=8` extends past P5's measured range (`P9`) |
| `B5` | **simple adaptive `m`** | `rho` fixed | `m_j = clip(ceil(c / max(tau_j, 1)) , 1, m_max)` or `m_j = m_lo` if `tau_j` short else `m_hi` | `m_j` | implementable | uses only `F01`; the cheapest possible adaptivity |
| `B6` | **simple state-dependent `rho` heuristic** | `rho_j = rho_hi` if `|zbar_j| <= q` else `rho_lo` | `m` | `m` | implementable | uses only `F08`; a two-level threshold rule, the null against which Family A must prove itself |

Additional heuristic baselines, included because the task specifies them and
because each isolates a distinct mechanism:

| id | policy | mechanism isolated |
|---|---|---|
| `B7` | `rho_j` from **alarm severity**: `rho_j = phi(overshoot_j)` (higher overshoot -> lower reuse) | `F04` alone |
| `B8` | `rho_j` from **terminal-window dispersion**: `rho_j = phi(sample var of the window)` | `F07` alone; expected to be near-useless, and that is a useful negative |
| `B9` | **fresh-sample injection**: `rho` fixed, `k_j = k > m` | decouples `k` from `m` (`H4`) |
| `B10` | **capped reuse**: `rho_j = min(rho, rho_cap)` with an additional cap on consecutive high-reuse cycles | limits compounding |
| `B11` | **confidence-triggered reuse**: reuse only when a preregistered confidence statistic on `|ehat_j|` is below a threshold, else `rho_j = 0` | a gate, not a dial |

`B7`–`B11` are *heuristics*, not method families: they have no derivation. Their
role is to make the Family A–F methods prove they are worth their complexity
(`METHOD_NOVELTY_SEPARATION.md`).

## 2. Method families

Six families, deliberately overlapping in control variable and differing in
*principle*. No family is preferred here.

### Family A — dispersion-aware reuse

**Principle.** Estimate a reference-risk proxy `risk_j` and reduce reuse when
the predicted reference dispersion is high.

**Control.** `rho_j = phi(risk_j)` or `m_j = psi(risk_j)`, `phi` monotone
decreasing, parameterised by 2–3 scalars.

**Risk proxy candidates (all implementable):**
`|zbar_j|`; an EWMA of `|zbar_i|`; `1/tau_j`; a plug-in `V-hat = rho^2 S(ehat_j)
+ (1-rho)^2/k` using the `S` table (`F21`) at the *estimated* `ehat_j`.

**Depends on P5?** The *motivation* does (`P11`: `S(e)` varies ~8x). The
*method* does not — `phi` is fitted, and the plug-in variant degrades to `B6`
if the `S` table is not trusted. **Survives all branches.**

**Honest weakness.** Reducing predicted dispersion is a Tier-3/latent-layer
move; `S18` forbids concluding a monitoring gain from it. Family A must be
gated on `Arl0` and `Dtail`, measured.

### Family B — tail-risk-aware reuse

**Principle.** Target the *tail*, not the mean: control `P(|e_{j+1}| > c)` or a
delay-tail surrogate, because the closed failure mode is a tail (`S9`, `S10`).

**Control.** Choose `u_j` to minimise a one-step tail proxy

```
That-j(u)  :=  Phat( |e_{j+1}| > c_beta  |  observables_j , u )
```

evaluated by plugging the *posterior* over `e_j` (§Family E) into the frozen
one-step law. With `c_beta` the ARL-calibrated radius
(`SAFETY_OBJECTIVES.md` §3.1).

**Depends on P5?** The exact one-step conditional law comes from `P2`/`P3`
(T1/T2). Under Branch C the same family survives with an *empirical* one-step
law estimated by P6 itself from the frozen simulator — more expensive, same
method. **Survives all branches, at different cost.**

**Honest weakness.** A one-step tail bound does not control the *stationary*
tail; the recursion can accumulate. That gap is theory target `T6-B`.

### Family C — fresh-sample injection

**Principle.** Reuse the terminal window but guarantee a floor of fresh
post-alarm information. This is the family that makes the cost model bite.

**Control.** `(k_fresh, rho, m)` with `k_j >= k_min > 0` whenever `rho_j < 1`;
variants: constant `k`, `k` increasing after consecutive high-reuse cycles,
`k` triggered by `ehat_j`.

**Key design point (`H4`).** In the frozen model `k = m`, which conflates two
different quantities: how many *past* observations are reused and how many
*new* ones are collected. Decoupling them is the smallest generalisation that
creates a genuine trade-off surface, and it is the one P5/P7 never explored.

**Depends on P5?** No. **Survives all branches.**

**Honest weakness.** It is close to "spend more samples", so it must be
compared at **matched `Fresh`**, never at matched `rho` (`K4`, `F3`).

### Family D — hybrid robust reference update

**Principle.** Combine reused and fresh information through shrinkage,
clipping, a robust window mean, or confidence weighting, instead of the frozen
convex combination.

**Control.** Replace `rho_j zbar_j + (1-rho_j) fresh_j` by e.g.
`rho_j clip(zbar_j, -c, c) + (1-rho_j) fresh_j`, or an inverse-variance weighting
`w_j = (1/S-hat) / (1/S-hat + k_j)`.

**Scope discipline.** Robustness to *non-Gaussian innovations* is **P8**
(`X5`). Family D stays inside the frozen Gaussian core: clipping and shrinkage
here are variance-control devices, not contamination defences, and must be
described as such.

**Depends on P5?** No. **Survives all branches.**

**Honest weakness.** Clipping `zbar` breaks the raw-mean identity's clean
factorisation (`P3`), so Family D forfeits the analytic route of Family F. It
also risks a *systematic* bias: clipping a symmetric variable is unbiased, but
clipping conditionally on an asymmetric selection effect is not. Must be
checked, not assumed.

### Family E — state-dependent policy from a filtered estimate

**Principle.** Build the best implementable estimate of the latent error and
condition everything on it. This is the family that exploits
`OBSERVABILITY_AUDIT.md` §3–§4.

**Estimator (`H1`, `H3`, `DESIGN_HYPOTHESIS`).** Using the exact increment
observability of `F09`/`F10`, all readings align on the single unknown `e_0`:

```
ehat_j  =  argmax_{e0}  sum_{i = j-n+1}^{j}  log L( tau_i , zbar_i ;  e0 + d_i )   +  log N(e0; 0, 1/m_0)
```

with `L` the frozen joint law of `(tau, zbar)` given the entering error,
precomputed offline (`F21`). A cheap first-order version is the bias-corrected
pooled readout of `OBSERVABILITY_AUDIT.md` §4.

**Control.** `rho_j = phi(ehat_j, precision_j)`, `m_j = psi(.)`, `k_j = chi(.)`;
crucially the policy can use its own *precision*, reusing more when it is
confident the reference is good and less when it is not.

**Depends on P5?** The likelihood table is a property of the frozen model that
P6 computes itself, not a P5 result. **Survives all branches.**

**Honest weaknesses, stated up front.**
* The filter assumes `theta` constant. Under a shift it is misspecified
  (`OBSERVABILITY_AUDIT.md` §4). Must be evaluated at `Delta > 0`.
* Per-cycle `SNR ~ 0.3` (§3.1 there) — pooling helps but the estimate is never
  sharp on the scale that matters (`E1`).
* Feedback: the policy's own past decisions shape `d_j`, so the filter is
  operating on a closed loop it is itself driving. This is where `H7` bites
  hardest.

### Family F — one-step risk control (conditional on P5)

**Principle.** Use the exact conditional law of `e_{j+1}` to choose `u_j`
optimally in one step.

Under `P2`/`P3` (T1/T2),

```
E[e_{j+1} | e_j = e, u] = rho R_m(e) ,
Var(e_{j+1} | e_j = e, u) = rho^2 S_m(e) + (1-rho)^2 / k ,
```

so the one-step second moment is the explicit quadratic

```
Q(rho; e, m, k)  =  rho^2 ( R_m(e)^2 + S_m(e) )  +  (1-rho)^2 / k
```

minimised at

```
rho_opt(e, m, k)  =  ( 1/k ) / ( R_m(e)^2 + S_m(e) + 1/k ) .
```

This is an inverse-variance weighting between the reused estimate and the fresh
baseline, which is both interpretable and, notably, **bounded away from `1`** —
it never recommends full reuse — and depends on `e` only through
`R_m(e)^2 + S_m(e)`, an even function. The implementable version substitutes
`ehat_j` from Family E, giving `Family E x F`.

> **This family is CONDITIONAL on P5 adjudication** (`P2`, `P3`). Under Branch C
> it does not disappear: the same rule is recoverable with `R^2 + S` replaced by
> an empirically estimated conditional second moment of `zbar` — but then it is
> an empirical rule, not a derived one, and the novelty claim weakens
> accordingly.
>
> **It also must not be over-sold.** `rho_opt` minimises the *one-step* second
> moment, which is a Tier-3 latent-layer quantity. Greedy one-step optimality
> is not stationary optimality (there is no reason the myopic rule is optimal
> for `E_pi[e^2]`, let alone for `Dtail`), and `S18` forbids the transfer. Its
> real value is as a **principled starting point** and as the object of theory
> targets `T6-A`/`T6-C`.

## 3. What is deliberately excluded

| excluded | why |
|---|---|
| any controller of the form `rho_j = c * rho_c` | `X1` |
| policies designed to suppress the period-2 orbit | `X2` |
| non-Gaussian robustness, contamination defence, alternative detectors | `X5` (P8) |
| changing the window convention, denominator or terminal-increment rule | `X4` |
| policies that alter detector thresholds, add a minimum dwell, or use a head start | `I1`; these change the monitoring semantics and would make the comparison with P7 meaningless |
| policies that read `Delta` | `F18` — oracle only |

The fifth row is worth a sentence: **adjusting `h` or `A` post-alarm is a
perfectly reasonable engineering idea and is explicitly out of P6's scope**,
because P6's entire comparability with the closed P7 numbers rests on the
detector being byte-identical. It belongs in a successor campaign.

## 4. Oracle benchmarks (never deployable; ceilings only)

Oracles answer the question *"how much is adaptive control worth at all?"* If
the oracle ceiling is close to the best fixed `rho`, P6's honest conclusion is
that adaptive re-baselining is not worth building — and that is a publishable
result.

| id | oracle | reads | ceiling it establishes |
|---|---|---|---|
| `Z1` | **one-step MSE oracle**: `rho_j = argmin_rho E[e_{j+1}^2 | e_j]` using the true `e_j` | `F14` | the value of perfect state knowledge under a myopic objective |
| `Z2` | **one-step tail oracle**: `u_j = argmin_u P(|e_{j+1}| > c_beta | e_j)` | `F14` | as `Z1` but for the tail objective `O1`/`O2` |
| `Z3` | **oracle reset**: `rho_j = 0, k_j = k_max` iff `|e_j| > c`, else `rho_j = 1` | `F14` | the value of a perfect *trigger* — the cheapest possible use of state knowledge |
| `Z4` | **shift-aware oracle**: knows `Delta` and minimises `P(delay > L)` directly | `F18` | the ceiling for the blind-spot mechanism `S10`; quantifies exactly how much `H8` costs |
| `Z5` | **stationary-law oracle**: picks the single fixed `rho` minimising the true stationary objective, computed offline | `F20` | the best *non-adaptive* policy — the bar any adaptive method must clear |
| `Z6` | **clairvoyant oracle**: chooses `u_j` knowing the realised `e_{j+1}` and `tau_{j+1}` | `F17`, `F19` | a loose upper bound; useful mainly to show `Z1`–`Z3` are not already saturated |

**`Z5` is the most important row in this table.** The interesting comparison is
not "adaptive beats full reuse" — `B3` is a straw man — but "adaptive beats the
*best fixed* `rho` at matched sample cost". `Z5` defines that bar exactly, and
`B2` estimates it.

## 5. Search-space discipline

* Each family is parameterised by **at most 3** scalars. Anything richer invites
  overfitting on a small screening budget (`F6`, `F8`).
* Parameters are fitted on a **tuning seed family** and never re-touched on the
  evaluation seed family (`I5`).
* A family is carried forward only if it beats the *matched-cost* fixed-`rho`
  baseline `B2*` — not `B3` — on the preregistered primary objective.
* Every family must be run on **both** detectors and at least three `m` values
  before any claim (`S13` licenses the expectation of transfer, not the claim).
