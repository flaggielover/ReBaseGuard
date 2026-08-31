# Novelty audit

## Verdict

```text
NOVELTY-NOT-ADJUDICATED
```

This campaign had no internet access and performed no literature search.  It
therefore declares **no** novelty verdict, and no artifact in this namespace
may be read as one.

The repository's `novelty_verification` campaign remains the only place where a
prior-art position is adjudicated, and it is a read-only dependency here.

## What can be claimed without a literature search

Only a *relative* claim, and only against artifacts inside this repository:

> Relative to the frozen ReBaseGuard core, Priority 4 replaces the Gaussian
> stopped-likelihood score `T_tau` by the general location score sum
> `sum_{t<=tau} psi(Z_t)` in the truncated-window derivative identity for every
> `m >= 1` and for both frozen detectors, weakens the differentiation
> hypothesis to a Lipschitz difference-quotient condition, and identifies the
> short-window correction's sign and the origin's fixed-point status as
> Gaussian- and symmetry-specific respectively.

That is a statement about this repository's own artifacts.  It is not a claim
about the state of the art.

## In-repository prior art, stated explicitly

| artifact | overlap with Priority 4 | difference |
|---|---|---|
| `location_family` (PARTIAL) | the stopped-score identity for a regular location family | terminal functional `H_tau = Z_tau` only, i.e. `m = 1`; no truncated window, no random denominator, no `tau < m` branch, no SR, no failure-mode proofs |
| `location_family_track3ab` (CLOSED) | replicates the same `m = 1` identity; Lean spine | its Lean `stoppedScore_derivative_bridge` **assumes** the derivative bridge as a hypothesis and returns it; Priority 4 proves the bridge from Mathlib's dominated-convergence machinery |
| `m_gt_1_priority1` (CLOSED) | the truncated window and the decomposition | Gaussian only; the nonnegativity of the correction is a Gaussian result, as Priority 4 shows |
| `sr_derivative_priority2` (CLOSED) | the SR detector | Gaussian only |
| `m_rho_stability_priority3` (CLOSED) | `lambda = rho(1-Gamma)`, `rho_c` | Gaussian only, and only at a fixed point at the origin |

## Prior-art areas a real audit must cover

Recorded as a precise TODO for whoever has search capability.  Each line names
what to look for, not what was found.

1. **Sequential analysis / stopped likelihood.**  Wald's identity, the stopped
   change of measure on `F_tau`, and differentiation of a stopped expectation
   with respect to a location parameter.  Question: is
   `d/de E_e[H_tau] = E_0[H_tau S_tau]` for a general location family standard
   textbook material, and under which regularity conditions is it usually
   stated?  Likely relevant: Siegmund, *Sequential Analysis*; Woodroofe,
   *Nonlinear Renewal Theory in Sequential Analysis*.
2. **Score/likelihood-ratio sensitivity estimators.**  The identity is the
   score-function (likelihood-ratio) gradient estimator of simulation
   optimisation.  Question: does that literature already contain the stopped,
   selection-biased, truncated-window case?  Likely relevant: Glynn; Rubinstein
   and Shapiro; L'Ecuyer.
3. **Self-starting and adaptive control charts.**  Question: is the
   destabilising feedback of estimating the reference from post-alarm data
   already characterised, and with what gain?  Likely relevant: Hawkins;
   Quesenberry; Jensen, Jones-Farmer, Champ and Woodall on estimation error in
   control charts.
4. **Post-selection / selective inference.**  Corollary G2 says the entire gain
   above one is a stopping-selection effect.  Question: is `Gamma - 1`
   equivalent to a known selection-bias functional?  Likely relevant: Berk,
   Brown, Buja, Zhang and Zhao; Lee, Sun, Sun and Taylor; Fithian, Sun and
   Taylor.
5. **Renewal and stopping-time theory.**  The geometric forcing tail (L1) and
   the Wald-type window bound (L2) are elementary and almost certainly
   standard; they should be cited, not claimed.
6. **Random dynamical systems / stochastic approximation.**  The conditional-
   mean map and its multiplier resemble a stochastic-approximation gain.
   Question: does that framing already give the `rho_c = 1/|1-Gamma|` boundary?
7. **Location-score identities.**  `E[psi] = 0` and `E[eps psi(eps)] = 1` are
   classical (they are the location Fisher-information normalisation in
   disguise).  They must be cited as classical.

## Discipline

Until items 1-7 are actually searched, every Priority-4 artifact states its
contribution as an extension **relative to the frozen ReBaseGuard core**, and
`tests/test_documents.py` enforces that no document contains a phrase such as
a priority assertion of the "first such proof
anywhere" kind.
