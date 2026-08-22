# Level-4 scoped report: symmetric SR derivative theorem

## Outcome

```text
SR-DERIVATIVE-CLOSED
```

For the authoritative symmetric two-chart SR detector at
`A=520.886133602749` and matched one-observation reuse, the closed theorem is

```text
Gamma_SR = E_0[Z_tau T_tau],
F'_rho(0) = rho(1-Gamma_SR).
```

The evidence chain comprises frozen source correspondence, a concrete human
stopped-score proof, exact reflection/rho structure, independent raw-score and
log-map numerics, and a compiled conditional Lean spine with a standard-axiom
audit.

The primary independent numerical comparison was:

| Route | Derivative estimate | Batch SE |
|---|---:|---:|
| raw stopped-score prediction | -16.291321 | 0.027569 |
| independent log conditional map, `h=0.0125` | -16.195010 | 0.039059 |

The pooled discrepancy was `|z|=2.015` and `0.591%`; both independent log
replications and every structural/calibration gate passed.  Exact ties were
zero.

The Lean result is conditional over explicit analytic hypotheses.  The
concrete infinite SR measurability, tail, moment, change-of-measure, and
domination arguments remain human-proved and are not called end-to-end Lean
formalization.

The post-Lean Arb attempt used the exact current runtime threshold rational but
did not complete a global residual cover/certificate.  Therefore the final
boundary is:

```yaml
derivative theorem: CLOSED
Gamma_SR > 2: CONFIRMATORY NUMERICAL
rigorous SR local-instability certificate: OPEN
```

No SR instability claim is certified or rigorous.  `SR-GAMMA-CERTIFIED` is not
awarded.

Full reproduction passed 863/863 checks: 168 isolated closure-track tests plus
the authoritative 695-test verifier.  D2.3, Stage D, and Stage F remain
historically unchanged; overall Level 4 remains `LEVEL-4-PARTIAL` because this
was a scoped theorem campaign, not a global re-audit.

The complete evidence and caveats are in
`level4/closure_proofs/sr_derivative/FINAL_REPORT.md`.
