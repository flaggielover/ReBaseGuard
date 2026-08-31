# Evidence boundary

Four kinds of evidence appear in this campaign.  They are never mixed, and no
statement is allowed to borrow strength from a stronger neighbour.

## 1. Analytic theorem (human proof)

`THEOREM.md` and `PROOF.md`.  Conditional on explicitly stated hypotheses
(A1)-(A7), which `PROOF.md` Section 8 discharges for the frozen two-sided
CUSUM and the frozen two-chart SR under two named innovation regimes
(bounded score with a `1+eta` moment; at-most-linear score with an exponential
moment).

Also analytic, and also human-proved:

* the closed-form Laplace instance of `PROOF.md` Section 11 — **unbounded
  horizon**, no truncation, no numerics;
* the closed-form uniform counterexample of `PROOF.md` Section 9;
* the Cauchy divergence of `PROOF.md` Section 10;
* Corollary G2 (deterministic stopping has gain exactly one);
* Theorem G3's pathwise identity and its sign characterisation.

What is *not* analytic: the value of `Gamma` for any frozen CUSUM or SR
configuration, Gaussian or otherwise.

## 2. Machine-checked (Lean)

`lean/GeneralLocationFamilyP4.lean`, audited in `results/axiom_audit.txt`.
Covers the abstract-likelihood derivative bridge, the Gaussian instance, `rho`
scaling, the general random-denominator decomposition and its sign analysis,
the algebraic neutrality corollary, the symmetry fixed point, and the bridges
into the closed Priority-3 classification.  It constructs no probability space
and discharges no concrete integrability or tail obligation.  See
`LEAN_CORRESPONDENCE.md` for the exact line.

## 3. Deterministic numerics with no sampling error

Route Q: adaptive quadrature for the memoryless detector, reported with the
quadrature error bound returned by the integrator.  This is *not* an interval
certificate — the integrator's error estimate is heuristic — but it is free of
Monte Carlo error, and it is evaluated on both sides of the identity
independently.

Route Q's detector is **not** the frozen ReBaseGuard detector.  Nothing in
Route Q is evidence about `h = 5` or `A = 520.886133602749`.

## 4. Rigorous interval certification (Arb)

`certificates/certificate.json`, at 160 bits.  Exactly three objects:

| object | horizon | what is certified |
|---|---|---|
| unit-variance Laplace, memoryless detector, `m = 1` | **unbounded** | `Gamma_1 = 1 + 2 sqrt 2`, the origin is fixed, the central difference converges to `-Gamma_1`, attraction at `rho = 1/4`, repulsion at `rho = 1/2` |
| uniform innovations, memoryless detector | finite algebra | the alarm probability is constant in `e`, the map is exactly linear with slope `-2`, and the identity defect is exactly `2` |
| finite-support exponential tilt with a bounded non-affine score | finite support | the derivative identity, the general decomposition, a strictly negative short correction *and a strictly negative expectation* `E[Q_5] = -1/10`, and that the Gaussian-form gain `7/2` differs from the true gain `5/2` |

The Laplace object's certification is an interval evaluation of a closed form
whose derivation is human mathematics; the interval layer removes floating-point
doubt, not proof obligations.  The tilt witness is an exact instance of the
abstract score theorem and is **not** a location family.

## 5. Monte Carlo (no certification)

Every `Gamma` reported under the frozen CUSUM or SR recursions, for every
family including the Gaussian control, and therefore every critical reuse
fraction and every stability classification derived from them.  Batch standard
errors; 95% intervals; cells whose interval straddles unit multiplier
magnitude are reported `INCONCLUSIVE` under the Priority-3 rule.

## 6. What is explicitly NOT established

* **No infinite-horizon interval certification of any frozen CUSUM or SR
  gain.**  This was already the boundary at Priority 1, 2 and 3, and Priority 4
  does not move it.
* No global, nonlinear, or multi-cycle stochastic stability result.
* No claim about detectors other than the two frozen ones and the memoryless
  validation rule.
* No claim that the reduced operating points (`h = 2`, `A = 20`) tell you
  anything about the frozen ones beyond sharing the same recursion.
* No novelty verdict.
