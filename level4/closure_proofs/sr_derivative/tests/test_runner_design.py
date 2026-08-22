from __future__ import annotations

import ast
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]
RUNNER = CAMPAIGN / "numerics/run_correspondence.py"


def assignments() -> dict[str, object]:
    tree = ast.parse(RUNNER.read_text())
    found: dict[str, object] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name):
            try:
                found[target.id] = ast.literal_eval(node.value)
            except ValueError:
                pass
    return found


def test_runner_hard_codes_frozen_sample_sizes_and_primary_step():
    values = assignments()
    assert values["PRIMARY_H"] == 0.0125
    assert values["CAL_TARGET_PATHS"] == 800_000
    assert values["CAL_SEARCH_PATHS"] == 200_000
    assert values["CAL_FINAL_PATHS"] == 800_000
    assert values["CAL_FIXED_BATCHES"] == 64
    assert values["CAL_FIXED_PATHS"] == 10_000
    assert values["ROUTE_A_BATCHES"] == 64
    assert values["ROUTE_A_PATHS"] == 25_000
    assert values["ROUTE_B_REPLICATIONS"] == 2
    assert values["ROUTE_B_BATCHES"] == 64
    assert values["ROUTE_B_PATHS"] == 12_500


def test_runner_has_no_quick_mode_or_sample_size_cli_override():
    text = RUNNER.read_text()
    assert "argparse" not in text
    assert "--quick" not in text
    assert "Richardson" not in text.replace("richardson", "")


def test_runner_freezes_paired_batch_derivative_and_diagnostic_order():
    text = RUNNER.read_text()
    assert "D_b" not in text  # implementation works from batch arrays, not prose
    assert "derivatives[replication, batch] = stopped.derivatives" in text
    assert '"controls_verdict": "DIAGNOSTIC ONLY; CANNOT FAIL OR RESCUE PRIMARY"' in text
    assert "pooled_finest_abs_z_at_most_3" in text

