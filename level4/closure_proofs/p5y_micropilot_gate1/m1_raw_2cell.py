"""P5Y Gate-1 M1 driver: PILOT-RAW-2CELL.

Two frozen cells, two arms (raw pilot / z-variable historical control), one
frozen assembly.  Falsification pilot only; produces no certificate of record.
"""
from __future__ import annotations

import json, math, resource, subprocess, sys, time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P5X = ROOT / "level4" / "closure_proofs" / "p5x_global_nonlinear_dynamics"
for p in (str(HERE), str(P5X / "certified_method_repair_ra"),
          str(P5X / "compute_optimization_r1"), str(P5X / "compute_optimization_r2")):
    if p not in sys.path:
        sys.path.insert(0, p)

from flint import arb                                                        # noqa: E402
from rebaseguard_certify.arb_backend import ball_record, rational, workprec   # noqa: E402
import ra_certifier as RA                                                     # noqa: E402
import raw_certifier as RAW                                                   # noqa: E402
from r2_certifier import certify_at_exact_drift_r2                            # noqa: E402
from drift_minorant import drift_monotone_resolvent                           # noqa: E402

DEN = 10 ** 7                 # frozen
LADDER = 4                    # frozen: n0 .. n0+3
WORKERS = 5                   # frozen
CELLS = {                     # frozen, exactly two, no third may be added
    "A_near": (2400000, 2600000),
    "B_far":  (105441104, 120000000),
}
R2_ANCHOR = (-1.584973380499857, -1.5676443748392161)   # historical, cell A
THRESH_FAR = 1.0              # frozen primary
THRESH_FAR_PREF = 0.75        # frozen preferred, not decisive
THRESH_NEAR = 0.05            # frozen


def _worker(job):
    arm, j, e_num, e_hi, C_ball_str = job
    t = time.time()
    C = arb(C_ball_str)
    if arm == "raw":
        rec = RAW.certify_raw_at_exact_drift(e_num, DEN, resolvent=C, e_hi_for_allowance=e_hi)
    else:
        rec = certify_at_exact_drift_r2(e_num, DEN, resolvent=C, e_hi_for_allowance=e_hi)
    rec["index"] = j
    rec["arm"] = arm
    rec["wall_seconds"] = time.time() - t
    return rec


def subcell_plan(lo_num, hi_num, C):
    """Frozen R1 rule: h = 1/(4 a C), ladder over n, exact tiling required."""
    with workprec(RA.BITS):
        a = arb(2) / (arb(2) * arb.pi()).sqrt()
        b2 = arb(4) * (-arb(1) / arb(2)).exp() / (arb(2) * arb.pi()).sqrt()
        h_max = arb(1) / (arb(4) * a * C)
        span = hi_num - lo_num
        width = span / DEN
        n0 = max(1, int(math.ceil(width / (2.0 * float(h_max.lower())))))
        chosen = None
        for k in range(LADDER):
            n = n0 + k
            if span % (2 * n):
                continue
            step = span // n
            if step % 2:
                continue
            h = arb(rational(span, 2 * n * DEN))
            closure = C * (arb(2) * a * h + b2 * h * h)
            if h <= h_max and closure <= arb(1) / arb(2):
                chosen = (n, h, closure)
                break
        if chosen is None:
            raise ArithmeticError("frozen ladder exhausted")
        return chosen + (a, b2, h_max, n0)


def assemble(arm, cells, lo_num, step, n_sub, C, a, b2, h_sub, e_hi_float):
    with workprec(RA.BITS):
        if arm == "raw":
            _, c2 = RAW.raw_bootstrap_constants()
        else:
            c2 = arb(rational(113788, 100000)) + b2 * arb(rational(
                round(e_hi_float * 10 ** 6), 10 ** 6))
        lo_hull = hi_hull = None
        worst = {"C_delta": arb(0), "second": arb(0), "S2": arb(0), "G0": arb(0)}
        per = []
        for j, rec in enumerate(cells):
            delta = arb(rec["delta"]["ball"])
            delta_d = arb(rec["delta_derivative"]["ball"])
            kv = "sup_chebyshev_F" if arm == "raw" else "sup_chebyshev_g"
            kdv = "sup_chebyshev_dF" if arm == "raw" else "sup_chebyshev_dg"
            ko = "Fhat_origin" if arm == "raw" else "ghat_origin"
            kdo = "dFhat_origin" if arm == "raw" else "dghat_origin"
            G0 = arb(rec[kv]["ball"]) + C * delta
            G1 = arb(rec[kdv]["ball"]) + C * delta_d
            S2 = arb(2) * C * (arb(2) * a * G1 + b2 * G0 + b2 * h_sub * G1 + c2)
            e_lo = arb(rational(lo_num + step * j, DEN))
            e_hi = arb(rational(lo_num + step * (j + 1), DEN))
            u_encl = arb(rec[ko]["ball"]) + arb(0, (C * delta).upper())
            du_encl = arb(rec[kdo]["ball"]) + arb(0, (C * delta_d).upper())
            second = (h_sub * h_sub / arb(2)) * S2
            r_encl = u_encl + arb(0, h_sub.upper()) * du_encl + arb(0, second.upper())
            if arm != "raw":
                e_range = (e_lo + e_hi) / arb(2) + arb(0, ((e_hi - e_lo) / arb(2)).upper())
                r_encl = e_range + r_encl
            lo_hull = r_encl.lower() if lo_hull is None else min(lo_hull, r_encl.lower())
            hi_hull = r_encl.upper() if hi_hull is None else max(hi_hull, r_encl.upper())
            for k, v in (("C_delta", C * delta), ("second", second), ("S2", S2), ("G0", G0)):
                worst[k] = worst[k].max(v)
            per.append({"index": j, "e_lo": float(e_lo), "e_hi": float(e_hi),
                        "e_0_rational": rec["e_rational"],
                        "depth": rec.get("subdivision_depth_used"),
                        "delta": rec["delta"], "C_delta": ball_record(C * delta),
                        "S2": ball_record(S2), "second_order_term": ball_record(second),
                        "sup_unknown": rec[kv], "R_enclosure": ball_record(r_encl),
                        "wall_seconds": rec["wall_seconds"]})
        half = float(((hi_hull - lo_hull) / arb(2)).upper())
        return {"c2_used": ball_record(c2), "R_lower": float(lo_hull), "R_upper": float(hi_hull),
                "half_width": half,
                "worst": {k: ball_record(v) for k, v in worst.items()},
                "per_subcell": per}


def run_cell(name, lo_num, hi_num):
    e_hi_float = hi_num / DEN
    res = drift_monotone_resolvent(e_num=lo_num, e_den=DEN)   # M2: smallest |e| is worst
    C = arb(res["resolvent_bound"]["ball"])
    n_sub, h_sub, closure, a, b2, h_max, n0 = subcell_plan(lo_num, hi_num, C)
    span = hi_num - lo_num
    step = span // n_sub
    if step * n_sub != span:
        raise ArithmeticError("sub-cells do not tile exactly")
    out = {"cell": name, "e_lo": lo_num / DEN, "e_hi": e_hi_float,
           "resolvent": res, "n_sub": n_sub, "n0_from_h_max": n0,
           "h_max": ball_record(h_max), "h_sub": ball_record(h_sub),
           "bootstrap_closure": ball_record(closure), "tiles_exactly": True, "arms": {}}
    for arm in ("raw", "z_control"):
        jobs = [(arm, j, lo_num + step * j + step // 2, e_hi_float,
                 C.str(40, radius=True)) for j in range(n_sub)]
        t0 = time.process_time()
        cc0 = resource.getrusage(resource.RUSAGE_CHILDREN)
        with ProcessPoolExecutor(max_workers=WORKERS) as pool:
            cells = sorted(pool.map(_worker, jobs), key=lambda r: r["index"])
        cc1 = resource.getrusage(resource.RUSAGE_CHILDREN)
        asm = assemble(arm, cells, lo_num, step, n_sub, C, a, b2, h_sub, e_hi_float)
        asm["cpu_seconds"] = (cc1.ru_utime + cc1.ru_stime) - (cc0.ru_utime + cc0.ru_stime)
        asm["parent_cpu_seconds"] = time.process_time() - t0
        out["arms"][arm] = asm
    return out


def main():
    t_all = time.time()
    payload = {"schema": "rebaseguard.p5y.gate1.m1.v1",
               "pilot": "PILOT-RAW-2CELL", "binding": False,
               "generated_utc": datetime.now(timezone.utc).isoformat(),
               "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                            capture_output=True, text=True).stdout.strip(),
               "frozen": {"cells": {k: [v[0] / DEN, v[1] / DEN] for k, v in CELLS.items()},
                          "den": DEN, "ladder": LADDER, "workers": WORKERS,
                          "taylor_order": RA.TAYLOR_N, "degree": RA.DEGREE,
                          "bits": RA.BITS, "r2_anchor": list(R2_ANCHOR),
                          "thresholds": {"far": THRESH_FAR, "far_preferred": THRESH_FAR_PREF,
                                         "near": THRESH_NEAR}},
               "cells": {}}
    for name, (lo, hi) in CELLS.items():
        payload["cells"][name] = run_cell(name, lo, hi)

    A = payload["cells"]["A_near"]["arms"]
    B = payload["cells"]["B_far"]["arms"]
    overlap = not (A["raw"]["R_upper"] < R2_ANCHOR[0] or A["raw"]["R_lower"] > R2_ANCHOR[1])
    verdict = {
        "A1_near_overlaps_r2_anchor": bool(overlap),
        "A2_far_half_width_below_1.0": bool(B["raw"]["half_width"] < THRESH_FAR),
        "A3_far_half_width_below_0.75": bool(B["raw"]["half_width"] < THRESH_FAR_PREF),
        "A4_near_half_width_below_0.05": bool(A["raw"]["half_width"] <= THRESH_NEAR),
        "far_width_reduction_vs_z_control": (B["z_control"]["half_width"]
                                             / B["raw"]["half_width"]),
        "near_width_ratio_raw_over_z": A["raw"]["half_width"] / A["z_control"]["half_width"],
        "z_control_far_fits_in_minus2_2": bool(B["z_control"]["R_lower"] > -2.0
                                               and B["z_control"]["R_upper"] < 2.0),
        "raw_far_fits_in_minus2_2": bool(B["raw"]["R_lower"] > -2.0
                                         and B["raw"]["R_upper"] < 2.0),
    }
    verdict["PILOT_RAW_2CELL"] = ("PASS" if (verdict["A1_near_overlaps_r2_anchor"]
                                             and verdict["A2_far_half_width_below_1.0"]
                                             and verdict["A4_near_half_width_below_0.05"])
                                  else "FAIL")
    payload["verdict"] = verdict
    ch = resource.getrusage(resource.RUSAGE_CHILDREN)
    payload["runtime"] = {"wall_seconds": time.time() - t_all,
                          "cpu_seconds_children_total": ch.ru_utime + ch.ru_stime,
                          "cpu_hours_children_total": (ch.ru_utime + ch.ru_stime) / 3600.0,
                          "peak_rss_mib_child_max": ch.ru_maxrss / (1024 * 1024)}
    (HERE / "results" / "m1_raw_2cell.json").write_text(json.dumps(payload, indent=1) + "\n")
    print(json.dumps({"verdict": verdict,
                      "A_near": {k: {kk: A[k][kk] for kk in ("R_lower", "R_upper", "half_width", "cpu_seconds")} for k in A},
                      "B_far": {k: {kk: B[k][kk] for kk in ("R_lower", "R_upper", "half_width", "cpu_seconds")} for k in B},
                      "n_sub": {n: payload["cells"][n]["n_sub"] for n in payload["cells"]},
                      "runtime": payload["runtime"]}, indent=1))


if __name__ == "__main__":
    main()
