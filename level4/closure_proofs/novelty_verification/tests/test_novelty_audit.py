import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "level4/closure_proofs/novelty_verification"


def read(relative):
    return json.loads((BASE / relative).read_text())


def test_search_manifest_schema_and_query_provenance():
    manifest = read("results/search_manifest.json")
    assert manifest["schema"] == "rebaseguard.novelty-search-manifest.v1"
    assert len(manifest["runs"]) == 144
    assert all(run["query"] and run["query_id"] and run["family"] for run in manifest["runs"])


def test_mandatory_family_coverage_in_two_indexes():
    manifest = read("results/search_manifest.json")
    completed = {(run["source"], run["family"], run["query_id"]) for run in manifest["runs"] if run["status"] == "COMPLETED"}
    for source in ("OpenAlex", "Crossref"):
        for family in (f"7{x}" for x in "ABCDEFGHI"):
            assert sum(source == s and family == f for s, f, _ in completed) == 4


def test_source_access_failures_are_explicit():
    manifest = read("results/search_manifest.json")
    assert manifest["source_access"] == {
        "OpenAlex": "COMPLETED", "Crossref": "COMPLETED",
        "Semantic Scholar": "ACCESS-UNAVAILABLE", "Google Scholar": "ACCESS-UNAVAILABLE",
    }
    assert all(run["error"] for run in manifest["runs"] if run["status"] == "ACCESS-UNAVAILABLE")


def test_candidate_pool_screening_counts():
    pool = read("results/candidate_pool.json")
    assert pool["raw_records_screened"] == 1440
    assert pool["unique_candidates_screened"] == 1251
    assert all(candidate["triage"].startswith("SCREENED") or candidate["triage"] == "MANUAL-REVIEW" for candidate in pool["candidates"])


def test_bibliography_metadata_and_uniqueness():
    bibliography = read("results/bibliography.json")
    works = bibliography["works"]
    assert len(works) == 33
    assert len({work["work_id"] for work in works}) == len(works)
    assert len({work["doi"] or (work["title"].casefold(), work["year"]) for work in works}) == len(works)
    assert all(work["title"] and work["authors"] and work["year"] and work["venue"] and work["stable_url"] for work in works)


def test_doi_normalization():
    works = read("results/bibliography.json")["works"]
    assert all(doi == doi.lower() and not doi.startswith(("http", "doi:")) and not doi.endswith(".") for doi in (work["doi"] for work in works) if doi)


def test_prior_art_matrix_complete():
    matrix = read("results/prior_art_matrix.json")
    assert matrix["components"] == [f"C{i}" for i in range(1, 12)]
    assert len(matrix["rows"]) == 33
    assert all(set(row["components"]) == set(matrix["components"]) for row in matrix["rows"])
    assert all(value in matrix["cell_values"] for row in matrix["rows"] for value in row["components"].values())


def test_c1_c11_have_prior_art_assessments():
    matrix = read("results/prior_art_matrix.json")
    for component in matrix["components"]:
        assert any(row["components"][component] != "UNCLEAR" for row in matrix["rows"])
    assert matrix["overlap_counts"]["DIRECT"] == 0
    assert matrix["overlap_counts"]["HIGH-PARTIAL"] == 9


def test_high_candidate_audit_completeness():
    high = set(read("results/prior_art_matrix.json")["high_partial_work_ids"])
    audits = read("bibliography/high_audits.json")
    assert {audit["work_id"] for audit in audits["audits"]} == high
    expected = set(audits["question_keys"])
    assert len(expected) == 13
    assert all(set(audit["answers"]) == expected and all(audit["answers"].values()) for audit in audits["audits"])


def test_snowball_provenance_and_stopping_rule():
    evidence = read("results/snowball_evidence.json")
    assessment = read("bibliography/snowball_assessment.json")
    assert len(evidence["seeds"]) == 17
    assert all(seed["backward_status"] == seed["forward_status"] == "COMPLETED" for seed in evidence["seeds"])
    assert assessment["stopping_rule_satisfied"]
    assert [row["new_direct"] for row in assessment["rounds"]] == [0, 0]
    assert [row["new_high_partial"] for row in assessment["rounds"]] == [0, 0]


def test_claim_firewall_complete_and_priority_forbidden():
    firewall = read("results/claim_firewall.json")
    assert len(firewall["claims"]) >= 13
    assert set(firewall["allowed_classifications"]) == {"SAFE", "SAFE-WITH-QUALIFIER", "UNSUPPORTED", "FORBIDDEN"}
    assert set(firewall["priority_words"]) == {"first", "first-ever", "unprecedented"}
    assert set(firewall["priority_words"].values()) == {"FORBIDDEN"}


def test_current_safe_outputs_have_no_priority_claim():
    text = "\n".join((BASE / name).read_text() for name in ("PUBLICATION_SAFE_CLAIMS.md", "RESUME_SAFE_CLAIMS.md"))
    assert not re.search(r"\b(first(?:-ever)?|unprecedented|previously unknown)\b", text, re.I)
    assert not re.search(r"\b(is|are) novel\b|\bnew (?:method|mechanism|theorem)\b", text, re.I)


def test_decision_is_mechanically_derived():
    decision = read("results/decision.json")
    assert all(decision["criteria"].values())
    assert decision["decision"] == "NOVELTY-VERIFICATION-CLOSED"
    assert decision["novelty_position"] == "N2"
    assert decision["original_global_requirement"] == "CLOSED"
    assert decision["remaining_fail_open_blockers"] == [{"name": "SEMI-REAL EXTERNAL VALIDATION", "type": "SCIENTIFIC"}]
    assert decision["historical_stage_f_verdict"] == decision["current_post_closure_global_verdict"] == "LEVEL-4-PARTIAL"


def test_generator_outputs_are_byte_stable():
    command = [str(ROOT / "level4/.venv/bin/python"), str(BASE / "src/generate_artifacts.py"), "--check"]
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr
    assert "16 generated artifacts byte-stable" in completed.stdout
