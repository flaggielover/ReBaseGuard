"""Pre-T2 structural preconditions for P5Y Gate-2D."""
from __future__ import annotations
import ast, io, json, subprocess, sys, tokenize
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
for p in (str(HERE), str(ROOT / "rebaseguard-proof" / "src"),
          str(ROOT / "level4/closure_proofs/p5x_global_nonlinear_dynamics/compute_optimization_r3_sr_symbolic")):
    if p not in sys.path:
        sys.path.insert(0, p)


def _code_only(src):
    out, toks = [], list(tokenize.generate_tokens(io.StringIO(src).readline))
    for i, t in enumerate(toks):
        if t.type == tokenize.COMMENT:
            continue
        if t.type == tokenize.STRING:
            j = i - 1
            while j >= 0 and toks[j].type in (tokenize.NL, tokenize.NEWLINE,
                                              tokenize.INDENT, tokenize.DEDENT):
                j -= 1
            if j < 0 or toks[j].type == tokenize.INDENT or toks[j].string in (":", ""):
                continue
        out.append(t.string)
    return " ".join(out)


import sr_realcandidate as S   # noqa: E402
SRC = (HERE / "sr_realcandidate.py").read_text()
CODE = _code_only(SRC)


def test_patch_and_grid_frozen():
    assert S.PATCH == (17, 11) and S.GRID == 64
    assert (S.E_NUM, S.E_DEN) == (1, 4)
    g2a = json.loads((ROOT / "level4/closure_proofs/p5y_gate2a_sr_precision/results/"
                      "sr_precision.json").read_text())
    assert g2a["frozen"]["patch"] == list(S.PATCH)


def test_only_one_patch_is_ever_used():
    tree = ast.parse(SRC)
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and getattr(n.func, "attr", "") == "patch_geometry"]
    assert len(calls) == 1
    assert any(isinstance(a, ast.Starred) and getattr(a.value, "id", "") == "PATCH"
               for a in calls[0].args)


def test_degree_is_8_not_10():
    assert S.DEGREE == 8
    for n in ast.walk(ast.parse(SRC)):
        if isinstance(n, ast.Assign) and any(getattr(t, "id", "") == "DEGREE" for t in n.targets):
            assert n.value.value == 8
    assert "degree 10" not in CODE.lower()


def test_candidate_bidegree_is_16_and_not_raisable():
    assert S.CAND_DEGREE == 16
    for n in ast.walk(ast.parse(SRC)):
        if isinstance(n, ast.Assign) and any(getattr(t, "id", "") == "CAND_DEGREE"
                                             for t in n.targets):
            assert n.value.value == 16
    for bad in ("CAND_DEGREE = 18", "CAND_DEGREE = 20", "CAND_DEGREE = 24"):
        assert bad not in SRC


def test_candidate_is_genuine_not_unit_candidate():
    """unit_candidate may appear ONLY as the declared control."""
    tree = ast.parse(SRC)
    uses = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
            and getattr(n.func, "id", "") == "unit_candidate"]
    assert len(uses) == 1, "unit_candidate must be used exactly once, as the control"
    assert '"unit_candidate_control"' in SRC
    assert "build_hhat1" in CODE and "gaussian_cdf" in CODE
    assert "h_1^SR" in SRC, "the represented function must be documented"


def test_exact_dyadic_rounding_rule():
    assert S.SCALE_BITS == 50
    assert "arb(2) ** SCALE_BITS" in SRC
    assert "int(round(float(" in SRC, "coefficients must be rounded to integers over 2^-50"


def test_residual_is_whole_domain_with_three_named_terms():
    fn = SRC.split("def cheb_fit_1d")[1].split("\ndef ")[0]
    assert "tail" in fn and "interp_err" in fn and "round_err" in fn
    assert "eps = tail + interp_err + round_err" in fn
    assert "CRAMER" in fn
    assert "full state square" in SRC, "fit domain must be the whole square, not pointwise"


def test_precision_grid_exactly_256_384_512():
    assert S.PRECISIONS == (256, 384, 512)
    tree = ast.parse(SRC)
    # precision may enter a measured cell ONLY from the frozen grid: every
    # run_cell call must take its precision as a variable, never a literal.
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and getattr(n.func, "id", "") == "run_cell"]
    assert calls
    for c in calls:
        assert not isinstance(c.args[0], ast.Constant) or c.args[0].value == S.REPRO_BITS, \
            "run_cell precision must come from PRECISIONS (or the frozen repro point)"
    assert "for b in PRECISIONS" in SRC


def test_p2_target_is_1e_minus_8():
    assert S.P2_TARGET == 1e-8
    assert "P2 <= 1e-8" in (HERE / "GATE2D_PREREGISTRATION.md").read_text()


def test_p1_repaired_target_frozen():
    assert abs(float(S.EPS_P1) - 1e-3) < 1e-15
    assert "(arb(1) - EPS_P1) * P1_TARGET" in SRC
    assert S.GATE2A_NZ == 28


def test_complexity_guard_frozen_and_checked_before_cells():
    assert S.MAX_COMPLEXITY_SCORE == 100_000
    assert SRC.index('out["complexity_guard"]') < SRC.index("cells = [run_cell")
    assert 'if not out["complexity_guard"]["PASS"]' in SRC


def test_no_hidden_high_degree_object_enters_the_path():
    """Everything composed is bidegree <= 16; no exact 120/121-degree series."""
    assert "CHEB_N = 60" in SRC
    fn = SRC.split("def run_cell")[1].split("\ndef ")[0]
    assert "compose_candidate(cand, a_p, a_m" in fn
    assert "softplus_taylor(up_c, DEGREE)" in fn
    assert "_recentred_sites" not in CODE and "phi_taylor_coefficients" not in CODE


def test_digit_loss_uses_radii_not_midpoints():
    fn = SRC.split("def run_cell")[1].split("\ndef ")[0]
    assert "acc.rad()" in fn and "-math.log10(rad / ab)" in fn
    assert ".mid()" not in fn.split("digits_lost")[0].split("rad =")[1][:200]
    cf = SRC.split("def classify")[1].split("\ndef ")[0]
    assert "acc_radius" in cf and "mid" not in cf


def test_candidate_residual_accounted_separately_from_working_precision():
    assert '"eps_cand"' in SRC and '"acc_radius"' in SRC
    assert '"P2_floor"' in SRC
    assert "acceptance_precondition" in SRC


def test_selection_takes_lowest_passing_precision():
    blk = SRC.split("sel = next(")[1].split(")\n")[0]
    assert "for c in cells" in blk and "P2_pass" in blk
    assert S.PRECISIONS == tuple(sorted(S.PRECISIONS))


def test_reproducibility_frozen_at_384():
    assert S.REPRO_BITS == 384
    assert '"ball_identical"' in SRC and "acc_lower" in SRC


def test_timing_repeats_frozen():
    assert S.TIMING_REPEATS == 5


def test_nonseparable_probe_is_declared_non_decisive():
    assert '"decisive": False' in SRC
    assert '"certifies_nothing": True' in SRC
    assert '"no_whole_domain_residual_certificate": True' in SRC
    blk = SRC.split("sel = next(")[1]
    assert "probe" not in blk.split("out[\"GATE2D_DECISION\"]")[0], \
        "the probe must not enter the decision"


def test_no_out_of_scope_work():
    for banned in ("rho_2", "K_z2", "s_min", "cover_walk", "second_moment",
                   "m_gt1", "lean"):
        assert banned not in CODE.lower().replace("second_moment_object_created", ""), banned


def test_protected_tree_and_prior_gates_untouched():
    diff = subprocess.run(["git", "diff", "--name-only", "c123b9b", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.split("\n")
    bad = [x for x in diff if x.strip() and not x.startswith("level4/closure_proofs/p5y_")]
    assert not bad, f"protected paths modified: {bad}"
    st = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                        capture_output=True, text=True).stdout.split("\n")
    dirty = [s for s in st if s.strip() and "p5y_gate2d_sr_realcandidate/" not in s]
    assert not dirty, f"working tree dirty outside Gate-2D: {dirty}"
