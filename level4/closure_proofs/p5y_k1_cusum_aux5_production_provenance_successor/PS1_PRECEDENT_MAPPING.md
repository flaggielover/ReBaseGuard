# PS1 production-provenance precedent: field-by-field mapping

**Sources:**
- `p5y_k1_ps1_production/driver/production_provenance.py` (byte-identical to the SR-authorized successor's copy)
- `driver/multihost.py` `CELL_RECORD_REQUIRED_FIELDS` and `validate_record`
- `driver/ps1_cellseq_launcher.py` (`_seal_one`, `production_preflight`)
- `config/LAUNCH_AUTHORIZATION.json` and `code/make_authorization.py`
- `driver/global_budget.py` `commit`
- the Lane C audit, `p5y_k1_ps1_postk1_adjudication_tooling/code/ps1_adjudication_audit.py`

**CUSUM counterparts:**
- the envelope (`code/prov_envelope.py`);
- the run authorization (`code/prov_authorization.py`);
- the authorized ledger (`code/prov_ledger.py`);
- the integrity audit (`code/prov_integrity.py`).

**Classes:**
- **EXACT:** the same property, bound the same way.
- **STRONGER:** the same property plus more binding.
- **INAPPLICABLE:** intentionally so, with the reason given.
- **MISSING:** absent. No row is MISSING.

## A. Sealed production cell record (`multihost.CELL_RECORD_REQUIRED_FIELDS` + `_seal_one`)

| PS1 field | CUSUM equivalent | Class |
|---|---|---|
| `cell_id` | `cell.cell_index`, plus `cell.geometry` (e0, rho, left, right, C_upper), `geometry_row_sha256` and `cells_table_sha256` | STRONGER |
| `role` (AWS/VULTR ownership) | Single bound host: `host_runtime.host_name` and `machine_id_sha256` equal the authorization's bound host. There is no multi-host role or ownership split. | INAPPLICABLE (replaced by host identity) |
| `producer_commit` | `producer.{producer_manifest_hash, runtime_contract_hash, producer_identity_hash, implementation_hash_kind, producer_manifest_*}` (content-addressed), plus `authorization.executor_hash` | STRONGER |
| `checkpoint_sha256` | `checkpoint.production_checkpoint_sha256`, plus `predecessor_checkpoint_sha256` and `predecessor_status` | STRONGER |
| `runtime_contract_hash` | `producer.runtime_contract_hash` and `host_runtime.runtime_contract_hash` | EXACT |
| `scientific_content_hash` | `scientific_record.scientific_content_hash`, plus `scientific_record.sha256` (bytes) and `auxiliary_evidence_hash` | STRONGER |
| `cpu_seconds` | `cpu_accounting.charge_usec` (integer µs), plus `charge_evidence` and a ledger reference | STRONGER |
| `obligations_completed = 28`, `complete = True` | `scientific_record.certificate_count = 28`; the seal also requires `provenance_chain` 28/28 all verified (PROVENANCE_CHAIN) | EXACT |
| `successor_id` | SR partition-successor identity. CUSUM has no partition successor; `geometry_row_sha256` identifies the frozen cell. | INAPPLICABLE |
| `B_cover_ratio` | A scientific status value. It stays inside the bound scientific record (`m.*.cover`) and is not copied into provenance, so the envelope remains result-agnostic. | INAPPLICABLE (bound via record sha) |
| `evidence.{t3,t4,t5,patches_gz}.{path,sha256}` | `scientific_record.{path, sha256}`: one Aux5 record per cell | EXACT |
| `task_id` | `ledger.attempt_id` and `ledger.supervisor_run_id`, plus `ledger.{reservation, running, seal}.{seq, entry_sha256, t_wall}` | STRONGER |
| `precision_bits = 256` | `scientific_record.precision_bits` and `authorization.universe.precision_bits`; the seal also enforces PRECISION | EXACT |
| sealed in `production/cells/NNNN.json` only (`gate_production_result_path`) | The envelope lives only at `provenance/<attempt>/CUSUM_<cell>.envelope.json` under the authorized runtime root, bound by path in the ledger. The audit refuses stray files (`C_unbound_envelope_files`). | EXACT |
| `gate_no_evidence_collision` | Records and envelopes are read-only once sealed or bound; `op_bind_provenance` refuses any rebinding (DUPLICATE_ENVELOPE) | STRONGER |

## B. `production_provenance` block (`production_provenance.seal` / `verify`)

| PS1 field or layer | CUSUM equivalent | Class |
|---|---|---|
| `schema` | `schema` (`…production-provenance-envelope.v1`) and `kind` | EXACT |
| `task_kind == "SCIENCE"` (KIND) | `task_kind == "SCIENCE"` | EXACT |
| `synthetic is False` (KIND) | `synthetic` must equal the campaign mode (False in production); synthetic records carry `SYNTHETIC_FIXTURE_NOT_SCIENCE` and are refused by the production seal | EXACT |
| `production_authorization_hash` (TEMPORAL) | `authorization.authorization_sha256`, plus `countersignature_sha256`, `authorization_id`, `production_run_id` and `ledger_id`. The ledger GENESIS state and journal entry 0 must name the same block (NO_PRE_RESULT_AUTHORIZATION). | STRONGER |
| `scientific_adapter_hash` | `authorization.executor_hash` (the EXECUTOR_HASH over the successor and predecessor execution code, `qualify5.py` and manifest v3), recomputed live by `verify_authorization` | EXACT |
| `certificate_digest` | `scientific_record.certificate_digest` (digest of all 28 certificate hashes) | EXACT |
| the synthetic stand-in `'%064x' % cell_id` refused | The qualification record bytes are refused (QUALIFICATION_RECORD_REUSE), and so is any record claiming more CPU than its attempt used (CPU_EVIDENCE_INCONSISTENT) | STRONGER |
| `binding` (BINDING layer; honest limit: digest, not signature) | `binding_sha256` over the whole envelope. In addition, `verify_pair` **recomputes the whole envelope** from the record, ledger, journal and authorization, and the ledger binds the envelope file sha256 (PROVENANCE_BOUND). The same honest limit applies: an adversary with write access to the whole ledger and journal is out of scope, as in PS1. | STRONGER |
| `verify` immediately after `seal` | `bind_envelope` runs `verify_pair(require_bound=False)` before the PROVENANCE_BOUND transition | EXACT |

## C. Launch authorization (`LAUNCH_AUTHORIZATION.json` and the preflight gates)

| PS1 field or gate | CUSUM equivalent (`RUN_AUTHORIZATION.json`, `prov_entry.py`) | Class |
|---|---|---|
| `schema`; `result_bearing: false` (a property of the object); `mode: PRODUCTION` | `schema`, `result_bearing: false` with `result_bearing_semantics`, `mode`, `status` | EXACT |
| `_HASH` file; `load_production_authorization` refuses on mismatch | `RUN_AUTHORIZATION_HASH`; `load_authorization` refuses (AUTHORIZATION_INVALID) | EXACT |
| committed before results; pre-result tag | P06: the authorization commit is recorded in the freeze record, is an ancestor of HEAD, and the file is byte-equal to that commit's copy. Genesis also refuses without authorization and countersignature. | EXACT |
| (not in PS1) | **Independent countersignature**: without it no ledger genesis is possible; the tooling cannot create one (SELF_AUTHORIZATION_REFUSED) | STRONGER |
| `campaign` | `campaign_id` | EXACT |
| `producer_commit`; ancestor of HEAD and executor unchanged since | `producer` identity; `executor_sources.files` and `EXECUTOR_HASH` recomputed live; checkpoint bound sources (P02) | STRONGER |
| `checkpoint_sha256` | `production_checkpoint_sha256`, plus `predecessor_checkpoint` | STRONGER |
| `successor_cells_path` / `_sha256` | `universe.{cells_table_sha256, geometry_digest, cell_indices_sha256, cells = 326, m_values}` | STRONGER |
| `live_patches_*` | The SR patch universe. The CUSUM certificate has no patch/panel decomposition (the record's `channel_provenance.end`). | INAPPLICABLE |
| `ps1_protocol_sha256` | The lifecycle protocol is inside the hash-bound checkpoint (`lifecycle`, `ledger`) | EXACT |
| `shard_manifest_sha256`; partition exactly once | Single host with per-cell admission in ascending index; `validate_state` requires the ledger cell set to equal the frozen universe exactly | INAPPLICABLE (partition exactness kept by universe equality) |
| `executor_source_manifest`, `executor_source_sha256`, `scientific_adapter_hash` | `executor_sources.files` and `EXECUTOR_HASH` | EXACT |
| `pythonpath_rel`; `hosts.*.python` and `environment` | `runtime.worker_argv_template` (`env -i`, pinned thread environment, venv python, certifier path) | EXACT |
| `hosts.*.workers`, `core_assignment`, `per_cell_reservation_cpu_h`, `work_dir` | `runtime.workers`, `runtime.cores`, `cap.reservation_usec`, `ledger.runtime_root` | EXACT |
| `runtime_contract_hashes` | `producer.runtime_contract_hash` | EXACT |
| `active_host`, `topology` | `host` (all bound host facts: name, machine-id sha, CPU, topology, kernel, glibc, libc sha) | STRONGER |
| `global_cpu_cap`, `governed_overhead_cpu_h`, `overhead_factor` | `cap.{cap_usec, reservation_usec, invariant [115, 100]}`; overhead is measured and charged rather than a fixed allowance | STRONGER |
| `far_field_obligation` | `universe.far_field_obligation` (`CUSUM:-1:far_field:all_m`, INHERITED) | EXACT |
| `handoff` | Single host, no handoff | INAPPLICABLE |
| `historical_production` (immutable, not inherited) | `predecessor_checkpoint` (BLOCKED, preserved, fenced, not inherited) | EXACT |
| preflight: role, thread contract, identities, precision/runtime probe, cap | P03 runs the predecessor preflight, whose C03–C11 cover identity, host, checkout, runtime probe, universe, qualification, cap and schemas | EXACT |
| `budget.commit(key, actual, sealed)` (ledger `completed_cells`) | SEALED transition (`attempts[aid].seal`), then the PROVENANCE_BOUND transition (`attempts[aid].provenance`), both in the hash-chained journal | STRONGER |

## D. Lane C integrity audit

| PS1 audit | CUSUM (`prov_integrity.audit`) | Class |
|---|---|---|
| A: sealed-cell completeness over the domain | `A_completeness`: verified pairs == frozen domain | STRONGER (pairs, not files) |
| B: sealed file == ledger entry (canonical) | Record sha == seal sha; envelope sha == ledger provenance sha; the envelope recomputes | STRONGER |
| C: evidence sha256 plus recomputed scientific hash | `verify_pair` → `verify_record` (hash_v2 recomputation, K4 structure, identity) | STRONGER |
| D: torn / duplicate / open reservations / runs / halt | `D_open_attempts`, `D_unsettled_supervisor_runs`, `D_halt`, `C_unbound_envelope_files`, DUPLICATE_ENVELOPE | EXACT |
| E: CPU accounting reconciles | Predecessor `validate_state` (every bucket equals its recorded charges, exact integers) | EXACT |
| F: continuity hash chain | `read_and_relate` must be CONTINUOUS (journal chain) | EXACT |
| G: per-cell coverage matrix | `pairs` map per cell (JSON) | EXACT |
| `INTEGRITY_READY_FOR_ADJUDICATION` | Same key and meaning, requiring a COMPLETE, settled ledger | EXACT |

## Verdict

- **Mandatory PS1 fields:** every one is EXACT or STRONGER, or INAPPLICABLE with a stated reason (multi-host role/shard/handoff, the SR patch universe, the SR partition successor id, and a status value kept inside the bound record).
- **MISSING:** none. Three fields were added during this mapping to avoid a MISSING row: envelope `precision_bits`, envelope `authorization.executor_hash`, and authorization `universe.far_field_obligation`.

```text
PS1_PROVENANCE_EQUIVALENCE = PASS
```
