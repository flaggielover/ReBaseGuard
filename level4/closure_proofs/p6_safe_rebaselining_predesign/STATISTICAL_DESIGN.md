# P6 statistical design

Uncertainty plan for the full campaign. Nothing here is run now; the point is
that the plan is fixed *before* the numbers exist.

---

## 1. The statistical unit

The **independent replicate** — one complete simulated chain of `n_cycles`
cycles from its own seed. Never the cycle, never the alarm. This is P7's choice
and P6 keeps it so the two campaigns' intervals are comparable
(`p7/CLOSURE_REPORT.md` item 4).

Consequences:

* `n_rep` sets the precision; `n_cycles` sets the bias (burn-in) and the
  within-replicate autocorrelation, not the precision.
* Per-replicate summaries (`Arl0`, `Rms`, `Dtail`, …) are the data. The analysis
  is then ordinary iid inference across `r`, which is why the autocorrelation of
  §4 never enters the interval arithmetic.

## 2. Paired comparison and common random numbers

**Design.** Policy `U` and policy `U'` are run at the same cell with the same
per-replicate seeds, and the analysis is on `d_r = M_r(U) - M_r(U')`.

**What this buys and what it does not.** The pairing is *valid* regardless of
how strongly the two runs actually couple: `(M_r(U), M_r(U'))` are iid across
`r`, so the paired mean is unbiased and a paired bootstrap over `r` is correct.
What is uncertain is the *efficiency* gain, and here P6 must be honest:

> In this chain, common random numbers decouple almost immediately. The moment
> two policies choose a different `(rho_j, m_j, k_j)`, the reference moves
> differently, the next cycle's `z_t = raw_t - e_j` differs, `tau_{j+1}` differs,
> and the two runs consume the RNG stream at different rates. **CRN here is seed
> alignment, not path coupling.** Variance reduction should be *measured*
> (report the observed paired correlation per cell), never assumed.

**Preregistered consequence.** Power calculations use the **unpaired** variance
as the conservative default; any efficiency the pairing delivers is a bonus. A
campaign that sized its runs assuming strong CRN coupling would be underpowered
(`F5`).

**A stronger coupling scheme, if it is needed.** Pre-draw a per-`(replicate,
cycle)` substream so that every policy enters cycle `j` of replicate `r` with
the same innovation sequence, regardless of what happened earlier. This restores
coupling at the *cycle* level, at the cost of breaking bit-identity with the P7
stream (`X1` of `EVALUATION_PROTOCOL.md` §7 would then apply only to the
frozen-stream mode). Recommendation: implement it **only if** the measured
paired correlation at the shortlist stage is below `0.3`, and if implemented,
run it as a clearly-labelled second mode, never as the source of headline
numbers claimed to correspond to P7.

## 3. Intervals

| quantity | method |
|---|---|
| a single metric at a single cell | normal interval on the replicate mean **and** a BCa bootstrap over replicates; both reported, as P7 did (they agreed to within 2.9% of interval width there) |
| a paired policy difference | bootstrap over replicate *pairs*, `B = 10000` |
| a ratio (`Rdelta`, `Coll`, relative ARL loss) | bootstrap on the ratio directly, never a ratio of separately-bootstrapped means |
| a quantile (`Dq95`, `Q95e`) | bootstrap over replicates of the per-replicate quantile |
| a tail probability (`Dtail(L)`) | bootstrap over replicates; **plus** the effective-event check of §5 |

Verdict labels are P7's: `INCONCLUSIVE` (interval straddles zero),
`STATISTICALLY_RESOLVED` (excludes zero), `PRACTICALLY_MATERIAL` (excludes zero
*and* exceeds the preregistered materiality threshold). The materiality
threshold is a preregistration item (`PREREGISTRATION_OPTIONS.md`).

## 4. Autocorrelation within a replicate

Cycles within a replicate are dependent — negatively at lag 1 under reuse
(P5 measures `ACF1 < 0` for every `rho > 0`; `PROVISIONAL_P5`) and, under a
state-dependent policy, with an unknown structure (`H7`).

Handling:

* For anything reported as a *mean over cycles within a replicate*, the
  dependence is absorbed into the replicate summary and does not bias it. It
  only inflates the within-replicate variance, which affects nothing because the
  unit is the replicate.
* For any statement about the chain *itself* (mixing, burn-in adequacy, R3
  flatness), report the integrated autocorrelation time with batch means,
  batch length `>= 10 x` the estimated IACT, and state the estimate's own
  uncertainty. Do **not** import P5's IACT (`<= 1` cycle) — that is
  `PROVISIONAL_P5` and it was measured for *fixed* `rho`.
* Negative lag-1 autocorrelation makes a naive iid variance estimate
  **conservative**, not anti-conservative — worth stating, because it means the
  main risk here is wasted compute, not a false positive.

## 5. Tail metrics need enough events

`Dtail(100)` at its most interesting is around `0.11` (`S9`), but a successful
policy is one that *drives it down*, so the design must be sized for the small
value, not the large one.

Preregistered rule: **a tail estimate is reported only if the expected number of
tail events per arm exceeds `200`** (relative standard error `~7%` for a
binomial-like count; the true error is larger because of within-replicate
dependence, hence the margin). At a target `Dtail(100) ~ 0.02` this needs
`~10^4` shifted cycles per arm. Below that threshold the cell is reported as
`INSUFFICIENT_TAIL_EVENTS`, never as `INCONCLUSIVE` — the two mean different
things and conflating them hides a design failure.

Where the tail is too expensive at confirmation scale, the preregistered
fallback is `Dq95` (a quantile, which needs far fewer events) with `Dtail`
reported as supporting evidence only. That substitution must be declared before
the data are seen.

## 6. Pareto-frontier uncertainty

Naive non-dominance over noisy point estimates over-selects: with `P` policies
and pure noise, roughly `O(log P)` of them land on the empirical frontier.
Preregistered handling:

* Dominance is declared only when **every** coordinate difference is resolved at
  the paired-CI level (`OPTIMIZATION_FORMULATIONS.md` E).
* Report a **frontier-membership frequency** by bootstrapping replicates and
  recomputing the frontier: a policy on the frontier in `< 50%` of bootstrap
  resamples is reported as "not resolved as frontier".
* Baselines and oracles are always plotted, so the frontier's *shape* carries
  the message even when membership is uncertain.

## 7. Power and sizing heuristics (not a study)

Two-sided, `alpha = 0.05`, `80%` power, unpaired (the conservative default of
§2). With `cv = sd/mean` of the **per-replicate summary** and `delta` the
relative effect to resolve,

```
n_rep  ~  2 * (1.96 + 0.84)^2 * (cv / delta)^2   ~   15.7 * (cv / delta)^2 .
```

The `cv` values below are order-of-magnitude anticipations to be **measured in
the pilot**, not design constants.

| effect to resolve | anticipated `cv` | `delta` | `n_rep` |
|---|---|---|---|
| `Arl0`, `5%` change | `~0.07` at `n_cycles = 200` | `0.05` | `~ 31` |
| `Arl0`, `1%` change (P7-scale resolution) | `~0.07` | `0.01` | `~ 770` |
| `Rms`, `10%` change | `~0.05` | `0.10` | `~ 4` |
| `Dmean`, `20%` change | `~0.15` | `0.20` | `~ 9` |
| `Dq95`, `20%` change | `~0.20` | `0.20` | `~ 16` |
| `Dtail(100)`, `0.11 -> 0.08` | binomial-dominated | — | **set by §5's event rule, not by this formula** |

Two readings of this table matter more than the numbers in it.

1. **In-control and reference metrics are cheap; delay-tail metrics are one to
   two orders of magnitude more expensive.** `n_rep` for `Rms` is single digits;
   `Dtail` needs `~10^4` shifted cycles per arm. That asymmetry drives the whole
   compute plan (`COMPUTE_PLAN.md`) and is the main argument for screening on a
   cheap surrogate before paying for the tail.
2. **`n_rep` is not the only lever.** Tail events accumulate as
   `n_rep x cycles_per_replicate`, so a tail budget can be met by longer
   replicates as well as by more of them — but only the replicate count buys
   *independent* information, so §5's event rule and this table must both be
   satisfied, not either one.

## 8. Multiplicity

P6 will compare many policies on several metrics. Preregistered handling:

* **One** primary objective, at **one** preregistered `(D, m, Delta)` primary
  cell, decided at the entry gate. Everything else is secondary and labelled so.
* Secondary comparisons carry a Benjamini–Hochberg FDR control at `q = 0.10`
  within each metric family, reported alongside the raw intervals.
* The reproduction requirements (both detectors, `>= 3` values of `m`, an
  independent seed family) are the real protection: they are far stronger than
  any alpha adjustment, because they require the effect to *recur*, not merely
  to be small-p once.

## 9. Seeds

* Seeds derive deterministically from `(seed_family, detector, m, policy_id,
  cell_hash, replicate_index)` via `numpy.random.SeedSequence`, so any single
  replicate is reproducible in isolation.
* **Three disjoint seed families**: `TUNE` (all fitting, all hyperparameter
  search), `EVAL` (all reported numbers), `REPLAY` (independent adjudication,
  never touched by the campaign team).
* Reusing a `TUNE` seed in `EVAL` is a campaign-invalidating error, so it is
  asserted by test (`I5`, `F9`).
