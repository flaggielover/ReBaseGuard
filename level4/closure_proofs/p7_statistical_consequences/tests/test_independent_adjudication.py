"""Checks for the independent, non-production-seed replay artifact."""
import json

from rebaseguard_p7.config import RESULTS, SEED_FAMILY


def replay():
    return json.loads((RESULTS / "independent_adjudication_replay.json").read_text())


def test_independent_replay_uses_a_distinct_stable_seed_family():
    data = replay()
    assert data["seed_family"] not in {
        SEED_FAMILY,
        data["campaign_adversarial_seed_family"],
    }
    assert max(abs(row["z_vs_production"]) for row in data["in_control"]) < 2.0


def test_independent_replay_preserves_headline_and_tail_mechanisms():
    data = replay()
    full = [row for row in data["in_control"] if row["rho"] == 1.0]
    assert len(full) == 8
    assert all(47.0 < row["arl"] < 82.0 for row in full)
    assert all(0.81 < row["fap100"] < 0.91 for row in full)
    assert all(5.0 < row["cycle_2_arl"] < 10.0 for row in full)
    for row in data["delay"]:
        assert row["median"] <= 10.0
        assert row["q95"] > 250.0
        assert row["p_gt_100"] > 0.11
        assert row["mean_delay_inside_0p2"] > 10 * row["mean_delay_outside_0p2"]
        assert row["p_gt_100_inside_0p2"] > 10 * row["p_gt_100_outside_0p2"]
    assert data["boundary_criterion_met"] is False
