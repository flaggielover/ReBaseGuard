"""The feasibility probe is evidence for a plan, so its claims are checked --
but only as *probe* claims.  Nothing here is a scientific assertion."""
from __future__ import annotations

import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
DOC = json.loads((NS / "feasibility" / "results" / "reduction_probe.json").read_text())
S = DOC["summary"]


def test_reduction_reproduces_p5_measured_map():
    # the reduction must land on P5's independently measured map; the residual
    # is a discretisation effect of the probe, bounded here so a future edit
    # that breaks the reduction is caught.
    assert S["max_abs_z_vs_p5_mc"] < 6.0
    assert S["max_abs_grid_delta_61_to_121"] < 5e-3


def test_probe_covers_both_detectors_and_all_windows():
    dets = {r["detector"] for r in DOC["correspondence"]}
    ms = {r["m"] for r in DOC["correspondence"]}
    assert dets == {"cusum", "sr"}
    assert ms == {1, 2, 3, 5}


def test_probe_saturation_margin_is_the_one_the_plan_assumes():
    # FROZEN_THEOREM.md P5X-T4 targets sup|R| < 2; CERTIFICATE_PLAN.md bets on
    # a half-width < 0.2 against the margin this line records.
    worst = max(S[f"{d}_m{m}_sup_absR_on_scan"] for d in ("cusum", "sr")
                for m in (1, 2, 3, 5))
    assert worst < 2.0
    assert 2.0 - worst > 0.4


def test_probe_variance_floor_is_positive():
    for det in ("cusum", "sr"):
        assert S[f"{det}_m1_inf_S_on_scan"] > 0.3


def test_probe_sign_matches_H2():
    for det in ("cusum", "sr"):
        assert S[f"{det}_sign_R_negative_on_positive_e"] is True
