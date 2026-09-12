"""Phase B/M: emit the additive governed recovery successor contract."""
import hashlib, json, subprocess, sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
PROD = Path("/home/ubuntu/work/ReBaseGuard-ps1-prod/level4/closure_proofs/p5y_k1_ps1_production")
OPS = Path("/home/ubuntu/work/ReBaseGuard-ps1-ops/level4/closure_proofs/p5y_k1_ps1_lifecycle_adapter")


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(*a): return subprocess.run(["git"] + list(a), capture_output=True, text=True).stdout.strip()


def main():
    auth = json.loads((PROD / "config" / "LAUNCH_AUTHORIZATION.json").read_text())
    src = {p.name: sha(p) for p in sorted((NS / "driver").glob("*.py"))}
    src.update({f"code/{p.name}": sha(p) for p in sorted((NS / "code").glob("*.py"))})
    src.update({f"tests/{p.name}": sha(p) for p in sorted((NS / "tests").glob("*.py"))})

    c = {
     "schema": "rebaseguard.p5y.k1.ps1.portable-recovery-successor.v1",
     "purpose": ("Additive governed recovery successor. Repairs EXECUTION/LIFECYCLE persistence "
                 "only: per-cell finalization, graceful drain, portable checkpoint, cross-host "
                 "resume. No scientific semantics are touched."),
     "result_bearing": False,
     "genuine_cells_at_freeze": 0,

     "predecessor": {
       "production_authorization_commit": "29b3bffb6a739121b66bdfcb23cb6b6544b39baf",
       "lifecycle_adapter_commit": "b45fb15285f9995271e14124e62b07930e5b904a",
       "halted_run_id": "20260912T041203Z-962132d3",
       "halted_ledger_sha256": "0557bc229c3fcdb10cb0dd0b5836fa62a6b0e6c2512656e6ec7e49294b4d6cab",
       "halt_reason": "RETRY_LIMIT",
       "halt_classification": "EXECUTION_LIFECYCLE_EXHAUSTION_NOT_A_SCIENTIFIC_COUNTEREXAMPLE",
       "historical_cpu_h": 92.32,
       "historical_finalized_cells": 0,
       "historical_committed_scientific_results": 0,
       "historical_patch_records": 24610,
       "historical_patch_records_status": "ARCHIVAL_ONLY_NEVER_SCIENTIFICALLY_ADMISSIBLE",
       "historical_torn_attempts": {"cells_0_to_63": 3},
       "immutability": "every historical run, settlement, torn counter, ledger hash and CPU figure is preserved verbatim",
     },

     "forensic_incident": {
       "classification": "HOST_OR_SYSTEMD_INFRASTRUCTURE_EVENT",
       "established": True,
       "events_utc": ["2026-09-12T06:01:57Z", "2026-09-12T06:02:07Z"],
       "mechanism": ("apt-daily-upgrade.service ran unattended-upgrades; systemd 255.4-1ubuntu8.17 "
                     "was re-executed (Reexecuting requested from client PID 256457 'systemctl'); the "
                     "service restart cascade stopped and restarted the transient production unit twice"),
       "ruled_out": ["OOM (dmesg oom-kill count 0)", "disk pressure", "operator/agent stop",
                     "scientific failure", "lifecycle implementation defect"],
       "third_tear": "2026-09-12T09:58:15Z sanctioned operator cost-control stop (STOP_SIGNAL_SIGTERM)",
     },

     "scientific_invariants_unchanged": {
       "producer_commit": auth["producer_commit"],
       "scientific_adapter_hash": auth["scientific_adapter_hash"],
       "successor_cells_sha256": auth["successor_cells_sha256"],
       "live_patches_sha256": auth["live_patches_sha256"],
       "live_patches_count": auth["live_patches_count"],
       "ps1_protocol_sha256": auth["ps1_protocol_sha256"],
       "shard_manifest_sha256": auth["shard_manifest_sha256"],
       "ps1_partition_anchor_commit": auth["ps1_partition_anchor_commit"],
       "precision_bits": 256, "cells": 369, "obligations_per_cell": 28,
       "candidates": 46, "contracts": 102, "D": 11, "Z": 20,
       "B_cover": "<= 1/20 STYLE_1", "theorem": "sup_e |R_D,m(e)| < 2, m = 1,2,3,5",
     },

     "phase_a_finding": {
       "CELL_LEVEL_FINALIZATION_IS_EXECUTION_ONLY": True,
       "structural_proof": ("succ_t3_aggregate.aggregate() strips cpu_seconds, peak_rss_kib, "
                            "cache_hits and cache_misses from every record before "
                            "consumed_records_sha256 and t3_record_sha256 are computed"),
       "empirical_proof": {
         "method": "identical cell-0 records, execution metadata scrambled, different directories",
         "consumed_records_sha256": "9b92706b0c186dbae2604a4641db36f555a5a352b4a0b53b882424f9a17e62c2",
         "t3_record_sha256": "cf16484528141be319837f59b9af2bc43f76d83d3f2a6fdddabad9089bb864e9",
         "t4_record_sha256": "86acf5a3b634ac438d6cb474b3e2b77ce95c4e156ac3ee5fb5677a6c8627f54d",
         "scientific_content_hash": "1511cd5cffe3fbcfeaa12271e4a03b52056759b3810a5b9e4de83a1df96a8cde",
         "identical_across_both_variants": True,
         "location_independence": "same basename in different directories yields identical hashes",
       },
     },

     "execution_change": {
       "predecessor_ordering": "patch-outer / cells-inner, one per-patch cache shared across the 4 cells",
       "successor_ordering": "cells-outer / patch-inner, cache per (cell, patch)",
       "why": ("a cell can only be finalized when all 3,994 of its patches are done; under "
               "patch-outer no cell reaches that boundary until all four do (~50h). Per-cell "
               "durability therefore REQUIRES cells-outer, which forfeits the cross-cell cache. "
               "The two are mutually exclusive; this is structural, not an implementation choice."),
       "cost": {"grouped_per_cell_cpu_h": [11.960742175300394, 12.582210991480842],
                "solo_cache_builder_cpu_h": 14.982282971,
                "measured_benchmark": {
                  "method": "same 12 live patches, same cells [0,1,2,3], same frozen opt_core.core, both orderings",
                  "cpu_predecessor_s": 641.993969814, "cpu_successor_s": 787.3821107500002,
                  "overhead_ratio": 1.2264634058449526, "overhead_pct": 22.6,
                  "cache_hits_predecessor": 1098, "cache_hits_successor": 0,
                  "records_compared": 48, "records_identical": 48,
                  "stripped_bundle_sha256": "a42d0a95aa07cb1bf4e9cda4a06ae92ee004ada45c898191b2a689958b9510ae",
                  "scientific_identity": "BIT_IDENTICAL_ON_REAL_COMPUTATION"},
                "campaign_predecessor_cpu_h": 4642.0,
                "campaign_successor_cpu_h": 5694.0,
                "per_cell_successor_cpu_h": 15.43,
                "delta_cpu_h": 1052.0, "delta_pct": 22.6,
                "global_cap_cpu_h": auth["global_cpu_cap"],
                "headroom_after_cpu_h": 906.0,
                "throughput_finalized_cells_per_24h_16_workers": 24.9,
                "estimated_campaign_days": 14.8},
       "cells_per_group": {"value": 4, "role": "scheduling/reservation unit only",
                           "governed_parameter": True,
                           "note": "operator may trade durability granularity back for cache reuse"},
       "durability_point": "atomic cell_done_XXXX.json written the instant a cell is complete and verified",
     },

     "retry_policy_generation_2": {
       "taxonomy": ["SCIENTIFIC_FAILURE", "INFRASTRUCTURE_TEAR",
                    "OPERATOR_EMERGENCY_STOP", "GRACEFUL_DRAIN"],
       "SCIENTIFIC_FAILURE": "halts immediately, never retried (inherited unchanged)",
       "INFRASTRUCTURE_TEAR": "bounded: max 3 per cell within generation 2",
       "OPERATOR_EMERGENCY_STOP": "tears only cells in flight; counts against the bound",
       "GRACEFUL_DRAIN": "NOT a tear; never increments torn_attempts",
       "historical_counters": "generation-1 torn_attempts (cells 0-63 = 3) remain visible forever and are NOT reset",
       "fresh_allowance_justification": ("generation 1 exhausted its allowance solely to an established "
                                         "environmental cause now gated by driver/host_guard.py; the "
                                         "allowance is fresh, bounded and predeclared, never unlimited"),
       "max_infra_tears_per_cell": 3,
     },

     "drain_semantics": {
       "checked_only_at": "a cell boundary, never mid-cell",
       "on_drain": ["enter DRAINING atomically", "stop admitting new cells",
                    "let in-flight cells reach their finalization boundary",
                    "seal/hash/commit each completed cell", "no worker starts another cell",
                    "settle ledger, release lock, emit checkpoint, exit cleanly"],
       "torn_increment": False,
       "distinct_from_stop": "STOP is emergency termination and does tear in-flight cells; DRAIN does not",
       "targeted_stop": {"flag": "--drain-after-completed N",
                         "semantics": "N OR THE FIRST SAFE DRAIN BOUNDARY AFTER N",
                         "honest_caveat": ("concurrent workers may finalize several cells between the "
                                           "check and the boundary, so the final count may exceed N; "
                                           "exact N is NOT promised")},
     },

     "checkpoint": {"schema": "rebaseguard.p5y.k1.ps1.portable-checkpoint.v1",
                    "bundle_schema": "rebaseguard.p5y.k1.ps1.portable-bundle.v1",
                    "invariant": "FINALIZED u PENDING = 369 cells; FINALIZED n PENDING = empty",
                    "excludes_mutable_state": ["pid", "flock", "systemd invocation", "open reservations",
                                               "in-memory cache", "temp writer state"]},

     "host_maintenance_gate": {
       "module": "driver/host_guard.py",
       "behaviour": "fails closed when a disruptive maintenance timer fires inside the declared window",
       "never_modifies_host_policy": True,
       "privilege_prefix_source": "frozen lifecycle contract hosts.<ROLE>.launch_prefix",
     },

     "source_manifest": src,
     "worktree_commit_at_freeze": git("-C", str(NS), "rev-parse", "HEAD"),
    }
    c["contract_sha256"] = hashlib.sha256(
        json.dumps(c, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    out = NS / "config" / "RECOVERY_CONTRACT.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(c, indent=1, sort_keys=True) + "\n")
    (NS / "config" / "RECOVERY_CONTRACT_HASH").write_text(c["contract_sha256"] + "\n")
    print(f"wrote {out}")
    print(f"  contract_sha256 : {c['contract_sha256']}")
    print(f"  source files    : {len(src)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
