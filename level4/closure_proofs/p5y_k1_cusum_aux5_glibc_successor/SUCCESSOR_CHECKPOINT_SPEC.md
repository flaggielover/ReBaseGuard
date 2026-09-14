# Successor checkpoint specification: CUSUM Aux5 new-glibc successor

**Status: SPECIFICATION ONLY. No successor checkpoint, authorization, countersignature, runtime root or ledger exists.** The checkpoint may be built only after Q6 PASS and an independent review PASS. It must be countersigned before any launch.

## 1. Files

The planned files are all additive and all in this namespace:

| File | Content |
|---|---|
| `config/GLIBC_SUCCESSOR_CHECKPOINT.json` + `_HASH` | schema `rebaseguard.p5y.k1.cusum-aux5.glibc-successor.checkpoint.v1`, status `FROZEN_PRE_PRODUCTION` |
| `config/FREEZE_RECORD.json` | Binds the checkpoint sha, the run authorization commit and the synthetic acceptance result |
| `config/RUN_AUTHORIZATION.json` + `_HASH` | Pre-result, `result_bearing: false`; binds the checkpoint, universe 128–325, the residual cap, the new host and a new run id and ledger id |
| `config/COUNTERSIGNATURE.json` | Written only by the independent reviewer. Schema `…glibc-successor.countersignature.v1`, verdict `APPROVED_CARRYOVER_AND_SUCCESSOR_LAUNCH` |
| `config/CARRYOVER_MANIFEST.json` | The 128 old pairs (see §3) |
| `evidence/requalification_r1/Q6_RESULT.json` | The executed requalification result |
| `evidence/containment/{PRE_STATE,POST_STATE}.json` | Host containment evidence |

## 2. Required checkpoint bindings

| Key | Binding |
|---|---|
| `proposal_sha256` | sha256 of `config/GLIBC_SUCCESSOR_PROPOSAL.json` (this freeze) |
| `carryover_rule` | sha256 of `CARRYOVER_PROTOCOL.md` as bound in the proposal |
| `predecessor` | provenance checkpoint `dd4c89d7…`, authorization `b8f11ec0…`, countersignature `1ceb92d4…`, ledger id `61eb8565…`, runtime root, sha256 of `ledger.json`, `journal.jsonl` and `reaper.jsonl`, ledger state `b3cee6ff…`, genesis entry `eee65c7b…`, last entry `eed2a555…`, cells digest `2a93585c…`, binding sha `0676fc82…` |
| `carryover_manifest` | sha256 of `CARRYOVER_MANIFEST.json`; `carryover_cells` = `[0..127]` |
| `requalification` | sha256 of `REQUALIFICATION_PROTOCOL.json`, `Q6_REFERENCE.json` and `Q6_RESULT.json`; `q6_result_sha256`; verdict PASS; measured c_max |
| `host` | every fact in `REQUALIFICATION_PROTOCOL.json` `host`; `guard_before_every_admission` = the frozen 9 facts **plus** all 11 `system_libraries_sha256` entries; the containment POST_STATE sha |
| `producer`, `runtime_contract`, `scientific_hash`, `precision`, `result_schema`, `k4` | byte-equal to the predecessor checkpoint sections (identity `3692d0fe…`, contract `bc75c9ea…`) |
| `production_universe` | exactly `[128..325]` (198 cells); `cell_indices` of the successor spec |
| `cost_cap` | `absolute_campaign_cap_usec` 1,080,000,000,000; `predecessor_settled_usec` 262,686,610,580; `successor_residual_cap_usec` 817,313,389,420 (the successor ledger genesis cap); invariant [115, 100]; reservation 3,600,000,000 |
| `runtime_root` | a new path, e.g. `/root/work/postk1-runs/cusum-aux5-production-glibc-r1`. Both earlier CUSUM runtime roots are refused as successor roots, as synthetic roots and as output locations |
| `countersignature_sha256` | sha256 of the committed `COUNTERSIGNATURE.json`; frozen P07 semantics (post-signature gate only) |
| `entrypoint` | successor preflight (see §5) |

The successor must **not** depend on the predecessor preflight host check (C04, predecessor P03). Those are bound to the old libc and would refuse forever. The successor binds its own host facts.

## 3. Carry-over manifest (cells 0–127)

For each cell: the attempt id, record path and sha256, envelope path and sha256, scientific content hash, process start (btime + ticks), reservation, running and seal journal entry seq and sha, and charge µs. Plus the predecessor audit pairs digest `07e6adb3…`. It is derived only from `config/PREDECESSOR_BINDING.json` and must equal its `cells` section.

## 4. Successor ledger semantics

- **Universe:** cells 128–325, all PENDING at genesis. Cells 0–127 are not rows, so the frozen `op_reserve` cannot admit them and `validate_state` refuses any extra cell.
- **Genesis cap:** 817,313,389,420 µs, bound at genesis and never changed. There is no import transition and no predecessor reaper record is read.
- **Lifecycle:** the frozen lifecycle modules are reused by import and unchanged (reservation, sealing, provenance envelope, reconciliation, drain, the stop rules, `CAP_CHANGE_FORBIDDEN`). A new successor spec supplies the universe, root, cap and host facts.
- **Predecessor immutable:** the terminal predecessor ledger is never opened with a lock, settled or written. The successor preflight re-collects the predecessor binding read-only and requires equality with the committed binding.
- **Independently auditable:** the successor ledger has its own authorization-born genesis and journal. A successor-only integrity audit verifies its pairs against the successor checkpoint and authorization.

## 5. Pre-genesis state and production-start predicate

The semantics come from issuance r2, unchanged:
- **PRE_GENESIS:** the successor runtime root is absent, or holds exactly `{campaign.lock, campaign.owner.json, reaper.jsonl}` as regular files, with a free empty lock, a bound-host owner, and only frozen-verifiable keeper-exit or REFUSED(30) supervisor reaper records.
- **PRODUCTION_STARTED:** `ledger.json` or `journal.jsonl` exists in the successor root.
- **Anything else is CORRUPTED** and refused.
- **Refused launches:** refused-launch overhead in the successor reaper is charged once at genesis by the frozen `unmatched_overhead`, inside the residual cap.
- **Launching:** only through a short-lived exec-in-place launcher outside the repository, whose argv carries no frozen P10 marker. Every remote verification command must be marker-free and must avoid host-guarded words.

**Successor preflight checks (proposed):**
1. Checkpoint and freeze.
2. Bound sources.
3. Proposal verifies (`verify-proposal`).
4. Live predecessor binding equals the committed binding.
5. Q6 PASS.
6. Host facts plus the 11 library hashes, and containment POST_STATE.
7. Runtime-contract probe.
8. Run authorization.
9. Countersignature (post-signature gate).
10. Synthetic acceptance.
11. Run state (pre-genesis).
12. Host idle.

`launch-readiness` must be `READY_TO_LAUNCH_SUCCESSOR`.

## 6. Composite audit and K4 export

- **Composite audit:** runs frozen `prov_integrity.audit` on the predecessor ledger (checkpoint `dd4c89d7`, 128 verified pairs) and a successor audit on the successor ledger (198 verified pairs, COMPLETE). It requires:
  - disjoint cells;
  - union exactly 0–325;
  - every record's producer identity `3692d0fe…`;
  - no qualification-record reuse;
  - the live predecessor binding equal to the committed binding.
- **Composite K4 attestation:** schema `rebaseguard.p5y.k1.cusum-production.integrity-attestation.v1` with `cells_verified = 326` and `all_scientific_hashes_verified = true`. `producer_checkpoint_sha256` is the successor checkpoint sha, and `production_provenance` holds both halves (each ledger state sha, genesis sha, authorization block and pairs) and the composite audit sha. An adjudicator must be able to recompute it exactly.
- **K4 export:** `k4_records/` holds exactly one record per verified pair of either half. No record enters K4 unless its pair verified.

## 7. Not created by this freeze

No checkpoint, authorization, countersignature, carry-over manifest, requalification result, containment evidence, runtime root or ledger.
