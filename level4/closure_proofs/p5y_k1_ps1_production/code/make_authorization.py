"""Write config/LAUNCH_AUTHORIZATION.json (+ _HASH) binding the PS1 producer commit (argv[1]) and every identity.
The executor source manifest is COLLECTED, not declared: a fresh interpreter imports the complete production execution
surface (launcher, pool worker, per-patch core, aggregation, T4, T5 and their science dependencies) and every loaded
module file inside the repository is bound by sha256."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
CP = NS.parent
PY = "/home/ubuntu/work/ReBaseGuard/level4/.venv/bin/python"
PYTHONPATH_REL = ["level4/closure_proofs/p5y_k1_ps1_production_qualification/code",
                  "level4/closure_proofs/p5y_k1_sr_o9_partition_successor/code",
                  "level4/closure_proofs/p5y_k1_sr_o9_curvature_successor/code",
                  "level4/closure_proofs/p5y_k1_sr_o9_t345_successor/code",
                  "level4/closure_proofs/p5y_k1_sr_o9_t2_closure_successor/code",
                  "level4/closure_proofs/p5y_k1_sr_o9_bint_p1_bound_successor/code",
                  "level4/closure_proofs/p5y_k1_sr_o9_endpoint_strip_successor/code",
                  "level4/closure_proofs/p5y_k1_sr_o9_t2_per_patch_successor/code",
                  "level4/closure_proofs/p5y_k1_sr_o9_executor_t1_successor/code"]
ENV = {"HOME": "/home/ubuntu", "LANG": "C.UTF-8", "PATH": "/usr/bin:/bin", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
       "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "BLIS_NUM_THREADS": "1", "VECLIB_MAXIMUM_THREADS": "1"}
COLLECT = r'''
import json, sys
sys.path.insert(0, sys.argv[1])
import sr_o9_candidates as T
with T.scientific_precision():
    import production_launcher, ps1_pool_worker, opt_core, ps1_opt, succ_t3, succ_t3_aggregate, succ_t4, succ_t5, succ_cells, succ_t1
    import sr_o9_patch_certifier as PC
    PC.packet()
import global_budget, multihost, production_provenance
root = sys.argv[2]
print(json.dumps(sorted({m.__file__ for m in list(sys.modules.values()) if getattr(m, "__file__", None) and m.__file__.startswith(root)})))
'''


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    producer = sys.argv[1]
    assert len(producer) == 40
    env = dict(ENV, PYTHONPATH=":".join(str(ROOT / r) for r in PYTHONPATH_REL), PYTHONDONTWRITEBYTECODE="1")
    files = json.loads(subprocess.check_output([PY, "-c", COLLECT, str(NS / "driver"), str(ROOT) + "/"], env=env, cwd=str(ROOT)))
    rel = sorted(str(Path(f).relative_to(ROOT)) for f in files)
    got = {r: sha(ROOT / r) for r in rel}
    exe = hashlib.sha256(json.dumps(got, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()
    c = json.loads((NS / "config/PS1_CONSTANTS.json").read_text())
    rel_of = lambda p: str(Path(p).relative_to(ROOT))                    # noqa: E731
    table = CP / "p5y_k1_sr_o9_partition_successor/config/successor_cells.json"
    live = CP / "p5y_k1_sr_o9_t345_successor/config/live_patches.txt"
    auth = {"schema": "rebaseguard.p5y.k1.ps1.launch-authorization.v1", "result_bearing": False, "mode": "PRODUCTION",
            "campaign": "PS1 SR full campaign (369 predeclared successor cells)", "producer_commit": producer,
            "ps1_partition_anchor_commit": "9bfe3a71dd1884c933aa237896c21d59f9775c0e",
            "ps1_region_result_commit": subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "p5y-k1-sr-ps1-313-region-28-of-28^{commit}"]).decode().strip(),
            "checkpoint_sha256": sha(CP / "p5y_k1_cover_ledger_successor/config/checkpoint.json"),
            "successor_cells_path": rel_of(table), "successor_cells_sha256": sha(table),
            "live_patches_path": rel_of(live), "live_patches_sha256": sha(live), "live_patches_count": 3994,
            "protocol_path": rel_of(NS / "config/protocol.json"), "ps1_protocol_sha256": sha(NS / "config/protocol.json"),
            "shard_manifest_sha256": sha(NS / "config/SHARD_MANIFEST.json"),
            "executor_source_manifest": rel, "executor_source_sha256": got, "scientific_adapter_hash": exe,
            "pythonpath_rel": PYTHONPATH_REL,
            "hosts": {"AWS": {"python": PY, "environment": ENV, "workers": 16, "core_assignment": list(range(16)),
                              "per_cell_reservation_cpu_h": c["ROLES"]["AWS"]["per_cell_reservation_cpu_h"],
                              "work_dir": "/home/ubuntu/rbg-runtime/p5y_k1_ps1_production/work",
                              "evidence_dir": "/home/ubuntu/rbg-runtime/p5y_k1_ps1_production/evidence"}},
            "runtime_contract_hashes": {"AWS": c["ROLES"]["AWS"]["runtime_contract_hash"], "VULTR": "NOT_QUALIFIED_FOR_PS1"},
            "active_host": "AWS", "topology": "A_AWS_ONLY", "global_cpu_cap": c["GLOBAL_CPU_CAP"],
            "governed_overhead_cpu_h": c["GOVERNED_OVERHEAD_CPU_H"], "overhead_factor": 1.15,
            "far_field_obligation": {"work_id": "SR:-1:far_field:all_m", "status": "INHERITED (P5X-T3 far field and splice obligations, unchanged)"},
            "handoff": {"public_key_fingerprint": None, "status": "NOT_USED (topology A: AWS owns all 369 cells)"},
            "historical_production": {"ledger": "p5y_k1_sr_production_authorized_successor/production/PRODUCTION_LEDGER.json",
                                      "sha256": "d338679045d839ac5913f8aafc8b8b56683713206fa2b38b0c6d320c31ffb14a",
                                      "status": "IMMUTABLE HISTORY; SUPERSEDED FOR PS1 ONLY (not inherited)"}}
    b = (json.dumps(auth, indent=1, sort_keys=True) + "\n").encode()
    (NS / "config/LAUNCH_AUTHORIZATION.json").write_bytes(b)
    (NS / "config/LAUNCH_AUTHORIZATION_HASH").write_text(hashlib.sha256(b).hexdigest() + "\n")
    print("executor files", len(rel), "EXECUTOR_HASH", exe, "auth sha", hashlib.sha256(b).hexdigest())


if __name__ == "__main__":
    main()
