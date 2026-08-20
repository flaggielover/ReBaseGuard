from __future__ import annotations

from rebaseguard_phase4c.contraction_prototype import (
    certify_block_sum_forcing,
    certify_one_sided_monotone_minorant,
)


def test_block_sum_forcing_proves_strict_contraction():
    result = certify_block_sum_forcing(n=9, bits=128)
    assert result["q"]["lower_enclosure"] != "0"
    assert float(result["resolvent_bound"]["upper_enclosure"].split()[0].strip("[")) > 20_000


def test_small_one_sided_minorant_has_mass_balance_and_positive_hit():
    result = certify_one_sided_monotone_minorant(
        n=10,
        cells=20,
        q_safe_num=1,
        q_safe_den=10_000_000,
        bits=128,
    )
    assert result["mass_balance"].startswith("every Arb")
    assert result["continuum_argument"]["sampled_grid_used"] is False
