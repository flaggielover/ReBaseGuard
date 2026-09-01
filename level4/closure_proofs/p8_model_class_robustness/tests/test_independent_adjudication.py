"""Independent adjudicator checks for window extraction and row banding.

These tests deliberately reconstruct expected values from primitive addresses
instead of reusing the ring-buffer extraction under review.
"""
from __future__ import annotations

import numpy as np

from rebaseguard_p8 import primitives as PR
from rebaseguard_p8.chain import simulate_chain
from rebaseguard_p8.stopped import simulate_row_block


EXP = "codex_independent_adjudication"


def test_stopped_windows_equal_naive_address_reconstruction():
    sample = simulate_row_block(
        experiment=EXP,
        family="t5",
        detector="cusum",
        threshold=5.669498491821448,
        batch=17,
        row_block=0,
        n_paths=768,
    )
    paths = np.linspace(0, sample.tau.size - 1, 97, dtype=int)
    for m in (1, 2, 3, 5, 10, 20):
        expected = []
        for path in paths:
            tau = int(sample.tau[path])
            lo = max(0, tau - m)
            raw = [
                PR.stopped_value(EXP, "t5", 17, int(path), t)
                for t in range(lo, tau)
            ]
            expected.append(float(np.mean(raw)))
        assert np.allclose(sample.zbar(m, "A")[paths], expected,
                           rtol=0.0, atol=1e-15)


def test_window_edges_tau_m_and_m_plus_one_are_exact():
    sample = simulate_row_block(
        experiment=EXP,
        family="gaussian",
        detector="cusum",
        threshold=5.0,
        batch=18,
        row_block=0,
        n_paths=4096,
    )
    for m in (1, 2, 3, 5, 10, 20):
        for tau in (m, m + 1):
            hit = np.flatnonzero(sample.tau == tau)
            if not hit.size:
                continue
            path = int(hit[0])
            raw = [
                PR.stopped_value(EXP, "gaussian", 18, path, t)
                for t in range(tau - m, tau)
            ]
            assert abs(sample.zbar(m, "A")[path] - np.mean(raw)) <= 1e-15


def test_stopped_request_size_does_not_change_overlapping_addresses():
    for n_small, n_large in ((255, 256), (256, 257), (4095, 4096), (4096, 4097)):
        small = PR.stopped_column(EXP, "contam0.05", 19, 513, n_small)
        large = PR.stopped_column(EXP, "contam0.05", 19, 513, n_large)
        assert np.array_equal(small, large[:n_small])


def test_chain_row_band_boundaries_and_request_sizes_are_exact():
    for n_small, n_large in ((255, 256), (256, 257), (511, 512), (512, 513)):
        small = PR.chain_monitor_column(
            EXP, "t10", "sr", 5, 3, 1025, n_small
        )
        large = PR.chain_monitor_column(
            EXP, "t10", "sr", 5, 3, 1025, n_large
        )
        assert np.array_equal(small, large[:n_small])


def test_chain_first_cycle_window_equals_naive_primitive_path():
    result = simulate_chain(
        experiment=EXP,
        family="gaussian",
        detector="cusum",
        threshold=5.0,
        m=5,
        rho=1.0,
        n_rep=64,
        n_cycles=1,
        burn_in=0,
    )
    for path in range(64):
        tau = int(result.tau[path, 0])
        lo = max(0, tau - 5)
        expected = np.mean(
            [
                PR.chain_monitor_column(
                    EXP, "gaussian", "cusum", 5, 0, t, 64
                )[path]
                for t in range(lo, tau)
            ]
        )
        assert abs(result.zbar[path, 0] - expected) <= 1e-15
