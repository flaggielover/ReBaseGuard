# Carry-over protocol: CUSUM Aux5 new-glibc successor

**Status: FROZEN PROPOSAL. Carry-over is NOT authorized merely by creating this file.**

It becomes active only after all four of the following hold:
- **(a)** Q6 PASS (`config/REQUALIFICATION_PROTOCOL.json`);
- **(b)** an independent governance review PASS;
- **(c)** an active independent countersignature exists that binds the sha256 of `config/GLIBC_SUCCESSOR_PROPOSAL.json` and the sha256 of the Q6 result;
- **(d)** a successor checkpoint binds this approved rule (`SUCCESSOR_CHECKPOINT_SPEC.md`).

Until then, `glibc_successor.py launch-readiness` returns `NOT_READY` and no successor production may launch.

## 1. Why an explicit rule is needed

- **No frozen rule decides this.** No frozen rule authorizes or forbids consuming sealed cells across a checkpoint boundary.
- **The K1 cover-ledger precedent forbids silent carry-over.** Its successor says: "No resume record or prior PASS is silently carried across the checkpoint boundary … Old records are evidence only; they cannot satisfy new coverage".
- **The frozen drift rule requires a new checkpoint.** The predecessor checkpoint states that "a change of host, kernel, glibc bytes or runtime contract requires requalification and a new checkpoint".
- **The frozen attestation builder cannot express a union.** `prov_integrity.build_k4_attestation` accepts only one COMPLETE ledger.

This protocol therefore defines an explicit, hash-linked rule. It never rewrites predecessor history.

## 2. Result set

```text
SUCCESSOR_PRODUCTION_RESULT = OLD_CARRYOVER ⊎ NEW_SUCCESSOR
OLD_CARRYOVER = cells 0-127    the verified (record, envelope) pairs of the terminal predecessor ledger, unchanged
NEW_SUCCESSOR = cells 128-325  pairs produced by the successor ledger under the new glibc
OLD_CARRYOVER ∩ NEW_SUCCESSOR = ∅;  OLD_CARRYOVER ∪ NEW_SUCCESSOR = {0, …, 325}
```

## 3. Required conditions

Each condition is machine-checked by `code/glibc_successor.py`. Unless marked otherwise, the check runs when the proposal is verified.

| # | Condition | Enforcement |
|---|---|---|
| R1 | **Predecessor immutable.** The predecessor runtime root, ledger, journal, reaper, records and envelopes are never written, settled, repaired, moved or deleted | Live binding re-collection must equal the committed binding (`compare_live`: `PREDECESSOR_CHANGED_SINCE_BINDING`) |
| R2 | **Exact predecessor hashes bound.** This covers `ledger.json`, `journal.jsonl`, `reaper.jsonl`, the ledger state, the genesis and last journal entries, and the cells digest | `config/PREDECESSOR_BINDING.json`, bound by sha256 in the proposal manifest |
| R3 | **All 128 record and envelope hashes bound**, each equal to its seal and bound envelope hash, the envelope naming its record and cell | `verify_binding`: `RECORD_HASH`, `ENVELOPE_MISSING_OR_CHANGED`, `ENVELOPE_NOT_BOUND_TO_RECORD` |
| R4 | **Terminal predecessor.** The disposition is terminal on the bound libc drift (`fa430b8f…` → `9792e3cb…`), with exactly 128 SEALED and 198 PENDING | `PREDECESSOR_NOT_TERMINAL`, `PREDECESSOR_STOP_IS_NOT_THE_BOUND_LIBC_DRIFT`, `PREDECESSOR_CELL_STATES` |
| R5 | **No post-drift admission.** No `RESERVED` at or after the libc ctime | `POST_DRIFT_ADMISSION` |
| R6 | **No post-drift worker start.** No `RUNNING` or process start at or after the libc ctime, each start lying between its reservation and its `RUNNING` entry | `POST_DRIFT_WORKER_START`, `WORKER_START_INCONSISTENT` |
| R7 | **Fail-closed stop.** Exactly one host-drift stop, after the drift, with no admission after it, and the terminal disposition as the last journal entry | `DRIFT_DETECTION_NOT_FAIL_CLOSED`, `DISPOSITION_NOT_FINAL_TERMINAL_ENTRY` |
| R8 | **Old pairs verify.** The frozen integrity audit reports 128 verified pairs, and full seal re-verification passes for all 128 cells | `OLD_PAIR_VERIFICATION_FAILED` |
| R9 | **Q6.** Under the new glibc, cells 318 and 323 (2 repeats each) reproduce the predecessor qualification scientific hashes and every certificate hash exactly | `evaluate_q6` against `config/Q6_REFERENCE.json`, checked at launch readiness. Failure sets `CARRYOVER_ROUTE = REJECTED` |
| R10 | **Same frozen producer.** Producer identity `3692d0fe…`, runtime contract `bc75c9ea…`, manifest file `611bd0a9…`, in every old and new record | `REQUALIFICATION_PROTOCOL.json` (P4); successor seal check; composite audit |
| R11 | **No qualification-record reuse.** No old or new record is byte-identical to a qualification record, and no Q6 record is copied from the predecessor qualification | `QUALIFICATION_RECORD_REUSE` (binding and Q6) |
| R12 | **No recomputation of cells 0–127.** The successor ledger universe is exactly 128–325, and any successor attempt on an old cell is refused | `check_no_recomputation`; successor spec `cell_indices`; checkpoint `production_universe` |
| R13 | **Strict disjointness** of the old and new cell sets | `check_partition`: `PARTITION_OVERLAP` |
| R14 | **Complete union coverage** of 0–325 | `check_partition`: `PARTITION_UNION` |
| R15 | **CPU continuity.** The absolute cap is 300 CPU-h, predecessor settled CPU is charged once, and the successor genesis cap is 817,313,389,420 µs | `check_cap`: `CAP_RESET_FORBIDDEN` and the other cap refusals; `config/CPU_CAP_CONTINUITY.json` |
| R16 | **Composite integrity audit before any K4 attestation.** It verifies old pairs against the predecessor checkpoint and authorization, and new pairs against the successor checkpoint and authorization, then disjointness, union and a single producer identity. K4 inputs are exported only from verified pairs of both halves | Successor checkpoint requirement (`SUCCESSOR_CHECKPOINT_SPEC.md` §6) |
| R17 | **Independent countersignature before successor launch.** It binds the proposal manifest sha256 and the Q6 result sha256 | `launch_readiness`: `COUNTERSIGNATURE_ABSENT` / `COUNTERSIGNATURE_INVALID` |
| R18 | **Host bound and contained.** The successor binds the new host facts, glibc-family and runtime-adjacent library hashes, and the containment post-state | `REQUALIFICATION_PROTOCOL.json` host section; `HOST_CONTAINMENT_PLAN.md` |

## 4. What this rule never does

- **Predecessor history stays as it is.** The predecessor terminal disposition is not cleared, reclassified or superseded for the predecessor ledger. As in the PS1 generation-transition precedent, it remains authoritative for that ledger forever.
- **Old cells are never imported as attempts.** Cells 0–127 do not enter the successor ledger as rows. The successor ledger contains only 128–325, and old cells are consumed only through the composite audit.
- **No reinterpretation.** It does not reinterpret any scientific record, obligation status or envelope.
- **No authorization of Q6.** It does not authorize requalification execution, containment or production.

## 5. Failure routes

| Event | Route |
|---|---|
| Q6 FAIL (any scientific or certificate hash differs, P1–P5 not PASS, wrong host) | `CARRYOVER_ROUTE = REJECTED`; no successor production may launch under this proposal. A new governance decision is required; full recomputation is the fallback. |
| Live re-collection differs from the committed binding | Proposal invalid (`PREDECESSOR_CHANGED_SINCE_BINDING` or `HOST_CHANGED_SINCE_BINDING`); stop and investigate |
| Independent review rejects carry-over | Carry-over not authorized; this proposal stays inactive |
