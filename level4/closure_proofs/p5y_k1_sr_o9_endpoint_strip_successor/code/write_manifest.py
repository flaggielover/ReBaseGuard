import glob, hashlib, json
from fractions import Fraction as Fr
from pathlib import Path
NS = Path(__file__).resolve().parents[1]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
up = lambda x: float(Fr(x[0]) * Fr(2) ** x[1])
def rowof(f):
    r = json.loads(Path(f).read_text()); s = r["scientific"]; n, o = s["new"]["nodes"], s["old"]["nodes"]
    return {"case": s["case"], "C_upper": s["C_upper"], "n_z": s["new"]["n_z"], "strip_ids": s["new"]["strip_ids"],
            "F0_old_delta_end": up(o["F:0:k0"]["channels"]["end"]), "F0_new_endpoint": up(n["F:0:k0"]["channels"]["end"]),
            "F0_C_new_over_gate": n["F:0:k0"]["end_over_gate"], "worst_F_r_C_new_over_gate": max(v["end_over_gate"] for v in n.values()),
            "F0_new_delta_patch": n["F:0:k0"]["delta_patch"], "F0_old_delta_patch": o["F:0:k0"]["delta_patch"],
            "new_failing_lines": sorted({g for v in n.values() for g, x in v["local_gates"].items() if not x["PASS"]}),
            "old_failing_lines": sorted({g for v in o.values() for g, x in v["local_gates"].items() if not x["PASS"]}),
            "strip_P1_pass": all(v["PASS"] for v in s["new"]["strip_P1"].values()),
            "new_cpu_s": r["timing"]["new_cpu_s"], "peak_rss_kib": r["peak_rss_kib"],
            "scientific_hash": r["scientific_hash"], "file_sha256": sha(f)}
micro = [rowof(f) for f in sorted(glob.glob(str(NS / "evidence/micropilot_*.json")))]
pilot = [rowof(f) for f in sorted(glob.glob(str(NS / "evidence/pilot36/*.json")))]
allrows = micro + pilot
m = {"schema": "rebaseguard.p5y.k1.sr.o9.endpoint-strip-successor.v1",
     "status": "ENDPOINT_STRIP_SUCCESSOR_MICROPILOT_PASS__INT_LINE_OPEN",
     "classification": "ENDPOINT_SUCCESSOR_MICROPILOT_PASS",
     "not_claimed": ["T2 closure", "whole-cell delta_cell", "refinement", "B_cover closure", "obligation closure", "production readiness"],
     "parent": {"t2_not_closing_commit": "29ee382b435afb7eeefbb4e4a465e5c8f383b29d", "tag": "p5y-k1-sr-o9-t2-endpoint-not-closing"},
     "architecture": {"id": "task1r-span-p1+strip-contract-v3",
                      "operator_split": "M(a,b) = core[L_c,U_c] - I_L(b) - I_U(a); strips contracted, not bounded",
                      "strip_ids": "SRstrip:v3:task1r-span-p1+strip-contract-v3:64:{i}:{j}:{L|U}",
                      "strip_error_channel": "end = e1 raised-degree truncation + e2 Taylor-model error + e3 weight remainder",
                      "unchanged": ["theorem target", "1/250 local gate", "B_cover target", "D=11", "Z=20", "256 bits", "degree 16",
                                    "46 candidates / 102 contracts", "core span panelisation task1r-span-p1-v1", "historical sliver method (predecessor)"]},
     "predecessor_defect_superseded": ("committed T2 engine RawShiftDrift used arb ** int: NaN on zero-centred panels (crash only, never a false "
                                       "pass) and radius-inflated elsewhere; replaced here by exact repeated multiplication for BOTH paths"),
     "raw_shift_fix_checks_sha256": sha(NS / "evidence/raw_shift_fix_checks.txt"),
     "strip_validation_sha256": sha(NS / "evidence/strip_validation.json"),
     "int_diagnosis_sha256": sha(NS / "evidence/int_diagnosis.json"),
     "kill_micropilot": micro, "bounded_pilot": pilot,
     "summary": {"runs": len(allrows), "endpoint_gate_pass": sum(1 for x in allrows if x["worst_F_r_C_new_over_gate"] <= 1),
                 "max_endpoint_ratio": max(x["worst_F_r_C_new_over_gate"] for x in allrows),
                 "pilot_all_F_r_k0_gates_pass": sum(1 for x in pilot if not x["new_failing_lines"]),
                 "pilot_old_all_pass": sum(1 for x in pilot if not x["old_failing_lines"]),
                 "pilot_failing_only_int": sum(1 for x in pilot if x["new_failing_lines"] == ["int"]),
                 "max_cpu_s": max(x["new_cpu_s"] for x in allrows), "max_rss_kib": max(x["peak_rss_kib"] for x in allrows)},
     "open_finding_int_line": ("B_int fails on 3/36 pilot cases (cell 0 (51,63), (63,54); cell 150 (51,63)); present identically in the "
                               "predecessor; attributed (diagnostic) to the frozen Task1R softplus Lagrange interval coefficient carried in "
                               "the Taylor coefficients (P1-sized), not to the endpoint method; not closed here"),
     "sources": {p.name: sha(p) for p in sorted((NS / "code").glob("*.py"))}}
(NS / "config/ENDPOINT_STRIP_MANIFEST.json").write_text(json.dumps(m, indent=1, sort_keys=True) + "\n")
print(json.dumps(m["summary"], indent=1))
