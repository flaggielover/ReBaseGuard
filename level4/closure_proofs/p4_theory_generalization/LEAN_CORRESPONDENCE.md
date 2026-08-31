# Lean correspondence

## 1. What is formalized

`lean/GeneralLocationFamilyP4.lean`, in namespace
`RebaseguardLean.Level4Priority4`.  It imports the closed Priority-3 synthesis
spine, which imports the closed Priority-1 and Priority-2 derivative spines.
None of the three is modified; all four files are compiled from their own
protected sources by `run_lean.py`.

| # | declaration | paper statement | why it is here |
|---|---|---|---|
| 1 | `hasDerivAt_stoppedMean` | `PROOF.md` §2, (2.2) | **the core bridge.** For an abstract likelihood family `L` with `L 0 = 1` and derivative `-S` at zero, `d/de ∫ A L = -∫ A S` |
| 2 | `reuse_derivative` | `THEOREM.md` (G1b) | the `rho` scaling on top of (1), reusing Priority 1's closed algebra |
| 3 | `gaussianLikelihood_zero` | `THEOREM.md` (T2) at `e=0` | the Gaussian family is normalised at the base point |
| 4 | `gaussianLikelihood_hasDerivAt` | `THEOREM.md` (T2) | the Gaussian family satisfies the abstract hypothesis with score `T` |
| 5 | `gaussian_reuse_derivative` | P1/P2 conclusion | **the closed Gaussian statement derived as an instance of (2)**, not restated |
| 6 | `generalDirect_eq_fixed_add_short` | `THEOREM.md` (G3a) | the random-denominator decomposition for an arbitrary score |
| 7 | `generalShortCorrection_gaussian` | `PROOF.md` §6 | the general correction reduces to Priority 1's for `psi(z)=z` |
| 8 | `generalShortCorrection_nonneg` | `PROOF.md` §6 | nonnegativity holds **given** `T S >= 0` |
| 9 | `generalShortCorrection_neg` | `PROOF.md` §6 | and fails when `T S < 0` |
| 10-13 | `witnessPrefix_total`, `witnessPrefix_score`, `witness_shortCorrection`, `witness_shortCorrection_neg` | `PROOF.md` §6 | the explicit bounded-score path `(5,-1,-1,-1)`: `T = 2`, `S = -2`, correction `= -1/5 < 0` |
| 14 | `neutral_gain_of_orthonormal_cross` | `PROOF.md` §5 | the algebraic core of Corollary G2: orthonormal cross moments force gain `1` |
| 15 | `neutral_multiplier` | `THEOREM.md` §5 | gain `1` gives multiplier exactly `0`, for every `rho` |
| 16 | `integral_eq_zero_of_odd_under_involution` | `PROOF.md` §7 | a measure-preserving involution negating `A_m` forces `E[A_m] = 0` |
| 17 | `reuse_fixed_point_of_zero_mean` | `PROOF.md` §7 | hence the origin is a fixed point |
| 18-19 | `general_attracting_of_lt_criticalRho`, `general_repelling_of_criticalRho_lt` | `THEOREM.md` §7 | the general gain feeds Priority 3's classification unchanged |

Axiom audit: `results/axiom_audit.txt`, machine-summarised in
`results/lean_compile.json`.  Every declaration depends on exactly
`propext`, `Classical.choice`, `Quot.sound`.  There is no `sorry`, no
`sorryAx`, and no project-specific axiom; `run_lean.py` asserts all of this and
also asserts that the source contains no `axiom ` declaration.

## 2. The one place Priority 4 strengthens the formal layer

Track 3A/3B's Lean spine contains

```lean
theorem stoppedScore_derivative_bridge
    ... (hbridge : HasDerivAt terminalMean (-(gamma ...)) 0) :
    HasDerivAt terminalMean (-(gamma ...)) 0 := hbridge
```

— the derivative bridge is an *assumed hypothesis returned unchanged*.
Priority 4's `hasDerivAt_stoppedMean` **proves** that step from Mathlib's
`hasDerivAt_integral_of_dominated_loc_of_lip`, given measurability, the base
normalisation, integrability, an integrable Lipschitz constant, and the
pointwise derivative at zero.  That is the difference between "the analytic
step is assumed" and "the analytic step is reduced to hypotheses about the
integrand".

Priority 1 and Priority 2 do prove their bridge, but through
`hasDerivAt_integral_of_dominated_loc_of_deriv_le`, which requires a pointwise
derivative at *every* point of a neighbourhood.  Priority 4 uses the Lipschitz
variant, which requires the derivative only at the base point.  That is the
formal counterpart of `ASSUMPTION_AUDIT.md` row 5, and it is what makes the
Laplace family admissible.

## 3. Where the formalization stops — explicitly

Lean does **not**:

* construct any probability space, filtration, stopping time, or stopped
  sigma-field;
* construct any location-family density, or prove that
  `prod f(Z_t+e)/f(Z_t)` is the Radon-Nikodym derivative of `Q_e` with respect
  to `Q_0` on `F_tau` (`PROOF.md` §1);
* discharge the concrete hypotheses (A2), (A4), (A5), (A6) for the frozen CUSUM
  or SR processes.  Lemmas L1-L5 of `PROOF.md` §8 are human proofs;
* evaluate any `Gamma`, certify any Monte Carlo number, or reproduce any
  quadrature value;
* say anything about the integration-by-parts identities `E[psi] = 0` and
  `E[eps psi(eps)] = 1` that Corollary G2 rests on.  Declaration 14
  formalises only the algebra *downstream* of them, taking the orthonormal
  cross-moment structure as a hypothesis;
* prove that the uniform or Cauchy failure modes occur.  Those are human
  proofs (`PROOF.md` §§9-10) and, for the uniform case, exact rational
  arithmetic in the Arb layer;
* say anything about global or nonlinear behaviour.

## 4. Honest summary of the boundary

The formal layer covers the *logical spine*: the interchange step under stated
integrand hypotheses, the algebra that turns it into a multiplier, the
decomposition and its sign, the neutrality algebra, the symmetry argument, and
the classification bridges.  It does not cover the *measure-theoretic
construction* of the stopped location-family model, nor the concrete analytic
estimates for the frozen detectors.  Those remain human-proved, and
`PROOF.md` states them in full rather than deferring to unnamed regularity.
