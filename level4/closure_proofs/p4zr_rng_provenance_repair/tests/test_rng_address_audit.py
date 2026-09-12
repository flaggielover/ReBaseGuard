"""Same-campaign RNG address separation: the audit itself."""
import pytest

from rebaseguard_p4zr.rng_address_audit import (
    AddressAuditError, AddressClass, StreamBlock, audit_manifest, audit_streams,
    blocks_from_manifest, predecessor_seed_check,
)

PASS = "RNG_ADDRESS_SEPARATION_PASS"
FAIL = "RNG_ADDRESS_SEPARATION_FAIL"


def cal(generator="PHILOX", key=1, lo=0, hi=9, label="cal", cfg="c", route="r"):
    return StreamBlock(generator=generator, key=key, batch_lo=lo, batch_hi=hi,
                       cls=AddressClass.CALIBRATION, label=label,
                       configuration=cfg, route=route, result_bearing=False)


def prod(generator="PHILOX", key=1, lo=0, hi=199, label="prod", cfg="c", route="r"):
    return StreamBlock(generator=generator, key=key, batch_lo=lo, batch_hi=hi,
                       cls=AddressClass.PRODUCTION, label=label,
                       configuration=cfg, route=route, result_bearing=True)


# --- case 1: disjoint calibration/production addresses -> PASS ---------------

def test_disjoint_keys_pass():
    r = audit_streams([cal(key=1000), prod(key=2000)])
    assert r["verdict"] == PASS
    assert r["address_overlaps"] == [] and r["seed_namespace_reuse"] == []


def test_disjoint_generators_on_the_same_key_is_namespace_reuse_not_overlap():
    """P4ZA's actual shape: one integer, two different bit generators."""
    r = audit_streams([cal(generator="PHILOX", key=4190001),
                       prod(generator="PCG64", key=4190001)])
    assert r["verdict"] == PASS, "different generators share no stream"
    assert r["address_overlaps"] == []
    assert len(r["seed_namespace_reuse"]) == 1
    f = r["seed_namespace_reuse"][0]
    assert f["calibration_generator"] == "PHILOX"
    assert f["production_generator"] == "PCG64"


# --- case 2: identical seed + overlapping batches -> FAIL -------------------

def test_identical_key_and_overlapping_batches_fail():
    r = audit_streams([cal(key=7, lo=0, hi=7), prod(key=7, lo=0, hi=199)])
    assert r["verdict"] == FAIL
    assert r["overlapping_address_total"] == 8
    assert r["address_overlaps"][0]["overlapping_batches"] == list(range(8))


def test_a_single_shared_batch_is_enough_to_fail():
    r = audit_streams([cal(key=7, lo=42, hi=42), prod(key=7, lo=0, hi=199)])
    assert r["verdict"] == FAIL
    assert r["overlapping_address_total"] == 1


def test_a_shorter_calibration_draw_is_not_a_weaker_collision():
    """Draw length is deliberately absent from the address model."""
    a = audit_streams([cal(key=7, lo=0, hi=0), prod(key=7, lo=0, hi=199)])
    b = audit_streams([cal(key=7, lo=0, hi=0), prod(key=7, lo=0, hi=0)])
    assert a["verdict"] == b["verdict"] == FAIL


# --- case 3: same seed + provably disjoint address ranges ------------------

def test_same_key_disjoint_batch_ranges_pass():
    """A declared batch partition of one key is legitimate, and is recorded.

    This is how P8R separates purposes inside one address class, so it must not
    be confused either with a collision or with cross-generator seed reuse.
    """
    r = audit_streams([cal(key=7, lo=0, hi=49), prod(key=7, lo=50, hi=249)])
    assert r["verdict"] == PASS
    assert r["address_overlaps"] == []
    assert r["seed_namespace_reuse"] == [], "same generator: not namespace reuse"
    assert len(r["key_partitions"]) == 1
    f = r["key_partitions"][0]
    assert f["severity"] == "KEY_PARTITION"
    assert f["calibration_batches"] == [0, 49]
    assert f["production_batches"] == [50, 249]


def test_same_key_adjacent_ranges_are_disjoint_at_the_boundary():
    assert audit_streams([cal(key=7, lo=0, hi=49),
                          prod(key=7, lo=50, hi=99)])["verdict"] == PASS
    assert audit_streams([cal(key=7, lo=0, hi=50),
                          prod(key=7, lo=50, hi=99)])["verdict"] == FAIL


# --- case 4: the predecessor-only check cannot substitute -------------------

def test_predecessor_only_check_misses_a_same_campaign_collision():
    """The check every P4Z-line audit actually ran, on the P4Z shape.

    P4Z's calibration seed 4090001 is also its own production rb_score seed for
    configuration 0.  Compared only against the *predecessor* seed sets it looks
    clean; the same-campaign address audit fails it.
    """
    p4z_campaign_seeds = {4090001, 4090002, 4090004}
    historical_predecessor_seeds = {4010001, 4010002, 4010003,
                                    4010004, 4010005, 4010006}
    assert predecessor_seed_check(p4z_campaign_seeds,
                                  historical_predecessor_seeds) is True

    r = audit_streams([
        cal(generator="PCG64", key=4090001, lo=0, hi=7,
            label="run_micropilots.py"),
        prod(generator="PCG64", key=4090001, lo=0, hi=199,
             cfg="frozen/cusum@5/gaussian", route="rb_score"),
    ])
    assert r["verdict"] == FAIL, (
        "the same-campaign audit must catch what the predecessor check misses")


def test_predecessor_check_and_address_audit_are_independent_signals():
    """A campaign can fail the predecessor check and pass the address audit."""
    assert predecessor_seed_check({4090001}, {4090001}) is False
    assert audit_streams([cal(key=1), prod(key=2)])["verdict"] == PASS


# --- manifest handling -----------------------------------------------------

def test_manifest_round_trip():
    m = {"campaign": "T", "programs": [
        {"label": "cal", "class": "calibration", "result_bearing": False,
         "streams": [{"generator": "PHILOX", "key": 1,
                      "batch_lo": 0, "batch_hi": 5}]},
        {"label": "prod", "class": "production", "result_bearing": True,
         "streams": [{"generator": "PHILOX", "key": 1,
                      "batch_lo": 0, "batch_hi": 9}]}]}
    assert audit_manifest(m)["verdict"] == FAIL
    assert audit_manifest(m)["campaign"] == "T"
    assert len(blocks_from_manifest(m)) == 2


def test_a_calibration_program_may_not_declare_itself_result_bearing():
    m = {"campaign": "T", "programs": [
        {"label": "cal", "class": "calibration", "result_bearing": True,
         "streams": []}]}
    with pytest.raises(AddressAuditError, match="result_bearing"):
        blocks_from_manifest(m)


def test_unknown_generator_is_rejected_rather_than_ignored():
    with pytest.raises(AddressAuditError, match="unknown generator"):
        StreamBlock(generator="MT19937", key=1, batch_lo=0, batch_hi=1,
                    cls=AddressClass.CALIBRATION, label="x")


def test_empty_batch_range_is_rejected():
    with pytest.raises(AddressAuditError, match="empty batch range"):
        cal(lo=5, hi=4)


def test_calibration_against_calibration_is_not_a_finding():
    r = audit_streams([cal(key=1, label="a"), cal(key=1, label="b")])
    assert r["verdict"] == PASS


def test_production_against_production_is_not_a_finding():
    r = audit_streams([prod(key=1, label="a"), prod(key=1, label="b")])
    assert r["verdict"] == PASS
