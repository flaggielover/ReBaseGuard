"""R2 benchmark B1: the full gate on the unchanged cell, optimized path."""
from __future__ import annotations
import json, math, os, platform, resource, subprocess, sys, time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
ROOT = NS.parents[2]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(NS / "certified_method_repair_ra"))
sys.path.insert(0, str(NS / "compute_optimization_r1"))

from flint import arb                                                    # noqa: E402
from rebaseguard_certify.arb_backend import ball_record, rational, workprec  # noqa: E402
import ra_certifier as RA                                                # noqa: E402
import r2_certifier as R2C                                              # noqa: E402
from drift_minorant import drift_monotone_resolvent                      # noqa: E402

CELL = (0.24, 0.26); THRESHOLD = 0.2; DEN = 10 ** 7; WORKERS = 5
R1_CPU_HOURS = 1.1727245380555558
R1_ENCL = (-1.5843524238144047, -1.5682610865345454)


def _worker(args):
    j, e_num, e_hi, cball = args
    t = time.time()
    with workprec(RA.BITS):
        C = arb(cball)
    rec = R2C.certify_at_exact_drift_r2(e_num, DEN, resolvent=C, e_hi_for_allowance=e_hi)
    rec["index"] = j; rec["wall_seconds"] = time.time() - t
    return rec


def main() -> None:
    t0, c0 = time.time(), time.process_time()
    minorant = drift_monotone_resolvent(e_num=24, e_den=100)
    cball = minorant["resolvent_bound"]["ball"]
    with workprec(RA.BITS):
        C = arb(cball)
        a = arb(2) / (arb(2) * arb.pi()).sqrt()
        b2 = arb(4) * (-arb(1) / arb(2)).exp() / (arb(2) * arb.pi()).sqrt()
        h_max = arb(1) / (arb(4) * a * C)
        span = round((CELL[1] - CELL[0]) * DEN)
        n0 = int(math.ceil((CELL[1] - CELL[0]) / (2.0 * float(h_max.lower()))))
        chosen = None
        for k in range(4):
            n = n0 + k
            if span % (2 * n):
                continue
            h = arb(rational(span, 2 * n * DEN))
            clos = C * (arb(2) * a * h + b2 * h * h)
            if h <= h_max and clos <= arb(1) / arb(2):
                chosen = (n, h, clos); break
        n_sub, h_sub, closure = chosen
        c2 = arb(rational(113788, 100000)) + b2 * arb(rational(26, 100))
    lo_num = round(CELL[0] * DEN); step = span // n_sub
    jobs = [(j, lo_num + step * j + step // 2, CELL[1], cball) for j in range(n_sub)]
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        cells = sorted(pool.map(_worker, jobs), key=lambda r: r["index"])

    with workprec(RA.BITS):
        lo_h = hi_h = None; per = []
        for j, rec in enumerate(cells):
            delta = arb(rec["delta"]["ball"]); delta_d = arb(rec["delta_derivative"]["ball"])
            G0 = arb(rec["sup_chebyshev_g"]["ball"]) + C * delta
            G1 = arb(rec["sup_chebyshev_dg"]["ball"]) + C * delta_d
            S2 = arb(2) * C * (arb(2) * a * G1 + b2 * G0 + b2 * h_sub * G1 + c2)
            e_lo = arb(rational(lo_num + step * j, DEN)); e_hi = arb(rational(lo_num + step * (j + 1), DEN))
            e_rng = (e_lo + e_hi) / arb(2) + arb(0, ((e_hi - e_lo) / arb(2)).upper())
            g_e = arb(rec["ghat_origin"]["ball"]) + arb(0, (C * delta).upper())
            dg_e = arb(rec["dghat_origin"]["ball"]) + arb(0, (C * delta_d).upper())
            second = (h_sub * h_sub / arb(2)) * S2
            r_e = e_rng + g_e + arb(0, h_sub.upper()) * dg_e + arb(0, second.upper())
            lo_h = r_e.lower() if lo_h is None else min(lo_h, r_e.lower())
            hi_h = r_e.upper() if hi_h is None else max(hi_h, r_e.upper())
            per.append({"index": j, "e_lo": float(e_lo), "e_hi": float(e_hi),
                        "depth_used": rec["subdivision_depth_used"],
                        "delta": rec["delta"], "delta_derivative": rec["delta_derivative"],
                        "R_enclosure": ball_record(r_e), "wall_seconds": rec["wall_seconds"]})
        half = float(((hi_h - lo_h) / arb(2)).upper())

    ch = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu_h = (ch.ru_utime + ch.ru_stime) / 3600.0
    sp = R1_CPU_HOURS / cpu_h if cpu_h else float("inf")
    band = ("R2_WEAK" if sp < 2 else "R2_MODERATE" if sp < 4 else
            "R2_STRONG" if sp < 8 else "R2_BREAKTHROUGH")
    overlap = not (float(hi_h) < R1_ENCL[0] or float(lo_h) > R1_ENCL[1])
    import flint
    payload = {
        "schema": "rebaseguard.p5x.opt-r2.benchmark.v1", "benchmark": "B1",
        "campaign": "P5X Compute Optimization R2 - Symbolic Residual and SR Cost Reduction",
        "candidates": ["C1 Bernstein depth ladder", "C2 dense affine substitution"],
        "classification": ["CERTIFIED_BOUND_REFACTOR", "CERTIFIED_BOUND_REFACTOR"],
        "target_unchanged": True, "scope_unchanged": True,
        "detector": "cusum", "m": 1, "moment": "first (with derivative equation)",
        "e_cell": list(CELL), "cell_unchanged": True,
        "taylor_order_N": RA.TAYLOR_N, "candidate_degree": RA.DEGREE,
        "precision_bits": RA.BITS,
        "subdivision_depth_used": sorted({r["depth_used"] for r in per}),
        "residual_degree": 145,
        "resolvent": {"bound": minorant["resolvent_bound"], "t_star": minorant["t_star"]},
        "subcells": {"n_sub": n_sub, "h_sub": ball_record(h_sub),
                     "bootstrap_closure": ball_record(closure), "tiles_cell_exactly": True},
        "certified_solves": 3 * n_sub, "bernstein_bounds": 2 * n_sub, "refinements": 0,
        "R_enclosure": {"lower": float(lo_h), "upper": float(hi_h)},
        "interval_width": float(hi_h - lo_h), "achieved_half_width": half,
        "stop_gate": {"frozen_threshold": THRESHOLD, "achieved_half_width": half,
                      "verdict": "PASS" if half <= THRESHOLD else "FAIL"},
        "correspondence": {"r1_enclosure": list(R1_ENCL), "overlaps_r1": overlap},
        "speed": {"r1_cpu_hours": R1_CPU_HOURS, "r2_cpu_hours": cpu_h,
                  "measured_speedup": sp, "speedup_class": band,
                  "r1_wall_seconds": 1262.9230999946594, "workers": WORKERS},
        "runtime": {"wall_seconds": time.time() - t0,
                    "cpu_seconds_children": ch.ru_utime + ch.ru_stime,
                    "peak_rss_mib_child_max": ch.ru_maxrss / (1024 * 1024)},
        "environment": {"python": platform.python_version(), "python_flint": flint.__version__,
                        "cpu_count": os.cpu_count()},
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                     capture_output=True, text=True).stdout.strip(),
        "per_subcell": per,
    }
    (NS / "results" / "r2_benchmark.json").write_text(json.dumps(payload, indent=1) + "\n")
    print(json.dumps({k: payload[k] for k in ("subcells", "subdivision_depth_used",
                      "R_enclosure", "achieved_half_width", "stop_gate",
                      "correspondence", "speed", "runtime")}, indent=1))


if __name__ == "__main__":
    main()
