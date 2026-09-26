# Frozen scope — P5Y-K1R2

Bound by `config/CHECKPOINT.json`. Nothing below may change after the freeze.

## Inherited from K1R, unchanged (verified by qualification)

* target `sup |R_D,m(e)| < 2`, strict; m universe `{1,2,3,5}`; precision 256 bits
* `B_cover` cap `1/20`; SR radius cap `1/25`; cost cap 150 NEW CPU-h shared with K1R
* CUSUM bridge `(11/2, 49750555/8388608]`, exactly 2 equal children
* SR bridge `(3803026123175981/562949953421312, 1883835/262144]`, exactly 6 equal children
* refinement depth 0; endpoint shrinkage prohibited

## New in K1R2 (execution/governance identity only)

* `CUSUM_BRIDGE_CELL_TABLE.json` — 2 cells at indices 1000–1001, frozen geometry schema
  (`left`, `right`, `e0`, `rho`, `C_evaluation`, `C_upper`, `nominal_step_half_width`)
* `SR_BRIDGE_CELL_TABLE.json` — 6 cells at indices 2000–2005, rho `≈0.0358941 ≤ 1/25`
* `CUSUM_BRIDGE_PRODUCER_CONTRACT.json` + `CUSUM_BRIDGE_CHECKPOINT.json` — bridge-only
  producer identity binding the bridge table hash and the 11-module kernel identity
* `SR_BRIDGE_AUTHORIZATION.json` — new AWS-only run authorization, no handoff, no synthetic
  path, binding the 39-file PS1 executor identity
* `SR_BRIDGE_OWNERSHIP.json` — bridge-only owners map; historical 0–368 refused as new work
* `RUNTIME_CONTRACT.json`, `PREDECESSOR_BINDING.json`, `COST_ACCOUNTING.json`

## Immutable

The frozen cover spec (`p5y_k1_cover_ledger_successor/config/*`), the historical CUSUM
producer identities, the PS1 369-cell table, ledger and authorization, the K1R freeze and
its halt, and B1's inherited PASS. Historical cell ids are **not resolvable as new work** in
either bridge table. Lineage: P5 PARTIAL, P5X PARTIAL, P5Y-K1 PARTIAL,
K1R HALTED_BY_GOVERNANCE after B1 PASS, K1R2 bridge-executor successor.
