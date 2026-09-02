# P5X handoff

Read `FROZEN_THEOREM.md`, `FROZEN_SCOPE.md`, `PROOF_OBLIGATIONS.md` and
`FROZEN_GATES.md` first. They are frozen; this file is the instruction set that
consumes them.

## 1. What has already happened

A mathematical feasibility audit only. No production result exists. The
feasibility verdict is `P5X_THEOREM_PATH_FOUND`, resting on one new exact
reduction (`P5X-T1`) and one floating-point probe that failed to falsify it.
Checkpoint A froze the theorem statements, scope, gates, proof obligations and
plans **before** any production work.

## 2. What must never happen

1. `level4/closure_proofs/p5_nonlinear_dynamics/` must stay byte-identical to
   `bb03c0e`. Original P5 stays `PARTIAL` forever.
2. No P5 gate is re-run, reworded, reinterpreted or weakened.
3. No P5 negative result is reinterpreted. In particular P7's operational
   negative finding and P5's rejection of the "runaway" and "multiple invariant
   laws" hypotheses stand.
4. This campaign is **not** `P5R` and must never be labelled one.
5. No Monte Carlo number and no floating-point grid may enter a proof path.
6. No document may assert that the flip bifurcation causes the stationary
   dispersion, or that the skeleton 2-cycle is the measured bimodality.
7. `results/` must remain empty of production artifacts until Checkpoint A is
   pushed.

## 3. Production order (frozen; step 3 is a stop-gate)

1. **Human proofs.** Write `L1`, `L2`, `L3`, `L5`, `L6` in full with constants,
   as `PROOF.md`. `L1` includes the term-by-term convention-A split
   `{tau >= m}` / `{tau = t < m}` of `P5X-T1(c)`.
2. **Resolvent.** Prove `L4` and express the bound as a function of the
   `e`-interval, reusing the monotone Bellman minorant of `N-01`.
3. **Single-cell stop-gate.** Build the certified enclosure `C1` for exactly one
   `e`-cell, one detector, `m = 1`. Publish the achieved half-width. If it
   exceeds `0.2`, **stop and re-plan**; do not scale.
4. **Scale.** Complete the `C1` and `C2` covers; derive `R_max`, `s_min`, `M_2`;
   establish `P5X-T4`, `P5X-T5`, `P5X-T6`.
5. **Level C.** Attempt `C3`, then `P5X-T7`. Report per detector and per `m`.
6. **Level D (optional).** Attempt `L8`, `C4`, `P5X-T8`. Report the first `eta`
   obtained and do not re-tune it.
7. **Lean.** Write `X1`–`X3` (and `X4`–`X6` if their theorems exist); run the
   axiom audit; write `LEAN_CORRESPONDENCE.md`.
8. **Empirical.** Run `E1`–`E6` on a seed family disjoint from P5's.
9. **Assemble.** Write `PROOF.md`, `CERTIFICATE_REPORT.md`, `RESULTS.md`,
   `NUMERICAL_CORRESPONDENCE.md`, `ADVERSARIAL_REVIEW.md`; compute the gates
   mechanically; submit a verdict.

## 4. Checkpoint discipline

* **Checkpoint A** (this commit): protocol, theorems, scope, gates, obligations,
  plans, feasibility probe, manifests, tests. **No production result.**
* **Checkpoint B**: the completed campaign with results and a mechanically
  derived `P5X_VERDICT`, submitted for independent adjudication. Never squash.
* Adjudication is a separate commit by a separate reader.

## 5. Attacks an adjudicator should run first

1. Re-derive `P5X-T1(c)` independently for `m = 3` and check the short-`tau`
   bookkeeping term by term; then confirm it against a direct simulation. This
   is the campaign's single point of failure.
2. Check that the certified `R'(0)` enclosure really contains the P3
   `1 - GammaTilde`, and that the `m = 1` cells intersect the existing `Gamma`
   certificates (`G2`). A reduction that is subtly wrong will most likely show
   up here.
3. Verify the cover **tiles** `[0, 12]` — matching endpoints, no gaps — rather
   than merely containing many cells (`G8`).
4. Confirm no accepted cell cites a sampled evaluation (`G8`), and that the
   far-field lemma's constant is evaluated, not asserted.
5. Confirm the protected tree, including that the two untracked audit
   namespaces are unchanged and were not swept into any commit (`G11`).
6. Read `RESULTS.md` for E-strong language (`G12`). The most likely
   overclaim in this campaign is a sentence that lets a reader believe the
   bifurcation explains the dispersion.
7. Check that `P5 = PARTIAL` still appears unchanged in the root status table
   and in every P5X document (`G10`).

## 6. If the campaign fails

Report it as `PARTIAL_CANDIDATE` or `FAILED` with the failure mode named from
`FAILURE_ANALYSIS.md` §6. A campaign that lands on Level B alone still
establishes something P5 did not have — a non-vacuous two-sided stationary
dispersion bound — and that is worth reporting honestly rather than dressing up.
