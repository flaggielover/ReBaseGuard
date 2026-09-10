"""Phase 7: consolidate T2 per-patch evidence and evaluate the 13-point T2 closure gate."""
import glob
import hashlib
import json
import subprocess
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parent
REPO = CP.parents[1]
EV = NS / "evidence"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()          # noqa: E731
jl = lambda p: json.loads(Path(p).read_text())                             # noqa: E731


def git(*a, repo=REPO):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True).stdout.strip()


def last_json_line(p):
    return json.loads(Path(p).read_text().strip().splitlines()[-1])


def main():
    p1 = jl(EV / "phase1_predecessors.json")
    audit = jl(EV / "equation_audit.json")
    uni = jl(EV / "universe_conformance.json")
    det = jl(EV / "determinism.json")
    cache = jl(EV / "cache_equivalence_compare.json")
    cmeas = jl(EV / "cache_measurements.json")
    dag = []
    for f in sorted(glob.glob(str(EV / "dag/*.json"))):
        r = jl(f)
        s = last_json_line(f[:-5] + ".log")
        dag.append({"file": str(Path(f).relative_to(NS)), "file_sha256": sha(f), **s,
                    "cpu_seconds_certify": r["run"]["cpu_seconds_certify"], "peak_rss_kib": r["run"]["peak_rss_kib"],
                    "candidate_identity_list_sha256": r["scientific"]["candidate_identity_list_sha256"],
                    "cell_identity_sha256": r["scientific"]["cell_identity_sha256"],
                    "equation_map_sha256": r["scientific"]["equation_map_sha256"],
                    "settings": r["scientific"]["settings"],
                    "no_deferred": all(v["class"] not in ("DEFERRED", "NOT_IMPLEMENTED") for v in r["scientific"]["nodes"].values()),
                    "dependency_hashes_complete": all(all(h for h in v["dependency_identity_hashes"].values())
                                                      for v in r["scientific"]["nodes"].values())})
    first = jl(sorted(glob.glob(str(EV / "dag/*.json")))[0])["scientific"]
    contracts = first["contracts_evaluated"]
    cand_by_cell = {}
    for f in sorted(glob.glob(str(EV / "dag/*.json"))):
        s = jl(f)["scientific"]
        cand_by_cell[str(s["case"]["cell"])] = {"candidate_identity_hashes": s["candidate_identity_hashes"],
                                                "candidate_identity_list_sha256": s["candidate_identity_list_sha256"]}
    code = {p.name: sha(p) for p in sorted((NS / "code").glob("*.py"))}
    deps = {rel: sha(CP / rel) for rel in (
        "p5y_k1_sr_o9_t2_per_patch_successor/code/sr_o9_equations.py",
        "p5y_k1_sr_o9_t2_per_patch_successor/code/sr_o9_patch_certifier.py",
        "p5y_k1_sr_o9_endpoint_strip_successor/code/sr_o9_endpoint_strips.py",
        "p5y_k1_sr_o9_bint_p1_bound_successor/code/sr_o9_bint_p1.py",
        "p5y_k1_sr_o9_executor_t1_successor/code/sr_o9_candidates.py",
        "p5y_k1_sr_o9_executor_t1_successor/code/t1_reference.py",
        "p5y_k1_task1r_budget_harness/code/harness.py",
        "p5y_k1_sr_backend_cost_audit/code/opt_backend.py",
        "p5x_global_nonlinear_dynamics/compute_optimization_r3_sr_symbolic/sr_local.py",
        "p5y_k1_cusum_aux4_fullcover/code/schema.py")}
    neg_path = "level4/closure_proofs/p5y_k1_sr_o9_t2_per_patch_successor/config/T2_NOT_CLOSING_RECORD.json"
    neg_now = jl(REPO / neg_path)
    neg_committed = hashlib.sha256(subprocess.run(["git", "-C", str(REPO), "show", f"29ee382b:{neg_path}"],
                                                  capture_output=True).stdout).hexdigest()
    prod = {}
    for w in ("ReBaseGuard-sr-parallel", "ReBaseGuard-sr-lifecycle"):
        rp = REPO.parent / w
        prod[w] = {"head": git("rev-parse", "--short", "HEAD", repo=rp), "dirty": bool(git("status", "--porcelain", repo=rp))}
    unit = "rbg-p5y-k1-sr-prod-aws-20260910T105333Z-640db8f2.service"
    st = subprocess.run(["systemctl", "show", unit, "-p", "ActiveState", "-p", "SubState", "-p", "StateChangeTimestamp"],
                        capture_output=True, text=True).stdout.strip().splitlines()
    active = subprocess.run(["systemctl", "list-units", "--state=active", "--no-pager", "--plain"],
                            capture_output=True, text=True).stdout
    procs = subprocess.run(["pgrep", "-af", "prodctl|supervisor.py|integrated_sr|production_launcher"],
                           capture_output=True, text=True).stdout.strip()
    prod.update({"historical_unit": unit, "historical_unit_state": st,
                 "active_rbg_units": [l for l in active.splitlines() if "rbg-" in l],
                 "production_processes": [l for l in procs.splitlines() if "pgrep" not in l]})
    prod_untouched = (prod["ReBaseGuard-sr-parallel"] == {"head": "bd7cf26", "dirty": False}
                      and prod["ReBaseGuard-sr-lifecycle"] == {"head": "bcec064", "dirty": False}
                      and not prod["active_rbg_units"] and not prod["production_processes"])
    settings_ok = all(d["settings"] == dag[0]["settings"] for d in dag) and dag[0]["settings"]["D"] == 11 and \
        dag[0]["settings"]["Z"] == 20 and dag[0]["settings"]["bits"] == 256 and dag[0]["settings"]["cand_degree"] == 16
    gate = {
        "1_all_predecessor_verifiers_pass": p1["all_pass"],
        "2_equation_map_complete": audit["checks"]["equation_map_equals_committed"] and audit["checks"]["nodes_45_residual_18_image_63_unique"]
                                   and audit["checks"]["node_contracts_equal_operator_applications"],
        "3_all_102_contracts_map_exactly": all(audit["checks"][k] for k in (
            "every_operator_use_maps_to_a_declared_contract", "contract_ids_bijective", "contracts_used_equal_frozen_census",
            "contracts_102_shifts_43_35_20_4", "h1_equals_delta_minus_K1_symbolic", "h1_numeric_closed_form_contained_all",
            "no_Phi_shortcut_in_certifier_sources")),
        "4_representative_full_DAG_passes": len(dag) == 36 and all(d["nodes_expected"] and d["n_nodes"] == 63 and d["contracts"] == 102
                                                                   and d["all_finite_nonnegative"] and d["no_deferred"]
                                                                   and d["dependency_hashes_complete"] for d in dag),
        "5_endpoint_gate_passes": all(d["endpoint_PASS"] for d in dag),
        "6_B_int_passes": all(d["B_int_PASS"] for d in dag),
        "7_all_local_gates_pass": all(d["all_F_local_gates_PASS"] and not d["failing"] for d in dag),
        "8_determinism_zero_scientific_leaves_moved": det["zero_scientific_leaves_moved"] and det["all_scientific_identical"],
        "9_cache_reuse_bit_identical": cache["all_scientific_identical"] and cache["zero_scientific_leaves_moved"],
        "10_all_3994_patches_conform": uni["live_patches"] == 3994 == uni["patches_matching_governance_table"] and uni["P1_exact_all_pass"]
                                       and uni["strip_P1_all_pass"] and uni["span_closure_all"] and uni["panel_ids_unique"]
                                       and uni["panel_ids_all_canonical_v2"] and uni["strip_ids_all_canonical_v3"]
                                       and uni["raw_shift"]["drift_nonfinite"] == 0 and uni["raw_shift"]["repeated_multiplication_installed"]
                                       and not uni["census_panel_units_83452_used"] and uni["cells"]["cell315"]["right_is_exactly_c_SR"]
                                       and uni["cells"]["all_finite"],
        "11_panels_76475_strips_7988_exact": uni["contracted_panels"] == 76475 and uni["endpoint_strips"] == 7988
                                             and uni["panel_units_historical_convention"] == 84463 and uni["panel_ids_count"] == 76475,
        "12_no_scientific_setting_changed": settings_ok and p1["verifiers"]["verify_bint_governance"]["checks"]["frozen_settings_unchanged"],
        "13_no_production_artifact_touched": prod_untouched,
    }
    closed = all(gate.values())
    rec = {
        "schema": "rebaseguard.p5y.k1.sr.o9.t2-closure-record.v1",
        "status": "T2_PER_PATCH_CERTIFICATION_CLOSED" if closed else "T2_NOT_CLOSED",
        "scope": "patch-level certified residual execution only",
        "not_claimed": ["whole-cell delta_cell closure", "midpoint refinement closure", "B_cover closure",
                        "28-obligation cell closure", "production readiness", "T3/T4/T5"],
        "closure_gate": gate,
        "lineage": {
            "M0": {"ruling": "DEGREE16_CONFORMANT (binding SR bidegree (16,16)); cell 315 exact splice; status rule",
                   "recorded_in": "p5y_k1_sr_o9_executor_t1_successor/code/sr_o9_candidates.py (T1 ab8d197)"},
            "T1": p1["commits"]["t1"], "pre_T2_governance": p1["commits"]["pre_t2_governance"],
            "A5_amendment": p1["commits"]["a5_amendment"], "T2_negative_evidence": p1["commits"]["t2_negative_evidence"],
            "endpoint_strip_successor": p1["commits"]["endpoint_strip_successor"],
            "bint_representation_audit": p1["commits"]["bint_representation_audit"],
            "P1_bound_B_int_authorization": p1["commits"]["bint_governance_authorization"],
            "B_int_pilot": p1["commits"]["bint_pilot"], "tags": p1["tags"]},
        "historical_negative_results_preserved": {
            "T2_NOT_CLOSING_RECORD": {"path": neg_path, "status": neg_now["status"],
                                      "sha256_now": sha(REPO / neg_path), "sha256_at_29ee382b": neg_committed,
                                      "unchanged": sha(REPO / neg_path) == neg_committed},
            "fa92afb": "BINT_REPRESENTATION_NUMERICALLY_NOT_CLOSING (separate-remainder route) stands",
            "b48973d6_status": "ENDPOINT_STRIP_SUCCESSOR_MICROPILOT_PASS__INT_LINE_OPEN stands as recorded"},
        "config_hashes": {
            "EQUATION_MAP.json": sha(CP / "p5y_k1_sr_o9_t2_per_patch_successor/config/EQUATION_MAP.json"),
            "PRE_T2_GOVERNANCE.json": sha(CP / "p5y_k1_sr_o9_pre_t2_governance_successor/config/PRE_T2_GOVERNANCE.json"),
            "P1_PANEL_UNIVERSE.json": sha(CP / "p5y_k1_sr_o9_pre_t2_governance_successor/config/P1_PANEL_UNIVERSE.json"),
            "A5_AMENDMENT.json": sha(CP / "p5y_k1_sr_o9_pre_t2_a5_amendment/config/A5_AMENDMENT.json"),
            "ENDPOINT_STRIP_MANIFEST.json": sha(CP / "p5y_k1_sr_o9_endpoint_strip_successor/config/ENDPOINT_STRIP_MANIFEST.json"),
            "P1_BOUND_REUSE_AUTHORIZATION.json": sha(CP / "p5y_k1_sr_o9_bint_p1_bound_successor/config/P1_BOUND_REUSE_AUTHORIZATION.json"),
            "BINT_P1_PILOT_MANIFEST.json": sha(CP / "p5y_k1_sr_o9_bint_p1_bound_successor/config/BINT_P1_PILOT_MANIFEST.json"),
            "T1_MANIFEST.json": sha(CP / "p5y_k1_sr_o9_executor_t1_successor/config/T1_MANIFEST.json")},
        "equation_map_sha256": audit["info"]["equation_map_sha256"],
        "certifier_source_sha256": {"successor": code, "dependencies": deps},
        "runtime_contract": {"authorized": "d49f043755ef658a60e3c4017022ddecf0642a087a6e5bb0c1f2aefbe9721191",
                             "live_equals_authorized": p1["verifiers"]["verify_pre_t2"]["checks"]["runtime_is_authorized"]},
        "scientific_settings": dag[0]["settings"],
        "candidates": {"count": 46, "basis_order_equals_T1": audit["checks"]["candidates_46_unique_equal_T1"],
                       "per_representative_cell": cand_by_cell},
        "contracts": {"count": len(contracts), "ids": contracts, "ids_sha256": hashlib.sha256(json.dumps(contracts).encode()).hexdigest(),
                      "by_shift": audit["info"]["by_shift"]},
        "universe": {k: uni[k] for k in ("live_patches", "contracted_panels", "endpoint_strips", "panel_units_historical_convention",
                                         "patches_where_exec_differs_from_census", "P1_worst_headroom_rel", "panel_ids_sha256",
                                         "strip_ids_sha256", "table_sha256", "governance_table_sha256", "raw_shift", "cells")},
        "universe_files": {f: sha(EV / f) for f in ("universe_table.json", "universe_panel_ids.json", "universe_conformance.json")},
        "representative_full_dag": dag,
        "determinism": {"file": "evidence/determinism.json", "sha256": sha(EV / "determinism.json"),
                        "pairs": [{"case": p["b"].split("/")[-1], "leaves": p["leaves"], "moved": p["moved"],
                                   "moved_by_class": p["moved_by_class"], "moved_incidental": p["moved_incidental"]} for p in det["pairs"]]},
        "cache_equivalence": {"file": "evidence/cache_equivalence_compare.json", "sha256": sha(EV / "cache_equivalence_compare.json"),
                              "pairs": len(cache["pairs"]), "all_scientific_identical": cache["all_scientific_identical"],
                              "measurements": cmeas, "production_block_size": "NOT FROZEN (explicitly deferred)"},
        "evidence_sha256": {f: sha(EV / f) for f in ("phase1_predecessors.json", "equation_audit.json")},
        "production": prod,
        "disclosures": [
            "Panel-ID label repair: the frozen T2 engine emits 'SRpanel:v2:task1r-span-p1-v1:...'; governance canonical is "
            "'SRpanel:v2:task1r-span-p1:...'. The successor emits the canonical form (labels key only the PanelShared cache and "
            "evidence; no scientific quantity depends on them). Predecessor evidence is not rewritten.",
            "Frozen aux4 classifier: its pattern 'run.**' compiles to a regex matching one segment below 'run'. A first cache "
            "comparison with nested counters (run.cache.hits, run.lagrange_factor_stats.*) therefore counted those as SCIENTIFIC "
            "although the 'scientific' subtree was byte-identical (evidence/superseded_nested_counters/). Counters were flattened "
            "to single-segment run.* keys and all runs repeated; the classifier itself is unchanged.",
            "P1 Lagrange factor (014879b): eq channel shifts <= 8e-7 relative (ball midpoint exactly 0); 444/1644 pilot "
            "evaluations use a wider ball than the historical interval series, still rigorous.",
            "Old arb**int raw-shift path would be non-finite on 4 of 29 zero-centred panels; the repeated-multiplication "
            "path (b48973d6) is installed and 0 non-finite drift values occur over 458,850 panel-cell evaluations."],
    }
    out = NS / "config/T2_CLOSURE_RECORD.json"
    out.write_text(json.dumps(rec, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps({"status": rec["status"], "gate": gate, "sha256": sha(out),
                      "negative_record_unchanged": rec["historical_negative_results_preserved"]["T2_NOT_CLOSING_RECORD"]["unchanged"],
                      "production": prod}, indent=1, default=str))


if __name__ == "__main__":
    main()
