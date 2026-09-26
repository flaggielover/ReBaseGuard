"""Generate the K1R5 frozen config. Deterministic. Halts if the aux4 kernel drifted."""
import hashlib
import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CFG = NS / "config"
REPO = Path("/home/ubuntu/work/ReBaseGuard")
AUX4 = REPO / "level4/closure_proofs/p5y_k1_cusum_aux4_fullcover"
K1R4 = NS.parent / "p5y_k1r4_bridge_successor"
WRAPPER = NS / "driver/k1r5_cusum_entry.py"


def sha_file(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def canon(o) -> bytes:
    return (json.dumps(o, indent=1, sort_keys=True) + "\n").encode()


def main() -> int:
    CFG.mkdir(parents=True, exist_ok=True)
    aux = json.loads((AUX4 / "manifests/producer_manifest_v2.json").read_text())
    drift = [f for f, h in aux["files"].items() if sha_file(REPO / f) != h]
    if drift:
        raise SystemExit(f"KERNEL_DRIFT: aux4 files no longer match aux4's own manifest: {drift}")
    files = {str((REPO / f).resolve()): h for f, h in aux["files"].items()}
    files[str(WRAPPER.resolve())] = sha_file(WRAPPER)
    manifest = {"schema": "k1.cusum-k1r5.producer-manifest.v1", "manifest_version": 1,
                "kind": "k1r5_cusum_bridge_entry_producer_manifest_v1",
                "files": files, "runtime": aux["runtime"],
                "inherited_kernel": {"source": "p5y_k1_cusum_aux4_fullcover/manifests/producer_manifest_v2.json",
                                     "aux4_manifest_sha256": sha_file(AUX4 / "manifests/producer_manifest_v2.json"),
                                     "files": len(aux["files"]), "verified_unchanged": True},
                "added": {"wrapper": str(WRAPPER.resolve())},
                "boundary": {"membership": "exact absolute resolved path",
                             "basename_exemptions": [], "site_packages": "bound via runtime.backend_libraries"}}
    (CFG / "PRODUCER_MANIFEST.json").write_bytes(canon(manifest))
    mh = sha_file(CFG / "PRODUCER_MANIFEST.json")
    rh = hashlib.sha256(json.dumps(aux["runtime"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    pid = hashlib.sha256(json.dumps({"producer_manifest_hash": mh, "runtime_contract_hash": rh,
                                     "schema": manifest["schema"], "version": 1},
                                    sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    ident = {"schema": "rebaseguard.p5y.k1r5.producer-identity.v1", "producer": "K1R5-CUSUM-BRIDGE-PRODUCER",
             "producer_manifest_hash": mh, "runtime_contract_hash": rh, "producer_identity_hash": pid,
             "identity_scheme": "identity4 manifest-bound scheme (IDENTITY_KIND reused as the scheme name), "
                                "bound to the K1R5 manifest rather than aux4's",
             "aux4_identity_reused": False}
    (CFG / "PRODUCER_IDENTITY.json").write_bytes(canon(ident))
    hist = json.loads((AUX4 / "diagnostics/cells/aux4_CUSUM_325_256.json").read_text())
    schema = {"schema": "rebaseguard.p5y.k1r5.result-schema.v1",
              "input_record": {"fields": {"left": "affine [p,'0/1']", "right": "affine [p,'0/1']",
                                          "e0": "affine [p,'0/1']", "rho": "affine [p,'0/1']",
                                          "C_evaluation": "affine [p,'0/1']", "C_upper": "plain 'num/den' str",
                                          "index": "int in {1000, 1001}", "detector": "'CUSUM'",
                                          "nominal_step_half_width": "str (not read by the kernel)"},
                               "identities": ["e0 == (left+right)/2", "rho == (right-left)/2"],
                               "source": "K1R4 config/CUSUM_BRIDGE_CELL_TABLE.json (hash-verified)"},
              "output_record": {"top_level_keys": sorted(set(hist) | {"k1r5_bridge"}),
                                "inherited_from_aux4_record_keys": sorted(hist),
                                "added_keys": ["k1r5_bridge"],
                                "scientific_hash": "hash_v2.record_scientific_hash (frozen, schema-driven)",
                                "file": "k1r5_CUSUM_<index>_256.json"},
              "marker": {"schema": "rebaseguard.p5y.k1r5.cusum-cell-done-marker.v1",
                         "file": "cell_done_<index>.json",
                         "binds": ["record_sha256", "scientific_content_hash", "producer_identity_hash",
                                   "k1r5_checkpoint_sha256", "cpu_seconds", "task_id"]},
              "evidence_layout": "one fresh directory per cell; must not exist before the run"}
    (CFG / "RESULT_SCHEMA.json").write_bytes(canon(schema))
    cons = {"schema": "rebaseguard.p5y.k1r5.concurrency.v1",
            "k1r5_writes": "only inside its own per-cell evidence directory (created exist_ok=False)",
            "k1r5_reads": ["K1R4 CUSUM bridge table (read-only, hash-checked)", "K1R5 config", "aux4 kernel"],
            "k1r4_sr_writes": "only inside its own per-cell evidence directories (exist_ok=False)",
            "shared_mutable_files": [], "campaign_locks": "none in either path", "ledgers": "none in either path",
            "thread_contract": {"k1r5": "OMP/OPENBLAS/MKL/NUMEXPR = 1 pinned at qualify4 import; flint.ctx.threads = 1",
                                "k1r4_sr": "OMP/OPENBLAS/MKL/NUMEXPR/BLIS/VECLIB = 1 at import and call"},
            "resources": {"k1r5_peak_rss_gib_per_cell": 0.25, "k1r4_sr_peak_rss_gib_per_cell": 0.28,
                          "combined_peak_gib": 2.2, "host_ram_gib": 123,
                          "processes": 8, "physical_cores": 16},
            "rule": "use evidence roots that are disjoint from every K1R4 SR evidence root"}
    (CFG / "CONCURRENCY.json").write_bytes(canon(cons))
    cost = {"schema": "rebaseguard.p5y.k1r5.cost.v1", "cap_cpu_h_shared": 150.0,
            "consumed_genuine_cpu_h_all_k1_repairs": 0.0, "k1r5_expected_cpu_h": 1.264,
            "k1r4_sr_expected_cpu_h": 76.23, "combined_expected_cpu_h": 77.494,
            "accounting": "committed CPU-h read from each sealed marker's cpu_seconds"}
    (CFG / "COST.json").write_bytes(canon(cost))
    k4 = json.loads((K1R4 / "config/CHECKPOINT.json").read_text())
    pred = {"schema": "rebaseguard.p5y.k1r5.predecessor-binding.v1",
            "k1r4": {"freeze": "d9e8f1185c04ee8beb339efff091a073e6ebc21d",
                     "checkpoint_sha256": (K1R4 / "config/CHECKPOINT_HASH").read_text().strip(),
                     "cusum_bridge_table_sha256": k4["frozen_artifacts"]["CUSUM_BRIDGE_CELL_TABLE.json"],
                     "sr": "UNTOUCHED by K1R5"},
            "k1r3": "PREREGISTRATION FAIL, not frozen (6fb3e17)", "k1r2": "HALTED (b258c18)",
            "k1r": "HALTED_BY_GOVERNANCE after B1 PASS", "b1": "INHERITED PASS",
            "history": {"P5": "PARTIAL", "P5X": "PARTIAL", "P5Y_K1": "PARTIAL"},
            "reason": "K1R4 froze the CUSUM cells and kernel but no production orchestration for them"}
    (CFG / "PREDECESSOR_BINDING.json").write_bytes(canon(pred))
    arts = {n: sha_file(CFG / n) for n in ("PRODUCER_MANIFEST.json", "PRODUCER_IDENTITY.json",
                                            "RESULT_SCHEMA.json", "CONCURRENCY.json", "COST.json",
                                            "PREDECESSOR_BINDING.json")}
    cp = {"schema": "rebaseguard.p5y.k1r5.checkpoint.v1", "campaign": "P5Y-K1R5-CUSUM-ENTRY",
          "scope": "the two frozen K1R4 CUSUM bridge cells 1000, 1001 only; SR untouched",
          "frozen_artifacts": arts, "wrapper_sha256": sha_file(WRAPPER),
          "producer_identity_hash": pid, "bridge_indices": [1000, 1001],
          "inherited": {"domain": "(11/2, 49750555/8388608]", "m_universe": [1, 2, 3, 5],
                        "precision_bits": 256, "target": "2/1", "b_cover_cap": "1/20", "cost_cap_cpu_h": 150.0},
          "production_started": False, "result_bearing": False, "k1_status": "PARTIAL (unchanged)"}
    (CFG / "CHECKPOINT.json").write_bytes(canon(cp))
    (CFG / "CHECKPOINT_HASH").write_text(sha_file(CFG / "CHECKPOINT.json") + "\n")
    print(json.dumps({"kernel_files_verified": len(aux["files"]), "producer_identity": pid,
                      "checkpoint": (CFG / "CHECKPOINT_HASH").read_text().strip()}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
