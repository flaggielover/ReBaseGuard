"""Pre-T2 structural preconditions for P5Y Gate-2F, including the negative
control that would have caught Gate-2E."""
from __future__ import annotations
import ast, io, json, subprocess, sys, tokenize
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
for p in (str(HERE), str(ROOT / "rebaseguard-proof" / "src"),
          str(ROOT / "level4/closure_proofs/p5x_global_nonlinear_dynamics/compute_optimization_r3_sr_symbolic"),
          str(ROOT / "level4/closure_proofs/p5y_gate2d_sr_realcandidate"),
          str(ROOT / "level4/closure_proofs/p5y_gate2e_sr_metric")):
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


import sr_metric_b as F      # noqa: E402
import sr_metric as S2E      # noqa: E402
from flint import arb        # noqa: E402
SRC = (HERE / "sr_metric_b.py").read_text()
CODE = _code_only(SRC)


def test_gate2d_and_gate2e_remain_fail():
    d = json.loads((ROOT / "level4/closure_proofs/p5y_gate2d_sr_realcandidate/results/"
                    "gate2d_adjudication.json").read_text())
    e = json.loads((ROOT / "level4/closure_proofs/p5y_gate2e_sr_metric/results/"
                    "sr_metric.json").read_text())
    assert d["governing_decision"] == "SR_REALCANDIDATE_FAIL_REPRESENTATION"
    assert e["GATE2E_DECISION"] == "SR_METRIC_FAIL_CANDIDATE"
    assert F.__dict__  # module importable


def test_metric_constants_are_gate2e_objects_not_transcribed():
    """Inheritance is by reference: no metric constant is re-declared here."""
    tree = ast.parse(SRC)
    declared = {t.id for n in ast.walk(tree) if isinstance(n, ast.Assign)
                for t in n.targets if getattr(t, "id", "").isupper()}
    forbidden = {"BOUNDARY", "SLACK_R", "ALPHA", "W_TARGET", "LEDGER",
                 "W_PANEL_MAX", "DELTA_CANDIDATE_MAX", "C_SR_QUARTER",
                 "N_PANELS", "E_ABS_RAW", "PRECISIONS", "PATCH", "GRID"}
    assert not (declared & forbidden), f"re-declared instead of inherited: {declared & forbidden}"
    assert declared >= {"P1_RULE_TARGET", "P1_CHECK_THRESHOLD", "MIN_HEADROOM_REL"}


def test_metric_type_is_still_absolute():
    a = F.inheritance_audit()
    assert a["checks"]["metric_type_absolute"] is True
    assert a["checks"]["target_R_max_lt_2"] is True
    assert '"metric_type": "ABSOLUTE"' in SRC


def test_inheritance_audit_passes():
    a = F.inheritance_audit()
    assert a["PASS"] is True, [k for k, v in a["checks"].items() if not v]
    assert a["checks"]["run_cell_is_gate2e_function"] is True


def test_eps_P1_is_exactly_1e_minus_3():
    assert abs(float(S2E.EPS_P1) - 1e-3) < 1e-15


def test_rule_target_strictly_below_check_threshold():
    assert float(F.P1_RULE_TARGET) < float(F.P1_CHECK_THRESHOLD)
    assert F.P1_RULE_TARGET < F.P1_CHECK_THRESHOLD


def test_thresholds_are_distinct_constants_and_not_reused():
    tree = ast.parse(SRC)
    names = {t.id for n in ast.walk(tree) if isinstance(n, ast.Assign)
             for t in n.targets if getattr(t, "id", "") in
             ("P1_RULE_TARGET", "P1_CHECK_THRESHOLD")}
    assert names == {"P1_RULE_TARGET", "P1_CHECK_THRESHOLD"}
    # the rule target is used ONLY to solve for h_z; the check uses the other
    geo = SRC.split("def geometry_and_Ed")[1].split("\ndef ")[0]
    assert "P1_RULE_TARGET" in geo and "P1_CHECK_THRESHOLD" not in geo
    ver = SRC.split("def p1_verdict")[1].split("\ndef ")[0]
    assert "check_threshold" in ver and "rule_target" in ver
    assert "(check_threshold - E_used) / check_threshold" in ver


def test_expected_headroom_is_about_eps_P1():
    rel = (float(F.P1_CHECK_THRESHOLD) - float(F.P1_RULE_TARGET)) / float(F.P1_CHECK_THRESHOLD)
    assert abs(rel - 1e-3) < 1e-9


def test_min_required_headroom_guard():
    assert F.MIN_HEADROOM_REL == 1e-6


def test_NEGATIVE_CONTROL_old_symmetric_logic_is_knife_edge():
    """The test that would have caught Gate-2E."""
    g = F.geometry_and_Ed()
    nc = F.negative_control(g["E_used"])
    assert nc["old_symmetric"]["knife_edge"] is True
    assert nc["old_symmetric"]["P1_PASS"] is False
    assert abs(nc["old_symmetric"]["headroom_rel"]) < 1e-6
    assert nc["new_asymmetric"]["robust"] is True
    assert nc["new_asymmetric"]["headroom_rel"] >= 1e-6
    assert nc["PASS"] is True


def test_p1_comparison_is_done_in_arb_not_on_a_float():
    ver = SRC.split("def p1_verdict")[1].split("\ndef ")[0]
    assert "E_used <= check_threshold" in ver
    assert "float(head.lower())" in ver, "headroom taken from the Arb lower endpoint"


def test_cells_use_gate2e_run_cell_verbatim():
    assert "S2E.run_cell(" in SRC
    tree = ast.parse(SRC)
    own = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
           and n.name in ("run_cell", "run_cell_2f")]
    assert not own, "Gate-2F must not define its own cell computation"


def test_objects_patch_grid_and_precisions_unchanged():
    assert S2E.PATCH == (17, 11) and S2E.GRID == 64
    assert S2E.PRECISIONS == (256, 384, 512) and S2E.DEGREE == 8
    assert S2E.CAND_DEGREE == 16
    tree = ast.parse(SRC)
    lits = {n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, int)}
    for banned in (640, 768, 192):
        assert banned not in lits, f"forbidden precision literal {banned}"


def test_no_candidate_refit():
    flat = CODE.replace(" ", "")
    assert "G2DM.build_hhat1" in flat and "G2DM.build_hhat2" in flat
    assert "cheb_fit_1d" not in flat and "cheb_candidate" not in flat
    assert '"refitted": False' in SRC


def test_execution_order_enforced_in_source():
    body = SRC.split("def run_pilot")[1].split("\ndef ")[0]
    order = ["inheritance_audit", "amplification_consistency", "p1_structural",
             "candidate_precondition", "representation_guard", "precision_grid"]
    idx = [body.index(f'"{s}"') for s in order]
    assert idx == sorted(idx), "enforced order violated"


def test_DECISIVE_invalid_precondition_skips_the_grid():
    r = F.run_pilot(candidate_budget=1e-30)
    assert r["acceptance_precondition"]["PASS"] is False
    assert "precision_grid" not in r["stages_run"]
    assert "cells" not in r
    assert r["decision"] == "SR_METRIC_B_FAIL_ABSOLUTE"


def test_old_P2_is_diagnostic_only():
    body = SRC.split("def run_pilot")[1].split("\ndef ")[0]
    sel = body.split("sel = next(")[1].split(")\n")[0]
    assert "P2" not in sel and "CELL_PASS" in sel
    assert '"P2_old_DIAGNOSTIC_ONLY"' not in body.split("sel = next(")[1]


def test_selection_takes_the_lowest_passing_precision():
    body = SRC.split("def run_pilot")[1].split("\ndef ")[0]
    assert "for c in cells[\"hhat_1\"]" in body
    assert S2E.PRECISIONS == tuple(sorted(S2E.PRECISIONS))
    assert "256" not in body.split("sel = next(")[1].split(")\n")[0], \
        "256 must not be hard-coded as the answer"


def test_no_gate2d_or_gate2e_residual_chooses_the_thresholds():
    head = SRC.split("# ---- THE ONLY NEW CONSTANTS")[1].split("# ---------")[0]
    assert "1.93" not in head and "sr_metric.json" not in head
    assert "eps_cand" not in head


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
    dirty = [s for s in st if s.strip() and "p5y_gate2f_sr_metric_b/" not in s]
    assert not dirty, f"working tree dirty outside Gate-2F: {dirty}"
