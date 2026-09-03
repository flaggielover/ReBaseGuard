"""CUSUM m=1 global production cover: invariants and the recorded FAIL.

These tests pin the result that was actually obtained, including its single
failing cell.  They must never be edited to assert a pass.
"""
from __future__ import annotations
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
R = json.loads((NS / "results" / "cusum_m1_production.json").read_text())
DOC = (NS / "cusum_global_production" / "PRODUCTION_RESULT.md").read_text()
FLAT = " ".join(DOC.split())


def test_anchored_to_the_binding_checkpoint():
    assert R["checkpoint_k"] == "3704988533f2d9038ddf0b35e58dea0eed4b6a2d"
    assert R["detector"] == "cusum" and R["m"] == 1 and R["moment"].startswith("first")


def test_criterion_is_the_theorem_consumer_not_f3():
    assert "ABS_MAX < 2" in R["criterion"]
    assert "F3=0.2 NOT applied" in R["criterion"]


def test_cover_has_no_gaps_and_spans_the_frozen_domain():
    assert R["coverage_gaps"] == [] and R["covers_full_domain"] is True
    assert R["e_domain"] == [0, 12]
    led = R["ledger"]
    assert abs(led[0]["e_lo"]) < 1e-12
    assert abs(led[-1]["e_hi"] - 12.0) < 1e-9
    for a, b in zip(led, led[1:]):
        assert abs(a["e_hi"] - b["e_lo"]) < 1e-12


def test_every_cell_carries_its_own_enclosure():
    for row in R["ledger"]:
        assert row["upper"] >= row["lower"]
        assert abs(row["abs_max"] - max(abs(row["lower"]), abs(row["upper"]))) < 1e-15
        assert abs(row["g3_margin"] - (2.0 - row["abs_max"])) < 1e-12


def test_no_cell_was_inferred():
    assert R["cells"] == len(R["ledger"]) == 47
    assert R["sub_cells"] == sum(r["n_sub"] for r in R["ledger"]) == 372


# --- the recorded outcome: 46/47, with cell 46 failing --------------------

def test_the_run_did_not_pass():
    assert R["all_pass"] is False
    assert R["min_g3_margin"] < 0.0


def test_exactly_one_cell_fails_and_it_is_the_last():
    bad = [r for r in R["ledger"] if r["status"] != "PASS"]
    assert [r["i"] for r in bad] == [46]
    assert bad[0]["e_lo"] == 10.5441104 and bad[0]["e_hi"] == 12.0
    assert bad[0]["abs_max"] > 2.0


def test_all_other_cells_pass_strictly():
    ok = [r for r in R["ledger"] if r["i"] != 46]
    assert len(ok) == 46
    assert all(r["status"] == "PASS" and r["abs_max"] < 2.0 for r in ok)


def test_failure_is_width_not_a_violation():
    bad = [r for r in R["ledger"] if r["i"] == 46][0]
    centre = (bad["lower"] + bad["upper"]) / 2.0
    assert abs(centre) < 1e-6            # centred on ~0: R is small there
    assert bad["half_width"] > 2.0       # the width alone breaks the criterion
    flat = " ".join(DOC.split())          # the doc is hard-wrapped
    assert "C-F2 failure (certificate too wide)" in flat
    assert "not a **C-F1 failure" in flat


def test_e_far_was_not_moved_after_the_result():
    scope = (NS / "FROZEN_SCOPE.md").read_text()
    assert "`e_far = 12`" in scope
    assert R["e_domain"] == [0, 12]
    assert "not being adopted here" in FLAT


# --- scope and resource --------------------------------------------------

def test_resource_stop_not_triggered():
    assert R["resource_stop_triggered"] is False
    assert R["cpu_hours"] <= R["resource_stop_threshold_cpu_h"] == 500.0


def test_second_moment_and_m_gt_1_recorded_as_not_run():
    assert R["second_moment_production"] == "NOT_RUN"
    assert "NO CERTIFIER" in R["m_gt_1"].upper()
    for tag in ("CUSUM_M2_G3", "CUSUM_M3_G3", "CUSUM_M5_G3"):
        assert tag in DOC
    assert "P5X_CUSUM_GLOBAL_G3          = INCOMPLETE" in DOC


def test_precision_matches_the_validated_certifier():
    assert R["precision_bits"] == 256 and R["taylor_order"] == 120
    assert R["degree"] == 12


def test_historical_verdicts_are_restated_unchanged():
    for line in ("P5X_FINAL_VERDICT         = PARTIAL",
                 "P5X_SR_GLOBAL_G3          = OUT_OF_BUDGET",
                 "LEVEL4_GLOBAL_CLOSURE     = NO",
                 "NOVELTY_STATUS            = NOT_ESTABLISHED"):
        assert line in DOC
