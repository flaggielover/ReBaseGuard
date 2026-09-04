"""Pre-T2 structural preconditions for P5Y Gate-2E, including the DECISIVE
negative control that the precision grid is not entered when the acceptance
precondition fails (the Gate-2D defect)."""
from __future__ import annotations
import ast, io, json, subprocess, sys, tokenize
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
for p in (str(HERE), str(ROOT / "rebaseguard-proof" / "src"),
          str(ROOT / "level4/closure_proofs/p5x_global_nonlinear_dynamics/compute_optimization_r3_sr_symbolic"),
          str(ROOT / "level4/closure_proofs/p5y_gate2d_sr_realcandidate")):
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


import sr_metric as S            # noqa: E402
SRC = (HERE / "sr_metric.py").read_text()
CODE = _code_only(SRC)
PRE = (HERE / "GATE2E_PREREGISTRATION.md").read_text()


def test_gate2d_remains_fail():
    d = json.loads((ROOT / "level4/closure_proofs/p5y_gate2d_sr_realcandidate/results/"
                    "gate2d_adjudication.json").read_text())
    assert d["governing_decision"] == "SR_REALCANDIDATE_FAIL_REPRESENTATION"
    assert "SR_REALCANDIDATE_FAIL_REPRESENTATION" in SRC


def test_scientific_target_is_R_max_lt_2():
    assert S.BOUNDARY == 2.0 and S.SLACK_R == 2.0
    assert "R_MAX_LT_2" in SRC
    assert "sup_e |R_{D,m}(e)| < 2" in PRE or "R_max(D,m) = sup_" in PRE


def test_threshold_does_not_consume_any_gate2d_residual():
    """ANTI-CIRCULARITY: no Gate-2D output may appear in the metric constants."""
    tree = ast.parse(SRC)
    frozen = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Constant):
            for t in n.targets:
                if getattr(t, "id", "").isupper():
                    frozen[t.id] = n.value.value
    for name in ("BOUNDARY", "SLACK_R", "ALPHA", "C_SR_QUARTER", "C_SR_ZERO",
                 "N_PANELS", "E_ABS_RAW"):
        assert name in frozen, f"{name} must be a frozen literal"
    # the Gate-2D candidate residual is 1.9301e-07; it must not be a metric input
    for v in frozen.values():
        if isinstance(v, float):
            assert abs(v - 1.9301e-07) > 1e-12, "Gate-2D eps_cand leaked into the metric"
    fn = SRC.split("# ---------------- FROZEN METRIC CONSTANTS")[1].split("def ")[0]
    assert "eps_cand" not in fn and "sr_realcandidate.json" not in fn


def test_slack_and_w_target_frozen_and_derived():
    assert S.W_TARGET == S.ALPHA * S.SLACK_R == 0.2
    assert "FROZEN_THRESHOLD = 0.2" in PRE, "w_target must cite the P5X Checkpoint-A rule"


def test_error_budget_ledger_frozen_and_sums_within_target():
    assert abs(sum(S.LEDGER.values()) + S.RESERVE_FRACTION - 1.0) < 1e-12
    assert sum(S.LEDGER.values()) <= 1.0
    assert abs(S.RESERVE_FRACTION - 0.05) < 1e-12
    assert abs(sum(S.B_ABS.values()) - 0.19) < 1e-12
    for k in ("B_cover", "B_candidate", "B_kernel", "B_other", "B_rounding", "B_interval"):
        assert k in S.B_ABS
    assert "B_resolvent" not in S.LEDGER, "C is multiplicative, not an additive budget"


def test_no_post_hoc_budget_redistribution_exists():
    assert "redistribut" not in CODE.lower()
    assert "borrow" not in CODE.lower()


def test_candidate_budget_derived_from_the_ledger():
    expect = 2 * S.B_ABS["B_candidate"] / (S.C_SR_QUARTER * S.E_ABS_RAW)
    assert abs(S.DELTA_CANDIDATE_MAX - expect) < 1e-15
    expect_w = S.LOCAL_GATE_BUDGET / (0.5 * S.C_SR_QUARTER * S.N_PANELS)
    assert abs(S.W_PANEL_MAX - expect_w) < 1e-15


def test_amplification_bound_direction_is_audited():
    a = S.direction_audit()
    assert a["type"] == "UPPER"
    assert a["cross_check_le_certified"] is True
    assert a["monotone_decreasing_in_e"] is True
    assert a["PASS"] is True


def test_primary_metric_does_not_divide_by_acc():
    fn = SRC.split("def run_cell")[1].split("\ndef ")[0]
    prim = fn.split("w_panel = ")[1].split("\n")[0]
    assert "/" not in prim, "the absolute metric must not divide by anything"
    assert "w_panel = rem_width + rad + cand_term" in fn
    assert "P2_old_DIAGNOSTIC_ONLY" in fn


def test_scale_aware_fallback_cannot_execute_when_absolute_is_valid():
    assert S.direction_audit()["PASS"] is True
    assert "scale_aware_fallback_invoked\": False" in SRC or \
           '"scale_aware_fallback_invoked": False' in SRC
    assert "max(1,|acc|)" in PRE.replace(", ", ",") and "rejected on dimensional grounds" in PRE
    # no fallback code path exists in the module at all
    assert "atol" not in CODE and "rtol" not in CODE


def test_objects_are_gate2d_objects_not_refitted():
    assert "import sr_realcandidate as G2DM" in SRC
    assert "G2DM.build_hhat1" in SRC and "G2DM.build_hhat2" in SRC
    assert "refitted\": False" in SRC or '"refitted": False' in SRC
    assert "unit_candidate()" in SRC


def test_patch_grid_degree_and_precisions_frozen():
    assert S.PATCH == (17, 11) and S.GRID == 64 and S.DEGREE == 8
    assert S.CAND_DEGREE == 16 and S.PRECISIONS == (256, 384, 512)
    tree = ast.parse(SRC)
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and getattr(n.func, "id", "") == "run_cell"]
    for c in calls:
        assert not isinstance(c.args[0], ast.Constant), "precision must come from the grid"


def test_precondition_branches_before_the_grid_in_source_order():
    body = SRC.split("def run_pilot")[1].split("\ndef ")[0]
    i_dir = body.index("direction_audit")
    i_pre = body.index("acceptance_precondition")
    i_gua = body.index("representation_guard")
    i_grid = body.index("precision_grid")
    assert i_dir < i_pre < i_gua < i_grid, "enforced order violated"
    assert body.index('return out', i_pre) < i_grid, "precondition must return early"


def test_DECISIVE_invalid_precondition_skips_the_grid():
    """Supply an impossible candidate budget: the grid must NOT be entered."""
    r = S.run_pilot(candidate_budget=1e-30)
    assert r["acceptance_precondition"]["PASS"] is False
    assert r["decision"] == "SR_METRIC_FAIL_CANDIDATE"
    assert "precision_grid" not in r["stages_run"], "the grid was entered despite a failed precondition"
    assert "cells" not in r


def test_DECISIVE_guard_failure_also_skips_the_grid():
    src = SRC.split("def run_pilot")[1].split("\ndef ")[0]
    assert src.index('"SR_METRIC_FAIL_ARCHITECTURE"') < src.index('"precision_grid"')


def test_p1_repair_unchanged():
    assert abs(float(S.EPS_P1) - 1e-3) < 1e-15
    assert S.GATE2A_NZ == 28
    assert "(arb(1) - EPS_P1) * P1_TARGET" in SRC


def test_complexity_guard_frozen():
    assert S.MAX_COMPLEXITY_SCORE == 100_000


def test_old_p2_is_diagnostic_only():
    body = SRC.split("def run_pilot")[1].split("\ndef ")[0]
    sel = body.split("sel = next(")[1].split(")\n")[0]
    assert "P2" not in sel, "the old relative P2 must not decide the selection"
    assert "ABS_PASS" in sel


def test_no_out_of_scope_work():
    for banned in ("s_min", "cover_walk", "rho_2", "K_z2", "lean", "m_gt1"):
        assert banned not in CODE.lower(), banned


def test_protected_tree_untouched():
    diff = subprocess.run(["git", "diff", "--name-only", "c123b9b", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.split("\n")
    bad = [x for x in diff if x.strip() and not x.startswith("level4/closure_proofs/p5y_")]
    assert not bad, f"protected paths modified: {bad}"
    st = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                        capture_output=True, text=True).stdout.split("\n")
    dirty = [s for s in st if s.strip() and "p5y_gate2e_sr_metric/" not in s]
    assert not dirty, f"working tree dirty outside Gate-2E: {dirty}"
