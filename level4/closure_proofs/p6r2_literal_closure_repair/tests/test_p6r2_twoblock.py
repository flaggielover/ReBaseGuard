"""G6B: the two-block BCa acceleration, verified against brute force.

Expected behaviour is derived from synthetic fixtures and literal leave-one-out
recomputation, never from the generated artifact.
"""
import numpy as np
import pytest

from rebaseguard_p6r2 import twoblock as TB


def _fixture(seed=0, n_a=11, n_b=7):
    rng = np.random.default_rng(seed)
    return (rng.lognormal(0.0, 0.6, n_a), rng.lognormal(0.0, 0.3, n_b),
            rng.lognormal(0.2, 0.6, n_a), rng.lognormal(0.1, 0.3, n_b))


@pytest.mark.parametrize("seed", range(6))
def test_closed_form_jackknives_match_brute_force(seed):
    an, ad, bn, bd = _fixture(seed)
    ja, jb = TB.jackknife_block_a(an, ad, bn, bd), TB.jackknife_block_b(an, ad, bn, bd)
    ba, bb = TB.brute_force_jackknives(an, ad, bn, bd)
    assert np.abs(ja - ba).max() < 1e-12
    assert np.abs(jb - bb).max() < 1e-12


@pytest.mark.parametrize("seed", range(6))
def test_two_block_acceleration_matches_brute_force_definition(seed):
    """Recompute the multi-sample acceleration from the brute-force jackknives."""
    an, ad, bn, bd = _fixture(seed)
    ba, bb = TB.brute_force_jackknives(an, ad, bn, bd)
    num = den = 0.0
    for j in (ba, bb):
        n = j.size
        u = (n - 1.0) * (j.mean() - j)
        num += (u ** 3).sum() / n ** 3
        den += (u ** 2).sum() / n ** 2
    expect = num / (6.0 * den ** 1.5)
    got = TB.two_block_acceleration(
        TB.jackknife_block_a(an, ad, bn, bd), TB.jackknife_block_b(an, ad, bn, bd))
    assert abs(got - expect) < 1e-12


def test_two_block_reduces_to_one_block_when_the_other_has_no_influence():
    """The generalisation must be exact, not merely approximate."""
    an, ad, bn, bd = _fixture(3)
    ja = TB.jackknife_block_a(an, ad, bn, bd)
    inert = np.full(9, 1.234)                     # zero influence
    assert abs(TB.two_block_acceleration(ja, inert)
               - TB.one_block_acceleration(ja)) < 1e-12


@pytest.mark.parametrize("seed", range(6))
def test_two_block_and_the_p6r_one_block_shortcut_differ(seed):
    """The defect must be visible: omitting a block with real influence changes a."""
    an, ad, bn, bd = _fixture(seed)
    ja = TB.jackknife_block_a(an, ad, bn, bd)
    jb = TB.jackknife_block_b(an, ad, bn, bd)
    two = TB.two_block_acceleration(ja, jb)
    one = TB.one_block_acceleration(jb)           # the P6R shortcut (shorter block)
    assert abs(two - one) > 1e-6, "the omitted block carried no influence here"


def test_both_blocks_contribute_influence_in_the_real_shape():
    """Neither block's jackknife is degenerate for the Rdelta functional."""
    an, ad, bn, bd = _fixture(1)
    ja = TB.jackknife_block_a(an, ad, bn, bd)
    jb = TB.jackknife_block_b(an, ad, bn, bd)
    assert ja.std() > 0 and jb.std() > 0


def test_rdelta_bca_reports_both_accelerations_and_the_estimand_is_unchanged():
    an, ad, bn, bd = _fixture(2, n_a=200, n_b=80)
    r = TB.rdelta_bca(an, ad, bn, bd, n_boot=400, seed=1)
    assert abs(r["theta"] - TB.rdelta_theta(an, ad, bn, bd)) < 1e-12
    assert r["accel_two_block"] != r["accel_one_block_p6r_shortcut"]
    assert r["bca_lo"] < r["rel"] < r["bca_hi"]
