"""The regenerated artifacts must satisfy the repair, derived from frozen inputs."""
import json
from pathlib import Path

import numpy as np
import pytest

NS = Path(__file__).resolve().parents[1]
RES = NS / "results"
P6R = NS.parent / "p6r_safe_rebaselining_confirmation"


def _new(fam):
    f = RES / f"p6r2_analysis_{fam}.json"
    if not f.exists():
        pytest.skip(f"p6r2_analysis_{fam}.json not produced yet")
    return json.loads(f.read_text())


def _old(fam):
    return json.loads((P6R / "results" / f"p6r_analysis_{fam}.json").read_text())


# --- strict JSON, no NaN/Infinity anywhere ---------------------------------

@pytest.mark.parametrize("fam", ("eval", "replay"))
def test_artifacts_are_strict_standards_compliant_json(fam):
    p = RES / f"p6r2_analysis_{fam}.json"
    if not p.exists():
        pytest.skip("not produced yet")
    raw = p.read_text()
    for token in ("NaN", "Infinity", "-Infinity"):
        assert token not in raw, f"{token} token in {p.name}"
    json.loads(raw, parse_constant=lambda c: (_ for _ in ()).throw(
        AssertionError(f"non-standard constant {c!r}")))


# --- all 56 previously invalid ratios repaired ------------------------------

def test_all_56_previously_invalid_ratios_are_now_first_class_undefined():
    """The target list comes from the FROZEN P6R enumeration, not the new JSON."""
    frozen = json.loads((P6R / "results" / "p6r_undefined_ratios.json").read_text())
    total = 0
    for fam in ("eval", "replay"):
        want = {(r["cell"], r["comparison"], r["metric"])
                for r in frozen["families"][fam]["entries"]}
        total += len(want)
        new = _new(fam)
        got = {(r["cell"], r["comparison"], r["metric"])
               for r in new["undefined_ledger"]}
        assert want == got, (fam, sorted(want ^ got)[:6])
        for cell, comp, metric in want:
            rec = new["cells"][cell]["comparisons"][comp][metric]
            assert rec["status"] == "UNDEFINED_ZERO_DENOMINATOR", (cell, comp, metric)
            assert rec["verdict"] == "NO_CLAIM"
            assert rec["relative_effect"] is None and rec["p_value"] is None
            assert rec["bca_interval"] is None and rec["normal_interval"] is None
            assert rec["p_adjusted"] is None
    assert total == 56, f"expected 56 previously invalid ratios, found {total}"


def test_p6r_had_favourable_labels_where_p6r2_now_says_no_claim():
    """The defect must be demonstrable, not merely asserted fixed."""
    frozen = json.loads((P6R / "results" / "p6r_undefined_ratios.json").read_text())
    bad = 0
    for fam in ("eval", "replay"):
        old = _old(fam)
        for r in frozen["families"][fam]["entries"]:
            v = old["cells"][r["cell"]]["comparisons"][r["comparison"]][r["metric"]]["verdict"]
            if v in ("PRACTICALLY_MATERIAL", "STATISTICALLY_RESOLVED"):
                bad += 1
    assert bad > 0, "no invalid favourable label found in P6R -- check the fixture"


@pytest.mark.parametrize("fam", ("eval", "replay"))
def test_no_undefined_record_enters_any_bh_family(fam):
    new = _new(fam)
    undef = {(r["cell"], r["comparison"], r["metric"])
             for r in new["undefined_ledger"]}
    for cell, row in new["cells"].items():
        for fname, f in row["bh"].items():
            for k in f["family"]:
                assert not any(c == cell and k == m for c, _, m in undef), (cell, k)
            for k in f.get("p_adjusted", {}):
                assert f["p_adjusted"][k] is not None
    for fkey in ("bh_F2_replication", "bh_F4_finite_reference"):
        if fkey in new:
            assert all(v is not None for v in new[fkey]["p_adjusted"].values())


# --- G6A, checked against the raw arrays ------------------------------------

def test_regenerated_f3_is_exactly_the_literal_family():
    new = _new("eval")
    f3 = new["cells"]["P"]["bh"]["F3_delta_scope_literal"]
    assert set(f3["family"]) == {"Dtail100@0.5", "Dq95@2.0"}
    assert f3["n_tests"] == 2
    assert "Dq95@0.5" not in f3["family"], "undeclared fallback still present"
    assert any(e["key"] == "Dtail100@2.0"
               and e["label"] == "INSUFFICIENT_TAIL_EVENTS"
               for e in f3["excluded_detail"])


def test_f3_repair_removed_exactly_one_undeclared_test_and_changed_no_decision():
    old_f3 = _old("eval")["cells"]["P"]["bh"]["F3_delta_scope"]
    new_f3 = _new("eval")["cells"]["P"]["bh"]["F3_delta_scope_literal"]
    assert set(old_f3["family"]) - set(new_f3["family"]) == {"Dq95@0.5"}
    assert set(new_f3["family"]) - set(old_f3["family"]) == set()
    # and no decision flips: nothing rejected before, nothing rejected after
    assert not any(old_f3["reject"].values())
    assert not any(new_f3["reject"].values())


# --- G6B --------------------------------------------------------------------

def test_rdelta_uses_the_two_block_acceleration_and_reports_the_shortcut():
    new = _new("eval")
    n = 0
    for cell, row in new["cells"].items():
        for blk, comps in row["comparisons"].items():
            r = comps.get("Rdelta")
            if r is None or r["status"] != "OK":
                continue
            d = r["two_block_diagnostics"]
            assert r["statistic"] == "rdelta_two_block_bca"
            assert d["accel_two_block"] != d["accel_one_block_p6r_shortcut"]
            assert d["n_block_a_delay"] != d["n_block_b_incontrol"]
            n += 1
    assert n > 20


def test_rdelta_estimand_is_unchanged_from_p6r():
    """Only the acceleration was repaired; the point estimate must not move."""
    new, old = _new("eval"), _old("eval")
    for cell, row in new["cells"].items():
        for blk, comps in row["comparisons"].items():
            r = comps.get("Rdelta")
            o = old["cells"][cell]["comparisons"][blk].get("Rdelta")
            if r is None or o is None or r["status"] != "OK":
                continue
            assert abs(r["relative_effect"] - o["rel"]) < 1e-12, (cell, blk)


# --- the regression guarantee ----------------------------------------------

@pytest.mark.parametrize("fam", ("eval", "replay"))
def test_every_other_defined_effect_reproduces_p6r_bit_for_bit(fam):
    new = _new(fam)
    reg = new["regression_vs_p6r"]
    assert reg["n_different"] == 0, reg["differences"][:5]
    assert reg["n_identical"] > 80


def test_the_confirmed_primary_result_is_untouched():
    """The independently confirmed primary numbers must survive the repair."""
    t = _new("eval")["cells"]["P"]["comparisons"]["vs_FIXED_TUNE@1.0"]
    for metric, want in (("Dtail100", -0.129173), ("Dq95", -0.149660),
                         ("Dmean", -0.083210), ("Arl0", 0.044323),
                         ("Rms", -0.043920)):
        assert abs(t[metric]["relative_effect"] - want) < 1e-5, metric
        assert t[metric]["status"] == "OK"


def test_replication_family_still_rejects_in_all_eight_cells():
    f2 = _new("eval")["bh_F2_replication"]
    assert f2["n_tests"] == 8 and all(f2["reject"].values())
