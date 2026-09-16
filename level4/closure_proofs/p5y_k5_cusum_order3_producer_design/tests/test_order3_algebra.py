"""Development unit tests. Seeds and systems are disjoint from config/QUALIFICATION_PROTOCOL.json trials."""
import json
import sys
from fractions import Fraction as Fr
from math import factorial
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))
import manufactured as MF  # noqa: E402
import order3_algebra as A  # noqa: E402
import qualify_nonscientific as Q  # noqa: E402


def test_series_derivatives_zero_kernel():
    """K = 0: F_r = S_r and W_(r,j) = 0 for j >= 1, so every derivative is the polynomial's."""
    s = [[[Fr(p + r + 1, p + 2)] for p in range(MF.DEG + 1)] for r in range(5)]
    sysm = MF.System(1, [[[Fr(0)]] for _ in range(MF.DEG + 1)], s, Fr(0))
    e = Fr(7, 5)
    obj = sysm.true_objects(e, 3)
    for r in range(5):
        for n in range(4):
            assert obj[("F", r)][n] == sysm.S_deriv(r, n, e)
    assert all(v == [Fr(0)] for (r, j) in A.W_INDICES for v in obj[("W", (r, j))])


def test_series_derivatives_constant_scalar_kernel():
    a = Fr(2, 7)
    s = [[[Fr((-1) ** p, factorial(p))] for p in range(MF.DEG + 1)] for _ in range(5)]
    sysm = MF.System(1, [[[a]]] + [[[Fr(0)]] for _ in range(MF.DEG)], s, Fr(0))
    e = Fr(1, 3)
    obj = sysm.true_objects(e, 3)
    for n in range(4):
        assert obj[("F", 0)][n][0] == sysm.S_deriv(0, n, e)[0] / (1 - a)
        assert obj[("W", (0, 2))][n][0] == a * a * sysm.S_deriv(0, n, e)[0]


def test_exact_candidates_have_zero_midpoint_error():
    sysm = MF.random_system(907, 2)
    inp, _ = MF.cell_inputs(sysm, Fr(3, 4), Fr(1, 40))
    res = A.cell_order3(inp)
    assert all(v == 0 for v in res["eps_mid"].values())
    assert all(v >= 0 for v in res["eps_cell"].values())


def test_small_sound_case_and_export_shape():
    sysm = MF.random_system(911, 1)
    e0, rho = Fr(1, 2), Fr(1, 40)
    inp, _ = MF.cell_inputs(sysm, e0, rho, seed=911, noise=Fr(1, 10 ** 5))
    res = A.cell_order3(inp)
    assert Q.violations(sysm, inp, res, e0, rho, (1, 5), objects=True, cell=True) == []
    rec = A.export_record("synthetic", e0, rho, res)
    assert set(rec["m"]) == {"1", "2", "3", "5"}
    for v in rec["m"].values():
        assert Fr(v["R3_cell_lower_L"]) <= Fr(v["R3_cell_upper_U"])


def test_reference_coefficients_equal_frozen_table():
    path = Q.REPO / "level4/closure_proofs/p5y_k1_cover_ledger_successor/config/checkpoint.json"
    table = json.loads(path.read_text())["assembly"]
    for m in A.M_VALUES:
        assert sorted((k, int(r), int(j), Fr(c)) for k, r, j, c in table[str(m)]) == sorted(A.coefficients(m))


def test_unknown_mutation_refused():
    sysm = MF.random_system(913, 1)
    inp, _ = MF.cell_inputs(sysm, Fr(1, 2), Fr(1, 40))
    try:
        A.cell_order3(inp, mutation="M0_NOT_A_MUTATION")
    except ValueError:
        return
    raise AssertionError("unknown mutation accepted")


def test_protocol_trials_disjoint_from_unit_seeds():
    proto = json.loads((NS / "config/QUALIFICATION_PROTOCOL.json").read_text())
    seeds = {t.get("seed") for t in proto["QN1_SOUNDNESS"]["trials"] + proto["QN2_MUTATION_SENSITIVITY"]["trials"]}
    assert seeds.isdisjoint({907, 911, 913})
    assert proto["status"] == "FROZEN_PRE_RESULT"


def test_static_fence_and_exactness():
    assert all(Q.static_checks().values()), Q.static_checks()


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
