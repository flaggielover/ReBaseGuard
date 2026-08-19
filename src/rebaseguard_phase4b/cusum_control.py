"""Read-only adapter from the protected CUSUM simulator to the Phase-4B harness."""

from __future__ import annotations

from rebaseguard_certify.diagnostics import simulate
from rebaseguard_phase4b.harness import StoppingSample


def simulate_protected_cusum_control(
    n: int,
    *,
    seed: int,
    k: float = 0.5,
    h: float = 5.0,
) -> StoppingSample:
    """Run the frozen CUSUM without changing its implementation or conventions."""

    result = simulate(n, seed=seed, k=k, h=h)
    return StoppingSample(
        tau=result.tau,
        z_tau=result.z_tau,
        t_tau=result.t_tau,
        arm=result.arm,
    )
