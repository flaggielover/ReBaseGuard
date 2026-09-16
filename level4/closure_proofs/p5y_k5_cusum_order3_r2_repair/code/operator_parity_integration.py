"""Real CUSUM Arb kernels at drift e = 0 on SYNTHETIC polynomials: the parity structure the graded method relies on.
NON-SCIENTIFIC. No collocation, candidate solve, DAG object, source term, record or R''' value.

Checks, at reachable states x (R1 real_operator_integration.reachable_states):
  P1 operator parity   K_i(0)[f o sigma](x) = (-1)^i K_i(0)[f](sigma x),  i = 0..3, both sides as frozen Arb
                       kernel enclosures; the balls must agree within both radii plus both truncation allowances
                       Z_RANGE * sup|f| * eps_z(i); cross-checked against independent float quadrature
  P2 graded range      for the rung-3 residual of synthetic polynomials at e = 0: the certified graded ranges
                       (cusum_graded.graded_range) dominate |(r(x) + s r(sigma x))/2| from float quadrature, s = +-1
"""
from __future__ import annotations

import sys
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parents[0]
for _p in (str(NS / "code"), str(CP / "p5y_k5_cusum_order3_real_producer/code"),
           str(CP / "p5y_k1_cusum_aux5_successor/code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import real_operator_integration as ROI  # noqa: E402  (R1, frozen)
from rebaseguard_certify.polynomial import bi_eval  # noqa: E402
from intervals import exact, workprec  # noqa: E402
from flint import arb  # noqa: E402
from cusum_layer2 import Pair, Z_RANGE  # noqa: E402

import cusum_graded as CG  # noqa: E402
import rung3_residual as RR  # noqa: E402

TOL = 1e-8


def run(seed: int, *, bits: int = 256) -> dict:
    cell = {"detector": "CUSUM", "index": -1, "e0": ["0"], "rho": ["1/1000"], "left": ["-1/1000"], "right": ["1/1000"],
            "C_upper": "2"}
    pays = ROI.synthetic_payloads(seed)
    states = ROI.reachable_states()
    p1, p2 = [], []
    with workprec(bits):
        cert = ROI.SyntheticOperatorCert(cell, bits=bits).setup(pays)
        f = cert.P["F", 1, 0]
        sf = cert.sup["F", 1, 0]
        fs = CG.swap_poly(f)
        for i in range(4):
            a = cert.K(fs, i)
            b = cert.K(f, i)
            allow = float((Z_RANGE * sf * cert.eps_zi(i)).upper())
            for p, m, branch in states:
                lhs = bi_eval(getattr(a, branch), exact(p), exact(m))
                rhs = bi_eval(getattr(b, branch), exact(m), exact(p)) * arb((-1) ** i)
                gap = abs(float(lhs.mid()) - float(rhs.mid())) - float(lhs.rad()) - float(rhs.rad())
                fl = ROI.K_float(pays[("F", 1, 0)], i, float(m), float(p), 0.0) * (-1) ** i
                p1.append({"i": i, "p": str(p), "m": str(m), "gap_beyond_radii": gap, "allow": allow,
                           "float_gap": abs(float(lhs.mid()) - fl) - float(lhs.rad()),
                           "ok": gap <= 2 * allow + TOL and abs(float(lhs.mid()) - fl) - float(lhs.rad()) <= allow + TOL})
        out = RR.g_residual(cert, 1)
        ge, go, gt = CG.graded_range(cert, cert.last_residual)
        allow = float(out["truncation_allowance"].upper())
        for p, m, _b in states:
            r1 = ROI.residual_float(pays, float(p), float(m), 0.0)
            r2 = ROI.residual_float(pays, float(m), float(p), 0.0)
            e_val, o_val = abs(r1 + r2) / 2, abs(r1 - r2) / 2
            p2.append({"p": str(p), "m": str(m), "even": e_val, "odd": o_val,
                       "ok": e_val <= float(ge.upper()) + allow + TOL and o_val <= float(go.upper()) + allow + TOL})
    return {"seed": seed, "P1_operator_parity_all_ok": all(x["ok"] for x in p1), "P1_checks": len(p1),
            "P1_max_gap_beyond_radii": max(x["gap_beyond_radii"] for x in p1),
            "P2_graded_range_all_ok": all(x["ok"] for x in p2), "P2_checks": len(p2),
            "graded_range": {"even": float(ge.upper()), "odd": float(go.upper()), "total": float(gt.upper())},
            "P1": p1, "P2": p2}


if __name__ == "__main__":
    r = run(int(sys.argv[1]) if len(sys.argv) > 1 else 5)
    print({k: v for k, v in r.items() if k not in ("P1", "P2")})
