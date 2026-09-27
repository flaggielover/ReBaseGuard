"""C2b validation checks that CAN FAIL (each with a planted negative control).

  hessian_fd_check   finite-difference second derivatives of Psi_w (float point evaluator) versus the certificate's
                     rigorous Hessian bounds; control: bounds scaled by 0.05 must be flagged.
  c11_kernel_check   exact P1 vertex kernel versus the independent C11 kernel_apply on an affine w (exact P1);
                     control: a kernel evaluated with a wrong reference value K must mismatch.
"""
from __future__ import annotations

import random
import sys
from fractions import Fraction as F

import c2b_common as CM
import c2b_exact as EX
import c2b_pointeval as PE


def to_int(Wf, Q):
    return [[int(round(v * (1 << Q))) for v in col] for col in Wf]


def hessian_fd_check(N, e, Wf, full, n_cells=60, n_pts=3, seed=7, Q=40, scale=1.0):
    """Returns max over samples of |FD second derivative| / bound, per component, and the number of violations."""
    CM.guard(e)
    S = EX.Setup(N, F(e))
    Wint = to_int(Wf, Q)
    Wq = [[v / (1 << Q) for v in col] for col in Wint]          # the exact dyadic w used by the bound
    Hb = EX.hessian_bounds(S, Wint, full)
    rnd = random.Random(seed)
    sample = rnd.sample(Hb, min(n_cells, len(Hb)))
    sc = 2.0 ** -(EX.P + Q)
    h = 1.0 / N
    d = h / 50
    worst = {"ss": 0.0, "sy": 0.0, "yy": 0.0}
    viol = 0
    ef = float(e)
    for (cell, jj, je, Hss, Hsy, Hyy, err) in sample:
        kind, i, j, ns, ilo, ihi, jlo, jhi, verts = cell
        s0, s1 = ns * h, (ns + 1) * h
        y0, y1 = ilo * h - 0.5 - ef, ihi * h - 0.5 - ef
        if y1 - y0 < 4 * d:          # AXM: y fixed; sample around it (bound still valid on a y-neighbourhood? no)
            y0, y1 = y0, y0          # keep y exactly fixed: only the s-direction is checked there
        B = {"ss": Hss * sc * scale, "sy": Hsy * sc * scale, "yy": Hyy * sc * scale}
        for _ in range(n_pts):
            s = rnd.uniform(s0 + 2 * d, s1 - 2 * d)
            y = rnd.uniform(y0 + 2 * d, y1 - 2 * d) if y1 > y0 else y0
            f = lambda a, b: PE.psi(Wq, N, a, b, full)  # noqa: E731
            c = f(s, y)
            fd = {"ss": (f(s + d, y) - 2 * c + f(s - d, y)) / d ** 2}
            if y1 > y0:
                fd["yy"] = (f(s, y + d) - 2 * c + f(s, y - d)) / d ** 2
                fd["sy"] = (f(s + d, y + d) - f(s + d, y - d) - f(s - d, y + d) + f(s - d, y - d)) / (4 * d * d)
            for k, v in fd.items():
                r = abs(v) / B[k] if B[k] > 0 else (float("inf") if abs(v) > 1e-6 else 0.0)
                worst[k] = max(worst[k], r)
                if abs(v) > B[k] * (1 + 1e-6) + 1e-5:
                    viol += 1
    return {"N": N, "e": str(F(e)), "full": full, "cells_sampled": len(sample), "points_per_cell": n_pts,
            "fd_step": d, "max_ratio_fd_over_bound": worst, "violations": viol, "bound_scale": scale}


def hessian_fd_check_cell(N, e, Wf, full, n_cells=80, n_pts=3, seed=7, Q=40, scale=1.0):
    """CORRECTED FD check (r1).  The bounds of hessian_bounds are claimed on the CELL (p, m in the cell, e fixed),
    not on the whole (s, y) rectangle; the first version (hessian_fd_check) sampled the rectangle, i.e. also points
    with m outside the cell, where the bound is not claimed.  Here points are drawn inside the cell with a margin of
    3 FD steps, so every stencil point stays in the cell.  Triangles: all three components.  p-axis segments: the
    only relevant direction (1,1) in (s,y), compared with Hss + 2 Hsy + Hyy.  m-axis segments: s only."""
    CM.guard(e)
    S = EX.Setup(N, F(e))
    Wint = to_int(Wf, Q)
    Wq = [[v / (1 << Q) for v in col] for col in Wint]
    Hb = EX.hessian_bounds(S, Wint, full)
    rnd = random.Random(seed)
    sample = rnd.sample(Hb, min(n_cells, len(Hb)))
    sc = 2.0 ** -(EX.P + Q)
    h = 1.0 / N
    d = h / 50
    dl = 3 * d / h
    ef = float(e)
    worst, viol, n_eval = {}, 0, 0
    f = lambda a, b: PE.psi(Wq, N, a, b, full)  # noqa: E731
    for (cell, jj, je, Hss, Hsy, Hyy, err) in sample:
        kind, i, j = cell[0], cell[1], cell[2]
        B = {"ss": Hss * sc * scale, "sy": Hsy * sc * scale, "yy": Hyy * sc * scale,
             "axis_p": (Hss + 2 * Hsy + Hyy) * sc * scale}
        for _ in range(n_pts):
            fd = {}
            if kind in ("L", "U"):
                while True:
                    a, b = rnd.uniform(dl, 1 - dl), rnd.uniform(dl, 1 - dl)
                    if (kind == "L" and a + b <= 1 - dl) or (kind == "U" and a + b >= 1 + dl):
                        break
                p, m = (i + a) * h, (j + b) * h
                s, y = p + m, p - 0.5 - ef
                c = f(s, y)
                fd["ss"] = (f(s + d, y) - 2 * c + f(s - d, y)) / d ** 2
                fd["yy"] = (f(s, y + d) - 2 * c + f(s, y - d)) / d ** 2
                fd["sy"] = (f(s + d, y + d) - f(s + d, y - d) - f(s - d, y + d) + f(s - d, y - d)) / (4 * d * d)
            elif kind == "AXP":
                p = (i + rnd.uniform(dl, 1 - dl)) * h
                g = lambda q: f(q, q - 0.5 - ef)  # noqa: E731
                fd["axis_p"] = (g(p + d) - 2 * g(p) + g(p - d)) / d ** 2
            else:
                m = (j + rnd.uniform(dl, 1 - dl)) * h
                y = -0.5 - ef
                fd["ss"] = (f(m + d, y) - 2 * f(m, y) + f(m - d, y)) / d ** 2
            n_eval += 1
            for k, v in fd.items():
                r = abs(v) / B[k] if B[k] > 0 else (float("inf") if abs(v) > 1e-6 else 0.0)
                worst[k] = max(worst.get(k, 0.0), r)
                if abs(v) > B[k] * (1 + 1e-6) + 1e-5:
                    viol += 1
    return {"N": N, "e": str(F(e)), "full": full, "cells_sampled": len(sample), "points": n_eval,
            "fd_step": d, "max_ratio_fd_over_bound": worst, "violations": viol, "bound_scale": scale,
            "sampler": "inside cell, margin 3 FD steps (r1)"}


def c11_kernel_check(N, e, A=F(20), B=F(5, 4), Kref=None, Q=20):
    """Exact P1 vertex kernel of w = A - B m against C11's kernel_apply (independent code).  If Kref is given the
    P1 side is evaluated with a WRONG reference value (negative control): it must mismatch."""
    CM.guard(e)
    sys.path.insert(0, str(CM.C11_CODE))
    import c11_certifier as C11
    S = EX.Setup(N, F(e))
    if Kref is not None:            # planted wrong kernel: rebuild lattices with K' instead of K
        old = EX.K
        EX.K = F(Kref)
        try:
            S = EX.Setup(N, F(e))
        finally:
            EX.K = old
    W = [[int((A - B * F(j, N)) * (1 << Q)) for j in range(S.mesh.cols[i])] for i in range(len(S.mesh.cols))]
    hi = EX.kernel_nodes(S, W, 0, True, True)
    lo = EX.kernel_nodes(S, W, 0, True, False)
    sc = F(1, 1 << (EX.P + Q))
    rnd = random.Random(3)
    pts = rnd.sample(S.mesh.nodes, 25) + [(0, 0), (5 * N, 0), (0, 5 * N)]
    mism, maxw = 0, 0.0
    for (i, j) in pts:
        c = C11.kernel_apply({(0, 0): A, (0, 1): -B}, F(i, N), F(j, N), F(e))
        l, h = lo[(i, j)] * sc, hi[(i, j)] * sc
        if not (l <= c.hi and c.lo <= h):
            mism += 1
        maxw = max(maxw, float(h - l))
    return {"N": N, "e": str(F(e)), "nodes_checked": len(pts), "mismatches": mism, "max_width": maxw,
            "wrong_K": None if Kref is None else str(F(Kref))}
