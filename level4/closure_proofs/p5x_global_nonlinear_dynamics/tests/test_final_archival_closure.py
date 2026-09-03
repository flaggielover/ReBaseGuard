"""Archival consistency of the P5X final closure record.

These tests check that the archive faithfully reproduces results recorded
elsewhere in the repository.  They verify NO science and must never be written
so that a failed gate reads as passed.
"""
from __future__ import annotations
import json, re, subprocess
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ARCH = NS / "final_archival_closure"
LEDGER = json.loads((ARCH / "commit_ledger.json").read_text())
CLAIMS = json.loads((ARCH / "final_claim_table.json").read_text())
DOC = (ARCH / "FINAL_ARCHIVAL_CLOSURE.md").read_text()
# flatten for phrase checks: drop markdown blockquote markers, then collapse
FLAT = " ".join(re.sub(r"(?m)^\s*>\s?", "", DOC).split())
PROD = json.loads((NS / "results" / "cusum_m1_production.json").read_text())
REPO = NS.parents[2]


def _git(*a):
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True,
                          text=True, check=True).stdout.strip()


# --- the archive exists and is classified as an archive -------------------

def test_commit_ledger_exists_and_is_classified():
    assert LEDGER["classification"] == "FINAL_ARCHIVAL_CLOSURE_RECORD"
    assert CLAIMS["classification"] == "FINAL_ARCHIVAL_CLOSURE_RECORD"
    assert "FINAL_ARCHIVAL_CLOSURE_RECORD" in DOC
    assert "not a scientific successor" in FLAT


def test_commit_ledger_covers_the_whole_campaign_and_maps_every_commit():
    assert LEDGER["commits_total"] == len(LEDGER["commits"]) == 35
    assert LEDGER["unmapped_subjects"] == []
    assert all(c["phase"] for c in LEDGER["commits"])


def test_ledger_commits_all_resolve_in_git():
    for c in LEDGER["commits"][:6] + LEDGER["commits"][-6:]:
        assert _git("rev-parse", "--verify", c["commit"] + "^{commit}") == c["commit"]


def test_ledger_endpoints_match_the_authoritative_commits():
    assert LEDGER["head"] == "66f9cbad4d638e276aa7d19994ffee4341bd6c1f"
    assert LEDGER["production_result"] == LEDGER["head"]
    assert LEDGER["checkpoint_k"] == "3704988533f2d9038ddf0b35e58dea0eed4b6a2d"
    assert LEDGER["commits"][-1]["commit"] == LEDGER["head"]


# --- statuses match their source artifacts, not the prose ----------------

def test_claim_table_uses_only_the_allowed_vocabulary():
    allowed = {"EXACT", "CERTIFIED", "EMPIRICAL", "CONDITIONAL",
               "FAIL", "OUT_OF_BUDGET", "NOT_RUN", "INCOMPLETE"}
    assert set(CLAIMS["vocabulary"]) == allowed
    for c in CLAIMS["claims"]:
        assert c["status"] in allowed
        assert c["scope"] and c["method"] and c["strongest_legitimate_claim"]
        assert c["commit"]
        if c["status"] in {"FAIL", "OUT_OF_BUDGET", "NOT_RUN", "INCOMPLETE"}:
            assert c.get("reason_if_non_pass") or c["status"] == "INCOMPLETE"


def _claim(name):
    return next(c for c in CLAIMS["claims"] if c["claim"].startswith(name))


def test_gate_statuses_match_the_recorded_gate_artifacts():
    res = NS / "results"
    assert json.loads((res / "r6_gate.json").read_text())["gate"] == "PASS"
    for f in ("r3_gate.json", "r4_gate.json", "r5_gate.json", "sr_prototype.json"):
        assert json.loads((res / f).read_text())["gate"] == "FAIL"
    assert json.loads((res / "r8_sr_prototype.json").read_text())["verdict"] == "FAIL"


def test_sr_local_certification_recorded_as_certified():
    assert _claim("SR m=1 local certification")["status"] == "CERTIFIED"
    assert _claim("SR m=1 sign")["status"] == "CERTIFIED"


def test_sr_global_out_of_budget_matches_the_far_field_audit():
    c = _claim("SR m=1 global G3")
    assert c["status"] == "OUT_OF_BUDGET"
    a = json.loads((NS / "far_field_wminus_edge_audit" / "audit_results.json").read_text())
    assert a["worst"]["G_new"] == 4708 and a["worst"]["G_max"] == 1536
    assert "4708" in c["reason_if_non_pass"] and "1536" in c["reason_if_non_pass"]


def test_sr_m_gt_1_and_second_moments_not_run():
    assert _claim("SR m>1 global G3")["status"] == "NOT_RUN"
    assert _claim("second-moment production")["status"] == "NOT_RUN"
    assert PROD["second_moment_production"] == "NOT_RUN"


def test_mechanism_is_conditional_not_exact():
    c = _claim("stationary nonlinear mechanism")
    assert c["status"] == "CONDITIONAL"
    assert "P5X-T4" in c["reason_if_non_pass"] and "P5X-T6" in c["reason_if_non_pass"]


# --- the CUSUM negative result is preserved exactly ----------------------

def test_cusum_m1_recorded_as_fail():
    assert _claim("CUSUM m=1 global G3")["status"] == "FAIL"
    assert "CUSUM_M1_G3             = FAIL" in DOC
    assert PROD["all_pass"] is False


def test_cusum_46_of_47_preserved():
    passing = sum(1 for r in PROD["ledger"] if r["status"] == "PASS")
    assert passing == 46 and len(PROD["ledger"]) == 47
    assert "CUSUM_M1_PASS_CELLS     = 46/47" in DOC
    assert "46 of the 47 cells" in FLAT      # narrative
    assert "46/47 frozen cover cells" in FLAT  # README wording


def test_failing_cell_preserved_verbatim():
    bad = [r for r in PROD["ledger"] if r["status"] != "PASS"]
    assert len(bad) == 1 and bad[0]["i"] == 46
    assert bad[0]["e_lo"] == 10.5441104 and bad[0]["e_hi"] == 12.0
    assert "10.5441104" in DOC and "2.336765897" in DOC


def test_failure_class_and_true_violation_recorded_separately():
    assert "CUSUM_M1_FAILURE_CLASS  = C-F2_CERTIFICATE_WIDTH" in DOC
    assert "TRUE_CUSUM_G3_VIOLATION = NOT_ESTABLISHED" in DOC


def test_archive_does_not_convert_the_fail_into_a_pass():
    # the theorem splice is named and explicitly refused
    assert "it is not done here" in FLAT
    assert _claim("CUSUM m=1 global G3")["status"] != "PASS"
    assert "46/47" in DOC and "PROVED_ALL_CELLS" not in DOC


def test_e_far_remains_12():
    assert "`e_far = 12`" in (NS / "FROZEN_SCOPE.md").read_text()
    assert PROD["e_domain"] == [0, 12]
    assert "frozen `e_far = 12` remains unchanged" in FLAT


def test_cusum_m_gt_1_incomplete_no_certifier():
    c = _claim("CUSUM m>1 global G3")
    assert c["status"] == "INCOMPLETE"
    assert "no production certifier" in c["method"]
    assert "NO CERTIFIER" in PROD["m_gt_1"].upper()


# --- governance ----------------------------------------------------------

def test_no_historical_verdict_changed():
    for line in ("P5_ORIGINAL_VERDICT       = PARTIAL",
                 "P5X_FINAL_VERDICT         = PARTIAL",
                 "P5_SCIENTIFIC_LINE_STATUS = PARTIALLY_REPAIRED_BY_SUCCESSOR",
                 "LEVEL4_GLOBAL_CLOSURE       = NO"):
        assert line in DOC


def test_forbidden_verdict_vocabulary_is_never_asserted():
    # the words may appear only in the sentence that rules them out
    for bad in ("PARTIAL_STRONG", "CLOSED_IN_SCOPE",
                "EFFECTIVELY_CLOSED", "PRACTICALLY_CLOSED"):
        assert DOC.count(bad) == 1
        assert "does not use" in FLAT


def test_future_options_are_marked_non_authorized():
    assert DOC.count("FUTURE_OPTION_ONLY") == 4
    assert "None is authorized, none is implemented" in FLAT


def test_handoff_does_not_claim_p4x_is_the_only_residual():
    assert "NEXT_ACTIVE_REPAIR_CAMPAIGN = P4X" in DOC
    assert "P5_SCIENTIFIC_LINE_REMAINING = YES" in DOC
    assert "not** claimed to be the only unresolved issue" in FLAT
    assert "P5 residual is frozen" in FLAT


# --- protected tree identity --------------------------------------------

def test_protected_trees_identical_by_git_object():
    for p in ("level4/closure_proofs/p5_nonlinear_dynamics",
              "rebaseguard-lean", "rebaseguard-proof",
              "level4/closure_proofs/p4_theory_generalization",
              "level4/closure_proofs/p9_final_synthesis"):
        assert _git("rev-parse", f"origin/main:{p}") == _git("rev-parse", f"HEAD:{p}")


def test_original_p5_tree_object_is_the_recorded_one():
    assert _git("rev-parse", "HEAD:level4/closure_proofs/p5_nonlinear_dynamics") \
        == "ec1d3b1da066a4ddda34f24bd5e062c6b8a93484"


def test_historical_p5x_result_directories_unchanged_since_their_commits():
    ns = "level4/closure_proofs/p5x_global_nonlinear_dynamics"
    for d, at in (("compute_optimization_r6_minimal_evaluator", "83baefb14d7c6a8250f3fab6b619da9c9463796c"),
                  ("compute_optimization_r8_sr_certification", "6c4744aa1272c6bf9639dc01c4bcb50f9f6e629f"),
                  ("far_field_wminus_edge_audit", "7995ec303c9cfc708908ca7b7b049a3285b4a127"),
                  ("cusum_global_production", "66f9cbad4d638e276aa7d19994ffee4341bd6c1f")):
        assert _git("rev-parse", f"{at}:{ns}/{d}") == _git("rev-parse", f"HEAD:{ns}/{d}")
