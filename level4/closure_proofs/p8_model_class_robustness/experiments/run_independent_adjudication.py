"""Independent, minimally coupled numerical checks for the P8 adjudication.

This simulator intentionally does not import P8's family, detector, primitive,
window, or estimator implementations.  It uses PCG64DXSM streams and a
shift-register window so that agreement is not a replay of the production
ring-buffer/Philox path.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parents[1]
RESULTS = HERE / "results"
N_BATCHES = 8
N_PATHS = 32_768
WINDOWS = (1, 5, 20)
Z95 = 1.959963984540054

CELLS = (
    ("cusum", "gaussian", 5.0),
    ("sr", "gaussian", 520.886133602749),
    ("cusum", "t3", 6.337011391962933),
    ("sr", "t3", 1676.9656644763495),
    ("cusum", "contam0.05", 7.671712168173407),
    ("sr", "t5", 929.2356243815761),
)


def draw_and_score(rng: np.random.Generator, family: str, n: int):
    if family == "gaussian":
        z = rng.standard_normal(n)
        return z, z
    if family == "t3":
        z = rng.standard_t(3, n) / math.sqrt(3.0)
        return z, 12.0 * z / (3.0 + 3.0 * z * z)
    if family == "t5":
        scale2 = 5.0 / 3.0
        z = rng.standard_t(5, n) / math.sqrt(scale2)
        return z, 6.0 * scale2 * z / (5.0 + scale2 * z * z)
    if family == "contam0.05":
        broad = rng.random(n) < 0.05
        base = rng.standard_normal(n)
        z = np.where(broad, 3.0 * base, base)
        c = math.sqrt(2.0 * math.pi)
        narrow = 0.95 * np.exp(-0.5 * z * z) / c
        wide = 0.05 * np.exp(-0.5 * (z / 3.0) ** 2) / (3.0 * c)
        psi = (narrow * z + wide * z / 9.0) / (narrow + wide)
        return z, psi
    raise ValueError(family)


def one_batch(detector: str, family: str, threshold: float, batch: int):
    code = sum(ord(c) for c in detector + family)
    rng = np.random.Generator(
        np.random.PCG64DXSM(np.random.SeedSequence([0xC0DE8, code, batch]))
    )
    plus = np.zeros(N_PATHS)
    minus = np.zeros(N_PATHS)
    psi_sum = np.zeros(N_PATHS)
    history = np.zeros((N_PATHS, max(WINDOWS)))
    tau = np.zeros(N_PATHS, dtype=np.int64)
    live = np.ones(N_PATHS, dtype=bool)
    t = 0
    while live.any():
        t += 1
        idx = np.flatnonzero(live)
        z, psi = draw_and_score(rng, family, idx.size)
        history[idx, 1:] = history[idx, :-1]
        history[idx, 0] = z
        psi_sum[idx] += psi
        if detector == "cusum":
            p = np.maximum(0.0, plus[idx] + z - 0.5)
            q = np.maximum(0.0, minus[idx] - z - 0.5)
            alarm = (p >= threshold) | (q >= threshold)
            plus[idx], minus[idx] = p, q
        else:
            lp = plus[idx] + z - 0.5
            lm = minus[idx] - z - 0.5
            alarm = (lp >= math.log(threshold)) | (lm >= math.log(threshold))
            plus[idx] = np.logaddexp(0.0, lp)
            minus[idx] = np.logaddexp(0.0, lm)
        if alarm.any():
            done = idx[alarm]
            tau[done] = t
            live[done] = False
        if t > 200_000:
            raise RuntimeError("independent simulator failed to alarm")
    out = {"arl": float(tau.mean()), "max_tau": int(tau.max())}
    for m in WINDOWS:
        w = np.minimum(m, tau)
        zbar = history[:, :m].sum(axis=1) / w
        out[str(m)] = float(np.mean(zbar * psi_sum))
    return out


def production_index():
    matrix = json.loads((RESULTS / "gamma_matrix_E1.json").read_text())
    return {(x["detector"], x["family"]): x for x in matrix["cells"]}


def main():
    production = production_index()
    rows = []
    for detector, family, threshold in CELLS:
        batches = [one_batch(detector, family, threshold, b)
                   for b in range(N_BATCHES)]
        rec = {"detector": detector, "family": family,
               "threshold": threshold, "batches": batches, "per_m": {}}
        for m in WINDOWS:
            values = np.array([b[str(m)] for b in batches])
            mean = float(values.mean())
            se = float(values.std(ddof=1) / math.sqrt(N_BATCHES))
            ref = production[detector, family]["per_m"][str(m)]
            combined = math.sqrt(se * se + ref["gamma_A_se"] ** 2)
            z = (mean - ref["gamma_A"]) / combined
            rec["per_m"][str(m)] = {
                "mean": mean,
                "se": se,
                "ci95": [mean - Z95 * se, mean + Z95 * se],
                "production_mean": ref["gamma_A"],
                "production_se": ref["gamma_A_se"],
                "combined_z": z,
                "within_3_combined_se": bool(abs(z) <= 3.0),
            }
        rows.append(rec)
        print(detector, family, rec["per_m"], flush=True)
    out = {
        "schema": "rebaseguard.p8.independent-adjudication-numerics.v1",
        "simulator": "independent PCG64DXSM/shift-register implementation",
        "n_batches": N_BATCHES,
        "paths_per_batch": N_PATHS,
        "rows": rows,
        "all_within_3_combined_se": all(
            x["within_3_combined_se"]
            for row in rows for x in row["per_m"].values()
        ),
    }
    (RESULTS / "independent_numerical_reproduction.json").write_text(
        json.dumps(out, indent=1) + "\n"
    )


if __name__ == "__main__":
    main()
