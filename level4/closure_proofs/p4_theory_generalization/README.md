# Level-4 Priority 4 — theory generalization beyond the closed Gaussian core

**Question.** Which parts of the closed ReBaseGuard derivative/stability
mechanism are Gaussian, and which follow from a much more general statistical
structure?

**Answer, in one line.** Exactly one substitution is Gaussian —
`psi(z) = z`, which turns the stopped score sum into the residual total
`T_tau`. Replace it by the location score of any regular family and the whole
P1/P2/P3 mechanism survives, for every truncated window length `m >= 1` and
both frozen detectors:

```text
F'_{rho,m}(0) = rho (1 - Gamma_{D,m,f}),
Gamma_{D,m,f} = E_0[ A_m * sum_{t<=tau} psi(Z_t) ],     psi = -f'/f.
```

Two further Gaussian dependencies are found and reported as *not* general:
the pathwise nonnegativity of the short-window correction, and the
differentiability hypothesis that the closed spines assume.

## What is new here relative to the repository

`location_family` and `location_family_track3ab` already proved the stopped
score identity for a **single terminal observation** (`m = 1`). They are frozen
scientific prerequisites, are not re-derived, and are not re-run for their own
sake. Priority 4 adds:

| # | contribution |
|---|---|
| 1 | the identity for the truncated window `w = min(m, tau)` at every `m >= 1`, with the random denominator and the `tau < m` branch |
| 2 | both frozen detectors (CUSUM and SR) in a single statement, with their stopping-tail hypotheses discharged |
| 3 | a **weaker** differentiation hypothesis (Lipschitz difference quotient) that admits Laplace, which the closed spines' dominated-derivative hypothesis excludes |
| 4 | Corollary G2: a non-selective stopping rule has gain exactly `1` for every regular family, so `Gamma - 1` *is* the stopping-selection effect |
| 5 | Theorem G3: the random-denominator decomposition is general; the Gaussian score makes its short-cycle correction nonnegative, while the correction and its expectation can be strictly negative off Gaussian |
| 6 | two proved failure modes: moving support (uniform) and no first moment (Cauchy), with an exact closed-form defect and an exact divergence |
| 7 | a Lean **proof** of the stopped-score derivative bridge that Track 3A/3B could only assume, plus the Gaussian case derived from it as an instance |
| 8 | a closed-form, unbounded-horizon, interval-certified non-Gaussian instance |

## Layout

```text
THEOREM.md                 the statements: G1, G1', G2, G3, G4, the discharge
                           lemmas, and the two proved failure modes
PROOF.md                   the complete human proof, with no step deferred
ASSUMPTION_AUDIT.md        Phase A: the four layers and the dependency table
NUMERICAL_CORRESPONDENCE.md  generated: all four evidence routes
EVIDENCE_BOUNDARY.md       what is proved / computed / certified, separately
LEAN_CORRESPONDENCE.md     the formal spine and exactly where it stops
PROVENANCE.md              what was frozen when, including the pilot defect
NOVELTY_AUDIT.md           NOVELTY-NOT-ADJUDICATED, and why
ADVERSARIAL_REVIEW.md      the attack on this campaign's own result
INDEPENDENT_ADJUDICATION.md independent theorem, numerical and repository audit
CLOSURE_REPORT.md          the verdict and the evidence behind each gate
CODEX_HANDOFF.md           the independent re-verification instructions
P5_HANDOFF.md              observations for the nonlinear/global campaign

src/rebaseguard_p4_general/  families, detectors, simulator, quadrature,
                             estimators
numerics/run_correspondence.py   the four-route campaign driver
certificates/                the frozen witness and its Arb certifier
lean/                        the Priority-4 proof spine and axiom audit
scripts/build_reports.py     map, tables and the generated report
tests/                       the focused suite
results/                     generated JSON/CSV artifacts
```

## The four evidence routes, kept apart

| route | what it is | what it can establish |
|---|---|---|
| **Q** | adaptive quadrature for the memoryless detector `tau = inf{t : \|Z_t\| >= c}` | the identity itself, to 10-12 digits, with **no sampling error** — but not at the frozen operating point |
| **N** | deterministic stopping `tau = n`, where Corollary G2 forces `Gamma = 1` | that the score, window and denominator code is right, against a known answer |
| **A** | `Gamma = E_0[A_m sum psi(Z_t)]` under the frozen CUSUM and SR | a Monte Carlo estimate of the theorem's side |
| **B** | common-random-number Richardson-extrapolated central difference of the actual map | a Monte Carlo estimate of the truth, using **no** likelihood, score or change of measure |

Routes A and B are compared against the 3% relative limit inherited unchanged
from the Track-3 location-family gate.

## Reproducing

```bash
bash level4/closure_proofs/p4_theory_generalization/reproduce.sh
```

The correspondence campaign is the expensive step (order one hour). Everything
else — the Arb certificate, the Lean spine, the focused suite — runs in
minutes.

## Status

```text
verdict                       PARTIAL
repository-wide verification  PASS (classified required matrix)
independent adjudication       COMPLETE
```

The mathematics is complete and unfalsified by every route that can carry the
weight — exact quadrature, an exact neutrality control, both frozen detectors,
six innovation families, a clean Lean audit and a passing Arb certificate.
Independent finer-step and fresh-score replays resolve the original
`skewnormal4/SR/m=2` discrepancy as finite-step bias plus Monte Carlo scatter,
and a fresh frozen-P2 implementation replay reconciles the older SR values.
The preregistered *numerical* gates nevertheless remain literally failed: nine
of ninety-six cells are a single infinite-variance family failing an accuracy
limit their estimator cannot reach, the original skew-normal cell is preserved
as generated, the Cauchy gate asks for the wrong failure shape, and the frozen
Gaussian comparison still uses its predeclared single-error statistic.
`CLOSURE_REPORT.md` §1 and `INDEPENDENT_ADJUDICATION.md` give the full
accounting.  No gate was rewritten after the data were seen.

## What this campaign does not claim

It is not distribution free. It is not detector universal. It says nothing
about global or nonlinear dynamics, period-2 orbits, hysteresis or basins —
those belong to Priority 5 and only a handoff note is written here. It
certifies no frozen CUSUM or SR gain: every such number in this campaign is a
Monte Carlo estimate. And it declares no novelty verdict: see
`NOVELTY_AUDIT.md`.
