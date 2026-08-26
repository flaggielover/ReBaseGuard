"""Consistency guards for the rigorous SR Taylor remainder profile."""

from __future__ import annotations

import json
from pathlib import Path

from flint import arb


RESULTS = Path(__file__).resolve().parents[1] / "results"


def load_profile():
    return json.loads((RESULTS / "sr_residual_remainder_budget.json").read_text())


def test_profile_reconstructs_committed_blocker_remainder():
    profile = load_profile()
    blocker = json.loads((RESULTS / "sr_taylor_residual_blocker.json").read_text())
    profiled = arb(profile["additive_budget"]["total_taylor_remainder"]["ball"])
    committed = arb(
        blocker["first_continuum_patch"]["taylor_remainder_a_upper"]["ball"]
    )
    assert not (profiled < committed or committed < profiled)


def test_profile_additive_integration_channels_sum_exactly():
    profile = load_profile()
    channels = profile["additive_budget"]["integration_channels"]
    channel_sum = sum(
        (arb(record["rigorous_upper"]["ball"]) for record in channels.values()),
        arb(0),
    )
    integration = arb(profile["additive_budget"]["integration_remainder"]["ball"])
    assert not (channel_sum < integration or integration < channel_sum)


def test_profile_identifies_dependency_and_mixed_terms_as_dominant():
    profile = load_profile()
    budget = profile["additive_budget"]
    dependency = arb(budget["interval_dependency_slack_total"]["ball"])
    integration = arb(budget["integration_remainder"]["ball"])
    mixed = arb(
        budget["integration_channels"]["mixed_state_innovation"]["rigorous_upper"][
            "ball"
        ]
    )
    innovation = arb(
        budget["integration_channels"]["innovation_width_only"]["rigorous_upper"][
            "ball"
        ]
    )
    assert dependency > arb(999) * integration / arb(1000)
    assert mixed > innovation
    assert mixed + innovation > arb(999) * integration / arb(1000)


def test_profile_accounts_for_no_tail_or_bernstein_term_yet():
    profile = load_profile()
    budget = profile["additive_budget"]
    assert arb(budget["tail_remainder"]["ball"]).contains(0)
    assert arb(budget["bernstein_remainder"]["ball"]).contains(0)
    assert profile["sampled_grid_used"] is False
    assert profile["reachable_geometry"]["global_reachable_cover_complete"] is False
