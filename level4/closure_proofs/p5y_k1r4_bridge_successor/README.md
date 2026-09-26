# P5Y-K1R4 — bridge successor with the conservative SR overlap repair

K1R3 found, before any freeze or computation, that the K1R SR bridge lower endpoint
`3803026123175981/562949953421312` lay ≈3.0e-17 **above** the exact compact-cover endpoint
`c_SR = log(4581762885148045/8796093022208) + 1/2`, leaving `(c_SR, old endpoint]` uncovered.
K1R4 repairs this prospectively by starting the SR bridge at a rational strictly below `c_SR`
and accepting a declared, redundant, certified overlap.

| | CUSUM | SR |
| --- | --- | --- |
| bridge | `(11/2, 49750555/8388608]` (unchanged) | `[33777657/5000000, 1883835/262144]` |
| cells | 2 (unchanged) | 6, derived by the frozen two-level rule |
| overlap with compact | none (exact rational splice) | `[q_SR, c_SR]`, width 6.4321473e-8 |
| kernel | frozen `CellCertifier`, byte-identical | 7 stages generated from frozen text |
| host | AWS or Vultr (lineage-bound) | AWS only |

## Nothing chosen by hand

* **q_SR** is `floor(c_SR·Q)/Q` on the frozen geometry grid `Q = 10⁷` — the value the frozen cover
  generator itself computed and recorded as `cover_witnesses.detectors.SR.terminal_floor_q = 67555314`.
* **The partition** is the frozen two-level construction: the geometry march from q_SR with the
  frozen step rule and monotone-C rule (2 parents), then RHO_CAP children on the frozen dyadic ladder
  (4 + 2 = 6). Children inherit the parent's `C_upper` and `C_evaluation`, as every historical
  successor cell does.
* **The obligation universe** is produced by the generated T5's own `work_ids`: 19 + 1 + 4 + 4 = 28 per
  cell, reading only `(detector, index)`.

## Qualification

12/12 gates and 15/15 negative controls, including a 369/369 byte-identical historical replay
(t3, t4, t5 files and scientific-content hashes; 0 patch solves) and 6/6 acceptance through the
real production entry. No genuine bridge certificate has been computed; 0.0 genuine CPU-h.
