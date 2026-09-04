#!/usr/bin/env python3
"""Cross-check every headline number in PILOT_REPORT.md against the JSON.

A report is only as good as the fact that nothing in it was transcribed by
hand.  This re-derives each figure from `results/*.json` and fails loudly on
any mismatch.  Run it after any change to the report or the results.
"""

from __future__ import annotations

import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
R = ROOT / "results"

rep = json.loads((R / "report.json").read_text())
val = json.loads((R / "validation.json").read_text())
ct = json.loads((R / "costtail.json").read_text())
cal = json.loads((R / "calibration.json").read_text())
des = json.loads((R / "design.json").read_text())
txt = (ROOT / "PILOT_REPORT.md").read_text()

failures: list[str] = []


def chk(label: str, ok: bool, detail: str = "") -> None:
    print(("OK   " if ok else "FAIL ") + label + (f"  {detail}" if detail else ""))
    if not ok:
        failures.append(label)


def q(sorted_values: list[float], p: float) -> float:
    i = min(len(sorted_values) - 1, math.ceil(p * len(sorted_values)) - 1)
    return sorted_values[i]


pe, se = rep["primary_endpoint"], rep["secondary_endpoint"]
chk("selected rule is C_staged_safety_1.00",
    rep["selected_rule"] == "C_staged_safety_1.00")
chk("the literal frozen criterion selected nothing",
    rep["literal_frozen_criterion_selection"] is None)
chk("primary endpoint 282/282 funded",
    (pe["attained"], pe["funded_replicates"]) == (282, 282))
chk("primary Clopper-Pearson lower 0.9894",
    abs(pe["clopper_pearson_lower"] - 0.9894) < 5e-5,
    f"{pe['clopper_pearson_lower']:.6f}")
chk("primary endpoint MET", pe["met"] is True)
chk("secondary minimum 0.9278 and MET",
    abs(se["min_cell_lower_bound"] - 0.9278) < 5e-5 and se["met"])

a = next(p for p in rep["validation_pooled"] if p["rule"] == "A_oneshot_one_topup")
c = next(p for p in rep["validation_pooled"] if p["rule"] == "C_staged_safety_1.00")
chk("baseline left 9 routes UNRESOLVED", a["unresolved"] == 9)
chk("selected rule left 0 UNRESOLVED", c["unresolved"] == 0)
chk("baseline bound 0.9450 is BELOW delta",
    abs(a["lower_bound_within_cap"] - 0.9450) < 5e-5
    and a["lower_bound_within_cap"] < 0.95)
chk("baseline attained 273 of 282 funded",
    (a["attained"], a["replicates"] - a["precision_limited"]) == (273, 282))
chk("no cap-terminated rule ever reached the third state",
    all(p["unresolved"] == 0 for p in rep["validation_pooled"]
        if not p["third_state_possible"]))
chk("every cap-terminated rule attained on every funded replicate",
    all(p["p_attain_within_cap"] == 1.0 for p in rep["validation_pooled"]
        if not p["third_state_possible"]))

ratios, conditional = [], []
for cell in val["cells"]:
    for r in cell["replicates"]:
        A = r["outcomes"]["A_oneshot_one_topup"]
        C = r["outcomes"]["C_staged_safety_1.00"]
        if A["blocks"] > 0:
            ratios.append(C["blocks"] / A["blocks"])
        if A["status"] == "UNRESOLVED":
            conditional.append(C["blocks"] / A["blocks"])
ratios.sort()
chk("317 comparable validation replicates", len(ratios) == 317, str(len(ratios)))
chk("median spend ratio is exactly 1.000", q(ratios, 0.5) == 1.0)
chk("mean spend ratio 1.0105",
    abs(sum(ratios) / len(ratios) - 1.0105) < 5e-5,
    f"{sum(ratios)/len(ratios):.4f}")
chk("q99 1.386 and max 2.022",
    abs(q(ratios, 0.99) - 1.386) < 5e-4 and abs(max(ratios) - 2.022) < 5e-4)
chk("spend identical on 97.2 % of replicates",
    abs(sum(x == 1.0 for x in ratios) / len(ratios) - 0.972) < 5e-4)
chk("9 third-state cases, mean 1.37, worst 2.02",
    len(conditional) == 9
    and abs(sum(conditional) / 9 - 1.370) < 5e-3
    and abs(max(conditional) - 2.022) < 5e-3)
chk("all 9 abandoned routes were rescued to ATTAINED",
    all(r["outcomes"]["C_staged_safety_1.00"]["status"] == "ATTAINED"
        for cell in val["cells"] for r in cell["replicates"]
        if r["outcomes"]["A_oneshot_one_topup"]["status"] == "UNRESOLVED"))

c5 = next(x for x in val["cells"] if x["cell"] == "C5")
a5 = next(x for x in c5["rules"] if x["rule"] == "A_oneshot_one_topup")
s5 = next(x for x in c5["rules"] if x["rule"] == "C_staged_safety_1.00")
chk("C5 control: baseline 5 UNRESOLVED with the cap never binding, staged 59/59",
    (a5["unresolved"], a5["precision_limited"], s5["attained"], s5["unresolved"])
    == (5, 0, 59, 0))

mults, oracle, attained, n = [], [], 0, 0
for cell in ct["cells"]:
    for r in cell["replicates"]:
        o = r["outcomes"]["C_staged_safety_1.00"]
        mults.append(o["block_multiplier"])
        n += 1
        attained += o["status"] == "ATTAINED"
        if r["oracle_multiplier"] is not None:
            oracle.append(r["oracle_multiplier"])
mults.sort(); oracle.sort()
chk("cost tail attained 127 of 144 at the 16x cap",
    (attained, n) == (127, 144), f"{attained}/{n}")
chk("cost tail q95 spend 8.33 against oracle q95 1.67",
    abs(q(mults, 0.95) - 8.3333) < 1e-3 and abs(q(oracle, 0.95) - 1.6667) < 1e-3)
chk("overshoot versus the oracle is 5.0x at q95",
    abs(q(mults, 0.95) / q(oracle, 0.95) - 5.0) < 0.05)

total = (cal["total_cpu_seconds"] / 3600 + des["cpu_hours"]
         + val["cpu_hours"] + ct["cpu_hours"])
chk("cumulative pilot CPU 1.1983 h, inside the 2.0 h cap",
    abs(total - 1.1983) < 5e-4 and total < 2.0, f"{total:.4f}")
chk("no STOP rule fired in any phase",
    des["stopped"] is None and val["stopped"] is None and ct["stopped"] is None)

expected = {"C1": 0.02522, "C2": 0.08986, "C3": 0.02631,
            "C4": 0.1471, "C5": 0.005528, "C6": 0.01858}
chk("r*_pilot matches the preregistered table",
    all(abs(x["r_star_pilot"] - expected[x["cell"]]) < 1e-9 for x in cal["cells"]))
chk("every cell's block means have Hill alpha > 2",
    all(x["by_m"]["1"]["hill_alpha_block_means"] > 2 for x in cal["cells"]))

for token in ("282 / 282", "0.9894", "0.9450", "1.0105", "127 / 144",
              "8.33", "1.67", "1.1983", "2.022", "1.37"):
    chk(f"report cites {token!r}", token in txt)

print()
if failures:
    print(f"{len(failures)} CHECK(S) FAILED")
    sys.exit(1)
print("ALL CHECKS PASS")
