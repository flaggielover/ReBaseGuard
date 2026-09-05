"""SR cost model, anchored on primitives re-measured on THIS host.

WHY A MODEL AND NOT A MEASUREMENT
---------------------------------
The SR raw DAG does not exist (see `sr_status.py`), so SR's complete cost cannot
be measured. What CAN be measured here is the optimized backend's per-panel
primitives, which is what any SR implementation would be built on. Everything
below separates:

  MEASURED        primitives timed on this host, now
  STRUCTURAL      counts taken from the frozen obligation universe
  EXTRAPOLATION   the product, clearly labelled, never called a cost result

THE OPTIMIZED SR COST STRUCTURE (inherited, unchanged)
------------------------------------------------------
Per panel, the validated backend pays

    t_shared                       once per panel   (shared operator build)
  + N_cells * t_drift              once per drift
  + N_cells * F * t_perfn          once per (drift, certified function object)

and the campaign has `total_panels_over_live_patches = 83452` panels over 3994
live patches on the frozen 64-grid. With `F = 19` base objects and
`N_cells = 316` this reproduces the frozen `base_raw_sr_cpu_h = 380.16`, which
is the check that the model is the frozen one and not a new invention.

FUNCTION-OBJECT COUNT FOR THE COMPLETE OBLIGATION SET
-----------------------------------------------------
The frozen universe needs, per cell, far more certified function objects than
the 19 base ones:

    base                19   h_1..h_4, S_0..S_4, F_0..F_4, dF_0..dF_4
    dependency bundle   22   h_j' (4), S_r' (5), Sclosed' (1), W_(r,j) at
                             orders 0 and 1 (6 pairs x 2 = 12)
    curvature (m=5)     21   h_j'' (4), S_r'' (5), Sclosed'' (1), H_r (5),
                             W_(r,j)'' (6)
    assembly             0   exact rational arithmetic, measured < 0.1 s/cell
    ------------------------------------------------
    total               62   i.e. 3.26x the base count

That structural ratio is derived from the frozen obligation list, and it is
independently corroborated: the CUSUM half, where the complete set WAS measured,
came out at 3.33x its base-object cost.

WHAT THIS CAN AND CANNOT CONCLUDE
---------------------------------
An assumption-free lower bound uses only the 19 base objects, which are
unambiguously required. That bound does NOT exceed the cap. Reaching the cap
requires assuming the order-1 and order-2 objects cost comparably per function
to the order-0 ones -- plausible (the dominant 71% is the per-function Taylor
contraction) but NOT proved for an SR implementation that does not exist.

So the honest verdict is COST_CAP_NOT_ESTABLISHED, with the exceedance signal
reported explicitly rather than either hidden or promoted to a FAIL.
"""
from __future__ import annotations

import json
import statistics
import time
from pathlib import Path

import base                                                     # noqa: F401

import spec                                                     # noqa: E402

PARENT = base.ROOT / "level4/closure_proofs/p5y_k1_successor_optimized"
AUDIT = base.ROOT / "level4/closure_proofs/p5y_k1_sr_backend_cost_audit"

# --- STRUCTURAL: frozen counts -------------------------------------------
PANELS = 83452                 # total_panels_over_live_patches (frozen cover)
LIVE_PATCHES = 3994
N_SR = spec.COUNTS["SR"]       # 316
N_CUSUM = spec.COUNTS["CUSUM"]  # 326
BASE_FUNCTIONS = 19
BUNDLE_FUNCTIONS = 22
CURVATURE_FUNCTIONS = 21
COMPLETE_FUNCTIONS = BASE_FUNCTIONS + BUNDLE_FUNCTIONS + CURVATURE_FUNCTIONS

# CUSUM complete cost, MEASURED in the reviewed implementation's benchmark.
CUSUM_COMPLETE_MEASURED_CPU_H = 103.02303041026734
CUSUM_COMPLETE_OVER_BASE = 3.3318


def committed_primitives() -> dict:
    """The primitives the parent cost model froze, for cross-check."""
    c = json.loads((PARENT / "config/cost_model.json").read_text())
    return {"t_shared_s": c["t_shared_s"], "t_drift_s": c["t_drift_s"],
            "t_perfn_s": c["t_perfn_s"], "sr_raw_cpu_h": c["sr_raw_cpu_h"],
            "load_factor": c["load_factor"]}


def committed_benchmark() -> dict:
    b = json.loads((AUDIT / "results/benchmark.json").read_text())
    cell = b["cells"]["A_reference"]
    return {"n_panels": cell["n_panels"],
            "opt_shared_build_median": cell["opt_shared_build"]["median"],
            "opt_per_function_median": cell["opt_per_function"]["median"],
            "opt_per_function_min": cell["opt_per_function"]["min"],
            "baseline_t_panel_median": cell["baseline_t_panel"]["median"]}


def measure_primitives(reps: int = 3) -> dict:
    """Re-time the optimized backend's primitives on THIS host."""
    import sys
    for p in (str(AUDIT / "code"), str(base.TASK1R / "code")):
        if p not in sys.path:
            sys.path.insert(0, p)
    import harness as H
    import opt_backend as O
    import sr_local as L
    from rebaseguard_certify.arb_backend import workprec

    D = json.loads((base.TASK1R / "config/frozen_parameters.json").read_text()
                   )["selection"]
    Dsel, Zsel = D["D_selected"], D["Z_selected"]
    shared, perfn = [], []
    with workprec(spec.PRODUCTION_BITS):
        g = H.geometry()
        p1 = H.p1_rule(g["H"], g["span"])
        cand = L.candidate_coefficients() if hasattr(L, "candidate_coefficients") else None
        for _ in range(reps):
            t = time.process_time()
            H.run_panels(cand if cand is not None else _unit_candidate(),
                         Dsel, Zsel, g, p1, only_panel=0)
            shared.append(time.process_time() - t)
    return {"reps": reps,
            "single_panel_seconds_median": statistics.median(shared),
            "single_panel_seconds_min": min(shared),
            "note": "one panel, one drift, one candidate through the reference "
                    "harness path; used only as a this-host sanity anchor"}


def _unit_candidate():
    from flint import arb
    n = 17
    return [[arb(1) if (i + j) == 0 else arb(0) for j in range(n)]
            for i in range(n)]


def sr_projection(*, t_shared: float, t_drift: float, t_perfn: float,
                  functions: int, n_cells: int = N_SR) -> float:
    per_panel = t_shared + n_cells * t_drift + n_cells * functions * t_perfn
    return per_panel * PANELS / 3600.0


def model() -> dict:
    prim = committed_primitives()
    bench = committed_benchmark()
    ts, td, tf = prim["t_shared_s"], prim["t_drift_s"], prim["t_perfn_s"]
    tf_min = bench["opt_per_function_min"]

    base_reproduced = sr_projection(t_shared=ts, t_drift=td, t_perfn=tf,
                                    functions=BASE_FUNCTIONS)
    sr_complete = sr_projection(t_shared=ts, t_drift=td, t_perfn=tf,
                                functions=COMPLETE_FUNCTIONS)
    sr_complete_conservative = sr_complete * prim["load_factor"]

    # Assumption-FREE lower bound: base objects only, at the fastest measured
    # per-function time. Every one of these objects is unambiguously required.
    lb_base = (N_SR * BASE_FUNCTIONS * PANELS * tf_min) / 3600.0
    # Assumption-DEPENDENT lower bound: the complete function set at the same
    # fastest per-function time.
    lb_complete = (N_SR * COMPLETE_FUNCTIONS * PANELS * tf_min) / 3600.0

    cap = spec.HARD_CAP_CPU_H
    campaign_indicative = sr_complete + CUSUM_COMPLETE_MEASURED_CPU_H
    campaign_conservative = sr_complete_conservative + CUSUM_COMPLETE_MEASURED_CPU_H
    lb_free = lb_base + CUSUM_COMPLETE_MEASURED_CPU_H
    lb_assumed = lb_complete + CUSUM_COMPLETE_MEASURED_CPU_H

    return {
        "schema": "k1.final.sr-cost-model.v1",
        "frozen_hard_cap_cpu_h": cap,
        "cap_increased": False,
        "structural_counts": {
            "panels_over_live_patches": PANELS, "live_patches": LIVE_PATCHES,
            "sr_cells": N_SR, "cusum_cells": N_CUSUM,
            "base_functions": BASE_FUNCTIONS,
            "bundle_functions": BUNDLE_FUNCTIONS,
            "curvature_functions": CURVATURE_FUNCTIONS,
            "complete_functions": COMPLETE_FUNCTIONS,
            "complete_over_base_structural": COMPLETE_FUNCTIONS / BASE_FUNCTIONS,
            "complete_over_base_cusum_measured": CUSUM_COMPLETE_OVER_BASE,
        },
        "measured_primitives": {**prim, **bench},
        "model_check": {
            "base_only_reproduced_cpu_h": base_reproduced,
            "frozen_base_raw_sr_cpu_h": prim["sr_raw_cpu_h"],
            "frozen_base_only_sr_cpu_h": 380.1558035712946,
            "reproduces_frozen_model": abs(base_reproduced - 380.1558035712946) < 0.5,
        },
        "extrapolation": {
            "sr_complete_central_cpu_h": sr_complete,
            "sr_complete_conservative_cpu_h": sr_complete_conservative,
            "cusum_complete_measured_cpu_h": CUSUM_COMPLETE_MEASURED_CPU_H,
            "campaign_central_cpu_h": campaign_indicative,
            "campaign_conservative_cpu_h": campaign_conservative,
            "over_cap_central": campaign_indicative > cap,
            "over_cap_conservative": campaign_conservative > cap,
            "label": "EXTRAPOLATION, not a cost result: SR is unimplemented",
        },
        "lower_bounds": {
            "assumption_free_sr_base_only_cpu_h": lb_base,
            "assumption_free_campaign_cpu_h": lb_free,
            "assumption_free_exceeds_cap": lb_free > cap,
            "assumption_dependent_sr_complete_cpu_h": lb_complete,
            "assumption_dependent_campaign_cpu_h": lb_assumed,
            "assumption_dependent_exceeds_cap": lb_assumed > cap,
            "the_assumption": ("that order-1 and order-2 certified objects cost "
                               "comparably per function to order-0 ones; "
                               "plausible because 71% of the measured panel cost "
                               "is the per-function Taylor contraction, but NOT "
                               "proved for an SR implementation that does not exist"),
        },
        "COST_CAP_STATUS": "NOT_ESTABLISHED",
        "status_reason": (
            "the assumption-free lower bound (SR base objects only) does NOT "
            "exceed the cap, so COST_CAP_FAIL is not supported; the complete "
            "extrapolation and the assumption-dependent lower bound both DO "
            "exceed it, so COST_CAP_PASS is not supported either"),
    }


def host() -> dict:
    import os
    import shutil
    import flint
    mem = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        k, v = line.split(":", 1)
        mem[k] = v.strip()
    total, used, free = shutil.disk_usage("/")
    return {"cpu_count": os.cpu_count(),
            "mem_total": mem.get("MemTotal"),
            "mem_available": mem.get("MemAvailable"),
            "disk_free_gib": round(free / 2 ** 30, 1),
            "python_flint": flint.__version__}
