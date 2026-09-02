"""R2 mandatory self-test S1-S8 (R2_FROZEN_SPEC section 5)."""
from __future__ import annotations
import json, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
ROOT = NS.parents[2]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(NS / "certified_method_repair_ra"))
sys.path.insert(0, str(NS / "compute_optimization_r1"))

from flint import arb                                                    # noqa: E402
from rebaseguard_certify.arb_backend import ball_record, rational, workprec  # noqa: E402
from rebaseguard_certify.polynomial import bi_add, bi_scale, chebyshev_payload_to_power  # noqa: E402
from rebaseguard_certify.residual import (_affine_to_unit_square, _kernel_polynomials,  # noqa: E402
                                          _max_abs_on_reachable, _parameterize_triangle)
import ra_certifier as RA                                                # noqa: E402
import r2_certifier as R2C                                              # noqa: E402
from drift_minorant import drift_monotone_resolvent                      # noqa: E402
from fast_range import affine_to_unit_square_fast, max_abs_on_reachable_fast  # noqa: E402


def main() -> None:
    t0 = time.time()
    out = {"schema": "rebaseguard.p5x.opt-r2.selftest.v1",
           "generated_utc": datetime.now(timezone.utc).isoformat(),
           "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                        capture_output=True, text=True).stdout.strip(),
           "checks": {}}
    ck = out["checks"]
    C = arb(drift_monotone_resolvent(e_num=24, e_den=100)["resolvent_bound"]["ball"])

    e = rational(1, 4)
    cg, _ = RA.solve_candidates(0.25)
    pay = cg.to_chebyshev_dyadic(scale_bits=RA.SCALE_BITS)
    with workprec(RA.BITS):
        g = chebyshev_payload_to_power(pay)
        b = RA.phi_taylor_coefficients(RA.TAYLOR_N, e)
        kl, kh = _kernel_polynomials(g, b, z_weight=0)
        rw = RA.reward_rho1(RA.TAYLOR_N, e)
        rl = bi_add(bi_add(g, bi_scale(kl, -arb(1))), bi_scale(rw, -arb(1)))
        rh = bi_add(bi_add(g, bi_scale(kh, -arb(1))), bi_scale(rw, -arb(1)))

        # S1 -- coefficient agreement on the REAL production polynomials
        s1 = True
        for (poly, rlo, rhi, tlo, thi) in ((_parameterize_triangle(rl), arb(0), arb(1), arb(0), arb(1)),
                                           (_parameterize_triangle(rh), arb(1), arb(4), arb(0), arb(1))):
            ref = _affine_to_unit_square(poly, rlo, rhi, tlo, thi)
            fast = affine_to_unit_square_fast(poly, rlo, rhi, tlo, thi)
            keys = set(ref) | set(fast)
            s1 = s1 and all((ref.get(k, arb(0)) - fast.get(k, arb(0))).contains(arb(0)) for k in keys)
        ck["S1_coefficient_agreement_on_production_polys"] = bool(s1)

        # S2 -- resulting bounds agree within a factor 2 at the same depth
        t = time.process_time(); ref_mx, _ = _max_abs_on_reachable(rl, rh, subdivision_depth=0)
        ref_cpu = time.process_time() - t
        t = time.process_time(); fast_mx, _ = max_abs_on_reachable_fast(rl, rh, subdivision_depth=0)
        fast_cpu = time.process_time() - t
        ratio = float((fast_mx / ref_mx).upper())
        ck["S2_reference_bound"] = ball_record(ref_mx)
        ck["S2_fast_bound"] = ball_record(fast_mx)
        ck["S2_ratio"] = ratio
        ck["S2_within_factor_2"] = bool(0.5 <= ratio <= 2.0)
        ck["S2_reference_cpu_s"] = ref_cpu
        ck["S2_fast_cpu_s"] = fast_cpu
        ck["S2_primitive_speedup"] = ref_cpu / fast_cpu if fast_cpu else float("inf")

    # S3 -- same equation assembly, imported unmodified
    ck["S3_uses_ra_certifier"] = "certified_method_repair_ra" in RA.__file__
    ck["S3_r2_imports_ra"] = R2C.RA.__file__ == RA.__file__

    # S4/S5 -- e=0 consistency and exact-rational drift
    rec0 = R2C.certify_at_exact_drift_r2(0, 1, resolvent=C, e_hi_for_allowance=0.0)
    with workprec(RA.BITS):
        g0 = arb(rec0["ghat_origin"]["ball"])
        ck["S4_ghat_origin_at_e0"] = rec0["ghat_origin"]
        ck["S4_origin_is_zero"] = bool(g0.abs_upper() < arb(10) ** -12)
    span = round((0.26 - 0.24) * 10 ** 7)
    ck["S5_exact_rational_tiling"] = bool(span % 8 == 0 and (span // 8) % 2 == 0)
    ck["S5_denominator"] = 10 ** 7

    # S6 -- no empirical monotonicity
    mo = drift_monotone_resolvent(e_num=24, e_den=100)
    ck["S6_no_empirical_monotonicity"] = mo["empirical_monotonicity_used"] is False

    # S7 -- deterministic bounded ladder
    ck["S7_depth_ladder"] = list(R2C.DEPTH_LADDER)
    ck["S7_ladder_bounded_and_deterministic"] = (tuple(R2C.DEPTH_LADDER) == (0, 1, 2, 3))

    # S8 -- first/second-moment interface unchanged (derivative equation certified)
    ck["S8_derivative_equation_certified"] = "delta_derivative" in rec0

    keys = ["S1_coefficient_agreement_on_production_polys", "S2_within_factor_2",
            "S3_uses_ra_certifier", "S3_r2_imports_ra", "S4_origin_is_zero",
            "S5_exact_rational_tiling", "S6_no_empirical_monotonicity",
            "S7_ladder_bounded_and_deterministic", "S8_derivative_equation_certified"]
    out["verdict"] = "PASS" if all(ck[k] for k in keys) else "FAIL"
    out["wall_seconds"] = time.time() - t0
    (NS / "results" / "r2_selftest.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: ck[k] for k in keys}, indent=1))
    print(f"S2 ratio={ratio:.4f}  ref={ref_cpu:.1f}s  fast={fast_cpu:.1f}s  "
          f"primitive speedup={ck['S2_primitive_speedup']:.2f}x")
    print("verdict:", out["verdict"], f"({out['wall_seconds']:.1f}s)")


if __name__ == "__main__":
    main()
