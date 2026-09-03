"""CUSUM m=1 first-moment global production cover over [0,12].

Mirrors the validated R2 benchmark cell-enclosure formula exactly; only the
cover walk is new.  Pass criterion is the theorem consumer |R| < 2 strictly.
"""
from __future__ import annotations
import json, math, resource, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
for p in (NS/"certified_method_repair_ra", NS/"compute_optimization_r1",
          NS/"compute_optimization_r2",
          Path(__file__).resolve().parents[5]/"rebaseguard-proof"/"src"):
    if str(p) not in sys.path: sys.path.insert(0, str(p))

from flint import arb                                        # noqa: E402
import ra_certifier as RA                                    # noqa: E402
import r2_certifier as R2C                                   # noqa: E402
from drift_minorant import drift_monotone_resolvent          # noqa: E402
from rebaseguard_certify.arb_backend import ball_record, rational, workprec  # noqa: E402

DEN = 10**7
E_MAX = 12 * DEN
N_SUB = 8
WORKERS = 5
STOP_CPU_HOURS = 500.0


def _consts():
    a = arb(2) / (arb(2) * arb.pi()).sqrt()
    b2 = arb(4) * (-arb(1) / arb(2)).exp() / (arb(2) * arb.pi()).sqrt()
    return a, b2


def build_cover():
    """Deterministic frozen walk; returns [(lo_num, hi_num, C_ball, hnum, n_sub)]."""
    with workprec(RA.BITS):
        a, b2 = _consts()
        af, b2f = float(a.mid()), float(b2.mid())
    cells, lo = [], 0
    while lo < E_MAX:
        m = drift_monotone_resolvent(e_num=lo, e_den=DEN)
        cball = m["resolvent_bound"]["ball"]
        with workprec(RA.BITS):
            C = arb(cball)
            Cf = float(C.mid()) + float(C.rad())
        hnum = int(math.floor(DEN / (4.0 * af * Cf)))
        while hnum > 1:
            h = hnum / DEN
            if Cf * (2.0 * af * h + b2f * h * h) <= 0.5:
                break
            hnum = max(1, int(hnum * 0.97))
        span = 2 * N_SUB * hnum
        n_sub = N_SUB
        if lo + span >= E_MAX:                       # final cell: retile exactly
            span = E_MAX - lo
            n_sub = max(1, -(-span // (2 * hnum)))
            while span % (2 * n_sub):
                n_sub += 1
        cells.append((lo, lo + span, cball, hnum, n_sub))
        lo += span
    return cells


def _worker(args):
    j, e_num, e_hi_f, cball = args
    t = time.time()
    with workprec(RA.BITS):
        C = arb(cball)
    rec = R2C.certify_at_exact_drift_r2(e_num, DEN, resolvent=C,
                                        e_hi_for_allowance=e_hi_f)
    rec["index"] = j
    rec["wall_seconds"] = time.time() - t
    return rec


def enclose_cell(lo, hi, cball, hnum, n_sub, recs):
    with workprec(RA.BITS):
        a, b2 = _consts()
        C = arb(cball)
        h_sub = arb(rational(hnum, DEN))
        c2 = arb(rational(113788, 100000)) + b2 * arb(rational(hi, DEN))
        step = (hi - lo) // n_sub
        lo_h = hi_h = None
        for j, rec in enumerate(recs):
            delta = arb(rec["delta"]["ball"]); delta_d = arb(rec["delta_derivative"]["ball"])
            G0 = arb(rec["sup_chebyshev_g"]["ball"]) + C * delta
            G1 = arb(rec["sup_chebyshev_dg"]["ball"]) + C * delta_d
            S2 = arb(2) * C * (arb(2) * a * G1 + b2 * G0 + b2 * h_sub * G1 + c2)
            e_lo = arb(rational(lo + step * j, DEN)); e_hi = arb(rational(lo + step * (j + 1), DEN))
            e_rng = (e_lo + e_hi) / arb(2) + arb(0, ((e_hi - e_lo) / arb(2)).upper())
            g_e = arb(rec["ghat_origin"]["ball"]) + arb(0, (C * delta).upper())
            dg_e = arb(rec["dghat_origin"]["ball"]) + arb(0, (C * delta_d).upper())
            r_e = (e_rng + g_e + arb(0, h_sub.upper()) * dg_e
                   + arb(0, ((h_sub * h_sub / arb(2)) * S2).upper()))
            lo_h = r_e.lower() if lo_h is None else min(lo_h, r_e.lower())
            hi_h = r_e.upper() if hi_h is None else max(hi_h, r_e.upper())
        return float(lo_h), float(hi_h)


def main():
    t0 = time.time()
    cells = build_cover()
    n_cells = len(cells)
    n_sub_total = sum(c[4] for c in cells)
    print(f"cover: {n_cells} outer cells, {n_sub_total} sub-cells over [0,12]", flush=True)
    ledger, worst = [], None
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        for idx, (lo, hi, cball, hnum, n_sub) in enumerate(cells):
            step = (hi - lo) // n_sub
            jobs = [(j, lo + step * j + step // 2, hi / DEN, cball) for j in range(n_sub)]
            recs = sorted(pool.map(_worker, jobs), key=lambda r: r["index"])
            L, U = enclose_cell(lo, hi, cball, hnum, n_sub, recs)
            am = max(abs(L), abs(U)); margin = 2.0 - am
            row = {"i": idx, "e_lo": lo / DEN, "e_hi": hi / DEN, "n_sub": n_sub,
                   "C": float(arb(cball).mid()), "lower": L, "upper": U,
                   "abs_max": am, "g3_margin": margin,
                   "half_width": (U - L) / 2.0,
                   "status": "PASS" if am < 2.0 else "FAIL"}
            ledger.append(row)
            if worst is None or margin < worst["g3_margin"]: worst = row
            ch = resource.getrusage(resource.RUSAGE_CHILDREN)
            cpu_h = (ch.ru_utime + ch.ru_stime) / 3600.0
            if cpu_h > STOP_CPU_HOURS:
                print(f"RESOURCE STOP at {cpu_h:.1f} CPU-h", flush=True); break
            if idx % 5 == 0 or idx == n_cells - 1:
                print(f"  cell {idx+1}/{n_cells} e=[{lo/DEN:.5f},{hi/DEN:.5f}] "
                      f"|R|max={am:.6f} margin={margin:.6f} cpu={cpu_h:.3f}h", flush=True)
    ch = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu_h = (ch.ru_utime + ch.ru_stime) / 3600.0
    gaps = [(ledger[i]["e_hi"], ledger[i+1]["e_lo"]) for i in range(len(ledger)-1)
            if abs(ledger[i]["e_hi"] - ledger[i+1]["e_lo"]) > 1e-12]
    out = {
        "schema": "rebaseguard.p5x.cusum.production.v1",
        "checkpoint_k": "3704988533f2d9038ddf0b35e58dea0eed4b6a2d",
        "detector": "cusum", "m": 1, "moment": "first (with derivative equation)",
        "e_domain": [0, 12], "den": DEN, "n_sub_per_cell": N_SUB,
        "precision_bits": RA.BITS, "taylor_order": RA.TAYLOR_N, "degree": RA.DEGREE,
        "criterion": "ABS_MAX < 2 strictly (theorem consumer G3); F3=0.2 NOT applied",
        "cells": len(ledger), "sub_cells": sum(r["n_sub"] for r in ledger),
        "all_pass": all(r["status"] == "PASS" for r in ledger),
        "coverage_gaps": gaps,
        "covers_full_domain": (abs(ledger[0]["e_lo"]) < 1e-12
                               and abs(ledger[-1]["e_hi"] - 12.0) < 1e-9 and not gaps),
        "worst_cell": worst,
        "min_g3_margin": min(r["g3_margin"] for r in ledger),
        "max_half_width": max(r["half_width"] for r in ledger),
        "cpu_hours": cpu_h, "wall_hours": (time.time() - t0) / 3600.0,
        "peak_rss_mib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1048576,
        "resource_stop_threshold_cpu_h": STOP_CPU_HOURS,
        "resource_stop_triggered": cpu_h > STOP_CPU_HOURS,
        "second_moment_production": "NOT_RUN",
        "m_gt_1": "NO CERTIFIER EXISTS (see Checkpoint K section 0)",
        "ledger": ledger,
    }
    (NS/"results"/"cusum_m1_production.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"\ncells={out['cells']} sub={out['sub_cells']} all_pass={out['all_pass']} "
          f"min_margin={out['min_g3_margin']:.6f} cpu={cpu_h:.3f}h "
          f"wall={out['wall_hours']:.3f}h gaps={len(gaps)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
