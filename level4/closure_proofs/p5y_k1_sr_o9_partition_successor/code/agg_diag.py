"""Aggregate the Phase 3/4 child diagnostics (NON-CERTIFYING) into rho-scaling and worst-child tables."""
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
MS = ("1", "2", "3", "5")


def main():
    recs = [json.loads(p.read_text()) for p in sorted((NS / "evidence/diag").glob("N*_k*.json"))]
    out = {"schema": "rebaseguard.p5y.k1.sr.o9.partition-diag-aggregate.v1", "DIAGNOSTIC_ONLY": True, "by_N": {}}
    for Nc in sorted({r["N"] for r in recs}):
        rs = sorted([r for r in recs if r["N"] == Nc], key=lambda r: r["k"])
        assert [r["k"] for r in rs] == list(range(Nc)), (Nc, [r["k"] for r in rs])
        row = {"children": Nc, "child_rho": rs[0]["rho"], "variants": {}}
        for var in ("B_certified", "A_oracle"):
            worst = {}
            for m in MS:
                w = max(rs, key=lambda r: r["variants"][var]["ratio"][m])
                v = w["variants"][var]
                worst[m] = {"worst_child_k": w["k"], "worst_child_e0": w["e0_float"], "ratio": v["ratio"][m],
                            "M_R2": v["M_R2"][m], "D_mag": v["D_mag"][m], "cover_children": v["cover_children"][m],
                            "max_contraction": v["max_contraction"],
                            "F4_derivative_C2k1nD": v["refinement"]["4"]["C_2k1_nD_derivative"],
                            "F4_source_CS2": v["refinement"]["4"]["C_S2_source"],
                            "F4_meanvalue_CdeltaH": v["refinement"]["4"]["C_deltaH"],
                            "F4_eps_H_cell": v["refinement"]["4"]["eps_H_cell"],
                            "best_child_ratio": min(r["variants"][var]["ratio"][m] for r in rs)}
            row["variants"][var] = {"worst": worst, "all_children_pass": all(r["variants"][var]["ratio"][m] < 1 for r in rs for m in MS),
                                    "worst_ratio_m235": max(worst[m]["ratio"] for m in ("2", "3", "5"))}
        row["ideal_true_worst"] = {m: max(r["ideal_true"][m]["ratio_center"] for r in rs) for m in MS}
        out["by_N"][str(Nc)] = row
    (NS / "evidence/phase34_diag_aggregate.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    for Nc, row in out["by_N"].items():
        b, a = row["variants"]["B_certified"], row["variants"]["A_oracle"]
        print(f"N={Nc:>2} rho={row['child_rho']:.5f} | B worst " + " ".join(f"m{m}={b['worst'][m]['ratio']:.4g}(k{b['worst'][m]['worst_child_k']})" for m in MS)
              + f" q={b['worst']['5']['max_contraction']:.3f} M_R2m5={b['worst']['5']['M_R2']:.4g} deriv={b['worst']['5']['F4_derivative_C2k1nD']:.3g} src={b['worst']['5']['F4_source_CS2']:.3g}"
              + f" | A worst " + " ".join(f"m{m}={a['worst'][m]['ratio']:.4g}" for m in MS) + f" | ideal m5 {row['ideal_true_worst']['5']:.3g}")


if __name__ == "__main__":
    main()
