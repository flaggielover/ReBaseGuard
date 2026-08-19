# ReBaseGuard Phase-4 Feasibility Pre-Gate Design

**Date:** 2026-08-19  
**Status:** Approved for implementation  
**Scope:** Resolve the finite-Bellman/Monte-Carlo discrepancy and audit the
detector dependence of the stopped-score identity. No second detector is in
scope.

## 1. Protected result and success criteria

The existing Level-3 continuum certificate is frozen. It proves, for the
two-sided Gaussian CUSUM with `k=0.5`, `h=5`, and `m=1`, that

```text
Gamma = E[Z_tau T_tau]
      in [3.924348200582897128..., 27.849382127546703281...],
```

so `Gamma>2`. This pre-gate must not modify its certificate, certifier, audit
path, or theorem unless a shared mathematical or convention defect is proved.

The pre-gate succeeds when it:

1. reproduces both the historical finite Arb value `18.7401484450...` and
   direct Monte Carlo near `15.87` under a traced common convention;
2. identifies and tests the exact cause of their disagreement, or isolates it
   honestly if resolution fails;
3. assesses every implication for the protected Level-3 theorem;
4. proves or conditions the strongest valid detector-independent stopped-score
   identity; and
5. issues a GREEN, YELLOW, or RED Level-4 route verdict without implementing a
   second detector.

## 2. Required separation of numerical pathways

Four artifacts remain visibly distinct:

1. **Protected continuum proof.** Existing Arb residual, contraction,
   enclosure, certificate, and independent replay code. Read-only during this
   pre-gate absent a demonstrated shared defect.
2. **Historical finite Bellman cross-check.** Existing `bellman.py` and stored
   `bellman_crosscheck.json`. Preserved byte-for-byte for forensic reproduction.
3. **Corrected/refined diagnostic Bellman solver.** A new module and artifacts.
   It may share exact model constants and Gaussian primitives, but not the
   historical transition-discretization implementation.
4. **Direct Monte Carlo and pathwise oracle.** The deterministic scalar oracle,
   independent path replay, and vectorized seeded simulation. These remain
   explicitly non-proof diagnostics.

Every generated artifact states its proof role. No point estimate is promoted
to continuum evidence.

## 3. Pathwise convention architecture

The canonical one-step oracle accepts `(S_plus, S_minus, T, z)` and returns:

- both post-update CUSUM arms;
- `T_next=T+z`;
- whether an alarm occurs after the update using `>=h`;
- alarm direction with deterministic tie handling; and
- terminal reward `z*T_next` on alarm, otherwise no reward.

The direct simulator is checked pathwise against a separately structured
reference replay. Hand-selected tests cover the origin, both boundaries,
resets, exact and epsilon threshold crossings, and large overshoots. Fixed
innovation sequences record the full trace, `tau`, `Z_tau`, `T_tau`, and
`Z_tau*T_tau`.

The Monte Carlo report uses at least two deterministic independent seeds and a
sample size that separates 15.87 from 18.74 by many standard errors. It reports
Gamma, its standard error, ARL, `E[T_tau^2]` versus `E[tau]`, `E[Z_tau]`,
`E[T_tau]`, and alarm-direction symmetry.

## 4. Bellman audit and corrected diagnostic solver

For a live CUSUM state `s` and cumulative sum `x`, define

```text
H(s,x) = E[Z_tau T_tau | s,x] = a(s)x+b(s).
```

First-step conditioning must be derived and tested as

```text
a = K a + r_a,
b = K b + K_z a + r_b,
```

where the continuation interval is exactly `ell<z<u`, and the absorbing
reward is `z(x+z)`. Thus `r_a` is the absorbing first moment and `r_b` the
absorbing second moment. The implemented convention must give
`Gamma=b(0,0)`.

The historical result is reproduced before any corrected result is generated.
The new diagnostic solver then performs controlled refinement while preserving
outward-rounded Arb evaluation of Gaussian bin moments and linear solves. It
uses the exact reachable continuation geometry or an explicitly equivalent
state representation and avoids silently assigning continuum transitions by
the historical midpoint/floor rule.

Refinement records resolution, transition construction, mass balance, Gamma,
and change from the prior level. If needed, two independent reconstruction
rules bracket or extrapolate the discretization effect. The outcome is
classified into exactly one of the requested categories: Monte Carlo bug,
finite Bellman bug, convention mismatch, finite discretization bias, continuum
formulation issue, or unresolved.

## 5. Convention matrix and forensic evidence

The final report traces every requested convention to source lines for all
four pathways, including alarm timing, increment indexing, terminal reward,
cumulative-sum definition, threshold comparison, overshoot, simultaneous arm
updates, ties, initial state, dwell/history logic, `m=1`, reachable geometry,
reward timing, continuation/absorption partition, and Gaussian tail signs.

Historical artifacts are never overwritten. Corrected outputs use new names
and schemas, and regression tests retain the old `18.7401484450...` reproduction
alongside the corrected/refined result.

## 6. Score-proof dependency audit

The existing proof of `F_1'(0)=1-Gamma` is reconstructed line by line. Each
line is mapped to its actual assumptions: location-family likelihood ratio,
iid observations, stopping-time measurability, almost-sure finiteness,
exponential integrability, terminal-window measurability, differentiability
under expectation, uniform integrability, symmetry, and any detector-specific
facts.

The first target is an arbitrary stopping time on the Gaussian innovation
filtration. With a sufficiently integrable terminal statistic

```text
W_tau,m = (1/m) sum_{r=0}^{m-1} Z_{tau-r},
```

the audit derives the stopped likelihood ratio and determines whether

```text
F'(0) = 1 - (1/m) sum_r Cov_0(Z_{tau-r}, T_tau)
```

requires any CUSUM recursion. Reflection symmetry is kept separate from the
score differentiation: it may turn centered covariances into raw products and
establish a zero fixed point, but it is not assumed merely to state a centered
score identity.

Only after the Gaussian result is settled, the audit treats a regular
one-parameter exponential family. For score `ell` and stopped score
`L_tau=sum_{t<=tau} ell(Z_t)`, it states the correct signed covariance formula
for a general terminal statistic and identifies the domination and
parameterization assumptions. It does not transplant the Gaussian `+1` term
to unrelated parameterizations.

## 7. Tests and audit artifacts

New tests cover:

- scalar oracle transitions and rewards;
- fixed path traces and vectorized/scalar agreement;
- Monte Carlo summary identities and deterministic seeds;
- exact historical Bellman reproduction;
- corrected solver mass balance, reflection behavior, and refinement trend;
- explicit Bellman reward decomposition; and
- protection checks showing the continuum certificate and its hashes are
  unchanged.

The final report is stored as
`proofs/ReBaseGuard_Phase4_Feasibility_PreGate_Report.md`. Supporting diagnostic
artifacts are machine-readable JSON with environment, versions, seeds,
resolutions, and hashes recorded for replay.

## 8. Stop conditions

This work stops after the discrepancy classification, Level-3 impact audit,
score-identity theorem audit, and Level-4 route decision. It does not implement
Shiryaev-Roberts, run broad parameter sweeps, or rewrite the certified theorem.
Routine sample-size, grid, and Arb-precision choices are made autonomously.
