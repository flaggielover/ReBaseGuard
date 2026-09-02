"""Implementation self-test, run before the stop-gate is believed.

At e = 0 the P5X equation  g = K_0 g + rho_{1,0}  is *literally* the `a`
equation of the certified Gamma chain (`closure/04_ARB_CERTIFICATE.md` section 3:
a = K a + r_a, r_a = phi(u) - phi(l)), because rho_{1,0} = phi(u) - phi(l).
So this module must reproduce the audited residual for `a`, and must return
ghat(0,0) = 0 (P5-T3: R(0) = 0).  Both are checked here; a discrepancy would
mean the P5X implementation, not the mathematics, is wrong.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
sys.path.insert(0, str(HERE))

from flint import arb                                              # noqa: E402
from rebaseguard_certify.arb_backend import ball_record, workprec  # noqa: E402
from rebaseguard_certify.polynomial import (                       # noqa: E402
    bi_add, bi_eval, bi_scale, chebyshev_payload_to_power,
)
from rebaseguard_certify.residual import (                         # noqa: E402
    _chebyshev_sup, _max_abs_on_reachable, _phi_coefficients, _reward_polynomials,
    construct_candidate_payloads,
)
from drift_certificate import kernel_polynomials, reward_rho1, solve_candidate  # noqa: E402


def residual_at(payload, e_ball, *, phi_order=50, subdivision_depth=3):
    ph = _phi_coefficients(phi_order)
    g = chebyshev_payload_to_power(payload)
    low, high = kernel_polynomials(g, ph, e_ball, z_weight=0)
    rw = reward_rho1(ph, e_ball)
    r_low = bi_add(bi_add(g, bi_scale(low, -arb(1))), bi_scale(rw, -arb(1)))
    r_high = bi_add(bi_add(g, bi_scale(high, -arb(1))), bi_scale(rw, -arb(1)))
    mx, _ = _max_abs_on_reachable(r_low, r_high, subdivision_depth=subdivision_depth)
    return mx, bi_eval(g, arb(0), arb(0)), _chebyshev_sup(payload)


def main() -> None:
    t0 = time.time()
    out: dict = {"schema": "rebaseguard.p5x.selftest.v1",
                 "generated_utc": datetime.now(timezone.utc).isoformat()}
    with workprec(256):
        ph = _phi_coefficients(50)
        reward_ours = reward_rho1(ph, arb(0))
        reward_gamma, _ = _reward_polynomials(ph)
        diff = bi_add(reward_ours, bi_scale(reward_gamma, -arb(1)))
        out["reward_equals_certified_r_a_at_e0"] = all(
            v.contains(arb(0)) for v in diff.values())

        gamma_payload = construct_candidate_payloads(degree=12, quadrature_order=400)
        base_mx, _, _ = residual_at(gamma_payload["a"], arb(0))
        ours = solve_candidate(drift=0.0, degree=12, quadrature_order=400)
        ours_payload = ours.to_chebyshev_dyadic(scale_bits=50)
        our_mx, our_origin, our_sup = residual_at(ours_payload, arb(0))
        out["gamma_a_candidate_residual_e0"] = ball_record(base_mx)
        out["p5x_g_candidate_residual_e0"] = ball_record(our_mx)
        out["p5x_ghat_origin_e0"] = ball_record(our_origin)
        out["p5x_sup_chebyshev_e0"] = ball_record(our_sup)
        out["residuals_agree"] = bool(
            (base_mx - our_mx).abs_upper() < arb(10) ** -12)
        out["ghat_origin_is_zero_to_1e-12"] = bool(our_origin.abs_upper() < arb(10) ** -12)
    out["wall_seconds"] = time.time() - t0
    path = NS / "results" / "selftest_e0.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
