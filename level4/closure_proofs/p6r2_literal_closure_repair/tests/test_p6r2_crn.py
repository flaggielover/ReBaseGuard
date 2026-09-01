"""G9: the CRN sensitivity must be free of the RNG-stream confound."""
import inspect

import numpy as np

from rebaseguard_p6r2 import fixedpath as FP


def test_cycle_streams_depend_only_on_cell_and_cycle_never_on_the_policy():
    sig = set(inspect.signature(FP.cycle_streams).parameters)
    assert sig == {"cell_tag", "cycle", "n_rep", "tape_len"}
    assert "policy" not in sig and "policy_id" not in sig
    a = FP.cycle_streams("cusum_m3", 4, 50, 64)
    b = FP.cycle_streams("cusum_m3", 4, 50, 64)
    assert np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1])


def test_different_cells_or_cycles_give_different_tapes():
    t0 = FP.cycle_streams("cusum_m3", 0, 40, 32)[0]
    assert not np.array_equal(t0, FP.cycle_streams("cusum_m3", 1, 40, 32)[0])
    assert not np.array_equal(t0, FP.cycle_streams("sr_m3", 0, 40, 32)[0])


def test_variants_see_identical_innovations_so_s1_alone_can_move_the_outcome():
    """Two variants differing ONLY in s1 must share the first cycle exactly."""
    kw = dict(detector="cusum", m=3, k=3, n_rep=250, n_cycles=6, burn_in=1,
              cell_tag="unit_test_cell", tape_len=600)
    base = FP.simulate_fixed_path(decide=FP.saw_decider(0.94, -1.07, 0.063, 2.56, 3, 3), **kw)
    pert = FP.simulate_fixed_path(decide=FP.saw_decider(0.94, -1.07, 0.063, 5.12, 3, 3), **kw)
    # cycle 0 starts from e = 0 in both, on the same tape: identical throughout
    assert np.array_equal(base["tau"][:, 0], pert["tau"][:, 0])
    assert np.array_equal(base["zbar"][:, 0], pert["zbar"][:, 0])
    assert np.array_equal(base["e_start"][:, 0], pert["e_start"][:, 0])


def test_a_policy_that_changes_rho_does_change_later_cycles():
    """CRN fixes the inputs; it must not make the perturbation invisible."""
    kw = dict(detector="cusum", m=3, k=3, n_rep=250, n_cycles=6, burn_in=1,
              cell_tag="unit_test_cell", tape_len=600)
    a = FP.simulate_fixed_path(decide=lambda z, t, w: np.full(z.size, 0.10), **kw)
    b = FP.simulate_fixed_path(decide=lambda z, t, w: np.full(z.size, 0.60), **kw)
    assert np.array_equal(a["zbar"][:, 0], b["zbar"][:, 0])      # same inputs
    assert not np.array_equal(a["e_start"][:, 1], b["e_start"][:, 1])  # different state


def test_s1_cannot_move_anything_when_no_window_is_truncated():
    """At m = 1, w == m always, so s1 never fires: movement must be EXACTLY zero."""
    kw = dict(detector="cusum", m=1, k=1, n_rep=300, n_cycles=8, burn_in=2,
              cell_tag="unit_test_m1", tape_len=800)
    a = FP.simulate_fixed_path(decide=FP.saw_decider(0.97, -1.02, 0.123, 0.123, 1, 1), **kw)
    b = FP.simulate_fixed_path(decide=FP.saw_decider(0.97, -1.02, 0.123, 9.999, 1, 1), **kw)
    assert a["rho_mean"] == b["rho_mean"]
    assert a["rms"] == b["rms"] and a["arl0"] == b["arl0"]


def test_the_driver_uses_the_frozen_detector_step():
    src = inspect.getsource(FP)
    assert "from rebaseguard_p7.detectors import make_step" in src
    assert "def cusum_update" not in src and "logaddexp" not in src


def test_convention_a_truncated_denominator_holds_in_the_driver():
    out = FP.simulate_fixed_path(
        detector="cusum", decide=lambda z, t, w: np.ones(z.size),   # rho = 1
        m=5, k=5, n_rep=400, n_cycles=6, burn_in=0, cell_tag="convA", tape_len=900)
    # rho = 1 => e_{j+1} = e_j + zbar_j exactly
    lhs = out["e_start"][:, 1:]
    rhs = (out["e_start"] + out["zbar"])[:, :-1]
    assert np.abs(lhs - rhs).max() < 1e-12
    assert (out["tau"] < 5).any(), "need truncated windows for this to bite"
