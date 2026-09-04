#!/usr/bin/env python3
"""Pilot-4 execution: master (benchmark) then reference (accuracy).

Executes PILOT4_PREREGISTRATION.md.  There is no allocation rule anywhere in
this file: no Stage-1 sizing, no staged top-up, no cap, no kappa.

Usage:
    run_measure.py master
    run_measure.py reference
"""

from __future__ import annotations

import json
import math
import resource
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT.parent / "p4y_precision_governance_pilot" / "src"))

from p4y_pilot.stats import clopper_pearson_lower, hill_alpha  # noqa: E402
from p4y_pilot4.addressing4 import audit_reachable_domain, seed  # noqa: E402
from p4y_pilot4.blocks4 import (  # noqa: E402
    BASE_BLOCK_PATHS, aggregate, base_series, factor_for,
)
from p4y_pilot4.estimand import (  # noqa: E402
    concentration, prefix_curve, ratio_spread, rel_se, split_estimates,
    theta_hat,
)
from p4y_pilot4.design4 import (  # noqa: E402
    ACCURACY_FACTOR, BETA, BLOCK_SIZES, BREF_GRID, CELLS, C_PREFIX, C_SPLIT,
    MAX_PRODUCTION_REFERENCE_HOURS, MAX_TOP1_SHARE, MAX_TOP5_SHARE,
    PILOT4_CPU_CAP_HOURS, PREFIX_FRACTIONS, R_REFERENCE_DRAWS,
    SECONDARY_FACTOR, SPLIT_PARTS, TARGET_PROBABILITY, brefs_for,
    master_base_blocks, master_pool_blocks, production_reference_hours,
    reachable_addresses, reference_base_blocks,
)


class Stop(RuntimeError):
    pass


def cpu() -> float:
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_utime + r.ru_stime


def spent(exclude: str) -> float:
    t = 0.0
    for n in ("master", "reference"):
        if n == exclude:
            continue
        p = ROOT / "results" / f"{n}.json"
        if p.exists():
            t += json.loads(p.read_text())["cpu_hours"]
    return t


def guard(used: float) -> None:
    if used > PILOT4_CPU_CAP_HOURS:
        raise Stop(f"CPU cap: {used:.3f} > {PILOT4_CPU_CAP_HOURS} h")


# ------------------------------------------------------------------ master
def run_master() -> int:
    inj = audit_reachable_domain(reachable_addresses())
    if not inj["collision_free"]:
        raise SystemExit(f"ADDRESS COLLISION: {inj}")
    out = {"schema": "rebaseguard.p4y-pilot4-master.v1", "binding": False,
           "base_block_paths": BASE_BLOCK_PATHS,
           "accuracy_factor": ACCURACY_FACTOR,
           "address_audit": {k: inj[k] for k in
                             ("addresses", "unique_seeds", "collision_free")},
           "strata": [], "stopped": None}
    c0 = cpu()
    try:
        for s in CELLS:
            guard((cpu() - c0) / 3600.0)
            n_base = master_base_blocks(s)
            pools = []
            for p in range(2):
                cc = cpu()
                pools.append(base_series(s.cell, seed(s.key, f"master{p}", 0),
                                         n_base))
                print(f"  {s.key} master{p}: {n_base} base blocks, "
                      f"{cpu()-cc:.1f} CPU-s", flush=True)
            rec = {"stratum": s.key, "config": s.cell.config,
                   "route": s.cell.route, "heavy": s.heavy, "role": s.role,
                   "master_base_blocks": n_base, "by_block_size": {}}
            for b in s.block_sizes:
                f = factor_for(b)
                npool = master_pool_blocks(s, b)
                a = aggregate(pools[0], f)[:npool]
                c = aggregate(pools[1], f)[:npool]
                both = np.concatenate([a, c])
                th = [theta_hat(a), theta_hat(c)]
                spread = ratio_spread(th)
                conc = concentration(both)
                pref = prefix_curve(both, PREFIX_FRACTIONS)
                pr = pref["1"]["theta"] / pref["0.5"]["theta"]
                quarters = split_estimates(both, SPLIT_PARTS)
                admissible = {
                    "disjoint_split": spread <= C_SPLIT,
                    "growing_prefix": (1 / C_PREFIX) <= pr <= C_PREFIX,
                    "extreme_top1": conc["top1"] <= MAX_TOP1_SHARE,
                    "extreme_top5": conc["top5"] <= MAX_TOP5_SHARE,
                }
                rec["by_block_size"][str(b)] = {
                    "block_paths": b, "pool_blocks_each": npool,
                    "theta_pool0": th[0], "theta_pool1": th[1],
                    "theta_benchmark": theta_hat(both),
                    "mean_benchmark": float(both.mean()),
                    "independent_pool_spread": spread,
                    "quarter_estimates": quarters,
                    "quarter_spread": ratio_spread(quarters),
                    "prefix_curve": pref, "prefix_full_over_half": pr,
                    "concentration": conc,
                    "hill_alpha_secondary": hill_alpha(list(both)),
                    "admissible_checks": admissible,
                    "benchmark_admissible": all(admissible.values()),
                }
                ok = "ADMISSIBLE" if all(admissible.values()) else "REJECTED"
                print(f"    b={b:>9d} theta={theta_hat(both):.5f} "
                      f"split={spread:6.3f} prefix={pr:6.3f} "
                      f"top1={conc['top1']:6.3f} top5={conc['top5']:6.3f} -> {ok}",
                      flush=True)
            out["strata"].append(rec)
    except Stop as exc:
        out["stopped"] = str(exc)
        print(f"\nSTOP: {exc}", flush=True)
    out["cpu_hours"] = (cpu() - c0) / 3600.0
    (ROOT / "results" / "master.json").write_text(json.dumps(out, indent=1))
    print(f"\nmaster CPU = {out['cpu_hours']*3600:.1f} s")
    return 0


# --------------------------------------------------------------- reference
def run_reference() -> int:
    mp = ROOT / "results" / "master.json"
    if not mp.exists():
        raise SystemExit("run master first")
    master = json.loads(mp.read_text())
    if master["stopped"]:
        raise SystemExit(f"master STOPPED: {master['stopped']}")
    bench = {r["stratum"]: r["by_block_size"] for r in master["strata"]}

    out = {"schema": "rebaseguard.p4y-pilot4-reference.v1", "binding": False,
           "draws": R_REFERENCE_DRAWS, "accuracy_factor": ACCURACY_FACTOR,
           "secondary_factor": SECONDARY_FACTOR,
           "target_probability": TARGET_PROBABILITY, "beta": BETA,
           "strata": [], "stopped": None}
    c0 = cpu()
    budget = spent("reference")
    try:
        for s in CELLS:
            n_base = reference_base_blocks(s)
            cc = cpu()
            draws = []
            for r in range(R_REFERENCE_DRAWS):
                guard(budget + (cpu() - c0) / 3600.0)
                draws.append(base_series(s.cell,
                                         seed(s.key, "reference", r), n_base))
            rec = {"stratum": s.key, "config": s.cell.config,
                   "route": s.cell.route, "heavy": s.heavy,
                   "reference_base_blocks": n_base, "candidates": [],
                   "cpu_seconds": cpu() - cc}
            for b in s.block_sizes:
                f = factor_for(b)
                tb = bench[s.key][str(b)]["theta_benchmark"]
                admissible = bench[s.key][str(b)]["benchmark_admissible"]
                for bref in brefs_for(s, b):
                    ratios = []
                    for d in draws:
                        vals = aggregate(d, f)[:bref]
                        if vals.size < bref:
                            ratios.append(math.nan)
                            continue
                        ratios.append(theta_hat(vals) / tb)
                    good = [x for x in ratios if math.isfinite(x)]
                    inside = sum(1 / ACCURACY_FACTOR <= x <= ACCURACY_FACTOR
                                 for x in good)
                    inside2 = sum(1 / SECONDARY_FACTOR <= x <= SECONDARY_FACTOR
                                  for x in good)
                    under = sum(x < 1.0 for x in good)
                    q = lambda p: (float(np.quantile(good, p)) if good
                                   else math.nan)
                    ref_h = production_reference_hours(b, bref)
                    rec["candidates"].append({
                        "block_paths": b, "bref": bref,
                        "benchmark_theta": tb,
                        "benchmark_admissible": admissible,
                        "draws": len(good),
                        "inside_band": inside,
                        "success_rate": inside / len(good) if good else math.nan,
                        "lower_bound": clopper_pearson_lower(inside, len(good),
                                                             BETA),
                        "inside_secondary_band": inside2,
                        "secondary_rate": (inside2 / len(good) if good
                                           else math.nan),
                        "underestimation_frequency": (under / len(good)
                                                      if good else math.nan),
                        "ratio_median": q(0.5), "ratio_q05": q(0.05),
                        "ratio_q10": q(0.10), "ratio_q90": q(0.90),
                        "ratio_q95": q(0.95),
                        "ratio_min": min(good) if good else math.nan,
                        "ratio_max": max(good) if good else math.nan,
                        "production_reference_hours": ref_h,
                        "affordable": ref_h <= MAX_PRODUCTION_REFERENCE_HOURS,
                        "reference_paths_per_stratum": b * bref,
                        "implied_relse_at_bref": rel_se(tb, bref),
                    })
                    cd = rec["candidates"][-1]
                    print(f"  {s.key:4s} b={b:>9d} B_ref={bref:4d}  "
                          f"med={cd['ratio_median']:6.3f} "
                          f"under={cd['underestimation_frequency']:5.2f} "
                          f"in[1/{ACCURACY_FACTOR:g},{ACCURACY_FACTOR:g}]="
                          f"{cd['inside_band']:2d}/{cd['draws']:2d} "
                          f"LB={cd['lower_bound']:.4f} "
                          f"bench={'ok' if admissible else 'REJECTED'}",
                          flush=True)
            out["strata"].append(rec)
    except Stop as exc:
        out["stopped"] = str(exc)
        print(f"\nSTOP: {exc}", flush=True)
    out["cpu_hours"] = (cpu() - c0) / 3600.0
    out["cumulative_cpu_hours"] = budget + out["cpu_hours"]
    (ROOT / "results" / "reference.json").write_text(json.dumps(out, indent=1))
    print(f"\nreference CPU = {out['cpu_hours']*3600:.1f} s; cumulative "
          f"{out['cumulative_cpu_hours']:.4f} / {PILOT4_CPU_CAP_HOURS} h")
    return 0


def main(phase: str) -> int:
    if phase == "master":
        return run_master()
    if phase == "reference":
        return run_reference()
    raise SystemExit("phase must be master or reference")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "master"))
