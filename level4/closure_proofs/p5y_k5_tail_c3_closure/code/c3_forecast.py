"""The C3 deterministic forecast on cells 306-309, classified mechanically against the frozen gate.

Refuses unless the gate hashes to its frozen value. Reads only committed certified evidence; evaluates no
scientific address; passes order3 = None throughout.

    python3 -B c3_forecast.py --out OUT.json
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
FIELDS = ("A0", "A1", "A2")


def load(path, name, pin=None):
    raw = Path(path).read_bytes()
    if pin and hashlib.sha256(raw).hexdigest() != pin:
        raise SystemExit(f"pin mismatch: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def classify(gate, per, universe):
    """The frozen classes, applied in the frozen order. Decides nothing not written in the gate."""
    thresh = F(str(gate["material_tightening_test"]["threshold"]))
    base_gap = {int(k): F(str(v)) for k, v in gate["baseline"]["gap"].items()}
    closed = [k for k in universe if per[str(k)]["closes"]]
    adoptable = [k for k in closed if per[str(k)]["adoption_floor"]["meets_floor"]]
    still = [k for k in universe if k not in closed]
    mt = {k: (F(str(per[str(k)]["gap_above_1"])) <= (1 - thresh) * base_gap[k])
          for k in still if base_gap[k] > 0}
    if per.get("__invalid__"):
        return "INVALID", closed, adoptable, still, mt
    if adoptable:
        return "USEFUL", closed, adoptable, still, mt
    if closed:
        return "PARTIAL", closed, adoptable, still, mt
    if mt and all(mt.values()):
        return "MATERIAL_TIGHTENING_ONLY", closed, adoptable, still, mt
    return "MARGINAL", closed, adoptable, still, mt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    SEL = load(NS / "code/c3_selector.py", "c3sel")
    gate = SEL.frozen_gate()                      # refuses unless sha256 == the frozen gate (review note N3)
    universe = gate["universe"]["cells"]
    degr = F(str(gate["adoption_floor"]["degradation_factor"]))

    FC = load(C2 / "code/c2_d5_forecast.py", "c2fc")
    B = FC.load(FC.B_NS / "code/tail_forecast_r2.py", "b_tf")
    T = sys.modules["tct_rule"]
    R = T.load_frozen("tc_rule", T.FROZEN["tc_rule"][1])
    DC = FC.load(FC.AD_NS / "code/deflated_consume.py", "ad_dc", FC.DC_SHA)

    adopted = json.loads((FC.B_NS / "evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json").read_bytes())["cells"]
    cover = {c["index"]: c for c in json.loads(
        (CP / "p5y_k1_cover_ledger_successor/config/cells.json").read_bytes()) if c["detector"] == "CUSUM"}
    c1 = {b["cell"]: b for b in json.loads(
        (FC.C1_NS / "evidence/registry_c1/REGISTRY_C1.json").read_bytes())["blocks"]}
    c2 = {b["cell"]: b for b in json.loads(
        (C2 / "evidence/registry_c2/REGISTRY_C2.json").read_bytes())["blocks"]}

    base_req = {int(k): F(str(v)) for k, v in gate["baseline"]["requirement"].items()}
    base_gap = {int(k): F(str(v)) for k, v in gate["baseline"]["gap"].items()}

    per = {}
    for k in universe:
        meas = json.loads((FC.B_NS / f"evidence/measurement_r1/TCT_INPUTS_{k}.json").read_bytes())
        meas["C_upper"] = adopted[str(k)]["C_upper"]
        aux, ad5, cov = adopted[str(k)]["auxiliary_evidence"], adopted[str(k)]["m"]["5"], cover[k]

        s = SEL.build(k, c1[k], c2[k], cov, meas, DC, T, B.rat)
        A = s["A"]
        d = FC.direct(T, R, meas, aux, A, ad5, cov, B)
        req = FC.requirement(T, R, meas, aux, A, ad5, cov, B)
        gap = max(F(0), req - 1) if req is not None else None

        # ---- the frozen adoption floor, evaluated per cell ---------------------------------------------
        kn = {i: F(meas["norms"]["k"][i]) for i in range(5)}
        Ag = T.atom_constants_generic(F(meas["C_upper"]), kn[1], kn[2])
        f1 = FC.direct(T, R, meas, aux, Ag, ad5, cov, B)["pass"]           # registry-independent supply
        f2 = FC.direct(T, R, meas, aux, {j: A[j] * degr for j in A}, ad5, cov, B)["pass"]
        margin = None
        if d["pass"]:
            lo, hi = F(1), F(4)
            for _ in range(60):
                mid = (lo + hi) / 2
                if FC.direct(T, R, meas, aux, {j: A[j] * mid for j in A}, ad5, cov, B)["pass"]:
                    lo = mid
                else:
                    hi = mid
            margin = float(lo)

        per[str(k)] = {
            "baseline_requirement_r5": float(base_req[k]), "baseline_gap_r5": float(base_gap[k]),
            "magnitude": float(d["mag"]), "Gamma": float(d["Gamma"]), "closes": bool(d["pass"]),
            "requirement": float(req) if req is not None else None,
            "gap_above_1": float(gap) if gap is not None else None,
            "closure_ratio": float(req) if req is not None else None,
            "gap_fall_vs_r5": (None if base_gap[k] == 0 or gap is None else float(1 - gap / base_gap[k])),
            "A": {j: float(A[j]) for j in FIELDS},
            "A_provenance": s["A_provenance"], "operator_provenance": s["operator_provenance"],
            "operator_tuple": s["operator_tuple"],
            "rejected_sources": s["rejected_sources"], "premise_fallback": s["premise_fallback"],
            "whole_cell_valid": not s["rejected_sources"],
            "adoption_floor": {"F1_registry_independent_closure": bool(f1),
                               "F2_survives_x1.25": bool(f2),
                               "uniform_A_margin": margin,
                               "meets_floor": bool(f1 or f2)},
        }

    cls, closed, adoptable, still, mt = classify(gate, per, universe)
    out = {"schema": "rebaseguard.p5y.k5.tail-c3.forecast.v1",
           "gate_sha256": SEL.GATE_SHA, "universe": universe,
           "new_real_scientific_addresses_evaluated": 0, "guard": "REAL_SCIENTIFIC_COMPUTE = DENY",
           "cells": per,
           "C3_CLASS": cls, "closed": closed, "adoptable": adoptable, "still_open": still,
           "materially_tightened": {str(k): v for k, v in mt.items()},
           "decision_rule_for_class": gate["decision_rule"][cls]}
    data = json.dumps(out, sort_keys=True, indent=1) + "\n"
    Path(a.out).write_text(data)
    print(json.dumps({"C3_CLASS": cls, "closed": closed, "adoptable": adoptable,
                      "still_open": still, "materially_tightened": {str(k): v for k, v in mt.items()},
                      "sha256": hashlib.sha256(data.encode()).hexdigest()}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
