"""Stream A0 task C1 aggregation: results/*.json (batch 1) -> results/A0_C1_TABLE.json.

Per declared drift: the NON-CERTIFIED reference estimate Lambda_ref (Richardson O(h^2) extrapolation of the pinned
C2b Nystrom values Lambda_h at the two finest meshes; the three-mesh ratio checks the O(h^2) assumption) and the MC
mean +- se; per rung: U, L (exact and float), slack U / Lambda_ref - 1, L / Lambda_ref - 1, bracket U / L - 1 and CPU.
Also the best certified bracket over all rungs of both certifiers (min U, max L) and the cross-certifier consistency
check max L <= min U (exact).  Reads only this stream's own files.
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a0_common as A  # noqa: E402


def load_all():
    out = {}
    for p in sorted(A.RESULTS.glob("*.json")):
        if p.name.startswith(("C2B_e", "C1B_e", "C1BX_e", "MC_e", "C2BX_e", "C1BH_e")) and "_det" not in p.name:
            out[p.name] = json.loads(p.read_text())
    return out


def main():
    R = load_all()
    table = {"schema": "A0_C1_TABLE/1", "latent_proxy": "validation-drift values; stream-internal only (T1/T2)",
             "drifts": {}}
    for e in A.DECLARED_DRIFTS:
        te = A.tag(F(e))
        c2 = sorted((r for n, r in R.items() if n.startswith(f"C2B_e{te}_N")), key=lambda r: r["N"])
        c1 = sorted((r for n, r in R.items() if n.startswith(f"C1B_e{te}_d")), key=lambda r: r["degree"])
        c2x = sorted((r for n, r in R.items() if n.startswith(f"C2BX_e{te}_N")), key=lambda r: r["N"])
        c1h = sorted((r for n, r in R.items() if n.startswith(f"C1BH_e{te}_d")), key=lambda r: r["degree"])
        mc = R.get(f"MC_e{te}.json")
        nys = {r["N"]: r["super"]["nystrom_Lambda_h_NONCERTIFIED"] for r in c2}
        nys.update({r["N"]: r["rung"]["nystrom_Lambda_h_NONCERTIFIED"] for r in c2x if r["N"] not in nys})
        Ns = sorted(nys)
        ref, conv = None, None
        if len(Ns) >= 2:
            n0, n1 = Ns[-2], Ns[-1]
            q = (n1 / n0) ** 2
            ref = (q * nys[n1] - nys[n0]) / (q - 1)
        if len(Ns) >= 3:
            n0, n1, n2 = Ns[-3], Ns[-2], Ns[-1]
            d1, d2 = nys[n1] - nys[n0], nys[n2] - nys[n1]
            conv = d1 / d2 if d2 else None                       # = 4 for clean O(h^2) with mesh doubling
        rows = []
        for r in c2:
            s, b = r["super"], r.get("sub", {})
            rows.append({"certifier": "C2B_P1", "rung": f"N={r['N']}", "U": s.get("U"), "L": b.get("L"),
                         "U_float": s.get("U_float"), "L_float": b.get("L_float"),
                         "status_U": s["status"], "status_L": b.get("status"),
                         "cpu_U": s.get("cpu_seconds"), "cpu_L": b.get("cpu_seconds"),
                         "cpu_proposal": (s.get("cpu_seconds_pipeline") or {}).get("proposal"),
                         "alpha": s.get("alpha"), "beta": s.get("beta"), "bumps": s.get("bumps"),
                         "one_minus_c": b.get("one_minus_c_float"), "nystrom_h": s.get("nystrom_Lambda_h_NONCERTIFIED")})
        for r in c2x:
            x = r["rung"]
            rows.append({"certifier": "C2B_P1_EXACT_SCALE", "rung": f"N={r['N']}", "U": x.get("U"), "L": x.get("L"),
                         "U_float": x.get("U_float"), "L_float": x.get("L_float"), "status_U": x["status_U"],
                         "status_L": x["status_L"], "cpu_U": x["cpu_seconds"]["total"], "cpu_L": 0.0,
                         "cpu_breakdown": x["cpu_seconds"], "alpha_up_minus_1": x.get("alpha_up_minus_1"),
                         "one_minus_c": x.get("one_minus_c_lo"), "nystrom_h": x.get("nystrom_Lambda_h_NONCERTIFIED")})
        for r in c1h:
            s = r["super"]
            rows.append({"certifier": "C1B_PW_HULL", "rung": f"d={r['degree']}", "U": s.get("U"), "L": s.get("L"),
                         "U_float": s.get("U_float"), "L_float": s.get("L_float"), "status_U": s["status"],
                         "status_L": s["status"], "cpu_U": s.get("cpu_seconds"), "cpu_L": 0.0,
                         "eta_W": s.get("eta_W_float"), "hull": s.get("hull")})
        lad = A.RESULTS / f"LADDER_e{te}_detA.json"
        if lad.exists():
            L_ = json.loads(lad.read_text())
            for r in L_["rungs"]:
                rows.append({"certifier": r["certifier"] + " [ladder run detA]", "rung": r["rung"], "U": r.get("U"),
                             "L": r.get("L"), "U_float": float(F(r["U"])) if r.get("U") else None,
                             "L_float": float(F(r["L"])) if r.get("L") else None, "status_U": r.get("status_U"),
                             "status_L": r.get("status_L"), "cpu_U": r.get("cpu"), "cpu_L": 0.0})
        for r in c1:
            s = r["super"]
            rows.append({"certifier": "C1B_PW", "rung": f"d={r['degree']}", "U": s.get("U"), "L": s.get("L"),
                         "U_float": s.get("U_float"), "L_float": s.get("L_float"), "status_U": s["status"],
                         "status_L": s["status"], "cpu_U": s.get("cpu_seconds"), "cpu_L": 0.0,
                         "eta_W": s.get("eta_W_float")})
        for row in rows:
            if ref and row["U_float"]:
                row["slack_U_vs_ref"] = row["U_float"] / ref - 1
            if ref and row["L_float"]:
                row["slack_L_vs_ref"] = row["L_float"] / ref - 1
            if row["U"] and row["L"]:
                row["bracket_U_over_L_minus_1"] = float(F(row["U"]) / F(row["L"]) - 1)
        Us = [F(r["U"]) for r in rows if r["U"] and r["status_U"] == "CERTIFIED"]
        Ls = [F(r["L"]) for r in rows if r["L"] and r["status_L"] == "CERTIFIED"]
        best = {}
        if Us and Ls:
            u, lo = min(Us), max(Ls)
            best = {"U_min": A.fs(u), "L_max": A.fs(lo), "U_min_float": float(u), "L_max_float": float(lo),
                    "bracket_minus_1": float(u / lo - 1), "consistent_L_le_U": lo <= u,
                    "slack_Umin_vs_ref": (float(u) / ref - 1) if ref else None}
        table["drifts"][e] = {"Lambda_ref_NONCERTIFIED": ref, "nystrom_by_N": nys, "richardson_ratio_d1_over_d2": conv,
                              "mc": ({k: mc[k] for k in ("mean", "se", "n_runs", "seed")} if mc else None),
                              "mc_z_vs_ref": ((mc["mean"] - ref) / mc["se"]) if (mc and ref) else None,
                              "rungs": rows, "best_certified": best}
    xs = {n: {k: r[k] for k in ("drift", "degree", "exact_equality", "PASS")} for n, r in R.items() if n.startswith("C1BX")}
    table["c1b_w_only_vs_pinned_certify_degree"] = xs
    A.write_json(A.RESULTS / "A0_C1_TABLE.json", table)
    print(json.dumps({e: {"ref": v["Lambda_ref_NONCERTIFIED"], "best": v["best_certified"].get("bracket_minus_1")}
                      for e, v in table["drifts"].items()}, indent=1))


if __name__ == "__main__":
    main()


def markdown(path=None):
    """Compact markdown tables (floats rounded for reading; exact values are in A0_C1_TABLE.json)."""
    t = json.loads((A.RESULTS / "A0_C1_TABLE.json").read_text())
    out = ["# A0_C1_TABLES — generated by a0_report.py from results/A0_C1_TABLE.json (validation drifts only)", "",
           "> Latent-proxy notice: validation-drift values only; stream-internal (T1/T2). slack = bound / Lambda_ref - 1;",
           "> Lambda_ref is NON-CERTIFIED (Richardson of the pinned Nystrom values at the two finest meshes).", ""]
    for e, v in t["drifts"].items():
        mc = v["mc"]
        out.append(f"## e = {e}")
        out.append("")
        out.append(f"Lambda_ref = {v['Lambda_ref_NONCERTIFIED']:.9f} (Richardson ratio d1/d2 = "
                   f"{v['richardson_ratio_d1_over_d2']:.4f}; 4 = clean O(h^2)); MC {mc['mean']:.5f} +- {mc['se']:.5f} "
                   f"(n = {mc['n_runs']}, seed {mc['seed']}; z = {v['mc_z_vs_ref']:+.2f})" if mc else
                   f"Lambda_ref = {v['Lambda_ref_NONCERTIFIED']}")
        out.append("")
        out.append("| certifier | rung | status U / L | U slack | L slack | U/L - 1 | CPU s (U / L) |")
        out.append("|---|---|---|---|---|---|---|")
        for r in v["rungs"]:
            def f(x):
                return "—" if x is None else f"{x:+.2e}"
            out.append(f"| {r['certifier']} | {r['rung']} | {r.get('status_U')} / {r.get('status_L')} | "
                       f"{f(r.get('slack_U_vs_ref'))} | {f(r.get('slack_L_vs_ref'))} | "
                       f"{'—' if r.get('bracket_U_over_L_minus_1') is None else format(r['bracket_U_over_L_minus_1'], '.2e')} | "
                       f"{r.get('cpu_U')} / {r.get('cpu_L')} |")
        b = v["best_certified"]
        if b:
            out.append("")
            out.append(f"Best certified bracket (min U, max L over all certified rungs): U/L - 1 = {b['bracket_minus_1']:.2e}, "
                       f"U slack {b['slack_Umin_vs_ref']:+.2e}, consistent (L <= U, exact): {b['consistent_L_le_U']}.")
        out.append("")
    (path or (A.HERE / "A0_C1_TABLES.md")).write_text("\n".join(out) + "\n")


if __name__ == "__main__" and "--md" in sys.argv:
    markdown()
