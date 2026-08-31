# Adversarial self-review

Phase G.  Each item is an attack on this campaign's own result, followed by
what was actually found and what was changed because of it.  Items that ended
in a narrowing of the claim are marked **NARROWED**; items that ended in a
correction are marked **FIXED**.

## A1. "There is a hidden Gaussian assumption in the reuse statistic."

`A_m` is the arithmetic mean of the last `min(m,tau)` raw residuals.  Nothing
in the proof uses a property of that particular functional beyond
measurability and integrability; `PROOF.md` §1 carries it intact through the
change of measure.  The `1/w` factor is bounded in `[1/m, 1]`, is `e`-free, and
is never differentiated.

Where a Gaussian assumption *was* hiding: the **sign** of the short-window
correction.  Priority 1 proves `Q_m >= 0`, and reads it as "the random
denominator cannot be replaced by `m`, because doing so deletes `Q_m`".  The
identity generalises; the sign does not, and Theorem G3 shows it is exactly the
sign of `T_tau S_tau`.  The Gaussian score turns that product into a square;
an exact rational non-Gaussian witness has `E[Q_5] = -1/10 < 0`.  Independent
adjudication removed the stronger iff wording because the campaign did not
prove an all-path functional converse.  **NARROWED** — Priority 4 never asserts
the sign in general and now claims Gaussian sufficiency, not uniqueness.

## A2. "The detectors are the Gaussian likelihood ratio, so the result is
still Gaussian."

True of the *construction* of both detectors and irrelevant to the theorem.
The CUSUM increment `Z - 1/2` and the SR chart `(1+R)exp(Z - 1/2)` are the
Gaussian log-likelihood-ratio objects for a unit shift.  Applied to Laplace or
Student-`t` innovations they are no longer that family's likelihood ratio —
they are simply fixed measurable functionals of the residual path, which is all
(A1) asks for.  The campaign deliberately does **not** replace them with each
family's own likelihood ratio, because doing so would change the frozen
detector.

## A3. "The differentiation under the integral is not justified."

This was taken seriously, and it produced the campaign's sharpest finding.  The
hypothesis P1 and P2 use — an integrable dominator for the pointwise
`e`-derivative on a whole neighbourhood — presupposes a.s. differentiability at
every `e` in that neighbourhood.  **That hypothesis is false for the Laplace
family**: `e -> log f(z+e)` has a kink at `e = -z`, and the union over `e` in a
neighbourhood of the bad sets has full measure.  Priority 4 therefore uses the
Lipschitz difference-quotient hypothesis (A6), which needs the derivative only
at the base point, and proves it in Lean through
`hasDerivAt_integral_of_dominated_loc_of_lip`.  **NARROWED and strengthened.**

## A4. "The domination hypothesis is assumed, not discharged."

`PROOF.md` §8 discharges it, twice, for two disjoint innovation regimes: L3 for
bounded scores with a `1 + eta` moment, L4 for at-most-linear scores with an
exponential moment.  Both consume L1 (geometric stopping tail) and L2 (the
Wald-type window moment bound).  L4 was rewritten during this review because
its first draft absorbed a constant without saying how; the current version
carries three explicit pathwise bounds and an explicit `C_delta`.  **FIXED.**

Residual weakness: L1's `p > 0` requires the innovation law to reach the
detector's forcing level `c_D`.  Every theorem-supported family here has
support `R`.  A compactly supported family with `a < c_D` would need a
different argument, and this is now stated in `PROOF.md` §8.

## A5. "Stopping-time integrability is missing."

L1 gives a geometric tail uniformly on a compact `e` neighbourhood, from a
one-step forcing event that is verified in code
(`test_forcing_increments_alarm_in_one_step_from_the_reset_state`).  L2 turns a
single innovation moment into a bound on every window moment using
`{tau >= n} ∈ F_{n-1}`.

## A6. "There is a denominator edge case."

`tau >= 1` by construction, so `w = min(m, tau) >= 1` and the reciprocal is
bounded by one.  The `{tau < m}` branch is tested directly
(`test_window_mean_is_the_truncated_average_including_the_alarm_increment`)
against `A_m = T_tau/tau`, and the pathwise decomposition is tested at every
`m` on a bounded-score family.

## A7. "Symmetry is assumed somewhere it should not be."

Audited line by line.  Symmetry appears in exactly one place, `PROOF.md` §7,
and it delivers exactly one thing: `E_0[A_m] = 0`, hence a fixed point at the
origin.  To make sure this is not a paper claim, the campaign measures
`E_0[A_1]` for a standardised skew-normal family and finds it of order one, not
of order the Monte Carlo error.  The classifier then **refuses** to give those
cells a stability label, reporting `FIXED-POINT-NOT-AT-ORIGIN`, and
`tests/test_results.py` asserts that refusal.  **NARROWED** — the Priority-3
stability map does not extend to asymmetric families at the origin, and
Priority 4 says so instead of quietly classifying them.

## A8. "The numerical evidence is overstated."

Four separate risks were found.

1. *Route A and Route B share the simulator.*  A defect in the detector code
   would move both.  This is mitigated, not eliminated: Route Q is independent
   of the simulator entirely and validates the identity to 10-12 digits, and
   the Gaussian cells at the frozen operating points are compared against the
   independently implemented Priority-1 and Priority-2 gains.
2. *Heavy-tailed cells have unreliable standard errors.*  `t3` and `t1p5` have
   finite variance but infinite fourth moment, so any variance estimate is
   itself heavy-tailed.  Batch-level errors are used throughout, which is what
   the closed campaigns do and what Track 3's variance diagnosis recommends,
   but the `|z|` column for those cells should be read as indicative.
3. *Route B is discretisation-biased.*  Measured, not assumed: at the frozen
   operating point a central difference at `h = 0.05` is about 5.5% low.  Route
   B reports a per-batch Richardson combination and an independent finer ladder
   re-tests the `O(h^2)` law.
4. *Route Q is not interval-certified.*  Adaptive quadrature returns a
   heuristic error estimate.  `EVIDENCE_BOUNDARY.md` places Route Q in its own
   layer, below Arb and above Monte Carlo.

## A9. "The cross-family gain table is a like-for-like comparison."

It is **not**, and this is the campaign's main interpretive limitation.  All
families are run at the *same* frozen threshold, so their in-control ARLs
differ substantially.  A difference between two families' `Gamma` therefore
mixes the effect of the innovation law with the effect of a different alarm
rate.  The historical Track-3 campaign avoided this by calibrating a separate
threshold per family to a common ARL; Priority 4 deliberately did not
introduce a new calibration artifact, and instead reports every ARL next to
every gain.  **NARROWED** — no claim is made that one family is "more" or
"less" stable than another; the claim is that the identity holds for each.

## A10. "`t1p5` is not on the same scale as the others."

Correct.  Student-`t` with `nu = 1.5` has no variance, so it cannot be
standardised to unit variance and is used at its natural scale.  Its `Gamma` is
therefore not comparable to the unit-variance families' — which is fine,
because its role is to sit on the far side of the finite-variance line and show
that the theorem does not need one.

## A11. "The `tau` and `m` conventions were silently changed."

They were not.  `w = min(m, tau)`, denominator `w`, terminal increment
included, inclusive post-update alarm, ordinary `tau` from `t = 1`, `m` grid
`[1,2,3,5]`, admissible `rho` in `[0,1]` — all inherited verbatim and recorded
in `manifest.json` under `conventions_inherited_unchanged`.  The frozen CUSUM
step is asserted bit-for-bit against `rebaseguard_level4.frozen.step_scalar` in
the test suite.

## A12. "This is just the Track-3 theorem renamed."

The most serious prior-art objection, and it is answered by scope, not by
rhetoric.  Track 3 and Track 3A/3B prove the stopped-score identity for the
terminal functional `H_tau = Z_tau`, that is `m = 1`.  They contain no
truncated window, no random denominator, no `tau < m` branch, no SR detector,
no discharge of the domination hypothesis, no failure-mode proofs, and their
Lean spine assumes the derivative bridge rather than proving it.  The overlap
is real and is stated at the top of `README.md`, in `manifest.json`, and in
`NOVELTY_AUDIT.md`.  **NARROWED** — the contribution is stated as the
intersection neither campaign covered, not as a new theorem about location
families.

## A13. "The novelty claim is unsupported."

There is no novelty claim.  `NOVELTY_AUDIT.md` returns
`NOVELTY-NOT-ADJUDICATED`, records that no literature search was possible, and
lists seven prior-art areas that a real audit must cover, with candidate
references.  `tests/test_documents.py` fails the build if any document contains
a priority assertion of the "first such proof
anywhere" kind.

## A14. "The protocol was frozen after seeing outcomes."

It was frozen after a pilot, and `PROVENANCE.md` §2 says so in those words.
The pilot found a real defect in this campaign's own random-number stream, and
that is disclosed with the mechanism, the symptom, the fix, and the permanent
regression test.  What the pilot saw: Gaussian and `t3` cells at the *reduced*
operating point.  What it did not see: any frozen-layer cell, any other family,
any certificate, and any classification.

## A15. "A frozen artifact was quietly repaired."

None was.  Two findings in `ASSUMPTION_AUDIT.md` §4 concern P1's and P2's own
hypotheses — that their differentiation hypothesis is stronger than their proof
needs, and that their nonnegativity result is Gaussian.  Neither is an
integrity problem, neither weakens the closed results, and neither is applied
to those artifacts.  `tests/test_integrity.py` asserts `git diff HEAD` is empty
for all twelve protected trees on every run.

## What survived, and in what form

The general derivative identity survived intact for `m >= 1`, both frozen
detectors, and six innovation families, with its hypotheses discharged in two
named regimes.  What did **not** survive generalisation: the sign of the
short-window correction, the fixed point at the origin without symmetry, and
the differentiation hypothesis as the closed spines state it.  Each of those is
reported as a limit of the generalisation, not as a footnote.
