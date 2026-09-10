"""T1 gates: SR O9 Layer-1 candidate construction ONLY (no certification)."""
import json
import os
import subprocess
import sys
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

import numpy as np
import pytest
from flint import arb, ctx

import sr_o9_candidates as T

CODE = Path(__file__).resolve().parents[1] / "code"
MODULE = CODE / "sr_o9_candidates.py"


def fresh_env(**over):
    env = {"HOME": os.environ.get("HOME", "/tmp"), "PATH": "/usr/bin:/bin",
           "LANG": "C.UTF-8", **{v: "1" for v in T.THREAD_VARS}}
    env.update(over)
    return env


@pytest.fixture(scope="module")
def cell150():
    return T.build_cell_candidates(150)


def _mant(x):
    m, e = x.mid().man_exp()
    m, e = int(m), int(e) + T.SCALE_BITS
    assert e >= 0 or m % (1 << -e) == 0
    return m << e if e >= 0 else m >> -e


# ------------------------------------------------------------ frozen inputs
def test_frozen_parameters_are_read_from_the_repository():
    cp = T.spec.CHECKPOINT
    assert T.FROZEN_BIDEGREE == (16, 16) == tuple(cp["complexity"]["hard_bidegree"]["SR"])
    assert T.FROZEN_BITS == 256 == cp["precision"]["SR_production_bits"]
    assert (T.FROZEN_D, T.FROZEN_Z) == (11, 20) == (cp["backend"]["D"], cp["backend"]["Z"])
    sys.path.insert(0, str(T.TASK1))
    import task1_f0
    assert (task1_f0.CAND_DEGREE, task1_f0.SCALE_BITS, task1_f0.COLLOC_QUAD,
            task1_f0.PROD_BITS) == (T.CAND_DEGREE, T.SCALE_BITS, T.COLLOC_QUAD, T.FROZEN_BITS)


def test_census_derived_from_frozen_dag_equals_frozen_o9_census():
    d = T.verify_census()
    assert d["distinct_candidates"] == 46 and d["certified_contracts"] == 102
    assert d["by_moment_shift"] == {"0": 43, "1": 35, "2": 20, "3": 4}
    assert sorted(T.BASIS_ORDER) == d["basis"] and len(set(T.BASIS_ORDER)) == 46
    frozen = T.frozen_o9_census()
    assert (frozen["distinct_candidates"], frozen["certified_contracts"]) == (46, 102)


def test_construction_order_is_a_topological_order_of_the_frozen_dag():
    nodes = T.sr_dag.build()["nodes"]
    pos = {n: i for i, n in enumerate(T.BASIS_ORDER)}
    for nid in T.BASIS_ORDER[1:]:
        for dep in nodes[nid]["dependencies"]:
            dep = T._alias(dep)
            if dep in pos:
                assert pos[dep] < pos[nid], (dep, nid)


# ------------------------------------------------------- 1. Task1R reference
def test_task1r_F0_bit_exact_against_the_frozen_task1_f0_function():
    sys.path.insert(0, str(T.TASK1))
    import sr_local as L
    import task1_f0
    from rebaseguard_certify.arb_backend import rational, workprec
    with workprec(256):
        _A, b, c = L.sr_constants()
        rows, _ = task1_f0.build_candidate(float(b), float(c), float(rational(1, 4)))
    mine, _, _ = T.reference_F0()
    assert mine == [[_mant(x) for x in r] for r in rows]


def test_task1r_F0_matches_the_authorized_runtime_frozen_identity():
    import t1_reference as R
    r = R.reproduce()
    assert r["dense_control_replica_faithful"], r
    assert r["t1_F0_matches_authorized_runtime_identity"], r


# ------------------------------------------------------ 2. cell-150 basis
def test_cell150_full_basis_is_complete_unique_and_finite(cell150):
    s = cell150["scientific"]
    cands = s["candidates"]
    assert [c["node"] for c in cands] == T.BASIS_ORDER == s["node_order"]
    assert len(cands) == 46
    assert len({c["identity_hash"] for c in cands}) == 46
    assert len({c["content_hash"] for c in cands}) == 46
    for c in cands:
        m = c["mantissas"]
        assert len(m) == 17 and all(len(r) == 17 for r in m)
        assert all(isinstance(v, int) and not isinstance(v, bool) for r in m for v in r)
        for v in c["construction_diagnostics"].values():
            assert not isinstance(v, float) or np.isfinite(v)
    assert Counter(c["node_class"] for c in cands) == Counter(
        {"FORWARD_OPERATOR": 24, "CLOSED_FORM_INTERPOLANT": 6, "RESOLVENT_SOLVE": 5,
         "DERIVATIVE_SOLVE": 5, "CURVATURE_SOLVE": 5, "EXACT": 1})
    assert s["status"] == "T1_CANDIDATE_CONSTRUCTION_ONLY"


def test_no_deferred_stub_remains_on_the_candidate_path():
    src = MODULE.read_text()
    assert "import sr_patch" not in src and "CandidateSolveDeferred" not in src
    for nid in T.BASIS_ORDER:
        T.node_class(nid)
    sys.path.insert(0, str(T.QUAL))
    import sr_patch                                   # frozen predecessor is unchanged
    assert issubclass(sr_patch.CandidateSolveDeferred, NotImplementedError)


def test_exact_constant_candidate_is_exact(cell150):
    one = cell150["scientific"]["candidates"][0]
    assert one["node"] == "const:1" and one["mantissas"] == T.EXACT_ONE


# ------------------------------------------------------ 3. determinism
def test_two_fresh_processes_are_byte_identical(tmp_path, cell150):
    outs = []
    for k in range(2):
        out = tmp_path / f"run{k}.json"
        subprocess.run([sys.executable, str(MODULE), "build", "--cell", "150", "--out", str(out)],
                       env=fresh_env(), check=True, capture_output=True, text=True)
        outs.append(out.read_bytes())
    assert outs[0] == outs[1]
    assert outs[0] == T.canonical(cell150["scientific"])
    d = json.loads(outs[0])
    assert d["node_order"] == T.BASIS_ORDER


# ------------------------------------------------------ 4. cell 315 geometry
def test_cell315_exact_terminal_geometry():
    c315, c314 = T.frozen_cell(315), T.frozen_cell(314)
    assert c315["left"] == c314["right"]
    tol = arb(2) ** -240
    with T.scientific_precision():
        g = T.cell_geometry(c315)
        _A, _b, c = T.sr_constants()
        assert (g["right"] - c).abs_upper() < tol                      # right == exact c_SR
        assert (g["e0"] - (g["left"] + g["right"]) / arb(2)).abs_upper() < tol
        assert (g["rho"] - (g["right"] - g["left"]) / arb(2)).abs_upper() < tol
        legacy = T.legacy_rational_reading(c315)
        assert legacy["right"] == 0                                    # the broken reading
        assert g["right"] > arb(6) and g["rho"] > 0 and g["rho"] < arb(1) / arb(40)
        e_f = T.nearest_double(g["e0"])
    assert e_f == 6.7328315821607365 and e_f != float(legacy["e0"])


def test_cell315_candidates_consume_the_exact_affine_e0():
    r = T.build_cell_candidates(315)["scientific"]
    with T.scientific_precision():
        e_f = T.nearest_double(T.cell_geometry(T.frozen_cell(315))["e0"])
    assert float.fromhex(r["construction"]["float_inputs_hex"]["e0"]) == e_f
    assert r["cell"]["right"] == ["0/1", "1/1"] and len(r["candidates"]) == 46


def test_sr_constants_equal_the_frozen_sr_local_constants():
    sys.path.insert(0, str(T.TASK1))
    import sr_local as L
    with T.scientific_precision():
        mine, frozen = T.sr_constants(), L.sr_constants()
        for a, b in zip(mine, frozen):
            assert a.mid() == b.mid() and a.rad() == b.rad()


# ------------------------------------------------------ 5. system reuse
def test_assembled_system_reuse_equals_fresh_assembly_bit_for_bit():
    with T.scientific_precision():
        b, c, e = T.float_inputs(T.cell_geometry(T.frozen_cell(150)))
    s1, s2 = T.NodalSystem(b, c, e), T.NodalSystem(b, c, e)
    assert all(np.array_equal(x, y) for x, y in zip(s1.M, s2.M))
    assert np.array_equal(s1.A, s2.A)
    assert np.array_equal(s1.A, np.eye(289) - s1.M[0])              # the same (I - K) system
    v1, _ = T.construct_nodal(s1)
    v2, _ = T.construct_nodal(s2)
    assert set(v1) == set(v2) and all(np.array_equal(v1[k], v2[k]) for k in v1)


# ------------------------------------------------------ 6. negatives
@pytest.mark.parametrize("bd", [(12, 12), (16, 12), (20, 20)])
def test_refuses_wrong_bidegree(bd):
    with pytest.raises(T.BidegreeRefused):
        T.build_cell_candidates(150, bidegree=bd)


@pytest.mark.parametrize("bits", [53, 128, 512])
def test_refuses_wrong_precision(bits):
    with pytest.raises(T.PrecisionRefused):
        T.build_cell_candidates(150, bits=bits)
    with pytest.raises(T.PrecisionRefused):
        with T.scientific_precision(bits):
            pass


def test_scientific_helpers_refuse_the_ambient_precision():
    old = ctx.prec
    try:
        ctx.prec = 53
        with pytest.raises(T.PrecisionRefused):
            T.sr_constants()
        with pytest.raises(T.PrecisionRefused):
            T.to_arb_matrix(T.EXACT_ONE)
        with pytest.raises(T.PrecisionRefused):
            T.cell_geometry(T.frozen_cell(150))
    finally:
        ctx.prec = old


def test_result_is_independent_of_the_ambient_precision():
    old = ctx.prec
    try:
        ctx.prec = 53
        a = T.build_cell_candidates(275)["scientific"]
        assert ctx.prec == 53
        ctx.prec = 1024
        b = T.build_cell_candidates(275)["scientific"]
        assert ctx.prec == 1024
    finally:
        ctx.prec = old
    assert T.canonical(a) == T.canonical(b)


def test_refuses_malformed_cells():
    c = T.frozen_cell(150)
    c["e0"] = ["2536818/20000000", "0/1"]
    with pytest.raises(T.CellRefused):
        T.build_cell_candidates(150, cell=c)
    c = T.frozen_cell(150)
    c["rho"] = ["581/800000"]
    with pytest.raises(T.CellRefused):
        T.build_cell_candidates(150, cell=c)
    for bad in (316, -1, "150", True):
        with pytest.raises(T.CellRefused):
            T.frozen_cell(bad)
    cusum = next(x for x in T.spec.CELLS if x["detector"] == "CUSUM")
    with pytest.raises(T.CellRefused):
        T.validate_cell(dict(cusum))


def test_refuses_decimalised_or_moved_cell315_right_endpoint():
    dec = T.frozen_cell(315)
    dec["right"] = [str(F(67555314643214731928, 10 ** 19)), "0/1"]
    dec["e0"] = [str((F(67101317, 10 ** 7) + F(67555314643214731928, 10 ** 19)) / 2), "0/1"]
    dec["rho"] = [str((F(67555314643214731928, 10 ** 19) - F(67101317, 10 ** 7)) / 2), "0/1"]
    with pytest.raises(T.CellRefused):
        T.build_cell_candidates(315, cell=dec)
    moved = T.frozen_cell(315)
    moved["right"] = ["0/1", "2/1"]
    with pytest.raises(T.CellRefused):
        T.build_cell_candidates(315, cell=moved)


@pytest.mark.parametrize("nid", ["S:3:k0", "S:4:k2", "W:3,0:k0", "W:0,3:k0", "W:1,2:k1",
                                 "M_R2:1", "op:K:k0", "R:1:k0", "H:0:k0", "F:5:k0",
                                 "h:5:k0", "h:1:k3", ""])
def test_refuses_unsupported_candidate_kinds(nid):
    with pytest.raises(T.UnsupportedCandidate):
        T.build_cell_candidates(150, nodes=[nid])


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_refuses_non_finite_nodal_values(bad):
    v = np.zeros(289)
    v[7] = bad
    with pytest.raises(T.NonFiniteCandidate):
        T.quantize(v)
    with pytest.raises(T.NonFiniteCandidate):
        T.quantize(np.zeros(288))


def test_refuses_an_unpinned_thread_environment(tmp_path):
    p = subprocess.run([sys.executable, str(MODULE), "build", "--cell", "150",
                        "--out", str(tmp_path / "x.json")],
                       env=fresh_env(OPENBLAS_NUM_THREADS="4"), capture_output=True, text=True)
    assert p.returncode != 0 and "ThreadContractRefused" in p.stderr
    assert not (tmp_path / "x.json").exists()


def test_the_cusum_degree12_helper_is_not_applied_to_sr_candidates():
    sys.path.insert(0, str(T.QUAL))
    import sr_patch
    with pytest.raises(sr_patch.KernelArgumentDegreeExceeded):
        sr_patch.assert_kernel_argument_degree(16)
    assert "assert_kernel_argument_degree(" not in MODULE.read_text()
    assert T.FROZEN_BIDEGREE == (16, 16)
