"""Record the T2 NOT-CLOSING result as immutable evidence (no science changed)."""
import hashlib
import json
import re
import subprocess
import sys
from fractions import Fraction as Fr
from pathlib import Path

import sr_o9_candidates as T
import sr_o9_equations as EQ
import sr_o9_patch_certifier as PC

NS = Path(__file__).resolve().parents[1]
GOV = T.CP / "p5y_k1_sr_o9_pre_t2_governance_successor"
AMD = T.CP / "p5y_k1_sr_o9_pre_t2_a5_amendment"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()          # noqa: E731


def main():
    T.check_threads()
    env = {"HOME": "/home/ubuntu", "PATH": "/usr/bin:/bin", "LANG": "C.UTF-8", **{v: "1" for v in T.THREAD_VARS}}
    pre = json.loads(subprocess.run([sys.executable, str(GOV / "code/verify_pre_t2.py"), "verify"], env=env,
                                    capture_output=True, text=True).stdout)
    m = EQ.build_map()
    committed_map = json.loads((NS / "config/EQUATION_MAP.json").read_text())
    refA = json.loads((GOV / "config/AUTHORIZED_RUNTIME_REFERENCES.json").read_text())["A"]["authorized_runtime_output"]
    amd = json.loads((AMD / "config/A5_AMENDMENT.json").read_text())["measurement"]
    C_SR = json.loads((T.CP / "p5y_k1_task1r_budget_harness/results/task1r_F0_qualification.json").read_text())["amplification"]["C_at_e"]
    mant, _, _ = T.reference_F0()
    with T.scientific_precision():
        cand = T.to_arb_matrix(mant)
        base = PC.task1r_report(cand, C_SR, "task1r_baseline", {})
        o9 = PC.task1r_report(cand, C_SR, "o9", {})
    c = lambda x: json.dumps(x, sort_keys=True)                            # noqa: E731
    refs = {"A4_components_byte_equal": c(base["components"]) == c(refA["components"]),
            "A4_delta_byte_equal": repr(base["delta_F0"]) == repr(refA["delta_F0"]),
            "A4_per_line_byte_equal": c(base["per_line"]) == c(refA["per_line"]),
            "A5_3_o9_equals_amendment_certificate": all(o9["components"][k] == amd["components"][k]["o9"] for k in o9["components"]),
            "A5_3_o9_exact_gates_all_pass": all(v["PASS"] for v in o9["exact_gates"].values()),
            "delta_baseline": base["delta_F0"], "delta_o9": o9["delta_F0"]}
    built = T.build_cell_candidates(150)["scientific"]
    hashes = {x["node"]: x["identity_hash"] for x in built["candidates"]}
    cell = T.frozen_cell(150)
    with T.scientific_precision():
        cands = {x["node"]: T.to_arb_matrix(x["mantissas"]) for x in built["candidates"]}
        r = PC.certify_patch(17, 11, T.cell_geometry(cell)["e0"], cands, cand_hashes=hashes,
                             C_gate=Fr(cell["C_upper"]), shared_cache={})
    timing = {k: r.pop(k) for k in ("cpu_s", "wall_s")}
    (NS / "evidence/onepatch_cell150_17_11.json").write_bytes(T.canonical(r))
    rows, cur = [], None
    for line in (NS / "evidence/b_end_characterisation.txt").read_text().splitlines():
        mm = re.match(r"cell\s+(\d+) .*C_upper=\s*([\d.]+)", line)
        if mm:
            cur = (int(mm.group(1)), float(mm.group(2)))
            continue
        mm = re.match(r"\s+patch\s+(\d+),\s*(\d+) n_z\s+(\d+)\s+C\*delta_end/\(1/250\) =\s+([\d.]+)\s+all F0 local gates pass=(\w+)\s+dominant=(\w+)\s+delta_patch=([\d.e+-]+)", line)
        if mm and cur:
            rows.append({"cell": cur[0], "C_upper": cur[1], "patch": [int(mm.group(1)), int(mm.group(2))],
                         "n_z": int(mm.group(3)), "C_delta_end_over_gate": float(mm.group(4)),
                         "F0_local_gates_all_pass": mm.group(5) == "True", "dominant": mm.group(6),
                         "delta_patch": float(mm.group(7))})
    fails = sum(1 for x in rows if not x["F0_local_gates_all_pass"])
    rec = {"schema": "rebaseguard.p5y.k1.sr.o9.t2.not-closing-record.v1",
           "status": "T2_EXECUTOR_IMPLEMENTED_ENDPOINT_GATE_NOT_CLOSING",
           "statements": ["generalized SR equation map implemented (45 residual + 18 operator-image nodes)",
                          "46 candidates / 102 contracts preserved (contract set == frozen census)",
                          "authorized-runtime Task1R (A4 byte-equal, A5.3) and O9 (C) references pass",
                          "one-patch full DAG executes (cell 150, patch (17,11): 63 nodes, 102 contracts)",
                          "frozen endpoint-sliver local gate C*delta_end <= 1/250 systematically fails",
                          "T2 scientific closure is NOT achieved",
                          "no whole-cell, refinement, B_cover or obligation closure is claimed"],
           "pre_t2_verifier_all_pass": pre["all_pass"],
           "equation_map_sha256": m["equation_map_sha256"],
           "equation_map_matches_committed": committed_map["equation_map_sha256"] == m["equation_map_sha256"],
           "contract_set_equals_frozen_census": m["contract_set_equals_frozen_census"],
           "references": refs,
           "onepatch": {"file": "evidence/onepatch_cell150_17_11.json", "nodes": len(r["nodes"]),
                        "contracts": len(r["contracts_evaluated"]), "evaluations": r["contract_evaluations"],
                        "all_finite_nonnegative": all(v["finite_nonnegative"] for v in r["nodes"].values()),
                        "F_k0_local_gates_all_pass": {n: v["local_gates_all_pass"] for n, v in r["nodes"].items() if "local_gates" in v},
                        "timing": timing},
           "endpoint_gate_failure_table": rows,
           "endpoint_gate_failures": f"{fails}/{len(rows)} representative (cell, patch) cases fail",
           "characterisation_txt_sha256": sha(NS / "evidence/b_end_characterisation.txt"),
           "parents": {"t1": "ab8d197398dc1d11e7ef983c9d66347080356da1", "pre_t2": "a296244c866368c78750eb5b1800aee8decbd249",
                       "a5_amendment": "44acc65e0fbb78507f90ff047bfff2a6936ddd54"},
           "sources": {p.name: sha(p) for p in sorted((NS / "code").glob("*.py"))}}
    (NS / "config/T2_NOT_CLOSING_RECORD.json").write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: rec[k] for k in ("status", "pre_t2_verifier_all_pass", "equation_map_matches_committed",
                                          "references", "endpoint_gate_failures")}, indent=1))
    print(json.dumps(rec["onepatch"], indent=0)[:900])


if __name__ == "__main__":
    main()
