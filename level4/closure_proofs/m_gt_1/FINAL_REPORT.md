# Final report — Stage-D `m>1` derivative closure proof

## 1. Exact decision

`MGT1-THEOREM-PARTIAL`

The correct formula was derived and human-proved, and its primary independent
numerical derivative correspondence passed at all eight window lengths. The
complete frozen numerical gate nevertheless failed an auxiliary
Stage-A/Stage-D separation threshold, so the campaign stopped before Lean.

## 2. Historical problem being repaired

Historical Stage D adopted an ordinary alarm time and a truncated window, but
mixed two different `Gamma_m` formulas: the direct random-denominator statistic
and a fixed-denominator lag average. Its pre-specified D2.3 finite-difference
test failed at all eight `m` values. This campaign is a new result and does not
rewrite Stage D.

## 3. Stage A versus Stage D

Stage A suppresses alarms before `m` and uses
`tau_m=inf{t>=m: alarm}`, so the stopped window always contains exactly `m`
observations. Stage D keeps the ordinary `tau=inf{t>=1: alarm}` and uses the
random length `w=min(m,tau)`. The maps coincide at `m=1` and differ in
definition for `m>1`.

## 4. Exact Stage-D reuse definition

\[
 A_m=\frac1{\min(m,\tau)}
      \sum_{r=0}^{\min(m,\tau)-1}Z_{\tau-r},
\]

\[
 E^+=\rho(e+A_m)+(1-\rho)\bar Y_m,
 \qquad E\bar Y_m=0.
\]

When `tau<m`, the reuse statistic is `A_m=T_tau/tau`; its denominator is
`w=tau`, not `m`. The reused reference includes the current reference `e`
additively.

## 5. The theorem

For every fixed positive integer `m` and `rho in [0,1]`, under the frozen
Gaussian CUSUM,

\[
 \boxed{F'_{\rho,m}(0)=\rho(1-\widetilde\Gamma_m)},
 \qquad
 \widetilde\Gamma_m=E_0[A_mT_\tau].
\]

Equivalently,

\[
 \boxed{F'_{\rho,m}(0)=\rho\left[
 1-\frac1m\sum_{r=0}^{m-1}\gamma_r-C_m\right]},
\]

where

\[
 \gamma_r=E_0[\mathbf1_{\{\tau>r\}}Z_{\tau-r}T_\tau],
 \quad
 C_m=E_0\left[\mathbf1_{\{\tau<m\}}
 (\tau^{-1}-m^{-1})T_\tau^2\right].
\]

## 6. Human proof

On the stopped sigma-field, the Gaussian location likelihood ratio is

\[
 L_e=\exp(-eT_\tau-e^2\tau/2).
\]

Therefore `F_{rho,m}(e)=rho[e+E_0(A_mL_e)]`. Each fixed lag-selected coordinate
is in `L2`: a stopping-slice Cauchy–Schwarz bound uses the Gaussian fourth
moment and the existing exponential tail of `tau`. Since `m` is fixed, Jensen
then gives `A_m in L2`. This combines with the existing exponential moments of
`T_tau` and `tau` to dominate

\[
 |A_m|(|T_\tau|+\delta\tau)e^{\delta|T_\tau|}
\]

for sufficiently small `delta`. Differentiation under the stopped expectation
is justified and `L'_0=-T_tau`, yielding the theorem. Splitting the window
normalization on `{tau<m}` proves the exact correction formula. Full details
are in `THEOREM.md`.

Gaussianity enters the likelihood ratio and moment bound; rho scaling and the
short-cycle algebra are distribution-free.

## 7. Proof obligations

Ten obligations are human-proved, including definitions, measurability,
integrability, differentiation under stopping, score representation,
short-cycle handling, rho scaling, m=1 reduction, lag decomposition, and the
final identity. M11 is `FAILED` because the complete numerical gate failed an
auxiliary check. M12 remains `OPEN` because Lean was not authorized past that
gate. M13 is not applicable because no new rigorous scalar inequality is
claimed.

## 8. Numerical correspondence

The primary theorem test passed strongly. Across `m={1,2,5,10,20,50,75,100}`:

- pooled theorem/direct-map discrepancies were `0.058–0.352` combined SE;
- every individual replicate discrepancy was below `0.99` combined SE;
- the two direct-derivative replications agreed within `1.43` combined SE;
- discrepancy shrank on both coarse step transitions for `8/8` `m` values;
- median observed convergence order was `1.675`;
- rho scaling held with maximum sample-level error `0.0`.

The complete numerical gate was `FAIL`, because the pre-exposure auxiliary
Stage-A/Stage-D difference check required every cell to exceed five SE. At
`m=20`, the two cells reached `4.73` and `3.20` SE. No pooling, retuning, or
sample-size increase was substituted after exposure.

## 9. `m=1` reduction

At `m=1`, `A_1=Z_tau`, `C_1=0`, and
`widetilde Gamma_1=E_0[Z_tau T_tau]`. The new estimate
`15.88769 ± 0.02850` agreed with the historical independent estimate
`15.85436 ± 0.02853` within `0.827` combined SE.

## 10. Role of `tau<m`

Short cycles change the denominator from `m` to `tau` and add exactly the
nonnegative correction `C_m` to the fixed-denominator lag average. Estimated
`C_m` rose from `0.00260` at `m=5` to `0.32884` at `m=100`. At `m=2`, no
`tau=1` event appeared in two million paths; this is expected with probability
`0.9269` because `P(tau=1)=2 Phi(-5.5)`.

Short cycles do not add a term beyond `widetilde Gamma_m`; they explain the
difference between the direct Stage-D scalar and the historical lag formula.

## 11. Rho scaling

Rho scaling is exact:

\[
 F_{\rho,m}(e)=\rho F_{1,m}(e),\qquad
 F'_{\rho,m}(0)=\rho F'_{1,m}(0).
\]

It follows from the frozen affine update and zero mean of the fresh reference,
not from an approximation.

## 12. Lean status

`NOT STARTED — NUMERICAL GATE NOT MET`.

No Lean file, placeholder, new axiom, or failed elaboration was created. This
is a protocol stop, not a Mathlib obstruction.

## 13. Arb status

`NOT STARTED / NOT REQUIRED FOR THE CLAIM MADE`.

The campaign claims a structural identity, not a new `m>1` stability or
instability inequality. The existing `m=1` certificate remains historical
regression evidence only.

## 14. Failed routes and checks

1. The auxiliary observed-short-cycle check failed at `m=2` because its
   expected event count was only `0.07596`; this is low power, not a theorem
   contradiction.
2. The Stage-A/Stage-D separation threshold failed at `m=20` in both
   replications. The pooled difference is `5.61` SE, but pooling was not the
   implemented frozen per-cell rule and is not substituted.

The initial result-serialization exception was a trivial NumPy scalar encoding
defect, exposed no numerical value, and changed no scientific code or rule.

## 15. Relationship to historical D2.3

Historical Stage D D2.3 remains `FAILED`. The correct wording is:

> A later closure-proof campaign derived and validated a corrected `m>1`
> derivative theorem under the Stage-D truncated-window convention, but its
> complete frozen closure gate remained partial.

The historical finite-difference result is not relabelled or overwritten.

## 16. Strongest new claim

The Stage-D truncated-window conditional-mean map has the human-proved
derivative representation

\[
 F'_{\rho,m}(0)=\rho(1-E_0[A_mT_\tau]),
\]

and an independently seeded, pre-specified central-difference experiment
confirmed this representation at all eight tested window lengths by less than
`0.36` combined SE in pooled comparisons.

## 17. Claims not supported

This campaign does not support a machine-checked frozen-CUSUM `m>1` corollary,
a new interval-certified inequality, an SR derivative theorem, an `m-rho`
phase map, a general location-family theorem, detector independence,
distribution-free theory, an operational transition at the `Gamma_m=2`
crossing, or overall Level-4 closure.

## 18. Remaining blockers

The complete correspondence gate needs a new independently frozen replication
whose Stage-A/Stage-D distinction design has adequate power and an outcome-blind
aggregation rule. Only after it passes may the already scoped Lean spine begin.

## 19. Reproduction

```bash
bash level4/closure_proofs/m_gt_1/reproduce.sh --resume
```

The script runs the isolated tests, reuses deterministic phase checkpoints,
re-evaluates every frozen criterion, and exits successfully only when it
reproduces the recorded numerical `FAIL` and partial proof-track decision.
Use the runner directly to receive its raw exit code `2` for the frozen gate:

```bash
level4/.venv/bin/python \
  level4/closure_proofs/m_gt_1/numerics/run_correspondence.py --resume
```

## 20. Previously unmet Level-4 requirement

This result does **not** close the previously unmet `m>1 derivative theorem`
requirement under the campaign's own closure rule. It materially advances the
requirement: the correct human theorem and its central numerical
correspondence are established, but the complete numerical gate failed and the
mandatory Lean spine remains open.

## 21. Verification and artifacts

The campaign adds 46 isolated tests. Together with the unchanged authoritative
695-test baseline, the verified full count is 741 passing tests. Entry points
are `DEFINITION_AUDIT.md`, `PROTOCOL.md`, `THEOREM.md`,
`CORRESPONDENCE_REPORT.md`, `PROOF_OBLIGATIONS.md`, and this report. Machine
decisions and raw results are under `results/`.

## 22. Next recommended proof track

**Proof Track 1A — Stage-A/Stage-D Distinction Replication and Lean Completion**
