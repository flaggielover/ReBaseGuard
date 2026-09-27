"""Log-log slopes of the atom-constant rungs against Lambda on FX_B, at every declared drift (0, 1/4, 1/2).

Reads NS/validation/B307_AUDIT_FIXTURES.json (produced by b307_run_fixtures.py; exact values rendered as floats) and
writes NS/validation/B307_SCALING.json.  Pure post-processing of synthetic results; no new model evaluation.
Negative control: a planted rung 'true * Lambda^{1/2}' must show a slope exactly 1/2 above the true one.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[2]
sys.path.insert(0, str(NS / "code"))
import ov_quarantine as Q  # noqa: E402

Q.install_import_guard()


def slope(xs, ys):
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)


def main():
    d = json.loads((NS / "validation" / "B307_AUDIT_FIXTURES.json").read_text())
    pts = [p for p in d["P2_ladders"]["points"] if p["spec"]["class"] == "FX_B"]
    out = {}
    for e in ("0", "1/4", "1/2"):
        sel = [p for p in pts if p["spec"]["e"] == e]
        xs = [math.log(p["Lambda"]) for p in sel]
        rec = {"Lambda": [p["Lambda"] for p in sel], "C_T": [p["C_T"] for p in sel], "C": [p["C"] for p in sel]}
        for A in ("A1", "A2", "A3"):
            rec[A] = {lv: slope(xs, [math.log(p[A][lv]) for p in sel]) for lv in sel[0][A]}
        rec["C_T_slope"] = slope(xs, [math.log(p["C_T"]) for p in sel])
        rec["C_slope"] = slope(xs, [math.log(p["C"]) for p in sel])
        planted = slope(xs, [math.log(p["A1"]["true"] * math.sqrt(p["Lambda"])) for p in sel])
        rec["negative_control_planted_extra_half_power_detected"] = abs(planted - rec["A1"]["true"] - 0.5) < 1e-9
        out[e] = rec
    with open(NS / "validation" / "B307_SCALING.json", "w") as fh:
        json.dump({"schema": "P5Y_K5_TAIL_OVERNIGHT_B307_SCALING/1", "producer": "streams/B_307/code/b307_scaling.py",
                   "class": "SYNTHETIC_VALIDATION", "source": "validation/B307_AUDIT_FIXTURES.json",
                   "slopes_vs_Lambda_by_drift": out}, fh, indent=1)
    Q.log_execution("streams/B_307/code/b307_scaling.py", "B307: FX_B log-log slopes of atom-constant rungs vs Lambda",
                    cells_touched=[], klass="SYNTHETIC_VALIDATION")
    for e, rec in out.items():
        print(e, {A: {k: round(v, 3) for k, v in rec[A].items()} for A in ("A1", "A2", "A3")},
              "C_T", round(rec["C_T_slope"], 3), "C", round(rec["C_slope"], 3),
              "Lambda", [round(x, 1) for x in rec["Lambda"]], "NC", rec["negative_control_planted_extra_half_power_detected"])


if __name__ == "__main__":
    main()
