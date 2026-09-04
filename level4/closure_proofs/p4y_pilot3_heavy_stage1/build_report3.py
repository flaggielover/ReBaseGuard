#!/usr/bin/env python3
"""Apply the frozen Pilot-3 selection and acceptance criteria.

Every threshold, weight, ordering and tie-break is fixed in
PILOT3_PREREGISTRATION.md and `src/p4y_pilot3/strata3.py`.  Selection reads
DESIGN only; validation is reported and never re-selects.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT.parent / "p4y_pilot2_final_prefreeze" / "src"))
sys.path.insert(0, str(ROOT.parent / "p4y_precision_governance_pilot" / "src"))

from p4y_pilot.stats import clopper_pearson_lower  # noqa: E402
from p4y_pilot3.projection3 import project  # noqa: E402
from p4y_pilot3.strata3 import (  # noqa: E402
    ATTAINMENT_FLOOR_MIXTURE, BETA, BMIN_SELECTABLE, CAP_MULTIPLIERS, DELTA,
    HEAVY_STRATUM_ATTAINMENT_FLOOR, HEAVY_STRATUM_PL_CEILING,
    KAPPA_CANDIDATES, N_STRATA_TOTAL, PRECISION_LIMITED_CEILING, PRIMARY_CELLS,
    stratum,
)
from p4y_pilot3.ucb import UCB_BASELINE, UCB_CANDIDATES  # noqa: E402

R = ROOT / "results"
#: Frozen simplicity order for the tie-break: closed form beats resampling.
SIMPLICITY = {"chi2": 0, "t_squared": 1, "bootstrap": 2, UCB_BASELINE: 0}


def load(name):
    p = R / f"{name}.json"
    return json.loads(p.read_text()) if p.exists() else None


def q(values, p):
    v = sorted(values)
    return v[min(len(v) - 1, math.ceil(p * len(v)) - 1)] if v else math.nan


def stratum_stats(phase, bmin, ucb, kname, mult):
    """Per (cell, stratum) outcome for one candidate.

    Ordinary strata are untouched by the heavy rule: they are always evaluated
    at their own historical reference with the point estimate, whatever Bmin
    and UCB the heavy rule uses.
    """
    key_heavy = f"{bmin}|{ucb}|{kname}"
    cap = f"{mult:g}"
    out = {}
    for cell in phase["cells"]:
        if not cell["primary"]:
            continue
        k = key_heavy if cell["heavy"] else \
            f"{cell['b_ref_ordinary']}|{UCB_BASELINE}|{kname}"
        n = valid = att = lim = 0
        mults, cov, cov_pt = [], 0, 0
        for rep in cell["replicates"]:
            c = rep["candidates"].get(k)
            if c is None:
                continue
            o = c["caps"][cap]
            n += 1
            valid += bool(o["valid"])
            att += o["valid"] and o["status"] == "ATTAINED"
            lim += o["valid"] and o["status"] == "PRECISION_LIMITED"
            if math.isfinite(o["block_multiplier"]):
                mults.append(o["block_multiplier"])
            cov += bool(c["stage1_covers_requirement"])
            cov_pt += bool(c["stage1_point_covers_requirement"])
        out[f"{cell['cell']}/{cell['stratum']}"] = {
            "cell": cell["cell"], "stratum": cell["stratum"],
            "heavy": cell["heavy"], "weight": cell["weight"],
            "replicates": n, "valid": valid, "attained": att,
            "precision_limited": lim, "invalid": n - valid,
            "valid_rate": valid / n if n else math.nan,
            "attainment_rate": att / n if n else math.nan,
            "precision_limited_rate": lim / n if n else math.nan,
            "stage1_coverage": cov / n if n else math.nan,
            "stage1_coverage_point_estimate": cov_pt / n if n else math.nan,
            "mean_multiplier": sum(mults) / len(mults) if mults else math.nan,
            "q95_multiplier": q(mults, 0.95), "multipliers": mults,
        }
    return out


def summarise_candidate(phase, bmin, ucb, kname, mult):
    st = stratum_stats(phase, bmin, ucb, kname, mult)
    tot_w = sum(v["weight"] for v in st.values())
    mix = lambda f: sum(v["weight"] * v[f] for v in st.values()) / tot_w
    n = sum(v["replicates"] for v in st.values())
    valid = sum(v["valid"] for v in st.values())
    heavy = {k: v for k, v in st.items() if v["heavy"]}
    hm = [m for v in heavy.values() for m in v["multipliers"]]
    return {
        "bmin": bmin, "ucb": ucb, "kappa": kname, "cap_multiplier": mult,
        "replicates": n, "valid": valid, "invalid": n - valid,
        "valid_rate": valid / n if n else math.nan,
        "valid_lower": clopper_pearson_lower(valid, n, BETA),
        "mixture_attainment": mix("attainment_rate"),
        "mixture_precision_limited": mix("precision_limited_rate"),
        "min_heavy_attainment": min((v["attainment_rate"] for v in heavy.values()),
                                    default=math.nan),
        "max_heavy_precision_limited": max(
            (v["precision_limited_rate"] for v in heavy.values()), default=math.nan),
        "heavy_mean_multiplier": sum(hm) / len(hm) if hm else math.nan,
        "heavy_q95_multiplier": q(hm, 0.95),
        "heavy_stage1_coverage": (sum(v["weight"] * v["stage1_coverage"]
                                      for v in heavy.values())
                                  / sum(v["weight"] for v in heavy.values())),
        "heavy_stage1_coverage_point": (
            sum(v["weight"] * v["stage1_coverage_point_estimate"]
                for v in heavy.values())
            / sum(v["weight"] for v in heavy.values())),
        "per_stratum": st,
    }


def with_projection(cand):
    kappa = KAPPA_CANDIDATES[cand["kappa"]]
    if not (math.isfinite(cand["heavy_mean_multiplier"])
            and math.isfinite(cand["heavy_q95_multiplier"])):
        return {**cand, "projection": None}
    p = project(bmin=cand["bmin"], kappa=kappa,
                heavy_alloc_multiplier=cand["heavy_mean_multiplier"],
                heavy_alloc_tail_multiplier=cand["heavy_q95_multiplier"])
    return {**cand, "projection": p}


def criteria(cand):
    p = cand.get("projection")
    c = {
        "1_valid_lower_bound": cand["valid_lower"] >= DELTA,
        "2_mixture_attainment": cand["mixture_attainment"] >= ATTAINMENT_FLOOR_MIXTURE,
        "3_mixture_precision_limited":
            cand["mixture_precision_limited"] <= PRECISION_LIMITED_CEILING,
        "4_every_heavy_stratum":
            (cand["min_heavy_attainment"] >= HEAVY_STRATUM_ATTAINMENT_FLOOR
             and cand["max_heavy_precision_limited"] <= HEAVY_STRATUM_PL_CEILING),
        "5_no_invalid_disposition": cand["invalid"] == 0,
        "8_total_cpu": bool(p) and p["total_cap_feasibility"] == "PASS",
        "9_max_config_cpu": bool(p) and p["per_config_cap_feasibility"] == "PASS",
    }
    return c, all(c.values())


def select(design):
    cands, log = [], []
    for bmin in BMIN_SELECTABLE:
        for ucb in UCB_CANDIDATES:
            for kname in KAPPA_CANDIDATES:
                for mult in CAP_MULTIPLIERS:
                    cand = with_projection(
                        summarise_candidate(design, bmin, ucb, kname, mult))
                    c, ok = criteria(cand)
                    cand["criteria"], cand["qualifies"] = c, ok
                    cands.append(cand)
    qual = [c for c in cands if c["qualifies"]]
    log.append(f"candidates evaluated: {len(cands)}; qualifying: {len(qual)}")
    if not qual:
        best = max(cands, key=lambda c: sum(c["criteria"].values()))
        log.append("NO QUALIFYING CANDIDATE")
        log.append("closest: " + json.dumps(
            {k: v for k, v in best.items()
             if k in ("bmin", "ucb", "kappa", "cap_multiplier")})
            + " failing " + ", ".join(k for k, v in best["criteria"].items() if not v))
        return None, cands, log
    qual.sort(key=lambda c: (
        round(c["projection"]["projected_total_conservative"], 9),
        round(c["projection"]["projected_max_config_conservative"], 9),
        round(c["mixture_precision_limited"], 9),
        SIMPLICITY[c["ucb"]],
        c["bmin"]))
    s = qual[0]
    log.append(f"SELECTED bmin={s['bmin']} ucb={s['ucb']} kappa={s['kappa']} "
               f"cap={s['cap_multiplier']:g}x  "
               f"total_cons={s['projection']['projected_total_conservative']:.2f}h "
               f"maxcfg_cons={s['projection']['projected_max_config_conservative']:.2f}h")
    return s, cands, log


def main() -> int:
    design, validation = load("design"), load("validation")
    bench = load("benchmark")
    if design is None:
        raise SystemExit("run design first")
    sel, cands, log = select(design)
    out = {"schema": "rebaseguard.p4y-pilot3-report.v1", "binding": False,
           "delta": DELTA, "beta": BETA, "selection_log": log,
           "selected": ({k: sel[k] for k in
                         ("bmin", "ucb", "kappa", "cap_multiplier")}
                        if sel else None),
           "design_candidates": [
               {k: v for k, v in c.items() if k != "per_stratum"}
               for c in cands],
           "design_selected_full": sel,
           "benchmark_stopped": bench["stopped"] if bench else None,
           "design_stopped": design["stopped"]}
    print("\n".join(log))

    if validation:
        out["validation_stopped"] = validation["stopped"]
        out["cumulative_cpu_hours"] = validation.get("cumulative_cpu_hours")
        curve = []
        for bmin in BMIN_SELECTABLE:
            for ucb in UCB_CANDIDATES:
                for kname in KAPPA_CANDIDATES:
                    for mult in CAP_MULTIPLIERS:
                        c = with_projection(summarise_candidate(
                            validation, bmin, ucb, kname, mult))
                        cr, ok = criteria(c)
                        c["criteria"], c["qualifies"] = cr, ok
                        curve.append(c)
        out["validation_curve"] = [
            {k: v for k, v in c.items() if k != "per_stratum"} for c in curve]
        if sel:
            v = next(c for c in curve
                     if (c["bmin"], c["ucb"], c["kappa"], c["cap_multiplier"])
                     == (sel["bmin"], sel["ucb"], sel["kappa"],
                         sel["cap_multiplier"]))
            out["validation_selected_full"] = v
            cr, ok = criteria(v)
            out["validation_criteria"], out["validation_all_pass"] = cr, ok
            p = v["projection"]
            print(f"\nVALIDATION of the selected candidate")
            print(f"  valid disposition {v['valid']}/{v['replicates']} = "
                  f"{v['valid_rate']:.4f}  CP lower {v['valid_lower']:.4f}")
            print(f"  mixture attainment {v['mixture_attainment']:.4f} "
                  f"(floor {ATTAINMENT_FLOOR_MIXTURE})")
            print(f"  mixture PRECISION_LIMITED {v['mixture_precision_limited']:.4f} "
                  f"(ceiling {PRECISION_LIMITED_CEILING})")
            print(f"  min heavy attainment {v['min_heavy_attainment']:.4f} "
                  f"(floor {HEAVY_STRATUM_ATTAINMENT_FLOOR})")
            print(f"  max heavy PL {v['max_heavy_precision_limited']:.4f} "
                  f"(ceiling {HEAVY_STRATUM_PL_CEILING})")
            print(f"  stage-1 coverage UCB {v['heavy_stage1_coverage']:.4f} "
                  f"vs point {v['heavy_stage1_coverage_point']:.4f}")
            print(f"  projected total {p['projected_total_central']:.2f} / "
                  f"{p['projected_total_conservative']:.2f} h "
                  f"(accept <= {p['accept_total_hours']:.0f})")
            print(f"  projected maxcfg {p['projected_max_config_central']:.2f} / "
                  f"{p['projected_max_config_conservative']:.2f} h "
                  f"(accept <= {p['accept_per_config_hours']:.0f})")
            for k, ok_ in cr.items():
                print(f"  {k}: {'PASS' if ok_ else 'FAIL'}")
            print(f"  ALL FROZEN CRITERIA: {'PASS' if ok else 'FAIL'}")

    (R / "report.json").write_text(json.dumps(out, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
