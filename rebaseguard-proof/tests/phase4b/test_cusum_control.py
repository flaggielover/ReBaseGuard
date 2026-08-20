from __future__ import annotations

import numpy as np

from rebaseguard_certify.diagnostics import simulate
from rebaseguard_phase4b.cusum_control import simulate_protected_cusum_control


def test_adapter_preserves_protected_cusum_paths_and_summary() -> None:
    protected = simulate(200, seed=1729)
    adapted = simulate_protected_cusum_control(200, seed=1729)

    np.testing.assert_array_equal(adapted.tau, protected.tau)
    np.testing.assert_array_equal(adapted.z_tau, protected.z_tau)
    np.testing.assert_array_equal(adapted.t_tau, protected.t_tau)
    np.testing.assert_array_equal(adapted.arm, protected.arm)
    common = adapted.summary(detector="control")
    old = protected.summary()
    for key in (
        "arl",
        "gamma",
        "gamma_se",
        "mean_z_tau",
        "mean_t_tau",
        "mean_t_tau_sq",
        "wald_second_gap",
        "mean_z_tau_sq",
        "cross_term",
    ):
        assert common[key] == old[key]
