# What "safe" means in P6

P6 is the first ReBaseGuard campaign that will *recommend* an action. A vague
notion of safety is therefore not merely sloppy, it is the mechanism by which a
prescriptive campaign produces a harmful recommendation. This document fixes the
candidate definitions, their estimators, and — most importantly — the **role**
each one is allowed to play.

Every quantitative claim cites a `DEPENDENCY_LEDGER.md` row id.

---

## 1. Notation

A **policy** `U` chooses, at the alarm ending cycle `j`, a decision

```
u_j = ( rho_j , m_j , k_j )     from observables available at that instant
```

and the frozen reference update (`D6`) is generalised in **exactly one line**:

```
e_{j+1} = rho_j * ( e_j + zbar_j ) + (1 - rho_j) * fresh_j ,
zbar_j  = (1/w_j) sum_{r<w_j} z_{tau_j - r} ,     w_j = min(m_j, tau_j) ,
fresh_j ~ N(0, 1/k_j)  independent of the cycle.
```

`k_j = m_j` recovers the frozen model exactly. Nothing else changes: detector
recurrences, thresholds, reset, stopping rule, inclusive test and the
convention-A truncated denominator are all frozen (`D1`–`D7`, `X4`).

Write `J` for the number of post-burn-in cycles in a replicate, `r = 1..n_rep`
for the replicate index (the statistical unit throughout, `EVALUATION_PROTOCOL.md`
§6), and `A(.)` for P7's frozen response function (`S2`).

## 2. What "safe" may **not** mean

| forbidden definition | why | ledger |
|---|---|---|
| `rho < rho_c`, or any monotone function of `rho/rho_c` | pre-committed boundary test returned `LOCAL-MATHEMATICAL, NOT OPERATIONAL`; and the measured ARL optimum sits `1.25x..4.1x` above `rho_c` | `X1` (`S11`, `S12`) |
| "keeps the reference chain off the bifurcated branch" | the orbit is not the harm | `X2` |
| "recovers the nominal `ARL_0 ~ 465`" | no cell in P7's entire grid reaches within a factor of 4 of nominal, and fresh-only itself loses `65%..83%` | `S20`, `S4`, `X12` |
| "reduces mean detection delay" **alone** | the failure mode is a right tail: at CUSUM `m=1, rho=1, Delta=1` the *median* delay (`7`) is **better** than nominal (`10.35`) while `q95 = 275` and `P(delay>100) = 11.4%` | `S9` |
| "reduces `E_pi[e^2]`" **alone** | P7 states explicitly that reducing the second moment is *not proved* to improve every metric, and P7-E — the transfer theorem that would have licensed the inference — was **rejected** | `S18`, `X6` |
| anything defined only on cycle 1 | the cycle *after* the first re-baselining collapses by `98%` | `S8` |

The last two rows are the ones a careless P6 would violate. They are the reason
§4 exists as a separate tier from §3.

## 3. Candidate objectives

### 3.1 Reference-state objectives (the latent layer)

All are functionals of the law of the entering reference error `e`. They are
**legitimate targets** because of `S1` (P7-A, exact): conditionally on `e_j` the
cycle is a fresh cycle at innovation mean `-e_j`, so every first-moment
monitoring consequence is a functional of the law of `e` alone.

| id | metric | per-replicate estimator | notes |
|---|---|---|---|
| `Rms` | `sqrt(E[e^2])` | `sqrt( (1/J) sum_j e_j^2 )` | the P5 headline coordinate (`P7`, provisional) |
| `Mad` | `E|e|` | `(1/J) sum_j |e_j|` | more robust to the platykurtic bulk (`P13`) |
| `M2` | `E[e^2]` | `(1/J) sum_j e_j^2` | the `Rms` square; report one, not both |
| `Tail(c)` | `P(|e| > c)` | `(1/J) sum_j 1{|e_j| > c}` | `c in {0.2, 0.5, 1.0}` preregistered |
| `Q95e` | `q95(|e|)` | empirical 95th percentile over `J` | |
| `OutCal(beta)` | mass outside the **ARL-calibrated tolerance region** | `(1/J) sum_j 1{ |e_j| > c_beta }` | see below |

> **The ARL-calibrated tolerance radius.** Define, from the *closed* response
> function `S2` alone,
> ```
> c_beta := sup{ c >= 0 : A(c) >= beta * A(0) } .
> ```
> `c_beta` is the largest reference error whose *conditional* in-control ARL
> still retains a fraction `beta` of nominal. From `S2` (`A(0)=465`,
> `A(0.1)=348`, `A(0.2)=191`), `c_{0.75} ~ 0.09` and `c_{0.5} ~ 0.16`.
> `OutCal(beta) = P(|e| > c_beta)` is then a reference-state metric with a
> **monitoring** meaning attached by an exact theorem rather than by analogy.
> It is P6's preferred reference-state tail metric for exactly that reason.
> The numerical `c_beta` must be re-derived from `p7/results/response_curves.json`
> at campaign start with an interpolation error budget; the values above are
> indicative (`E1`-adjacent, not a design constant).

**Warning attached to this whole subsection.** A reference-state metric is a
*surrogate*. `S18` forbids inferring a monitoring improvement from a
reference-state improvement by any first-order argument. Surrogates may be
optimised; the monitoring metric must still be **measured**.

### 3.2 Monitoring objectives (the observable layer)

| id | metric | per-replicate estimator | notes |
|---|---|---|---|
| `Arl0` | in-control mean cycle length | `(1/J) sum_j tau_j` at `Delta = 0` | the P7 headline (`S3`, `S4`) |
| `Fap(H)` | `P(at least one alarm within H in-control observations)` from the start of a post-burn-in cycle | fraction of post-burn-in cycles with `tau_j <= H` | `H = 100` matches `S7` |
| `Rate` | alarms per `1000` in-control observations | `1000 / Arl0` | reporting form of `Arl0` |
| `Dmean` | `E[delay | Delta]` | mean over shifted cycles | `S5` |
| `Dmed` | `median(delay)` | | **must be reported beside `Dmean`** (`S9`) |
| `Dq95` | `q95(delay)` | | tail |
| `Dtail(L)` | `P(delay > L)` | | `L in {50, 100}` preregistered; `L=100` matches `S9` |
| `Rdelta` | `E[tau_Delta] / E[tau_0]` | ratio of the two above | discrimination; `>= 1` means the shifted cycle is *longer* than in-control (`S6`) |
| `Coll` | post-first-rebaseline collapse ratio `E[tau_2]/E[tau_1]` | finite-cycle, no burn-in | `S8`; the one-cycle-hiding-later-cycles guard |

`Dtail(L)` and `Dq95` are the metrics `S9` exists to force into the design. A
P6 method that does not report them is not evaluable.

### 3.3 Resource / utility objectives (the cost layer)

Re-baselining is done to *save data*. A policy that reduces risk by spending
unlimited fresh samples has solved nothing — it has reinvented "never reuse",
which `S4`/`X12` already show is itself unsafe.

| id | metric | per-replicate estimator | notes |
|---|---|---|---|
| `Reuse` | reused observations per alarm | `(1/J) sum_j w_j`, `w_j = min(m_j, tau_j)` | |
| `Fresh` | fresh observations per alarm | `(1/J) sum_j k_j * 1{rho_j < 1}` | see the cost model below |
| `FracReuse` | sample-count reuse fraction | `E[ w_j / (w_j + k_j 1{rho_j<1}) ]` | **distinct from the algebraic weight `rho_j`** |
| `Wbar` | mean algebraic reuse weight | `(1/J) sum_j rho_j` | reporting only; not a cost |
| `Down` | unmonitored post-alarm observations per alarm | `= Fresh` under the default model | the *operational* cost |
| `Eff` | fresh observations per unit of in-control ARL retained | `Fresh / Arl0` | efficiency summary |

> **The fresh-sample cost model is a P6 design decision (`H5`), not an inherited
> fact.** In the frozen model `fresh_j` is drawn after the alarm and carries
> weight `(1 - rho_j)`; at `rho_j = 1` it has zero weight and *no fresh sample
> need be collected at all*. So sample cost is `k_j * 1{rho_j < 1}`, and **full
> reuse is free in samples**. That asymmetry is precisely the tension P6 exists
> to resolve, and P5/P7 never modelled it. Two sub-decisions must be
> preregistered at the entry gate:
>
> * **(C-a)** Is the fresh-collection window *monitored* or *blind*? If blind, a
>   shift arriving during it is missed entirely and `Down` becomes a genuine
>   risk term, not just a cost term. Default proposal: **blind**, because that
>   is the conservative reading and because it makes `Fresh` a risk as well as a
>   cost, preventing the degenerate "spend fresh samples freely" solution.
> * **(C-b)** Is the cost step-shaped (`k_j 1{rho_j<1}`) or proportional
>   (`(1-rho_j) k_j`)? Default proposal: **step-shaped**, because it matches the
>   frozen model literally. The proportional variant should be run as a
>   sensitivity, not as the primary.

## 4. Role assignment: constraint, objective, or report

This is the part that keeps P6 honest. Every metric above is assigned exactly
one role, **before** any data are seen.

### Tier 0 — invariants (not metrics; violation voids the run)

| # | invariant | enforcement |
|---|---|---|
| I1 | Frozen detector semantics unchanged (`D1`–`D7`) | correspondence test: a constant policy must reproduce `p7.chain.simulate_chain` with **bit-identical `tau`** |
| I2 | No implementable policy reads latent `e_j` (`X11`) | structural: the observation object handed to an implementable policy has no such field; asserted by test |
| I3 | No policy reads post-change information before it exists, and no policy reads `Delta` | structural + test |
| I4 | Convention A preserved (`X4`) | test |
| I5 | Tuning seeds disjoint from evaluation seeds | seed-derivation utility; asserted by test |

### Tier 1 — hard safety constraints (candidates; **one set** chosen at the gate)

A constraint must be (i) monitoring-level, not surrogate, and (ii) stated
against a **named control**, never against an absolute aspiration (`S20`, `E1`).

| id | candidate constraint | control | rationale |
|---|---|---|---|
| `K1` | `Arl0(U) >= Arl0(fixed-rho best-in-grid at the same mean `Fresh`)` | matched-cost fixed-`rho` | the honest "do no harm on false alarms" constraint |
| `K2` | `Dtail(100) <= Dtail(100)` of full reuse, with the paired CI excluding 0 | `rho = 1` | the `S9` tail constraint |
| `K3` | `Coll >= ` a preregistered floor | — | forbids the `S8` finite-cycle collapse |
| `K4` | `Fresh(U) <= Fresh(fresh-only)` | `B0` | forbids the degenerate solution |

**Recommended default constraint set: `{K1, K4}` as hard constraints, `K2` as
the primary objective (below), `K3` as a reported gate.** Rationale: `K1` and
`K4` are the two ways a policy can cheat, so they belong in the feasible-set
definition; `K2` is the thing P6 is actually trying to improve, so it belongs in
the objective, not the constraint. Awaiting approval at
`FULL_CAMPAIGN_ENTRY_GATE.md` item 4.

### Tier 2 — primary objective (candidates; **exactly one** chosen at the gate)

| id | candidate primary objective | argument for | argument against |
|---|---|---|---|
| `O1` | minimise `Dtail(L)` (or `Dq95`) at a preregistered `Delta`, subject to Tier 1 | directly targets the closed failure mechanism `S9`/`S10`; cannot be gamed by mean-shifting | needs many tail events, so it is the most expensive to estimate (`COMPUTE_PLAN.md` §5); depends on the choice of `Delta` |
| `O2` | minimise `OutCal(beta)` subject to Tier 1 | cheap to estimate, low variance, and given meaning by the *exact* `S1` rather than by analogy | a surrogate — `S18` forbids concluding a monitoring gain from it |
| `O3` | maximise `Arl0` subject to Tier 1 | the P7 headline coordinate, directly comparable to `S3`/`S4` | `S9` shows in-control performance can look fine while the delay tail is the real damage |
| `O4` | composite `w1 * normalised Dtail + w2 * normalised OutCal + w3 * normalised Fresh` | expresses the real trade-off in one number | the weights are unjustifiable from anything closed; invites post-hoc tuning |
| `O5` | Pareto frontier over (`Dtail`, `Fresh`) with `Arl0` as a constraint | makes no arbitrary trade-off, and is the honest scientific output | no single "winner", which is *fine* — P6 need not produce one |

**Recommendation: `O1` as the primary, with `O5` as the reported scientific
output and `O2` as a declared, separately-reported surrogate.** The reasoning is
that `S9` is the strongest closed statement P7 hands over about *where the
damage is*, and it is a tail statement; and that `O5` protects P6 from the
"selected a winner" failure mode (`FAILURE_MODE_REGISTER.md` F7). `O4` is
explicitly **not** recommended.

### Tier 3 — reporting only (never optimised, never a gate)

`Rms`, `M2`, `Mad`, `Q95e`, `Tail(c)`, `Dmean`, `Dmed`, `Rate`, `Fap(H)`,
`Rdelta`, `Wbar`, `FracReuse`, `Eff`, and every P5-derived diagnostic
(`ACF1`, alternation rate, bimodality contrast, `Gamma_eff`). Diagnostics of how
much reuse is in effect are *not* safety metrics: `ACF1` and the alternation
rate are monotone in `rho` straight through the optimum and so cannot
distinguish a good operating point from a bad one (`P5`'s own §4 warning).

`rho_c` appears in Tier 3 **only** as an axis annotation on figures. It is never
a constraint, never an objective, never a threshold (`X1`).

## 5. The three-layer discipline, stated once

```
   cost layer          Fresh, Down          <- what the operator pays
   observable layer    Arl0, Dtail, Coll    <- what P6 must MEASURE and gate on
   latent layer        e-law functionals    <- what P6 may OPTIMISE as a surrogate
```

Optimising downward is allowed. Concluding upward is not (`S18`, `X6`). Any P6
sentence of the form "the policy reduces reference dispersion, therefore it
improves monitoring" is a defect, and `FAILURE_MODE_REGISTER.md` F2 exists to
catch it.
