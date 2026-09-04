"""Projection of a fresh full-scope P4Y production cost.

Cost basis is P4X's own measured execution of the identical scientific scope.
That is COST METADATA -- CPU-hours actually consumed -- and is used here only
as a scale.  No P4X correspondence outcome, discrepancy, z or pass/fail enters
this module, and none is needed to project compute.
"""

from __future__ import annotations

from .strata import (
    ACCEPT_PER_CONFIG_HOURS, ACCEPT_TOTAL_HOURS, FUTURE_PER_CONFIG_CAP_HOURS,
    FUTURE_TOTAL_CAP_HOURS, P4X_MAX_CONFIG_CPU_HOURS, P4X_TOTAL_CPU_HOURS,
    REQUIRED_RESERVE,
)


def project(*, mean_multiplier: float, tail_multiplier: float,
            baseline_multiplier: float) -> dict:
    """Scale the P4X cost basis by the measured staged-rule spend.

    ``mean_multiplier`` and ``tail_multiplier`` are blocks-used / B1 for the
    recommended rule; ``baseline_multiplier`` is the same quantity for a run
    that stops at stage 1, which is what the P4X cost basis already paid for.
    The ratio is what P4Y adds.
    """
    central_ratio = mean_multiplier / baseline_multiplier
    conservative_ratio = tail_multiplier / baseline_multiplier
    total_central = P4X_TOTAL_CPU_HOURS * central_ratio
    total_conservative = P4X_TOTAL_CPU_HOURS * conservative_ratio
    max_central = P4X_MAX_CONFIG_CPU_HOURS * central_ratio
    max_conservative = P4X_MAX_CONFIG_CPU_HOURS * conservative_ratio
    return {
        "basis_total_cpu_hours": P4X_TOTAL_CPU_HOURS,
        "basis_max_config_cpu_hours": P4X_MAX_CONFIG_CPU_HOURS,
        "central_ratio": central_ratio,
        "conservative_ratio": conservative_ratio,
        "projected_total_central": total_central,
        "projected_total_conservative": total_conservative,
        "projected_max_config_central": max_central,
        "projected_max_config_conservative": max_conservative,
        "future_total_cap": FUTURE_TOTAL_CAP_HOURS,
        "future_per_config_cap": FUTURE_PER_CONFIG_CAP_HOURS,
        "required_reserve": REQUIRED_RESERVE,
        "accept_total_hours": ACCEPT_TOTAL_HOURS,
        "accept_per_config_hours": ACCEPT_PER_CONFIG_HOURS,
        "total_cap_feasibility":
            "PASS" if total_conservative <= ACCEPT_TOTAL_HOURS else "FAIL",
        "per_config_cap_feasibility":
            "PASS" if max_conservative <= ACCEPT_PER_CONFIG_HOURS else "FAIL",
    }
