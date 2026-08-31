#!/usr/bin/env python3
"""Independent, targeted P5 adjudication checks.

This script deliberately does not import ``rebaseguard_p5``.  It uses the frozen
P7 cycle implementation only as a comparison oracle for the raw-mean identity,
and otherwise restates the two detector recurrences locally.  The long-chain
check records the realised terminal raw mean, avoiding the gridded/PCHIP map
used by the discovery analysis of T11.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

CAMPAIGN = Path(__file__).resolve().parents[1]
ROOT = CAMPAIGN.parents[2]
P7_SRC = ROOT / "level4/closure_proofs/p7_statistical_consequences/src"
sys.path.insert(0, str(P7_SRC))

from rebaseguard_p7.cycles import simulate_cycles as frozen_cycles  # noqa: E402

LOG_A = math.log(520.886133602749)
K = 0.5
H = 5.0


def detector_step(detector: str, plus: np.ndarray, minus: np.ndarray,
                  z: np.ndarray):
    """Local restatement of the frozen inclusive detector recurrences."""
    if detector == "cusum":
        np_ = np.maximum(0.0, plus + z - K)
        nm_ = np.maximum(0.0, minus - z - K)
        return np_, nm_, np_ >= H, nm_ >= H
    lp = plus + z - 0.5
    lm = minus - z - 0.5
    crossed_p = lp >= LOG_A
    crossed_m = lm >= LOG_A
    return np.logaddexp(0.0, lp), np.logaddexp(0.0, lm), crossed_p, crossed_m


def independent_cycles(*, detector: str, e: float, n_paths: int, m_grid,
                       rng: np.random.Generator, max_steps: int = 2_000_000):
    """From-scratch frozen cycles with a terminal buffer of raw observations."""
    m_grid = tuple(int(m) for m in m_grid)
    L = max(m_grid)
    plus = np.zeros(n_paths)
    minus = np.zeros(n_paths)
    raw_buf = np.zeros((n_paths, L))
    pos = np.zeros(n_paths, dtype=np.int64)
    active = np.ones(n_paths, dtype=bool)
    tau = np.zeros(n_paths, dtype=np.int64)
    for t in range(1, max_steps + 1):
        idx = np.flatnonzero(active)
        if not idx.size:
            break
        raw = rng.standard_normal(idx.size)
        np_, nm_, cu, cd = detector_step(detector, plus[idx], minus[idx], raw - e)
        plus[idx], minus[idx] = np_, nm_
        raw_buf[idx, pos[idx] % L] = raw
        pos[idx] += 1
        done = idx[cu | cd]
        if done.size:
            tau[done] = t
            active[done] = False
    else:
        raise RuntimeError("independent cycle simulation did not finish")

    order = (pos[:, None] - 1 - np.arange(L)[None, :]) % L
    lags = np.take_along_axis(raw_buf, order, axis=1)
    csum = np.cumsum(np.where(np.arange(L)[None, :] < tau[:, None], lags, 0.0), axis=1)
    rows = np.arange(n_paths)
    rbar = np.empty((len(m_grid), n_paths))
    for j, m in enumerate(m_grid):
        w = np.minimum(m, tau)
        rbar[j] = csum[rows, w - 1] / w
    return tau, rbar


def raw_identity_audit():
    rows = []
    for detector in ("cusum", "sr"):
        for e in (-1.3, 0.4):
            seed = np.random.SeedSequence([20260831, 11 if detector == "cusum" else 13,
                                           0 if e < 0 else 1])
            a = frozen_cycles(detector=detector, e=e, n_paths=512,
                              m_grid=(1, 2, 3, 5),
                              rng=np.random.Generator(np.random.PCG64(seed)))
            tau, rbar = independent_cycles(
                detector=detector, e=e, n_paths=512, m_grid=(1, 2, 3, 5),
                rng=np.random.Generator(np.random.PCG64(seed)))
            for j, m in enumerate((1, 2, 3, 5)):
                window_gap = float(np.max(np.abs((a.zbar[j] + e) - rbar[j])))
                for rho in (0.0, 0.37, 1.0):
                    fresh_rng = np.random.Generator(np.random.PCG64(
                        np.random.SeedSequence([20260831, j, int(100 * rho), int(e > 0)])))
                    fresh = fresh_rng.standard_normal(512) / math.sqrt(m)
                    legacy = rho * (e + a.zbar[j]) + (1.0 - rho) * fresh
                    raw = rho * rbar[j] + (1.0 - rho) * fresh
                    rows.append({
                        "detector": detector, "m": m, "rho": rho, "e": e,
                        "tau_equal": bool(np.array_equal(a.tau, tau)),
                        "max_window_gap": window_gap,
                        "max_next_state_gap": float(np.max(np.abs(legacy - raw))),
                    })
    return {
        "n_configurations": len(rows),
        "all_tau_equal": all(r["tau_equal"] for r in rows),
        "max_window_gap": max(r["max_window_gap"] for r in rows),
        "max_next_state_gap": max(r["max_next_state_gap"] for r in rows),
        "rows": rows,
    }


def slope_bandwidth_audit():
    """Reanalyse both independent discovery seed families at shrinking bandwidths."""
    p3 = json.loads((ROOT / "level4/closure_proofs/m_rho_stability_priority3/results/boundary_table.json").read_text())
    target = {(r["detector_short"].lower(), int(r["m"])): 1.0 - r["gamma_tilde"]
              for r in p3["rows"] if r["layer"].startswith("GAUSSIAN")}
    out = []
    for filename in ("nonlinear_map.json", "nonlinear_map_rep.json"):
        data = json.loads((CAMPAIGN / "results" / filename).read_text())
        for detector in ("cusum", "sr"):
            by_e = {float(r["e"]): r for r in data["rows"] if r["detector"] == detector}
            for m in (1, 2, 3, 5):
                for h in (0.005, 0.01, 0.02, 0.03, 0.05):
                    qp = next(q for q in by_e[h]["per_m"] if q["m"] == m)
                    qm = next(q for q in by_e[-h]["per_m"] if q["m"] == m)
                    slope = (qp["R"] - qm["R"]) / (2.0 * h)
                    se = math.hypot(qp["R_se"], qm["R_se"]) / (2.0 * h)
                    out.append({
                        "source": filename, "detector": detector, "m": m, "h": h,
                        "slope": slope, "se": se, "p3_slope": target[(detector, m)],
                        "relative_difference": abs(slope - target[(detector, m)]) /
                                               abs(target[(detector, m)]),
                    })
    return out


def independent_chain(*, detector: str, m: int, rho: float, n_rep: int,
                      n_cycles: int, rng: np.random.Generator):
    """Local chain implementation returning entering state and realised Rbar."""
    L = m
    e = np.zeros(n_rep)
    plus = np.zeros(n_rep)
    minus = np.zeros(n_rep)
    buf = np.zeros((n_rep, L))
    pos = np.zeros(n_rep, dtype=np.int64)
    t = np.zeros(n_rep, dtype=np.int64)
    cyc = np.zeros(n_rep, dtype=np.int64)
    states = np.zeros((n_rep, n_cycles + 1))
    rbars = np.zeros((n_rep, n_cycles))
    while np.any(cyc < n_cycles):
        idx = np.flatnonzero(cyc < n_cycles)
        raw = rng.standard_normal(idx.size)
        np_, nm_, cu, cd = detector_step(detector, plus[idx], minus[idx], raw - e[idx])
        plus[idx], minus[idx] = np_, nm_
        buf[idx, pos[idx] % L] = raw
        pos[idx] += 1
        t[idx] += 1
        done = idx[cu | cd]
        if not done.size:
            continue
        w = np.minimum(m, t[done])
        order = (pos[done, None] - 1 - np.arange(L)[None, :]) % L
        lags = np.take_along_axis(buf[done], order, axis=1)
        rbar = np.where(np.arange(L)[None, :] < w[:, None], lags, 0.0).sum(axis=1) / w
        c = cyc[done]
        rbars[done, c] = rbar
        fresh = rng.standard_normal(done.size) / math.sqrt(m)
        e[done] = rho * rbar + (1.0 - rho) * fresh
        states[done, c + 1] = e[done]
        plus[done] = minus[done] = 0.0
        buf[done] = 0.0
        pos[done] = t[done] = 0
        cyc[done] += 1
    return states, rbars


def t11_direct_audit():
    detector, m, rho = "sr", 3, 0.8  # discovery analysis's worst residual
    states, rbars = independent_chain(
        detector=detector, m=m, rho=rho, n_rep=32, n_cycles=5000,
        rng=np.random.Generator(np.random.PCG64(
            np.random.SeedSequence([20260831, 113, 3, 80]))))
    burn = 500
    acfs, directs = [], []
    for e, rbar in zip(states, rbars):
        x = e[burn:-1]
        y = e[burn + 1:]
        rb = rbar[burn:]
        xc = x - x.mean()
        acfs.append(float(np.mean(xc * (y - y.mean())) / np.mean(xc * xc)))
        directs.append(float(rho * np.mean(xc * rb) / np.mean(xc * xc)))
    acfs = np.asarray(acfs)
    directs = np.asarray(directs)
    gap = acfs - directs
    return {
        "detector": detector, "m": m, "rho": rho, "n_rep": 32,
        "post_burn_cycles_per_rep": 4500,
        "acf1_mean": float(acfs.mean()),
        "acf1_se": float(acfs.std(ddof=1) / math.sqrt(acfs.size)),
        "direct_identity_mean": float(directs.mean()),
        "direct_identity_se": float(directs.std(ddof=1) / math.sqrt(directs.size)),
        "paired_gap_mean": float(gap.mean()),
        "paired_gap_se": float(gap.std(ddof=1) / math.sqrt(gap.size)),
        "discovery_pchip_prediction": -0.5315048905313842,
        "discovery_chain_measurement": -0.5488626045170903,
    }


def main():
    result = {
        "seed_family": 20260831,
        "raw_identity": raw_identity_audit(),
        "slope_bandwidths": slope_bandwidth_audit(),
        "t11_direct": t11_direct_audit(),
    }
    out = CAMPAIGN / "results/independent_adjudication.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "raw_identity": {k: v for k, v in result["raw_identity"].items() if k != "rows"},
        "t11_direct": result["t11_direct"],
    }, indent=2))
    print("wrote", out)


if __name__ == "__main__":
    main()
