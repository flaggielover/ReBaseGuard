"""E6: an independent reimplementation, used to check representative cells.

This simulator deliberately shares nothing with the production path:

* a different bit generator (``PCG64DXSM``, not ``Philox``);
* an entropy source **outside** the P8R address system entirely, so agreement
  cannot be a replay of the same field;
* its own inline family draws and location scores, not
  ``rebaseguard_p8r.families``;
* its own CUSUM and SR recurrences, not ``rebaseguard_p8r.detectors``;
* a shift-register window, not the production ring buffer.

It reads production only to compare.  Cells and windows are frozen below and in
``PRODUCTION_PLAN.md`` §6 before any production result existed.

Usage:  run_independent_repro.py
"""
from __future__ import annotations

import hashlib
import math
import time

import numpy as np

import _common as C                                              # noqa: E402
from rebaseguard_p8r.config import (COMBINED_Z_TOLERANCE,        # noqa: E402
                                     E6_REPRO_BATCHES,
                                     E6_REPRO_PATHS, RESULTS, Z95)

WINDOWS = (1, 5, 20)

#: representative cells: the two Gaussian anchors, the heavy-tail pair whose
#: interpretation is contested, and two mid-tail / contaminated controls.
CELLS = (("cusum", "gaussian"), ("sr", "gaussian"),
         ("cusum", "t3"), ("sr", "t3"),
         ("cusum", "contam0.05"), ("sr", "t5"))


def _entropy(detector: str, family: str, batch: int) -> list[int]:
    h = hashlib.sha256(
        f"p8r-independent-reimplementation|{detector}|{family}|{batch}"
        .encode()).digest()
    return [int.from_bytes(h[i:i + 8], "big") for i in (0, 8, 16, 24)]


def draw_and_score(rng: np.random.Generator, family: str, n: int):
    """Inline family draw and location score psi = -f'/f, independently coded."""
    if family == "gaussian":
        z = rng.standard_normal(n)
        return z, z
    if family in ("t3", "t5", "t10"):
        nu = int(family[1:])
        a2 = nu / (nu - 2.0)
        z = rng.standard_t(nu, n) / math.sqrt(a2)
        return z, (nu + 1.0) * a2 * z / (nu + a2 * z * z)
    if family.startswith("contam"):
        ec = float(family[6:])
        broad = rng.random(n) < ec
        base = rng.standard_normal(n)
        z = np.where(broad, 3.0 * base, base)
        c = math.sqrt(2.0 * math.pi)
        narrow = (1.0 - ec) * np.exp(-0.5 * z * z) / c
        wide = ec * np.exp(-0.5 * (z / 3.0) ** 2) / (3.0 * c)
        return z, (narrow * z + wide * z / 9.0) / (narrow + wide)
    raise ValueError(family)


def one_batch(detector: str, family: str, threshold: float, batch: int,
              n_paths: int):
    rng = np.random.Generator(
        np.random.PCG64DXSM(np.random.SeedSequence(_entropy(detector, family,
                                                            batch))))
    plus = np.zeros(n_paths)
    minus = np.zeros(n_paths)
    psi_sum = np.zeros(n_paths)
    history = np.zeros((n_paths, max(WINDOWS)))
    tau = np.zeros(n_paths, dtype=np.int64)
    live = np.ones(n_paths, dtype=bool)
    log_thr = math.log(threshold) if detector == "sr" else None
    t = 0
    while live.any():
        t += 1
        idx = np.flatnonzero(live)
        z, psi = draw_and_score(rng, family, idx.size)
        history[idx, 1:] = history[idx, :-1]          # shift register
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
            alarm = (lp >= log_thr) | (lm >= log_thr)
            plus[idx] = np.logaddexp(0.0, lp)
            minus[idx] = np.logaddexp(0.0, lm)
        if alarm.any():
            done = idx[alarm]
            tau[done] = t
            live[done] = False
        if t > 500_000:
            raise RuntimeError("independent simulator failed to alarm")
    out = {"arl": float(tau.mean()), "max_tau": int(tau.max())}
    for m in WINDOWS:
        w = np.minimum(m, tau)
        out[str(m)] = float(np.mean(history[:, :m].sum(axis=1) / w * psi_sum))
    return out


def main() -> None:
    prod = {(c["detector"], c["family"]): c
            for c in C.load_payload(RESULTS / "gamma_matrix_E1.json")["cells"]}
    rows, t0 = [], time.time()
    for detector, family in CELLS:
        ref_cell = prod[(detector, family)]
        if ref_cell["status"] != "OK":
            continue
        thr = ref_cell["threshold"]
        batches = [one_batch(detector, family, thr, b, E6_REPRO_PATHS)
                   for b in range(E6_REPRO_BATCHES)]
        for m in WINDOWS:
            v = np.array([b[str(m)] for b in batches])
            mean = float(v.mean())
            se = float(v.std(ddof=1) / math.sqrt(v.size))
            ref = ref_cell["per_m"][str(m)]
            z = ((mean - ref["gamma_A"])
                 / math.sqrt(se ** 2 + ref["gamma_A_se"] ** 2))
            rows.append({"detector": detector, "family": family, "m": m,
                         "gamma_A": mean, "se": se,
                         "ci95": [mean - Z95 * se, mean + Z95 * se],
                         "production": ref["gamma_A"],
                         "production_se": ref["gamma_A_se"], "z": z,
                         "within": bool(abs(z) <= COMBINED_Z_TOLERANCE)})
        print(f"  {detector}/{family} arl="
              f"{np.mean([b['arl'] for b in batches]):.2f} "
              f"[{time.time() - t0:.0f}s]", flush=True)
    payload = {"note": ("independent bit generator, entropy source, family "
                        "code, detector recurrences and window structure; "
                        "reads production only to compare"),
               "bit_generator": "PCG64DXSM",
               "n_batches": E6_REPRO_BATCHES,
               "paths_per_batch": E6_REPRO_PATHS,
               "cells": [list(c) for c in CELLS], "windows": list(WINDOWS),
               "tolerance_combined_se": COMBINED_Z_TOLERANCE,
               "seconds": time.time() - t0, "rows": rows}
    C.write(RESULTS / "independent_reproduction.json",
            C.envelope(generator="run_independent_repro.py",
                       schema="rebaseguard.p8r.independent-reproduction.v1",
                       tags=[], payload=payload))
    ok = sum(r["within"] for r in rows)
    print(f"DONE independent reproduction: {ok}/{len(rows)} within "
          f"{COMBINED_Z_TOLERANCE} combined SE")


if __name__ == "__main__":
    main()
