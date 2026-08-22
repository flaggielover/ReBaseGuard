# Symmetric SR derivative closure campaign

This namespace contains Proof Track 2 of the Level-4 closure campaign: the
local derivative theorem for the frozen symmetric two-chart
Shiryaev--Roberts detector with one-observation reuse.

The closure target is `SR-DERIVATIVE-CLOSED`.  It means that the frozen
definition/code correspondence, human stopped-score proof, independent
numerical correspondence, symmetry and rho scaling, conditional Lean proof
spine, axiom audit, and repository verification have all closed.

Arb is a separate, non-blocking rigor upgrade.  Unless its certificate is
successfully completed at the authoritative Stage D threshold
`A = 520.886133602749`, the only permitted scalar status is:

```yaml
derivative theorem: CLOSED
Gamma_SR > 2: CONFIRMATORY NUMERICAL
rigorous SR instability certificate: OPEN
```

An eventual successful certificate adds `SR-GAMMA-CERTIFIED`; it does not
change the meaning of `SR-DERIVATIVE-CLOSED`.

## Order of work

1. audit and freeze the exact detector/reuse correspondence;
2. freeze and hash `PROTOCOL.md` before confirmatory outcomes;
3. prove the concrete analytic theorem and discharge its human obligations;
4. run the two independent numerical routes and close their gates;
5. only then formalize the conditional Lean proof spine;
6. only after Lean, attempt the optional Arb certificate; and
7. reproduce all artifacts and run the authoritative repository verifier.

No Track-2 confirmatory numerical outcome existed when the protocol was
frozen.

