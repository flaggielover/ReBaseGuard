"""Real-operator integration of the rung-3 residual on SYNTHETIC polynomials. NON-SCIENTIFIC.

`rung3_residual.g_residual` is run on the frozen CUSUM Arb primitives: `_kernel_polynomials` with the order-120
recentred phi^(i) series (i = 0..3), `Pair`, the reachable-continuum Bernstein range `max_abs_on_reachable_fast`,
the frozen truncation allowances `eps_zi`, and the drift-aware norm table. The arguments G, F, D, H, S3 are
SYNTHETIC degree-12 dyadic Chebyshev polynomials (smooth test functions on the state square), not DAG objects.
Nothing here is a candidate for, or an approximation of, any R_(D,m) derivative, and the drift is a synthetic
exact rational, not a frozen cover cell. No collocation, Layer-1 solve or K1 record is used.

Independent check: the same residual is evaluated in float at sample states by adaptive Gauss-Legendre quadrature
of the defining integrals

    K_i f(p, m) = int_(m - c)^(c - p) f(max(0, p + z - k), max(0, m - z - k)) phi^(i)(z + e) dz,
    phi^(i) = (-1)^i He_i phi,   k = 1/2, c = 11/2,

split at the kinks z = k - p and z = m - k, at states of the reachable set the frozen range covers (triangle
p + m <= 4, low branch for p + m <= 1 and high branch above, plus the tails (p, 0), (0, m) with p, m in [4, 5]).
Two conditions: (a) pointwise, the Arb residual branch evaluated at the state encloses the float residual within the
certified truncation allowance plus a float quadrature tolerance; (b) delta_mid dominates every sampled |residual|.
"""
from __future__ import annotations

import math
import sys
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parents[0]
for _p in (str(NS / "code"), str(CP / "p5y_k1_cusum_aux5_successor/code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import ancestry5                                                       # noqa: E402,F401

import numpy as np                                                     # noqa: E402
from flint import arb                                                  # noqa: E402

import cusum_layer1 as L1                                              # noqa: E402
from cusum_layer2 import CellCertifier, Pair, Z_RANGE                  # noqa: E402  (sets the RA path)
import ra_certifier as RA                                              # noqa: E402
import sharp_norms                                                     # noqa: E402
from intervals import exact, workprec                                  # noqa: E402
from rebaseguard_certify.polynomial import bi_eval, chebyshev_payload_to_power  # noqa: E402
from rebaseguard_certify.residual import _chebyshev_sup                # noqa: E402

import rung3_residual as RR                                            # noqa: E402

K_ = 0.5
C_ = 5.5


class SyntheticOperatorCert(CellCertifier):
    """CellCertifier's operator/range surface only; `prepare` (collocation, DAG) is never called."""

    vec = staticmethod(Pair)
    z_range = Z_RANGE

    def setup(self, payloads: dict):
        e = exact(self.e0)
        self.b = [RA.phi_taylor_coefficients(self.order, e)]
        for _ in range(3):
            self.b.append(RA.derivative_coefficients(self.b[-1]))
        self.eps_z = RA.taylor_remainder(self.order, exact(F(11, 2)))
        self.norms = sharp_norms.table(self.left, self.right)
        self.reward_allow = {3: arb(0)}
        self.P, self.sup, self.payloads = {}, {}, payloads
        for key, pay in payloads.items():
            self.P[key] = chebyshev_payload_to_power(pay)
            self.sup[key] = _chebyshev_sup(pay)
        return self

    def certify(self, name, residual, extra, envelope):
        self.last_residual = residual                    # retained for the pointwise comparison only
        return super().certify(name, residual, extra, envelope)


FLOAT_TOL = 1e-8


def reachable_states() -> list[tuple[F, F, str]]:
    out = []
    for r in (F(0), F(1, 2), F(1), F(2), F(3), F(4)):
        for t in (F(0), F(1, 4), F(1, 2), F(3, 4), F(1)):
            out.append((r * t, r * (1 - t), "lo" if r <= 1 else "hi"))
    for x in (F(9, 2), F(5)):
        out += [(x, F(0), "hi"), (F(0), x, "hi")]
    return out


def synthetic_payloads(seed: int) -> dict:
    n = L1.DEGREE + 1
    x = np.cos(np.pi * np.arange(n) / L1.DEGREE)
    nodes = 0.5 * L1.H_FROZEN * (1.0 - x)
    P, M = np.meshgrid(nodes, nodes, indexing="ij")
    out = {}
    for idx, fam in enumerate(("G", "F", "D", "H")):
        a = 0.3 + 0.1 * ((seed + idx) % 5)
        vals = np.cos(a * P + 0.2 * (idx + 1) * M) * np.exp(-0.05 * (P + M)) * (1 + idx)
        out[(fam, 1, 0)] = L1.dyadic_candidate(vals.ravel(), n)
    vals = np.sin(0.4 * P - 0.3 * M + seed) * 0.5
    out[("S", 1, 3)] = L1.dyadic_candidate(vals.ravel(), n)
    return out


def cheb_eval(pay: dict, p: float, m: float) -> float:
    c = np.asarray(pay["numerators"], dtype=float) / float(1 << int(pay["scale_bits"]))
    u, v = 2.0 * p / L1.H_FROZEN - 1.0, 2.0 * m / L1.H_FROZEN - 1.0
    return float(np.polynomial.chebyshev.chebval2d(u, v, c))


def he(i: int, y: float) -> float:
    return [1.0, y, y * y - 1.0, y ** 3 - 3.0 * y][i]


def K_float(pay: dict, i: int, p: float, m: float, e: float, nodes: int = 96) -> float:
    lo, hi = m - C_, C_ - p
    cuts = sorted({lo, hi, *(z for z in (K_ - p, m - K_) if lo < z < hi)})
    gn, gw = np.polynomial.legendre.leggauss(nodes)
    total = 0.0
    for a, b in zip(cuts[:-1], cuts[1:]):
        mid, rad = 0.5 * (a + b), 0.5 * (b - a)
        for t, w in zip(gn, gw):
            z = mid + rad * t
            y = z + e
            dens = (-1) ** i * he(i, y) * math.exp(-0.5 * y * y) / math.sqrt(2 * math.pi)
            total += rad * w * dens * cheb_eval(pay, max(0.0, p + z - K_), max(0.0, m - z - K_))
    return total


def residual_float(pays: dict, p: float, m: float, e: float) -> float:
    val = cheb_eval(pays[("G", 1, 0)], p, m)
    for c, i, fam in RR.TERMS:
        val -= c * K_float(pays[(fam, 1, 0)], i, p, m, e)
    return val - cheb_eval(pays[("S", 1, 3)], p, m)


def run(seed: int, e0: F, rho: F, *, bits: int = 256) -> dict:
    cell = {"detector": "CUSUM", "index": -1, "e0": [str(e0)], "rho": [str(rho)],
            "left": [str(e0 - rho)], "right": [str(e0 + rho)], "C_upper": "2"}
    pays = synthetic_payloads(seed)
    rows = []
    with workprec(bits):
        cert = SyntheticOperatorCert(cell, bits=bits).setup(pays)
        out = RR.g_residual(cert, 1)
        allow = float(out["truncation_allowance"].upper())
        for p, m, branch in reachable_states():
            poly = getattr(cert.last_residual, branch)
            ball = bi_eval(poly, exact(p), exact(m))
            fl = residual_float(pays, float(p), float(m), float(e0))
            gap = abs(float(ball.mid()) - fl) - float(ball.rad())
            rows.append({"p": str(p), "m": str(m), "branch": branch, "arb_mid": float(ball.mid()),
                         "float": fl, "gap_beyond_radius": gap, "ok": gap <= allow + FLOAT_TOL})
    delta_mid = float(out["delta_mid"].upper())
    worst = max(abs(x["float"]) for x in rows)
    return {"seed": seed, "e0": str(e0), "rho": str(rho), "bits": bits,
            "delta_mid": delta_mid, "polynomial_residual": float(out["polynomial_residual"].upper()),
            "truncation_allowance": allow, "delta_cell": float(out["delta_cell"].upper()),
            "cpu_seconds": out["cpu_seconds"], "states": len(rows),
            "pointwise_all_ok": all(x["ok"] for x in rows),
            "max_gap_beyond_radius": max(x["gap_beyond_radius"] for x in rows),
            "float_sampled_max_abs_residual": worst,
            "dominates": delta_mid >= worst * (1 + 1e-9) + FLOAT_TOL, "pointwise": rows}


if __name__ == "__main__":
    res = run(int(sys.argv[1]) if len(sys.argv) > 1 else 1, F(1, 3), F(1, 1000))
    print({k: v for k, v in res.items() if k != "pointwise"})
