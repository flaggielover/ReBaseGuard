"""Kill-micropilot table: predecessor (8b8a242) vs curvature successor (mean-value, N = 1), plus the residual
decomposition of what still binds cell 313. Read-only over committed and kill evidence."""
import json
import re
from fractions import Fraction as Fr
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
OLD = NS.parent / "p5y_k1_sr_o9_t345_successor/evidence"
KILL = NS / "evidence/kill"
num = lambda s: float(re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", s)[0])   # noqa: E731
f = lambda x: float(Fr(x))                                                       # noqa: E731


def iv(r):
    return [f(r["lo"]), f(r["hi"])]


def main():
    ideal = json.loads((NS / "evidence/phase2_decomposition.json").read_text())
    rows, dec = [], {}
    for c in (275, 313, 315, 150):
        o, n = json.loads((OLD / f"t4/t4_c{c}.json").read_text()), json.loads((KILL / f"t4_c{c}.json").read_text())
        t5 = json.loads((KILL / f"t5_c{c}.json").read_text())
        st = {x["identity"]["obligation_id"]: x["status"] for x in t5["obligations"]}
        log = json.loads((KILL / f"run_c{c}.log").read_text())
        for m in ("1", "2", "3", "5"):
            Lo, Ln = o["m"][m], n["m"][m]
            rows.append({"cell": c, "m": int(m), "subdivision_level": 1,
                         "D_interval_old": iv(Lo["D_interval"]), "D_interval_new": iv(Ln["D_interval"]),
                         "M_R2_old": f(Lo["M_R2"]), "M_R2_new": f(Ln["M_R2"]),
                         "B_cover_old": f(Lo["cover"]["usage"]), "B_cover_new": f(Ln["cover"]["usage"]),
                         "ratio_old": Lo["B_cover_ratio"], "ratio_new": Ln["B_cover_ratio"],
                         "idealized_ratio_DIAGNOSTIC": ideal[str(c)]["m"][m]["IDEALIZED_B_cover_ratio_DIAGNOSTIC"],
                         "ledger_old": Lo["status"], "ledger_new": Ln["status"],
                         "target_old": Lo["target_gate"]["status"], "target_new": Ln["target_gate"]["status"],
                         "curvature_obligation_new": st[f"SR:{c}:curvature:{m}"], "assembly_obligation_new": st[f"SR:{c}:assembly:{m}"],
                         "failing_gates_new": sorted(k for k, g in Ln["top_level_gates"].items() if g.get("status") == "FAIL")})
        rows[-1]["_cell_run"] = {"cpu_s": log["cpu_s"], "rss_kib": log["rss_kib"], "t4_sha": log["t4_sha"], "T5": log["T5"]}
        if c == 313:
            for r in range(5):
                s, i = n["refinement"][str(r)]["summary"], n["refinement"][str(r)]["inputs"]
                Cf, k1, k2 = f(i["C"]), f(i["k1"]), f(i["k2"])
                dec[r] = {"eps_H_cell": num(s["eps_H_cell"]), "C*deltaH_cell": Cf * f(i["delta_H_cell"]),
                          "C*k2*eps_F_cell": Cf * k2 * num(s["eps_F_cell"]), "C*2k1*eps_D_cell": Cf * 2 * k1 * num(s["eps_D_cell"]),
                          "C*eps_S2_cell": Cf * f(i["eps_S2_cell"]), "iterations": s["iterations"], "contraction": num(s["contraction"]),
                          "sup_H_hat": f(i["sup_H_hat"]), "sup_H_final": num(s["sup_H"])}
    out = {"schema": "rebaseguard.p5y.k1.sr.o9.curvature-kill-table.v1", "rows": rows, "cell313_H_closure_after_successor": dec,
           "critical": {f"{c}/m{m}": next(r["ratio_new"] for r in rows if r["cell"] == c and r["m"] == m)
                        for c, m in ((313, 2), (313, 5), (315, 2), (275, 2))}}
    (NS / "evidence/kill_table.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    for r in rows:
        print(f"c{r['cell']} m{r['m']}: ratio {r['ratio_old']:.4g} -> {r['ratio_new']:.4g} (ideal {r['idealized_ratio_DIAGNOSTIC']:.3g}) | M_R2 {r['M_R2_old']:.4g} -> {r['M_R2_new']:.4g} |"
              f" |D| {max(map(abs, r['D_interval_new'])):.4g} | curv {r['curvature_obligation_new']} asm {r['assembly_obligation_new']} | target {r['target_old']}->{r['target_new']} | fail {r['failing_gates_new']}")
    print("critical", out["critical"])
    for r, d in dec.items():
        print(f"313 H_{r}: eps_H {d['eps_H_cell']:.4g} = C*dH {d['C*deltaH_cell']:.3g} + C*k2*eF {d['C*k2*eps_F_cell']:.3g} + C*2k1*eD {d['C*2k1*eps_D_cell']:.3g} + C*S2 {d['C*eps_S2_cell']:.3g} | iters {d['iterations']} kappa' {d['contraction']:.3f} supHhat {d['sup_H_hat']:.3g}")


if __name__ == "__main__":
    main()
