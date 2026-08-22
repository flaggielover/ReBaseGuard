# Final report — general location-family derivative track

## A. Exact Track-3 verdict

```text
LOCATION-FAMILY-THEOREM-PARTIAL
```

The human stopped-score theorem is proved under explicit analytic hypotheses,
the Gaussian reduction and five regular-family numerical cells pass, and the
pooled t3 correspondence is favorable.  The complete frozen gate nevertheless
failed because t3's two independent Route-B replications differed by 4.605%,
above the precommitted 3% relative limit.  Lean was not authorized and was not
started.

The result is not distribution-free, universal, detector-independent, or a
class-wide instability certificate.

## B--D. The theorem, score, and ReBaseGuard derivative

Under the frozen residual convention

```text
Z_t=epsilon_t-e,
f_e(z)=f(z+e),
```

the correctly signed parameter score is

```text
s(z)=d/de log f(z+e)|_0=f'(z)/f(z).
```

Writing the conventional location score as `psi=-f'/f` gives `s=-psi` and

```text
S_tau=sum_{t<=tau}s(Z_t)=-sum_{t<=tau}psi(Z_t).
```

For a fixed measurable residual-path stopping/terminal functional and under
the explicit stopped change-of-measure, integrability, and domination
hypotheses in `THEOREM.md`,

```text
d/de E_e[H_tau]|_0=E_0[H_tau S_tau].
```

For actual raw-observation `m=1` ReBaseGuard reuse,

```text
Gamma_f=E_0[Z_tau sum_{t<=tau}psi(Z_t)]
       =-E_0[Z_tau S_tau],
F'_rho(0)=rho(1-Gamma_f).
```

## E. Role of symmetry

Symmetry is not required for the stopped-score derivative identity or exact
rho scaling.  An even density plus a reflection-equivariant two-sided detector
and odd terminal functional imply oddness of `F_rho` and the fixed point
`F_rho(0)=0`.  Local instability additionally needs that fixed point and

```text
rho|1-Gamma_f|>1.
```

If `Gamma_f>1`, the condition is `Gamma_f>1+1/rho`; for `rho=1`, it is
`Gamma_f>2`.

## F. Gaussian reduction

For `f=phi`, `s(z)=-z`, `psi(z)=z`, and `S_tau=-T_tau`.  Hence

```text
Gamma_f=E_0[Z_tau T_tau],
F'_rho(0)=rho(1-Gamma_f),
```

exactly the existing Gaussian theorem.  The new Gaussian estimate
`15.9375 ± 0.0574` agrees with Stage D's `15.8671 ± 0.0495` at combined
`|z|=0.928` and 0.442% relative discrepancy.

## G. Historical Stage-D t3 ambiguity

The theorem-relevant raw-reuse gain is neither historical candidate:

```text
new Gamma_f                            = 8.7101 ± 0.4632,
historical Gamma_psi                   = 2.5980,
historical Gamma_psi/E[psi']           = 1.2990.
```

Stage D used terminal functional `psi(Z_tau)`; actual `m=1` ReBaseGuard uses
`Z_tau`.  Dividing by `E[psi']` describes the influence-function update of a
different M-estimator rule.  This mathematical distinction was frozen before
Track-3 outcomes.

Historical Stage-D t3 remains `AMBIGUOUS`.  Track 3 does not retroactively
select, repair, or relabel either Stage-D estimand.

## H. Numerical correspondence table

| family | `Gamma_f` | Route A derivative | Route B derivative | correspondence `|z|` | relative | replication relative | result |
|---|---:|---:|---:|---:|---:|---:|---|
| Gaussian | 15.9375 ± 0.0574 | -14.9375 ± 0.0574 | -14.7927 ± 0.0661 | 1.653 | 0.974% | 0.041% | PASS |
| t10 | 15.5459 ± 0.0702 | -14.5459 ± 0.0702 | -14.3312 ± 0.0844 | 1.956 | 1.487% | 0.646% | PASS |
| t5 | 13.3638 ± 0.1588 | -12.3638 ± 0.1588 | -12.1779 ± 0.1106 | 0.961 | 1.515% | 1.234% | PASS |
| **t3** | **8.7101 ± 0.4632** | **-7.7101 ± 0.4632** | **-7.6338 ± 0.1339** | **0.158** | **0.995%** | **4.605%** | **FAIL** |
| contam 5% | 15.3817 ± 0.1431 | -14.3817 ± 0.1431 | -14.7231 ± 0.1116 | 1.882 | 2.346% | 0.854% | PASS |
| contam 10% | 18.3196 ± 0.1172 | -17.3196 ± 0.1172 | -17.1737 ± 0.1362 | 0.812 | 0.846% | 0.157% | PASS |

All fixed-threshold ARLs reproduced within 0.23%, and every tie count was zero.
The retained-summary auditor independently reconstructed the exact single
failed predicate.  Favorable pooled t3 correspondence and `|z|=1.318` between
replications cannot rescue the frozen 4.605% relative failure.

## I. Negative/edge case

Translated centered uniform noise shifts support.  With deterministic
`tau=1`, its interior a.e. log-density score is zero, but
`dE_e[Z_1]/de=-1`.  This exact mismatch shows why common support and local
absolute continuity are necessary.  It is not a regular-family confirmation.

## J--K. Lean declarations and axiom audit

There are no Track-3 Lean declarations.  The protocol authorized Lean only
after an all-family numerical pass, and that gate failed.  Therefore:

```text
Lean status: NOT AUTHORIZED / NOT RUN
Track-3 axiom audit: NOT RUN
```

Existing Gaussian `IntegralBridge` infrastructure remains historical and is
not presented as a general-family formalization.

## L. Human-proved analytic boundary

The human theorem explicitly assumes or proves at the appropriate layer:

- stopped-prefix measurability and parameter-independent residual functional;
- positive absolutely continuous density on locally common support;
- finite-prefix likelihood differentiation;
- almost-sure finiteness;
- absolute summability of event-sliced change of measure;
- integrability of the stopped terminal functional; and
- an integrable dominator for stopped likelihood difference quotients.

The bounded-score corollary plus a geometric CUSUM forcing tail gives a
concrete human route for the Student-t cells.  Gaussian and contaminated-normal
cells use their exponential moments and at-most-linear scores.  None of these
concrete infinite-process obligations is machine-checked in Track 3.

## M. Requirement status

```yaml
general location-family theorem: PARTIAL
human conditional theorem: PROVED
all-family numerical correspondence: FAILED
reusable Lean spine: NOT AUTHORIZED
```

## N. Historical status

No global re-audit was performed.  Level 1--3 remains `CLOSED`; Stage D remains
`STAGE-D-PARTIAL`; D2.3 remains `FAILED`; Stage-D t3 remains `AMBIGUOUS`; Stage
F and overall Level 4 remain `LEVEL-4-PARTIAL`; Proof Tracks 1/1A/1B/2 remain
unchanged; and the rigorous SR instability certificate remains `OPEN`.

## O--Q. Verification, reproduction, and git

The final package contains 37 Track-3 tests.  Together with 168 historical
closure-track tests and 695 authoritative tests, the clean target is 900/900.

Reproduce with:

```bash
bash level4/closure_proofs/location_family/reproduce.sh
```

The frozen numerical-gate commit is
`a515951731c8f182b82fff6107e3144c301bc2da`.  The final closing commit and
push status are recorded by repository history and the completion response.

## R. Strongest publication-safe claim

For a fixed measurable residual-path stopping rule and a regular
one-dimensional location family satisfying explicit stopped
change-of-measure, integrability, and domination conditions, the local
derivative of a stopped functional is its product with the correctly signed
stopped score.  For raw matched `m=1` ReBaseGuard reuse this gives
`F'_rho(0)=rho(1-Gamma_f)`.  A frozen six-family correspondence campaign
supported the identity in pooled comparisons but remained partial because the
t3 independent-replication relative gate failed.

## S. Strongest resume-safe bullet

- Track 3 proved the conditional human identity and resolved the raw-reuse
  estimand as `Gamma_f=E[Z_tau sum psi]`, but is
  `LOCATION-FAMILY-THEOREM-PARTIAL`: t3 failed only the frozen 3% replication-
  relative gate (4.605%), so Lean was correctly not started.

## T. Recommended next proof track

Start a new, separately frozen t3 variance-aware correspondence replication.
Pre-register its sample size and primary precision rule from the retained t3
batch variance before drawing new paths.  Do not edit Track 3 or relabel its
failure.  Only a new passing gate should authorize the reusable general Lean
spine.
