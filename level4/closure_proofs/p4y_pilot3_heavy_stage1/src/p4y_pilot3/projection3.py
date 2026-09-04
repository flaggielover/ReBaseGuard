"""Fresh full-scope P4Y cost projection on the REAL production mixture.

Cost basis is P4X's own measured execution -- `cost_ledger.json`, 24.749
CPU-hours with 18.599 on `frozen/cusum@5/t1p5`.  That is measured CPU, i.e.
cost metadata; no P4X correspondence outcome, discrepancy, z or pass/fail is
read here, and none is needed to project compute.

The projection is decomposed as brief section 17 requires:

    reference expansion   the extra heavy-tail reference blocks Bmin buys
    stage-1 allocation    the UCB-sized initial allocation
    staged top-ups        whatever the staged rule adds afterwards
"""

from __future__ import annotations

import json
from pathlib import Path

from .strata3 import (
    ACCEPT_PER_CONFIG_HOURS, ACCEPT_TOTAL_HOURS, FUTURE_PER_CONFIG_CAP_HOURS,
    FUTURE_TOTAL_CAP_HOURS, PRODUCTION_BLOCK_HEAVY, REQUIRED_RESERVE,
)

_P4X = Path("/Users/suzhe/ReBaseGuard-p4x/level4/closure_proofs/"
            "p4x_generalization_boundary")


def load_basis() -> dict:
    """Per-(configuration, route) measured cost, apportioned from the ledger.

    The ledger records measured CPU per CONFIGURATION.  Routes are apportioned
    within a configuration in proportion to `blocks * block_size * rate` from
    the frozen plan, which for the heavy configurations puts >99 % on Route B
    -- the ratio that matters.  Apportionment never changes a configuration
    total, so the max-configuration figure is exact.
    """
    cp = json.loads((_P4X / "checkpoint_a" / "results"
                     / "checkpoint_a.json").read_text())
    led = json.loads((_P4X / "production" / "results"
                      / "c2_cell_ledger.json").read_text())
    cost = json.loads((_P4X / "production" / "results"
                       / "cost_ledger.json").read_text())

    final = {}
    for x in led["cells"]:
        for r in ("route_a", "route_b"):
            k = (x["config"], r)
            final.setdefault(k, (x[r]["blocks"], x[r]["block_size"]))

    rows = {}
    for p in cp["production_plan"]:
        bs = p["minimum_block_paths"]
        for r in ("route_a", "route_b"):
            k = (p["config"], r)
            if k in rows:
                continue
            d = p[r]
            blocks, fbs = final[k]
            rows[k] = {
                "config": p["config"], "route": r, "family": p["family"],
                "heavy": p["heavy_tailed"], "block_size": fbs,
                "rate_s_per_1e6": d["seconds_per_1e6_paths"],
                "b_ref_hist": d["reference_paths"] / bs,
                "b1_hist": d["stage1_paths"] / bs,
                "final_blocks": blocks,
                "share_raw": blocks * fbs * d["seconds_per_1e6_paths"],
            }

    by_cfg = {}
    for k, v in rows.items():
        by_cfg.setdefault(v["config"], []).append(k)
    measured = cost["per_configuration_cpu_hours"]
    for cfg, keys in by_cfg.items():
        tot = sum(rows[k]["share_raw"] for k in keys) or 1.0
        for k in keys:
            rows[k]["measured_cpu_hours"] = (measured[cfg]
                                             * rows[k]["share_raw"] / tot)
            rows[k]["cpu_per_block"] = (rows[k]["measured_cpu_hours"]
                                        / max(rows[k]["final_blocks"], 1))
    return {"rows": rows, "measured_total": cost["total_cpu_hours"],
            "measured_max_config": cost["max_configuration_cpu_hours"],
            "per_configuration": measured}


def heavy_requirements(kappa: float) -> dict:
    """Blocks each production heavy stratum needs, under a given kappa.

    Derived from P4X's stage-1 achieved relative SE -- PRECISION metadata, not
    a correspondence outcome: no discrepancy, no z, no pass/fail is read.  It
    is used ONLY for the cost projection that brief section 17 requires, never
    to select a rule, a kappa, a cap or a Bmin.

    Cross-check: at kappa = 0.3197 this basis sums to 13 363 blocks against
    the 13 367 P4X actually executed.  The four-block gap is exactly the
    sharding over-execution defect Pilot-1 repaired, which is a strong
    independent confirmation that the basis is the right one.
    """
    import math

    plan = json.loads((_P4X / "production" / "results"
                       / "c2_stage2_plan.json").read_text())
    out = {}
    for row in plan["plans"]:
        if "t1p5" not in row["config"]:
            continue
        b1 = row["stage1_N"] / PRODUCTION_BLOCK_HEAVY
        rel = row["stage1_SE_worst_relative"]
        need = (math.ceil(b1 * (rel / 0.010823) ** (1.0 / kappa))
                if rel > 0.010823 else math.ceil(b1))
        out[(row["config"], row["route"])] = need
    return out


def project(*, bmin: int, kappa: float, heavy_alloc_multiplier: float,
            heavy_alloc_tail_multiplier: float) -> dict:
    """Project P4Y under the frozen rule.

    ``heavy_alloc_multiplier`` is measured blocks-used / B_required for the
    heavy strata under the selected candidate; the tail version is its q95.
    Ordinary strata are untouched by the heavy rule and keep their measured
    P4X cost.
    """
    basis = load_basis()
    rows = basis["rows"]
    need = heavy_requirements(kappa)
    out_rows, per_cfg_central, per_cfg_cons = [], {}, {}
    ref_expansion = stage_alloc_central = stage_alloc_cons = ordinary = 0.0

    for k, v in rows.items():
        cpb = v["cpu_per_block"]
        if v["heavy"]:
            # reference expansion: from the historical B_ref up to Bmin
            extra_ref = max(0.0, bmin - v["b_ref_hist"])
            ref_h = extra_ref * (PRODUCTION_BLOCK_HEAVY / v["block_size"]) * cpb
            base_req = need[(v["config"], v["route"])]
            alloc_c = base_req * heavy_alloc_multiplier * cpb
            alloc_t = base_req * heavy_alloc_tail_multiplier * cpb
            ref_expansion += ref_h
            stage_alloc_central += alloc_c
            stage_alloc_cons += alloc_t
            c, t = ref_h + alloc_c, ref_h + alloc_t
        else:
            ordinary += v["measured_cpu_hours"]
            c = t = v["measured_cpu_hours"]
        per_cfg_central[v["config"]] = per_cfg_central.get(v["config"], 0) + c
        per_cfg_cons[v["config"]] = per_cfg_cons.get(v["config"], 0) + t
        out_rows.append({**{q: v[q] for q in ("config", "route", "heavy")},
                         "central_cpu_hours": c, "conservative_cpu_hours": t})

    total_c = sum(per_cfg_central.values())
    total_t = sum(per_cfg_cons.values())
    max_c = max(per_cfg_central.values())
    max_t = max(per_cfg_cons.values())
    return {
        "bmin": bmin,
        "kappa": kappa,
        "heavy_requirement_blocks": sum(need.values()),
        "heavy_alloc_multiplier": heavy_alloc_multiplier,
        "heavy_alloc_tail_multiplier": heavy_alloc_tail_multiplier,
        "basis_measured_total": basis["measured_total"],
        "basis_measured_max_config": basis["measured_max_config"],
        "decomposition": {
            "heavy_reference_expansion": ref_expansion,
            "heavy_stage1_and_topups_central": stage_alloc_central,
            "heavy_stage1_and_topups_conservative": stage_alloc_cons,
            "ordinary_unchanged": ordinary,
        },
        "projected_total_central": total_c,
        "projected_total_conservative": total_t,
        "projected_max_config_central": max_c,
        "projected_max_config_conservative": max_t,
        "max_config_central_name": max(per_cfg_central, key=per_cfg_central.get),
        "future_total_cap": FUTURE_TOTAL_CAP_HOURS,
        "future_per_config_cap": FUTURE_PER_CONFIG_CAP_HOURS,
        "required_reserve": REQUIRED_RESERVE,
        "accept_total_hours": ACCEPT_TOTAL_HOURS,
        "accept_per_config_hours": ACCEPT_PER_CONFIG_HOURS,
        "total_cap_feasibility": "PASS" if total_t <= ACCEPT_TOTAL_HOURS else "FAIL",
        "per_config_cap_feasibility":
            "PASS" if max_t <= ACCEPT_PER_CONFIG_HOURS else "FAIL",
    }
