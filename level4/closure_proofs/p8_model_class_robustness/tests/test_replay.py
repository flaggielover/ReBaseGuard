"""Replay reproducibility: a re-run at the same addresses is bit-identical."""
import numpy as np

from rebaseguard_p8 import primitives as PR
from rebaseguard_p8.chain import simulate_chain
from rebaseguard_p8.stopped import simulate_batch, simulate_row_block

EXP = "unit_test"


def test_stopped_row_block_replays_bit_for_bit():
    kw = dict(experiment=EXP, family="t5", detector="cusum",
              threshold=5.669498491821448, batch=2, row_block=1, n_paths=1024)
    a = simulate_row_block(**kw)
    PR.clear_cache()
    b = simulate_row_block(**kw)
    assert np.array_equal(a.tau, b.tau)
    assert np.array_equal(a.T, b.T) and np.array_equal(a.Psi, b.Psi)
    assert np.array_equal(a.lag_z, b.lag_z)


def test_stopped_batch_is_the_concatenation_of_its_row_blocks():
    kw = dict(experiment=EXP, family="gaussian", detector="cusum",
              threshold=5.0, batch=3)
    whole = simulate_batch(n_row_blocks=2, L=4, **kw)
    parts = [simulate_row_block(row_block=rb, L=4, **kw) for rb in range(2)]
    assert np.array_equal(whole.tau, np.concatenate([p.tau for p in parts]))


def test_chain_replays_bit_for_bit():
    kw = dict(experiment=EXP, family="contam0.05", detector="sr",
              threshold=1000.0, m=3, rho=0.4, n_rep=128, n_cycles=5, burn_in=1)
    a = simulate_chain(**kw)
    PR.clear_cache()
    b = simulate_chain(**kw)
    assert np.array_equal(a.tau, b.tau)
    assert np.array_equal(a.e_start, b.e_start)


def test_a_single_replicate_is_recoverable_alone():
    """Replicate r's primitive path does not depend on how many others ran."""
    big = PR.chain_monitor_column(EXP, "gaussian", "cusum", 1, 0, 5, 1024)
    need = np.zeros(1024, bool)
    need[777] = True
    small = PR.chain_monitor_column(EXP, "gaussian", "cusum", 1, 0, 5, 1024,
                                    need=need)
    assert small[777] == big[777]


def test_changing_rho_does_not_change_the_primitive_field():
    d1 = PR.chain_field_digest(EXP, "t10", "cusum", 2, 128, 3, 1)
    a = simulate_chain(experiment=EXP, family="t10", detector="cusum",
                       threshold=5.234517732360302, m=2, rho=0.0, n_rep=128,
                       n_cycles=3, burn_in=0)
    b = simulate_chain(experiment=EXP, family="t10", detector="cusum",
                       threshold=5.234517732360302, m=2, rho=1.0, n_rep=128,
                       n_cycles=3, burn_in=0)
    d2 = PR.chain_field_digest(EXP, "t10", "cusum", 2, 128, 3, 1)
    assert d1 == d2
    # cycle 0 is identical because it starts from the same state on the same
    # field; later cycles are free to diverge and are expected to.
    assert np.array_equal(a.tau[:, 0], b.tau[:, 0])
    assert not np.array_equal(a.tau[:, 2], b.tau[:, 2])
