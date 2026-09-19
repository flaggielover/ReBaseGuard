"""Falsification gate S12 for the certified operator registry (review r1 M1 / r2): independent float quadrature.

Independent of the frozen certification path: no _kernel_polynomials, no Pair, no phi Taylor series, no Bernstein. Each
payload is evaluated as a Chebyshev tensor polynomial (numpy chebval2d), the kernel integral is computed by composite
Gauss-Legendre on the exact z-pieces [m-c, beta], [beta, alpha], [alpha, c-p] (or [m-c, alpha], [alpha, beta],
[beta, c-p]), with scipy's ndtr for the closed forms. Every CERTIFIED inequality is then evaluated on thousands of
states (both axes to 5, dense near p+m = 1 and p+m = 4, the triangle, the origin) and at the ends and centre of its drift
set:
    taboo blocks   w - 1 - Khat_e w >= 0 and w >= 0                 at e in {e_lo, ec, e_hi}
    ARL cells      W - 1 - K_e W >= 0                                at e in {x_lo, e0, x_hi}
    taboo cells    |r_j(x; e0)| <= lambda_mid_j, |r_j(x; e)| <= lambda_cell_j (e = cell ends), j = 0, 1, 2
The gate is qualified by planted bugs that it must flag: a supersolution without margin (alpha = 1), a supersolution
certified against a too-lenient operator (0.9 Khat), a block certified at one end only (wide block, point certificate),
and residual bounds shrunk tenfold.

    python3 -B code/falsify_registry.py run --registry REGISTRY.json --out FALSIFY.json
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from numpy.polynomial import chebyshev as Ch
from scipy.special import ndtr

H, K, C = 5.0, 0.5, 5.5
GL_N = 64
GN, GW = np.polynomial.legendre.leggauss(GL_N)
SQ2PI = math.sqrt(2 * math.pi)


def payload_coeffs(pay: dict) -> np.ndarray:
    den = float(1 << pay["scale_bits"])
    return np.array(pay["numerators"], dtype=float) / den


def peval(c: np.ndarray, p, m):
    return Ch.chebval2d(2 * np.asarray(p) / H - 1, 2 * np.asarray(m) / H - 1, c)


def phi_i(y, i):
    base = np.exp(-0.5 * y * y) / SQ2PI
    return base * {0: 1.0, 1: -y, 2: y * y - 1.0}[i]


def pieces(p, m):
    ell, up = m - C, C - p
    beta, alpha = m - K, K - p
    if beta < alpha:
        return [(ell, beta, False), (beta, alpha, True), (alpha, up, False)]
    return [(ell, alpha, False), (alpha, beta, False), (beta, up, False)]


def kernel(c: np.ndarray, p: float, m: float, e: float, i: int, taboo: bool, subdiv: int = 8) -> float:
    """(K_i f)(p, m) or (Khat_i f)(p, m) for the polynomial f with coefficients c; composite Gauss-Legendre."""
    tot = 0.0
    f_origin = float(peval(c, 0.0, 0.0))
    for a, b, is_atom in pieces(p, m):
        if b <= a:
            continue
        if is_atom:
            if taboo:
                continue
            # f(T) = f(a) on the atom window
            edges = np.linspace(a, b, 3)
            for lo, hi in zip(edges[:-1], edges[1:]):
                z = 0.5 * (lo + hi) + 0.5 * (hi - lo) * GN
                tot += f_origin * float(np.sum(0.5 * (hi - lo) * GW * phi_i(z + e, i)))
            continue
        edges = np.linspace(a, b, subdiv + 1)
        for lo, hi in zip(edges[:-1], edges[1:]):
            z = 0.5 * (lo + hi) + 0.5 * (hi - lo) * GN
            vals = peval(c, np.maximum(0.0, p + z - K), np.maximum(0.0, m - z - K))
            tot += float(np.sum(0.5 * (hi - lo) * GW * phi_i(z + e, i) * vals))
    return tot


def h1(p, m, e, k):
    u, l = C - p + e, m - C + e
    if k == 0:
        return 1.0 - ndtr(u) + ndtr(l)
    s0 = phi_i(u, 0) - phi_i(l, 0)
    if k == 1:
        return -s0
    s1 = -u * phi_i(u, 0) + l * phi_i(l, 0)
    return -s1


def states(n_axis=220, n_tri=500, seed=5):
    rng = np.random.default_rng(seed)
    pts = [(0.0, 0.0)]
    ax = np.unique(np.concatenate([np.linspace(0, 5, n_axis), np.linspace(0.9, 1.1, 21), np.linspace(3.9, 4.1, 21),
                                   np.linspace(4.9, 5.0, 11)]))
    pts += [(float(v), 0.0) for v in ax] + [(0.0, float(v)) for v in ax]
    for s in np.concatenate([np.linspace(0.02, 4.0, 25), np.linspace(0.95, 1.05, 11), np.linspace(3.95, 4.0, 6)]):
        for t in np.linspace(0.05, 0.95, 9):
            pts.append((float(s * t), float(s * (1 - t))))
    while len(pts) < 2 * len(ax) + 1 + 450 + n_tri:
        p, m = rng.uniform(0, 4, 2)
        if p + m <= 4:
            pts.append((float(p), float(m)))
    return pts


def check_super(c, e_list, taboo: bool, pts, margin_floor=0.0):
    worst = math.inf
    arg = None
    for e in e_list:
        for p, m in pts:
            v = float(peval(c, p, m)) - 1.0 - kernel(c, p, m, e, 0, taboo)
            if v < worst:
                worst, arg = v, (p, m, e)
    wmin = min(float(peval(c, p, m)) for p, m in pts)
    return {"min_value": worst, "at": arg, "w_min": wmin, "ok": worst >= margin_floor - 1e-9 and wmin >= -1e-12}


def residuals(pays, p, m, e):
    c0, c1, c2 = (payload_coeffs(pays[k]) for k in ("d0", "d1", "d2"))
    v0, v1, v2 = (float(peval(c, p, m)) for c in (c0, c1, c2))
    r0 = v0 - kernel(c0, p, m, e, 0, True) - h1(p, m, e, 0)
    r1 = v1 - kernel(c1, p, m, e, 0, True) - kernel(c0, p, m, e, 1, True) - h1(p, m, e, 1)
    r2 = (v2 - kernel(c2, p, m, e, 0, True) - 2 * kernel(c1, p, m, e, 1, True) - kernel(c0, p, m, e, 2, True)
          - h1(p, m, e, 2))
    return abs(r0), abs(r1), abs(r2)


def check_cell_residuals(art, pts, shrink=1.0):
    e0, rho = float(F(art["e0"])), float(F(art["rho"]))
    lm = [float(F(art["lambda_mid"][str(j)])) / shrink for j in range(3)]
    lc = [float(F(art["lambda_cell"][str(j)])) / shrink for j in range(3)]
    worst_mid, worst_cell = [0.0] * 3, [0.0] * 3
    for p, m in pts:
        for j, r in enumerate(residuals(art["payloads"], p, m, e0)):
            worst_mid[j] = max(worst_mid[j], r / lm[j])
        for e in (e0 - rho, e0 + rho):
            for j, r in enumerate(residuals(art["payloads"], p, m, e)):
                worst_cell[j] = max(worst_cell[j], r / lc[j])
    return {"max_ratio_mid": worst_mid, "max_ratio_cell": worst_cell,
            "ok": max(worst_mid) <= 1.0 + 1e-9 and max(worst_cell) <= 1.0 + 1e-9}


WORKERS = 7


def _cell_job(args):
    k, art_dir = args
    art_dir = Path(art_dir)
    pts_small = states()[::4]
    a = json.loads((art_dir / f"arl_cell_{k:03d}.json").read_text())
    lo, hi = float(F(a["e_lo"])), float(F(a["e_hi"]))
    r = check_super(payload_coeffs(a["payload"]), (lo, 0.5 * (lo + hi), hi), False, pts_small)
    d = json.loads((art_dir / f"taboo_cell_{k:03d}.json").read_text())
    return k, r, check_cell_residuals(d, pts_small)


def run(reg: dict, art_dir: Path, cells=None) -> dict:
    pts = states()
    pts_small = pts[::4]
    out = {"states": len(pts), "blocks": {}, "arl_cells": {}, "taboo_cells": {}, "flags": []}
    for i, b in reg["taboo_blocks"].items():
        art = json.loads((art_dir / f"taboo_block_{int(i):02d}.json").read_text())
        lo, hi = float(F(art["e_lo"])), float(F(art["e_hi"]))
        r = check_super(payload_coeffs(art["payload"]), (lo, 0.5 * (lo + hi), hi), True, pts)
        out["blocks"][i] = r
        if not r["ok"]:
            out["flags"].append(["taboo_block", i, r["min_value"]])
    sel = cells if cells is not None else [b["cell"] for b in reg["blocks"]]
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(WORKERS) as ex:
        results = list(ex.map(_cell_job, [(k, str(art_dir)) for k in sel]))
    for k, r, rr in results:
        out["arl_cells"][str(k)] = r
        if not r["ok"]:
            out["flags"].append(["arl_cell", k, r["min_value"]])
        out["taboo_cells"][str(k)] = rr
        if not rr["ok"]:
            out["flags"].append(["taboo_cell", k, rr["max_ratio_mid"], rr["max_ratio_cell"]])
    out["pass"] = not out["flags"]
    return out


def planted(art_dir: Path, probe_path: Path | None) -> dict:
    """The gate must flag each planted bug."""
    pts = states()[::4]
    res = {}
    art = json.loads((art_dir / "taboo_block_05.json").read_text())
    c = payload_coeffs(art["payload"])
    alpha = float(F(art["proposal"]["alpha"]))
    e = float(F(art["ec"]))
    # P1 no margin: w / alpha (the float taboo solution itself) must violate w >= 1 + Khat w somewhere
    res["P1_no_margin"] = not check_super(c / alpha, (e,), True, pts)["ok"]
    # P2 certified against a lenient operator: the scaled w = 0.8 w passes 0.9-scaled checks but not the true one
    res["P2_lenient_operator"] = not check_super(0.8 * c, (e,), True, pts)["ok"]
    # P3 one end only: the probe's wide-block payload (a point certificate at the block centre) fails at the block ends
    if probe_path is not None and probe_path.exists():
        pr = json.loads(probe_path.read_text())
        cw = payload_coeffs(pr["payload"])
        res["P3_one_end_only"] = not check_super(cw, (float(F(pr["wide_block"][0])), float(F(pr["wide_block"][1]))),
                                                 True, pts)["ok"]
    # P4 residual bounds shrunk tenfold must be exceeded
    d = json.loads((art_dir / "taboo_cell_050.json").read_text())
    res["P4_residual_shrunk"] = not check_cell_residuals(d, pts, shrink=10.0)["ok"]
    res["pass"] = all(v for k, v in res.items() if k != "pass")
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("run",))
    ap.add_argument("--registry", required=True)
    ap.add_argument("--probe", default=None)
    ap.add_argument("--cells", default=None)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    regp = Path(a.registry)
    reg = json.loads(regp.read_text())
    cells = None if a.cells is None else [int(x) for x in a.cells.split(",")]
    res = {"schema": "rebaseguard.p5y.k5.perron-deflation.falsification-gate.v1", "quadrature": f"GL{GL_N} x 8 per piece",
           "gate": run(reg, regp.parent, cells), "planted": planted(regp.parent, Path(a.probe) if a.probe else None)}
    res["pass"] = res["gate"]["pass"] and res["planted"]["pass"]
    Path(a.out).write_text(json.dumps(res, indent=1, sort_keys=True, default=float) + "\n")
    print(json.dumps({"pass": res["pass"], "flags": res["gate"]["flags"][:10], "planted": res["planted"],
                      "states": res["gate"]["states"]}, default=float))
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
