# P5Y K1 SR — production-lifecycle successor (PRE-RESULT, OPERATIONAL ONLY)

Parent (frozen, untouched): tag `p5y-k1-sr-production-authorized-preresult`
@ `bd7cf269792bc146e911ee57a85533b7b7b1aa9d`
(namespace `level4/closure_proofs/p5y_k1_sr_production_authorized_successor`).

This successor is ADDITIVE and result-free. It binds the parent production
authorization unchanged and adds only the execution, recovery and CPU-settlement
contract of the production lifecycle. No science, threshold, scope, shard,
topology, execution order, provenance or handoff semantics is changed.

* Scientific identity changed: **NO** (`scientific_identity_changed: false`)
* Campaign: 316 cells (247 AWS, 69 Vultr), 8849 obligations
* ONE global cap: exactly **4500 CPU-h**; no per-host caps; overhead factor 1.15
* Genuine SR production cells at freeze: **0**
* Failure-mode inventory written before implementation: `LIFECYCLE_INVENTORY.md`

## Layout

| path | role |
|---|---|
| `config/OPERATIONAL_CONTRACT.json` | the hash-bound operational contract (mode `PRODUCTION`) |
| `config/OPERATIONAL_CONTRACT_HASH` | sha256 of the contract bytes |
| `config/RUNTIME_STATE_EXCLUDE` | governed git exclude block for production runtime state |
| `config/OPS_SOURCE_MANIFEST.json` | sha256 of every file of this successor (except itself and its hash) |
| `config/OPS_SOURCE_MANIFEST_HASH` | sha256 of the manifest bytes; verified by `supervisor.verify_ops_source` |
| `ops/prodctl.py` | operator CLI (render/start/stop/status/recover/verify/settle-fallback/handoff/assemble) |
| `ops/supervisor.py` | main process of the ONE sanctioned transient systemd service per run |
| `ops/produce_entry.py` | bound child: frozen `production_preflight` + `run_production_cells(poll_timeout=None)` |
| `ops/ledger_ops.py`, `ops/locks.py`, `ops/runtime_state.py`, `ops/opscommon.py` | settlement, locks, runtime-state policy, primitives |
| `tests/` | result-free synthetic suite + `systemd_live_acceptance.py` (live systemd, SYNTHETIC_CONTROL) |

## Service (per run)

`systemd-run` transient SYSTEM service, `Type=exec`, `Restart=no`,
`KillMode=control-group`, `CPUAccounting=yes`, `TimeoutStopSec=180`,
`RuntimeMaxSec=infinity`, `ExecStopPost=prodctl.py settle-fallback`, six numerical
thread variables fixed to `1`. CPU evidence hierarchy: supervisor final cgroup →
ExecStopPost cgroup → journal `CPU_USAGE_NSEC` → tail bound.

## No-science readiness (does not start anything)

AWS (as `ubuntu`):

    /home/ubuntu/work/ReBaseGuard/level4/.venv/bin/python \
      /home/ubuntu/work/ReBaseGuard-sr-lifecycle/level4/closure_proofs/p5y_k1_sr_production_lifecycle_successor/ops/prodctl.py verify --role AWS
    ... prodctl.py status --role AWS

Vultr (as `root`):

    /root/prov/tree/level4/.venv/bin/python \
      /root/prov/tree/level4/closure_proofs/p5y_k1_sr_production_lifecycle_successor/ops/prodctl.py verify --role VULTR

Execution order is frozen: AWS → authenticated handoff → Vultr. Production is
started ONLY by `prodctl.py start --role AWS` after independent adjudication.
