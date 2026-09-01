"""Fixed-primitive simulator: every draw is fetched BY ADDRESS, never by live set.

The repaired contract, and the exact difference from the P6R2 driver:

* P6R2 read the pre-generated tape as ``tape[live_idx, pos]`` -- addressable while
  the tape lasted -- but past the tape it called
  ``overflow.standard_normal(len(live_idx))`` on a shared sequential generator.
  The number of values drawn, and therefore which value reached which replicate,
  depended on **how many replicates were still live**, which depends on the
  policy parameter.  That is the failure the adjudication found.
* Here every step reads the **full column** ``primitives.monitor_column(...,
  index=t, ...)`` for all ``n_rep`` replicates and selects the live ones by
  boolean mask.  Replicate ``r`` receives the value at address ``(r, j, t)``
  whatever else is happening, and observation ``t = 2457`` is served from block
  ``4`` exactly as observation ``t = 3`` is served from block ``0``.  **Overflow
  is not a special case.**

Endogenous trajectories -- entering states, stopping times, terminal windows,
``zbar``, live sets -- are free to diverge across variants.  That divergence is
the expected consequence of perturbing the parameter and is measured, not
prevented.

The detector step is the **frozen** one imported from the P7 core, and the
reference update is the frozen convention-A line.  Nothing about SAW-M changes.
"""
from __future__ import annotations

import numpy as np

from rebaseguard_p7.detectors import make_step

from . import primitives as PR

#: Checkpoint ladder for the consumption-level identity evidence.  Cumulative
#: sums of the monitor reads are recorded at these observation indices, so the
#: evidence reaches DEEP addresses -- 1023 and 2047 are past the 512-wide first
#: block and past the 2000-step tape whose absence broke the P6R2 driver.
LADDER = (0, 1, 2, 3, 4, 5, 6, 7, 15, 31, 63, 127, 255, 511, 1023, 2047)


def saw_decider(g0: float, g1: float, s0: float, s1: float, m: int, k: int,
                s_floor: float = 1e-2, rho_max: float = 0.95):
    """SAW-M's shipped rule.  ``s1`` is the ONLY quantity a variant perturbs."""
    nu = 1.0 / float(k)

    def decide(zbar, tau, w):
        mu = (g0 + g1 / np.sqrt(tau)) * zbar
        s = np.maximum(np.where(w < float(m), s1, s0), s_floor)
        return np.minimum(nu / (mu * mu + s + nu), rho_max)

    return decide


def simulate(*, detector: str, decide, m: int, k: int, n_rep: int,
             n_cycles: int, burn_in: int, e0: float = 0.0,
             ladder=LADDER, max_steps: int = 60_000):
    """Run the frozen chain on the addressable primitive field."""
    step, _thr, _log = make_step(detector, None)
    e = np.full(n_rep, float(e0))

    tau = np.zeros((n_rep, n_cycles), np.int64)
    e_start = np.zeros((n_rep, n_cycles))
    zbar_rec = np.zeros((n_rep, n_cycles))
    rho_rec = np.zeros((n_rep, n_cycles))
    fresh_rec = np.zeros((n_rep, n_cycles))
    ladder = tuple(int(x) for x in ladder)
    lad_pos = {t_: i for i, t_ in enumerate(ladder)}
    ladder_sum = np.zeros((n_rep, n_cycles, len(ladder)))
    ovf_count = np.zeros((n_rep, n_cycles), np.int64)
    max_block = 0

    for j in range(n_cycles):
        e_start[:, j] = e
        plus = np.zeros(n_rep)
        minus = np.zeros(n_rep)
        buf = np.zeros((n_rep, m))
        t_cnt = np.zeros(n_rep, np.int64)
        live = np.ones(n_rep, bool)
        run_mon = np.zeros(n_rep)
        t = 0
        while live.any():
            if t >= max_steps:
                raise RuntimeError(f"cycle {j} exceeded {max_steps} steps")
            # ---- THE REPAIR: full column by address, selected by mask -------
            col = PR.monitor_column(detector, m, k, j, t, n_rep)
            max_block = max(max_block, t // PR.BLOCK_LEN)
            idx = np.flatnonzero(live)
            x = col[idx]                       # value depends on (r, j, t) only
            z = x - e[idx]
            np_, nm_, cu, cd = step(plus[idx], minus[idx], z)
            plus[idx] = np_
            minus[idx] = nm_
            buf[idx, t % m] = z
            t_cnt[idx] += 1
            # consumption-level evidence: cumulative sums at the ladder points
            run_mon[idx] += x
            if t in lad_pos:
                ladder_sum[idx, j, lad_pos[t]] = run_mon[idx]
            if t >= PR.BLOCK_LEN:
                ovf_count[idx, j] += 1
            crossed = cu | cd
            if crossed.any():
                done = idx[crossed]
                tau[done, j] = t_cnt[done]
                live[done] = False
            t += 1
        # ---- frozen convention-A reference update -------------------------
        w = np.minimum(m, tau[:, j])
        cols = np.arange(m)[None, :]
        order = (tau[:, j][:, None] - 1 - cols) % m
        window = np.take_along_axis(buf, order, axis=1)
        zbar = np.where(cols < w[:, None], window, 0.0).sum(axis=1) / w
        rho = np.asarray(decide(zbar, tau[:, j].astype(float), w.astype(float)),
                         float)
        f = PR.fresh(detector, m, k, j, n_rep)
        fresh_rec[:, j] = f
        e = rho * (e + zbar) + (1.0 - rho) * (f / np.sqrt(k))
        zbar_rec[:, j] = zbar
        rho_rec[:, j] = rho

    sl = slice(burn_in, n_cycles)
    return {
        "tau": tau, "e_start": e_start, "zbar": zbar_rec, "rho": rho_rec,
        "fresh": fresh_rec, "ladder_sum": ladder_sum, "ladder": ladder,
        "ovf_count": ovf_count, "max_block_index": int(max_block),
        "n_monitor_draws": int(tau.sum()),
        "n_overflow_draws": int(ovf_count.sum()),
        "n_fresh_draws": int(n_rep * n_cycles),
        "arl0": float(tau[:, sl].mean()),
        "rms": float(np.sqrt((e_start[:, sl] ** 2).mean())),
        "rho_mean": float(rho_rec[:, sl].mean()),
        "n_rep": int(n_rep), "n_cycles": int(n_cycles), "burn_in": int(burn_in),
    }
