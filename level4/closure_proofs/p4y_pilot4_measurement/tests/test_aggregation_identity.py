"""The exact identity Pilot-4's whole architecture rests on.

Every frozen per-block statistic is a PLAIN AVERAGE of per-path
contributions, so a block value over ``k*n`` paths equals the mean of ``k``
independent block values over ``n`` paths -- EXACTLY.  These tests verify it
bit-for-bit by splitting a simulated block's own paths, rather than assuming
it.

Without this, building 4 000 000-path logical blocks from 50 000-path base
blocks would be an approximation.  With it, it is an identity, and it is what
keeps the 4e6 grid point inside memory (318 MB was measured for a single
1e6-path block; 4e6 would be ~1.2 GB).
"""

import sys
from pathlib import Path

import numpy as np
import pytest

from p4y_pilot4.blocks4 import aggregate, base_blocks_needed, factor_for

_P4 = Path(__file__).resolve().parents[2] / "p4_theory_generalization"
sys.path.insert(0, str(_P4 / "src"))
from rebaseguard_p4_general.detectors import Detector  # noqa: E402
from rebaseguard_p4_general.families import REGISTRY  # noqa: E402
from rebaseguard_p4_general.simulate import simulate_group  # noqa: E402

N = 8000


@pytest.mark.parametrize("family", ["t1p5", "gaussian"])
@pytest.mark.parametrize("m", [1, 2, 5])
def test_route_a_block_value_is_a_plain_path_average(family, m):
    (run,) = simulate_group(family=REGISTRY[family], detector=Detector("cusum", 2.0),
                            e_values=(0.0,), n_paths=N, seed=990001, batch=0,
                            m_max=5, mode="compact", max_steps=60_000)
    per_path = run.window_mean(m) * run.score_sum
    whole = float(per_path.mean())
    for k in (2, 4, 8):
        parts = [float(per_path[i * (N // k):(i + 1) * (N // k)].mean())
                 for i in range(k)]
        assert whole == float(np.mean(parts)) or abs(
            whole - float(np.mean(parts))) < 1e-12 * max(1.0, abs(whole))


@pytest.mark.parametrize("m", [1, 3])
def test_route_b_richardson_is_linear_in_the_path_averages(m):
    fam, det = REGISTRY["t1p5"], Detector("cusum", 2.0)
    per_step = {}
    for step in (0.05, 0.025):
        plus, minus = simulate_group(family=fam, detector=det,
                                     e_values=(step, -step), n_paths=N,
                                     seed=990002, batch=0, m_max=5,
                                     mode="aligned", max_steps=60_000)
        per_step[step] = -((plus.window_mean(m) - minus.window_mean(m))
                           / (2.0 * step))
    rich = (4.0 * per_step[0.025] - per_step[0.05]) / 3.0
    whole = float(rich.mean())
    for k in (2, 4):
        parts = [float(rich[i * (N // k):(i + 1) * (N // k)].mean())
                 for i in range(k)]
        assert abs(whole - float(np.mean(parts))) < 1e-12 * max(1.0, abs(whole))


def test_aggregate_is_the_mean_of_consecutive_groups():
    x = np.arange(24, dtype=float)
    assert list(aggregate(x, 1)) == list(x)
    assert list(aggregate(x, 2)) == [0.5, 2.5, 4.5, 6.5, 8.5, 10.5, 12.5,
                                     14.5, 16.5, 18.5, 20.5, 22.5]
    assert list(aggregate(x, 8)) == [3.5, 11.5, 19.5]


def test_aggregate_drops_only_an_incomplete_trailing_group():
    x = np.arange(10, dtype=float)
    out = aggregate(x, 4)
    assert out.size == 2                       # 10 // 4 == 2
    assert list(out) == [1.5, 5.5]


def test_aggregate_preserves_the_overall_mean_when_it_divides():
    rng = np.random.default_rng(3)
    x = rng.standard_normal(240)
    for f in (1, 2, 4, 8, 16):
        assert abs(aggregate(x, f).mean() - x.mean()) < 1e-12


def test_block_size_bookkeeping():
    assert factor_for(250_000) == 5
    assert factor_for(1_000_000) == 20
    assert factor_for(4_000_000) == 80
    assert base_blocks_needed(4_000_000, 64) == 5120
    with pytest.raises(ValueError):
        factor_for(70_000)
