"""Phase 11: the PRE-RESULT PS1 production protocol (config/protocol.json). Reads only committed identities and the
Phase-4 qualification summary / Phase-10 constants; contains no production result."""
import hashlib
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parent


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    table = json.loads((CP / "p5y_k1_sr_o9_partition_successor/config/successor_cells.json").read_text())
    cons = json.loads((NS / "config/PS1_CONSTANTS.json").read_text())
    qs = json.loads((CP / "p5y_k1_ps1_production_qualification/evidence/qual_summary.json").read_text())
    probe = json.loads((CP / "p5y_k1_ps1_production_qualification/evidence/runtime_probe_aws.json").read_text())
    proto = {
        "schema": "rebaseguard.p5y.k1.ps1.production-protocol.v1", "result_bearing": False,
        "purpose": "Genuine full PS1 SR campaign over the 369 predeclared successor cells, AWS only (topology A).",
        "immutable_predecessors": {"ps1_partition_anchor": "9bfe3a71dd1884c933aa237896c21d59f9775c0e",
                                   "ps1_region_result_tag": "p5y-k1-sr-ps1-313-region-28-of-28",
                                   "historical_lifecycle": "bcec064 (p5y_k1_sr_production_lifecycle_successor)",
                                   "historical_production_authorization": "bd7cf26 (p5y_k1_sr_production_authorized_successor)",
                                   "historical_production_ledger_sha256": "d338679045d839ac5913f8aafc8b8b56683713206fa2b38b0c6d320c31ffb14a",
                                   "historical_caps": "1,126 and 4,500 CPU-h caps remain immutable history; superseded for PS1 only"},
        "partition": {"table_sha256": sha(CP / "p5y_k1_sr_o9_partition_successor/config/successor_cells.json"),
                      "n_cells": table["n_cells"], "cell_ids": [c["id"] for c in table["cells"]]},
        "science_unchanged": ["theorem target sup_e |R_D,m(e)| < 2, m = 1,2,3,5", "B_cover <= 1/20 per cell, STYLE_1",
                              "D = 11, Z = 20, 256 bits, candidate degree 16", "46 candidates / 102 contracts per cell",
                              "endpoint-strip successor, P1 softplus derivative bound, B_int successor",
                              "midpoint-only T3; governed mean-value curvature successor; frozen T4/T5 (generated verbatim)"],
        "executor": {"per_patch_function": "opt_core.core = frozen t3_patch.core + bit-identical OPT-S/OPT-C memoisation",
                     "identity_evidence": "343/343 cell-patch records bit-identical to committed certified records; "
                                          "full-cell identity of 150, 360-363, 368 in Phase 4 (qual_summary.identity_vs_certified)",
                     "unit": "deterministic group of 4 consecutive cells (terminal cell alone), patch-outer, shared per-patch "
                             "drift-independent panel cache; each cell admitted, accounted, verified, sealed individually"},
        "hosts": {"AWS": {"cpu": "Intel Xeon Platinum 8488C, 16 physical cores, SMT (32 logical), 123 GiB",
                          "workers": 16, "pinning": "logical cpus 0-15 (one per physical core; SMT siblings 16-31 unused)",
                          "runtime": probe["runtime"]["fingerprint"], "runtime_sha256": probe["runtime"]["sha256"]},
                  "VULTR": {"status": "NOT_QUALIFIED_FOR_PS1 in this protocol (no PS1 code deployed; owns no cells)"}},
        "shard_manifest_sha256": sha(NS / "config/SHARD_MANIFEST.json"),
        "cost": {"measured": qs["per_cell_cpu_h_stats"], "group4_per_cell": qs["group4_per_cell_cpu_h"],
                 "projection_cpu_h": qs["projection_cpu_h"]},
        "budget": {"global_cpu_cap": cons["GLOBAL_CPU_CAP"], "derivation": cons["derivation"],
                   "governed_overhead_cpu_h": cons["GOVERNED_OVERHEAD_CPU_H"],
                   "per_cell_reservation_cpu_h": cons["ROLES"]["AWS"]["per_cell_reservation_cpu_h"],
                   "invariant": "1.15*(committed + open reservations + TORN escrows + SHADOW + requested + overhead) <= cap at every admission",
                   "settlement": "charge = max(0, U_final - C_run) from the run cgroup (evidence hierarchy SUPERVISOR_FINAL > "
                                 "EXECSTOPPOST_CGROUP > JOURNAL > TAIL_BOUND)", "per_host_caps": "NONE"},
        "retry_and_halt": {"infrastructure_tear": "worker/process/host loss -> torn escrow, retry at most twice per cell; the 3rd tear halts",
                           "science_failure": "any worker-reported failure, malformed or unverifiable result, or any cell not "
                                              "T5_28_OF_28_PASS HALTS the campaign; never retried",
                           "cap": "admission refused when the invariant would fail; the campaign stops, it never over-spends"},
        "precision_contract": "every worker is a fresh interpreter that verifies 256-bit precision inside the scientific "
                              "context and the six-variable thread contract before accepting any task; the launcher probes the same",
        "transport_contract": "atomic JSON files only between processes; no multiprocessing Queue; no Arb object crosses a "
                              "process boundary; the launcher re-reads and re-hashes every evidence file from disk before sealing",
        "evidence_format": {"per_cell": "t3/t4/t5 canonical JSON + gzip(-n, mtime 0) patch records, sha256-bound in the sealed cell record",
                            "evidence_root": "/home/ubuntu/rbg-runtime/p5y_k1_ps1_production/evidence (outside every source tree)",
                            "sealed_records": "level4/closure_proofs/p5y_k1_ps1_production/production/cells/NNNN.json"},
        "determinism_contract": "bit-identical scientific records for identical (cell, patch) across processes, batch "
                                "sizes, worker counts and runs (measured); any divergence is a science failure",
        "provenance_firewall": {"genuine_result_namespace": "p5y_k1_ps1_production/production (+ evidence root)",
                                "production_ledger": "p5y_k1_ps1_production/production/PRODUCTION_LEDGER.json (NEW; the "
                                                     "historical ledger is neither read for admission nor written)",
                                "production_root": "separate local clone /home/ubuntu/work/ReBaseGuard-ps1-prod at the "
                                                   "authorization commit (own .git and runtime exclude policy)",
                                "genuine_cells_at_protocol_freeze": 0},
        "halt_rules": ["science failure", "3rd infrastructure tear of a cell", "cap invariant", "disk below 5 GiB",
                       "any identity drift (authorization, executor, table, patches, protocol, shard manifest, runtime)"],
    }
    b = (json.dumps(proto, indent=1, sort_keys=True) + "\n").encode()
    (NS / "config/protocol.json").write_bytes(b)
    print("protocol sha256", hashlib.sha256(b).hexdigest())


if __name__ == "__main__":
    main()
