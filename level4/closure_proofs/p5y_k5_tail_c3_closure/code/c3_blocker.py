"""Reconstruct, from committed certified evidence only, why cells 306-309 remain open under authoritative r5.

Reads no K1 record store, evaluates no scientific address. Everything here is derived from the C2 namespace's
committed artifacts and the frozen theorem/consumer modules, which C3 treats as read-only predecessors.

    python3 -B c3_blocker.py --out OUT.json
"""
import argparse
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
CP = HERE.parents[2]
C2 = CP / "p5y_k5_tail_c2_closure"
OPEN = (306, 307, 308, 309)


def load(path, name, pin=None):
    raw = Path(path).read_bytes()
    if pin and hashlib.sha256(raw).hexdigest() != pin:
        raise SystemExit(f"pin mismatch: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    FC = load(C2 / "code/c2_d5_forecast.py", "c2fc")
    B = FC.load(FC.B_NS / "code/tail_forecast_r2.py", "b_tf")
    T = sys.modules["tct_rule"]
    R = T.load_frozen("tc_rule", T.FROZEN["tc_rule"][1])
    DC = FC.load(FC.AD_NS / "code/deflated_consume.py", "ad_dc", FC.DC_SHA)

    adopted = json.loads((FC.B_NS / "evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json").read_bytes())["cells"]
    cover = {c["index"]: c for c in json.loads(
        (CP / "p5y_k1_cover_ledger_successor/config/cells.json").read_bytes()) if c["detector"] == "CUSUM"}
    c1b = {b["cell"]: b for b in json.loads(
        (FC.C1_NS / "evidence/registry_c1/REGISTRY_C1.json").read_bytes())["blocks"]}
    c2b = {b["cell"]: b for b in json.loads(
        (C2 / "evidence/registry_c2/REGISTRY_C2.json").read_bytes())["blocks"]}

    def dv(b):
        return DC.atom_constants_r2(*(F(str(b[x])) for x in ("Abar", "tau", "C_T", "D_lo", "D1", "D2")))

    def opmix(c1, c2):
        g = lambda b, f: F(str(b[f]))
        return {"Abar": min(g(c1, "Abar"), g(c2, "Abar")), "tau": min(g(c1, "tau"), g(c2, "tau")),
                "C_T": min(g(c1, "C_T"), g(c2, "C_T")), "D_lo": max(g(c1, "D_lo"), g(c2, "D_lo")),
                "D1": min(g(c1, "D1"), g(c2, "D1")), "D2": min(g(c1, "D2"), g(c2, "D2"))}

    out = {"schema": "rebaseguard.p5y.k5.tail-c3.blocker.v1",
           "source": "committed certified evidence only; no record store, no new-real evaluation",
           "cells": {}}

    for k in OPEN:
        meas = json.loads((FC.B_NS / f"evidence/measurement_r1/TCT_INPUTS_{k}.json").read_bytes())
        meas["C_upper"] = adopted[str(k)]["C_upper"]
        aux = adopted[str(k)]["auxiliary_evidence"]
        ad5, cov = adopted[str(k)]["m"]["5"], cover[k]
        kn = {i: F(meas["norms"]["k"][i]) for i in range(5)}

        sup = {"G": T.atom_constants_generic(F(meas["C_upper"]), kn[1], kn[2]),
               "C1": dv(c1b[k]), "C2": dv(c2b[k]), "operator_mixed": dv(opmix(c1b[k], c2b[k]))}
        sup["D4_min_over_supplies"] = FC.combine({n: sup[n] for n in ("G", "C1", "C2")})[0]

        per = {}
        for name, A in sup.items():
            d = FC.direct(T, R, meas, aux, A, ad5, cov, B)
            req = FC.requirement(T, R, meas, aux, A, ad5, cov, B)
            # uniform-A margin: the factor by which every A_j could be inflated before the cell reopens
            lo, hi = F(1), F(4)
            if d["pass"]:
                for _ in range(60):
                    mid = (lo + hi) / 2
                    if FC.direct(T, R, meas, aux, {j: A[j] * mid for j in A}, ad5, cov, B)["pass"]:
                        lo = mid
                    else:
                        hi = mid
                margin = float(lo)
            else:
                margin = None
            per[name] = {"Gamma": float(d["Gamma"]), "closes": d["pass"],
                         "magnitude": float(d["mag"]), "M_needed_ratio": None,
                         "requirement": float(req) if req is not None else None,
                         "uniform_A_margin": margin,
                         "A": {j: float(A[j]) for j in ("A0", "A1", "A2")}}

        # radius decomposition under the mixed supply: what actually blocks
        A = sup["operator_mixed"]
        lo_, hi_, obj = T.tail_enclosure(R, meas, aux, A, 5, None)
        grouped = {"order3_residual_fG": 0.0, "P3_envelope_Env4": 0.0,
                   "order2_fH": 0.0, "order1_fD": 0.0, "order0_fF": 0.0}
        tot = F(0)
        for r in range(5):
            o = obj[r]
            rad = o["rad"]
            tot += rad
            p = o["p"]
            grouped["order3_residual_fG"] += float(o["f_G"])
            grouped["P3_envelope_Env4"] += float(o["env4"])
        out["cells"][str(k)] = {
            "per_supply": per,
            "operator_mixed_radius_mean": float(tot / 5),
            "fG_plus_Env4_mean": {"f_G": grouped["order3_residual_fG"] / 5,
                                  "Env4": grouped["P3_envelope_Env4"] / 5},
            "certificate_surfaces": {
                "G": "Lemma G generic constants from C_upper and the adopted norms - NO Arb/FLINT registry",
                "C1": "Lemma Dv' over the C1 one-block-per-cell Arb/FLINT registry",
                "C2": "Lemma Dv' over the C2 refined sub-block Arb/FLINT registry",
                "operator_mixed": "Lemma Dv' over componentwise-best of the C1 and C2 Arb/FLINT registries",
            },
            "independence": {
                "G_is_registry_independent": True,
                "C1_C2_share_surface": "both are taboo_certify Arb supersolutions; same implementation, same pin",
                "operator_mixed_is_registry_independent": False,
            },
        }

    data = json.dumps(out, sort_keys=True, indent=1) + "\n"
    Path(a.out).write_text(data)
    print(json.dumps({"cells": list(OPEN), "sha256": hashlib.sha256(data.encode()).hexdigest()}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
