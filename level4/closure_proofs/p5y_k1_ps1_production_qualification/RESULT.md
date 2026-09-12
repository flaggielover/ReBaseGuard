# PS1 full-campaign cost requalification and pre-result production authorization

**Classification: `PS1_PRODUCTION_AUTHORIZATION_CLOSED`.** `AWS_GENUINE_PS1_SR_PRODUCTION_AUTHORIZED_TO_START = YES` - NOT started. Genuine PS1 production cells: 0.

## A. Current cost decomposition (frozen certifier, idle core, full-cell model)

| cell | CPU-h | basis | strips F | O9 core D | shared tensors B | drift tensors C | residual E | other |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| 10 | 11.94 | 13-cell mean (cell NOT in the qualification set; only its stage SHARES are its own) | 40% | 30% | 28% | 1% | 1% | 1% |
| 150 | 11.78 | Phase-4 measured | 40% | 30% | 28% | 1% | 1% | 1% |
| 360 | 13.41 | Phase-4 measured | 40% | 30% | 27% | 1% | 1% | 2% |
| 368 | 11.68 | Phase-4 measured | 35% | 29% | 34% | 1% | 1% | 2% |

Topology duplication (L): 32-way SMT costs 1.86x the CPU of 16 physical-core workers for the same work; the committed runs used 30 workers.

## B/C. Optimizations and measured speedups (all bit-identical)

- OPT-S/OPT-C shift-independent memoisation: frozen 48.3 s -> 36.5 s on the identity set; 343/343 cell-patch records bit-identical to committed certified records; full-cell identity of 6 certified cells.
- One worker per physical core (16, pinned 0-15) instead of 30 on 16 cores.
- Deterministic groups of 4 cells per worker (patch-outer, shared drift-independent panel cache).

| cells per patch | frozen CPU-s/cell | optimised CPU-s/cell |
|---:|---:|---:|
| 1 | 88.7 | 75.7 |
| 2 | 85.6 | 69.9 |
| 4 | 79.7 | 63.0 |
| 8 | - | 61.8 |
| 16 | - | 61.4 |

## D. Requalified projection (measured, 13 real cells, production unit, 16 physical-core workers)

Per-cell CPU-h: mean 11.94, p50 11.78, p90 14.97, max 14.98 (n=13).
369-cell projection: 4413 CPU-h (mean groups), 4642 (worst group); +10% 4855, +15% 5075.

## E. Recommended global cap: 6600 CPU-h (PS1 only; derivation in config/PS1_CONSTANTS.json)

## F/G. Throughput

AWS: Xeon 8488C, 16 physical cores, 123 GiB, runtime fb0dbe330667612e; 16 workers -> about 32 cells/day.
Vultr: EPYC-Milan 8 vCPU (8 independent in the prior benchmark), 15 GiB; NOT qualified for PS1 (no PS1 code deployed).

## H/I. Shard plan and wall time

Production dispatches a WHOLE cell group to an idle worker slot and runs all 3,994 live patches for that group's cells inside the one worker; a group is never split across workers. Wall time is therefore the makespan of 93 tasks (92 groups of 4 cells + the terminal [368]) greedily dispatched to 16 slots.

| basis | total CPU-h | ideal wall (perfectly divisible) | makespan | utilisation |
|---|---:|---:|---:|---:|
| mean based | 4405 | 11.47 d | 11.94 d | 0.961 |
| worst group based | 4642 | 12.09 d | 12.58 d | 0.961 |

Slot occupancy: {'5': 3, '6': 13} (groups per slot). The only imbalance is quantisation - 93 does not divide by 16 - costing 1.041x over the perfectly divisible ideal.

The Phase-4 qualification harness had a DIFFERENT shape: all 16 workers split ONE group's patch range, and the low patch indices carried 290/291 patches against ~244 and were the expensive ones, giving 1.35x within-group worker imbalance (measured 1.37/1.37/1.30 across the three 4-cell groups) and a long single-worker tail. That shape does NOT occur in production and is recorded in evidence/qual/makespan_model.json for contrast only.

## J-M. Lifecycle, adapter, precision/transport, clean checkout

Lifecycle: REUSE_WITH_ADDITIVE_PS1_ADAPTER. Suite exit codes: {'deterministic_replay': 0, 'install_runtime_policy': 0, 'original_lifecycle_suite': 1, 'partition_and_historical_regression': 0, 'prodctl_render': 0, 'prodctl_status': 0, 'prodctl_verify': 0, 'ps1_lifecycle_adapter': 0, 'ps1_production': 0}.

Deterministic fresh-process replay of Phase-4 production-path records: {'1:0,0': True, '1:24,20': True, '150:38,26': True, '150:8,36': True, '368:51,63': True, '368:63,54': True}, all_identical=True.

Executor identity: 343/343 cell-patch records bit-identical to committed certified records; full-cell identity (t3 delta and x0, consumed records, t4 ledgers, t5 statuses) for the 6 certified cells 150, 360-363, 368, each 28/28.

### Known pre-existing failure in the original audited lifecycle suite

`original_lifecycle_suite` exits 1 on exactly one assertion, `test_lifecycle_integrated.py::test_real_production_namespaces_untouched`, which requires the real production namespace to contain only README.md. It also contains PRODUCTION_LEDGER.json, written by the historical torn attempt of 2026-09-10 (sha256 d338679045d839ac..., 0 genuine cells completed, 0.000591 CPU-h committed, 16 cells torn). That file predates this round's parent commit by two days and is byte-unchanged; the suite is preserved unchanged and the assertion is a correct report, not a regression. adjudicate.py accepts the non-zero exit ONLY while the ledger hashes to the recorded historical value, still records no genuine cell, and that test is the sole failure with no errors; disposition recorded as `known_pre_existing_only`. Any mutation, any genuine cell, or any second failure fails the check closed.

### Historical production ledger: superseded, not inherited

The frozen authorization records the historical ledger as `IMMUTABLE HISTORY; SUPERSEDED FOR PS1 ONLY (not inherited)`. PS1 opens a fresh ledger under p5y_k1_ps1_production/production/, which is empty at freeze (README.md only). The historical ledger was read for verification and never written. Evidence: evidence/historical_ledger_provenance.json.

## N. Commits

producer c9b12670d4da677d384747aa703c725c58bac65a, authorization 29b3bffb6a739121b66bdfcb23cb6b6544b39baf, adapter b45fb15285f9995271e14124e62b07930e5b904a.

## O. Genuine production cells: 0

## P. Start command (NOT RUN)

    /home/ubuntu/work/ReBaseGuard/level4/.venv/bin/python \
      /home/ubuntu/work/ReBaseGuard-ps1-ops/level4/closure_proofs/p5y_k1_ps1_lifecycle_adapter/ops/prodctl.py start --role AWS

Operator preconditions: operator runs tests/ps1_systemd_live_acceptance.py (prepare, start, stop, report) with the contract's privilege prefix on AWS and confirms: completion, cgroup settlement, stop settlement, restart completion; prodctl.py install-runtime-policy --role AWS in the PS1 production clone; prodctl.py verify --role AWS and status --role AWS show NOT_STARTED/READY with 0 genuine cells
