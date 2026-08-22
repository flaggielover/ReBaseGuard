"""Route A: raw-state CUSUM stopped-location-gain implementation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .frozen import K


@dataclass(frozen=True, slots=True)
class ScorePaths:
    tau: np.ndarray
    terminal: np.ndarray
    psi_total: np.ndarray
    direction: np.ndarray
    ties: int
    simultaneous_crossings: int

    @property
    def gain(self) -> np.ndarray:
        return self.terminal * self.psi_total


def draw_innovations(
    family: str, rng: np.random.Generator, size: int
) -> np.ndarray:
    if family == "gaussian":
        return rng.standard_normal(size)
    if family.startswith("t"):
        nu = int(family[1:])
        scale = np.sqrt(nu / (nu - 2.0))
        return rng.standard_t(nu, size=size) / scale
    if family.startswith("contam"):
        eps = float(family.removeprefix("contam"))
        broad = rng.random(size) < eps
        z = rng.standard_normal(size)
        return np.where(broad, 3.0 * z, z)
    raise ValueError(f"unknown family: {family}")


def location_score(family: str, z: np.ndarray) -> np.ndarray:
    """Conventional location score psi=-f'/f, not the e-parameter score."""
    z = np.asarray(z, dtype=float)
    if family == "gaussian":
        return z
    if family.startswith("t"):
        nu = int(family[1:])
        scale_sq = nu / (nu - 2.0)
        return (nu + 1.0) * scale_sq * z / (nu + scale_sq * z * z)
    if family.startswith("contam"):
        eps = float(family.removeprefix("contam"))
        narrow = (1.0 - eps) * np.exp(-0.5 * z * z) / np.sqrt(2.0 * np.pi)
        broad = eps * np.exp(-0.5 * (z / 3.0) ** 2) / (
            3.0 * np.sqrt(2.0 * np.pi)
        )
        return (narrow * z + broad * z / 9.0) / (narrow + broad)
    raise ValueError(f"unknown family: {family}")


def log_density(family: str, z: np.ndarray) -> np.ndarray:
    """Independent analytic density helper for deterministic score tests."""
    z = np.asarray(z, dtype=float)
    if family == "gaussian":
        return -0.5 * z * z - 0.5 * np.log(2.0 * np.pi)
    if family.startswith("t"):
        from scipy.special import gammaln

        nu = int(family[1:])
        scale = np.sqrt(nu / (nu - 2.0))
        y = scale * z
        constant = (
            gammaln((nu + 1.0) / 2.0)
            - gammaln(nu / 2.0)
            - 0.5 * np.log(nu * np.pi)
            + np.log(scale)
        )
        return constant - 0.5 * (nu + 1.0) * np.log1p(y * y / nu)
    if family.startswith("contam"):
        eps = float(family.removeprefix("contam"))
        narrow = (1.0 - eps) * np.exp(-0.5 * z * z) / np.sqrt(2.0 * np.pi)
        broad = eps * np.exp(-0.5 * (z / 3.0) ** 2) / (
            3.0 * np.sqrt(2.0 * np.pi)
        )
        return np.log(narrow + broad)
    raise ValueError(f"unknown family: {family}")


def trace_raw(path: np.ndarray, threshold: float) -> tuple[int, float, float, int]:
    plus = 0.0
    minus = 0.0
    psi_sum = 0.0
    for time, z_raw in enumerate(np.asarray(path, dtype=float), start=1):
        z = float(z_raw)
        plus = max(0.0, plus + z - K)
        minus = max(0.0, minus - z - K)
        psi_sum += z  # deterministic trace is the Gaussian control
        crossed_plus = plus >= threshold
        crossed_minus = minus >= threshold
        if crossed_plus or crossed_minus:
            direction = int(crossed_plus) - int(crossed_minus)
            return time, z, psi_sum, direction
    raise RuntimeError("path did not alarm")


def simulate_score_batch(
    *,
    family: str,
    threshold: float,
    n_paths: int,
    rng: np.random.Generator,
    max_steps: int = 4_000_000,
) -> ScorePaths:
    plus = np.zeros(n_paths)
    minus = np.zeros(n_paths)
    psi_total = np.zeros(n_paths)
    active = np.ones(n_paths, dtype=bool)
    tau = np.zeros(n_paths, dtype=np.int64)
    terminal = np.zeros(n_paths)
    direction = np.zeros(n_paths, dtype=np.int8)
    ties = 0
    simultaneous = 0

    for step in range(1, max_steps + 1):
        idx = np.flatnonzero(active)
        if idx.size == 0:
            break
        z = draw_innovations(family, rng, idx.size)
        next_plus = np.maximum(0.0, plus[idx] + z - K)
        next_minus = np.maximum(0.0, minus[idx] - z - K)
        plus[idx] = next_plus
        minus[idx] = next_minus
        psi_total[idx] += location_score(family, z)
        crossed_plus = next_plus >= threshold
        crossed_minus = next_minus >= threshold
        crossed = crossed_plus | crossed_minus
        if not crossed.any():
            continue
        both = crossed_plus & crossed_minus
        count_both = int(np.count_nonzero(both))
        ties += count_both
        simultaneous += count_both
        done = idx[crossed]
        tau[done] = step
        terminal[done] = z[crossed]
        direction[done] = (
            crossed_plus[crossed].astype(np.int8)
            - crossed_minus[crossed].astype(np.int8)
        )
        active[done] = False
    else:
        raise RuntimeError(f"{int(active.sum())} Route-A paths did not alarm")

    return ScorePaths(
        tau=tau,
        terminal=terminal,
        psi_total=psi_total,
        direction=direction,
        ties=ties,
        simultaneous_crossings=simultaneous,
    )

