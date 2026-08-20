"""Common Phase-4B stopping-time diagnostic summaries."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class StoppingSample:
    tau: np.ndarray
    z_tau: np.ndarray
    t_tau: np.ndarray
    arm: np.ndarray

    def summary(self, *, detector: str) -> dict[str, float | int | str]:
        n = int(self.tau.size)
        rewards = self.z_tau * self.t_tau
        gamma = float(np.mean(rewards))
        gamma_se = float(np.std(rewards, ddof=1) / np.sqrt(n))
        arl = float(np.mean(self.tau))
        arl_se = float(np.std(self.tau, ddof=1) / np.sqrt(n))
        plus_fraction = float(np.mean(self.arm == 1))
        minus_fraction = float(np.mean(self.arm == -1))
        tie_fraction = float(np.mean(self.arm == 2))
        return {
            "proof_role": "NON-RIGOROUS PHASE-4B DIAGNOSTIC ONLY",
            "detector": detector,
            "n": n,
            "arl": arl,
            "arl_se": arl_se,
            "gamma": gamma,
            "gamma_se": gamma_se,
            "gamma_ci95_lower": gamma - 1.959963984540054 * gamma_se,
            "gamma_ci95_upper": gamma + 1.959963984540054 * gamma_se,
            "fprime": 1.0 - gamma,
            "fprime_se": gamma_se,
            "mean_z_tau": float(np.mean(self.z_tau)),
            "mean_t_tau": float(np.mean(self.t_tau)),
            "mean_t_tau_sq": float(np.mean(self.t_tau * self.t_tau)),
            "wald_second_gap": float(np.mean(self.t_tau * self.t_tau) - arl),
            "mean_z_tau_sq": float(np.mean(self.z_tau * self.z_tau)),
            "cross_term": float(np.mean(self.z_tau * (self.t_tau - self.z_tau))),
            "plus_fraction": plus_fraction,
            "minus_fraction": minus_fraction,
            "tie_fraction": tie_fraction,
            "direction_symmetry_gap": plus_fraction - minus_fraction,
        }

