"""Pre-T2 structural preconditions for P5Y Gate-2C-bis."""
from __future__ import annotations
import ast, io, json, subprocess, sys, tokenize
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
for p in (str(HERE), str(ROOT / "rebaseguard-proof" / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)


def _code_only(src: str) -> str:
    out = []
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
                continue
        out.append(tok.string)
    return " ".join(out)


import m2b_assembly as MA          # noqa: E402
import m2b_certifier as MC         # noqa: E402
SRC_A = (HERE / "m2b_assembly.py").read_text()
SRC_C = (HERE / "m2b_certifier.py").read_text()
CODE_A, CODE_C = _code_only(SRC_A), _code_only(SRC_C)


def test_detector_drift_and_m_set():
    assert MA.K_F == 0.5 and MA.H_F == 5.0 and MA.C_F == 5.5
    assert (MA.E_NUM, MA.E_DEN) == (1, 4)
    assert MA.M_SET == (1, 2)


def test_candidate_degree_is_exactly_12_and_not_adjustable():
    assert MC.KEEP == 12 and MC.SCALE_BITS == 50 and MC.CHEB_N == 120
    for n in ast.walk(ast.parse(SRC_C)):
        if isinstance(n, ast.Assign) and any(getattr(t, "id", "") == "KEEP" for t in n.targets):
            assert n.value.value == 12
    for banned in ("14", "16", "18", "20"):
        assert f"KEEP = {banned}" not in SRC_C


def test_every_kernel_call_goes_through_the_guard():
    """No raw _kernel_polynomials call may bypass the bidegree guard."""
    tree = ast.parse(SRC_C)
    direct = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
              and getattr(n.func, "id", "") == "_kernel_polynomials"]
    guard = next(n for n in ast.walk(tree)
                 if isinstance(n, ast.FunctionDef) and n.name == "guarded_kernel")
    inside = [n for n in ast.walk(guard) if isinstance(n, ast.Call)
              and getattr(n.func, "id", "") == "_kernel_polynomials"]
    assert len(direct) == len(inside) == 1, \
        "the only _kernel_polynomials call must be the one inside guarded_kernel"
    assert any(isinstance(n, ast.Raise) for n in ast.walk(guard)), \
        "the guard must raise on an over-degree argument"


def test_bidegree_guard_threshold_is_12():
    fn = SRC_C.split("def guarded_kernel")[1].split("\ndef ")[0]
    assert "if dp > KEEP or dm > KEEP" in fn


def test_complexity_budget_frozen():
    assert MA.MAX_COMPLEXITY_SCORE == 400_000
    assert "(deg_p + 1) * (deg_m + 1) * (z_degree_after + 1)" in \
        (HERE / "GATE2CBIS_PREREGISTRATION.md").read_text()


def test_no_degree121_object_enters_the_kernel_path():
    """The exact high-degree h_1 must not be constructed for kernel use at all."""
    assert "h1_bipoly" not in CODE_C, "the Gate-2C degree-121 builder must not be used"
    assert "_recentred_sites" not in CODE_C, "no degree-120 recentred series in the kernel path"
    assert "reward_rho1_raw" not in CODE_C
    assert "cheb_candidate_1d" in CODE_C


def test_raw_m2_assembly_is_unchanged_from_gate2c():
    blk = SRC_A.split("R2e = ")[1].split("\n")[0]
    assert blk.strip() == "(F0e + F1e + S0_exact) / arb(2)"
    assert "R1e = F0e" in SRC_A
    g2c = (ROOT / "level4/closure_proofs/p5y_gate2c_m2_assembly/m2_assembly.py").read_text()
    old = g2c.split("R2e = ")[1].split("\n")[0].strip()
    assert old == "(F0e + F1e + S0) / arb(2)", "Gate-2C's assembly must be as recorded"


def test_candidate_residual_is_propagated_into_delta():
    assert "delta = poly_f + arb(11) * sup_f * eps_z + cand_allow" in SRC_C
    assert "cand_allow = e_abs * eps_h" in SRC_C
    assert "cand_allow_d = arb(2) * eps_h + e_abs * eps_dh" in SRC_C


def test_candidate_error_has_three_named_rigorous_terms():
    fn = SRC_C.split("def cheb_candidate_1d")[1].split("\ndef ")[0]
    assert "tail" in fn and "interp_err" in fn and "round_err" in fn
    assert "eps = tail + interp_err + round_err" in fn
    assert "CRAMER" in fn, "the interpolation-error term must use a rigorous derivative bound"


def test_shared_m1_objects_reused_not_resolved_again():
    assert "solve_candidates_raw" not in CODE_C, "m=2 must not re-solve F_0"
    tree = ast.parse(SRC_A)
    n1 = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Call)
             and getattr(n.func, "attr", "") == "certify_raw_at_exact_drift")
    n2 = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Call)
             and getattr(n.func, "attr", "") == "certify_F1")
    assert n1 == 1 and n2 == 1


def test_correspondence_is_implementation_independent():
    fn = _code_only(SRC_A.split("def monte_carlo_R2")[1].split("\ndef ")[0])
    for banned in ("arb", "RA.", "RAW.", "M2B.", "kernel", "candidate", "bi_eval",
                   "resolvent", "chebyshev"):
        assert banned not in fn, f"MC touched assembly machinery: {banned}"
    flat = fn.replace(" ", "")
    assert "np.maximum(0.0,sp[idx]+z-K_F)" in flat
    assert "(sp_n>=H_F)|(sm_n>=H_F)" in flat


def test_tolerance_seed_and_repeats_frozen():
    assert MA.ABS_TOL == 5e-3 and MA.N_CYCLES == 1_000_000 and MA.SEED == 20260904
    assert MA.CERTIFIED_REPEATS == 2 and MA.ASSEMBLY_REPEATS == 5
    assert MA.MAX_CANDIDATE_RESIDUAL_SHARE == 0.50


def test_cap_is_1260_and_watchdog_documented():
    pre = (HERE / "GATE2CBIS_PREREGISTRATION.md").read_text()
    assert "1260 CPU-seconds" in pre and "watchdog" in pre
    assert "cap_cpu_seconds\": 1260" in SRC_A or '"cap_cpu_seconds": 1260' in SRC_A


def test_no_second_moment_no_sr_no_cover():
    for s in (CODE_A, CODE_C):
        for banned in ("rho_2", "rho2", "K_z2", "pair_function", "Rbar2",
                       "softplus", "logaddexp", "sr_local", "cover_walk",
                       "patch_geometry", "e_star"):
            assert banned not in s, f"out-of-scope reference: {banned}"
    for s in (SRC_A, SRC_C):
        for n in ast.walk(ast.parse(s)):
            if isinstance(n, ast.keyword) and n.arg == "z_weight":
                if isinstance(n.value, ast.Constant):
                    assert n.value.value in (0, 1), "z_weight=2 is the second-moment kernel"


def test_gate2c_history_preserved():
    p = ROOT / "level4/closure_proofs/p5y_gate2c_m2_assembly/results/m2_assembly_abort.json"
    assert p.exists(), "the failed Gate-2C run must not be deleted"
    assert json.loads(p.read_text())["GATE2C_DECISION"] == "M2_ASSEMBLY_INCOMPLETE_EXTERNAL"


def test_protected_tree_untouched():
    diff = subprocess.run(["git", "diff", "--name-only", "c123b9b", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.split("\n")
    bad = [x for x in diff if x.strip() and not x.startswith(
        "level4/closure_proofs/p5y_")]
    assert not bad, f"protected paths modified: {bad}"
    st = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                        capture_output=True, text=True).stdout.split("\n")
    dirty = [s for s in st if s.strip() and "p5y_gate2cbis_m2_assembly_b/" not in s]
    assert not dirty, f"working tree dirty outside Gate-2C-bis: {dirty}"
