"""Seeded vectorized diagnostics. None of this module is proof evidence."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class DiagnosticResult:
    tau: np.ndarray
    z_tau: np.ndarray
    t_tau: np.ndarray
    pre_plus: np.ndarray
    pre_minus: np.ndarray
    terminal_plus: np.ndarray
    terminal_minus: np.ndarray
    arm: np.ndarray

    def summary(self) -> dict[str, float | int | str]:
        rewards = self.z_tau * self.t_tau
        gamma_se = float(np.std(rewards, ddof=1) / np.sqrt(self.tau.size))
        up_fraction = float(np.mean(self.arm == 1))
        return {
            "proof_role": "NON-RIGOROUS DIAGNOSTIC ONLY",
            "n": int(self.tau.size),
            "mean_tau": float(np.mean(self.tau)),
            "arl": float(np.mean(self.tau)),
            "mean_z_tau": float(np.mean(self.z_tau)),
            "mean_t_tau": float(np.mean(self.t_tau)),
            "mean_t_tau_sq": float(np.mean(self.t_tau * self.t_tau)),
            "wald_second_gap": float(
                np.mean(self.t_tau * self.t_tau) - np.mean(self.tau)
            ),
            "gamma": float(np.mean(rewards)),
            "gamma_se": gamma_se,
            "mean_z_tau_sq": float(np.mean(self.z_tau * self.z_tau)),
            "cross_term": float(np.mean(self.z_tau * (self.t_tau - self.z_tau))),
            "up_fraction": up_fraction,
            "down_fraction": 1.0 - up_fraction,
            "alarm_symmetry_gap": 2.0 * up_fraction - 1.0,
        }


def simulate(
    n: int,
    *,
    seed: int,
    k: float = 0.5,
    h: float = 5.0,
    batch_size: int | None = None,
    max_steps: int = 100_000,
) -> DiagnosticResult:
    """Simulate all paths in lockstep so results are batch-size invariant."""

    if n <= 0:
        raise ValueError("n must be positive")
    del batch_size
    rng = np.random.default_rng(seed)
    plus = np.zeros(n)
    minus = np.zeros(n)
    total = np.zeros(n)
    active = np.ones(n, dtype=bool)
    tau = np.zeros(n, dtype=np.int64)
    z_tau = np.zeros(n)
    t_tau = np.zeros(n)
    pre_plus = np.zeros(n)
    pre_minus = np.zeros(n)
    terminal_plus = np.zeros(n)
    terminal_minus = np.zeros(n)
    arm = np.zeros(n, dtype=np.int8)

    for time in range(1, max_steps + 1):
        indices = np.flatnonzero(active)
        if indices.size == 0:
            break
        z = rng.standard_normal(indices.size)
        old_plus = plus[indices]
        old_minus = minus[indices]
        new_plus = np.maximum(0.0, old_plus + z - k)
        new_minus = np.maximum(0.0, old_minus - z - k)
        total[indices] += z
        plus[indices] = new_plus
        minus[indices] = new_minus
        fired = (new_plus >= h) | (new_minus >= h)
        if np.any(fired):
            done = indices[fired]
            tau[done] = time
            z_tau[done] = z[fired]
            t_tau[done] = total[done]
            pre_plus[done] = old_plus[fired]
            pre_minus[done] = old_minus[fired]
            terminal_plus[done] = new_plus[fired]
            terminal_minus[done] = new_minus[fired]
            arm[done] = np.where(new_plus[fired] >= h, 1, -1)
            active[done] = False
    else:
        raise RuntimeError(f"{int(np.sum(active))} paths did not alarm by max_steps")

    return DiagnosticResult(
        tau,
        z_tau,
        t_tau,
        pre_plus,
        pre_minus,
        terminal_plus,
        terminal_minus,
        arm,
    )
