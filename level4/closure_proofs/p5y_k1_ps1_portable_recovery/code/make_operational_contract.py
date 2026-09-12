"""Emit the recovery successor's OPERATIONAL_CONTRACT.json (additive over the frozen adapter).

Only lifecycle/execution fields change. parent.commit becomes the recovery code commit; the
predecessor authorization commit is recorded, never overwritten.
"""
import hashlib, json, subprocess, sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
FROZEN = Path("/home/ubuntu/work/ReBaseGuard-ps1-ops/level4/closure_proofs/"
              "p5y_k1_ps1_lifecycle_adapter/config/OPERATIONAL_CONTRACT.json")
PRED_COMMIT = "29b3bffb6a739121b66bdfcb23cb6b6544b39baf"


def main():
    code_commit = sys.argv[1] if len(sys.argv) > 1 else subprocess.check_output(
        ["git", "-C", str(NS), "rev-parse", "HEAD"]).decode().strip()
    c = json.loads(FROZEN.read_text())
    c.pop("_sha256", None)
    c["what_this_is"] = ("PS1 PORTABLE RECOVERY successor: per-cell durable finalization, graceful "
                         "drain, portable checkpoint, deterministic export, governed cross-host "
                         "resume. Execution/lifecycle only; no scientific semantics change.")
    c["parent"]["predecessor_commit"] = PRED_COMMIT
    c["parent"]["predecessor_tag"] = "p5y-k1-sr-ps1-production-authorized-preresult"
    c["parent"]["commit"] = code_commit
    c["parent"]["tag"] = "p5y-k1-sr-ps1-portable-recovery-preresult"
    c["service"]["unit_prefix"] = "rbg-p5y-k1-ps1-recov-"
    c["service"]["supervisor"] = "ops/supervisor.py"
    c["service"]["entry"] = "ops/produce_entry.py"
    c["service"]["science_command"] = (
        "ps1_cellseq_launcher.production_preflight() + run_production_cells(): per-cell durable "
        "finalization; the group result only frees a worker slot")
    c["recovery"] = {
        "predecessor_halt": {"run_id": "20260912T041203Z-962132d3", "reason": "RETRY_LIMIT",
                             "ledger_sha256": "0557bc229c3fcdb10cb0dd0b5836fa62a6b0e6c2512656e6ec7e49294b4d6cab",
                             "classification": "EXECUTION_LIFECYCLE_EXHAUSTION_NOT_A_SCIENTIFIC_COUNTEREXAMPLE",
                             "historical_cpu_h": 92.32, "historical_finalized_cells": 0,
                             "historical_patch_records": 24610,
                             "historical_patch_records_status": "ARCHIVAL_ONLY",
                             "torn_attempts_preserved": {"cells_0_to_63": 3}},
        "forensic_root_cause": "HOST_OR_SYSTEMD_INFRASTRUCTURE_EVENT (apt-daily-upgrade -> systemd re-exec)",
        "durability_boundary": "cell_done_XXXX.json, written atomically per cell",
        "drain": {"command": "prodctl.py drain --role <ROLE>",
                  "checked_at": "cell boundary only",
                  "increments_torn_attempts": False,
                  "targeted_stop": "--drain-after-completed N == N or the first safe boundary after N"},
        "retry_policy_generation_2": {"max_infra_tears_per_cell": 3,
                                      "GRACEFUL_DRAIN_is_a_tear": False,
                                      "historical_counters_reset": False},
        "checkpoint_schema": "rebaseguard.p5y.k1.ps1.portable-checkpoint.v1",
        "bundle_schema": "rebaseguard.p5y.k1.ps1.portable-bundle.v1",
        "host_maintenance_gate": "driver/host_guard.py (fails closed inside the declared window)",
        "cost": {"overhead_ratio_measured": 1.2264634058449526,
                 "campaign_cpu_h": 5694.0, "cells_per_24h": 24.9},
    }
    c["scientific_identity_changed"] = False
    src = {}
    for sub in ("driver", "ops", "code", "tests"):
        for p in sorted((NS / sub).glob("*.py")):
            src[f"{sub}/{p.name}"] = hashlib.sha256(p.read_bytes()).hexdigest()
    c["recovery_source_manifest"] = src

    # ESTABLISHED REPOSITORY RULE (model A, as the frozen lifecycle adapter does it):
    # opscommon.load_contract verifies sha256(RAW FILE BYTES) against the hash held in the
    # separate OPERATIONAL_CONTRACT_HASH file, and sets c["_sha256"] in memory only. The
    # contract therefore must NOT embed its own hash -- doing so is self-referential and
    # unsatisfiable, which is exactly the defect this repairs. Write the file first, then
    # hash the bytes that were written.
    out = NS / "config" / "OPERATIONAL_CONTRACT.json"
    payload = (json.dumps(c, indent=1, sort_keys=True) + "\n").encode()
    assert b'"_contract_sha256"' not in payload and b'"_sha256"' not in payload, \
        "the contract must never embed its own hash"
    out.write_bytes(payload)
    digest = hashlib.sha256(out.read_bytes()).hexdigest()      # hash of what is ON DISK
    (NS / "config" / "OPERATIONAL_CONTRACT_HASH").write_text(digest + "\n")
    print(f"wrote {out}")
    print(f"  parent.commit   : {code_commit}")
    print(f"  contract sha256 : {digest}  (== sha256 of the written file)")
    print(f"  source files    : {len(src)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
