"""Predecessor rigor check (read-only). The frozen SR-lane sr_operators.one_step_norms bounds ||K_z''|| by
int|w|phi + |e| k2 + int w^2 phi, justified by the pointwise-FALSE |w||w^2-1| <= |w| + w^2 (fails for |w| > 1.62).
The value is still a valid certificate input if it is >= a rigorous bound on the actual window:
    ||K_z''_e|| <= int_W |w||w^2-1| phi(w) dw + max|e| * int_W |w^2-1| phi(w) dw,   W = [-c_SR+e_lo, c_SR+e_hi]
(|z| = |w - e| <= |w| + |e|), evaluated in closed form (antiderivative -(w^2+1)phi, sign changes at -1, 0, 1).
Checked at the midpoint (point e0) and at the cell ball, as t4_cell used them for the committed cells."""
import json
import sys
from pathlib import Path

import sr_o9_candidates as T
import sr_o9_patch_certifier as PC
import curv_mv as M
from flint import arb

sys.path.insert(0, str(T.CP / "p5y_k1_sr_qualification/code"))
import sr_operators as OPS                                        # noqa: E402

NS = Path(__file__).resolve().parents[1]


def w_He2(a, b):
    a, b = arb(a.lower()), arb(b.upper())
    pts = [a] + [r for r in (arb(-1), arb(0), arb(1)) if a.upper() < r.lower() and r.upper() < b.lower()] + [b]
    G = lambda w: -(w * w + arb(1)) * M.phi(w)                      # noqa: E731
    return sum(((G(h) - G(l)).abs_upper() for l, h in zip(pts[:-1], pts[1:])), arb(0))


def main():
    rows = []
    with T.scientific_precision():
        _A, _b, c = PC.L.sr_constants()
        for cell in (0, 150, 250, 275, 313, 315):
            g = T.cell_geometry(T.frozen_cell(cell))
            for mode in ("mid", "cell"):
                lo, hi = (g["e0"], g["e0"]) if mode == "mid" else (g["left"], g["right"])
                e = g["e0"] if mode == "mid" else g["e0"] + arb(0, g["rho"].abs_upper())
                a, b = -c + lo, c + hi
                E = arb(max(lo.abs_upper(), hi.abs_upper()).upper())
                rig = w_He2(a, b) + E * M.A(2, a, b)
                used = OPS.one_step_norms(e)["kz2"].abs_upper()
                rows.append({"cell": cell, "mode": mode, "sr_operators_kz2_used": float(used), "rigorous_bound": float(rig),
                             "used_is_valid_upper_bound": bool(used.lower() >= rig.upper()),
                             "slack_ratio": float(used / rig)})
    out = {"schema": "rebaseguard.p5y.k1.sr.o9.kz2-predecessor-check.v1", "rows": rows,
           "all_valid": all(r["used_is_valid_upper_bound"] for r in rows)}
    (NS / "evidence/kz2_predecessor_check.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"all_valid": out["all_valid"]}))
    for r in rows:
        print(r["cell"], r["mode"], "used %.5g rigorous %.5g valid %s ratio %.3f" % (r["sr_operators_kz2_used"], r["rigorous_bound"], r["used_is_valid_upper_bound"], r["slack_ratio"]))


if __name__ == "__main__":
    main()
