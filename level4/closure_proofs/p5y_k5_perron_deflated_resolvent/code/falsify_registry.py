"""Falsification gate S12 (r2) for the certified operator registry: independent float quadrature against the CERTIFIED claims.

Independent of the certification path: no _kernel_polynomials, no Pair, no phi Taylor series, no Bernstein. A payload is
evaluated as a Chebyshev tensor polynomial (numpy chebval2d); (K_i f)(p, m) = int phi^(i)(z+e) f(T(p,m;z)) dz is computed by
composite Gauss-Legendre on the exact z-pieces [m-c, beta], [beta, alpha], [alpha, c-p] (or [m-c, alpha], [alpha, beta],
[beta, c-p]); the atom piece contributes f(0,0) * int phi^(i) (whole kernel only); closed forms use scipy's ndtr.

Checked against the certified numbers (review r3 B1): on ~5k states -- the whole reachable set, three offsets of the
atom-collapse line p+m = 1 at 401 points each, a band around it, near-axis strips and the edge p+m = 4 -- then refined on a
21x21 local grid around every extreme:
    taboo blocks  min (w - 1 - Khat_e w) >= certified margin at e in {e_lo, ec, e_hi};  w >= 0;  C_T >= max w;  tau >= w(a)
    ARL cells     min (W - 1 - K_e W) >= certified margin at e in {x_lo, e0, x_hi};  Abar >= W(a)
    taboo cells   max |r_j(x; e0)| / lambda_mid_j <= 1,  max |r_j(x; e)| / lambda_cell_j <= 1 (e = cell ends);
                  d_j(0,0) inside the recorded candidate_at_atom ball
Planted bugs the gate must flag: no margin (w / alpha); a localized bump of height 0.02 subtracted near (0.9, 0.1);
a point certificate used on a wide block (probe payload); residual bounds shrunk 1.2x; C_T understated to 0.999 max w;
Abar understated to 0.9999 W(a).

    python3 -B code/falsify_registry.py run --registry REGISTRY.json --probe PROBE.json --out FALSIFY.json [--workers N]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F
from pathlib import Path

import numpy as np
from numpy.polynomial import chebyshev as Ch
from scipy.special import ndtr

H, K, C = 5.0, 0.5, 5.5
GL_N, SUBDIV = 64, 8
GN, GW = np.polynomial.legendre.leggauss(GL_N)
SQ2PI = math.sqrt(2 * math.pi)
TOL = 1e-9
WORKERS = 6


def payload_coeffs(pay: dict) -> np.ndarray:
    den = float(1 << pay["scale_bits"])
    return np.array(pay["numerators"], dtype=float) / den


def peval(c: np.ndarray, p, m):
    return Ch.chebval2d(2 * np.asarray(p, dtype=float) / H - 1, 2 * np.asarray(m, dtype=float) / H - 1, c)


def phi_i(y, i):
    base = np.exp(-0.5 * y * y) / SQ2PI
    return base * {0: 1.0, 1: -y, 2: y * y - 1.0}[i]


def _nodes(a, b, n):
    edges = np.linspace(a, b, n + 1)
    lo, hi = edges[:-1, None], edges[1:, None]
    z = 0.5 * (lo + hi) + 0.5 * (hi - lo) * GN[None, :]
    w = 0.5 * (hi - lo) * GW[None, :]
    return z.ravel(), w.ravel()


def kernel(f, p: float, m: float, e: float, i: int, taboo: bool) -> float:
    """(K_i f)(p, m), or (Khat_i f)(p, m) if taboo; f is a callable f(P, M) on arrays."""
    ell, up = m - C, C - p
    beta, alpha = m - K, K - p
    tot = 0.0
    if beta < alpha:
        segs = [(ell, beta), (alpha, up)]
        if not taboo:
            z, w = _nodes(beta, alpha, 2)
            tot += float(f(np.array([0.0]), np.array([0.0]))[0]) * float(np.sum(w * phi_i(z + e, i)))
    else:
        segs = [(ell, alpha), (alpha, beta), (beta, up)]
    zs, ws = [], []
    for a, b in segs:
        if b > a:
            z, w = _nodes(a, b, SUBDIV)
            zs.append(z)
            ws.append(w)
    z, w = np.concatenate(zs), np.concatenate(ws)
    vals = f(np.maximum(0.0, p + z - K), np.maximum(0.0, m - z - K))
    return tot + float(np.sum(w * phi_i(z + e, i) * vals))


def poly(c):
    return lambda P, M: peval(c, P, M)


def h1(p, m, e, k):
    u, l = C - p + e, m - C + e
    if k == 0:
        return float(1.0 - ndtr(u) + ndtr(l))
    s0 = phi_i(u, 0) - phi_i(l, 0)
    if k == 1:
        return float(-s0)
    return float(-(-u * phi_i(u, 0) + l * phi_i(l, 0)))


def reachable(p, m):
    return p >= 0 and m >= 0 and p <= H and m <= H and (p == 0 or m == 0 or p + m <= 4 + 1e-12)


def states(seed=5):
    rng = np.random.default_rng(seed)
    pts = [(0.0, 0.0)]
    ax = np.unique(np.concatenate([np.linspace(0, 5, 220), np.linspace(0.9, 1.1, 21), np.linspace(3.9, 4.1, 21),
                                   np.linspace(4.9, 5.0, 11)]))
    pts += [(float(v), 0.0) for v in ax] + [(0.0, float(v)) for v in ax]
    for s in np.concatenate([np.linspace(0.02, 4.0, 25), np.linspace(0.95, 1.05, 11), np.linspace(3.95, 4.0, 6)]):
        for t in np.linspace(0.05, 0.95, 9):
            pts.append((float(s * t), float(s * (1 - t))))
    while len(pts) < 2 * len(ax) + 1 + 450 + 500:
        p, m = rng.uniform(0, 4, 2)
        if p + m <= 4:
            pts.append((float(p), float(m)))
    return pts


def dense_states():
    """review r3 B1: the atom-collapse line p+m = 1 (three offsets x 401), a band around it, near-axis strips, p+m = 4."""
    pts = []
    t401 = np.linspace(0, 1, 401)
    for r in (1 - 1e-3, 1.0, 1 + 1e-3):
        pts += [(float(r * t), float(r * (1 - t))) for t in t401]
    for r in np.linspace(0.97, 1.03, 13):
        pts += [(float(r * t), float(r * (1 - t))) for t in np.linspace(0, 1, 101)]
    for d in (1e-3, 5e-3, 1e-2, 2e-2, 5e-2):
        for v in np.linspace(0, 3.9, 80):
            pts += [(d, float(v)), (float(v), d)]
    for r in (4 - 1e-3, 4.0):
        pts += [(float(r * t), float(r * (1 - t))) for t in np.linspace(0, 1, 201)]
    return [x for x in pts if reachable(*x)]


def local_grid(p0, m0, h=0.01, n=21):
    return [(float(p), float(m)) for p in np.linspace(p0 - h, p0 + h, n) for m in np.linspace(m0 - h, m0 + h, n)
            if reachable(float(p), float(m))]


def super_min(f, e_list, taboo, pts):
    best = (math.inf, None)
    for e in e_list:
        for p, m in pts:
            v = float(f(np.array([p]), np.array([m]))[0]) - 1.0 - kernel(f, p, m, e, 0, taboo)
            if v < best[0]:
                best = (v, (p, m, e))
    p0, m0, e0 = best[1]
    for p, m in local_grid(p0, m0):
        v = float(f(np.array([p]), np.array([m]))[0]) - 1.0 - kernel(f, p, m, e0, 0, taboo)
        if v < best[0]:
            best = (v, (p, m, e0))
    return best


def residual_triplet(fs, p, m, e):
    f0, f1, f2 = fs
    P, M = np.array([p]), np.array([m])
    v0, v1, v2 = (float(f(P, M)[0]) for f in fs)
    r0 = v0 - kernel(f0, p, m, e, 0, True) - h1(p, m, e, 0)
    r1 = v1 - kernel(f1, p, m, e, 0, True) - kernel(f0, p, m, e, 1, True) - h1(p, m, e, 1)
    r2 = (v2 - kernel(f2, p, m, e, 0, True) - 2 * kernel(f1, p, m, e, 1, True) - kernel(f0, p, m, e, 2, True)
          - h1(p, m, e, 2))
    return abs(r0), abs(r1), abs(r2)


def residual_max_ratio(fs, lam, e_list, pts):
    best = (0.0, None)
    for e in e_list:
        for p, m in pts:
            r = max(x / l for x, l in zip(residual_triplet(fs, p, m, e), lam))
            if r > best[0]:
                best = (r, (p, m, e))
    p0, m0, e0 = best[1]
    for p, m in local_grid(p0, m0):
        r = max(x / l for x, l in zip(residual_triplet(fs, p, m, e0), lam))
        if r > best[0]:
            best = (r, (p, m, e0))
    return best


# ------------------------------------------------------------------------------------------------ jobs
def _block_job(args):
    path = args
    a = json.loads(Path(path).read_text())
    c = payload_coeffs(a["payload"])
    lo, hi = float(F(a["e_lo"])), float(F(a["e_hi"]))
    pts = states() + dense_states()
    v, at = super_min(poly(c), (lo, 0.5 * (lo + hi), hi), True, pts)
    wvals = peval(c, np.array([x[0] for x in pts]), np.array([x[1] for x in pts]))
    margin = float(F(a["margin_lower_bound"]))
    out = {"min_value": v, "at": at, "certified_margin": margin, "w_min": float(wvals.min()),
           "w_max_sampled": float(wvals.max()), "C_T": float(F(a["C_T"])), "w_at_atom": float(peval(c, 0.0, 0.0)),
           "tau": float(F(a["tau"]))}
    out["ok"] = (v >= margin - TOL and out["w_min"] >= -TOL and out["C_T"] >= out["w_max_sampled"] - TOL
                 and out["tau"] >= out["w_at_atom"] - TOL)
    return Path(path).name, out


def _cell_job(args):
    k, art_dir = args
    art_dir = Path(art_dir)
    pts = states()[::4] + dense_states()
    a = json.loads((art_dir / f"arl_cell_{k:03d}.json").read_text())
    c = payload_coeffs(a["payload"])
    lo, hi = float(F(a["e_lo"])), float(F(a["e_hi"]))
    v, at = super_min(poly(c), (lo, 0.5 * (lo + hi), hi), False, pts)
    arl = {"min_value": v, "at": at, "certified_margin": float(F(a["margin_lower_bound"])),
           "Abar": float(F(a["tau"])), "W_at_atom": float(peval(c, 0.0, 0.0))}
    arl["ok"] = v >= arl["certified_margin"] - TOL and arl["Abar"] >= arl["W_at_atom"] - TOL
    d = json.loads((art_dir / f"taboo_cell_{k:03d}.json").read_text())
    fs = tuple(poly(payload_coeffs(d["payloads"][f"d{j}"])) for j in range(3))
    e0, rho = float(F(d["e0"])), float(F(d["rho"]))
    lm = [float(F(d["lambda_mid"][str(j)])) for j in range(3)]
    lc = [float(F(d["lambda_cell"][str(j)])) for j in range(3)]
    rmid, amid = residual_max_ratio(fs, lm, (e0,), pts)
    rcell, acell = residual_max_ratio(fs, lc, (e0 - rho, e0 + rho), pts)
    inside = []
    for j in range(3):
        lo_j, hi_j = (float(F(x)) for x in d["candidate_at_atom"][f"d{j}"])
        val = float(fs[j](np.array([0.0]), np.array([0.0]))[0])
        inside.append(lo_j - 1e-12 * max(1.0, abs(val)) <= val <= hi_j + 1e-12 * max(1.0, abs(val)))
    tab = {"max_ratio_mid": rmid, "at_mid": amid, "max_ratio_cell": rcell, "at_cell": acell, "atom_values_inside": inside}
    tab["ok"] = rmid <= 1.0 + TOL and rcell <= 1.0 + TOL and all(inside)
    return k, arl, tab


def run(reg: dict, art_dir: Path, cells=None, workers: int = WORKERS) -> dict:
    out = {"states_blocks": len(states() + dense_states()), "states_cells": len(states()[::4] + dense_states()),
           "blocks": {}, "arl_cells": {}, "taboo_cells": {}, "flags": []}
    sel = cells if cells is not None else [b["cell"] for b in reg["blocks"]]
    with ProcessPoolExecutor(workers) as ex:
        blocks = list(ex.map(_block_job, [str(art_dir / f"taboo_block_{int(i):02d}.json") for i in reg["taboo_blocks"]]))
        cellres = list(ex.map(_cell_job, [(k, str(art_dir)) for k in sel]))
    for name, r in blocks:
        out["blocks"][name] = r
        if not r["ok"]:
            out["flags"].append(["taboo_block", name, r])
    for k, arl, tab in cellres:
        out["arl_cells"][str(k)] = arl
        out["taboo_cells"][str(k)] = tab
        if not arl["ok"]:
            out["flags"].append(["arl_cell", k, arl])
        if not tab["ok"]:
            out["flags"].append(["taboo_cell", k, tab])
    out["worst"] = {
        "taboo_block_slack_min": min(r["min_value"] - r["certified_margin"] for r in out["blocks"].values()),
        "arl_cell_slack_min": min(r["min_value"] - r["certified_margin"] for r in out["arl_cells"].values()),
        "taboo_cell_ratio_mid_max": max(r["max_ratio_mid"] for r in out["taboo_cells"].values()),
        "taboo_cell_ratio_cell_max": max(r["max_ratio_cell"] for r in out["taboo_cells"].values())}
    out["pass"] = not out["flags"]
    return out


# ------------------------------------------------------------------------------------------------ planted bugs
def planted(art_dir: Path, probe_path: Path | None) -> dict:
    pts = states()[::4] + dense_states()
    res = {}
    a = json.loads((art_dir / "taboo_block_05.json").read_text())
    c = payload_coeffs(a["payload"])
    alpha = float(F(a["proposal"]["alpha"]))
    lo, hi = float(F(a["e_lo"])), float(F(a["e_hi"]))
    ec = 0.5 * (lo + hi)
    margin = float(F(a["margin_lower_bound"]))
    # P1 no margin
    res["P1_no_margin"] = super_min(poly(c / alpha), (ec,), True, pts)[0] < margin - TOL

    # P2 localized bump of height 0.02 near (0.9, 0.1), width 0.03, subtracted from w
    def bumped(P, M):
        return peval(c, P, M) - 0.02 * np.exp(-((P - 0.9) ** 2 + (M - 0.1) ** 2) / (2 * 0.03 ** 2))
    res["P2_localized_bump"] = super_min(bumped, (ec,), True, pts)[0] < margin - TOL
    # P3 point certificate on a wide block
    if probe_path is not None and probe_path.exists():
        pr = json.loads(probe_path.read_text())
        cw = payload_coeffs(pr["payload"])
        res["P3_point_certificate_on_wide_block"] = super_min(
            poly(cw), (float(F(pr["wide_block"][0])), float(F(pr["wide_block"][1]))), True, pts)[0] < 0.0
    else:
        res["P3_point_certificate_on_wide_block"] = False
    # P4 residual bounds shrunk 1.2x
    flagged = []
    for k in (0, 148):
        d = json.loads((art_dir / f"taboo_cell_{k:03d}.json").read_text())
        fs = tuple(poly(payload_coeffs(d["payloads"][f"d{j}"])) for j in range(3))
        lm = [float(F(d["lambda_mid"][str(j)])) / 1.2 for j in range(3)]
        flagged.append(residual_max_ratio(fs, lm, (float(F(d["e0"])),), pts)[0] > 1.0 + TOL)
    res["P4_lambda_shrunk_1.2"] = all(flagged)
    # P5 / P6 run the real job functions on mutated artifacts (review r4: no tautologies)
    import shutil
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        a5 = dict(a)
        wmax = float(peval(c, np.array([x[0] for x in pts]), np.array([x[1] for x in pts])).max())
        a5["C_T"] = str(F(0.999 * wmax).limit_denominator(10 ** 12))
        (tdp / "taboo_block_05.json").write_text(json.dumps(a5))
        res["P5_C_T_understated"] = _block_job(str(tdp / "taboo_block_05.json"))[1]["ok"] is False
        b = json.loads((art_dir / "arl_cell_050.json").read_text())
        Wa = float(peval(payload_coeffs(b["payload"]), 0.0, 0.0))
        b["tau"] = str(F(0.9999 * Wa).limit_denominator(10 ** 12))
        (tdp / "arl_cell_050.json").write_text(json.dumps(b))
        shutil.copy(art_dir / "taboo_cell_050.json", tdp / "taboo_cell_050.json")
        res["P6_Abar_understated"] = _cell_job((50, td))[1]["ok"] is False
    res["pass"] = all(v for kk, v in res.items() if kk != "pass")
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("run",))
    ap.add_argument("--registry", required=True)
    ap.add_argument("--probe", default=None)
    ap.add_argument("--cells", default=None)
    ap.add_argument("--workers", type=int, default=WORKERS)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    regp = Path(a.registry)
    reg = json.loads(regp.read_text())
    cells = None if a.cells is None else [int(x) for x in a.cells.split(",")]
    res = {"schema": "rebaseguard.p5y.k5.perron-deflation.falsification-gate.v2",
           "quadrature": f"Gauss-Legendre {GL_N} x {SUBDIV} per z-piece", "tolerance": TOL,
           "gate": run(reg, regp.parent, cells, a.workers), "planted": planted(regp.parent, Path(a.probe) if a.probe else None)}
    res["pass"] = res["gate"]["pass"] and res["planted"]["pass"]
    Path(a.out).write_text(json.dumps(res, indent=1, sort_keys=True, default=float) + "\n")
    print(json.dumps({"pass": res["pass"], "flags": res["gate"]["flags"][:5], "worst": res["gate"]["worst"],
                      "planted": res["planted"], "states": [res["gate"]["states_blocks"], res["gate"]["states_cells"]]},
                     default=float))
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
