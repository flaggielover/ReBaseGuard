#!/usr/bin/env python3
"""Apply the predeclared selection criterion and build the comparison tables.

Selection (PILOT_PREREGISTRATION.md sec. 7), applied to the DESIGN phase only:
among rules that cannot reach the third state and whose pooled design
attainment fraction is >= delta, take the smallest mean block multiplier.
Ties: smaller worst-case multiplier, then fewer free parameters.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from p4y_pilot.config import B1_NOMINAL, BETA, DELTA  # noqa: E402
from p4y_pilot.rules import ATTAINED, CANDIDATES, PRECISION_LIMITED, UNRESOLVED  # noqa: E402
from p4y_pilot.stats import clopper_pearson_lower  # noqa: E402

FREE_PARAMETERS = {r.name: (0 if r.adaptive else (0 if r.safety == 1.0 else 1))
                   + (0 if math.isinf(r.max_stages) else 1)
                   for r in CANDIDATES}


def pool_rule(phase: dict, name: str) -> dict:
    """Pool one rule's outcomes over every cell in a phase."""
    att = lim = unres = n = 0
    mults, worst = [], 0.0
    per_cell = []
    for cell in phase["cells"]:
        s = next(x for x in cell["rules"] if x["rule"] == name)
        att += s["attained"]; lim += s["precision_limited"]
        unres += s["unresolved"]; n += s["replicates"]
        mults.append(s["mean_block_multiplier"])
        worst = max(worst, s["max_block_multiplier"])
        per_cell.append({
            "cell": cell["cell"], "config": cell["config"],
            "route": cell["route"], "heavy": cell["heavy"],
            "attained": s["attained"], "replicates": s["replicates"],
            "precision_limited": s["precision_limited"],
            "unresolved": s["unresolved"],
            "p_attain": s["p_attain_all"],
            "lower_bound": s["lower_bound_all"],
            "mean_block_multiplier": s["mean_block_multiplier"],
            "max_block_multiplier": s["max_block_multiplier"],
        })
    resolvable = n - lim
    return {
        "rule": name, "replicates": n,
        "attained": att, "precision_limited": lim, "unresolved": unres,
        "third_state_possible": next(
            r for r in CANDIDATES if r.name == name).max_stages != math.inf,
        "p_attain": att / n if n else math.nan,
        "lower_bound": clopper_pearson_lower(att, n, BETA),
        "p_attain_within_cap": att / resolvable if resolvable else math.nan,
        "lower_bound_within_cap": (clopper_pearson_lower(att, resolvable, BETA)
                                   if resolvable else 0.0),
        "mean_block_multiplier": sum(mults) / len(mults) if mults else math.nan,
        "max_block_multiplier": worst,
        "free_parameters": FREE_PARAMETERS[name],
        "per_cell": per_cell,
    }


def select(design: dict) -> tuple[str, list[dict], list[str]]:
    pooled = [pool_rule(design, r.name) for r in CANDIDATES]
    log = []
    eligible = []
    for p in pooled:
        why = []
        if p["third_state_possible"]:
            why.append("admits the third state")
        if p["p_attain"] < DELTA:
            why.append(f"design attainment {p['p_attain']:.3f} < delta {DELTA}")
        if why:
            log.append(f"{p['rule']}: EXCLUDED -- " + "; ".join(why))
        else:
            log.append(f"{p['rule']}: eligible, "
                       f"mean multiplier {p['mean_block_multiplier']:.3f}")
            eligible.append(p)
    if not eligible:
        return "", pooled, log + ["NO ELIGIBLE RULE"]
    eligible.sort(key=lambda p: (round(p["mean_block_multiplier"], 6),
                                 round(p["max_block_multiplier"], 6),
                                 p["free_parameters"], p["rule"]))
    log.append(f"SELECTED: {eligible[0]['rule']}")
    return eligible[0]["rule"], pooled, log


def main() -> int:
    design = json.loads((ROOT / "results" / "design.json").read_text())
    chosen, design_pooled, log = select(design)
    out = {"schema": "rebaseguard.p4y-pilot-report.v1", "binding": False,
           "delta": DELTA, "beta": BETA, "b1_nominal": B1_NOMINAL,
           "selection_log": log, "selected_rule": chosen,
           "design_pooled": design_pooled,
           "design_cpu_hours": design["cpu_hours"],
           "design_stopped": design["stopped"]}
    print("\n".join(log))

    vpath = ROOT / "results" / "validation.json"
    if vpath.exists():
        val = json.loads(vpath.read_text())
        out["validation_pooled"] = [pool_rule(val, r.name) for r in CANDIDATES]
        out["validation_cpu_hours"] = val["cpu_hours"]
        out["validation_stopped"] = val["stopped"]
        out["cumulative_cpu_hours"] = val["cumulative_pilot_cpu_hours"]
        sel = next(p for p in out["validation_pooled"] if p["rule"] == chosen)
        out["primary_endpoint"] = {
            "rule": chosen, "replicates": sel["replicates"],
            "attained": sel["attained"],
            "p_attain": sel["p_attain"],
            "clopper_pearson_lower": sel["lower_bound"],
            "target": DELTA,
            "met": sel["lower_bound"] >= DELTA,
        }
        out["secondary_endpoint"] = {
            "min_cell_lower_bound": min(c["lower_bound"] for c in sel["per_cell"]),
            "threshold": 0.90,
            "met": min(c["lower_bound"] for c in sel["per_cell"]) >= 0.90,
            "per_cell": sel["per_cell"],
        }
        print(f"\nPRIMARY: {chosen} attained {sel['attained']}/{sel['replicates']}"
              f"  p_attain={sel['p_attain']:.4f}"
              f"  CP lower={sel['lower_bound']:.4f}  target={DELTA}"
              f"  -> {'MET' if out['primary_endpoint']['met'] else 'NOT MET'}")
        print(f"SECONDARY: min per-cell lower bound = "
              f"{out['secondary_endpoint']['min_cell_lower_bound']:.4f}"
              f"  -> {'MET' if out['secondary_endpoint']['met'] else 'NOT MET'}")
    (ROOT / "results" / "report.json").write_text(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
