# Level-4 scoped report: general location-family derivative theorem

## Outcome

```text
LOCATION-FAMILY-THEOREM-PARTIAL
```

For residuals `Z=epsilon-e` with density `f_e(z)=f(z+e)`, the parameter score
is `s=f'/f=-psi`.  Under explicit stopped change-of-measure, integrability, and
domination hypotheses, the human theorem proves

```text
d/de E_e[H_tau]|_0=E_0[H_tau sum s(Z_t)].
```

For actual raw-observation `m=1` ReBaseGuard reuse,

```text
Gamma_f=E[Z_tau sum psi(Z_t)],
F'_rho(0)=rho(1-Gamma_f).
```

This reduces exactly to the closed Gaussian formula.  It also resolves the
new theorem's estimand question: neither historical Stage-D t3 quantity is the
raw-reuse gain, because both use `psi(Z_tau)` rather than `Z_tau`.  Historical
t3 remains `AMBIGUOUS`.

The frozen numerical campaign passed five of six regular families.  t3's
pooled score/direct correspondence passed (`|z|=0.158`, 0.995%), but its two
independent direct replications differed by 4.605%, above the frozen 3% relative
limit.  The numerical gate therefore failed.  Lean was not authorized and was
not run.

The result is not distribution-free, universal, detector-independent, or an
instability certificate for a class.  Stage D/F and Proof Tracks 1--2 remain
unchanged; overall Level 4 remains `LEVEL-4-PARTIAL`.

See `level4/closure_proofs/location_family/FINAL_REPORT.md` for the complete
evidence and assumption boundary.

