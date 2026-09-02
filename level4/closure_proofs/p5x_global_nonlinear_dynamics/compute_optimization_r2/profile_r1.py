"""R2 step 1 - profile the R1 certifier.  Measurement, not guesswork.

Only ONE certified path exists (CUSUM, m=1, first moment), so this profiles it
exactly and additionally times each PRIMITIVE separately, so that m>1, SR and
second-moment costs can be composed from measured primitives and operator counts
instead of being guessed.
"""
from __future__ import annotations

import cProfile
import json
import pstats
import subprocess
import sys
import time
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
ROOT = NS.parents[2]
sys.path.insert(0, str(NS / "certified_method_repair_ra"))
sys.path.insert(0, str(NS / "compute_optimization_r1"))

from flint import arb                                                    # noqa: E402
from rebaseguard_certify.arb_backend import rational, workprec           # noqa: E402
from rebaseguard_certify.polynomial import chebyshev_payload_to_power     # noqa: E402
from rebaseguard_certify.residual import _kernel_polynomials, _max_abs_on_reachable  # noqa: E402
import ra_certifier as RA                                                # noqa: E402

BUCKETS = {
    "candidate_solve_numpy": ("_collocation", "solve_candidates", "leggauss", "_basis",
                              "_barycentric_weights", "solve", "to_chebyshev_dyadic",
                              "chebvander2d"),
    "hermite_taylor_coeffs": ("phi_taylor_coefficients", "derivative_coefficients",
                              "taylor_remainder"),
    "cheb_to_power": ("chebyshev_payload_to_power", "chebyshev_basis"),
    "kernel_substitute": ("_substitute_candidate", "tri_pow", "tri_mul", "tri_add"),
    "kernel_phi_multiply": ("_multiply_by_phi",),
    "kernel_integrate_z": ("_integrate_z",),
    "reward_build": ("reward_rho1", "reward_drho1", "_recentred_sites",
                     "_series_at_affine", "_cdf_at_affine"),
    "bernstein_param": ("_parameterize_triangle", "_affine_to_unit_square"),
    "bernstein_transform": ("_power_to_bernstein",),
    "bernstein_subdivide": ("_bernstein_max_abs", "_split_patch", "_split_curve"),
    "poly_bi_primitives": ("bi_mul", "bi_add", "bi_scale", "bi_pow", "bi_eval"),
}


def bucket_of(func_name: str) -> str | None:
    for b, names in BUCKETS.items():
        if func_name in names:
            return b
    return None


def profile_cell(e_num: int, e_den: int) -> dict:
    pr = cProfile.Profile()
    t0, c0 = time.time(), time.process_time()
    pr.enable()
    RA.certify_at_exact_drift(e_num, e_den, e_hi_for_allowance=0.26)
    pr.disable()
    wall, cpu = time.time() - t0, time.process_time() - c0
    st = pstats.Stats(pr, stream=StringIO())
    tot = {}
    for (fn, ln, name), (cc, nc, tt, ct, callers) in st.stats.items():
        b = bucket_of(name)
        if b is None:
            continue
        cur = tot.setdefault(b, {"tottime": 0.0, "ncalls": 0})
        cur["tottime"] += tt
        cur["ncalls"] += nc
    accounted = sum(v["tottime"] for v in tot.values())
    rows = sorted(({"bucket": k, "tottime": v["tottime"], "ncalls": v["ncalls"],
                    "pct_of_cpu": 100.0 * v["tottime"] / cpu} for k, v in tot.items()),
                  key=lambda r: -r["tottime"])
    return {"e": f"{e_num}/{e_den}", "wall_seconds": wall, "cpu_seconds": cpu,
            "accounted_seconds": accounted,
            "unaccounted_pct": 100.0 * (cpu - accounted) / cpu, "buckets": rows}


def time_primitives() -> dict:
    """Cost of one call to each expensive primitive, for the cost model."""
    out = {}
    e = rational(1, 4)
    cand_g, cand_dg = None, None
    t = time.time()
    cand_g, cand_dg = RA.solve_candidates(0.25)
    out["solve_candidates_pair"] = time.time() - t
    pay_g = cand_g.to_chebyshev_dyadic(scale_bits=RA.SCALE_BITS)
    pay_dg = cand_dg.to_chebyshev_dyadic(scale_bits=RA.SCALE_BITS)
    with workprec(RA.BITS):
        t = time.time(); b = RA.phi_taylor_coefficients(RA.TAYLOR_N, e)
        out["phi_taylor_coefficients"] = time.time() - t
        t = time.time(); db = RA.derivative_coefficients(b)
        out["derivative_coefficients"] = time.time() - t
        t = time.time(); g_hat = chebyshev_payload_to_power(pay_g)
        out["chebyshev_payload_to_power"] = time.time() - t
        dg_hat = chebyshev_payload_to_power(pay_dg)
        t = time.time(); kl, kh = _kernel_polynomials(g_hat, b, z_weight=0)
        out["kernel_polynomials_ONE"] = time.time() - t
        t = time.time(); rw = RA.reward_rho1(RA.TAYLOR_N, e)
        out["reward_rho1"] = time.time() - t
        t = time.time(); drw = RA.reward_drho1(RA.TAYLOR_N, e)
        out["reward_drho1"] = time.time() - t
        from rebaseguard_certify.polynomial import bi_add, bi_scale
        res_l = bi_add(bi_add(g_hat, bi_scale(kl, -arb(1))), bi_scale(rw, -arb(1)))
        res_h = bi_add(bi_add(g_hat, bi_scale(kh, -arb(1))), bi_scale(rw, -arb(1)))
        t = time.time(); _max_abs_on_reachable(res_l, res_h, subdivision_depth=3)
        out["max_abs_on_reachable_ONE"] = time.time() - t
    return out


def main() -> None:
    out = {"schema": "rebaseguard.p5x.opt-r2.profile.v1",
           "generated_utc": datetime.now(timezone.utc).isoformat(),
           "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                        capture_output=True, text=True).stdout.strip(),
           "note": "only the CUSUM m=1 first-moment path exists; m>1, SR and "
                   "second-moment costs are composed from measured primitives",
           "config": {"taylor_order": RA.TAYLOR_N, "candidate_degree": RA.DEGREE,
                      "precision_bits": RA.BITS,
                      "subdivision_depth": RA.SUBDIVISION_DEPTH,
                      "quadrature_order": RA.QUADRATURE},
           "cells": [], "primitives": {}}
    for lab, (n, d) in (("near-origin e=0.25", (2500000, 10 ** 7)),
                        ("moderate e=4", (40000000, 10 ** 7))):
        r = profile_cell(n, d)
        r["label"] = lab
        out["cells"].append(r)
        print(f"== {lab}: cpu={r['cpu_seconds']:.1f}s unaccounted={r['unaccounted_pct']:.1f}%", flush=True)
        for b in r["buckets"]:
            print(f"   {b['bucket']:24} {b['tottime']:8.1f}s {b['pct_of_cpu']:6.1f}%  n={b['ncalls']}", flush=True)
    out["primitives"] = time_primitives()
    print("== primitives ==", flush=True)
    for k, v in sorted(out["primitives"].items(), key=lambda kv: -kv[1]):
        print(f"   {k:32} {v:8.2f}s", flush=True)
    (NS / "results" / "r2_profile.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
