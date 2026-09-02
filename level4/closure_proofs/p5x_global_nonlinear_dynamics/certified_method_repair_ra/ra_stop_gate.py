"""The R-A' stop-gate, exactly as RA_FROZEN_SPEC.md declares.

Cell, threshold, degree, order, precision, sub-cell rule, bootstrap and verdict
semantics are all frozen; nothing here chooses a parameter.
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

from flint import arb                                          # noqa: E402
from rebaseguard_certify.arb_backend import ball_record, rational, workprec  # noqa: E402
import ra_certifier as RA                                      # noqa: E402

CELL = (0.24, 0.26)                 # frozen: same binding cell as the failed gate
THRESHOLD = 0.2                     # frozen
DEN = 10 ** 7                       # e_0 denominator, frozen


def _worker(args):
    j, e_num, e_hi = args
    t = time.time()
    rec = RA.certify_at_exact_drift(e_num, DEN, e_hi_for_allowance=e_hi)
    rec = {k: v for k, v in rec.items() if not k.startswith("_")}
    rec["index"] = j
    rec["wall_seconds"] = time.time() - t
    return rec


def main() -> None:
    t0 = time.time()
    c0 = time.process_time()
    with workprec(RA.BITS):
        e_ball = arb(rational(25, 100), rational(1, 100))       # covers [0.24, 0.26]
        C, block_n, q_n = RA.resolvent_bound(e_ball)
        a = arb(2) * (-(arb(0))).exp() / (arb(2) * arb.pi()).sqrt()   # 2 phi(0)
        b2 = arb(4) * (-arb(1) / arb(2)).exp() / (arb(2) * arb.pi()).sqrt()  # 4 phi(1)
        h_max = arb(1) / (arb(4) * a * C)
        n_sub = int(math.ceil((CELL[1] - CELL[0]) / (2.0 * float(h_max.lower()))))
        h_sub = arb(rational(round((CELL[1] - CELL[0]) * DEN), 2 * n_sub * DEN))
        if not h_sub <= h_max:
            raise ArithmeticError("sub-cell half-width exceeds the frozen bound")
        closure = C * (arb(2) * a * h_sub + b2 * h_sub * h_sub)
        if not closure <= arb(1) / arb(2):
            raise ArithmeticError("bootstrap closure condition failed")
        c2 = arb(rational(113788, 100000)) + b2 * arb(rational(26, 100))

    # frozen sub-cell grid
    lo_num = round(CELL[0] * DEN)
    step = round((CELL[1] - CELL[0]) * DEN) // n_sub
    if step * n_sub != round((CELL[1] - CELL[0]) * DEN):
        raise ArithmeticError("sub-cells do not tile the declared cell")
    jobs = []
    for j in range(n_sub):
        mid = lo_num + step * j + step // 2
        if step % 2:
            raise ArithmeticError("sub-cell midpoint is not exactly representable")
        jobs.append((j, mid, CELL[1]))

    workers = max(1, min(5, (os.cpu_count() or 2) - 1))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        cells = sorted(pool.map(_worker, jobs), key=lambda r: r["index"])

    with workprec(RA.BITS):
        lo_hull = None
        hi_hull = None
        per_cell = []
        for j, rec in enumerate(cells):
            delta = arb(rec["delta"]["ball"])
            delta_d = arb(rec["delta_derivative"]["ball"])
            sup_g = arb(rec["sup_chebyshev_g"]["ball"])
            sup_dg = arb(rec["sup_chebyshev_dg"]["ball"])
            g0 = arb(rec["ghat_origin"]["ball"])
            dg0 = arb(rec["dghat_origin"]["ball"])
            G0 = sup_g + C * delta
            G1 = sup_dg + C * delta_d
            S2 = arb(2) * C * (arb(2) * a * G1 + b2 * G0 + b2 * h_sub * G1 + c2)
            e_lo = arb(rational(lo_num + step * j, DEN))
            e_hi = arb(rational(lo_num + step * (j + 1), DEN))
            e_range = (e_lo + e_hi) / arb(2) + arb(0, ((e_hi - e_lo) / arb(2)).upper())
            g_encl = g0 + arb(0, (C * delta).upper())
            dg_encl = dg0 + arb(0, (C * delta_d).upper())
            first = arb(0, h_sub.upper()) * dg_encl
            second = arb(0, ((h_sub * h_sub / arb(2)) * S2).upper())
            r_encl = e_range + g_encl + first + second
            lo_hull = r_encl.lower() if lo_hull is None else min(lo_hull, r_encl.lower())
            hi_hull = r_encl.upper() if hi_hull is None else max(hi_hull, r_encl.upper())
            per_cell.append({
                "index": j, "e_lo": float(e_lo), "e_hi": float(e_hi),
                "e_0_rational": rec["e_rational"],
                "delta": rec["delta"], "delta_derivative": rec["delta_derivative"],
                "ghat_origin": rec["ghat_origin"], "dghat_origin": rec["dghat_origin"],
                "G0": ball_record(G0), "G1": ball_record(G1), "S2": ball_record(S2),
                "C_delta": ball_record(C * delta),
                "taylor_second_order_term": ball_record((h_sub * h_sub / arb(2)) * S2),
                "R_enclosure": ball_record(r_encl),
                "wall_seconds": rec["wall_seconds"],
            })
        half = (hi_hull - lo_hull) / arb(2)
        half_f = float(half.upper())

    usage = resource.getrusage(resource.RUSAGE_SELF)
    child = resource.getrusage(resource.RUSAGE_CHILDREN)
    import flint
    payload = {
        "schema": "rebaseguard.p5x.ra.stop-gate.v1",
        "method": "R-A' (recentred Taylor representation + exact-centre Taylor model in e)",
        "supersedes_method": "first certified method, FAILED at commit 528908b (result preserved)",
        "target": "R_{CUSUM,m=1}(e) over the closed cell",
        "detector": "cusum", "m": 1, "e_cell": list(CELL),
        "cell_unchanged_from_failed_gate": True,
        "model": {"k_num": 1, "k_den": 2, "h_num": 5, "h_den": 1},
        "taylor_order_N": RA.TAYLOR_N, "candidate_degree": RA.DEGREE,
        "precision_bits": RA.BITS, "subdivision_depth": RA.SUBDIVISION_DEPTH,
        "resolvent": {"bound": ball_record(C), "block_length_n": block_n,
                      "q_n_lower": ball_record(q_n), "imported_constant": False,
                      "monotonicity_in_e_used": False},
        "subcells": {"n_sub": n_sub, "h_max_frozen_formula": ball_record(h_max),
                     "h_sub": ball_record(h_sub),
                     "bootstrap_closure": ball_record(closure),
                     "tiles_cell_exactly": True},
        "certified_solves": 3 * n_sub,
        "bernstein_bounds": 2 * n_sub,
        "R_enclosure": {"lower": float(lo_hull), "upper": float(hi_hull)},
        "interval_width": float(hi_hull - lo_hull),
        "achieved_half_width": half_f,
        "stop_gate": {"frozen_threshold": THRESHOLD,
                      "achieved_half_width": half_f,
                      "verdict": "PASS" if half_f <= THRESHOLD else "FAIL",
                      "rule": "RA_FROZEN_SPEC.md section 11; not reinterpretable"},
        "runtime": {"wall_seconds": time.time() - t0,
                    "cpu_seconds_parent": time.process_time() - c0,
                    "cpu_seconds_children": child.ru_utime + child.ru_stime,
                    "workers": workers,
                    "peak_rss_mib_parent": usage.ru_maxrss / (1024 * 1024),
                    "peak_rss_mib_child_max": child.ru_maxrss / (1024 * 1024)},
        "environment": {"python": platform.python_version(),
                        "python_flint": flint.__version__,
                        "platform": platform.platform(), "cpu_count": os.cpu_count()},
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                     capture_output=True, text=True).stdout.strip(),
        "per_subcell": per_cell,
    }
    (NS / "results" / "ra_stop_gate.json").write_text(json.dumps(payload, indent=1) + "\n")
    print(json.dumps({k: payload[k] for k in
                      ("e_cell", "subcells", "resolvent", "R_enclosure",
                       "achieved_half_width", "stop_gate", "runtime")}, indent=1))


if __name__ == "__main__":
    main()
