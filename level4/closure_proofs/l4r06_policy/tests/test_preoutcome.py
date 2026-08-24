from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path

import numpy as np
import pytest

import analysis
import campaign
import policy
import simulator
from config import (
    ACTIVE_REGIMES,
    COMBINED_PROTOCOL_SHA256,
    N_BOOTSTRAP,
    REGIMES,
    SEED_ADVERSARIAL,
    SEED_BOOTSTRAP,
    SEED_CONFIRM,
    SHIFTS,
)
from detection import DetectionConfig, simulate_detection
from integrity import verify
from rebaseguard_level4.multicycle import (
    MultiCycleConfig,
    simulate_multicycle,
)

CAMPAIGN = Path(__file__).resolve().parents[1]
ROOT = CAMPAIGN.parents[2]


def test_frozen_protocol_and_history_are_intact():
    result = verify()
    assert result["status"] == "PASS", result["errors"]
    record = json.loads((CAMPAIGN / "results/protocol_hash.json").read_text())
    chunks = b"".join((CAMPAIGN / name).read_bytes()
                      for name in record["combined_sha256_order"])
    assert hashlib.sha256(chunks).hexdigest() == COMBINED_PROTOCOL_SHA256
    assert record["confirmatory_outcomes_existed_when_frozen"] is False


def test_policy_is_reconstructed_from_the_protected_d4_lower_bound():
    expected = {
        1: 0.05364218801989182,
        20: 0.24541780396034488,
        70: 0.7819935545467208,
        100: 1.0,
    }
    d4 = policy.d4_lower_bounds()
    for m, want in expected.items():
        action = policy.p3_action(m)
        assert action.rho == pytest.approx(want, abs=1e-15)
        assert action.uncapped_allowance == pytest.approx(0.8 * d4[m], abs=1e-15)
        assert action.rho == min(1.0, action.uncapped_allowance)
        assert action.multiplier_bound <= 0.8 + 1e-15
    assert policy.p3_action(100).saturated
    assert policy.p3_action(100).uncapped_allowance > 1.0


def test_no_point_estimate_policy_or_p4_exists():
    source = inspect.getsource(policy) + inspect.getsource(campaign)
    assert '"P4"' not in source and "point_estimate" not in source
    assert set(policy.policies(20)) == {"P0", "P1", "P2", "P3"}


def test_regimes_allocation_seeds_and_cell_grid_are_frozen():
    assert REGIMES == (1, 20, 70, 100)
    assert ACTIVE_REGIMES == (1, 20, 70)
    assert SHIFTS == (0.25, 0.5, 1.0, 1.5)
    assert (SEED_CONFIRM, SEED_BOOTSTRAP, SEED_ADVERSARIAL) == (
        2026082406, 2026082407, 2026082408)
    assert N_BOOTSTRAP == 10_000
    keys = campaign.expected_keys()
    assert len(keys) == 4 * 4 * 5 == 80
    assert len({campaign.key_hash(k) for k in keys}) == 80
    assert all(k["n_replicates"] == 200 and k["n_events"] == 200 for k in keys)


@pytest.mark.parametrize("m", REGIMES)
@pytest.mark.parametrize("rho", [0.0, 0.0297958439, 1.0])
def test_zero_shift_matches_frozen_multicycle_oracle_bit_for_bit(m, rho):
    cfg = simulator.ArmConfig(
        n_replicates=4, n_events=4, burn_in=3, cycles_between=2,
        rho=rho, m=m, shift=0.0, master_seed=81422,
    )
    got = simulator.simulate_arm(cfg, retain_trace=True)["_trace"]
    want = simulate_multicycle(MultiCycleConfig(
        n_replicates=4, n_cycles=12, burn_in=3, rho=rho, m=m,
        master_seed=81422, max_steps=100_000_000,
    ))
    shape = (4, 15)
    assert np.array_equal(got["e_prev"], want.e_prev.reshape(shape))
    assert np.array_equal(got["e_next"], want.e_next.reshape(shape))
    assert np.array_equal(got["tau"], want.tau.reshape(shape))
    assert np.array_equal(got["direction"], want.direction.reshape(shape))


def test_shifted_m1_matches_immutable_stage_c_semantics():
    common = dict(n_replicates=5, burn_in=3, rho=0.2, shift=0.5,
                  master_seed=99817, n_changes=4, cycles_between=2)
    got = simulator.simulate_arm(simulator.ArmConfig(
        n_replicates=5, n_events=4, burn_in=3, cycles_between=2,
        rho=0.2, m=1, shift=0.5, master_seed=99817,
    ), retain_trace=True)["_trace"]
    want = simulate_detection(DetectionConfig(n_cycles_after=1, **common))
    shape = (5, 15)
    assert np.array_equal(got["e_prev"], want.e_prev.reshape(shape))
    assert np.array_equal(got["e_next"], want.e_next.reshape(shape))
    assert np.array_equal(got["tau"], want.tau.reshape(shape))


def test_boundary_shift_occurs_before_cycle_zero_when_burnin_is_zero():
    got = simulator.simulate_arm(simulator.ArmConfig(
        n_replicates=3, n_events=2, burn_in=0, cycles_between=0,
        rho=0.0, m=1, shift=0.5, master_seed=76,
    ), retain_trace=True)["_trace"]
    want = simulate_detection(DetectionConfig(
        n_replicates=3, burn_in=0, n_cycles_after=1, rho=0.0,
        shift=0.5, master_seed=76, n_changes=2, cycles_between=0,
    ))
    assert np.array_equal(got["e_prev"], want.e_prev.reshape(3, 2))
    assert np.array_equal(got["tau"], want.tau.reshape(3, 2))


def test_simultaneous_family_bound_is_joint_and_directional():
    rng = np.random.default_rng(5)
    x = rng.normal(size=(200, 3))
    idx = rng.integers(0, 200, size=(1000, 200))
    funcs = [lambda ix, j=j: float(x[:, j].mean()) if ix is None
             else x[ix, j].mean(axis=1) for j in range(3)]
    upper = analysis._family([{"j": j} for j in range(3)], funcs, idx, "upper")
    lower = analysis._family([{"j": j} for j in range(3)], funcs, idx, "lower")
    assert upper["family_size"] == lower["family_size"] == 3
    assert upper["critical_value"] > 1.0 and lower["critical_value"] > 1.0
    for u, lo in zip(upper["rows"], lower["rows"], strict=True):
        assert lo["simultaneous_lower95"] < lo["point"]
        assert u["simultaneous_upper95"] > u["point"]


def test_original_requirement_and_immutable_c6_are_documented_exactly():
    audit = (CAMPAIGN / "REQUIREMENT_AUDIT.md").read_text()
    protocol = (CAMPAIGN / "PROTOCOL.md").read_text()
    assert "Stability-aware reuse policy with monitoring consequences" in audit
    assert "C6" in audit and "{0.25,0.5,1.0,1.5}" in audit
    assert "| 0.25 |" in audit and "| 0.50 |" in audit
    assert "Stage C remains `STAGE-C-PARTIAL`" in protocol
    assert "L4R-12 is untouched" in protocol


def test_result_contract_if_confirmatory_artifacts_exist():
    path = CAMPAIGN / "results/scientific_findings.json"
    if not path.exists():
        return
    data = json.loads(path.read_text())
    assert data["allocation"]["n_cells"] == 80
    assert data["historical_firewall"]["historical_C6"] == "FAILED"
    assert len(data["H6-2"]["family"]["rows"]) == 3
    assert len(data["H6-3"]["family"]["rows"]) == 3
    assert len(data["H6-4"]["family"]["rows"]) == 16
    assert len(data["absolute_delay_safety"]["family"]["rows"]) == 16
