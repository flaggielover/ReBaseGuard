# P5Y K1 SR — additive production authorization successor (PRE-RESULT)

`RESULT_BEARING = false`. `GENUINE_SR_PRODUCTION_CELLS = 0`.
`production_enabled = true` — production is *authorised*, not *started*.

## What this successor is

The frozen `p5y_k1_sr_multihost_handoff_successor` closed the AWS → VULTR role
transition (`ROLE_TRANSITION_CLOSED`) and left exactly one thing shut:

> `gate_production_enabled`: *"production_enabled is false in the frozen launch
> authorization; result-bearing execution refused. A future additive
> authorization changing ONLY this field makes the path below reachable."*

This namespace **is** that pre-declared additive authorization. It invents no
parallel mechanism.

## What is carried forward byte-for-byte

`driver/{executor_adapter,global_budget,handoff,integrated_sr_launcher,multihost,
worker_pool}.py`, `config/{SHARD_MANIFEST.json,SHARD_MANIFEST_SHA256.json,
handoff_pubkey.pem,HANDOFF_PUBKEY_FINGERPRINT}` and
`evidence/scientific_adapter_identity.json` are **bit-identical** copies of the
predecessor. No frozen line is modified, weakened or removed. Scope, thresholds,
cap, shard split, handoff and executor are unchanged.

## What is genuinely new

| addition | why |
|---|---|
| `config/LAUNCH_AUTHORIZATION.json` | `production_enabled=true`, binding the full campaign identity |
| `driver/production_provenance.py` | the genuine-vs-synthetic firewall |
| `driver/production_launcher.py` | the operative SCIENCE entry point; composes frozen primitives |
| `production/` | the dedicated immutable production result namespace |

### The gap this closes

The frozen record schema makes a genuine science record and a Phase-8 synthetic
stand-in **structurally identical** — both carry a well-formed 64-hex
`scientific_content_hash`. `assemble_global_ledger` therefore accepted a *wholly
synthetic* 316-cell / 8849-obligation campaign. That was harmless while
`production_enabled=false`; it is not harmless once production is authorised.

`production_provenance` closes it with four independent layers — temporal
(authorization hash), checkpoint (a new checkpoint identity the frozen
`validate_record` already enforces), kind (`task_kind`/`synthetic`/stand-in
rejection) and binding (canonical digest). See the module docstring, including
its stated limit.

## Invariants (re-verified, not asserted)

316 cells · 247 AWS / 69 VULTR · 8849 obligations · ONE global 4500 CPU-h cap ·
no per-host cap · AWS → authenticated handoff → VULTR.

## Running

```
python driver/production_launcher.py --ready-check    # every gate, no science
python driver/production_launcher.py --produce        # RESULT-BEARING; needs approval
```
