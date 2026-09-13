# Generation-2 runtime isolation successor: RESULT (operational only, synthetic acceptance)

```
GEN2_RUNTIME_ISOLATION_REPAIR        = PASS_SYNTHETIC_NOT_DEPLOYED
LANE_A_DEPLOYMENT_ALLOWED_ONLY_AFTER = CURRENT_LIVE_DRAIN_SETTLED   (DEPLOYMENT_GATE.md)
LIVE_AWS_RUN_TOUCHED                 = NO
NEW_RESULT_BEARING_COMPUTE           = NONE
```

The repair is **unfrozen** and **not deployed**: production refuses until an operator commits
`config/OPERATIONAL_CONTRACT_HASH` under the deployment gate. No scientific module is read or changed.

## Adverse findings (stand regardless of the repair qualifying)

1. **Generation-2/generation-1 runtime-path mismatch in the DEPLOYED gen2 ops** (AUDIT M1–M4).
   - The live launcher takes work, DRAIN and evidence paths from the frozen authorization, which names the gen1 runtime root.
   - `prodctl drain` writes the gen2 root, so it is a no-op for the live run.
   - The separation that `GENERATION_TRANSITION.json` declares is not realised.
2. **Broken crash-recovery reconciliation in the deployed gen2 ops** (M3, M6).
   - Supervisor reconciliation scans `<gen2 runtime>/evidence`, which the live launcher never writes.
   - Pre-start recovery and ExecStopPost settle without reconciling at all.
   - Durable cells are therefore torn and recomputed after SIGTERM, SIGKILL, worker loss or supervisor loss. The negative control reproduces this.
3. **Stale DRAIN hazard** (M7): the next start after a completed drain drains immediately with 0 admissions.
4. **The old acceptance harness masked the path defect** (M10): its hook rewrote the authorization `work_dir`/`evidence_dir` to the contract `runtime_dir`, which the genuine path never does.
5. Also found: M5 (the recovery driver was imported from the production tree), M8 (orphan workers undetected), M11 (portable resume depended on the authorised host's interpreter path).

## Repair (additive, generated from hash-verified gen2 sources; `code/make_isolation_ops.py`)

| defect (AUDIT.md) | repair |
|---|---|
| M1/M2/M3 path split | `driver/generation_paths.py` is the ONE resolver (work, evidence, DRAIN, checkpoints, export, drain archive under `runtime_dir`). `produce_entry` rebinds exactly `hosts[role].work_dir/evidence_dir` of the frozen authorization **object** after the frozen preflight; the file and hash are unchanged, and a guard fails closed if any other field would differ. |
| M3 legacy markers | reconciliation scans the generation root, then the declared legacy authorization-bound roots (read-only; markers are pid-bound to the settling run) |
| M4 | checkpoint/export evidence root comes from the resolver |
| M5 | recovery driver imported from THIS ops root |
| M6 | durable-marker reconciliation from the recorded launcher pid in pre-start recovery and in the ExecStopPost settle-fallback |
| M7 | pre-start `STALE_DRAIN_FLAG` refusal; `prodctl clear-drain` archives the flag with a continuity record |
| M8 | worker/entry names added to orphan detection |
| M10 | new harness never aligns paths: the authorization names a DECOY legacy root |
| M11 | resume probes with the contract-bound interpreter |
| isolation gate | runtime root not inside a source tree, not aliasing the predecessor production root or legacy roots; every derived path inside the root |

Generated: 5 patched files (`opscommon`, `produce_entry`, `supervisor`, `prodctl`, `ps1_reconcile`) and 6 byte-identical copies. Hashes are in `config/GENERATION_REPORT.json`. The qualified source hashes are in `config/QUALIFIED_SOURCE_HASHES.json`.

## Verification (`evidence/r2_final/`: ACCEPTANCE.json, RUNLOG.txt with source sha256s, acceptance.log; host rebaseguard-vultr-02; clone `082526be`)

Unit tests: `tests/test_isolation_units.py` (10). Deployment-gate tests, added after qualification: `tests/test_deployment_gate.py`.

| scenario | result |
|---|---|
| graceful drain: foreign legacy DRAIN planted and ignored; `prodctl drain` honoured; stale-flag restart refused; `clear-drain`; resume to 24/24 | PASS |
| SIGTERM (`prodctl stop`): durable cells finalized, in-flight torn once, restart completes 8/8 | PASS |
| SIGKILL launcher after a durable marker: supervisor reconciliation finalizes it from the generation root | PASS |
| SIGKILL launcher before the marker rename: no false finalization | PASS |
| worker loss: 0,1 finalized; 2,3 torn once; not halted; restart completes 4/4 | PASS |
| supervisor SIGKILL with ExecStopPost disabled: stale reservations visible, lock not stale, restart settles with JOURNAL evidence, 8/8 | PASS |
| crash with unsealed durable markers → **pre-start** reconciliation finalizes [1,5], never torn (new in the final run) | PASS |
| crash with unsealed durable markers → **ExecStopPost** reconciliation finalizes [2,6] before restart (new in the final run) | PASS |
| checkpoint → export → clean-dir resume (VERIFIED_READY, 365 pending); corrupt checkpoint, tampered evidence and historical-CPU reset all REFUSED; evidence root = generation root | PASS |
| every scenario: decoy legacy root untouched; markers only under the generation evidence root | PASS |
| **NEGATIVE CONTROL, unrepaired gen2 ops, drain**: `prodctl drain` not honoured (>8 admissions after the flag, lock LIVE); launcher wrote markers into the authorization-bound root; generation root empty | defect reproduced |
| **NEGATIVE CONTROL, unrepaired gen2 ops, SIGKILL after marker**: durable marker for cell 1 exists in the legacy root; no reconciliation; cell 1 torn | defect reproduced |

### Initial Lane A harness failures (first run `evidence/r1_superseded/ACCEPTANCE.json`: 4 FAIL; retained, not rewritten)

| scenario | classification | disposition |
|---|---|---|
| sigterm | **harness defect**: the check required `STOP_SIGNAL_SIGTERM`, but a cgroup SIGTERM can reach the launcher first (`CHILD_EXIT_-15`); ops behaviour was correct | assertion widened to both signatures |
| worker_loss | **harness defect**: death-attempt counter keyed on the group leader, so the restarted group died again | counter keyed per declared-death cell |
| checkpoint | **genuine ops portability defect (M11)**: `prodctl resume` probed with the authorization's AWS interpreter path and refused on another host | repaired in the generated ops (qualified sources include it) |
| neg_drain | **harness defect** in the negative control: the workload completed inside the drain wait, so the defect was not observable | workload lengthened; the explicit admission-count criterion is now reproduced |

The final run used one source version (sha256 list in `evidence/r2_final/RUNLOG.txt`), and that version is the qualified one.

## Deployment

Not performed. Follow `DEPLOYMENT_GATE.md`.
