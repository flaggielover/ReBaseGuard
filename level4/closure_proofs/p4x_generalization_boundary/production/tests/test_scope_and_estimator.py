"""Scope, estimator identity, and anchor reproduction."""

from __future__ import annotations

import pytest


def test_anchors_reproduced_exactly(anchors):
    """Every frozen anchor must reproduce, or production may not launch."""
    assert anchors["all_anchors_reproduced"] is True
    assert anchors["mismatches"] == []
    assert anchors["comparisons"] >= 48


def test_anchor_reproduction_validates_the_frozen_semantics(anchors):
    validated = " ".join(anchors["semantics_validated_by_exact_reproduction"])
    for item in ("Route-A", "Route-B", "Richardson", "Philox",
                 "detector parameters", "window semantics",
                 "alarm-causing increment", "family parameterisation"):
        assert item in validated, item


def test_scope_is_exactly_96_cells_in_24_configurations(ledger, checkpoint):
    assert ledger["cells_total"] == 96
    assert checkpoint["production_scope"]["theorem_supported_cells"] == 96
    assert len({c["config"] for c in ledger["cells"]}) == 24


def test_scope_matches_the_frozen_grid(ledger, p4_correspondence):
    hist = {(c["layer"], c["detector"], c["family"], c["m"])
            for c in p4_correspondence["monte_carlo"]["cells"]
            if c["family_class"] == "THEOREM-SUPPORTED"}
    got = {(c["layer"], c["detector"], c["family"], c["m"])
           for c in ledger["cells"]}
    assert got == hist


def test_every_cell_covers_both_routes_and_all_windows(ledger):
    by_cfg = {}
    for c in ledger["cells"]:
        by_cfg.setdefault(c["config"], set()).add(c["m"])
        assert "route_a" in c and "route_b" in c
    for cfg, ms in by_cfg.items():
        assert ms == {1, 2, 3, 5}, cfg


def test_estimator_is_the_frozen_one(stage1, checkpoint):
    assert stage1["fd_steps"] == checkpoint["estimator_plan"]["fd_steps"] == [0.05, 0.025]
    assert checkpoint["estimator_plan"]["variance_reduction_adopted"] == "NONE"


def test_no_rejected_variance_reduction_method_is_used(prod_dir):
    """The rejected R0 candidates must not appear in the production driver."""
    src = (prod_dir / "run_c2_production.py").read_text()
    for banned in ("reflection", "antithetic", "control_variate",
                   "importance", "stratif"):
        assert banned not in src.lower(), banned


def test_production_uses_a_fresh_seed_namespace(stage1):
    assert stage1["seed_base"] == 4210000
    for spec in stage1["specs"]:
        assert 4210000 <= spec["seed"] < 4220000


def test_h_values_recorded_on_every_cell(ledger):
    for c in ledger["cells"]:
        assert c["h_values"] == [0.05, 0.025]
        assert "Richardson" in c["richardson"] or "4 D(h/2)" in c["richardson"]
