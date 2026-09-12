"""Final P4Z closure packet: internal consistency, pins, and preserved history.

Everything is re-derived from the repository, so a drifted pin or an edited
frozen artifact fails here rather than silently changing the record.
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

NS = Path(__file__).resolve().parent.parent
CP = NS.parent
REPO = CP.parent.parent
sys.path.insert(0, str(NS))

import build_manifest as bm  # noqa: E402

MAN = json.loads((NS / "MANIFEST.json").read_text())
GD = json.loads((NS / "gate_discharge.json").read_text())
FC = json.loads((NS / "final_closure.json").read_text())

PARENT_BRANCH = "p4zr-rng-provenance-repair"
OWN = "level4/closure_proofs/p4z_final_closure/"


def git(*a):
    return subprocess.run(("git", "-C", str(REPO)) + a,
                          capture_output=True, text=True, check=True).stdout.strip()


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# --- 1. the packet is derivable, not hand-written -------------------------

def test_manifest_is_exactly_what_the_builder_derives():
    fresh = bm.build_manifest()
    fresh.pop("corroboration_only", None)
    assert fresh == MAN, "MANIFEST.json is stale; re-run build_manifest.py"


def test_gate_discharge_is_exactly_what_the_builder_derives():
    assert bm.gate_discharge() == GD, "gate_discharge.json is stale"


def test_every_pinned_file_hash_still_matches():
    checked = 0
    def walk(o):
        nonlocal checked
        if isinstance(o, dict):
            if set(o) >= {"path", "sha256"} and isinstance(o.get("path"), str):
                p = REPO / o["path"]
                assert p.is_file(), f"pinned file missing: {o['path']}"
                assert sha(p) == o["sha256"], f"pin drifted: {o['path']}"
                checked += 1
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(MAN)
    assert checked >= 12, f"expected many pins, checked {checked}"


def test_manifest_carries_no_hash_of_itself():
    assert "EXCLUDED BY CONSTRUCTION" in MAN["manifest_self_hash"]
    blob = json.dumps(MAN, indent=2, sort_keys=True) + "\n"
    assert sha(NS / "MANIFEST.json") not in blob


# --- 2. frozen and protected artifacts ------------------------------------

def test_frozen_p4_theorem_tree_is_byte_identical_everywhere():
    want = MAN["frozen_theorem"]["tree_object"]
    assert want == "eede90383da44c250871b1bb97d12045c897c8d9"
    path = MAN["frozen_theorem"]["namespace"]
    for ref in ("HEAD", "main", "codex/presentation-refresh",
                "p4x-feasibility-audit", "p4y-pilot4-measurement",
                "p4zb-skewnormal4-k7", "p4zr-rng-provenance-repair"):
        assert git("rev-parse", f"{ref}:{path}") == want, f"{ref} differs"


def test_protected_trees_match_their_pinned_values():
    for path, want in MAN["protected_trees"].items():
        assert git("rev-parse", f"HEAD:{path}") == want, f"{path} changed"


def test_successor_trees_match_their_own_branch_tips():
    for path in ("level4/closure_proofs/p4z_location_family_feasibility",
                 "level4/closure_proofs/p4za_fullscope_closure",
                 "level4/closure_proofs/p4zb_skewnormal4_k7"):
        assert git("rev-parse", f"HEAD:{path}") == \
            git("rev-parse", f"p4zb-skewnormal4-k7:{path}"), f"{path} changed"


def test_p4zr_tree_matches_its_own_branch_tip():
    path = "level4/closure_proofs/p4zr_rng_provenance_repair"
    assert git("rev-parse", f"HEAD:{path}") == \
        git("rev-parse", f"{PARENT_BRANCH}:{path}")


def test_packet_touches_no_path_outside_its_own_namespace():
    changed = [p for p in git("diff", "--name-only", PARENT_BRANCH, "HEAD").splitlines() if p]
    working = [l[3:].strip().strip('"') for l in git("status", "--porcelain").splitlines() if l]
    outside = [p for p in changed + working if p and not p.startswith(OWN)]
    assert not outside, f"packet modified protected paths: {sorted(set(outside))}"


def test_defective_historical_scripts_remain_unedited():
    for rel in ("level4/closure_proofs/p4z_location_family_feasibility/micropilots/run_micropilots.py",
                "level4/closure_proofs/p4z_location_family_feasibility/micropilots/run_fd_ladder.py",
                "level4/closure_proofs/p4za_fullscope_closure/audit/calibrate_ladder.py"):
        assert git("rev-parse", f"HEAD:{rel}") == \
            git("rev-parse", f"p4zb-skewnormal4-k7:{rel}")


# --- 3. historical verdicts preserved -------------------------------------

def test_historical_p4_verdict_is_still_partial_in_its_own_artifact():
    d = json.loads((CP / "p4_theory_generalization" / "results"
                    / "closure_decision.json").read_text())
    assert d["verdict"] == "PARTIAL"
    assert d["all_required_gates_pass"] is False
    assert FC["status"]["historical_verdict"]["P4"] == "PARTIAL"
    assert GD["historical_p4_verdict_unchanged"] is True


def test_stagewise_self_verdicts_are_retained_verbatim():
    got = FC["historical_record_preserved"]["stagewise_self_verdicts"]
    for name, path in (
        ("P4Z", CP / "p4z_location_family_feasibility" / "results" / "successor_closure.json"),
        ("P4ZA", CP / "p4za_fullscope_closure" / "results" / "p4za_successor_closure.json"),
        ("P4ZB", CP / "p4zb_skewnormal4_k7" / "results" / "p4zb_successor_closure.json"),
    ):
        assert got[name] == json.loads(path.read_text())["verdict"]
    assert got["P4ZA"] == "P4ZA_INCONCLUSIVE"
    assert got["P4ZB"] == "P4ZB_CLOSED"


def test_p4x_is_not_rehabilitated_and_p4y_is_not_reinterpreted():
    assert GD["p4x_campaign_rehabilitated"] is False
    assert FC["adjudications"]["B3_rule_c"]["p4x_campaign_rehabilitated"] is False
    assert MAN["historical_lineage"]["P4X"]["rehabilitated_by_this_packet"] is False
    assert MAN["historical_lineage"]["P4Y"]["outcome"] == "NOT_FEASIBLE"
    assert MAN["historical_lineage"]["P4X"]["scientific_failures"] == "NONE"


# --- 4. the closure statement itself --------------------------------------

def test_the_three_statuses_are_distinct_and_correct():
    s = FC["status"]
    assert s["historical_verdict"]["P4"] == "PARTIAL"
    assert s["historical_verdict"]["immutable"] is True
    assert s["successor_closure"]["P4Z"] == "CLOSED"
    assert s["scientific_line"]["P4_SCIENTIFIC_LINE"] == "CLOSED_BY_LATER_SUCCESSOR"
    assert FC["verdict"] == "P4Z_CLOSED"


def test_p4_equals_closed_is_never_asserted_anywhere_in_the_packet():
    """Prose may name the forbidden claim only to deny it; JSON may not at all."""
    for p in sorted(NS.glob("*.json")):
        assert "P4 = CLOSED" not in p.read_text() or \
            p.name == "final_closure.json", p.name
    fc_text = json.dumps(FC)
    assert "P4 = CLOSED" in fc_text  # only inside claims_explicitly_not_made
    assert "P4 = CLOSED" in FC["claims_explicitly_not_made"]

    negators = ("not ", "no ", "never", "neither", "nor ", "denied")
    for p in sorted(NS.glob("*.md")):
        for n, line in enumerate(p.read_text().splitlines(), 1):
            if "P4 = CLOSED" in line or "P4 CLOSED" in line:
                assert any(t in line.lower() for t in negators), \
                    f"{p.name}:{n} asserts P4 = CLOSED: {line.strip()}"


def test_all_three_original_gates_are_discharged():
    assert len(GD["originally_failed_gates"]) == 3
    assert GD["originally_failed_gates"] == sorted([
        "all_theorem_supported_cells_pass",
        "all_outside_assumption_cells_demonstrate_failure",
        "gaussian_consistency_with_closed_core"])
    assert GD["all_discharged"] is True
    assert all(r["status"] == "DISCHARGED" for r in GD["gates"])
    assert FC["original_p4_failed_gates"]["all_discharged"] is True


def test_gate_discharge_matches_p4s_own_recorded_gate_ledger():
    gates = json.loads((CP / "p4_theory_generalization" / "results"
                        / "closure_decision.json").read_text())["gates"]
    assert sorted(k for k, v in gates.items() if v is False) == \
        GD["originally_failed_gates"]


def test_rule_c_is_applied_only_to_c4_and_c5():
    applied = [r["original_p4_gate"] for r in GD["gates"] if r["rule_c_applied"]]
    assert applied == ["all_outside_assumption_cells_demonstrate_failure",
                       "gaussian_consistency_with_closed_core"]
    for r in GD["gates"]:
        if r["rule_c_applied"]:
            f = r["rule_c_findings"]
            assert f["uses_no_tainted_result_bearing_computation"] is True
            assert f["frozen_provenance_intact"] is True
            assert "NONE" in f["new_compute"]


# --- 5. the numerical basis -----------------------------------------------

def test_strict_gate_numbers_match_the_reconstruction_artifact():
    src = json.loads((CP / "p4zr_rng_provenance_repair" / "results"
                      / "strict_gate_reconstruction.json").read_text())
    sg = MAN["strict_gate_reconstruction"]
    assert sg["cells_total"] == src["cells_total"] == 96
    assert sg["cells_passing"] == src["cells_passing_the_strict_gate"] == 96
    assert sg["cells_exceeding_either_frozen_gate"] == 0
    assert sg["worst_z_monte_carlo_error_only"] == pytest.approx(1.7876746141, abs=1e-9)
    assert sg["worst_relative_discrepancy"] == pytest.approx(0.0094996044, abs=1e-9)
    assert sg["worst_z_monte_carlo_error_only"] < sg["z_limit"] == 4.0
    assert sg["worst_relative_discrepancy"] < sg["relative_limit"] == 0.03


def test_final_coverage_still_reads_96_of_96():
    cov = json.loads((CP / "p4zb_skewnormal4_k7" / "results"
                      / "final_coverage.json").read_text())
    assert cov["cells_total"] == 96
    assert cov["counts"] == {"COVERED_PASS": 96, "COVERED_FAIL": 0,
                             "INCONCLUSIVE": 0, "UNCOVERED": 0}
    assert cov["conservation"]["conserved"] is True
    assert cov["authoritative_sources"] == {"P4Z": 44, "P4ZA": 48, "P4ZB": 4}
    assert FC["numerical_basis"]["counts"] == cov["counts"]


def test_no_new_numerical_compute_is_claimed_or_stored():
    assert MAN["new_numerical_compute"] == "NONE"
    assert FC["new_numerical_compute"] == "NONE"
    assert not list(NS.rglob("blocks")), "packet stores no block data"
    for p in NS.rglob("*.json"):
        assert json.loads(p.read_text()).get("result_bearing") is not True


# --- 6. adjudication inputs pinned to real, current commits ----------------

def test_b2_and_b4_commits_exist_and_are_current():
    b2 = MAN["adjudication_inputs"]["B2_rng_provenance"]
    assert b2["commit"] == git("rev-parse", "p4zr-rng-provenance-repair")
    assert git("cat-file", "-t", b2["commit"]) == "commit"
    b4 = MAN["adjudication_inputs"]["B4_presentation"]
    assert b4["commit"] == git("rev-parse", "codex/presentation-refresh")
    assert git("cat-file", "-t", b4["commit"]) == "commit"


def test_successor_freeze_commits_carry_no_result_blocks():
    """Protocol-before-result, verified at the git object level."""
    for name, ns in (("P4Z", "p4z_location_family_feasibility"),
                     ("P4ZA", "p4za_fullscope_closure"),
                     ("P4ZB", "p4zb_skewnormal4_k7")):
        c = MAN["successor_campaigns"][name]
        path = f"level4/closure_proofs/{ns}"
        at_freeze = git("ls-tree", "-r", "--name-only", c["freeze_commit"], "--", path)
        at_result = git("ls-tree", "-r", "--name-only", c["result_commit"], "--", path)
        assert sum("/blocks/" in l for l in at_freeze.splitlines()) == 0, name
        assert sum("/blocks/" in l for l in at_result.splitlines()) > 0, name


def test_b2_findings_match_the_disclosure_artifact():
    d = json.loads((CP / "p4zr_rng_provenance_repair" / "results"
                    / "rng_collision_disclosure.json").read_text())
    f = MAN["adjudication_inputs"]["B2_rng_provenance"]["findings"]
    assert f["P4Z"] == "RNG_ADDRESS_SEPARATION_FAIL"
    assert f["P4ZA"] == "RNG_ADDRESS_SEPARATION_PASS"
    assert f["P4ZB"] == "RNG_ADDRESS_SEPARATION_PASS"
    assert f["address_overlaps_total"] == 5
    assert f["overlapping_addresses_total"] == 25
    assert f["disposition_bearing_overlaps"] == 0
    assert f["disposition_bearing_overlaps"] == d["impact"]["disposition_bearing_overlaps"]


def test_k7_diagnostic_history_is_preserved_not_erased():
    for rel in MAN["adjudication_inputs"]["B1_k7"]["diagnostic_history_preserved"]:
        assert (REPO / rel).is_file(), rel
    # P4ZA's refusal to widen the limit must still be on the record
    za = json.loads((CP / "p4za_fullscope_closure" / "results"
                     / "p4za_successor_closure.json").read_text())
    assert za["verdict"] == "P4ZA_INCONCLUSIVE"
    assert "NOT widened" in za["what_remains_open"]["reading"]


# --- 7. honesty of language -----------------------------------------------

def test_impact_language_is_bounded_not_absolute():
    txt = FC["adjudications"]["B2_rng_provenance"]["impact_statement"].lower()
    assert "no observed disposition dependence" in txt
    assert "bounded by" in txt
    for banned in ("harmless", "no impact", "zero risk", "cannot have affected"):
        assert banned not in txt


def test_residual_uncertainty_is_carried_forward_not_discharged():
    assert len(FC["residual_uncertainty"]) >= 5
    joined = " ".join(FC["residual_uncertainty"]).lower()
    assert "counterfactual" in joined
    assert FC["adjudications"]["B2_rng_provenance"]["residual_uncertainty_retained"] is True


def test_out_of_scope_claims_are_explicitly_disclaimed():
    c = FC["claims_explicitly_not_made"]
    assert "P4 = CLOSED" in c
    assert any("Level-4" in x for x in c)
    assert any("rehabilitated" in x for x in c)
    assert any("production readiness" in x for x in c)


def test_no_out_of_scope_closure_is_asserted_in_prose():
    forbidden = (r"\bP5\s*=\s*CLOSED", r"\bK1\s*=\s*CLOSED",
                 r"Level-4\s*=\s*CLOSED", r"\bPS1\s*=\s*CLOSED")
    for p in sorted(NS.glob("*.md")):
        text = p.read_text()
        for pat in forbidden:
            assert not re.search(pat, text), f"{p.name} asserts {pat}"
