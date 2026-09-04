"""Pre-T2 structural preconditions for P5Y Gate-2C.  No results needed."""
from __future__ import annotations
import ast, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
for p in (str(HERE), str(ROOT / "rebaseguard-proof" / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)
import m2_assembly as MA          # noqa: E402
import m2_certifier as MC         # noqa: E402


def _code_only(src: str) -> str:
    """Executable source with comments and docstrings removed, so that a negative
    declaration or a docstring can never satisfy or violate a content assertion."""
    import io, tokenize
    out, prev_was_string_stmt = [], False
    toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    for i, tok in enumerate(toks):
        if tok.type == tokenize.COMMENT:
            continue
        if tok.type == tokenize.STRING:
            j = i - 1
            while j >= 0 and toks[j].type in (tokenize.NL, tokenize.NEWLINE,
                                              tokenize.INDENT, tokenize.DEDENT):
                j -= 1
            if j < 0 or toks[j].type == tokenize.INDENT or toks[j].string in (":", ""):
                continue        # a docstring
        out.append(tok.string)
    return " ".join(out)


SRC_A = (HERE / "m2_assembly.py").read_text()
SRC_C = (HERE / "m2_certifier.py").read_text()


def test_detector_is_exactly_cusum():
    assert MA.K_F == 0.5 and MA.H_F == 5.0 and MA.C_F == 5.5
    assert "cusum" in SRC_A.lower()
    for banned in ("softplus", "logaddexp", "sr_local"):
        assert banned not in _code_only(SRC_C) and banned not in _code_only(SRC_A), \
            f"SR machinery leaked: {banned}"


def test_m_set_is_exactly_1_and_2():
    assert MA.M_SET == (1, 2)
    tree = ast.parse(SRC_A)
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and any(getattr(t, "id", "") == "M_SET" for t in n.targets):
            assert [e.value for e in n.value.elts] == [1, 2]


def test_exactly_one_frozen_drift():
    assert (MA.E_NUM, MA.E_DEN) == (1, 4)
    calls = [n for n in ast.walk(ast.parse(SRC_A))
             if isinstance(n, ast.Call) and getattr(n.func, "attr", "") in
             ("certify_raw_at_exact_drift", "certify_F1")]
    for c in calls:
        assert all(isinstance(a, ast.Name) and a.id in ("E_NUM", "E_DEN") for a in c.args[:2]), \
            "every certification must use the single frozen drift"


def test_raw_variable_convention_is_used():
    assert "reward_rho1_raw" in SRC_C
    assert "certify_raw_at_exact_drift" in SRC_A
    assert "d_e h_1 = -S_0^raw" in SRC_C
    # no external '+e' may appear in the m=2 assembly
    blk = SRC_A.split("R2e = ")[1].split("\n")[0]
    assert "+ e" not in blk and "arb(2)" in blk


def test_m2_assembly_matches_the_frozen_symbolic_structure():
    """R_2 = (1/2)[F_0 + F_1 + S_0^raw] -- exactly, no extra term."""
    blk = SRC_A.split("R2e = ")[1].split("\n")[0]
    assert blk.strip() == "(F0e + F1e + S0) / arb(2)"
    assert "R1e = F0e" in SRC_A


def test_shared_functions_are_not_duplicated():
    """F_0 must be solved once; the m=2 path must not re-derive it."""
    assert SRC_C.count("solve_candidates_raw") == 0, "m=2 must not re-solve F_0"
    assert "solve_F1" in SRC_C
    tree = ast.parse(SRC_A)
    n_m1 = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Call)
               and getattr(n.func, "attr", "") == "certify_raw_at_exact_drift")
    n_m2 = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Call)
               and getattr(n.func, "attr", "") == "certify_F1")
    assert n_m1 == 1 and n_m2 == 1, "each object certified in exactly one timed loop"


def test_independent_estimate_is_implementation_independent():
    """The MC must simulate the detector and touch no assembly machinery."""
    fn = _code_only(SRC_A.split("def monte_carlo_R2")[1].split("\ndef ")[0])
    for banned in ("arb", "RA.", "RAW.", "M2.", "kernel", "candidate", "bi_eval",
                   "resolvent", "chebyshev"):
        assert banned not in fn, f"MC touched assembly machinery: {banned}"
    flat = fn.replace(" ", "")
    assert "np.maximum(0.0,sp[idx]+z-K_F)" in flat, "MC must run the frozen recursion"
    assert "np.maximum(0.0,sm[idx]-z-K_F)" in flat
    assert "rng.standard_normal" in flat
    assert "(sp_n>=H_F)|(sm_n>=H_F)" in flat, "inclusive post-update alarm test"


def test_tolerance_and_repeats_frozen():
    assert MA.ABS_TOL == 5e-3
    assert MA.CERTIFIED_REPEATS == 2 and MA.ASSEMBLY_REPEATS == 5
    assert MA.N_CYCLES == 1_000_000 and MA.SEED == 20260904
    pre = (HERE / "GATE2C_PREREGISTRATION.md").read_text()
    assert "N_CYCLES = 1_000_000" in pre and "SEED = 20260904" in pre
    assert "max( 4 SE , 5e-3 )" in pre


def test_cost_ratio_excludes_shared_solve_duplication():
    blk = SRC_A.split("ratio_incr = ")[1].split("\n")[0]
    assert blk.strip() == "T_incr / T_m1"
    assert "ratio_per_unit = ratio_incr / UNITS_ADDED_BY_M2" in SRC_A
    assert MA.UNITS_ADDED_BY_M2 == 2


def test_no_second_moment_object_is_created():
    for s in (_code_only(SRC_A), _code_only(SRC_C)):
        for banned in ("rho_2", "rho2", "K_z2", "pair_function", "Rbar2"):
            assert banned not in s, f"second-moment object referenced: {banned}"
    # z_weight may only ever be 0 or 1: weight 2 is the second-moment operator
    for s in (SRC_A, SRC_C):
        for n in ast.walk(ast.parse(s)):
            if isinstance(n, ast.keyword) and n.arg == "z_weight":
                assert n.value.value in (0, 1), "z_weight=2 is the second-moment kernel"
    # and the run must declare that no second-moment object was created
    assert '"second_moment_object_created": False' in SRC_A


def test_no_sr_and_no_cover_execution():
    for s in (_code_only(SRC_A), _code_only(SRC_C)):
        for banned in ("cover_walk", "patch_geometry", "sr_cover", "sr_precision",
                       "e_star", "full_cover"):
            assert banned not in s, f"out-of-scope execution: {banned}"


def test_no_other_m_values():
    for s in (_code_only(SRC_A), _code_only(SRC_C)):
        for banned in ("h_2", "h2_", "S_2raw", "s2_raw", "F_2", "m=3", "m=5"):
            assert banned not in s, f"another m referenced: {banned}"


def test_protected_tree_and_prior_gates_untouched():
    diff = subprocess.run(["git", "diff", "--name-only", "c123b9b", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.split("\n")
    bad = [x for x in diff if x.strip() and not x.startswith(
        ("level4/closure_proofs/p5y_micropilot_gate1/",
         "level4/closure_proofs/p5y_gate2a_sr_precision/",
         "level4/closure_proofs/p5y_gate2b_sr_cover/",
         "level4/closure_proofs/p5y_gate2c_m2_assembly/"))]
    assert not bad, f"protected paths modified: {bad}"
    st = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                        capture_output=True, text=True).stdout.split("\n")
    dirty = [s for s in st if s.strip() and "p5y_gate2c_m2_assembly/" not in s]
    assert not dirty, f"working tree dirty outside Gate-2C: {dirty}"
