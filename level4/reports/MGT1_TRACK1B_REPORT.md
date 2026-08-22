# Proof Track 1B final report

## A. Track verdict

`MGT1-TRACK1B-CLOSED`

Every frozen closure criterion passed. This is an isolated closure of the
`m>1` derivative-theorem requirement, not a global Level-4 re-audit.

## B. Track 1A's `3.130` discrepancy

It was not explained by an omitted covariance term. Track 1A compared a
direct estimator and a fixed-plus-correction estimator generated from
disjoint seed families, stopped paths, `tau`, `T_tau`, lags, short-cycle
events, and batches. Its sampling covariance was zero by design, so the
frozen `3.1302795226595075 > 3` result remains failed.

The common positive direction across `m` is consistent with route-level Monte
Carlo fluctuation propagated through a cross-`m`-correlated grid. That is a
diagnosis, not a reinterpretation or pass.

## C. Covariance sign and magnitude

For the estimators actually compared in Track 1A, `Cov(X,Y)=0` by design.

For Track 1B Route P, same-path covariance was positive and essentially
maximal. Batch covariances for `m={1,2,5,10,20,50}` were
`{0.063138,0.044595,0.025402,0.010202,0.003528,0.001008}` and all correlations
were one to printed precision (minimum `0.9999999999999999`).

## D. Old combined-SE calculation

Valid. Track 1A correctly used
`sqrt(SE_X^2+SE_Y^2)` for independent routes. In Track 1B's paired route, the
correct calculation is

`Var(X-Y)=Var(X)+Var(Y)-2Cov(X,Y)`.

Ignoring its positive covariance would be strongly conservative.

## E. Paired replication by `m`

| `m` | mean direct−reconstruction | paired SE | naive independent SE | covariance | correlation |
|---:|---:|---:|---:|---:|---:|
| 1 | 0 | 0 | 0.044419 | 0.063138 | 1.000000000 |
| 2 | +2.22e-16 | 2.29e-16 | 0.037331 | 0.044595 | 1.000000000 |
| 5 | -3.33e-16 | 1.93e-16 | 0.028174 | 0.025402 | 1.000000000 |
| 10 | +1.11e-16 | 1.58e-16 | 0.017856 | 0.010202 | 1.000000000 |
| 20 | -6.94e-17 | 8.91e-17 | 0.010500 | 0.003528 | 1.000000000 |
| 50 | -2.78e-17 | 4.73e-17 | 0.005611 | 0.001008 | 1.000000000 |

Maximum pathwise discrepancy was `8.53e-14`; maximum batch-mean discrepancy
was `5.33e-15`. Alignment, covariance identity, correction sign, and all
roundoff gates passed.

## F. Independent-route cross-check by `m`

| `m` | direct | reconstruction | difference ± SE | marginal z | relative discrepancy |
|---:|---:|---:|---:|---:|---:|
| 1 | 15.84199 | 15.92487 | -0.08288 ± 0.04377 | -1.894 | 0.522% |
| 2 | 13.21139 | 13.27364 | -0.06225 ± 0.03735 | -1.667 | 0.470% |
| 5 | 10.15878 | 10.20356 | -0.04478 ± 0.02717 | -1.648 | 0.440% |
| 10 | 7.06623 | 7.10949 | -0.04326 ± 0.01624 | -2.664 | 0.610% |
| 20 | 4.24120 | 4.26833 | -0.02713 ± 0.00956 | -2.837 | 0.638% |
| 50 | 2.35172 | 2.36321 | -0.01149 ± 0.00465 | -2.469 | 0.487% |

The frozen six-dimensional Hotelling test gave `T²=15.2599`, condition number
`774.8`, and `p=0.043014 >= 0.01`. The two routes used separately implemented
calculations and disjoint seeds. Per-cell z-values are retained diagnostics,
not verdict criteria.

## G. Short-cycle correction replication

| `m` | `P(tau<m)` | `C_m ± batch SE` |
|---:|---:|---:|
| 1 | 0 | 0 exactly |
| 2 | 0 observed | 0 observed |
| 5 | 0.0007194 | 0.00273995 ± 0.00009062 |
| 10 | 0.0074238 | 0.02316266 ± 0.00029840 |
| 20 | 0.0277331 | 0.07834101 ± 0.00055082 |
| 50 | 0.0896331 | 0.20263707 ± 0.00088520 |

Every correction integrand was nonnegative. Track 1A comparators were not
pooled into these results.

## H. Stage-A/Stage-D distinction replication

| `m` | `Gamma_D-Gamma_A ± SE` | 95% CI | standardized effect |
|---:|---:|---:|---:|
| 1 | -0.04010 ± 0.04943 | [-0.13698,+0.05679] | -0.00099 |
| 2 | -0.09218 ± 0.04444 | [-0.17927,-0.00508] | -0.00275 |
| 5 | -0.01412 ± 0.03591 | [-0.08451,+0.05627] | -0.00056 |
| 10 | +0.01130 ± 0.02351 | [-0.03477,+0.05737] | +0.00068 |
| 20 | +0.05058 ± 0.01206 | [+0.02694,+0.07421] | +0.00534 |
| 50 | +0.13340 ± 0.00608 | [+0.12148,+0.14532] | +0.02824 |

The `m=20,50` directions replicate Track 1A. The opposite-sign `m=2`
inconsistency is preserved. This check was pre-registered as secondary and did
not control the numerical gate.

## I. `m=1` control

`PASS`. On the shared structural stream, Stage A and Stage D had identical
`tau`, `T_tau`, lags, and gain integrands. Direct and reconstructed values
agreed exactly, and `C_1=0`. The human and Lean theorem reduce to
`F'_{rho,1}(0)=rho(1-E_0[Z_tau T_tau])`.

## J. Lean status

`PASS — COMPILED STABLE SPINE`.

Lean checks `w=min(m,tau)`, the short/long partition, the whole-path
short-cycle consequence, pointwise and expectation decompositions,
nonnegativity, `m=1`, rho scaling, and derivative-map algebra. It reuses the
existing proved stopped-integral differentiation bridge.

This is classification B: a checked algebraic consequence of a general
dominated-differentiation lemma. It is not a fully instantiated, end-to-end
machine proof of the concrete frozen-CUSUM random-window derivative theorem.

## K. Exact axioms and assumptions remaining

`#print axioms` reports exactly `propext`, `Classical.choice`, and `Quot.sound`
for each of the four audited headline theorems. No project-specific axiom,
`sorry`, or `admit` exists.

For the concrete CUSUM application, Lean still receives rather than derives:

- the mapping from stopped paths to the random-window `A_m`;
- a.e. strong measurability of `A_m`, `T_tau`, and real-valued `tau`;
- integrability of `A_m`; and
- a uniform integrable dominator for the likelihood-integrand derivative near
  zero.

Those application obligations are supplied by the human theorem and prior
stopped-moment analysis. The complete concrete theorem is therefore not
called machine-checked.

## L. Arb status

`NOT REQUIRED`. Track 1B makes no new rigorously interval-certified numerical
inequality claim.

## M. Scoped `m>1` derivative-theorem requirement

`CLOSED`

The combined human proof, Track 1 correspondence, Track 1A distinction and
failure record, fresh covariance-aware paired replication, independent-route
cross-check, and compiled transparent Lean spine close this isolated
requirement. No overall Level-4 re-audit was performed.

## N. Historical D2.3

`FAILED`, unchanged. Proof Track 1 remains `MGT1-THEOREM-PARTIAL`; Proof Track
1A remains `MGT1-TRACK1A-FAILED`; Stage F remains `LEVEL-4-PARTIAL` with its
frozen pre-Track-1B ledger unchanged.

## O. Tests

- authoritative repository verifier: 695/695;
- Proof Track 1: 46/46;
- Proof Track 1A: 32/32;
- Proof Track 1B: 32/32;
- combined executed count: 805/805.

The one-command Track 1B reproducer passed the expected historical decisions,
resumed the frozen Track 1B result, compiled Lean, and enforced the axiom
allowlist. The authoritative verifier reported a clean worktree and intact
history.

## P. Artifact entry points

- `level4/closure_proofs/m_gt_1_track1b/REPLICATION_REPORT.md`
- `level4/closure_proofs/m_gt_1_track1b/COVARIANCE_AUDIT.md`
- `level4/closure_proofs/m_gt_1_track1b/THEOREM.md`
- `level4/closure_proofs/m_gt_1_track1b/LEAN_CORRESPONDENCE.md`
- `level4/closure_proofs/m_gt_1_track1b/PROOF_OBLIGATIONS.md`
- `level4/closure_proofs/m_gt_1_track1b/FAILURE_DIAGNOSES.md`
- `level4/closure_proofs/m_gt_1_track1b/results/decision.json`
- `level4/closure_proofs/m_gt_1_track1b/reproduce.sh`

## Q. Git

The frozen protocol (`253694e`), numerical gate (`f81d689`), Lean closure
(`5ee899a`), and historical-freeze integration fix (`d480129`) were committed
and pushed to `origin/main`. This final report and verified decision are the
final green checkpoint; history was not rewritten.

## R. Next proof track

**Proof Track 2 — Symmetric Two-Chart Shiryaev–Roberts Derivative Theorem**
