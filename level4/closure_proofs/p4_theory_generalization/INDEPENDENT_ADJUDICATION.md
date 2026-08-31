# Independent Priority-4 adjudication

## Decision

```text
PARTIAL
```

The main stopped-score derivative theorem survives independent re-derivation,
the repository-wide required matrix passes, Lean and Arb replay cleanly, all
twelve protected trees are byte-identical to `HEAD`, and both named numerical
discrepancies are reconciled.  P4 is nevertheless not upgraded to `CLOSED`:
three literal frozen gates remain false and were not weakened or regenerated.
The machine decision in `results/closure_decision.json` therefore remains
`PARTIAL`.

## Strongest theorem accepted

Under (A1)-(A7), for every fixed `m >= 1`,

```text
g_m'(0) = -E_0[A_m sum_{t<=tau} psi(Z_t)],
F'_{rho,m}(0) = rho (1 - Gamma_{D,m,f}).
```

The proof correctly keeps `w=min(m,tau)` and its random denominator inside the
stopped path functional, including the `tau<m` branch.  The change of measure
is first justified on each `{tau=n}` and then summed using (A5)-(A6).  The
Lipschitz difference quotient in (A6) is enough for dominated convergence and
admits Laplace.  L3 needs a finite `1+eta` moment, not finite variance; L4's
constant `4/(d^2 e^2)` and its geometric Cauchy-Schwarz bound check out.

Symmetry is separate: it is needed to make the origin a fixed point before the
Priority-3 local classification can be applied.  The derivative identity does
not need symmetry.

## Theorem narrowing

The original G3 prose overstated its converse.  What is proved is:

```text
sign(Q_{m,f}) = sign(T_tau S_tau^psi) on tau<m;
psi(z)=c z, c>0, makes the product a square;
non-Gaussian corrections can be negative pathwise and in expectation.
```

The campaign did not prove that all-path sign preservation forces a linear
score, and a general affine score also has an intercept that must be handled.
The theorem and supporting prose now claim Gaussian sufficiency plus explicit
non-Gaussian failure, not an iff characterisation.  G1, G1', G2 and G4 are
unchanged.

## `skewnormal4 / SR / m=2`

The original frozen cell was genuinely inconsistent as generated:

```text
Route A                         6.3875 +/- 0.0284
Route B, steps .05/.025         6.5561 +/- 0.0270
combined |z|                    4.29
```

Two independent attacks resolved it without rewriting that cell:

| run | m=2 estimate | comparison |
|---|---:|---:|
| finer Route B, `.025/.0125`, 960k paths | `6.5170 +/- 0.0391` | moves toward Route A |
| smallest Route B, `.0125/.00625`, 480k paths | `6.4342 +/- 0.0785` | `0.56` combined SE from original Route A |
| fresh Route A, 1.6M paths | `6.4549 +/- 0.0452` | `0.23` combined SE from smallest Route B |

At the smallest pair, all four windows agree with the original Route A within
`0.09-0.56` combined standard errors.  The diagnosis is finite-step bias in
the asymmetric frozen-SR map plus ordinary score-route Monte Carlo scatter.
The variance cost at `h=.00625` explains why a finer step is less precise even
as its bias falls.  This resolves the scientific anomaly, but the original
protocol result remains immutable and its gate remains failed.

## Frozen Priority-2 SR mismatch

A fresh 1.6M-path run through the frozen Priority-2 score implementation gave:

| m | fresh P2 implementation | P4 Route A | combined `|z|` |
|---:|---:|---:|---:|
| 1 | `17.3132 +/- 0.0363` | `17.2589 +/- 0.0203` | 1.31 |
| 2 | `14.4055 +/- 0.0309` | `14.3586 +/- 0.0161` | 1.35 |
| 3 | `12.8688 +/- 0.0268` | `12.8313 +/- 0.0130` | 1.26 |
| 5 | `10.9575 +/- 0.0210` | `10.9230 +/- 0.0097` | 1.49 |

This independently rules out a recurrence, alarm, or window mismatch at the
reported scale.  The older 240k-path P2 result was a correlated high Monte
Carlo realization across `m`.  Its literal historical comparison gate still
fails because that frozen gate treats the older Monte Carlo point as exact.

## Exact routes, Lean, and certificates

The deterministic stopping result gives `g_m(e)=-e` and `Gamma=1` exactly.
The uniform moving-support calculation has defect `2`; Cauchy is excluded
because `E|A_m|` diverges already on `tau=1`; and the Laplace memoryless route
gives `Gamma_1=1+2 sqrt(2)`.  An independent logistic, `m=3`, Route-Q
implementation returned `2.208388950726001`, within `2.7e-11` of the recorded
value.

Lean recompiled 19 intended declarations from the P1/P2/P3/P4 sources.  The
exact axiom set is `propext`, `Classical.choice`, and `Quot.sound`; there is no
`sorry`, `sorryAx`, project scientific axiom, or unsafe shortcut.  The bridge
uses Mathlib's local Lipschitz dominated-integral lemma.  It does not construct
the stopped probability model or discharge L1-L5, matching the documented
boundary.

Arb passed at the stored 160 bits and again independently at 256 bits.  It
certifies only the Laplace memoryless closed form, the uniform defect, and the
finite-support negative-correction witness.  No frozen CUSUM or SR gain is
interval-certified.

## Repository and integrity

`results/verification.json` now records `all_gates_pass=true`: all required
regressions pass, the Level 1-3 aggregate passes, environment-sensitive checks
are reproduced under controlled locale/PATH changes, freeze-scoped suites pass
at their defining revisions, and the known Level-4/archive diagnostics are
unchanged.  The focused P4 suite reported `134 passed, 2 skipped` in that run.
After the adjudication artifacts and G3 narrowing were added, a final isolated
P4 overlay on clean `HEAD` reported `137 passed, 2 skipped`.

All twelve protected trees in `manifest.json` are byte-identical to `HEAD`.
The disclosed near-miss file
`sr_derivative_priority2/derive_closure.py` hashes to
`fe7cef0e936e745b51477c7f3eee718acad7241baf46cc7c17179bc49e57ff31`
in both the worktree and `HEAD`.

## Remaining failed gates and novelty

The remaining failed gates are:

1. `all_theorem_supported_cells_pass` — the original skew-normal cell and nine
   precision-limited `t1p5` cells remain frozen failures.
2. `all_outside_assumption_cells_demonstrate_failure` — Cauchy produces the
   proved non-convergence failure, not the sharp deterministic defect the gate
   was written to detect.
3. `gaussian_consistency_with_closed_core` — the frozen gate uses only P4's
   error bar and treats an older Monte Carlo estimate as exact.

No independent literature search was performed.  The status remains exactly
`NOVELTY-NOT-ADJUDICATED`.
