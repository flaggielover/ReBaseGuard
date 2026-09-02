"""R1 optimized benchmark — exactly R1_FROZEN_SPEC.md.

The certified target is computed by IMPORTING the unmodified R-A' certifier.
The only difference from `ra_stop_gate.py` is the source of the resolvent bound
and, consequently, the number of sub-cells.
"""
from __future__ import annotations

import json
import math
import os
import platform
import resource
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
ROOT = NS.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(NS / "certified_method_repair_ra"))

from flint import arb                                                    # noqa: E402
from rebaseguard_certify.arb_backend import ball_record, rational, workprec  # noqa: E402
import ra_certifier as RA                                                # noqa: E402
from drift_minorant import block_forcing_resolvent, drift_monotone_resolvent  # noqa: E402

CELL = (0.24, 0.26)          # frozen, unchanged from the failed gate and R-A'
THRESHOLD = 0.2              # frozen
DEN = 10 ** 7                # frozen
WORKERS = 5                  # frozen, matches the baseline so CPU is comparable
LADDER = 4                   # frozen: n, n+1, n+2, n+3


def _worker(args):
    j, e_num, e_hi = args
    t = time.time()
    rec = RA.certify_at_exact_drift(e_num, DEN, e_hi_for_allowance=e_hi)
    rec = {k: v for k, v in rec.items() if not k.startswith("_")}
    rec["index"] = j
    rec["wall_seconds"] = time.time() - t
    return rec


def main() -> None:
    t0, c0 = time.time(), time.process_time()
    e_lo_num = round(CELL[0] * 100)
    minorant = drift_monotone_resolvent(e_num=e_lo_num, e_den=100)
    baseline = block_forcing_resolvent(e_num=e_lo_num, e_den=100)
    if minorant["resolvent_bound_upper_float"] > baseline["resolvent_bound_upper_float"]:
        raise ArithmeticError("minorant is not tighter than block forcing; abort per spec section 6")

    with workprec(RA.BITS):
        C = arb(minorant["resolvent_bound"]["ball"])
        a = arb(2) / (arb(2) * arb.pi()).sqrt()
        b2 = arb(4) * (-arb(1) / arb(2)).exp() / (arb(2) * arb.pi()).sqrt()
        h_max = arb(1) / (arb(4) * a * C)
        n0 = int(math.ceil((CELL[1] - CELL[0]) / (2.0 * float(h_max.lower()))))
        chosen = None
        for k in range(LADDER):
            n = n0 + k
            span = round((CELL[1] - CELL[0]) * DEN)
            if span % (2 * n):
                continue
            h = arb(rational(span, 2 * n * DEN))
            closure = C * (arb(2) * a * h + b2 * h * h)
            if h <= h_max and closure <= arb(1) / arb(2):
                chosen = (n, h, closure)
                break
        if chosen is None:
            raise ArithmeticError("frozen ladder exhausted; abort per spec section 6")
        n_sub, h_sub, closure = chosen
        c2 = arb(rational(113788, 100000)) + b2 * arb(rational(26, 100))

    span = round((CELL[1] - CELL[0]) * DEN)
    lo_num = round(CELL[0] * DEN)
    step = span // n_sub
    if step * n_sub != span or step % 2:
        raise ArithmeticError("sub-cells do not tile the declared cell exactly")
    jobs = [(j, lo_num + step * j + step // 2, CELL[1]) for j in range(n_sub)]

    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        cells = sorted(pool.map(_worker, jobs), key=lambda r: r["index"])

    with workprec(RA.BITS):
        lo_hull = hi_hull = None
        per_cell = []
        worst = {"C_delta": arb(0), "second": arb(0), "S2": arb(0)}
        for j, rec in enumerate(cells):
            delta = arb(rec["delta"]["ball"])
            delta_d = arb(rec["delta_derivative"]["ball"])
            G0 = arb(rec["sup_chebyshev_g"]["ball"]) + C * delta
            G1 = arb(rec["sup_chebyshev_dg"]["ball"]) + C * delta_d
            S2 = arb(2) * C * (arb(2) * a * G1 + b2 * G0 + b2 * h_sub * G1 + c2)
            e_lo = arb(rational(lo_num + step * j, DEN))
            e_hi = arb(rational(lo_num + step * (j + 1), DEN))
            e_range = (e_lo + e_hi) / arb(2) + arb(0, ((e_hi - e_lo) / arb(2)).upper())
            g_encl = arb(rec["ghat_origin"]["ball"]) + arb(0, (C * delta).upper())
            dg_encl = arb(rec["dghat_origin"]["ball"]) + arb(0, (C * delta_d).upper())
            second = (h_sub * h_sub / arb(2)) * S2
            r_encl = e_range + g_encl + arb(0, h_sub.upper()) * dg_encl + arb(0, second.upper())
            lo_hull = r_encl.lower() if lo_hull is None else min(lo_hull, r_encl.lower())
            hi_hull = r_encl.upper() if hi_hull is None else max(hi_hull, r_encl.upper())
            worst["C_delta"] = worst["C_delta"].max(C * delta)
            worst["second"] = worst["second"].max(second)
            worst["S2"] = worst["S2"].max(S2)
            per_cell.append({
                "index": j, "e_lo": float(e_lo), "e_hi": float(e_hi),
                "e_0_rational": rec["e_rational"],
                "delta": rec["delta"], "delta_derivative": rec["delta_derivative"],
                "ghat_origin": rec["ghat_origin"], "dghat_origin": rec["dghat_origin"],
                "C_delta": ball_record(C * delta), "S2": ball_record(S2),
                "taylor_second_order_term": ball_record(second),
                "R_enclosure": ball_record(r_encl), "wall_seconds": rec["wall_seconds"],
            })
        half = float(((hi_hull - lo_hull) / arb(2)).upper())

    usage = resource.getrusage(resource.RUSAGE_SELF)
    child = resource.getrusage(resource.RUSAGE_CHILDREN)
    import flint
    cpu_children = child.ru_utime + child.ru_stime
    baseline_cpu_hours = 6.20
    optimized_cpu_hours = cpu_children / 3600.0
    speedup = baseline_cpu_hours / optimized_cpu_hours if optimized_cpu_hours else float("inf")
    band = ("NOT_WORTH_MIGRATING" if speedup < 2.0 else
            "BORDERLINE" if speedup < 3.0 else
            "WORTH_MIGRATING" if speedup < 4.0 else "STRONG_PASS")
    ra_lo, ra_hi = -1.5902505376455707, -1.5618975830490345
    overlap = not (float(hi_hull) < ra_lo or float(lo_hull) > ra_hi)

    payload = {
        "schema": "rebaseguard.p5x.opt-r1.benchmark.v1",
        "campaign": "P5X Compute Optimization R1 - Drift-Explicit Resolvent Reduction",
        "classification": "CERTIFIED_BOUND_REFACTOR",
        "target_unchanged": True, "scope_unchanged": True,
        "reference_implementation": "certified_method_repair_ra/ra_certifier.py (imported unmodified)",
        "detector": "cusum", "m": 1, "e_cell": list(CELL),
        "cell_unchanged_from_ra": True,
        "model": {"k_num": 1, "k_den": 2, "h_num": 5, "h_den": 1},
        "taylor_order_N": RA.TAYLOR_N, "candidate_degree": RA.DEGREE,
        "precision_bits": RA.BITS, "subdivision_depth": RA.SUBDIVISION_DEPTH,
        "resolvent_optimized": minorant,
        "resolvent_baseline_block_forcing": baseline,
        "resolvent_reduction_factor": baseline["resolvent_bound_upper_float"]
                                      / minorant["resolvent_bound_upper_float"],
        "subcells": {"n_sub": n_sub, "h_max": ball_record(h_max), "h_sub": ball_record(h_sub),
                     "bootstrap_closure": ball_record(closure), "ladder_steps_used": n_sub - n0,
                     "tiles_cell_exactly": True},
        "certified_solves": 3 * n_sub, "bernstein_bounds": 2 * n_sub, "refinements": 0,
        "worst_components": {k: ball_record(v) for k, v in worst.items()},
        "R_enclosure": {"lower": float(lo_hull), "upper": float(hi_hull)},
        "interval_width": float(hi_hull - lo_hull),
        "achieved_half_width": half,
        "stop_gate": {"frozen_threshold": THRESHOLD, "achieved_half_width": half,
                      "verdict": "PASS" if half <= THRESHOLD else "FAIL",
                      "rule": "R1_FROZEN_SPEC.md section 10; not reinterpretable"},
        "correspondence": {"ra_enclosure": [ra_lo, ra_hi], "overlaps_ra": overlap},
        "speed": {"baseline_cpu_hours": baseline_cpu_hours,
                  "optimized_cpu_hours": optimized_cpu_hours,
                  "measured_speedup": speedup, "speedup_class": band,
                  "baseline_wall_seconds": 5173.286681890488,
                  "workers": WORKERS},
        "runtime": {"wall_seconds": time.time() - t0,
                    "cpu_seconds_parent": time.process_time() - c0,
                    "cpu_seconds_children": cpu_children,
                    "peak_rss_mib_parent": usage.ru_maxrss / (1024 * 1024),
                    "peak_rss_mib_child_max": child.ru_maxrss / (1024 * 1024)},
        "environment": {"python": platform.python_version(), "python_flint": flint.__version__,
                        "platform": platform.platform(), "cpu_count": os.cpu_count()},
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                     capture_output=True, text=True).stdout.strip(),
        "per_subcell": per_cell,
    }
    (NS / "results" / "r1_benchmark.json").write_text(json.dumps(payload, indent=1) + "\n")
    print(json.dumps({k: payload[k] for k in
                      ("subcells", "resolvent_reduction_factor", "R_enclosure",
                       "achieved_half_width", "stop_gate", "correspondence",
                       "speed", "runtime")}, indent=1))


if __name__ == "__main__":
    main()
