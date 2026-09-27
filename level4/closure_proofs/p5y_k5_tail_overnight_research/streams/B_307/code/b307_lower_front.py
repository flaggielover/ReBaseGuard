"""Safe historical cases: the 34 committed lower-front theorem-TC cells (CUSUM cells 11-44, every m, every r).

These cells carry REAL order-3 data (delta_G, abs_G_at_a, sup G) from the adopted lower-front campaign.  This
script (a) independently re-implements the theorem-TC arithmetic (b307_lib; no tc_rule import) and must reproduce
every committed TC_CONSUMPTION.tc_audit H_TC interval EXACTLY (gate, with a planted-perturbation negative control);
(b) recomputes, from the SAME committed fields, the TC-T zero-candidate surrogate
    f_G^surr = 3 k1 s_H + 3 k2 s_D + k3 s_F + sigma3 + eps_src[3]
with sigma3 from the frozen pure J/h tower (the Aux3 order-3 source suprema of (P3') are NOT in these cell files,
so the (P3') refinement cannot be applied here; the pure tower is a valid but possibly looser sigma3);
(c) compares the real-G contributions with the surrogate: alpha, beta, the A0-level order-3/4 group Q, per-object
half-widths and the m-enclosure widths.  No transfer of any of these ratios to any other cell is made.
Writes NS/validation/B307_LOWER_FRONT_ORDER3.json.  Class NONTARGET_REAL_VALIDATION.
"""
from __future__ import annotations

import json
import sys
import time
from fractions import Fraction as F
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import b307_lib as L  # noqa: E402
from b307_lib import Q, NS  # noqa: E402

Q.install_import_guard()

ROOT = NS.parent  # level4/closure_proofs
LF = ROOT / "p5y_k5_lower_front_order3" / "evidence" / "tc_r1"
CELLS_JSON = ROOT / "p5y_k1_cover_ledger_successor" / "config" / "cells.json"
M_VALUES = (1, 2, 3, 5)


LF_CELLS = range(11, 45)  # the 34 committed lower-front TC cells (declared rule); nothing else is kept


def load_lower_front_cover():
    """cells.json filtered AT LOAD TIME to CUSUM cells 11-44 (review F18): the path is guarded, each kept entry is
    guarded per m, and no other entry is retained."""
    Q.guard_path(CELLS_JSON)
    kept = {}
    for c in json.loads(CELLS_JSON.read_text()):
        if c["detector"] != "CUSUM" or int(c["index"]) not in LF_CELLS:
            continue
        for m in M_VALUES:
            Q.guard_cell("CUSUM", m, int(c["index"]))
        kept[int(c["index"])] = c
    if sorted(kept) != list(LF_CELLS):
        raise RuntimeError("lower-front cover filter did not return exactly cells 11-44")
    return kept


def coefficients(m):
    """ERROR_ALGEBRA section 4: F_r gets 1/m (r < m); W_(r,t-r-1) gets 1/t - 1/m (1 <= t < m, r < t)."""
    rows = [("F", r, 0, F(1, m)) for r in range(m)]
    rows += [("W", r, t - r - 1, F(1, t) - F(1, m)) for t in range(1, m) for r in range(t)]
    return rows


def tower(k, j, supS0, order):
    """frozen pure J/h Leibniz tower (THEOREM_TC P3): returns sigma_order(r) for r = 0..4."""
    h = {1: {0: F(1), **{nn: supS0[nn - 1] for nn in range(1, 5)}}}
    for jj in range(2, 5):
        h[jj] = {0: F(1)}
        for nn in range(1, 5):
            h[jj][nn] = sum((comb(nn, i) * k[i] * h[jj - 1][nn - i] for i in range(nn + 1)), F(0))
    sig = {0: supS0[order]}
    for r in range(1, 5):
        sig[r] = sum((comb(order, i) * j[i] * h[r][order - i] for i in range(order + 1)), F(0))
    return sig


def per_object(cell, r, A, route, perturb=F(0)):
    o = cell["r"][str(r)]
    rho = F(cell["rho"])
    k = [F(x) for x in cell["norms"]["k"]]
    j = [F(x) for x in cell["norms"]["j"]]
    supS0 = [F(x) for x in cell["sup_S0"]]
    eps = [F(x) for x in o["eps_src"]]
    fF, fD, fH = F(o["delta_F"]) + eps[0], F(o["delta_D"]) + eps[1], F(o["delta_H"]) + eps[2]
    sF, sD, sH, sGr = (F(o["sup"][x]) for x in ("F", "D", "H", "G"))
    s4 = tower(k, j, supS0, 4)[r]
    s3 = tower(k, j, supS0, 3)[r]
    if route == "real":
        fG, sG, Gat = F(o["delta_G"]) + eps[3] + perturb, sGr, F(o["abs_G_at_a"])
    else:
        fG, sG, Gat = 3 * k[1] * sH + 3 * k[2] * sD + k[3] * sF + s3 + eps[3], F(0), F(0)
    e4 = L.env4(sF, sD, sH, sG, k, s4, rho)
    p = L.taylor_p(fF, fD, fH, fG, e4, rho)
    rad = L.radius(A[0], A[1], A[2], p)
    return {"fF": fF, "fD": fD, "fH": fH, "fG": fG, "sG": sG, "Gat": Gat, "sigma3": s3, "sigma4": s4, "env4": e4,
            "p": p, "rad": rad, "half": rho * Gat + rad, "k": k, "rho": rho, "sH": sH, "sD": sD, "sF": sF}


def enclosure(cell, objs, m):
    lo = hi = F(0)
    for kind, r, jj, c in coefficients(m):
        if kind == "F":
            a_lo, a_hi = (F(x) for x in cell["r"][str(r)]["H_at_a"])
            lo += c * (a_lo - objs[r]["half"])
            hi += c * (a_hi + objs[r]["half"])
        else:
            w_lo, w_hi = (F(x) for x in cell["W2"][f"{r}:{jj}"])
            lo += c * w_lo
            hi += c * w_hi
    return lo, hi


def stats(v):
    v = sorted(float(x) for x in v)
    return {"n": len(v), "min": v[0], "median": v[len(v) // 2], "max": v[-1]} if v else None


def main():
    t0 = time.time()
    cons = json.loads((LF / "TC_CONSUMPTION.json").read_text())
    audit = cons["tc_audit"]
    cover = load_lower_front_cover()
    files = sorted(LF.glob("cells/TC_CELL_*.json"), key=lambda p: int(p.stem.split("_")[-1]))
    touched, repro_ok, repro_n = [], 0, 0
    rows, encl = [], []
    for fp in files:
        Q.guard_path(fp)
        cell = json.loads(fp.read_text())
        cid = int(cell["cell"])
        for m in M_VALUES:
            Q.guard_cell("CUSUM", m, cid)
            touched.append({"detector": "CUSUM", "m": m, "cell": cid})
        Q.guard_drift(F(cell["left"]), F(cell["right"]))
        Araw = audit[str(cid)]["1"]["A"]
        A = (F(Araw["A0"]), F(Araw["A1"]), F(Araw["A2"]))
        real = [per_object(cell, r, A, "real") for r in range(5)]
        surr = [per_object(cell, r, A, "surrogate") for r in range(5)]
        for m in M_VALUES:
            assert all(F(audit[str(cid)][str(m)]["A"][x]) == A[i] for i, x in enumerate(("A0", "A1", "A2")))
            lo, hi = enclosure(cell, real, m)
            c_lo, c_hi = (F(x) for x in audit[str(cid)][str(m)]["H_TC"])
            repro_n += 1
            repro_ok += int(lo == c_lo and hi == c_hi)
            slo, shi = enclosure(cell, surr, m)
            encl.append({"cell": cid, "m": m, "width_real": float(hi - lo), "width_surrogate": float(shi - slo),
                         "ratio_real_over_surrogate": float((hi - lo) / (shi - slo))})
        C_up = F(cover[cid]["C_upper"])
        rho = F(cell["rho"])
        for r in range(5):
            re, su = real[r], surr[r]
            k = re["k"]
            fs = su["fG"]
            sGpart = L.env4_sG_part(re["sG"], k, rho)
            Q_real = rho * re["Gat"] + A[0] * rho * re["fG"] + A[0] * rho ** 2 / 2 * sGpart
            Q_surr = A[0] * rho * fs
            rows.append({
                "cell": cid, "r": r, "rho": float(rho), "A0": float(A[0]), "C_upper": float(C_up),
                "fG_surrogate": float(fs), "fG_real": float(re["fG"]),
                "sigma3_share_of_fG_surrogate": float(su["sigma3"] / fs),
                "sG_over_sH": float(re["sG"] / re["sH"]),
                "absGa_over_sG": float(re["Gat"] / re["sG"]),
                "alpha_absGa_over_A0fGsurr": float(re["Gat"] / (A[0] * fs)),
                "beta_env4_sG_penalty_ratio": float(rho * sGpart / (2 * fs)),
                "Q_real_over_Q_surrogate": float(Q_real / Q_surr),
                "half_real_over_half_surrogate": float(re["half"] / su["half"]),
                "perron_index_sG_over_Cupper_fGsurr": float(re["sG"] / (C_up * fs)),
                "cover_factor_2k1rhoC": float(2 * k[1] * rho * C_up),
                "real_half_split": {"centre_motion": float(rho * re["Gat"]),
                                    "A0_rho_fG": float(A[0] * rho * re["fG"]),
                                    "A0_rho2_env4_over2": float(A[0] * rho ** 2 * re["env4"] / 2),
                                    "of_which_sG_part": float(A[0] * rho ** 2 * sGpart / 2),
                                    "A0_fH": float(A[0] * re["fH"]),
                                    "2A1_p1": float(2 * A[1] * re["p"][1]), "A2_p0": float(A[2] * re["p"][0])},
                "surrogate_half_split": {"A0_rho_fG": float(A[0] * rho * fs),
                                         "A0_rho2_env4_over2": float(A[0] * rho ** 2 * su["env4"] / 2),
                                         "A0_fH": float(A[0] * su["fH"]),
                                         "2A1_p1": float(2 * A[1] * su["p"][1]), "A2_p0": float(A[2] * su["p"][0])},
            })
    # negative control: a 2^-60 perturbation of one committed field must break exact reproduction
    cell11 = json.loads((LF / "cells" / "TC_CELL_11.json").read_text())
    Araw = audit["11"]["1"]["A"]
    A = (F(Araw["A0"]), F(Araw["A1"]), F(Araw["A2"]))
    objs = [per_object(cell11, r, A, "real", perturb=(F(1, 2 ** 60) if r == 0 else F(0))) for r in range(5)]
    lo, hi = enclosure(cell11, objs, 5)
    c_lo, c_hi = (F(x) for x in audit["11"]["5"]["H_TC"])
    nc_detected = not (lo == c_lo and hi == c_hi)
    keys = ["fG_surrogate", "fG_real", "sigma3_share_of_fG_surrogate", "sG_over_sH", "absGa_over_sG",
            "alpha_absGa_over_A0fGsurr", "beta_env4_sG_penalty_ratio", "Q_real_over_Q_surrogate",
            "half_real_over_half_surrogate", "perron_index_sG_over_Cupper_fGsurr", "cover_factor_2k1rhoC"]
    out = {
        "schema": "P5Y_K5_TAIL_OVERNIGHT_B307_LOWER_FRONT_ORDER3/1",
        "producer": "streams/B_307/code/b307_lower_front.py",
        "class": "NONTARGET_REAL_VALIDATION",
        "inputs": {"cells": [str(p.relative_to(ROOT)) for p in files], "consumption": str((LF / "TC_CONSUMPTION.json").relative_to(ROOT)),
                   "cover": str(CELLS_JSON.relative_to(ROOT))},
        "coverage": {"cells": len(files), "objects": len(rows), "enclosures": len(encl)},
        "reproduction_gate": {"exact_matches": repro_ok, "of": repro_n,
                              "negative_control_perturbed_delta_G_detected": nc_detected},
        "sigma3_note": "pure J/h tower (Aux3 (P3') inputs are not in the lower-front cell files)",
        "baseline_caveat": "the surrogate baseline uses the pure-tower sigma3, which is looser than a (P3')-refined surrogate; every real/surrogate ratio here therefore FAVOURS the real-G route (R1)",
        "enclosure_narrowing_factor_surrogate_over_real_all_m": {
            "min": min(1 / e["ratio_real_over_surrogate"] for e in encl),
            "max": max(1 / e["ratio_real_over_surrogate"] for e in encl)},
        "summary_by_r": {str(r): {kk: stats([x[kk] for x in rows if x["r"] == r]) for kk in keys} for r in range(5)},
        "summary_all": {kk: stats([x[kk] for x in rows]) for kk in keys},
        "enclosure_width_ratio_real_over_surrogate": {str(m): stats([e["ratio_real_over_surrogate"] for e in encl if e["m"] == m])
                                                      for m in M_VALUES},
        "rows": rows,
        "enclosures": encl,
        "wall_seconds": time.time() - t0,
    }
    with open(NS / "validation" / "B307_LOWER_FRONT_ORDER3.json", "w") as fh:
        json.dump(out, fh, indent=1)
    Q.log_execution("streams/B_307/code/b307_lower_front.py",
                    "B307: lower-front real order-3 vs zero-candidate surrogate (committed fields only; exact TC reproduction gate)",
                    cells_touched=touched, klass="NONTARGET_REAL_VALIDATION",
                    notes=f"repro {repro_ok}/{repro_n}; NC detected={nc_detected}")
    print(json.dumps({"repro": f"{repro_ok}/{repro_n}", "nc": nc_detected, "summary_all": out["summary_all"],
                      "encl": out["enclosure_width_ratio_real_over_surrogate"],
                      "narrowing": out["enclosure_narrowing_factor_surrogate_over_real_all_m"]}, indent=1)[-1500:])


if __name__ == "__main__":
    main()
