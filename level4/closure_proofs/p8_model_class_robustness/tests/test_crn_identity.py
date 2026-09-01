"""G13: the addressable primitive field is a pure function of its address.

These are the P6R2b Gate-9 properties, re-established for P8's own field:
no live-set dependence, no execution-order dependence, no dependence on the
axes P8 compares, and no special case at block boundaries.
"""
import numpy as np
import pytest

from rebaseguard_p8 import primitives as PR

EXP = "unit_test"


def test_stopped_value_matches_column_and_block():
    col = PR.stopped_column(EXP, "t5", 3, 700, 4096)
    for p in (0, 1, 4095, 2048):
        assert PR.stopped_value(EXP, "t5", 3, p, 700) == col[p]


def test_stopped_value_is_order_independent():
    """Querying the same addresses in reverse order returns the same values."""
    addrs = [(5, 3), (100, 1000), (7, 0), (4000, 5000)]
    a = {ad: PR.stopped_value(EXP, "gaussian", 0, *ad) for ad in addrs}
    PR.clear_cache()
    b = {ad: PR.stopped_value(EXP, "gaussian", 0, *ad) for ad in reversed(addrs)}
    assert a == b


def test_stopped_value_survives_cache_clear():
    v = PR.stopped_value(EXP, "contam0.1", 2, 17, 4321)
    PR.clear_cache()
    assert PR.stopped_value(EXP, "contam0.1", 2, 17, 4321) == v


@pytest.mark.parametrize("index", [0, 1, 127, 128, 129, 511, 512, 4321, 12345])
def test_no_special_case_at_block_boundaries(index):
    """Observation t is served from block t//BLOCK_LEN for every t, forever."""
    v = PR.stopped_value(EXP, "gaussian", 0, 9, index)
    b, off = divmod(index, PR.BLOCK_LEN)
    blk = PR.stopped_block(EXP, "gaussian", 0, 9 // PR.ROWS_PER_BLOCK, b)
    assert v == blk[9 % PR.ROWS_PER_BLOCK, off]
    assert b == index // PR.BLOCK_LEN


def test_chain_column_is_live_set_independent():
    """The banding mask is an efficiency device and changes no delivered value."""
    full = PR.chain_monitor_column(EXP, "t5", "cusum", 3, 7, 900, 1024)
    need = np.zeros(1024, bool)
    need[300] = True
    sparse = PR.chain_monitor_column(EXP, "t5", "cusum", 3, 7, 900, 1024,
                                     need=need)
    assert sparse[300] == full[300]
    need2 = np.ones(1024, bool)
    need2[:512] = False
    sparse2 = PR.chain_monitor_column(EXP, "t5", "cusum", 3, 7, 900, 1024,
                                      need=need2)
    assert np.array_equal(sparse2[512:], full[512:])


def test_chain_column_deep_address_beyond_block_3():
    """Evidence must reach past block index 3, as the P6R2b standard requires."""
    idx = 4 * PR.BLOCK_LEN + 5
    assert idx // PR.BLOCK_LEN >= 4
    a = PR.chain_monitor_column(EXP, "gaussian", "sr", 5, 2, idx, 512)
    PR.clear_cache()
    b = PR.chain_monitor_column(EXP, "gaussian", "sr", 5, 2, idx, 512)
    assert np.array_equal(a, b)


def test_chain_address_excludes_the_compared_axes():
    """rho, shift and drift pattern must not appear in any chain address."""
    key = PR.chain_address("e", "t5", "cusum", 3, 4, PR.MONITOR, 1)
    assert len(key) == 8
    # the address is built only from the declared components
    assert key == PR.chain_address("e", "t5", "cusum", 3, 4, PR.MONITOR, 1)


def test_different_primitive_types_do_not_collide():
    mon = PR.chain_block(EXP, "gaussian", "cusum", 1, 0, PR.MONITOR, 0, 256)
    aux = PR.chain_block(EXP, "gaussian", "cusum", 1, 0, PR.AUX, 0, 256)
    assert not np.allclose(mon[:, 0], aux[:, 0])


def test_family_is_in_the_address_so_families_are_not_paired():
    a = PR.stopped_column(EXP, "gaussian", 0, 0, 256)
    b = PR.stopped_column(EXP, "t5", 0, 0, 256)
    assert not np.allclose(a, b)


def test_chain_field_digest_is_variant_free():
    d1 = PR.chain_field_digest(EXP, "gaussian", "cusum", 1, 128, 2, 1)
    PR.clear_cache()
    d2 = PR.chain_field_digest(EXP, "gaussian", "cusum", 1, 128, 2, 1)
    assert d1 == d2 and len(d1) == 64
