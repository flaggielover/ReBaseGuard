"""The four cost-driving configurations must be the ones the audit named,
reconstructed from the frozen Priority-4 artifacts rather than guessed."""

from __future__ import annotations

import pytest

EXPECTED = {
    ("frozen", "sr@520.886", "t1p5"),
    ("frozen", "cusum@5", "t1p5"),
    ("reduced", "sr@20", "t1p5"),
    ("frozen", "sr@520.886", "skewnormal4"),
}


def test_audit_named_exactly_these_four(pilot_dir):
    """The names are read from the audit's own draft successor scope."""
    text = (pilot_dir.parent / "feasibility_and_scope_audit"
            / "DRAFT_SUCCESSOR_SCOPE.md").read_text()
    for fragment in ("frozen/sr/t1p5", "frozen/cusum/t1p5",
                     "reduced/sr/t1p5", "frozen/sr/skewnormal4"):
        assert fragment in text, fragment


def test_pilot_covers_exactly_the_four_configurations(pilot):
    got = set()
    for name in pilot["results"]:
        layer, detector, family = name.split("/")
        got.add((layer, detector, family))
    assert got == EXPECTED


def test_frozen_sr_t1p5_is_among_them(pilot):
    assert "frozen/sr@520.886/t1p5" in pilot["results"]


@pytest.mark.parametrize("layer,detector,family", sorted(EXPECTED))
def test_each_configuration_exists_in_the_frozen_p4_grid(
        p4_correspondence, layer, detector, family):
    cells = [c for c in p4_correspondence["monte_carlo"]["cells"]
             if (c["layer"], c["detector"], c["family"]) == (layer, detector, family)]
    assert len(cells) == 4, (layer, detector, family)
    assert {c["m"] for c in cells} == {1, 2, 3, 5}


def test_historical_relative_se_matches_the_frozen_artifact(pilot, p4_correspondence):
    """Every historical relative SE quoted by the pilot is recomputable."""
    for name, res in pilot["results"].items():
        layer, detector, family = name.split("/")
        for m_str, quoted in res["config"]["hist_rel_se"].items():
            cell = next(c for c in p4_correspondence["monte_carlo"]["cells"]
                        if (c["layer"], c["detector"], c["family"], c["m"])
                        == (layer, detector, family, int(m_str)))
            actual = cell["route_b"]["se"] / abs(cell["route_b"]["mean"])
            assert actual == pytest.approx(quoted, rel=2e-3), (name, m_str)


def test_the_three_t1p5_configs_are_variance_limited(pilot, p4_correspondence):
    """t1p5 fails on precision: Route-B relative SE is comparable to the gate."""
    for name in ("frozen/sr@520.886/t1p5", "frozen/cusum@5/t1p5",
                 "reduced/sr@20/t1p5"):
        layer, detector, family = name.split("/")
        cell = next(c for c in p4_correspondence["monte_carlo"]["cells"]
                    if (c["layer"], c["detector"], c["family"], c["m"])
                    == (layer, detector, family, 1))
        rel_se = cell["route_b"]["se"] / abs(cell["route_b"]["mean"])
        assert rel_se > 0.03, name          # exceeds the accuracy gate itself
        assert cell["correspondence"]["z"] < 4.0, name   # yet consistent


def test_the_skewnormal_config_is_bias_limited_not_variance_limited(
        p4_correspondence):
    """skewnormal4 is precise and offset: the opposite pathology."""
    cells = [c for c in p4_correspondence["monte_carlo"]["cells"]
             if (c["layer"], c["detector"], c["family"])
             == ("frozen", "sr@520.886", "skewnormal4")]
    for cell in cells:
        rel_se = cell["route_b"]["se"] / abs(cell["route_b"]["mean"])
        assert rel_se < 0.006, cell["m"]                       # precise
        assert cell["correspondence"]["relative_discrepancy"] > 0.02, cell["m"]
    # one-signed: Route B sits above Route A at every window
    assert all(c["route_b"]["mean"] > c["route_a"]["mean"] for c in cells)
