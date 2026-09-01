"""Fixed-path (common random number) driver for the calibration sensitivity (G9).

The adjudication found the official ``s1`` sensitivity artifact **confounded**:
the variants used different ``policy_id`` values and therefore different RNG
streams, so the measured movement mixed the parameter perturbation with Monte
Carlo path differences.

This module fixes the stochastic paths.  For a given cell, the raw innovations
of **cycle ``j`` of replicate ``r``** are drawn from a generator seeded
deterministically by ``(cell, j)`` alone, and the post-alarm fresh draws from a
matching stream.  **Every variant therefore sees the identical innovation
sequence in every (replicate, cycle)**; the only thing that can differ is the
reuse weight the perturbed constant produces, propagating through ``e``.

That is cycle-level common random numbers -- the "per-(replicate, cycle)
substream" scheme the P6 statistical design named as the stronger coupling
option, and it is exactly what removes the confound.

Scope discipline.  This is a **diagnostic** driver used for no primary claim.
It reuses the **frozen** detector step function imported from the P7 core, and
it implements the frozen convention-A reference update verbatim:

    w = min(m, tau) ,  zbar = mean of the last w innovations ,
    e' = rho (e + zbar) + (1 - rho) * fresh ,   fresh ~ N(0, 1/k) .

It does **not** recalibrate SAW-M and does **not** change any shipped constant.
"""
from __future__ import annotations

import hashlib

import numpy as np

from rebaseguard_p7.detectors import make_step

#: entropy root for the fixed innovation tape.  Fixed; never varied by policy.
_TAPE_ROOT = 0x50365232_43524E          # "P6R2CRN"
#: steps pre-drawn per cycle before the deterministic overflow stream is used
DEFAULT_TAPE_LEN = 2000


def _tag(s: str) -> int:
    return int.from_bytes(hashlib.sha256(s.encode()).digest()[:8], "big")


def cycle_streams(cell_tag: str, cycle: int, n_rep: int, tape_len: int):
    """The innovation tape and fresh draws for one cycle.

    Seeded by ``(cell_tag, cycle)`` ONLY -- never by the policy -- so every
    variant reads the same numbers at the same positions.
    """
    ss = np.random.SeedSequence([_TAPE_ROOT, _tag(cell_tag), int(cycle)])
    rng = np.random.default_rng(ss)
    tape = rng.standard_normal((n_rep, tape_len))
    fresh = rng.standard_normal(n_rep)
    overflow = np.random.default_rng(
        np.random.SeedSequence([_TAPE_ROOT, _tag(cell_tag), int(cycle), 999]))
    return tape, fresh, overflow


def simulate_fixed_path(*, detector: str, decide, m: int, k: int, n_rep: int,
                        n_cycles: int, burn_in: int, cell_tag: str,
                        tape_len: int = DEFAULT_TAPE_LEN, e0: float = 0.0):
    """Run the frozen chain on a FIXED innovation tape.

    ``decide(zbar, tau, w)`` returns the reuse weight per live replicate.  The
    detector, the stopping rule and the convention-A update are the frozen ones.
    Returns per-cycle ``tau``, ``e_start``, ``zbar`` and ``rho`` arrays plus the
    overflow count (draws taken beyond the pre-drawn tape).
    """
    step, thr, log_thr = make_step(detector, None)
    e = np.full(n_rep, float(e0))
    tau = np.zeros((n_rep, n_cycles), np.int64)
    e_start = np.zeros((n_rep, n_cycles))
    zbar_rec = np.zeros((n_rep, n_cycles))
    rho_rec = np.zeros((n_rep, n_cycles))
    n_overflow = 0

    for j in range(n_cycles):
        e_start[:, j] = e
        tape, fresh, overflow = cycle_streams(cell_tag, j, n_rep, tape_len)
        plus = np.zeros(n_rep)
        minus = np.zeros(n_rep)
        buf = np.zeros((n_rep, m))
        t = np.zeros(n_rep, np.int64)
        live = np.ones(n_rep, bool)
        pos = 0
        while live.any():
            idx = np.flatnonzero(live)
            if pos < tape_len:
                x = tape[idx, pos]
            else:
                x = overflow.standard_normal(idx.size)     # deterministic, shared
                n_overflow += idx.size
            z = x - e[idx]
            np_, nm_, cu, cd = step(plus[idx], minus[idx], z)
            plus[idx] = np_
            minus[idx] = nm_
            buf[idx, pos % m] = z
            t[idx] += 1
            pos += 1
            crossed = cu | cd
            if crossed.any():
                done = idx[crossed]
                tau[done, j] = t[done]
                live[done] = False
        # --- frozen convention-A reference update -------------------------
        w = np.minimum(m, tau[:, j])
        cols = np.arange(m)[None, :]
        order = (tau[:, j][:, None] - 1 - cols) % m
        window = np.take_along_axis(buf, order, axis=1)
        valid = cols < w[:, None]
        zbar = np.where(valid, window, 0.0).sum(axis=1) / w
        rho = np.asarray(decide(zbar, tau[:, j].astype(float), w.astype(float)),
                         float)
        e = rho * (e + zbar) + (1.0 - rho) * (fresh / np.sqrt(k))
        zbar_rec[:, j] = zbar
        rho_rec[:, j] = rho

    sl = slice(burn_in, n_cycles)
    return {"tau": tau, "e_start": e_start, "zbar": zbar_rec, "rho": rho_rec,
            "n_overflow_draws": int(n_overflow),
            "arl0": float(tau[:, sl].mean()),
            "rms": float(np.sqrt((e_start[:, sl] ** 2).mean())),
            "rho_mean": float(rho_rec[:, sl].mean()),
            "burn_in": int(burn_in), "n_rep": int(n_rep), "n_cycles": int(n_cycles)}


def saw_decider(g0: float, g1: float, s0: float, s1: float, m: int, k: int,
                s_floor: float = 1e-2, rho_max: float = 0.95):
    """SAW-M's shipped rule, with ``s1`` as the only quantity a variant perturbs."""
    nu = 1.0 / float(k)

    def decide(zbar, tau, w):
        mu = (g0 + g1 / np.sqrt(tau)) * zbar
        s = np.maximum(np.where(w < float(m), s1, s0), s_floor)
        v = mu * mu + s
        return np.minimum(nu / (v + nu), rho_max)

    return decide
