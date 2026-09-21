"""Phases 1, 2 and 5: the blocker decomposition, the reproduction of C4's sensitivity anchors, and the kill gates.

Everything is recomputed from committed evidence through the frozen consumers. Results are tagged by epistemic
status: CERTIFIED (a deterministic re-evaluation of frozen certified inputs), REPRODUCED (an independently
recomputed predecessor claim), or DIAGNOSTIC (a sensitivity sweep in which the independent TC-T crosscheck had to
be aligned to the frozen path, or which consumes an uncertified float floor).

    python3 -B c5_analysis.py --out-decomposition D.json --out-sensitivity S.json
"""
import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import c5_transport as TR                                                      # noqa: E402
from c5_common import OPEN_CELLS, cell_supply, committed_inputs, frozen_stack, knock  # noqa: E402

# DIAGNOSTIC floors on Lambda = sup_cell E_a[tau]: C4's Monte-Carlo at the cell's own left endpoint, and for 307
# the interpolation of C4's two committed midpoint diagnostics. Never certified, never load-bearing.
LAMBDA_DIAG = {307: F(45929, 10000), 308: F(43110, 10000), 309: F(40473, 10000)}
C4_CERT_FLOOR = {307: None, 308: F(3512733596022926, 10 ** 15), 309: F(3297250281519544, 10 ** 15)}
C4_ANCHORS = {"baseline": 3.214236, "sup_FDH_halved": 4.160309, "rho_halved": 7.534321}


def signed_enclosure(d, ad5):
    """The signed whole-cell R'' enclosure the frozen consumer actually uses: sealed R2 interval ^ TC-T."""
    a = max(F(ad5["R2_interval"]["lo"]), d["lo"])
    b = min(F(ad5["R2_interval"]["hi"]), d["hi"])
    M0 = F(ad5["M_R2"])
    if a > b:
        return -M0, M0, True
    return max(a, -M0), min(b, M0), False


def decompose(FC, B, T, R, DC, SEL, adopted, cover, c1, c2):
    out = {}
    for k in OPEN_CELLS:
        meas, aux, ad5, cov, s = cell_supply(k, FC, B, T, R, DC, SEL, adopted, cover, c1, c2)
        A = s["A"]
        d = FC.direct(T, R, meas, aux, A, ad5, cov, B)
        lo, hi, obj = T.tail_enclosure(R, meas, aux, A, 5, None)
        e0, rho, x_hi = (B.rat(cov[t]) for t in ("e0", "rho", "right"))
        g_hi = F(ad5["R_interval"]["hi"]) - e0 * F(ad5["D_interval"]["lo"])
        need_M = (-g_hi) / (rho * x_hi)
        Clo = Chi = S = F(0)
        parts = {"A0*p2": F(0), "2A1*p1": F(0), "A2*p0": F(0)}
        sub = {"A0*fH": F(0), "A0*rho*fG": F(0), "A0*rho^2*env4/2": F(0)}
        for kind, r, jj, c in R.coefficients(5):
            if kind == "F":
                a, b = (F(x) for x in meas["r"][str(r)]["H_at_a"])
                Clo += c * a
                Chi += c * b
                o = obj[r]
                p0, p1, p2 = o["p"]
                S += c * o["half"]
                parts["A0*p2"] += c * A["A0"] * p2
                parts["2A1*p1"] += c * 2 * A["A1"] * p1
                parts["A2*p0"] += c * A["A2"] * p0
                fH = F(meas["r"][str(r)]["delta_H"]) + F(meas["r"][str(r)]["eps_src"][2])
                sub["A0*fH"] += c * A["A0"] * fH
                sub["A0*rho*fG"] += c * A["A0"] * rho * o["f_G"]
                sub["A0*rho^2*env4/2"] += c * A["A0"] * rho * rho * o["env4"] / 2
            else:
                a, b = (F(x) for x in meas["W2"][f"{r}:{jj}"])
                Clo += c * a
                Chi += c * b
        M = max(abs(lo), abs(hi))
        tot = sum(parts.values())
        Hlo, Hhi, empty = signed_enclosure(d, ad5)
        t5 = TR.gamma(g_hi, Hlo, Hhi, e0, rho)
        out[str(k)] = {
            "status": "CERTIFIED",
            "e0": str(e0), "rho": str(rho), "x_hi": str(x_hi),
            "Gamma_frozen": float(d["Gamma"]), "closes_frozen": bool(d["pass"]),
            "g_hi": float(g_hi), "penalty_frozen": float(rho * x_hi * d["M"]),
            "M_used": float(d["M"]), "M_needed_for_closure": float(need_M),
            "M_reduction_factor_needed": float(d["M"] / need_M),
            "R2_enclosure_signed": [float(Hlo), float(Hhi)], "intersection_empty": empty,
            "TCT_enclosure": [float(lo), float(hi)],
            "centre": [float(Clo), float(Chi)], "radius_sum_S": float(S),
            "S_must_fall_by_percent": float(100 * (M - need_M) / S) if M > need_M else 0.0,
            "radius_split": {n: {"value": float(v), "percent_of_S": float(100 * v / tot)} for n, v in parts.items()},
            "within_A0p2": {n: {"value": float(v), "percent_of_S": float(100 * v / tot)} for n, v in sub.items()},
            "C5T": {"Gamma": float(t5["Gamma"]), "penalty": float(t5["P"]),
                    "improvement_percent": float(100 * (1 - t5["improvement_factor"])),
                    "binding_direction": t5["binding_direction"], "closes": bool(t5["pass"])},
        }
    return out


def sensitivity(FC, B, T, R, DC, SEL, adopted, cover, c1, c2):
    S = {k: cell_supply(k, FC, B, T, R, DC, SEL, adopted, cover, c1, c2) for k in (307, 308, 309)}
    knobs = [
        ("baseline", {}, "CERTIFIED"),
        ("fG -> 0 (perfect order-3 surrogate)", {"fG": F(0)}, "DIAGNOSTIC"),
        ("env4 -> 0 (perfect 4th-order envelope)", {"env4": F(0)}, "DIAGNOSTIC"),
        ("fG and env4 -> 0", {"fG": F(0), "env4": F(0)}, "DIAGNOSTIC"),
        ("sigma3 -> 0", {"sigma3": F(0)}, "DIAGNOSTIC"),
        ("sigma4 -> 0", {"sigma4": F(0)}, "DIAGNOSTIC"),
        ("sigma3 and sigma4 -> 0", {"sigma3": F(0), "sigma4": F(0)}, "DIAGNOSTIC"),
        ("sup F/D/H halved", {"supF": F(1, 2), "supD": F(1, 2), "supH": F(1, 2)}, "DIAGNOSTIC"),
        ("sup F/D/H -> 0", {"supF": F(0), "supD": F(0), "supH": F(0)}, "DIAGNOSTIC"),
        ("A1 = A2 = 0 (the C4 knockout)", {"A1": F(0), "A2": F(0)}, "CERTIFIED"),
        ("rho halved (cover refinement)", {"rho": F(1, 2)}, "DIAGNOSTIC"),
        ("fG, env4, A1, A2 all -> 0", {"fG": F(0), "env4": F(0), "A1": F(0), "A2": F(0)}, "DIAGNOSTIC"),
    ]
    rows = []
    for name, sc, status in knobs:
        row = {"knob": name, "status": status, "cells": {}}
        for k in (307, 308, 309):
            meas, aux, ad5, cov, s = S[k]
            d = knock(FC, B, T, R, meas, aux, ad5, cov, s["A"], sc)
            row["cells"][str(k)] = {"Gamma": float(d["Gamma"]), "closes": bool(d["pass"])}
        rows.append(row)

    # the atom-constant direction pushed to its floor
    floor = {}
    for k in (307, 308, 309):
        meas, aux, ad5, cov, s = S[k]
        r = {"A0_certified": float(s["A"]["A0"])}
        if C4_CERT_FLOOR[k] is not None:
            d = knock(FC, B, T, R, meas, aux, ad5, cov,
                      {"A0": C4_CERT_FLOOR[k], "A1": F(0), "A2": F(0)})
            r["at_C4_certified_floor_A1A2_zero"] = {"A0": float(C4_CERT_FLOOR[k]), "Gamma": float(d["Gamma"]),
                                                    "closes": bool(d["pass"]), "status": "CERTIFIED"}
        d = knock(FC, B, T, R, meas, aux, ad5, cov, {"A0": LAMBDA_DIAG[k], "A1": F(0), "A2": F(0)})
        r["at_diagnostic_Lambda_A1A2_zero"] = {"A0": float(LAMBDA_DIAG[k]), "Gamma": float(d["Gamma"]),
                                               "closes": bool(d["pass"]), "status": "DIAGNOSTIC"}
        floor[str(k)] = r

    # C4 anchor reproduction: the critical A0 at A1 = A2 = 0, cell 309
    meas, aux, ad5, cov, s = S[309]

    def crit(sc):
        lo, hi = F(0), F(100)
        if not knock(FC, B, T, R, meas, aux, ad5, cov, {"A0": lo, "A1": F(0), "A2": F(0)}, sc)["pass"]:
            return None
        for _ in range(140):
            mid = (lo + hi) / 2
            if knock(FC, B, T, R, meas, aux, ad5, cov, {"A0": mid, "A1": F(0), "A2": F(0)}, sc)["pass"]:
                lo = mid
            else:
                hi = mid
        return lo
    anchors = {}
    for name, sc in (("baseline", {}),
                     ("sup_FDH_halved", {"supF": F(1, 2), "supD": F(1, 2), "supH": F(1, 2)}),
                     ("rho_halved", {"rho": F(1, 2)})):
        c = crit(sc)
        anchors[name] = {"recomputed_critical_A0": float(c),
                         "c4_adjudicator_claimed": C4_ANCHORS[name],
                         "agrees_to_1e-5": abs(float(c) - C4_ANCHORS[name]) < 1e-5,
                         "status": "REPRODUCED"}
    return {"knockouts": rows, "atom_constant_floor": floor, "c4_anchor_reproduction": anchors}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-decomposition", required=True)
    ap.add_argument("--out-sensitivity", required=True)
    a = ap.parse_args()
    FC, B, T, R, DC, SEL = frozen_stack()
    adopted, cover, c1, c2 = committed_inputs(FC)

    dec = decompose(FC, B, T, R, DC, SEL, adopted, cover, c1, c2)
    Path(a.out_decomposition).write_text(json.dumps(
        {"schema": "rebaseguard.p5y.k5.tail-c5.decomposition.v1",
         "clause": "Gamma = g_hi + rho*x_hi*M ; only M is improvable, g_hi/rho/x_hi are sealed record and cover",
         "cells": dec, "new_real_scientific_addresses_evaluated": 0,
         "guard": "REAL_SCIENTIFIC_COMPUTE = DENY"}, sort_keys=True, indent=1) + "\n")

    sen = sensitivity(FC, B, T, R, DC, SEL, adopted, cover, c1, c2)
    Path(a.out_sensitivity).write_text(json.dumps(
        {"schema": "rebaseguard.p5y.k5.tail-c5.sensitivity.v1", **sen,
         "crosscheck_note": "every scaled row aligns the independent TC-T crosscheck to the frozen path and is "
                            "therefore DIAGNOSTIC; the baseline and the A1=A2=0 rows scale no ingredient and run "
                            "with the crosscheck live",
         "new_real_scientific_addresses_evaluated": 0,
         "guard": "REAL_SCIENTIFIC_COMPUTE = DENY"}, sort_keys=True, indent=1) + "\n")

    for k, v in dec.items():
        print(f"cell {k}: Gamma={v['Gamma_frozen']:+.9f} -> C5-T {v['C5T']['Gamma']:+.9f} "
              f"({v['C5T']['improvement_percent']:.3f}%)  S must fall {v['S_must_fall_by_percent']:.2f}%  "
              f"A0*rho*fG={v['within_A0p2']['A0*rho*fG']['percent_of_S']:.1f}% of S")
    print("anchors:", json.dumps({k: v["agrees_to_1e-5"] for k, v in sen["c4_anchor_reproduction"].items()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
