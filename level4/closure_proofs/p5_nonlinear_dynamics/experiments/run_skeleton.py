#!/usr/bin/env python3
"""E3: full deterministic-skeleton scan of f_rho(e) = rho * R(e).

Independent of the T9 symmetric-branch algebra, this iterates the *measured*
map (monotone cubic interpolation of R on the union of the main and tail grids,
odd-extended) from many initial conditions and classifies the attractor.  It is
the check that P5 has not mislabelled a period-2 structure that the algebra
predicts but the map does not have, and the search for asymmetric 2-cycles,
higher cycles and cascades on rho in (0, 1].
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rebaseguard_p5 import RESULTS                                # noqa: E402

M_GRID = (1, 2, 3, 5)


def build_R(det, m, main, tail):
    e, R = [], []
    for src in (main, tail):
        for r in src["rows"]:
            if r["detector"] != det:
                continue
            e.append(r["e"])
            R.append([q["R"] for q in r["per_m"] if q["m"] == m][0])
    e = np.array(e)
    R = np.array(R)
    o = np.argsort(e)
    e, R = e[o], R[o]
    # symmetrise (T3 is exact; the estimate is not) and extend flat to 0
    Rs = 0.5 * (R - R[::-1])
    e = np.concatenate([[-64.0], e, [64.0]])
    Rs = np.concatenate([[0.0], Rs, [0.0]])
    f = PchipInterpolator(e, Rs, extrapolate=False)
    return lambda x: np.nan_to_num(f(np.clip(x, -64.0, 64.0)))


def classify(orbit, tol=1e-7):
    """Smallest period <= 16 of the tail of an orbit, or 0 if none."""
    tail = orbit[-64:]
    for p in range(1, 17):
        if np.max(np.abs(tail[p:] - tail[:-p])) < tol:
            return p
    return 0


def main():
    main_j = json.loads((RESULTS / "nonlinear_map.json").read_text())
    tail_j = json.loads((RESULTS / "map_tail.json").read_text())
    rhos = np.round(np.arange(0.01, 1.0001, 0.005), 5)
    inits = np.concatenate([np.linspace(-8, 8, 81), [1e-6, -1e-6, 0.0]])
    cells = []
    for det in ("cusum", "sr"):
        for m in M_GRID:
            R = build_R(det, m, main_j, tail_j)
            rows = []
            for rho in rhos:
                x = inits.copy()
                for _ in range(4000):                      # transient
                    x = rho * R(x)
                orb = np.empty((256, x.size))
                for k in range(256):
                    x = rho * R(x)
                    orb[k] = x
                per = np.array([classify(orb[:, i]) for i in range(x.size)])
                amp = np.abs(orb).max(axis=0)
                # distinct attractors: round the sorted period-p orbit
                sig = {tuple(np.round(np.sort(orb[-16:, i]), 4))
                       for i in range(x.size)}
                rows.append({
                    "rho": float(rho),
                    "periods": sorted(set(int(p) for p in per)),
                    "max_period": int(per.max()),
                    "n_distinct_attractors": len(sig),
                    "amp_max": float(amp.max()),
                    "amp_from_zero": float(np.abs(orb[:, -1]).max()),
                    "amp_from_1e6": float(np.abs(orb[:, -3]).max()),
                })
            cells.append({"detector": det, "m": int(m), "rows": rows})
            per_all = sorted({p for r in rows for p in r["periods"]})
            nat = max(r["n_distinct_attractors"] for r in rows)
            first2 = next((r["rho"] for r in rows if r["max_period"] == 2), None)
            print(f"{det:5s} m={m}  periods seen={per_all}  "
                  f"max distinct attractors={nat}  "
                  f"first rho with period 2 = {first2}  "
                  f"amp@rho=1 = {rows[-1]['amp_max']:.4f}")
    (RESULTS / "skeleton_scan.json").write_text(
        json.dumps({"cells": cells}, indent=1))
    print("wrote skeleton_scan.json")


if __name__ == "__main__":
    main()
