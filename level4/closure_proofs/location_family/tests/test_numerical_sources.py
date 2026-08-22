from __future__ import annotations

import ast
from pathlib import Path

import numpy as np

from rebaseguard_location_family.frozen import (
    FAMILIES,
    H_STEPS,
    MASTER_SEED,
    PRIMARY_H,
    ROUTE_A_BATCHES,
    ROUTE_A_PATHS_PER_BATCH,
    ROUTE_B_BATCHES,
    ROUTE_B_PATHS_PER_BATCH,
    THRESHOLDS,
)
from rebaseguard_location_family.route_a import (
    location_score,
    log_density,
    trace_raw,
)
from rebaseguard_location_family.route_b import trace_signed
from rebaseguard_location_family.statistics import (
    combined_z,
    mean_se,
    observed_order,
    paired_derivatives,
    richardson,
    symmetric_relative_difference,
)

CAMPAIGN = Path(__file__).resolve().parents[1]


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    result = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            result.add(node.module or "")
    return result


def test_frozen_constants_match_protocol_exactly():
    assert MASTER_SEED == 2026082307
    assert H_STEPS == (0.05, 0.025, 0.0125)
    assert PRIMARY_H == 0.0125
    assert ROUTE_A_BATCHES == ROUTE_B_BATCHES == 48
    assert ROUTE_A_PATHS_PER_BATCH == 10_000
    assert ROUTE_B_PATHS_PER_BATCH == 5_000
    assert set(THRESHOLDS) == set(FAMILIES)
    assert THRESHOLDS["t3"] == 6.337011391962933


def test_scores_equal_negative_log_density_derivative():
    grid = np.array([-4.0, -1.25, -0.2, 0.0, 0.2, 1.25, 4.0])
    dx = 1e-6
    for family in FAMILIES:
        expected = -(
            log_density(family, grid + dx) - log_density(family, grid - dx)
        ) / (2.0 * dx)
        np.testing.assert_allclose(
            location_score(family, grid), expected, rtol=0.0, atol=2e-7
        )


def test_gaussian_reduction_is_pointwise_exact():
    grid = np.array([-3.0, -0.0, 0.25, 2.5])
    assert np.array_equal(location_score("gaussian", grid), grid)


def test_independent_chart_representations_agree_and_reflect():
    path = np.full(40, 1.25)
    for threshold in THRESHOLDS.values():
        raw = trace_raw(path, threshold)
        signed = trace_signed(path, threshold)
        reflected_raw = trace_raw(-path, threshold)
        reflected_signed = trace_signed(-path, threshold)
        assert raw[0] == signed[0] == reflected_raw[0] == reflected_signed[0]
        assert raw[1] == signed[1] == -reflected_raw[1] == -reflected_signed[1]
        assert raw[3] == signed[2] == -reflected_raw[3] == -reflected_signed[2]
        assert raw[2] == -reflected_raw[2]
        assert raw[1] * raw[2] == reflected_raw[1] * reflected_raw[2]


def test_route_sources_are_independent_and_route_b_has_no_gain_logic():
    route_a = CAMPAIGN / "src/rebaseguard_location_family/route_a.py"
    route_b = CAMPAIGN / "src/rebaseguard_location_family/route_b.py"
    assert not any("route_b" in name for name in _imports(route_a))
    assert not any("route_a" in name for name in _imports(route_b))
    route_b_text = route_b.read_text().lower()
    for forbidden in ("location_score", "psi_total", "gamma_f", "stopped_gain"):
        assert forbidden not in route_b_text


def test_paired_batch_derivative_uses_maps_from_same_batch():
    errors = np.array([-0.05, 0.05, -0.025, 0.025, -0.0125, 0.0125])
    maps = 2.0 * errors + errors**3
    derivative = paired_derivatives(maps, errors, H_STEPS)
    expected = np.array([2.0 + h * h for h in H_STEPS])
    np.testing.assert_allclose(derivative, expected, rtol=0.0, atol=1e-14)
    assert abs(observed_order(derivative) - 2.0) < 1e-10
    assert abs(richardson(derivative[1], derivative[2]) - 2.0) < 1e-14


def test_batch_statistics_have_frozen_covariance_aware_forms():
    mean, se = mean_se(np.array([1.0, 2.0, 3.0, 4.0]))
    assert mean == 2.5
    assert se == np.std([1.0, 2.0, 3.0, 4.0], ddof=1) / 2.0
    assert combined_z(2.0, 0.3, 1.5, 0.4) == 1.0
    assert symmetric_relative_difference(-2.0, -2.0) == 0.0


def test_runner_has_no_quick_or_sample_size_override():
    runner = (CAMPAIGN / "numerics/run_correspondence.py").read_text()
    assert "argparse" not in runner
    assert "--quick" not in runner
    assert "ROUTE_A_BATCHES" in runner
    assert "ROUTE_B_PATHS_PER_BATCH" in runner
    assert "NUMERICAL GATE CLOSED — LEAN AUTHORIZED" in runner

