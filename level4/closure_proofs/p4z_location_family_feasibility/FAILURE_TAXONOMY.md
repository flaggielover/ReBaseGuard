# P4Z Phase 1 — failure taxonomy for the P4 / P4X / P4Y line

The mandatory separation first, because it decides everything downstream.

```text
FAILURES OF THE THEOREM TARGET          = 0
FAILURES OF THE MEASUREMENT ARCHITECTURE = 6   (F-01 .. F-06)
```

No historical artifact contains a measurement that contradicts G1, G1', G2, G3
or G4 on a family and detector inside the hypotheses.  Across P4 and P4X, 96
theorem-supported cells were adjudicated against the unchanged
`relative <= 0.03` and `|z| <= 4` gate and **zero** FAILED.  The two behaviours
that look like failures — the uniform family's exact defect of 2 and the Cauchy
family's non-convergence — are the theorem's own proved failure modes F1 and F2
appearing exactly where `THEOREM.md` §9 says they must.  They are confirmations,
not counterexamples.

Everything the line did not close is a property of how the number was measured.

## Classification

| id | what failed | categories | theorem or architecture |
|---|---|---|---|
| `F-01` | historical Route-A summand `A_m S_tau^psi` has infinite variance for `t1p5` | `ESTIMATOR_VARIANCE` | architecture |
| `F-02` | historical Route-B CRN difference is a heavy-tailed rare-event estimator | `ESTIMATOR_VARIANCE`, `INSUFFICIENT_POWER` | architecture |
| `F-03` | the batch standard error estimates a quantity that does not exist | `ESTIMATOR_VARIANCE`, `CERTIFICATE_WIDTH` | architecture |
| `F-04` | "achieve `r*`, at most one top-up" leaves an unadjudicable state | `STOPPING_RULE_DEFECT`, `GOVERNANCE_VIOLATION` | architecture |
| `F-05` | `N_req` targets an expectation where a quantile is required | `STOPPING_RULE_DEFECT`, `INSUFFICIENT_POWER` | architecture |
| `F-06` | P4's Gaussian-consistency statistic divided by one campaign's SE alone | `IMPLEMENTATION_DEFECT`, `CERTIFICATE_WIDTH` | architecture |
| `N-01` | uniform: identity false, exact defect 2 | `NOT_ESTABLISHED` → resolved as proved failure mode F1 | theorem, and *proved* |
| `N-02` | cauchy: estimand does not exist | `NOT_ESTABLISHED` → resolved as proved failure mode F2 | theorem, and *proved* |

Categories that are **not** claimed anywhere in this line, and the evidence:

* `SCIENTIFIC_COUNTEREXAMPLE` — none.  0 of 96 cells failed the gate in either
  campaign.
* `ESTIMATOR_BIAS` — no bias was demonstrated.  P4X's R0 pilot found the coarse
  finite-difference step "inadmissibly biased" for `skewnormal4`, but that
  candidate was rejected and never entered production; the frozen Richardson
  pair was retained.
* `PATH_BUDGET_VIOLATION` — none.  24.75 of 60 authorised CPU-hours, 18.60 of
  40 per configuration.  Sharding preserved total N, block size, estimator,
  precision rule and gate.
* `NUMERICAL_CONDITIONING` — not the obstacle.  The SR charts are carried in
  the log domain precisely so they stay finite for heavy-tailed innovations,
  and P4X's anchor phase reproduced 48 frozen comparisons at `1e-12` with 0
  mismatches.

## F-01 — the dominant term

`t1p5` is a raw Student-`t` with `nu = 1.5`: finite mean, **infinite variance**,
tail index exactly `1.5`.  The Route-A per-path summand is `A_m S_tau^psi`.
`psi` is bounded for this family (`sup|psi| = (nu+1)/(2 sqrt(nu)) = 1.0206`) and
`tau` has a geometric tail, so `S_tau^psi` has every moment.  `A_m` does not:
its alarm-causing increment `Z_tau` inherits the family's `x^{-1.5}` tail.

Hence `E[(A_m S_tau^psi)^2] = infinity`, and the empirical standard deviation of
the summand is an estimate of a quantity that is not there.  Measured on
200 000 paths by the P4Z micro-pilot, the Hill index of the historical summand
is `1.5–1.6` on every `t1p5` cell — the theoretical value — and a single path
carries **30 % to 97 %** of the total squared deviation.

`estimators.py`'s own docstring states the opposite: *"The stopped gain of a
heavy-tailed family has a finite variance but an infinite fourth moment, so a
per-path sample-variance error bar is not trustworthy; the batch means are far
closer to normal."*  The first clause is false for `t1p5`, and the remedy it
justifies — batch means — does not repair an infinite second moment, because
block means of `alpha`-stable summands keep the same tail index `alpha`.  The
later P4X heavy-tail policy patched the *exponent* (`kappa = 1 - 1/alpha`)
without revisiting the variance claim the batch-SE convention rests on.

## F-02 — the other route fails differently, and worse

Under common random numbers the two shifted runs share innovations, so on any
path where the stopping time and window indices agree the pathwise difference
of `A_m` is exactly `-2h` and the estimator contributes exactly `1`.  All of the
signal and all of the variance live on the rare paths where the two runs
disagree, and there the difference is `O(Z_tau / 2h)` — the family's full tail,
amplified by 10 to 40.  The historical Route B is therefore a rare-event
estimator of a heavy-tailed jump.  Its measured cost shows it: 2 255 250 000
paths and 66 759 CPU-seconds for one configuration, to reach relSE `0.0062`.

## F-03 — the certificate width was never trustworthy

P4Y Pilot-3 froze a normal-theory uncertainty `1/sqrt(2(n-1))` for a standard
deviation of a law with tail index 1.5 and had to be stopped.  Pilot-4 replaced
it with an empirical admissibility test and found the sharper statement: at
`b = 250 000` two *independent* master pools of 2048 blocks agreed to within
2–4 % on `HSR` and `HB` while a single block carried 21–25 % of the squared
deviation.  Agreement diagnostics cannot see this; concentration diagnostics
can.  Consequently every `t1p5` standard error in the P4/P4X record — and every
`z` computed from one — is unreliable in a way no allocation rule can fix.

## F-04 — the unadjudicable state

Checkpoint A §8.1 permits **at most one** top-up, triggered by a route's own
achieved relative SE exceeding `r*`, and §10 gate `X6` requires each route to
"reach `r*` or be declared `PRECISION_LIMITED`", where `PRECISION_LIMITED` is
declared from *projected cost alone*.  A route that takes its top-up, still
misses `r*`, and hits no cap satisfies neither branch.  Eight cells landed
exactly there.  This is a defect in the rule's totality, not a breach of it:
P4X applied its own rule correctly and recorded the outcome honestly rather
than counting the cells as passes.

## F-05 — targeting an expectation

`N_req = N_ref (relSE_ref / r*)^(1/kappa)` inverts a deterministic rate.  All
three ingredients are random or a model: `relSE_ref` is a statistic, the
realised relSE at `N_req` is a statistic, and `relSE ∝ N^{-kappa}` is
asymptotic.  Landing the *expectation* on `r*` attains it with probability
`F_{chi2_{B-1}}(B-1)` ≈ 0.55, not 0.95.  Under a heavy tail it is worse: the
sample scale is right-skewed and usually *below* the scale it estimates, so
top-ups are systematically undersized.  Pilot-1 measured under-estimation on
75 % of fresh draws pooled, and 100 % on the heaviest cell.

## F-06 — a statistic that treats one Monte Carlo value as exact

P4's `gaussian_consistency_with_closed_core` divided the difference by P4's own
standard error alone, treating the closed Priority-3 Monte Carlo values as
exact, and reached `z = 12.91`.  P4X's `z_combined` uses both campaigns'
published uncertainty and reaches `2.977` against the same limit of 4.  P4's
own decision record labels the historical statistic "not the right test for two
Monte Carlo estimates" and states it was left unchanged after the data were
seen.  P4Z inherits the corrected statistic and does not revisit P4's gate.

## What follows

`F-01`, `F-02` and `F-03` are one defect seen three times: the estimator's
per-path summand carries the innovation law's tail.  `F-04` and `F-05` are
governance consequences of trying to buy precision that the estimator cannot
deliver.  `F-06` is independent and already repaired by P4X.

A successor that changes only the allocation rule cannot work, and P4X and P4Y
between them demonstrated that over five campaigns.  P4Z therefore changes the
estimator so that the per-path summand has finite variance, and leaves the
scientific thresholds, the theorem, the conventions and the detectors alone.
