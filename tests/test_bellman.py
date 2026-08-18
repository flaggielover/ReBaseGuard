from flint import arb

from rebaseguard_certify.bellman import finite_interval_bellman_crosscheck


def test_independent_bellman_crosscheck_is_mass_balanced_and_nonproof():
    result = finite_interval_bellman_crosscheck(cells=4, z_bins=16, bits=128)
    assert result["continuum_certificate"] is False
    assert result["mass_balance_rows"] == 25
    assert arb(result["gamma_finite"]["ball"]) > 2
