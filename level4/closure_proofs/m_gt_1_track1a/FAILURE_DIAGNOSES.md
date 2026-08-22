# Failure-first diagnoses

## F1 — independent decomposition pooled `m=20`: FAILED

The direct Stage-D route estimated `Gamma_D(20)=4.26631 ± 0.00668`; the
disjoint reconstruction route estimated `Gamma_B(20)+C_20=4.23676` with the
corresponding independent comparison SE. Their discrepancy was `0.02955 ±
0.00944`, or `3.130` SE. The protocol required every pooled cell to be within
three SE, so the complete numerical verdict is `FAIL`.

This is not an observed algebraic contradiction:

- both independent routes satisfied the decomposition pointwise to floating-
  point roundoff;
- every correction integrand was nonnegative;
- all per-replication comparisons were below four SE;
- the `m=20` per-replication z values were `2.881` and `1.546`; and
- the route discrepancy had the same positive direction across `m` because
  each route intentionally reused its ordinary stopped paths across the grid.

These facts diagnose the failure as an independent-route Monte Carlo
fluctuation consistent with the exact identity, but the frozen threshold is
not waived. No paths were added, no cell was dropped, and no correlated global
test was substituted.

**Protocol changed:** no.  
**Theorem changed:** no.  
**Effect:** mandatory stop; Lean not started; final verdict
`MGT1-TRACK1A-FAILED`.

## F2 — rare-event correction pooling serialization: repaired, not a gate change

One `tau=1` cycle appeared in the two million direct Stage-D paths at `m=2`.
One replicate had no such event and hence a zero empirical SE, while the other
had `C_2=1.51749e-5 ± 1.51749e-5`. The initial report generator treated any
zero-SE replicate as though the pooled correction were the structural zero and
printed `C_2=0`.

After the scientific run had already ended in `FAIL`, the reporting code was
corrected to combine retained count/mean/variance equivalents across the two
equal-size replications for this undefined inverse-variance edge case. It now
reports `C_2=7.58745e-6 ± 7.58745e-6`. The saved checkpoints, seeds, paths,
estimands, distinction result, decomposition discrepancies, and failed verdict
did not change. The deterministic checkpoints were only re-evaluated.

## Historical failure retained

Historical Stage-D D2.3 remains `FAILED` at its frozen primary finite-
difference step. Track 1A neither overwrites nor reinterprets it. The previous
proof track remains `MGT1-THEOREM-PARTIAL`.

