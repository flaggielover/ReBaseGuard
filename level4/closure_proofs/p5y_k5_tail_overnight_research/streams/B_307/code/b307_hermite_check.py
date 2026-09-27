"""GH: float-level identity checks of the likelihood-ratio / Hermite representation used in REAL_ORDER3_THEORY.md.

(1) One-step kernel derivatives of the frozen CUSUM map (H = 5, K = 1/2, c = H + K = 11/2), at the DECLARED drifts
    e in {0, 1/4, 1/2, 1, 3} only (ov_quarantine.guard_drift on each):
        d^i/de^i (K_e g)(p,m)  ==  int_{m-c}^{c-p} g(T(p,m;z)) He_i(S) phi(z+e) dz,   S = -(z+e),
    for g = 1 and g = post-state coordinate p' = max(0, p+z-K), i = 1..4.  Left side: closed forms differentiated by
    truncated Taylor-jet arithmetic (exact up to rounding); right side: composite Gauss-Legendre quadrature.
(2) The j-step Gaussian-location identity behind  h_j^(n)(x) = E_x[1{tau=j} j^{n/2} He_n(M_j/sqrt j)]:
        d^n/de^n prod_k phi(u_k)  ==  j^{n/2} He_n(M/sqrt j) prod_k phi(u_k),  u_k = z_k + e,  M = -sum u_k,
    at seeded random points, j = 1..4, n = 1..4 (pointwise algebraic identity, checked with jets).
(3) kappa_n = E|He_n(Y)|, n = 1..4 (reference values for the LR h-tower bound ||h_j^(n)|| <= kappa_n j^{n/2}).
Negative controls: (1) with the (-1)^i sign dropped (He_i(z+e)); (2) with the variance-j rescaling dropped
(He_n(M) instead of j^{n/2} He_n(M/sqrt j)).  Both must be detected.
Writes NS/validation/B307_HERMITE_IDENTITY.json.  Class NONTARGET_DRIFT_VALIDATION.  Float only: not a certificate.
"""
from __future__ import annotations

import json
import math
import random
import sys
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[2]
sys.path.insert(0, str(NS / "code"))
import ov_quarantine as Q  # noqa: E402

Q.install_import_guard()

H, KK = 5.0, 0.5
CC = H + KK
ORDER = 5  # jets carry derivatives 0..4


def he(n, x):
    a, b = 1.0, x
    if n == 0:
        return a
    for k in range(1, n):
        a, b = b, x * b - k * a
    return b


def phi(u):
    return math.exp(-u * u / 2) / math.sqrt(2 * math.pi)


def Phi(u):
    return 0.5 * math.erfc(-u / math.sqrt(2))


# --------------------------------------------------------------------- Taylor jets in the drift increment eps
def jmul(a, b):
    return [sum(a[i] * b[k - i] for i in range(k + 1)) for k in range(ORDER)]


def jadd(a, b, s=1.0):
    return [x + s * y for x, y in zip(a, b)]


def jet_phi(u0):
    """Taylor coefficients of phi(u0 + eps): phi^(k)(u0)/k! = (-1)^k He_k(u0) phi(u0) / k!."""
    return [(-1) ** k * he(k, u0) * phi(u0) / math.factorial(k) for k in range(ORDER)]


def jet_Phi(u0):
    return [Phi(u0)] + [(-1) ** (k - 1) * he(k - 1, u0) * phi(u0) / math.factorial(k) for k in range(1, ORDER)]


def jet_lin(c0, c1):
    return [c0, c1] + [0.0] * (ORDER - 2)


def derivs(jet):
    return [math.factorial(k) * jet[k] for k in range(ORDER)]


# --------------------------------------------------------------------- quadrature
GL_X = [-0.9739065285171717, -0.8650633666889845, -0.6794095682990244, -0.4333953941292472, -0.1488743389816312,
        0.1488743389816312, 0.4333953941292472, 0.6794095682990244, 0.8650633666889845, 0.9739065285171717]
GL_W = [0.0666713443086881, 0.1494513491505806, 0.2190863625159820, 0.2692667193099963, 0.2955242247147529,
        0.2955242247147529, 0.2692667193099963, 0.2190863625159820, 0.1494513491505806, 0.0666713443086881]


def integrate(f, a, b, pieces=200):
    h = (b - a) / pieces
    tot = 0.0
    for i in range(pieces):
        lo = a + i * h
        mid, half = lo + h / 2, h / 2
        tot += half * sum(w * f(mid + half * x) for x, w in zip(GL_X, GL_W))
    return tot


def one_step(p, m, e, i, g, sign_ok=True):
    lo, hi = m - CC, CC - p
    kink = KK - p
    def integrand(z):
        s = -(z + e)
        w = he(i, s) if sign_ok else he(i, z + e)
        return g(p, m, z) * w * phi(z + e)
    pts = sorted({lo, hi, min(max(kink, lo), hi)})
    return sum(integrate(integrand, a, b) for a, b in zip(pts, pts[1:]) if b > a)


def closed_form_jets(p, m, e, which):
    if which == "one":
        return jadd(jet_Phi(CC - p + e), jet_Phi(m - CC + e), -1.0)
    # g = p' = max(0, p + z - K) on z in [K - p, c - p]:  (p - K - e)[Phi(b) - Phi(a)] + phi(a) - phi(b)
    a0, b0 = KK - p + e, CC - p + e
    dPhi = jadd(jet_Phi(b0), jet_Phi(a0), -1.0)
    return jadd(jmul(jet_lin(p - KK - e, -1.0), dPhi), jadd(jet_phi(a0), jet_phi(b0), -1.0))


G_FUN = {"one": lambda p, m, z: 1.0, "post_p": lambda p, m, z: max(0.0, p + z - KK)}


def main():
    drifts = [Fr(0), Fr(1, 4), Fr(1, 2), Fr(1), Fr(3)]
    states = [(0, 0), (1, 0), (0, 1), (2, 1), (3, 0), (0, 4)]
    rows, worst, nc_detected, nc_total = [], 0.0, 0, 0
    for ef in drifts:
        Q.guard_drift(ef)
        e = float(ef)
        for (p, m) in states:
            for which in ("one", "post_p"):
                d = derivs(closed_form_jets(p, m, e, which))
                for i in range(1, 5):
                    lr = one_step(p, m, e, i, G_FUN[which])
                    err = abs(lr - d[i]) / max(1.0, abs(d[i]))
                    worst = max(worst, err)
                    rows.append({"e": str(ef), "state": [p, m], "g": which, "i": i, "closed_form": d[i],
                                 "hermite_lr": lr, "rel_err": err})
                    if i % 2 == 1:
                        bad = one_step(p, m, e, i, G_FUN[which], sign_ok=False)
                        nc_total += 1
                        if abs(bad - d[i]) / max(1.0, abs(d[i])) > 1e-6:
                            nc_detected += 1
    # (2) j-step Gaussian-location identity at random points
    rng = random.Random(20260928)
    worst2, nc2, nc2_total = 0.0, 0, 0
    for j in range(1, 5):
        for _ in range(25):
            u = [rng.uniform(-3, 3) for _ in range(j)]
            jet = [1.0] + [0.0] * (ORDER - 1)
            val = 1.0
            for uk in u:
                jet = jmul(jet, jet_phi(uk))
                val *= phi(uk)
            d = derivs(jet)
            M = -sum(u)
            for n in range(1, 5):
                lr = j ** (n / 2) * he(n, M / math.sqrt(j)) * val
                worst2 = max(worst2, abs(lr - d[n]) / max(1e-300, abs(val)))
                if j >= 2:
                    nc2_total += 1
                    if abs(he(n, M) * val - d[n]) / max(1e-300, abs(val)) > 1e-6:
                        nc2 += 1
    # (3) kappa_n
    kap = {n: integrate(lambda y, n=n: abs(he(n, y)) * phi(y), -12.0, 12.0, pieces=2400) for n in range(1, 5)}
    out = {
        "schema": "P5Y_K5_TAIL_OVERNIGHT_B307_HERMITE_IDENTITY/1",
        "producer": "streams/B_307/code/b307_hermite_check.py",
        "class": "NONTARGET_DRIFT_VALIDATION",
        "float_only_not_a_certificate": True,
        "drifts": [str(x) for x in drifts], "states": states,
        "one_step": {"cases": len(rows), "worst_rel_err": worst,
                     "negative_control_sign_dropped": {"detected": nc_detected, "of": nc_total}},
        "j_step_location_identity": {"points": 100, "orders": [1, 2, 3, 4], "worst_rel_err": worst2,
                                     "negative_control_no_variance_rescaling": {"detected": nc2, "of": nc2_total}},
        "kappa_n_E_abs_He_n": kap,
        "rows": rows,
    }
    with open(NS / "validation" / "B307_HERMITE_IDENTITY.json", "w") as fh:
        json.dump(out, fh, indent=1)
    Q.log_execution("streams/B_307/code/b307_hermite_check.py",
                    "B307 GH: Hermite/LR identity of CUSUM kernel derivatives at declared drifts {0,1/4,1/2,1,3}",
                    cells_touched=[], klass="NONTARGET_DRIFT_VALIDATION",
                    notes=f"worst one-step {worst:.2e}; j-step {worst2:.2e}; NC {nc_detected}/{nc_total}, {nc2}/{nc2_total}")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
