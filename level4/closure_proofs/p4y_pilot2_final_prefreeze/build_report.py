#!/usr/bin/env python3
"""Apply the frozen Pilot-2 selection and acceptance criteria.

Every threshold, every ordering and every tie-break is fixed in
PILOT2_PREREGISTRATION.md and in `src/p4y_pilot2/strata.py`.  This module
contains no free choice: it reads design.json, selects (kappa, cap), reads
validation.json, and evaluates the frozen pass criteria A-L.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT.parent / "p4y_precision_governance_pilot" / "src"))

from p4y_pilot.stats import clopper_pearson_lower  # noqa: E402
from p4y_pilot2.project import project  # noqa: E402
from p4y_pilot2.strata import (  # noqa: E402
    ATTAINMENT_FLOOR_POOLED, ATTAINMENT_FLOOR_STRATUM, BETA, CAP_MULTIPLIERS,
    DELTA, KAPPA_CANDIDATES, PILOT2_CPU_CAP_HOURS, PRECISION_LIMITED_CEILING,
    PRIMARY_CELLS,
)

R = ROOT / "results"


def load(name):
    p = R / f"{name}.json"
    return json.loads(p.read_text()) if p.exists() else None


def cells_of(phase, primary_only=True):
    return [c for c in phase["cells"] if c["primary"] or not primary_only]


def collect(phase, kname, mult, primary_only=True):
    """Every replicate outcome for one (kappa, cap multiplier)."""
    key = f"{mult:g}"
    rows = []
    for cell in cells_of(phase, primary_only):
        for rep in cell["replicates"]:
            o = rep["kappas"][kname]["caps"][key]
            rows.append({"cell": cell["cell"], "stratum": cell["stratum"],
                         "b1_nominal": cell["b1_nominal"], **o})
    return rows


def tally(rows):
    n = len(rows)
    valid = sum(r["valid"] for r in rows)
    att = sum(r["valid"] and r["status"] == "ATTAINED" for r in rows)
    lim = sum(r["valid"] and r["status"] == "PRECISION_LIMITED" for r in rows)
    mult = sorted(r["block_multiplier"] for r in rows)
    q = lambda p: mult[min(len(mult) - 1, math.ceil(p * len(mult)) - 1)] if mult else math.nan
    return {
        "replicates": n, "valid": valid, "attained": att, "precision_limited": lim,
        "invalid": n - valid,
        "valid_rate": valid / n if n else math.nan,
        "valid_lower": clopper_pearson_lower(valid, n, BETA),
        "attainment_rate": att / n if n else math.nan,
        "attainment_lower": clopper_pearson_lower(att, n, BETA),
        "precision_limited_rate": lim / n if n else math.nan,
        "mean_multiplier": sum(mult) / n if n else math.nan,
        "q50_multiplier": q(0.50), "q90_multiplier": q(0.90),
        "q95_multiplier": q(0.95),
        "max_multiplier": max(mult) if mult else math.nan,
        "invalid_reasons": sorted({x for r in rows for x in r["reasons"]})[:6],
    }


def per_stratum(rows):
    out = {}
    for r in rows:
        out.setdefault(f"{r['cell']}/{r['stratum']}", []).append(r)
    return {k: tally(v) for k, v in out.items()}


def select(design) -> dict:
    """FROZEN cap-selection then kappa-selection, on DESIGN only."""
    log, per_kappa = [], {}
    for kname in KAPPA_CANDIDATES:
        chosen = None
        for mult in CAP_MULTIPLIERS:
            rows = collect(design, kname, mult)
            t = tally(rows)
            st = per_stratum(rows)
            ok_valid = t["valid_rate"] == 1.0
            ok_pooled = t["attainment_rate"] >= ATTAINMENT_FLOOR_POOLED
            ok_stratum = all(s["attainment_rate"] >= ATTAINMENT_FLOOR_STRATUM
                             for s in st.values())
            log.append(
                f"{kname} cap={mult:g}x  valid={t['valid_rate']:.4f} "
                f"att={t['attainment_rate']:.4f} "
                f"min_stratum_att={min(s['attainment_rate'] for s in st.values()):.4f} "
                f"meanX={t['mean_multiplier']:.3f} -> "
                + ("ELIGIBLE" if (ok_valid and ok_pooled and ok_stratum)
                   else "no"))
            if ok_valid and ok_pooled and ok_stratum and chosen is None:
                chosen = {"kappa": kname, "multiplier": mult, "design": t,
                          "design_per_stratum": st}
        per_kappa[kname] = chosen
        if chosen is None:
            log.append(f"{kname}: NO SELECTABLE CAP in the frozen grid")
    viable = [v for v in per_kappa.values() if v]
    if not viable:
        log.append("NO KAPPA HAS A SELECTABLE CAP")
        return {"selected": None, "log": log, "per_kappa": per_kappa}
    viable.sort(key=lambda v: (round(v["design"]["mean_multiplier"], 9),
                               v["multiplier"],
                               list(KAPPA_CANDIDATES).index(v["kappa"])))
    log.append(f"SELECTED kappa={viable[0]['kappa']} "
               f"cap={viable[0]['multiplier']:g}x")
    return {"selected": viable[0], "log": log, "per_kappa": per_kappa}


def main() -> int:
    design, validation = load("design"), load("validation")
    calib = load("calibration")
    if design is None:
        raise SystemExit("run design first")
    sel = select(design)
    out = {"schema": "rebaseguard.p4y-pilot2-report.v1", "binding": False,
           "delta": DELTA, "beta": BETA,
           "selection_log": sel["log"],
           "selected": {k: v for k, v in (sel["selected"] or {}).items()
                        if k in ("kappa", "multiplier")} or None,
           "design_stopped": design["stopped"],
           "calibration_stopped": calib["stopped"] if calib else None}
    print("\n".join(sel["log"]))

    # full kappa x cap curve on design, for the negative-results section
    out["design_curve"] = {
        kname: {f"{m:g}": tally(collect(design, kname, m))
                for m in CAP_MULTIPLIERS}
        for kname in KAPPA_CANDIDATES}

    if validation and sel["selected"]:
        kname = sel["selected"]["kappa"]
        mult = sel["selected"]["multiplier"]
        rows = collect(validation, kname, mult)
        t = tally(rows)
        st = per_stratum(rows)
        out["validation_curve"] = {
            kn: {f"{m:g}": tally(collect(validation, kn, m))
                 for m in CAP_MULTIPLIERS} for kn in KAPPA_CANDIDATES}
        out["primary"] = t
        out["primary_per_stratum"] = st
        rob = collect(validation, kname, mult, primary_only=False)
        rob = [r for r in rob if r["cell"] not in PRIMARY_CELLS]
        out["robustness_route_b"] = tally(rob) if rob else None
        out["validation_stopped"] = validation["stopped"]
        out["cumulative_cpu_hours"] = validation.get("cumulative_cpu_hours")

        baseline = 1.0          # a run that stops at its own stage 1
        proj = project(mean_multiplier=t["mean_multiplier"],
                       tail_multiplier=t["q95_multiplier"],
                       baseline_multiplier=baseline)
        out["projection"] = proj
        out["acceptance"] = {
            "B_valid_disposition_lower_bound": {
                "value": t["valid_lower"], "target": DELTA,
                "met": t["valid_lower"] >= DELTA},
            "C_attainment": {
                "rate": t["attainment_rate"],
                "lower": t["attainment_lower"],
                "rate_target": ATTAINMENT_FLOOR_POOLED,
                "lower_target": 0.90,
                "precision_limited_rate": t["precision_limited_rate"],
                "precision_limited_ceiling": PRECISION_LIMITED_CEILING,
                "met": (t["attainment_rate"] >= ATTAINMENT_FLOOR_POOLED
                        and t["attainment_lower"] >= 0.90
                        and t["precision_limited_rate"] <= PRECISION_LIMITED_CEILING)},
            "F_total_cpu": {"value": proj["projected_total_conservative"],
                            "limit": proj["accept_total_hours"],
                            "met": proj["total_cap_feasibility"] == "PASS"},
            "G_max_config_cpu": {"value": proj["projected_max_config_conservative"],
                                 "limit": proj["accept_per_config_hours"],
                                 "met": proj["per_config_cap_feasibility"] == "PASS"},
            "K_no_stop": {"met": not any([calib["stopped"] if calib else None,
                                          design["stopped"],
                                          validation["stopped"]])},
        }
        print(f"\nPRIMARY  kappa={kname} cap={mult:g}x")
        print(f"  valid disposition {t['valid']}/{t['replicates']} = "
              f"{t['valid_rate']:.4f}  CP lower {t['valid_lower']:.4f} "
              f"(target {DELTA})")
        print(f"  ATTAINED          {t['attained']}/{t['replicates']} = "
              f"{t['attainment_rate']:.4f}  CP lower {t['attainment_lower']:.4f}")
        print(f"  PRECISION_LIMITED {t['precision_limited']}/{t['replicates']} = "
              f"{t['precision_limited_rate']:.4f} "
              f"(ceiling {PRECISION_LIMITED_CEILING})")
        print(f"  block multiplier  mean {t['mean_multiplier']:.3f} "
              f"q95 {t['q95_multiplier']:.3f} max {t['max_multiplier']:.3f}")
        print(f"  projected total   {proj['projected_total_central']:.2f} h central / "
              f"{proj['projected_total_conservative']:.2f} h conservative "
              f"(accept <= {proj['accept_total_hours']:.1f})")
        print(f"  projected maxcfg  {proj['projected_max_config_central']:.2f} h / "
              f"{proj['projected_max_config_conservative']:.2f} h "
              f"(accept <= {proj['accept_per_config_hours']:.1f})")
        for k, v in out["acceptance"].items():
            print(f"  {k}: {'MET' if v['met'] else 'NOT MET'}")

    (R / "report.json").write_text(json.dumps(out, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
