# Preregistration — P5Y-K1R4

Every step below happened before any genuine bridge result, in this order:
derive q_SR → derive the partition → derive the universe → generate stages → qualify schemas →
replay 369 cells → test bridge acceptance → negative controls → mint authorization → commit → freeze.

## Production (not run here)
* **CUSUM** 1000, 1001: frozen `Aux3Certifier` on the affine-pair records, 256 bits, m ∈ {1,2,3,5}.
* **SR** 2000–2005 on AWS: `driver/k1r4_bridge_worker.run_cell` → `admit()` (freeze identity,
  authorization, runtime, ownership, registry, geometry, identity, universe, T3 inputs) → the generated
  `k1r4_bridge_cellseq.run_group` (frozen worker text). Each cell sealed independently.

## Gates carried over
`G_SCIENCE` (an enclosure reaching 2 halts and is reported, never refined around), `G_COVERAGE`,
`G_BUDGET` (refinement depth 0), `G_GOVERNANCE`, `G_COST` (halt before 150 CPU-h), `G_SCOPE`
(no post-result endpoint, cell, m, threshold, precision, host or theorem change). Plus: freeze and
stage-hash identity checked at every admission.

## Expected cost
6 × 12.705 + 2 × 0.632 ≈ 77.5 CPU-h against the shared 150 CPU-h cap; SR ≈ 13–15 h wall on AWS.

## Disclosure
The q_SR repair, the partition and the universe were all derived from frozen artifacts, and no bridge
result existed at any point. The only prior scientific observation remains the one disclosed in K1R
(the Aux5 statuses behind B1). K1R4 decides nothing about K1.
