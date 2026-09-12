# PS1 production namespace (PRE-RESULT, 0 genuine cells)

Additive production package for the full PS1 SR campaign (369 predeclared successor cells). Scientific identity is
unchanged: the per-patch function is the frozen T2-closed certifier with bit-identical memoisation, and T3
aggregation, T4 and T5 are the committed PS1 successor stages.

| path | role |
|---|---|
| `driver/production_launcher.py` | NEW PS1 launcher: preflight gates, per-cell admission, persistent pinned pool, from-disk verification, sealing |
| `driver/ps1_pool_worker.py` | NEW persistent worker: fresh-interpreter precision/thread probe, one cell group per task, JSON-file transport |
| `driver/multihost.py` | GENERATED from the historical accounting module (`code/make_multihost.py`); only PS1 constants substituted |
| `driver/global_budget.py`, `production_provenance.py`, `handoff.py` | byte-identical copies of the historical modules |
| `config/PS1_CONSTANTS.json` | measured-cost derived cap, overhead, reservation, host roles (`code/make_constants.py`) |
| `config/SHARD_MANIFEST.json` | 369 cells, all AWS; 93 deterministic groups (`code/make_shard_manifest.py`) |
| `config/protocol.json` | the pre-result production protocol (`code/make_protocol.py`) |
| `config/LAUNCH_AUTHORIZATION.json` | binds the producer commit and every identity (`code/make_authorization.py`), added in the authorization commit |
| `production/` | genuine result namespace (ledger + sealed cell records); EMPTY at freeze |
| `tests/test_ps1_production.py` | result-free acceptance |

Production is started ONLY through the PS1 lifecycle adapter (`../p5y_k1_ps1_lifecycle_adapter`) after the final
authorization record says YES. Nothing in this namespace starts it.
