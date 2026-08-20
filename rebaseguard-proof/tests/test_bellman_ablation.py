from flint import arb

from rebaseguard_certify.bellman import finite_interval_bellman_crosscheck
from rebaseguard_certify.bellman_ablation import (
    historical_floor_reachable_ablation,
)


def test_unreachable_square_nodes_do_not_change_historical_origin_value():
    historical = finite_interval_bellman_crosscheck(cells=4, z_bins=16, bits=128)
    reachable = historical_floor_reachable_ablation(cells=4, z_bins=16, bits=128)
    historical_gamma = arb(historical["gamma_finite"]["ball"])
    reachable_gamma = arb(reachable["gamma_finite"]["ball"])
    assert (historical_gamma - reachable_gamma).contains(0)
    assert reachable["reachable_nodes"] < reachable["full_square_nodes"]


def test_floor_projection_explains_excessive_historical_persistence():
    floor = historical_floor_reachable_ablation(cells=12, z_bins=96, bits=128)
    floor_arl = float(arb(floor["arl_finite"]["ball"]).mid())
    assert floor_arl > 2_000.0
