# Failure-first diagnoses

## F1 — historical Track 1A `m=20`: FAILED and unexplained by covariance

Track 1A's frozen independent-route discrepancy remains
`3.1302795226595075 > 3`. Its direct and reconstruction routes used disjoint
seed families and stopped paths, so their covariance was zero by design and
the old quadrature SE was valid. No covariance correction changes that result.

The cross-`m` grid reused trajectories within each route, making the six
cellwise deviations correlated. A route-level Monte Carlo fluctuation is
consistent with the observed same-direction differences, but is a diagnosis,
not a waiver. Track 1A remains `MGT1-TRACK1A-FAILED`.

## F2 — an independence variance model would fail for Route P

Track 1B's same-path direct and reconstruction values have positive, nearly
maximal covariance. Treating them as independent would overstate the SE of
their difference by many orders of magnitude. Route P therefore uses

`Var(X-Y)=Var(X)+Var(Y)-2Cov(X,Y)`

and verifies this formula against the directly computed batch differences.
This invalid hypothetical model was not the model used by Track 1A.

## F3 — first Track 1B independent-route discrepancies retained

All independent-route point differences were negative. The marginal z-values
were `-1.894, -1.667, -1.648, -2.664, -2.837, -2.469` over
`m={1,2,5,10,20,50}`. The full frozen six-dimensional test passed with
`p=0.043014`; no cell, batch, or path was removed. These discrepancies remain
in `results/replication.json` and `REPLICATION_REPORT.md`.

## F4 — secondary Stage-A/Stage-D `m=2` inconsistency

Track 1B estimated `Gamma_D-Gamma_A=-0.09218 ± 0.04444` at `m=2`, with 95%
CI `[-0.17927,-0.00508]`. This is opposite to Track 1A's point direction.
The distinction check was pre-registered as secondary and does not control
the gate. With no Track 1B short cycle observed at `m=2`, the discrepancy
concerns the stopping-time distinction, not the denominator correction.

## F5 — initial Lean formulations failed locally and were repaired

The first elaboration exposed two proof-level issues:

1. simplification did not close correction nonnegativity after the short-cycle
   branch; the proof now explicitly combines reciprocal-order nonnegativity
   with `sq_nonneg T`;
2. rho derivative scaling did not match syntactically; the proof now uses
   `HasDerivAt.const_mul` followed by normalization of subtraction.

The next compilation passed. A later standalone audit invocation initially
failed to find the sibling module because the campaign lives outside the Lake
package root; the reproducer now supplies an explicit module root and
`LEAN_PATH`. This was build wiring, not a theorem failure.

## F6 — analytic assumptions discovered during formalization

The existing `IntegralBridge` proves dominated differentiation only after
receiving measurability, integrability, a positive neighborhood, and a uniform
integrable derivative dominator. Track 1B exposes those hypotheses but does
not instantiate them for the concrete random-window CUSUM statistic. The
human theorem relies on prior stopped-moment work for that application.

Therefore the complete frozen-CUSUM derivative theorem is not described as
machine-checked end to end. The Lean result is the compiled stable spine and
conditional analytic bridge.

## Historical failure retained

Stage-D D2.3 remains `FAILED`; Proof Track 1 remains
`MGT1-THEOREM-PARTIAL`; Stage F remains `LEVEL-4-PARTIAL`. Track 1B performs
no global Level-4 re-audit.
