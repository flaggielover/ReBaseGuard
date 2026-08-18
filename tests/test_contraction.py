from flint import arb

from rebaseguard_certify.contraction import certify_block_contraction


def test_global_block_contraction_is_strict_and_analytic():
    certificate = certify_block_contraction(n=7, bits=192)
    assert certificate["scope"] == "entire reachable continuum"
    assert certificate["method"] == "Gaussian block-sum forcing event"
    assert arb(certificate["q_n"]["ball"]) > 0
    assert arb(certificate["beta_n"]["ball"]) < 1
    assert arb(certificate["resolvent_bound"]["ball"]) > 1


def test_contraction_uses_exact_model_parameters():
    certificate = certify_block_contraction(n=7, bits=160)
    assert certificate["model"] == {"k_num": 1, "k_den": 2, "h_num": 5, "h_den": 1}
    assert certificate["derivation"]["sampled_grid_used"] is False
    assert certificate["derivation"]["forcing_threshold"] == "h+n*k"

