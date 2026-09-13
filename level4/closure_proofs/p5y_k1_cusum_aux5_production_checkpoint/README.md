# P5Y K1 CUSUM Aux5 production checkpoint (rebaseguard-vultr-02)

This namespace moves the qualified CUSUM Aux5 successor from **QUALIFIED** to **READY_TO_LAUNCH_PRODUCTION**. It freezes the production checkpoint, the ledger and lifecycle, the cost-cap invariant, the K4 structural attestation and the production entrypoint.

**It launches nothing.** No production cell has been started. The frozen certifier is not run by anything in this namespace except a launch, and a launch is an explicit operator action.

## What is reused unchanged

| Object | Source | Bound by |
|---|---|---|
| Certifier | Aux5 `code/qualify5.py`, run as its own `env -i` interpreter pinned to one core | manifest v3, checkpoint `producer` |
| Producer identity and runtime contract | `manifests/producer_manifest_v3.json` (`3692d0fe…`, `bc75c9ea…`) | checkpoint `producer`, `runtime_contract` |
| Scientific universe, geometry, precision | K1 spec `cells.json` (326 CUSUM cells, m ∈ {1,2,3,5}, 256 bits) | checkpoint `scientific_universe`, `geometry`, `precision` |
| Scientific-hash semantics | Aux4 `schema.py` and `hash_v2.py` | checkpoint `scientific_hash` |
| Cost-cap formula | Aux5 `config/COST_CAP_FORMULA.json` and `code/cap_formula.py` | checkpoint `cost_cap` |
| Qualification evidence | Aux5 `evidence/qualification_r1/` | checkpoint `qualification` |
| K4 assembly checkpoint | `p5y_k2k5_postk1_audit` (frozen, not edited) | checkpoint `k4` |

No scientific definition is changed.

## What this namespace adds

All of it is **non-certifying**.

| Module | Role |
|---|---|
| `code/prod_ledger.py` | Ledger states and invariants, the hash-chained journal, accounting, keeper evidence, crash reconciliation, export and restore |
| `code/prod_supervisor.py` | Admission loop, drain, heartbeat, keeper (`PR_SET_CHILD_SUBREAPER`), exit codes |
| `code/prod_sealer.py` | Seal-time record verification: identity, runtime, schema, hash recomputation, K4 structure, CPU evidence, qualification reuse |
| `code/prod_spec.py` | Campaign specifications. The production spec is built only from the frozen checkpoint; the synthetic spec can never reach the production root. |
| `code/prod_cells.py`, `code/prod_common.py` | Frozen geometry, durable writes, process and host facts |
| `code/k4_input_attestation.py` | Structural K4 input attestation, and the post-production integrity attestation (not run) |
| `code/make_production_checkpoint.py` | Builds `config/PRODUCTION_CHECKPOINT.json` and refuses on any disagreement |
| `code/prod_entry.py` | The only production entrypoint: `preflight` (C01–C14), `launch`, `status`, `drain`, `undrain`, `settle`, `export`, `attest` |
| `tests/acceptance.py`, `tests/synthetic_worker.py` | Synthetic, non-result-bearing acceptance |

## Lifecycle in one paragraph

A PENDING cell is RESERVED durably before its worker starts. It becomes RUNNING (pid and start ticks) immediately after. It is SEALED only after the record verifies and is made read-only.

- A worker lost to a signal leaves a **TORN** attempt. It is charged, and the cell is retried; the third infrastructure tear of one cell halts the campaign.
- A nonzero exit, or a record that fails the seal, is **FAILED**. It is charged, never retried, and the campaign halts.
- A supervisor that dies takes its workers with it (`PR_SET_PDEATHSIG`). The keeper reaps them with exact rusage.
- The next supervisor reconciles every open attempt before it admits anything. A still-live orphan is refused, never adopted.
- A drain (SIGTERM, SIGINT or the `DRAIN` marker) stops admissions and lets admitted work finish.
- Admission requires `115·(committed + in-flight + R) ≤ 100·CAP`, with CAP = 300 CPU-h and R = 1 CPU-h. The cap is bound at genesis and can never change.
- An admission denied with nothing in flight records `INCOMPLETE_BUDGET_EXHAUSTED`.

## Launch (operator only; not performed here)

```text
cd /root/work/postk1-aux5/level4/closure_proofs/p5y_k1_cusum_aux5_production_checkpoint/code
/root/work/rbg-cusum-aux5-venv/bin/python -B prod_entry.py preflight        # must print READY
setsid nohup /root/work/rbg-cusum-aux5-venv/bin/python -B prod_entry.py launch \
    --confirm-checkpoint-sha256 "$(cat ../config/PRODUCTION_CHECKPOINT_HASH)" > /root/work/postk1-runs/cusum-aux5-production.log 2>&1 &
```

The supervisor re-runs the whole preflight under the campaign lock before its first admission.
