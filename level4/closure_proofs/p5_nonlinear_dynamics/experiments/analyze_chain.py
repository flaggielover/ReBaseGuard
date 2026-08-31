#!/usr/bin/env python3
"""E2-analysis: dispersion law, T11 cross-check, ergodicity and boundary test."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rebaseguard_p5 import RESULTS                                # noqa: E402

Z = 1.959963984540054


def build_s_and_R(det, m):
    """Symmetrised PCHIP interpolant of R from both seed families + tail."""
    acc = {}
    for f in ("nonlinear_map.json", "nonlinear_map_rep.json", "map_tail.json"):
        d = json.loads((RESULTS / f).read_text())
        for r in d["rows"]:
            if r["detector"] != det:
                continue
            q = [q for q in r["per_m"] if q["m"] == m][0]
            acc.setdefault(round(r["e"], 6), []).append((q["R"], q["R_se"]))
    xs = np.array(sorted(acc))
    rs = np.array([float(np.average([v[0] for v in acc[x]],
                                    weights=[1 / v[1] ** 2 for v in acc[x]]))
                   for x in xs])
    rs = 0.5 * (rs - rs[::-1])                       # impose exact T3 oddness
    xs = np.concatenate([[-64.0], xs, [64.0]])
    rs = np.concatenate([[0.0], rs, [0.0]])
    f = PchipInterpolator(xs, rs, extrapolate=False)
    return lambda x: np.nan_to_num(f(np.clip(x, -64.0, 64.0)))


def main():
    ch = json.loads((RESULTS / "chain_sweep.json").read_text())
    samp = np.load(RESULTS / "chain_samples.npz")
    Rf = {}
    out = []
    for c in ch["cells"]:
        det, m, rho = c["detector"], c["m"], c["rho"]
        if (det, m) not in Rf:
            Rf[(det, m)] = build_s_and_R(det, m)
        a = c["all"]
        row = {k: c[k] for k in ("detector", "m", "rho", "rho_over_rhoc",
                                 "rho_crit")}
        for k in ("rms", "mad", "q90", "q95", "q99", "p_gt_1", "p_gt_2",
                  "p_gt_3", "acf1", "alt_rate", "arl", "iact", "kurt", "mean"):
            row[k] = a[k]
            row[k + "_se"] = a[k + "_se"]
        # initial-condition independence: max |group mean - pooled| / pooled se
        gz = {}
        for key in ("rms", "acf1", "arl"):
            gs = [c[f"e0_{v:+.0f}"][key] for v in ch["e0_groups"]]
            ses = [c[f"e0_{v:+.0f}"][key + "_se"] for v in ch["e0_groups"]]
            zz = max(abs(gs[i] - gs[j]) / np.hypot(ses[i], ses[j])
                     for i in range(3) for j in range(i + 1, 3))
            gz[key] = float(zz)
        row["init_dependence_z"] = gz
        out.append(row)

    # ---- T11: ACF1 predicted from the MAP, measured on the CHAIN ----------
    t11 = []
    for key in samp.files:
        det, mm, rr = key.split("_")
        m = int(mm[1:]); rho = float(rr[3:])
        e = samp[key]
        R = Rf[(det, m)]
        pred = rho * float(np.mean(e * R(e)) / np.mean(e ** 2))
        cell = [c for c in ch["cells"] if c["detector"] == det
                and c["m"] == m and abs(c["rho"] - rho) < 1e-9][0]
        meas = cell["all"]["acf1"]; se = cell["all"]["acf1_se"]
        sbar = -pred / rho if rho > 0 else float("nan")
        t11.append({"detector": det, "m": m, "rho": rho,
                    "acf1_measured": meas, "acf1_se": se,
                    "acf1_predicted_from_map": pred,
                    "abs_gap": abs(pred - meas),
                    "gap_in_se": abs(pred - meas) / se if se > 0 else 0.0,
                    "Gamma_eff": 1.0 + sbar,
                    "gamma_tilde_tangent": 1.0 - float(R(1e-9) / 1e-9)})

    # ---- boundary test: is there a feature at rho = rho_c? ---------------
    bnd = []
    for det in ("cusum", "sr"):
        for m in (1, 2, 3, 5):
            rows = sorted([r for r in out if r["detector"] == det
                           and r["m"] == m], key=lambda r: r["rho"])
            x = np.array([r["rho"] for r in rows])
            for metric in ("rms", "q95", "p_gt_2", "acf1", "arl"):
                y = np.array([r[metric] for r in rows])
                se = np.array([r[metric + "_se"] for r in rows])
                rc = rows[0]["rho_crit"]
                k = int(np.argmin(np.abs(x - rc)))
                if 1 <= k < len(x) - 1:
                    # local second difference in units of its own standard error
                    d2 = y[k + 1] - 2 * y[k] + y[k - 1]
                    sd2 = np.sqrt(se[k + 1] ** 2 + 4 * se[k] ** 2 + se[k - 1] ** 2)
                    # compare with the largest |second difference| elsewhere
                    all_d2 = np.abs(y[2:] - 2 * y[1:-1] + y[:-2])
                    bnd.append({"detector": det, "m": m, "metric": metric,
                                "rho_c": rc, "rho_at_k": float(x[k]),
                                "d2_at_rhoc": float(d2),
                                "d2_at_rhoc_in_se": float(abs(d2) / sd2),
                                "rank_of_|d2|_at_rhoc":
                                    int(1 + (all_d2 > abs(d2)).sum()),
                                "n_interior_points": int(all_d2.size)})
    res = {"cells": out, "t11": t11, "boundary_probe": bnd}
    (RESULTS / "chain_analysis.json").write_text(json.dumps(res, indent=1))

    print("== T11: ACF1 predicted from the map vs measured on the chain ==")
    for t in sorted(t11, key=lambda t: (t["detector"], t["m"], t["rho"])):
        print(f"{t['detector']:5s} m={t['m']} rho={t['rho']:.2f} "
              f"meas={t['acf1_measured']:+.4f}+/-{Z*t['acf1_se']:.4f} "
              f"pred={t['acf1_predicted_from_map']:+.4f} "
              f"gap={t['abs_gap']:.4f} ({t['gap_in_se']:.1f} se) "
              f"Gamma_eff={t['Gamma_eff']:.3f} vs tangent {t['gamma_tilde_tangent']:.2f}")
    print("\n== dispersion vs rho (cusum m=1) ==")
    for r in sorted([r for r in out if r["detector"] == "cusum" and r["m"] == 1],
                    key=lambda r: r["rho"]):
        print(f"rho={r['rho']:.4f} (x{r['rho_over_rhoc']:5.1f} rho_c) "
              f"rms={r['rms']:.4f}+/-{Z*r['rms_se']:.4f} q95={r['q95']:.3f} "
              f"P(|e|>2)={r['p_gt_2']:.4f} acf1={r['acf1']:+.4f} "
              f"alt={r['alt_rate']:.4f} arl={r['arl']:7.2f} iact={r['iact']:.2f} "
              f"kurt={r['kurt']:.2f} initz={max(r['init_dependence_z'].values()):.2f}")
    print("\n== boundary probe: |2nd difference| at rho_c, ranked among all ==")
    worst = sorted(bnd, key=lambda b: b["rank_of_|d2|_at_rhoc"])[:6]
    for b in worst:
        print(f"{b['detector']:5s} m={b['m']} {b['metric']:7s} "
              f"rank {b['rank_of_|d2|_at_rhoc']}/{b['n_interior_points']} "
              f"({b['d2_at_rhoc_in_se']:.1f} se)")
    nsig = sum(1 for b in bnd if b["rank_of_|d2|_at_rhoc"] == 1)
    print(f"metrics where rho_c is the single largest curvature point: "
          f"{nsig}/{len(bnd)}")
    print("wrote chain_analysis.json")


if __name__ == "__main__":
    main()
