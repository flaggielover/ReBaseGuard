import numpy as np

from rebaseguard_certify.diagnostics import simulate


def test_diagnostics_are_seeded_and_record_terminal_data():
    left = simulate(128, seed=1729, batch_size=64)
    right = simulate(128, seed=1729, batch_size=32)
    for name in ("tau", "z_tau", "t_tau", "pre_plus", "pre_minus", "arm"):
        assert np.array_equal(getattr(left, name), getattr(right, name))


def test_diagnostic_summary_is_labelled_nonrigorous():
    result = simulate(256, seed=20260818)
    summary = result.summary()
    assert summary["proof_role"] == "NON-RIGOROUS DIAGNOSTIC ONLY"
    assert summary["n"] == 256
    assert summary["arl"] == summary["mean_tau"]
    assert summary["gamma_se"] > 0.0
    assert summary["up_fraction"] + summary["down_fraction"] == 1.0
