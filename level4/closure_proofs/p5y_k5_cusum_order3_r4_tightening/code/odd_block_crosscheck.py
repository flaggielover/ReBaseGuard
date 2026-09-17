"""R4-B independent cross-check of the odd-block certificate (float; NOT evidence of the bound, a second code path).

Independent of the polynomial piece bookkeeping of odd_block_certificate.py:
  X1  reflection identity: for x in H, (K_o w)(x) is recomputed as the RAW kernel applied to the sigma-odd extension
      u_w(y) = w(y) (y_p > y_m), -w(sigma y) (y_p < y_m), 0 (diagonal, incl. the origin atom), by Gauss-Legendre over the
      survival window with break points at the axis kinks only (no split at -d/2 is assumed);
  X2  supersolution margin L(x) = w - 1 - (K_o w)(x) at a dense deterministic sample of H cap R must be >= the certified
      margin lower bound minus a float tolerance;
  X3  positivity of the reflected kernel phi(z) - phi(-d - z) on z >= -d/2 at sampled (d, z);
  X4  ordering: float odd-block norm estimate (power iteration of the float K_o, non-evidence) <= certified C_o0(R4)
      <= certified C_o0(R3); a certified upper bound below a converged float estimate indicates a defect.
"""
from __future__ import annotations

import math

import numpy as np

K_, C_ = 0.5, 5.5
GN, GW = np.polynomial.legendre.leggauss(160)


def cheb_eval(pay, p, m):
    c = np.asarray(pay["numerators"], dtype=float) / float(1 << int(pay["scale_bits"]))
    return np.polynomial.chebyshev.chebval2d(2 * np.asarray(p) / 5.0 - 1, 2 * np.asarray(m) / 5.0 - 1, c)


def phi(z):
    return np.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)


def odd_extension(pay, yp, ym):
    a = cheb_eval(pay, yp, ym)
    b = cheb_eval(pay, ym, yp)
    return np.where(yp > ym, a, np.where(yp < ym, -b, 0.0))


def raw_odd_apply(pay, p, m):
    lo, hi = m - C_, C_ - p
    cuts = sorted({lo, hi} | {z for z in (K_ - p, m - K_) if lo < z < hi})
    tot = 0.0
    for a, b in zip(cuts[:-1], cuts[1:]):
        c, r = 0.5 * (a + b), 0.5 * (b - a)
        z = c + r * GN
        yp, ym = np.maximum(0.0, p + z - K_), np.maximum(0.0, m - z - K_)
        u = odd_extension(pay, yp, ym)
        # the diagonal crossing z = -d/2 lies inside one sub-interval: split it there for quadrature accuracy only
        if a < (m - p) / 2 < b:
            tot += _split(pay, p, m, a, (m - p) / 2) + _split(pay, p, m, (m - p) / 2, b)
        else:
            tot += float(np.sum(r * GW * phi(z) * u))
    return tot


def _split(pay, p, m, a, b):
    c, r = 0.5 * (a + b), 0.5 * (b - a)
    z = c + r * GN
    yp, ym = np.maximum(0.0, p + z - K_), np.maximum(0.0, m - z - K_)
    return float(np.sum(r * GW * phi(z) * odd_extension(pay, yp, ym)))


def h_samples():
    out = []
    for r in np.concatenate([np.linspace(0.0, 1.0, 21), np.linspace(1.0, 4.0, 61)[1:]]):
        for t in np.linspace(0.5, 1.0, 26):
            out.append((float(r * t), float(r * (1 - t))))
    out += [(float(p), 0.0) for p in np.linspace(4.0, 5.0, 21)]
    return out


def margins(pay):
    rows = []
    for p, m in h_samples():
        w = float(cheb_eval(pay, p, m))
        rows.append((w - 1.0 - raw_odd_apply(pay, p, m), p, m, w))
    return rows


def kernel_positivity(samples: int = 400) -> int:
    bad = 0
    for d in np.linspace(0.0, 5.0, samples // 20):
        z = np.linspace(-d / 2, 5.5, 20)
        bad += int(np.sum(phi(z) - phi(-d - z) < -1e-15))
    return bad


def float_odd_norm(M, n, iters: int = 4000) -> float:
    g = np.ones(n * n)
    acc = np.ones(n * n)
    for _ in range(iters):
        g = M @ g
        acc = acc + g
        if np.max(np.abs(g)) < 1e-14:
            break
    return float(acc.max())


def crosscheck(pay, certified_margin: float, C_R4: float, C_R3: float, M=None, n=None, tol: float = 1e-6) -> dict:
    rows = margins(pay)
    worst = min(rows)
    x2_fail = [r for r in rows if r[0] < certified_margin - tol]
    wmax = max(r[3] for r in rows)
    out = {"X1_X2_samples": len(rows), "X2_float_min_margin": worst[0], "X2_at": [worst[1], worst[2]],
           "X2_violations": len(x2_fail), "X3_negative_reflected_kernel": kernel_positivity(),
           "float_sup_w_on_samples": wmax, "sup_w_le_certified_C": wmax <= C_R4 + tol}
    if M is not None:
        est = float_odd_norm(M, n)
        out["X4_float_odd_norm_estimate"] = est
        out["X4_ordering"] = est <= C_R4 + tol and C_R4 <= C_R3
    out["pass"] = (not x2_fail and out["X3_negative_reflected_kernel"] == 0 and out["sup_w_le_certified_C"]
                   and out.get("X4_ordering", True))
    return out
