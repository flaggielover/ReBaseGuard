# Frozen scope — P5Y-K1R

Everything below is fixed by `config/CHECKPOINT.json` and may not change after the freeze.

## Science (inherited, unchanged)

* theorem target: `sup |R_D,m(e)| < 2`, strict, target `2/1`
* detector universe: `{CUSUM, SR}`; m universe: `{1, 2, 3, 5}`
* precision: 256 bits; `B_cover` cap: `1/20`; SR radius cap `r_max = 1/25`
* far field: **P5X-T3, inherited and NOT modified**

## Domains (exact rationals, no shrinkage)

| detector | compact (inherited) | K1R bridge | far field (inherited) |
| --- | --- | --- | --- |
| CUSUM | `[0, 11/2]` | `(11/2, 49750555/8388608]`, 2 cells | `[49750555/8388608, ∞)` |
| SR | `[0, c_SR]` | `(c_SR, 1883835/262144]`, 6 cells | `[1883835/262144, ∞)` |

Endpoint ownership: the compact segment owns `c`; the bridge owns the open interval up to
`e_close`; the far field owns `e_close` itself. The bridge's closed upper endpoint is a
declared redundant overlap, so no point is omitted and no point has ambiguous ownership.

## Partitions

* CUSUM: 2 equal children, width `3613211/16777216` (≈0.2153642), rho ≈0.1076821
* SR: 6 equal children, rho `≈0.0358941 ≤ 1/25` — the frozen radius cap holds for every child
* refinement depth: **0**. Adaptive refinement after results is prohibited; a cell that
  fails its frozen budget HALTS K1R and is reported, never re-split.

## Hosts

* SR bridge: **AWS only**. No Vultr substitution (cross-host bit identity FAIL; Vultr owns no
  SR cells). Executor identity = the qualified PS1 lineage: 39-file manifest, adapter
  `13ba2ecd…`, producer `c9b12670`, checkpoint `1c2a6825…`.
* CUSUM bridge and B1 fallback: the qualified CUSUM runtime of the producer lineage selected
  by the admission decision, with producer/kernel/libc identity binding.
* The Mac is never a scientific producer.

## Cost

Cap **150 CPU-h**; expected 77.5 (1.26 CUSUM + 76.2 SR), plus 3.2 if the B1 fallback runs.
Consumed at freeze: **0.0**. Admitted inherited evidence costs nothing. K1R has no claim on
the PS1 6600 CPU-h cap.

## Immutable

P5 = PARTIAL, P5X = PARTIAL, P5Y-K1 = PARTIAL. The adjudication (`K1_THEOREM_SCOPE` PASS,
`PS1_SUCCESSOR_VALIDITY` PASS, `SR_PS1_K1` PASS, `K1_GOVERNANCE` PASS, `CUSUM_K1` INCOMPLETE,
`K1_FAR_FIELD` FAIL, verdict `K1_PARTIAL` at commit `15e70072`) is authoritative and is not
restated, weakened or overturned by K1R.
