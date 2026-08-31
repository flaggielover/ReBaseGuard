#!/usr/bin/env python3
"""E6: the stationary law at high resolution — unimodal, bimodal, or metastable?

Per-replicate histograms so that the mode test carries replicate standard
errors, plus residence-time / alternation diagnostics for metastability.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rebaseguard_p5 import RESULTS, SEED_FAMILY, SEED_FAMILY_ALT  # noqa: E402
from rebaseguard_p5.chain import simulate_chain_raw               # noqa: E402
from rebaseguard_p5.kernel import child_rng                       # noqa: E402

CELLS = [("cusum", 1), ("cusum", 3), ("sr", 1), ("sr", 5)]
CELLS_X = [("cusum", 1), ("cusum", 3), ("sr", 1)]
RHOS = (0.3, 0.5, 0.8, 1.0)
RHOS_X = (0.35, 0.40, 0.45, 0.55, 0.60, 0.65, 0.70)
N_REP, N_CYCLES, BURN = 240, 4000, 400
BINS = np.linspace(-4.0, 4.0, 161)
Z = 1.959963984540054


def residence(e):
    """Mean run length of consecutive same-sign entering errors, per replicate."""
    out = []
    for row in e:
        s = np.sign(row)
        s = s[s != 0]
        if s.size < 2:
            out.append(np.nan); continue
        flips = int((s[1:] != s[:-1]).sum())
        out.append(s.size / (flips + 1))
    return np.array(out)


def main(seed_family=SEED_FAMILY, tag=41, out="density.json", cells=None, rhos=None):
    cells = cells or CELLS
    rhos = rhos or RHOS
    an = json.loads((RESULTS / "map_analysis.json").read_text())["cells"]
    rows = []
    for det, m in cells:
        br = [c for c in an if c["detector"] == det and c["m"] == m][0]["branch"]
        for i, rho in enumerate(rhos):
            e0 = np.tile([0.0, 6.0, -6.0], N_REP // 3)
            r = simulate_chain_raw(detector=det, m=m, rho=rho, n_rep=N_REP,
                                   n_cycles=N_CYCLES, burn_in=BURN, e0=e0,
                                   rng=child_rng(seed_family, det, tag + m, i))
            e = r.post(r.e_start)
            H = np.array([np.histogram(row, bins=BINS, density=True)[0]
                          for row in e])
            c = 0.5 * (BINS[1:] + BINS[:-1])
            dens = H.mean(axis=0)
            dse = H.std(axis=0, ddof=1) / np.sqrt(N_REP)
            q = [b for b in br if abs(b["rho"] - rho) < 1e-9]
            estar = q[0]["e_star"] if q and q[0].get("exists") else float("nan")
            i0 = int(np.argmin(np.abs(c)))
            istar = int(np.argmin(np.abs(c - estar))) if np.isfinite(estar) else i0
            # per-replicate contrast: density at +/-e* minus density at 0
            contrast = 0.5 * (H[:, istar] + H[:, 2 * i0 - istar]) - H[:, i0]
            res = residence(e)
            rows.append({
                "detector": det, "m": m, "rho": rho, "e_star": estar,
                "n_rep": N_REP, "n_cycles": N_CYCLES, "burn_in": BURN,
                "centers": c.tolist(), "density": dens.tolist(),
                "density_se": dse.tolist(),
                "dens_at_0": float(dens[i0]), "dens_at_0_se": float(dse[i0]),
                "dens_at_estar": float(0.5 * (dens[istar] + dens[2*i0-istar])),
                "contrast_mean": float(contrast.mean()),
                "contrast_se": float(contrast.std(ddof=1) / np.sqrt(N_REP)),
                "n_interior_local_maxima": int(sum(
                    1 for k in range(4, len(dens) - 4)
                    if dens[k] == max(dens[k-4:k+5]) and dens[k] > 0.05*dens.max())),
                "mean_residence_cycles": float(np.nanmean(res)),
                "residence_se": float(np.nanstd(res, ddof=1)/np.sqrt(N_REP)),
                "alt_rate": float((np.sign(e[:, :-1])*np.sign(e[:, 1:]) < 0).mean()),
                "kurtosis": float(((e - e.mean())**4).mean()/((e**2).mean()**2)),
                "rms": float(np.sqrt((e**2).mean())),
            })
            print(f"{det} m={m} rho={rho}: dens(0)={dens[i0]:.4f}+/-{Z*dse[i0]:.4f}"
                  f"  dens(+/-e*={estar:.2f})={rows[-1]['dens_at_estar']:.4f}"
                  f"  contrast={contrast.mean():+.4f}+/-{Z*rows[-1]['contrast_se']:.4f}"
                  f"  local maxima={rows[-1]['n_interior_local_maxima']}"
                  f"  residence={rows[-1]['mean_residence_cycles']:.3f}"
                  f"  alt={rows[-1]['alt_rate']:.3f} kurt={rows[-1]['kurtosis']:.2f}",
                  flush=True)
    (RESULTS / out).write_text(json.dumps(
        {"seed_family": seed_family, "bins": BINS.tolist(), "rows": rows},
        indent=1))
    print("wrote", out)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--seed-family", type=int, default=SEED_FAMILY)
    p.add_argument("--tag", type=int, default=41)
    p.add_argument("--out", default="density.json")
    p.add_argument("--crossover", action="store_true")
    a = p.parse_args()
    if a.crossover:
        main(a.seed_family, a.tag, a.out, CELLS_X, RHOS_X)
    else:
        main(a.seed_family, a.tag, a.out)
