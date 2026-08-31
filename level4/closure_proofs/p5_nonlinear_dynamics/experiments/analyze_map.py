#!/usr/bin/env python3
"""E1-analysis: the fixed function R, the secant gain s, and the skeleton.

Produces ``results/map_analysis.json``:
  * R'(0) from the map grid vs the frozen P3 ``1 - GammaTilde``;
  * the secant gain  s(e) = -R(e)/e  and its monotonicity audit;
  * the symmetric period-2 branch  e*(rho)  solving  s(e*) = 1/rho;
  * the 2-cycle multiplier  rho^2 R'(e*)^2  and its stability verdict;
  * the noise floor sqrt(V(e*)) and the skeleton signal-to-noise ratio.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rebaseguard_p5 import P3, RESULTS                            # noqa: E402

RHO_OUT = (0.05, 0.0608, 0.067, 0.0815, 0.0913, 0.0995, 0.1084, 0.15, 0.2,
           0.35, 0.45, 0.55, 0.65,
           0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0)


def p3_boundaries() -> dict:
    t = json.loads((P3 / "results" / "boundary_table.json").read_text())
    return {(r["detector_short"].lower(), int(r["m"])): r for r in t["rows"]
            if r["layer"].startswith("GAUSSIAN")}


def series(rows, det, m):
    sel = [r for r in rows if r["detector"] == det]
    e = np.array([r["e"] for r in sel])
    o = np.argsort(e)
    e = e[o]
    R = np.array([[q["R"] for q in r["per_m"] if q["m"] == m][0] for r in sel])[o]
    Rse = np.array([[q["R_se"] for q in r["per_m"] if q["m"] == m][0]
                    for r in sel])[o]
    S = np.array([[q["S"] for q in r["per_m"] if q["m"] == m][0] for r in sel])[o]
    A = np.array([r["tau_mean"] for r in sel])[o]
    return e, R, Rse, S, A


def interp(x, xs, ys):
    return float(np.interp(x, xs, ys))


def main(src="nonlinear_map.json", out="map_analysis.json"):
    d = json.loads((RESULTS / src).read_text())
    bnd = p3_boundaries()
    cells = []
    for det in ("cusum", "sr"):
        for m in d["m_grid"]:
            e, R, Rse, S, A = series(d["rows"], det, m)
            pos = e > 0
            ep, Rp, Sp = e[pos], R[pos], S[pos]
            sp = -Rp / ep                             # secant gain on e>0
            # slope at 0 from the two innermost symmetric pairs
            small = np.argsort(np.abs(e))[:5]
            sl = np.polyfit(e[small], R[small], 1)[0]
            g3 = bnd[(det, m)]["gamma_tilde"]
            rc = bnd[(det, m)]["rho_crit"]
            # oddness residual
            odd = float(np.max(np.abs(R + R[::-1])))
            odd_se = float(np.max(Rse))
            # monotonicity of s on e>0
            dif = np.diff(sp)
            viol = [{"e_lo": float(ep[i]), "e_hi": float(ep[i + 1]),
                     "s_lo": float(sp[i]), "s_hi": float(sp[i + 1])}
                    for i in np.flatnonzero(dif > 0)]
            # period-2 branch: s(e*) = 1/rho, s decreasing -> invert
            xs, ys = sp[::-1], ep[::-1]               # s increasing order
            branch = []
            rho_list = sorted(set(RHO_OUT) | {round(float(rc), 10)})
            for rho in rho_list:
                target = 1.0 / rho
                if target > sp[0] or target < sp[-1]:
                    branch.append({"rho": rho, "exists": False})
                    continue
                estar = interp(target, xs, ys)
                # R' at e* by central difference on the measured grid
                k = int(np.searchsorted(ep, estar))
                k = min(max(k, 1), len(ep) - 2)
                dR = (Rp[k + 1] - Rp[k - 1]) / (ep[k + 1] - ep[k - 1])
                mult = rho * rho * dR * dR
                Sst = interp(estar, ep, Sp)
                V = rho * rho * Sst + (1 - rho) ** 2 / m
                branch.append({
                    "rho": rho, "exists": True, "e_star": estar,
                    "R_prime_at_estar": float(dR),
                    "cycle2_multiplier": float(mult),
                    "cycle2_stable": bool(mult < 1.0),
                    "S_at_estar": Sst, "noise_sd": float(np.sqrt(V)),
                    "snr": float(estar / np.sqrt(V))})
            cells.append({
                "detector": det, "m": int(m),
                "R_prime_0_measured": float(sl),
                "p3_one_minus_gamma": float(1.0 - g3),
                "rel_err_vs_p3": float(abs(sl - (1 - g3)) / abs(1 - g3)),
                "p3_rho_crit": float(rc),
                "rho_crit_from_map": float(1.0 / abs(sl)),
                "s_at_0plus": float(sp[0]), "e_at_s0plus": float(ep[0]),
                "s_max_e": float(sp[-1]), "max_e": float(ep[-1]),
                "sup_abs_R": float(np.max(np.abs(R))),
                "argmax_abs_R": float(e[int(np.argmax(np.abs(R)))]),
                "oddness_max_resid": odd, "oddness_max_se": odd_se,
                "s_monotone_decreasing": len(viol) == 0,
                "s_monotonicity_violations": viol,
                "A_max": float(np.max(A)), "A_at_0": float(A[e == 0][0]),
                "S_at_0": float(S[e == 0][0]),
                "branch": branch})
    (RESULTS / out).write_text(json.dumps({"cells": cells}, indent=1))
    for c in cells:
        b1 = [x for x in c["branch"] if x["rho"] == 1.0][0]
        print(f"{c['detector']:5s} m={c['m']}  R'(0)={c['R_prime_0_measured']:+8.3f}"
              f"  P3 1-G={c['p3_one_minus_gamma']:+8.3f}"
              f"  rel={c['rel_err_vs_p3']:.4f}"
              f"  sup|R|={c['sup_abs_R']:.3f}@{c['argmax_abs_R']:+.2f}"
              f"  odd={c['oddness_max_resid']:.4f}(se{c['oddness_max_se']:.4f})"
              f"  s_dec={c['s_monotone_decreasing']}"
              f"  e*(1)={b1.get('e_star', float('nan')):.3f}"
              f"  mult={b1.get('cycle2_multiplier', float('nan')):.3f}"
              f"  snr={b1.get('snr', float('nan')):.2f}")
    print("wrote", RESULTS / out)


if __name__ == "__main__":
    main(*sys.argv[1:])
