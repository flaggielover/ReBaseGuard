"""Estimator non-drift for the Pilot-2 cells, and frozen-anchor reproduction.

Pilot-2 changes precision GOVERNANCE only.  The estimators, the theorem, the
detectors, r* and the correspondence gate are inherited and must be provably
untouched -- brief section 5 and the kill criteria.
"""

import json
import math
import sys
from pathlib import Path

import pytest

from p4y_pilot.blocks import FD_STEPS, M_GRID, block_value, summarise
from p4y_pilot2.addressing import seed
from p4y_pilot2.strata import (
    CELLS, FROZEN_ACCURACY_CRITERION, KAPPA_A, KAPPA_B, R_STAR, R_STAR_EXACT,
)

_P4 = Path(__file__).resolve().parents[2] / "p4_theory_generalization"
sys.path.insert(0, str(_P4 / "src"))
from rebaseguard_p4_general.detectors import Detector  # noqa: E402
from rebaseguard_p4_general.estimators import route_a, route_b  # noqa: E402
from rebaseguard_p4_general.families import REGISTRY  # noqa: E402

BLOCKS = 6


@pytest.mark.parametrize("name", list(CELLS))
def test_per_block_pooling_reproduces_the_frozen_estimator_exactly(name):
    cell = CELLS[name]
    probe = type(cell)(key=cell.key, layer=cell.layer, kind=cell.kind,
                       threshold=cell.threshold, family=cell.family,
                       route=cell.route, max_steps=cell.max_steps,
                       block_size=2_000, heavy=cell.heavy)
    s = seed(name, "T1", "calibration", 0)
    common = dict(family=REGISTRY[probe.family],
                  detector=Detector(probe.kind, probe.threshold),
                  m_grid=M_GRID, batches=BLOCKS, paths=probe.block_size,
                  seed=s, max_steps=probe.max_steps)
    frozen = (route_a(**common) if probe.route == "route_a"
              else route_b(**common, fd_steps=FD_STEPS))
    blocks = [block_value(probe, s, i) for i in range(BLOCKS)]
    for m in M_GRID:
        got = summarise([b[m] for b in blocks])
        ref = frozen["by_m"][str(m)]["gamma"]
        assert got["mean"] == ref["mean"], f"{name} m={m} mean drifted"
        assert got["se"] == ref["se"], f"{name} m={m} se drifted"


def test_r_star_is_the_inherited_frozen_value():
    assert R_STAR == 0.010823
    assert R_STAR_EXACT == 0.010823062977345114
    assert R_STAR == pytest.approx(
        FROZEN_ACCURACY_CRITERION / (1.96 * math.sqrt(2)), abs=5e-7)
    protocol = json.loads((_P4 / "configs" / "P4_PROTOCOL.json").read_text())
    assert protocol["gates"]["correspondence_relative_limit"] == 0.03
    assert protocol["gates"]["correspondence_z_limit"] == 4.0


def test_the_frozen_protocol_file_still_hashes_to_its_recorded_digest():
    import hashlib

    corr = json.loads((_P4 / "results" / "correspondence.json").read_text())
    raw = (_P4 / "configs" / "P4_PROTOCOL.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == corr["protocol_sha256"]


def test_the_inherited_m_grid_and_fd_steps_are_unchanged():
    protocol = json.loads((_P4 / "configs" / "P4_PROTOCOL.json").read_text())
    assert list(M_GRID) == protocol["m_grid"] == [1, 2, 3, 5]
    assert list(FD_STEPS) == protocol["fd_steps"] == [0.05, 0.025]


def test_route_q_anchors_still_reproduce():
    """Deterministic quadrature: the environment has not drifted."""
    from rebaseguard_p4_general import quadrature as routeq

    corr = json.loads((_P4 / "results" / "correspondence.json").read_text())
    protocol = json.loads((_P4 / "configs" / "P4_PROTOCOL.json").read_text())
    c = protocol["route_q"]["c"]
    for row in corr["route_q"]["rows"]:
        gain, _ = routeq.gain(REGISTRY[row["family"]], c, row["m"])
        assert gain == pytest.approx(row["gamma_score_route"], rel=1e-10)


def test_the_two_kappa_candidates_are_the_frozen_pair():
    assert KAPPA_A == 1.0 - 1.0 / 1.47
    assert KAPPA_A == 0.3197278911564626
    assert KAPPA_B == 0.5
    checkpoint_kappa = 0.3197278911564626   # P4X heavy_tail_policy.kappa_t1p5
    assert KAPPA_A == checkpoint_kappa
