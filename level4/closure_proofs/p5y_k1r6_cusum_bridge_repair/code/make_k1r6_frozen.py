"""Generate the K1R6 frozen config. Deterministic. Halts if the aux4 kernel or a generated stage drifted."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CFG = NS / "config"
REPO = Path("/home/ubuntu/work/ReBaseGuard")
AUX4 = REPO / "level4/closure_proofs/p5y_k1_cusum_aux4_fullcover"
K1R4 = NS.parent / "p5y_k1r4_bridge_successor"
K1R5 = NS.parent / "p5y_k1r5_cusum_entry"
TABLE = K1R4 / "config/CUSUM_BRIDGE_CELL_TABLE.json"
DRIVER = ("k1r6_cusum_entry.py", "identity_k1r6.py", "k1r6_chain.py", "fast_range_k1r6.py",
          "k1r6_certifier.py", "k1r6_bridge_resolver.py")
HALT = Path("/home/ubuntu/work/k1-bridge-prod/run-20260926T075918Z/CUSUM_HALT.json")
HALT_SHA256 = "12c0a4be97e0e9f1bedcbaa1e3bed1432c1fc616ec6d3b53e57fe17343eb272e"


def sha_file(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def canon(o) -> bytes:
    return (json.dumps(o, indent=1, sort_keys=True) + "\n").encode()


def main() -> int:
    CFG.mkdir(parents=True, exist_ok=True)
    chk = subprocess.run([sys.executable, str(NS / "code/make_k1r6_stages.py"), "--check"], capture_output=True, text=True)
    if chk.returncode != 0:
        raise SystemExit(f"GENERATED_STAGE_DRIFT: {chk.stdout}{chk.stderr}")
    aux = json.loads((AUX4 / "manifests/producer_manifest_v2.json").read_text())
    drift = [f for f, h in aux["files"].items() if sha_file(REPO / f) != h]
    if drift:
        raise SystemExit(f"KERNEL_DRIFT: aux4 files no longer match aux4's own manifest: {drift}")
    k4 = json.loads((K1R4 / "config/CHECKPOINT.json").read_text())
    if sha_file(TABLE) != k4["frozen_artifacts"]["CUSUM_BRIDGE_CELL_TABLE.json"]:
        raise SystemExit("BRIDGE_TABLE_DRIFT")
    if sha_file(HALT) != HALT_SHA256:
        raise SystemExit("PREDECESSOR_HALT_EVIDENCE_DRIFT")
    hist = json.loads((AUX4 / "diagnostics/cells/aux4_CUSUM_325_256.json").read_text())

    schema = {"schema": "rebaseguard.p5y.k1r6.result-schema.v1",
              "input_record": {"source": "K1R4 config/CUSUM_BRIDGE_CELL_TABLE.json (hash-verified twice: entry "
                                         "bridge_cell() against the K1R4 checkpoint, identity resolver against its pin)",
                               "fields": "unchanged from K1R5 (affine [p,'0/1'] left/right/e0/rho/C_evaluation; "
                                         "C_upper 'num/den'; index in {1000, 1001}; detector 'CUSUM')",
                               "identities": ["e0 == (left+right)/2", "rho == (right-left)/2",
                                              "identity resolver record == certified cell (checked before certify)"]},
              "output_record": {"top_level_keys": sorted(set(hist) | {"k1r6_bridge"}),
                                "inherited_from_aux4_record_keys": sorted(hist), "added_keys": ["k1r6_bridge"],
                                "k1r6_bridge": {
                                    "index": "int", "k1r4_table_sha256": "sha256", "k1r4_checkpoint_sha256": "sha256",
                                    "k1r6_checkpoint_sha256": "sha256",
                                    "identity_cells_sha256": "sha256 = exact K1R4 CUSUM bridge-table hash (CELL_PROVENANCE)",
                                    "identity_provenance": "CELL_PROVENANCE vs SCIENTIFIC_REGIME_PROVENANCE declaration",
                                    "zero_case": {"rule": "str", "zero_case_count": "int",
                                                  "firings": "[{seq, object, part in {low, high, plus_tail, minus_tail}, "
                                                             "reason, call_chain}]",
                                                  "by_object_part": "{'<object>|<part>': count}"}},
                                "scientific_hash": ("hash_v2.record_scientific_hash (frozen, by EXCLUSION): every "
                                                    "non-incidental leaf is hashed, so k1r6_bridge -- including the "
                                                    "deterministic zero_case firing record -- IS inside "
                                                    "scientific_content_hash by this schema's definition. The firing "
                                                    "record carries no timing and no counter; it is a deterministic "
                                                    "function of the certified inputs."),
                                "certificate_identity": "identity_k1r6.canonical_identity: identity4 field list and "
                                                        "IDENTITY_KIND unchanged; cells_sha256 + cell geometry from the "
                                                        "bridge table; checkpoint_hash / obligation_universe_total inherited",
                                "file": "k1r6_CUSUM_<index>_256.json"},
              "marker": {"schema": "rebaseguard.p5y.k1r6.cusum-cell-done-marker.v1", "file": "cell_done_<index>.json",
                         "binds": ["record_sha256", "scientific_content_hash", "producer_identity_hash",
                                   "k1r6_checkpoint_sha256", "cpu_seconds", "task_id"]},
              "evidence_layout": "one fresh directory per cell; must not exist before the run"}
    (CFG / "RESULT_SCHEMA.json").write_bytes(canon(schema))
    sys.path.insert(0, str(NS / "driver"))
    import k1r6_bridge_resolver as RES
    prov = {"schema": "rebaseguard.p5y.k1r6.identity-provenance.v1", **RES.PROVENANCE,
            "values_inherited": {"checkpoint_hash": "spec.CHECKPOINT_SHA256 (cover-ledger successor config/checkpoint.json)",
                                 "error_algebra_sha256": "spec.ERROR_ALGEBRA_SHA256",
                                 "obligation_universe_total": "spec.TOTAL_UNITS = 17978 (scheme constant; the "
                                                              "bridge adds 2 x 28 units OUTSIDE it, bound by K1R4)"},
            "value_rebound": {"cells_sha256": RES.BRIDGE_CELLS_SHA256}}
    (CFG / "IDENTITY_PROVENANCE.json").write_bytes(canon(prov))

    files = {str((REPO / f).resolve()): h for f, h in aux["files"].items()}
    for n in DRIVER:
        files[str((NS / "driver" / n).resolve())] = sha_file(NS / "driver" / n)
    for p in (TABLE, CFG / "TRANSFORMATION_MANIFEST.json", CFG / "RESULT_SCHEMA.json",
              CFG / "IDENTITY_PROVENANCE.json", NS / "code/make_k1r6_stages.py"):
        files[str(p.resolve())] = sha_file(p)
    manifest = {"schema": "k1.cusum-k1r6.producer-manifest.v1", "manifest_version": 1,
                "kind": "k1r6_cusum_bridge_repair_producer_manifest_v1",
                "files": files, "runtime": aux["runtime"],
                "inherited_kernel": {"source": "p5y_k1_cusum_aux4_fullcover/manifests/producer_manifest_v2.json",
                                     "aux4_manifest_sha256": sha_file(AUX4 / "manifests/producer_manifest_v2.json"),
                                     "files": len(aux["files"]), "verified_unchanged": True},
                "added": {"generated": [str((NS / "driver" / n).resolve()) for n in DRIVER[:5]],
                          "hand_written": [str((NS / "driver/k1r6_bridge_resolver.py").resolve())],
                          "data": [str(TABLE.resolve())],
                          "config": ["TRANSFORMATION_MANIFEST.json", "RESULT_SCHEMA.json", "IDENTITY_PROVENANCE.json"],
                          "generator": "code/make_k1r6_stages.py"},
                "boundary": {"membership": "exact absolute resolved path", "basename_exemptions": [],
                             "site_packages": "bound via runtime.backend_libraries",
                             "successor_module_binding": "verify_k1r6_modules(): each K1R6 module loaded from its manifest path"}}
    (CFG / "PRODUCER_MANIFEST.json").write_bytes(canon(manifest))
    mh = sha_file(CFG / "PRODUCER_MANIFEST.json")
    rh = hashlib.sha256(json.dumps(aux["runtime"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    pid = hashlib.sha256(json.dumps({"producer_manifest_hash": mh, "runtime_contract_hash": rh,
                                     "schema": manifest["schema"], "version": 1},
                                    sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    ident = {"schema": "rebaseguard.p5y.k1r6.producer-identity.v1", "producer": "K1R6-CUSUM-BRIDGE-REPAIR-PRODUCER",
             "producer_manifest_hash": mh, "runtime_contract_hash": rh, "producer_identity_hash": pid,
             "identity_scheme": "identity4 manifest-bound scheme (IDENTITY_KIND reused), generated as identity_k1r6: "
                                "bridge-native cell provenance, inherited scientific-regime provenance",
             "aux4_identity_reused": False, "k1r5_identity_reused": False}
    (CFG / "PRODUCER_IDENTITY.json").write_bytes(canon(ident))

    cons = {"schema": "rebaseguard.p5y.k1r6.concurrency.v1",
            "k1r6_writes": "only inside its own per-cell evidence directory (created exist_ok=False)",
            "k1r6_reads": ["K1R4 CUSUM bridge table (read-only, hash-checked)", "K1R6 config", "aux4 kernel"],
            "k1r4_sr": "RUNNING (6 genuine cells, run-20260926T075918Z) -- never touched by K1R6",
            "shared_mutable_files": [], "campaign_locks": "none", "ledgers": "none",
            "thread_contract": "unchanged: OMP/OPENBLAS/MKL/NUMEXPR/BLIS/VECLIB = 1 before import; flint.ctx.threads = 1",
            "rule": "fresh evidence roots disjoint from every K1R4 SR evidence root; cores not used by SR"}
    (CFG / "CONCURRENCY.json").write_bytes(canon(cons))
    cost = {"schema": "rebaseguard.p5y.k1r6.cost.v1", "cap_cpu_h_shared": 150.0,
            "previous_consumed_unsealed_cpu_h": 0.61,
            "previous_consumed_unsealed_detail": {"K1R5 CUSUM 1000": 0.508, "K1R5 CUSUM 1001": 0.102,
                                                  "source": "run-20260926T075918Z/CUSUM_HALT.json (wall of pinned "
                                                            "single-thread processes; upper bound)",
                                                  "never_reset": True},
            "committed_genuine_cpu_h_k1r6": 0.0, "k1r6_expected_cpu_h": 1.264,
            "k1r4_sr_expected_cpu_h": 76.23, "k1r4_sr_status": "running; committed CPU read from its sealed markers",
            "projected_total_cpu_h": round(0.61 + 1.264 + 76.23, 3),
            "accounting": "committed CPU-h from each sealed marker's cpu_seconds; unsealed consumption carried forward"}
    (CFG / "COST.json").write_bytes(canon(cost))
    pred = {"schema": "rebaseguard.p5y.k1r6.predecessor-binding.v1",
            "k1r5": {"freeze": "0cd4e8dd36615971745eb37c00197d735723cc82",
                     "checkpoint_sha256": (K1R5 / "config/CHECKPOINT_HASH").read_text().strip(),
                     "production": "FAILED 2026-09-26, run-20260926T075918Z, 0 sealed",
                     "halt_evidence_sha256": HALT_SHA256,
                     "failures": {"1000": "ORCHESTRATION_IDENTITY_DEFECT (identity4 -> repair_universe._cell_of KeyError)",
                                  "1001": "RANGE_OPERATOR_TOTALITY_GAP (empty sparse zero polynomial -> "
                                          "_power_to_bernstein ValueError)"},
                     "artifacts": "IMMUTABLE; not modified by K1R6"},
            "k1r4": {"freeze": "d9e8f1185c04ee8beb339efff091a073e6ebc21d",
                     "checkpoint_sha256": (K1R4 / "config/CHECKPOINT_HASH").read_text().strip(),
                     "cusum_bridge_table_sha256": k4["frozen_artifacts"]["CUSUM_BRIDGE_CELL_TABLE.json"],
                     "sr": "UNTOUCHED by K1R6 (running)"},
            "history": {"P5": "PARTIAL", "P5X": "PARTIAL", "P5Y_K1": "PARTIAL"}}
    (CFG / "PREDECESSOR_BINDING.json").write_bytes(canon(pred))
    arts = {n: sha_file(CFG / n) for n in ("PRODUCER_MANIFEST.json", "PRODUCER_IDENTITY.json", "RESULT_SCHEMA.json",
                                            "IDENTITY_PROVENANCE.json", "TRANSFORMATION_MANIFEST.json",
                                            "CONCURRENCY.json", "COST.json", "PREDECESSOR_BINDING.json")}
    cp = {"schema": "rebaseguard.p5y.k1r6.checkpoint.v1", "campaign": "P5Y-K1R6-CUSUM-BRIDGE-REPAIR",
          "scope": "the two K1R4 CUSUM bridge cells 1000, 1001 only; repairs exactly the two K1R5 production-path "
                   "defects; SR untouched",
          "frozen_artifacts": arts, "stages": {n: sha_file(NS / "driver" / n) for n in DRIVER},
          "producer_identity_hash": pid, "bridge_indices": [1000, 1001],
          "inherited": {"domain": "(11/2, 49750555/8388608]", "m_universe": [1, 2, 3, 5], "precision_bits": 256,
                        "target": "2/1", "b_cover_cap": "1/20", "cost_cap_cpu_h": 150.0},
          "previous_consumed_unsealed_cpu_h": 0.61,
          "production_started": False, "result_bearing": False, "k1_status": "PARTIAL (unchanged)"}
    (CFG / "CHECKPOINT.json").write_bytes(canon(cp))
    (CFG / "CHECKPOINT_HASH").write_text(sha_file(CFG / "CHECKPOINT.json") + "\n")
    print(json.dumps({"kernel_files_verified": len(aux["files"]), "producer_manifest_files": len(files),
                      "producer_identity": pid, "checkpoint": (CFG / "CHECKPOINT_HASH").read_text().strip()}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
