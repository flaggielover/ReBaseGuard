"""Policy-driven re-baselining chain over the FROZEN detector core.

The only line that differs from ``rebaseguard_p7.chain.simulate_chain`` is the
reference update, which becomes

    e_{j+1} = rho_j * (e_j + zbar_j) + (1 - rho_j) * fresh_j ,
    zbar_j  = (1/w_j) sum_{r<w_j} z_{tau_j - r} ,   w_j = min(m_j, tau_j) ,
    fresh_j ~ N(0, 1/k_j) ,

with ``(rho_j, m_j, k_j)`` chosen by a policy from the observables of
``policy.CycleObservation``.  Detector recurrences, thresholds, reset, the
stopping rule, the inclusive post-update test and the convention-A truncated
denominator are untouched (DEPENDENCY_LEDGER.md D1-D7, X4).

With a ``ConstantPolicy(rho, m)`` this consumes the RNG stream in exactly the
frozen order, and ``tests/test_correspondence.py`` asserts bit-identical ``tau``
against the P7 chain.

The policy is given its own ``np.random.Generator`` so that a randomised policy
cannot perturb the chain's stream.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

_P7_SRC = Path(__file__).resolve().parents[3] / "p7_statistical_consequences" / "src"
if str(_P7_SRC) not in sys.path:
    sys.path.insert(0, str(_P7_SRC))

from rebaseguard_p7 import CUSUM as _P7_CUSUM          # noqa: E402
from rebaseguard_p7.detectors import make_step         # noqa: E402

from .policy import (                                   # noqa: E402
    CycleObservation, OracleObservation, validate_decision,
)


@dataclass(slots=True)
class PolicyChainResult:
    """Per-cycle record.  All arrays are ``(n_rep, n_cycles)``."""
    tau: np.ndarray
    e_start: np.ndarray          # LATENT: analysis/oracle use only
    direction: np.ndarray
    rho: np.ndarray              # the decision taken at the END of each cycle
    m: np.ndarray
    k: np.ndarray
    zbar: np.ndarray             # observable
    detector: str
    policy_name: str
    policy_class: str
    burn_in: int
    shift: float
    shift_cycle: int

    def post(self, a: np.ndarray) -> np.ndarray:
        return a[:, self.burn_in:]


def simulate_policy_chain(*, detector: str, policy, n_rep: int, n_cycles: int,
                          burn_in: int, rng: np.random.Generator,
                          e0: float | None = 0.0, shift: float = 0.0,
                          shift_cycle: int = -1, m0: int = 1,
                          threshold: float | None = None,
                          policy_rng: np.random.Generator | None = None,
                          max_steps: int = 40_000_000) -> PolicyChainResult:
    """Simulate ``n_rep`` replicates of ``n_cycles`` cycles under ``policy``.

    ``e0`` controls the *initial baseline error* and, with it, whether the
    history channel of OBSERVABILITY_AUDIT.md section 4 is legally observable:

    * ``e0=None`` -- draw ``e_0 ~ N(0, 1/m0)`` per replicate, the deployable
      setting.  ``e_0`` is unknown to the policy, so ``displacement =
      e_j - e_0`` carries no latent information and is supplied.
    * ``e0=<float>`` -- a *known* initial error (P7's finite-cycle convention is
      ``e0=0.0``).  Then ``e_j = e_0 + displacement`` would hand the policy the
      latent state exactly, so ``displacement`` and ``last_move`` are withheld
      (NaN) and a policy declaring ``uses_history`` is refused.

    This asymmetry is a finding of the pre-design, not a configuration detail:
    see OBSERVABILITY_AUDIT.md section 4a and FAILURE_MODE_REGISTER.md F1.
    """
    step, thr, log_thr = make_step(detector, threshold)
    thr_eff = float(thr if detector == _P7_CUSUM else log_thr)
    L = max(int(getattr(policy, "max_m", 1)), 1)
    requires_oracle = bool(getattr(policy, "requires_oracle", False))
    history_observable = e0 is None
    if getattr(policy, "uses_history", False) and not history_observable:
        raise ValueError(
            f"policy {getattr(policy, 'name', policy)!r} uses the history channel "
            "(displacement / last_move), which leaks the latent state when e0 is "
            "known; run with e0=None so that e_0 ~ N(0, 1/m0) is unknown"
        )
    policy.reset(n_rep)
    if policy_rng is None:
        policy_rng = np.random.default_rng(0)
    policy.rng = policy_rng

    if history_observable:
        e = rng.standard_normal(n_rep) / np.sqrt(float(m0))
    else:
        e = np.full(n_rep, float(e0))
    e_origin = e.copy()          # the unknown e_0; never exposed to a policy
    e_prev = e.copy()
    plus = np.zeros(n_rep)
    minus = np.zeros(n_rep)
    buf = np.zeros((n_rep, L))
    pos = np.zeros(n_rep, dtype=np.int64)
    t = np.zeros(n_rep, dtype=np.int64)
    cyc = np.zeros(n_rep, dtype=np.int64)

    # observable bookkeeping
    nan = np.full(n_rep, np.nan)
    prev_tau = np.zeros(n_rep, dtype=np.int64)
    prev_zbar = np.zeros(n_rep)
    prev_rho = np.zeros(n_rep)
    prev_m = np.full(n_rep, L, dtype=np.int64)
    prev_k = np.full(n_rep, L, dtype=np.int64)

    tau = np.zeros((n_rep, n_cycles), dtype=np.int64)
    e_start = np.zeros((n_rep, n_cycles))
    direction = np.zeros((n_rep, n_cycles), dtype=np.int8)
    rho_rec = np.zeros((n_rep, n_cycles))
    m_rec = np.zeros((n_rep, n_cycles), dtype=np.int64)
    k_rec = np.zeros((n_rep, n_cycles), dtype=np.int64)
    zbar_rec = np.zeros((n_rep, n_cycles))

    if shift_cycle == 0 and shift != 0.0:
        e -= shift
    e_start[:, 0] = e
    cols = np.arange(L)

    for _ in range(max_steps):
        live = cyc < n_cycles
        if not live.any():
            break
        idx = np.flatnonzero(live)
        z = rng.standard_normal(idx.size) - e[idx]
        np_, nm_, cu, cd = step(plus[idx], minus[idx], z)
        plus[idx] = np_
        minus[idx] = nm_
        buf[idx, pos[idx] % L] = z
        pos[idx] += 1
        t[idx] += 1

        crossed = cu | cd
        if not crossed.any():
            continue
        done = idx[crossed]
        c = cyc[done]
        tau[done, c] = t[done]
        direction[done, c] = np.where(cu[crossed], np.int8(1), np.int8(-1))

        # --- observables at the alarm -------------------------------------
        order = (pos[done][:, None] - 1 - cols[None, :]) % L
        window = np.take_along_axis(buf[done], order, axis=1)
        window_valid = cols[None, :] < t[done][:, None]
        obs_kw = dict(
            rep=done.copy(),
            cycle=int(c[0]) if c.size and np.all(c == c[0]) else -1,
            tau=t[done].copy(),
            direction=direction[done, c].copy(),
            stat_plus=plus[done].copy(),
            stat_minus=minus[done].copy(),
            overshoot=np.maximum(plus[done], minus[done]) - thr_eff,
            window=window,
            window_valid=window_valid,
            displacement=(e[done] - e_origin[done]) if history_observable
                         else nan[done].copy(),
            last_move=(e[done] - e_prev[done]) if history_observable
                      else nan[done].copy(),
            prev_tau=prev_tau[done].copy(),
            prev_zbar=prev_zbar[done].copy(),
            prev_rho=prev_rho[done].copy(),
            prev_m=prev_m[done].copy(),
            prev_k=prev_k[done].copy(),
        )
        if requires_oracle:
            obs = OracleObservation(e_current=e[done].copy(), shift=float(shift),
                                    **obs_kw)
        else:
            obs = CycleObservation(**obs_kw)

        decision = policy.decide(obs)
        validate_decision(decision, done.size, L)
        rho_j, m_j, k_j = decision.rho, decision.m, decision.k

        # --- frozen reference update, with (rho_j, m_j, k_j) --------------
        w = np.minimum(m_j, t[done])
        valid = (cols[None, :] < w[:, None]) & window_valid
        zbar = np.where(valid, window, 0.0).sum(axis=1) / w

        fresh = rng.standard_normal(done.size) / np.sqrt(k_j)
        e_prev[done] = e[done]
        e[done] = rho_j * (e[done] + zbar) + (1.0 - rho_j) * fresh

        rho_rec[done, c] = rho_j
        m_rec[done, c] = m_j
        k_rec[done, c] = k_j
        zbar_rec[done, c] = zbar
        prev_tau[done] = t[done]
        prev_zbar[done] = zbar
        prev_rho[done] = rho_j
        prev_m[done] = m_j
        prev_k[done] = k_j

        plus[done] = 0.0
        minus[done] = 0.0
        buf[done] = 0.0
        pos[done] = 0
        t[done] = 0
        cyc[done] = c + 1

        nxt = cyc[done]
        go = nxt < n_cycles
        if go.any():
            adv = done[go]
            if shift != 0.0:
                hit = adv[cyc[adv] == shift_cycle]
                if hit.size:
                    e[hit] -= shift
            e_start[adv, cyc[adv]] = e[adv]
    else:
        raise RuntimeError(f"{int((cyc < n_cycles).sum())} replicates unfinished")

    return PolicyChainResult(
        tau=tau, e_start=e_start, direction=direction, rho=rho_rec, m=m_rec,
        k=k_rec, zbar=zbar_rec, detector=detector,
        policy_name=getattr(policy, "name", "unnamed"),
        policy_class=getattr(policy, "policy_class", "implementable"),
        burn_in=int(burn_in), shift=float(shift), shift_cycle=int(shift_cycle),
    )
