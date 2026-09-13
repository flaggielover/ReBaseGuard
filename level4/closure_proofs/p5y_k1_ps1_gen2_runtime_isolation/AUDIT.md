# Generation-2 runtime isolation: defect audit (pre-repair, read-only)

This audit is based on:
- the gen2 lineage source (`082526be`, fetched read-only from the AWS ops worktree);
- a read-only observation of the live AWS host at 2026-09-13T04:26Z (`ps`, `systemctl list-units`, `ls`, `cat`), which took no lock, ran no prodctl and wrote nothing.

The live run was not touched and no evidence was moved.

| id | path | consumer and source of truth | live observation | consequence |
|---|---|---|---|---|
| M1 | work root | launcher `Pool(... host["work_dir"])` ← frozen `LAUNCH_AUTHORIZATION.hosts.AWS.work_dir` = `rbg-runtime/p5y_k1_ps1_production/work` (gen1) | live `slot_*` workdirs under the gen1 root | gen2 work state is co-mingled with gen1 run dirs |
| M2 | DRAIN marker | launcher/worker `drain_flag_path(auth)` → gen1 `work/DRAIN`; `prodctl drain` → contract `runtime_dir/work/DRAIN` = gen2 | `rbg-runtime/p5y_k1_ps1_generation2/work` does not exist; an operator had to write a compatibility DRAIN at the gen1 path (16:04:18Z) | **`prodctl drain` is a no-op for the live run** |
| M3 | evidence root | launcher task `evidence_dir` ← authorization (gen1); `ps1_reconcile._markers` ← contract `runtime_dir/evidence` (gen2) | gen2 `evidence/` absent; live evidence at gen1 `evidence/20260912T154659Z-277931` | **supervisor-owned durable-marker reconciliation is blind** for SIGTERM, SIGKILL and worker loss: durable cells would be torn and recomputed, not finalized (reproduced, see the negative control) |
| M4 | checkpoint / export | `evidence_root_at_build` and `source_evidence_root` ← authorization (gen1) | — | provenance labels name the wrong generation (the copy itself uses record paths) |
| M5 | recovery driver import | `prodctl._recovery_driver` imports `ps1_checkpoint`/`host_guard` from the **production tree** namespace `p5y_k1_ps1_portable_recovery`, not from `ops_root` | gen2 prod tree `4cd7a45` ≠ ops tree `082526b` (config-only difference today) | ops code can silently diverge from the executing tree |
| M6 | crash recovery | pre-start recovery and ExecStopPost settle-fallback settle an unsettled run **without** marker reconciliation | — | a supervisor SIGKILL or host loss tears cells that were already durable |
| M7 | stale DRAIN | no start gate for an existing DRAIN | gen1 compat flag persists after the drain | the next start (unrepaired) drains immediately with 0 admissions |
| M8 | orphan detection | `live_run_processes` does not match `ps1_cellseq_worker.py` | — | orphaned workers are invisible to pre-start |
| M9 | stale lock state | gen1 `campaign.owner.json` names pid 259346 (`prodctl:<lambda>`), flock released | — | harmless (kernel flock), reported only |
| M10 | test masking | the synthetic hook rewrote authorization `work_dir`/`evidence_dir` to the contract `runtime_dir` | — | the predecessor A/B2 acceptance passed only because the harness did the path alignment the genuine path lacks |
| M11 | portable resume | `_resume` probes with the authorization's interpreter path | — | a bundle cannot be verified on a host with a different layout (found on Vultr) |

The live run remains safe as long as it ends by the graceful drain already in force. The launcher then
reaps its own markers, and settlement follows a normal exit. **Do not use `prodctl stop` on the live run
before the drain completes (M3).**
