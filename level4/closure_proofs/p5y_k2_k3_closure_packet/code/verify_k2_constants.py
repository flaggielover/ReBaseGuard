"""Exact-rational replay of every numerical inequality used by Theorem K2 (K2_ADJUDICATION.md s3).

No floating point is used in any assertion. Prints a JSON report; exits non-zero on any failure.
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from math import factorial

A = F("520.886133602749")          # frozen SR threshold (exact decimal)
H, K = F(5), F(1, 2)               # frozen CUSUM h, k


def e_lower(n: int) -> F:
    return sum((F(1, factorial(k)) for k in range(n + 1)), F(0))


def sqrt_e_lower(n: int) -> F:
    return sum((F(1, 2 ** k * factorial(k)) for k in range(n + 1)), F(0))


def kappa_from_M(M: F) -> F:
    return 1 / (12 * M * M)


def report() -> dict:
    checks = {}
    c_cusum = H + K
    checks["c_CUSUM == 11/2"] = c_cusum == F(11, 2)
    G_cusum = 2 * c_cusum
    checks["G_CUSUM == 11"] = G_cusum == 11
    M_cusum = G_cusum / 2 + 2 / G_cusum
    checks["M_CUSUM == 125/22"] = M_cusum == F(125, 22)
    kc = kappa_from_M(M_cusum)
    checks["kappa_CUSUM == 121/46875"] = kc == F(121, 46875)
    # SR: log A < 13/2  <=  A < e^6 * e^(1/2) with rational lower bounds
    e6 = e_lower(6) ** 6
    esq = sqrt_e_lower(4)
    checks["e_lower(6) == 1957/720"] = e_lower(6) == F(1957, 720)
    checks["sqrt_e_lower(4) == 633/384"] = sqrt_e_lower(4) == F(633, 384)
    checks["A < e_lower^6 * sqrt_e_lower  (so log A < 13/2)"] = A < e6 * esq
    checks["lower bound of e^(13/2) exceeds 663"] = e6 * esq > 663
    G_sr_bound = 2 * F(13, 2) + 1
    checks["G_SR bound == 14"] = G_sr_bound == 14
    M_sr = F(7) + F(1, 7)                        # lambda(G/2) <= lambda(7) < 7 + 1/7
    checks["M_SR == 50/7"] = M_sr == F(50, 7)
    ks = kappa_from_M(M_sr)
    checks["kappa_SR == 49/30000"] = ks == F(49, 30000)
    checks["kappa* <= 1/12 (case a>=0 bound dominates)"] = kc <= F(1, 12) and ks <= F(1, 12)
    checks["G >= 2 for both detectors"] = G_cusum >= 2 and G_sr_bound >= 2
    bounds = {f"{d}|m={m}": str(k / (m * m)) for d, k in (("CUSUM", kc), ("SR", ks)) for m in (1, 2, 3, 5)}
    return {"schema": "rebaseguard.p5y.k2.constant-replay.v1", "exact": True, "checks": checks,
            "all_pass": all(checks.values()), "kappa": {"CUSUM": str(kc), "SR": str(ks)},
            "s_min_lower_bounds": bounds}


def main() -> int:
    r = report()
    print(json.dumps(r, indent=1, sort_keys=True))
    return 0 if r["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
