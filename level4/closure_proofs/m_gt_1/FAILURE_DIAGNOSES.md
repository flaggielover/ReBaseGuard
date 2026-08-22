# Failure-first record

## Historical failure retained as provenance

Historical Stage D D2.3 remains `FAILED`: its pre-specified primary central
difference at `h=0.05` agreed at `0/8` window lengths. The stored diagnosis is
`O(h^2)` finite-difference truncation bias; Richardson was diagnostic only.
This campaign does not alter the result, protocol, report, or decision.

## New campaign failures

### N1 — observed-short-cycle check at `m=2`: FAILED, low power

No `tau=1` cycle was observed in the two million Route-A paths. At `m=2`, this
is the only short-cycle event. Its exact probability is
`2 Phi(-5.5)=3.7979e-8`, so the expected count was only `0.07596` and the
probability of zero was `0.9269`. The pointwise correction identity passed, and
short cycles were observed from `m=5` onward.

**Theorem changed:** no.
**Protocol changed:** no.
**Effect:** retained as a failed overstrict implementation check. It is not a
mathematical counterexample.

### N2 — Stage-A/Stage-D map-separation threshold: FAILED

At `m=100`, both independent comparisons passed decisively (`49.05` and
`46.88` SE). At `m=20`, the point estimates differed in the expected direction
but reached only `4.73` and `3.20` combined SE, below the implemented frozen
five-SE per-cell requirement. The pooled `m=20` value is `5.61` SE, but pooling
was not substituted after exposure.

**Theorem changed:** no.
**Protocol changed:** no.
**Effect:** the complete numerical gate is `FAIL`; Lean was not started; final
decision is `MGT1-THEOREM-PARTIAL`.

The earlier JSON-serialization exception is not retained as a scientific
failure: it occurred after computation, exposed no value, changed no scientific
code or criterion, and was fixed only by converting NumPy scalar types during
serialization. The identical deterministic seeds were rerun.
