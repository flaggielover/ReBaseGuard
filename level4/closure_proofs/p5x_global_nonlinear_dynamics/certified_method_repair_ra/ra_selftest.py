"""R-A' mandatory self-test.  Must pass before the stop-gate may run.

Five checks, exactly as RA_FROZEN_SPEC.md section 12.1.  S4 is an interval
*containment* test, not a digit-equality test: R-A' and the inherited Gamma
pipeline truncate differently, so equality would be the wrong assertion.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
ROOT = NS.parents[2]
sys.path.insert(0, str(HERE))

from flint import arb                                              # noqa: E402
from rebaseguard_certify.arb_backend import (                      # noqa: E402
    ball_record, gaussian_cdf, rational, workprec,
)
from rebaseguard_certify.polynomial import bi_eval                 # noqa: E402
from rebaseguard_certify.residual import _phi_coefficients         # noqa: E402
import ra_certifier as RA                                          # noqa: E402

GAMMA_A_RESIDUAL = "3.0027342099356678100269439666606576992909146330180751030572988784324151472360720e-6"


def _phi(x: arb) -> arb:
    return (-(x * x) / arb(2)).exp() / (arb(2) * arb.pi()).sqrt()


def main() -> None:
    t0 = time.time()
    out: dict = {"schema": "rebaseguard.p5x.ra.selftest.v1",
                 "generated_utc": datetime.now(timezone.utc).isoformat(),
                 "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                              capture_output=True, text=True).stdout.strip(),
                 "taylor_order": RA.TAYLOR_N, "checks": {}}
    with workprec(RA.BITS):
        # S1 -- coefficient identity at e = 0
        b0 = RA.phi_taylor_coefficients(RA.TAYLOR_N, arb(0))
        plain = _phi_coefficients(RA.TAYLOR_N // 2)
        s1 = all((b0[i] - plain[i]).contains(arb(0)) for i in range(len(plain)))
        s1 = s1 and all(b0[i].contains(arb(0)) for i in range(1, len(plain), 2))
        out["checks"]["S1_coefficient_identity"] = bool(s1)

        # S2 -- recentred reward accuracy against exact Arb phi/Phi
        eps_reward = RA.taylor_remainder(RA.TAYLOR_N, rational(5, 2))
        allow = eps_reward * (arb(1) + rational(5, 2)) * arb(4)
        worst = arb(0)
        for e_num, e_den in ((0, 1), (1, 4)):
            e = rational(e_num, e_den)
            poly = RA.reward_rho1(RA.TAYLOR_N, e)
            for p_n, m_n in ((0, 0), (1, 0), (0, 1), (3, 1), (2, 2), (9, 0), (0, 9)):
                p, m = rational(p_n, 2), rational(m_n, 2)
                u, l = rational(11, 2) - p, m - rational(11, 2)
                exact = (_phi(u + e) - _phi(l + e)
                         - e * (arb(1) - gaussian_cdf(u + e) + gaussian_cdf(l + e)))
                worst = worst.max((bi_eval(poly, p, m) - exact).abs_upper())
        out["checks"]["S2_reward_worst_error"] = ball_record(worst)
        out["checks"]["S2_reward_allowance"] = ball_record(allow)
        out["checks"]["S2_reward_accuracy"] = bool(worst < allow)

        # S3 -- recentred kernel weight accuracy
        eps_z = RA.taylor_remainder(RA.TAYLOR_N, rational(11, 2))
        worst_z = arb(0)
        for e_num, e_den in ((0, 1), (1, 4)):
            e = rational(e_num, e_den)
            coeffs = RA.phi_taylor_coefficients(RA.TAYLOR_N, e)
            for z_n in (-11, -7, -3, 0, 3, 7, 11):
                z = rational(z_n, 2)
                acc = arb(0)
                for c in reversed(coeffs):
                    acc = acc * z + c
                worst_z = worst_z.max((acc - _phi(z + e)).abs_upper())
        out["checks"]["S3_weight_worst_error"] = ball_record(worst_z)
        out["checks"]["S3_weight_allowance"] = ball_record(eps_z)
        out["checks"]["S3_weight_accuracy"] = bool(worst_z < eps_z)

    # S4/S5 -- full certification at e = 0
    rec = RA.certify_at_exact_drift(0, 1, e_hi_for_allowance=0.0)
    with workprec(RA.BITS):
        gamma = arb(GAMMA_A_RESIDUAL)
        gap = (rec["_delta"] - gamma).abs_upper()
        eps_mac_50 = (rational(121, 8) ** 51) / (
            arb(1) * arb(51).gamma() * arb(51) * (arb(2) * arb.pi()).sqrt())
        containment = rec["_delta"] + arb(0, rec["_delta"].upper())
        allow4 = arb(11) * rec["_sup_g"] * (RA.taylor_remainder(RA.TAYLOR_N, rational(11, 2))
                                           + eps_mac_50) + arb(1) / arb(10 ** 5)
        out["checks"]["S4_ra_residual"] = rec["polynomial_residual_value"]
        out["checks"]["S4_ra_delta"] = rec["delta"]
        out["checks"]["S4_gamma_reference"] = GAMMA_A_RESIDUAL
        out["checks"]["S4_gap"] = ball_record(gap)
        out["checks"]["S4_allowance"] = ball_record(allow4)
        out["checks"]["S4_residual_containment"] = bool(gap < allow4)
        g0 = rec["_g0"]
        out["checks"]["S5_ghat_origin"] = rec["ghat_origin"]
        out["checks"]["S5_origin_is_zero"] = bool(g0.abs_upper() < arb(10) ** -12)
    out["delta_derivative_at_e0"] = rec["delta_derivative"]
    out["sup_chebyshev_g"] = rec["sup_chebyshev_g"]
    out["sup_chebyshev_dg"] = rec["sup_chebyshev_dg"]
    out["wall_seconds"] = time.time() - t0
    keys = ("S1_coefficient_identity", "S2_reward_accuracy", "S3_weight_accuracy",
            "S4_residual_containment", "S5_origin_is_zero")
    out["verdict"] = "PASS" if all(out["checks"][k] for k in keys) else "FAIL"
    path = NS / "results" / "ra_selftest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "checks"}, indent=1))
    print(json.dumps(out["checks"], indent=1))


if __name__ == "__main__":
    main()
