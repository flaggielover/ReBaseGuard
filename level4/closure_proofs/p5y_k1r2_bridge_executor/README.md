# P5Y-K1R2 — bridge executor successor

K1R halted correctly under `G_GOVERNANCE` before any bridge computation: the qualified
CUSUM producer resolves cells only from the frozen 326-cell `spec.CELLS` (whose sha256 is
bound into its producer identity and cover-geometry gate), and the PS1 SR worker refuses
any cell outside the frozen 369-cell table and owners map. Neither can be extended without
mutating a frozen artifact.

K1R2 is additive and changes **execution and governance identity only**. It supplies
bridge-only cell tables so the *same* kernels can be called on the *same* frozen bridge
intervals.

| | CUSUM bridge | SR bridge |
| --- | --- | --- |
| domain | `(11/2, 49750555/8388608]` | `(c_SR, 1883835/262144]` |
| cells | 2, indices 1000–1001 | 6, indices 2000–2005 |
| hosts | AWS or Vultr (lineage-bound) | **AWS only** |
| kernel | 11 modules, byte-identical | 39-file PS1 executor, byte-identical |

`c_SR = 3803026123175981/562949953421312`.

Inherited unchanged: target `sup |R_D,m(e)| < 2`, m ∈ {1,2,3,5}, 256-bit precision,
`B_cover` cap 1/20, SR radius cap 1/25, 150 CPU-h shared cap.

## Where C_upper came from

Bridge cells need the same geometry input the frozen cover carried per cell. It is computed
by the **frozen cover-geometry routines themselves** — `drift_monotone_resolvent` (CUSUM) and
`sr_drift_monotone_resolvent` (SR) at 192-bit workprec under python-flint 0.9.0, the exact
call the frozen generator used — then rounded up on the frozen `2^32` denominator and capped
by the frozen monotone rule against the last frozen cell (CUSUM 325, SR 368). This is cover
geometry, declared non-decisive by the original design ("Only Bellman geometry … no K1 object
solves"); no obligation, certificate or status is produced. Each bridge cell's width is also
checked against the frozen step rule `Q·A_DEN·C_DEN / (2·a_num·C_num)` and passes.

## Status

Qualification only: 20/20 checks, `production_started = false`, 0.0 new CPU-h, no bridge
result. K1 stays PARTIAL; K1R stays HALTED_BY_GOVERNANCE after B1 PASS.
