"""Evaluate the FROZEN feasibility gate (config/FEASIBILITY_GATES.json) on a certified operator registry.

No K1 record and no R value is read. For every front cell k in 11..148 the theorem-AD constants A_j^cert(k) derived from
the certified registry (consumer rule of that registry) are compared with A_j^fc(k; s) derived from the frozen forecast
model forecast_registry(profile, s). Level L holds iff A_j^cert(k) <= A_j^fc(k; s_L) for all k, j.

    python3 -B code/gate_eval.py --registry REGISTRY.json --out GATE_RESULT.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(REPO / "level4/closure_proofs/p5y_k5_order3_readiness_audit/code"))
import deflated_consume as DC  # noqa: E402
import k5_minimality as KM  # noqa: E402

GATES = NS / "config/FEASIBILITY_GATES.json"
PROFILE = NS / "evidence/OPERATOR_FLOAT_PROFILE_deg20.json"
CELLS_JSON = REPO / "level4/closure_proofs/p5y_k1_cover_ledger_successor/config/cells.json"
FRONT = range(11, 149)


def constants(reg, x_lo, x_hi):
    c = DC.block_for(reg, x_lo, x_hi)
    if c is None:
        return None
    if reg.get("rule") == "r2":
        return DC.atom_constants_r2(c["Abar"], c["tau"], c["C"], c["Dlo"], c["D1"], c["D2"])
    return DC.atom_constants(c["tau"], c["C"], c["Dlo"], c["D1"], c["D2"])


def dominated(cert, fc):
    return cert is not None and fc is not None and all(cert[j] <= fc[j] for j in ("A0", "A1", "A2"))


def evaluate(reg: dict) -> dict:
    gates = json.loads(GATES.read_text())
    profile = json.loads(PROFILE.read_text())
    cover = {c["index"]: c for c in KM.load_cells(CELLS_JSON, "CUSUM")}
    geo = {k: (KM.rat(cover[k]["left"]), KM.rat(cover[k]["right"]), KM.rat(cover[k]["C_upper"])) for k in FRONT}
    cert = {k: constants(reg, *geo[k][:2]) for k in FRONT}
    scales = sorted(gates["forecast_front_coverage_fraction_by_scale"], key=F)
    dom = {}
    for s in scales:
        fc_reg = DC.forecast_registry(profile, F(s))
        dom[s] = [k for k in FRONT if not dominated(cert[k], constants(fc_reg, *geo[k][:2]))]
    s_min = next((s for s in scales if not dom[s]), None)
    lv = gates["levels"]
    level = "UNINFORMATIVE"
    if not dom.get(lv["MARGINAL"]["threshold_scale"], [0]):
        level = "MARGINAL"
    if not dom.get(lv["USEFUL"]["threshold_scale"], [0]):
        level = "USEFUL"
    # descriptive: certified constants against the generic stack (C_upper, C^2 k1, 2 C^3 k1^2 + C^2 k2)
    k1, k2 = DC.K1_BOUND, DC.K2_BOUND
    ratios = []
    for k in FRONT:
        Cu = geo[k][2]
        gen = {"A0": Cu, "A1": Cu ** 2 * k1, "A2": 2 * Cu ** 3 * k1 ** 2 + Cu ** 2 * k2}
        ratios.append({j: float(gen[j] / cert[k][j]) for j in ("A0", "A1", "A2")} if cert[k] else None)
    rows = [b for b in reg["blocks"] if any(geo[k][0] < F(b["e_hi"]) and F(b["e_lo"]) < geo[k][1] for k in FRONT)]
    summ = {key: [min(float(F(b[key])) for b in rows), max(float(F(b[key])) for b in rows)]
            for key in ("Abar", "C_T", "tau", "D_lo", "D1", "D2")}
    return {"schema": "rebaseguard.p5y.k5.perron-deflation.gate-result.v1",
            "registry_sha256": None, "gates_sha256": hashlib.sha256(GATES.read_bytes()).hexdigest(),
            "front_cells": [FRONT.start, FRONT.stop - 1], "uncovered_front_cells": [k for k in FRONT if cert[k] is None],
            "not_dominated_by_scale": {s: v for s, v in dom.items()},
            "smallest_dominating_scale": s_min, "level": level,
            "forecast_coverage_at_smallest_dominating_scale":
                gates["forecast_front_coverage_fraction_by_scale"].get(s_min) if s_min else None,
            "certified_constants_front_range": summ,
            "improvement_over_generic_stack": {j: [min(r[j] for r in ratios if r), max(r[j] for r in ratios if r)]
                                               for j in ("A0", "A1", "A2")}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    raw = Path(a.registry).read_bytes()
    reg = json.loads(raw)
    if reg.get("certified") is not True:
        raise SystemExit("registry is not certified")
    res = evaluate(reg)
    res["registry_sha256"] = hashlib.sha256(raw).hexdigest()
    Path(a.out).write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: res[k] for k in ("level", "smallest_dominating_scale", "uncovered_front_cells",
                                         "forecast_coverage_at_smallest_dominating_scale",
                                         "certified_constants_front_range", "improvement_over_generic_stack")},
                     indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
