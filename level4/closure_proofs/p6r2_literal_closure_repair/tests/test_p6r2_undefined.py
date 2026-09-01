"""G6C / G12: zero-denominator comparisons must be first-class undefined."""
import json

import numpy as np
import pytest

from rebaseguard_p6r2 import effects as EF
from rebaseguard_p6r2 import families as FAM
from rebaseguard_p6r2 import undefined as UD


def test_zero_denominator_yields_the_undefined_status_at_source():
    a = np.random.default_rng(0).lognormal(size=200)
    rec = EF.ratio_of_means(a, np.zeros(200), metric="C_acq")
    assert rec["status"] == UD.STATUS_UNDEFINED
    assert rec["verdict"] == UD.VERDICT_NO_CLAIM
    assert rec["n_boot"] == 0, "no bootstrap may run for an undefined comparison"


def test_undefined_record_is_all_json_null_never_nan_or_inf():
    a = np.random.default_rng(1).lognormal(size=200)
    rec = EF.ratio_of_means(a, np.zeros(200), metric="Wbar")
    for k in ("relative_effect", "bca_interval", "normal_interval", "boot_sd",
              "p_value", "p_adjusted", "z0", "accel", "pair_corr"):
        assert rec[k] is None, k
    txt = json.dumps(rec, allow_nan=False)          # would raise on NaN/Infinity
    assert "NaN" not in txt and "Infinity" not in txt
    assert json.loads(txt)["relative_effect"] is None


def test_undefined_verdict_is_never_a_finite_effect_label():
    a = np.random.default_rng(2).lognormal(size=100)
    rec = EF.ratio_of_means(a, np.zeros(100), metric="x")
    for bad in UD.FORBIDDEN_ON_UNDEFINED:
        assert rec["verdict"] != bad


def test_zero_quantile_denominator_is_also_undefined():
    rng = np.random.default_rng(3)
    a = rng.lognormal(size=300)
    b = np.zeros(300)
    rec = EF.ratio_of_quantiles(a, b, 0.95, metric="Dq95")
    assert rec["status"] == UD.STATUS_UNDEFINED and rec["verdict"] == "NO_CLAIM"


def test_ratio_of_ratios_with_a_zero_component_is_undefined():
    rng = np.random.default_rng(4)
    n = 50
    rec = EF.ratio_of_ratios(rng.lognormal(size=n), rng.lognormal(size=n),
                             np.zeros(n), rng.lognormal(size=n), metric="Coll")
    assert rec["status"] == UD.STATUS_UNDEFINED


def test_undefined_never_enters_bh_and_never_receives_an_adjusted_p():
    rng = np.random.default_rng(5)
    a, b = rng.lognormal(size=300), rng.lognormal(0.3, 1.0, 300)
    good = EF.ratio_of_means(a, b, metric="good", seed=1)
    bad = EF.ratio_of_means(a, np.zeros(300), metric="bad")
    fam = FAM.bh_over_defined({"good": good, "bad": bad})
    assert fam["family"] == ["good"] and fam["n_tests"] == 1
    assert fam["excluded"]["bad"] == UD.STATUS_UNDEFINED
    assert "bad" not in fam["p_adjusted"] and "bad" not in fam["reject"]
    assert bad["p_adjusted"] is None


def test_subfloor_tail_also_excluded_from_bh_but_stays_defined():
    rng = np.random.default_rng(6)
    a, b = rng.lognormal(size=300), rng.lognormal(0.2, 1.0, 300)
    r = EF.apply_tail_gate(EF.ratio_of_means(a, b, metric="Dtail100", seed=2), 10, 9)
    assert r["status"] == UD.STATUS_OK
    assert r["verdict"] == "INSUFFICIENT_TAIL_EVENTS"
    fam = FAM.bh_over_defined({"t": r})
    assert fam["n_tests"] == 0 and fam["excluded"]["t"] == "INSUFFICIENT_TAIL_EVENTS"


def test_tail_gate_never_upgrades_an_undefined_record():
    a = np.random.default_rng(7).lognormal(size=100)
    rec = EF.apply_tail_gate(EF.ratio_of_means(a, np.zeros(100), metric="Dtail100"),
                             10_000, 10_000)
    assert rec["status"] == UD.STATUS_UNDEFINED and rec["verdict"] == "NO_CLAIM"


def test_defined_record_with_a_nonfinite_field_is_rejected_loudly():
    with pytest.raises(ValueError):
        EF._finite_record("m", "s", {"rel": float("inf"), "bca_lo": 0.0,
                                     "bca_hi": 1.0, "normal_lo": 0.0,
                                     "normal_hi": 1.0, "boot_sd": 1.0,
                                     "p_value": 0.1, "n_boot": 10, "z0": 0.0,
                                     "accel": 0.0}, 10,
                          method_mean=1.0, control_mean=1.0)


def test_strict_json_helpers():
    assert UD.sanitise_for_strict_json({"a": float("nan"), "b": [float("inf"), 1.0]}) \
        == {"a": None, "b": [None, 1.0]}
    with pytest.raises(ValueError):
        UD.assert_no_nonfinite({"x": float("nan")})
