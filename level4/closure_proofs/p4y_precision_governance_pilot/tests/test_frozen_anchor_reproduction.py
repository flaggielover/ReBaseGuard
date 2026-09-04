"""Zero-compute reproduction of the frozen Priority-4 Route-Q anchors.

Route Q is deterministic quadrature: no Monte Carlo, no seed, no sampling.  If
the frozen scientific machinery still evaluates to the recorded numbers in
THIS environment, then a future P4Y can be reproduced here; if it does not,
that is estimator/environment drift and a kill criterion.

The pilot's own Monte Carlo does not need to reproduce P4X's numbers -- it
uses fresh seeds by design -- so this is the only bit-level tie to the frozen
campaign, and it is deliberately the deterministic one.
"""

import json
import sys
from pathlib import Path

import pytest

_P4 = Path(__file__).resolve().parents[2] / "p4_theory_generalization"
sys.path.insert(0, str(_P4 / "src"))

from rebaseguard_p4_general import quadrature as routeq  # noqa: E402
from rebaseguard_p4_general.families import REGISTRY  # noqa: E402

FROZEN = json.loads((_P4 / "results" / "correspondence.json").read_text())
PROTOCOL = json.loads((_P4 / "configs" / "P4_PROTOCOL.json").read_text())
ROWS = FROZEN["route_q"]["rows"]
C = PROTOCOL["route_q"]["c"]
TOL = PROTOCOL["route_q"]["tolerance_relative"]


@pytest.mark.parametrize("row", ROWS, ids=lambda r: f"{r['family']}_m{r['m']}")
def test_route_q_gain_reproduces_the_frozen_value(row):
    gain, _ = routeq.gain(REGISTRY[row["family"]], C, row["m"])
    assert gain == pytest.approx(row["gamma_score_route"], rel=1e-10)


@pytest.mark.parametrize("row", ROWS, ids=lambda r: f"{r['family']}_m{r['m']}")
def test_route_q_map_derivative_reproduces_the_frozen_value(row):
    d = routeq.map_derivative(REGISTRY[row["family"]], C, row["m"])
    assert -d == pytest.approx(row["negative_map_derivative"], rel=1e-8)


@pytest.mark.parametrize("row", ROWS, ids=lambda r: f"{r['family']}_m{r['m']}")
def test_the_frozen_route_q_identity_still_holds(row):
    """The theorem's own identity, re-evaluated rather than re-read."""
    gain, _ = routeq.gain(REGISTRY[row["family"]], C, row["m"])
    d = routeq.map_derivative(REGISTRY[row["family"]], C, row["m"])
    assert abs(gain + d) / max(abs(gain), 1e-12) <= TOL


def test_the_frozen_protocol_file_is_the_one_the_results_were_built_from():
    import hashlib

    raw = (_P4 / "configs" / "P4_PROTOCOL.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == FROZEN["protocol_sha256"]


def test_r_star_is_forced_by_the_unchanged_three_percent_criterion():
    import math

    from p4y_pilot.config import R_STAR_PRODUCTION

    limit = PROTOCOL["gates"]["correspondence_relative_limit"]
    assert limit == 0.03
    assert R_STAR_PRODUCTION == pytest.approx(limit / (1.96 * math.sqrt(2)),
                                              abs=5e-7)


def test_the_inherited_m_grid_and_steps_are_unchanged():
    from p4y_pilot.config import FD_STEPS, M_GRID

    assert list(M_GRID) == PROTOCOL["m_grid"] == [1, 2, 3, 5]
    assert list(FD_STEPS) == PROTOCOL["fd_steps"] == [0.05, 0.025]


def test_the_inherited_gate_is_unchanged():
    assert PROTOCOL["gates"]["correspondence_relative_limit"] == 0.03
    assert PROTOCOL["gates"]["correspondence_z_limit"] == 4.0
