# P6 theory targets

Candidate theorems for the full campaign. **None is proved here**; §7 records
the one small feasibility lemma that was worth writing down, and even that is
elementary.

For each target: the statement, what it would buy, and — the point of the
exercise — **exactly which `PROVISIONAL_P5` rows it needs**, so that
`P5_ADJUDICATION_CONTINGENCIES.md` can retire the unreachable ones on the day
Codex reports.

Notation as in `SAFETY_OBJECTIVES.md` §1. `U` is a policy;
`Fcal_j` is the observable sigma-field at the alarm ending cycle `j`
(`OBSERVABILITY_AUDIT.md` §2).

---

## T6-A. One-step reference-risk bound under a controlled reuse rule

> **Target.** For any policy `U` measurable w.r.t. `Fcal_j` and taking values in
> `[0, rho_max] x M x K`,
> ```
> E[ e_{j+1}^2 | Fcal_j ]  <=  rho_max^2 ( R_{m}(e_j)^2 + S_{m}(e_j) )  +  (1 - rho_j)^2 / k_j
> ```
> and, uniformly in the state,
> ```
> sup_e  E[ e_{j+1}^2 | e_j = e, u ]  <=  rho^2 C_D  +  (1-rho)^2 / k .
> ```

**Buys.** The feasibility statement for `OPTIMIZATION_FORMULATIONS.md` C: a
controlled reuse rule cannot make the one-step second moment worse than an
explicit, state-independent quantity. It also legitimises the greedy rule of
Family F by exhibiting what that rule is minimising.

**P5 dependence.** The conditional form needs `P3` (T2). The uniform form needs
`P4` (T5) — **and inherits its vacuous constants** (`C_CUSUM <= 9.9e8` against a
measured `sup_e A(e) ~ 465`, `P5/LIMITATIONS.md` §3). A version with realistic
constants requires the hypothesis `sup_e E[tau|e] = E[tau|0]`, which P5 states
and does **not** claim.

**Difficulty.** Low, conditional on P5. This is the cheapest target and the one
most likely to be *just algebra*.

**Honest limit.** A one-step bound on a Tier-3 latent quantity. `S18` forbids
converting it into a monitoring guarantee. On its own it is not a P6 result.

## T6-B. Sufficient condition for a bounded stationary second moment under a state-dependent controller

> **Target.** Give conditions on the policy class `Ucal` under which the
> **closed-loop** chain `(e_j)` under `U` admits a unique invariant law with
> finite second moment, and `E[e_j^2]` is bounded uniformly in `j`.

**Buys.** This is the theorem P6 most needs and the one `H7` makes necessary.
Under a state-dependent `U`, `(e_j)` is no longer the time-homogeneous chain of
`D9`, so P5's `T7` (`P1`) **does not transfer**. Without T6-B, no P6 statement
about a stationary quantity is well-posed, and every objective must be written
in finite-horizon form.

**Route.** The promising one does *not* go through Foster–Lyapunov. `P2` (T1)
gives a **state-independent** one-step moment bound, which is strictly stronger
than an outer-drift condition and survives an arbitrary `Fcal_j`-measurable
choice of `(rho_j, m_j, k_j)` in a compact set, because the bound is uniform in
those arguments. The remaining work is the minorisation: P5's two-step Doeblin
argument uses the `{tau = 1}` event, whose probability does not depend on the
policy's choice, so it plausibly extends to policy-dependent kernels on a
compact decision set. **That is a conjecture, not a proof.**

**P5 dependence.** Heavy: `P2`, `P4`, and the *architecture* of `P1`. Under
Branch C, T6-B is out of reach and P6 must run entirely in finite-horizon terms.

**Difficulty.** Medium-high. This is the target worth the most and costing the
most.

## T6-C. Monotonicity / dominance: fresh injection vs full reuse

> **Target.** Show that increasing the fresh count `k` (at fixed `rho < 1`, `m`)
> strictly decreases the one-step conditional second moment, and identify
> conditions under which the effect is monotone through to the stationary law
> and to `Arl0`.

**Buys.** A directional guarantee — "more fresh information never hurts the
reference" — which is the sort of statement an operator can act on, and the
formal backing for Family C.

**Route.** The one-step half is immediate from the explicit
`Q(rho; e, m, k) = rho^2 (R^2 + S) + (1-rho)^2/k`, decreasing in `k` for
`rho < 1`. The *stationary* half is the hard part and requires a stochastic
monotonicity or coupling argument that the frozen chain may simply not admit —
`R` is non-monotone (it has a secondary lobe near `|e| ~ 5.5..7`, `p5/LIMITATIONS.md`
§6), which is exactly the sort of feature that breaks coupling arguments.

**P5 dependence.** One-step half: `P3`. Stationary half: `P1` plus T6-B.

**Difficulty.** One-step: trivial. Stationary: high, possibly false.

**Honest note.** Even the full result would say nothing about `Dtail`. And it
does not imply "more fresh is better" *operationally*, because fresh samples
cost downtime (`H5`) — the trade-off is the point.

## T6-D. Guaranteed upper bound on a tail probability

> **Target.** For a controlled rule, an explicit bound of the form
> ```
> P( |e_{j+1}| > c | Fcal_j )  <=  B( c, u_j, Fcal_j )
> ```
> with `B` computable from observables, so that a policy can *enforce* a tail
> constraint rather than merely optimise a proxy.

**Buys.** The only route to a genuine *safety guarantee* rather than an
empirical improvement — and hence the strongest available candidate for
`METHOD_NOVELTY_SEPARATION.md`'s "theorem-backed safety guarantee" criterion.

**Routes, in increasing sharpness.**
1. Chebyshev on T6-A: `B = (rho^2(R^2+S) + (1-rho)^2/k) / c^2`. Immediate, and
   probably far too loose to be useful at the `c ~ 0.16` scale that matters.
2. A sub-Gaussian bound on `Rbar` via `P2`: `Rbar` is a mean of at most `m` iid
   standard normals, but with a **randomly selected, stopping-time-dependent**
   index set, so the naive `N(0, 1/w)` bound is invalid. The correct route needs
   a bound on the selection effect, e.g. through `P(tau = t | e)`.
3. Exact numerical evaluation of the one-step law from the precomputed frozen
   tables (`F21`) — not a theorem, but a *certified numerical* bound, which is
   the rank-3/4 outcome most likely to be achievable.

**P5 dependence.** `P2`/`P3`. Route 3 is the only one that survives Branch C,
where P6 would have to estimate the one-step law itself.

**Difficulty.** Route 1 low and probably useless; route 2 high; route 3 medium
and most promising.

## T6-E. Pareto statement linking sample reuse to monitoring risk

> **Target.** Establish that a genuine trade-off exists — that no policy in
> `Ucal` simultaneously attains the minimum of `Fresh` and the minimum of the
> monitoring risk — and characterise the frontier's endpoints.

**Buys.** Justifies `OPTIMIZATION_FORMULATIONS.md` E as *the* scientific output
rather than as an evasion of choosing a winner. The endpoints are already
suggestive: `rho = 1` costs zero fresh samples (`H5`) and is the worst monitoring
case (`S3`, `S5`, `S8`); `rho = 0` costs the most and is still `65%..83%` below
nominal (`S4`). A theorem that the frontier between them is non-degenerate would
be the cleanest structural statement P6 could make.

**P5 dependence.** The *existence* claim is mostly empirical and needs none. A
*characterisation* would need T6-B.

**Difficulty.** Medium. The likely honest outcome is a partial result: a proof
that the two endpoints are not comparable, plus a measured frontier.

---

## Cross-cutting: what would need to be re-proved, not inherited

| inherited statement | why it does **not** transfer to a state-dependent policy |
|---|---|
| `D9` time-homogeneity | the kernel depends on `Fcal_j` through `u_j` |
| `P1` (T7) unique `pi`, uniform ergodicity, all moments | proved for **fixed** `(D, m, rho)`; T6-B is exactly the request to extend it |
| `P6` (T11) `ACF1 = rho(1 - Gamma_eff)` | assumes a scalar `rho`; meaningless when `rho_j` is random |
| `S16`/`S17` (P7-B/C/D) | conditional on the same fixed-policy stationary law |
| `P7`/`P8` (the `rho*` optimum and RMS/ARL co-optimality) | properties of the fixed-`rho` family; a state-dependent policy is not in that family |

`S1` (P7-A) is the exception and the reason P6 is tractable at all: it is a
**per-cycle conditional** statement — given `e_j`, the cycle is a fresh cycle at
innovation mean `-e_j` — and it therefore holds under *any* policy, adaptive or
not, since the policy acts only between cycles. Every P6 objective is built on
`S1` for exactly this reason.

## 7. The one feasibility lemma worth stating now

**Lemma (greedy one-step reuse weight).** Under `P2`/`P3` (T1/T2), for fixed
`(e, m, k)` the one-step second moment
`Q(rho) = rho^2 (R_m(e)^2 + S_m(e)) + (1-rho)^2/k` is strictly convex in `rho`
and minimised at

```
rho_opt(e, m, k)  =  ( 1/k ) / ( R_m(e)^2 + S_m(e) + 1/k )   in  (0, 1) ,
```

an inverse-variance weighting between the reused estimate and the fresh
baseline.

*Proof.* `Q'(rho) = 2 rho (R^2+S) - 2(1-rho)/k`, `Q''= 2(R^2+S+1/k) > 0`; set
`Q' = 0`. Since `R^2 + S > 0` and `1/k > 0`, the root lies strictly between `0`
and `1`. ∎

Three observations, all of which matter for the design and none of which is a
P6 result:

1. **It never recommends full reuse.** `rho_opt < 1` strictly, for every state,
   every `m` and every `k`. Full reuse is one-step-inadmissible under a
   second-moment objective.
2. **It never recommends zero reuse either**, so the interior operating region
   that `S12` observed empirically and `P7` observed provisionally is at least
   *consistent* with a first-principles rule. That is a consistency remark, not
   a derivation of `rho*`.
3. **It depends on the state only through `R^2 + S`**, an even function, so the
   implementable version needs `|ehat_j|` and not its sign — which makes `tau_j`
   (sign-blind, `OBSERVABILITY_AUDIT.md` §3.2) a sufficient sensor for *this*
   rule, a genuinely convenient fact.

This lemma is elementary and is recorded only to show Family F is well-posed.
It is **conditional on P5** and carries no closure weight.
