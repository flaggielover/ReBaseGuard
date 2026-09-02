"""The four address classes are disjoint, exhaustively and by value.

This is the structural half of the P8 repair.  P8's calibration re-verified a
tuned threshold at an address it had already inspected; P8R makes that
impossible, and these tests are the proof obligation for that claim.
"""
from itertools import combinations

import numpy as np
import pytest

from rebaseguard_p8r import primitives as PR
from rebaseguard_p8r.addressing import (TAG_INVENTORY, AddressClass, class_of,
                                        require_class, tag, tag_digest)
from conftest import payload_or_skip


def test_every_campaign_tag_is_minted_and_classified():
    for t in TAG_INVENTORY:
        assert t.startswith("p8r/")
        assert isinstance(class_of(t), AddressClass)


def test_tag_digests_are_pairwise_distinct():
    d = {t: tag_digest(t) for t in TAG_INVENTORY}
    assert len(set(d.values())) == len(TAG_INVENTORY), d


def test_class_pairs_never_share_an_address():
    """Two tags in different classes cannot produce equal addresses for ANY
    value of the remaining components, because the tag digest differs."""
    for a, b in combinations(TAG_INVENTORY, 2):
        if class_of(a) is class_of(b):
            continue
        for batch in (0, 7, 11, 1000, 2000, 3000):
            for rb in (0, 3):
                for blk in (0, 5, 4096):
                    assert (PR.stopped_address(a, "t5", batch, rb, blk)
                            != PR.stopped_address(b, "t5", batch, rb, blk))


def test_calibration_and_production_classes_are_disjoint():
    cal = {t for t in TAG_INVENTORY
           if class_of(t) is not AddressClass.PRODUCTION}
    prod = {t for t in TAG_INVENTORY if class_of(t) is AddressClass.PRODUCTION}
    assert cal and prod
    assert not ({tag_digest(t) for t in cal} & {tag_digest(t) for t in prod})


def test_search_and_verify_classes_deliver_different_values():
    from rebaseguard_p8r.addressing import (CAL_SEARCH_ARL0,
                                            CAL_VERIFY_1_ARL0,
                                            CAL_VERIFY_2_ARL0)
    vals = [PR.stopped_block(t, "gaussian", 7, 0, 0, n_rows=4, width=4)
            for t in (CAL_SEARCH_ARL0, CAL_VERIFY_1_ARL0, CAL_VERIFY_2_ARL0)]
    for a, b in combinations(vals, 2):
        assert not np.array_equal(a, b)


def test_require_class_refuses_a_foreign_class():
    with pytest.raises(PermissionError):
        require_class(tag(AddressClass.PRODUCTION, "gamma_e1"),
                      {AddressClass.CAL_SEARCH})


def test_primitives_reject_a_tag_not_minted_by_the_address_layer():
    for bad in ("p8_gamma_E1", "gamma_e1", "p8r/gamma_e1",
                "p8r/production", "p8r/nope/gamma_e1"):
        with pytest.raises(ValueError):
            PR.stopped_address(bad, "gaussian", 0, 0, 0)


def test_executed_calibration_never_touched_a_verification_address():
    cal = payload_or_skip("results/sr_calibration.json")
    for r in cal["rows"]:
        search = {(t["address_class"], t["batch"])
                  for t in r["search_trace"] + r["retry_trace"]}
        verify = {(v["address_class"], v["batch"])
                  for v in (r["verify_1"], r["verify_2"]) if v}
        assert all(c == AddressClass.CAL_SEARCH.value for c, _ in search)
        assert all(c != AddressClass.CAL_SEARCH.value for c, _ in verify)
        assert not (search & verify)


def test_verify_1_is_never_read_twice_for_a_retried_family():
    cal = payload_or_skip("results/sr_calibration.json")
    for r in cal["rows"]:
        if r["outcome"] != "ACCEPTED_VERIFY_2":
            continue
        # a retried family must have been accepted on CAL_VERIFY_2, and its
        # CAL_VERIFY_1 record must still show the ORIGINAL failed threshold.
        assert r["verify_2"]["address_class"] == AddressClass.CAL_VERIFY_2.value
        assert not r["verify_1"]["accepted"]
        assert r["verify_1"]["threshold"] != r["threshold"]
