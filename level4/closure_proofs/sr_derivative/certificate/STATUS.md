# Optional Arb certificate status

```yaml
additional_status: NOT AWARDED
Gamma_SR > 2: CONFIRMATORY NUMERICAL
rigorous SR local-instability certificate: OPEN
```

The authoritative-threshold Arb attempt was executed at the exact runtime
rational

```text
4581762885148045 / 8796093022208
```

corresponding to the Stage D label `A=520.886133602749`.  It did not use the
historical `520.3125` threshold.

The attempt successfully recomputed outward-rounded reachable-geometry
constants, the forcing bound, a fresh exact-dyadic degree-16 candidate, and
representative Arb residual cells.  An independently written auditor verified
the threshold serialization, candidate digest and symmetry, geometry overlap,
and the explicit absence of a certificate claim.

It did not produce the required exact global patch cover, certified global
residual suprema, sharp certified resolvent/error propagation, or a final
`Gamma_SR` interval with strict lower endpoint above two.  Representative
cells cannot substitute for a continuum supremum.

Consequently `SR-GAMMA-CERTIFIED` is not recorded.  This OPEN status is
non-blocking for `SR-DERIVATIVE-CLOSED`.

