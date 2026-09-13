"""Apply the PREDECLARED decision rules to the cross-host replay outputs. Result-agnostic w.r.t. science:
it compares bits and measures cost; it never reads or computes a T3/T4/T5 status or B_cover ratio.

  python analyze_crosshost.py PREDECLARATION.json OUT.json replay_R1.json replay_R2.json [replay_R3.json ...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    pre = json.loads(Path(sys.argv[1]).read_text())
    out = Path(sys.argv[2])
    reps = [json.loads(Path(p).read_text()) for p in sys.argv[3:]]
    rules = pre["decision_rules"]
    contract_reps = [r for r in reps if r["label"] in pre["replicates"]["contract_conformant"]]
    diag_reps = [r for r in reps if r["label"] not in pre["replicates"]["contract_conformant"]]

    def rowmap(r):
        return {(x["cell"], tuple(x["patch"])): x for x in r["rows"]}

    maps = [rowmap(r) for r in contract_reps]
    keys = sorted(set().union(*maps)) if maps else []
    fresh_process_identical = all(len({m[k]["leaf_sha256"] for m in maps if k in m}) == 1 and all(k in m for m in maps)
                                  for k in keys)
    cross_host_identical = all(m[k]["bit_identical_to_committed_aws"] for m in maps for k in m)
    diag = {r["label"]: {"all_bit_identical_to_aws": r["all_bit_identical"],
                         "OPENBLAS_CORETYPE": r["runtime"]["diagnostic"].get("OPENBLAS_CORETYPE")} for r in diag_reps}
    # cost: per-patch Vultr CPU vs the committed AWS CPU of the SAME cold-cache pairs
    ratios, v_cpu, a_cpu = [], 0.0, 0.0
    for m in maps:
        for k, x in m.items():
            v_cpu += x["cpu_s"]
            a_cpu += x["aws_cpu_s"]
            ratios.append(x["cpu_s"] / x["aws_cpu_s"])
    ratio = v_cpu / a_cpu if a_cpu else None
    ratios.sort()
    basis = pre["projection_basis_cpu_h"]
    proj = {k: {"aws_basis_cpu_h": v, "vultr_equivalent_cpu_h": round(v * ratio, 1),
                "vultr_equivalent_cpu_h_p90_ratio": round(v * ratios[int(0.9 * (len(ratios) - 1))], 1)}
            for k, v in basis.items()} if ratio else {}
    runtime_hashes = sorted({r["runtime"]["sha256"] for r in contract_reps})
    verdict = {
        "SR_DETERMINISM_FRESH_PROCESS": "PASS" if fresh_process_identical and len(contract_reps) >= 2 else "FAIL",
        "SR_CROSS_HOST_BIT_IDENTITY_VS_COMMITTED_AWS": "PASS" if cross_host_identical else "FAIL",
        "RUNTIME_CONTRACT_HASH_EQUALS_AWS": runtime_hashes == [rules["aws_runtime_contract_hash"]],
    }
    verdict["VULTR_PS1_PRODUCER_QUALIFICATION_EVIDENCE"] = (
        "PASS_NON_DISPOSITION_BEARING" if all(v in ("PASS", True) for v in verdict.values()) else "FAIL")
    res = {"schema": "rebaseguard.p5y.k1.sr.ps1.vultr-crosshost-analysis.v1", "result_bearing": False,
           "disposition_bearing": False, "predeclaration": pre["predeclaration_sha256_note"],
           "replicates": [r["label"] for r in reps], "pairs": len(keys), "verdict": verdict,
           "diagnostic_replicates": diag, "runtime_hashes": runtime_hashes,
           "cost": {"vultr_cpu_s_sum": v_cpu, "aws_cpu_s_sum_same_pairs": a_cpu, "vultr_over_aws_cpu_ratio": ratio,
                    "per_pair_ratio_min_p50_p90_max": [ratios[0], ratios[len(ratios) // 2],
                                                       ratios[int(0.9 * (len(ratios) - 1))], ratios[-1]] if ratios else None,
                    "peak_rss_kib_max": max(r["peak_rss_kib"] for r in reps),
                    "process_cpu_s": {r["label"]: r["process_cpu_s"] for r in reps},
                    "process_wall_s": {r["label"]: r["process_wall_s"] for r in reps},
                    "projection": proj}}
    out.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"verdict": verdict, "ratio": ratio, "projection": proj}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
