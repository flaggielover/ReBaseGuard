from __future__ import annotations

import importlib.util
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]
RUNNER = CAMPAIGN / "numerics/run_correspondence.py"


def _load_runner():
    spec = importlib.util.spec_from_file_location("track3_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_all_deterministic_preoutcome_controls_pass():
    controls = _load_runner().structural_controls()
    assert controls["pass"] is True
    assert all(controls["checks"].values())
    assert all(value <= 2e-7 for value in controls["score_grid_max_abs_errors"].values())
    assert controls["uniform_edge"]["actual_dE_e_Z1"] == -1.0
    assert controls["uniform_edge"]["interior_a.e._score_prediction_for_dE"] == 0.0
    assert "NOT THEOREM CONFIRMATION" in controls["uniform_edge"]["classification"]

