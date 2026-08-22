"""Stage F tests: integrity of the historical record and of the final verdict.

Stage F performed no scientific experiment. These tests exist to make it
impossible for the closure audit to quietly inflate, mutate or repair the
history it is auditing.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
SF = REPO / "level4" / "stage_f"
RES = SF / "results"
REPORTS = REPO / "level4" / "reports"

FROZEN = {
    "level4/stage_c/STAGE_C_PROTOCOL.md":
        "36bd6ba03a20b7f87dc0eb91c42e5c023c03d7a23cba0c515390d1130b2cedd7",
    "level4/stage_c1/STAGE_C1_PROTOCOL.md":
        "7b45c091229387e255b285013a4f7d60fac7c2adad66ba83d69e30c3ef79cbdb",
    "level4/stage_d/STAGE_D_PROTOCOL.md":
        "925adecf08c7234375333a26c3af934b005e0d8b4cfce470b77834d7245e8b2e",
    "level4/stage_e/STAGE_E_PROTOCOL.md":
        "974487019f57c7c319b3bfafcdc20497ab6fca86834ad0d2245a694296ef23cc",
    "level4/stage_d/notes/D2_3_STEP_PRECOMMIT.md":
        "7b7a54c64f4c86334415a03cd45797e7cb8b923d378fa90180a71f1831588dea",
    "level4/stage_d/notes/D2_5_PRECOMMIT.md":
        "fb6272ef839d7f3b36af3c8a8ace3d3059df7028dda337455b9df6baaf92bba7",
    "level4/stage_d/notes/D3_REGULARITY.md":
        "9eafbcd25870a19e20d5f84c763c5252bd44b3af809de4821d1e99555f93626e",
}
DECISIONS = {
    "level4/stage_c/results/findings.json": "STAGE-C-PARTIAL",
    "level4/stage_c1/results/findings_confirmatory.json":
        "STAGE-C1-CLOSED-CONFIRMED-SENSITIVITY",
    "level4/stage_d/results/stage_d_decision.json": "STAGE-D-PARTIAL",
    "level4/stage_e/results/stage_e_decision.json": "STAGE-E-PARTIAL",
    "level4/stage_b/certificate/period2_certificate.json":
        "STAGE-B-CLOSED-RIGOROUS-PERIOD2",
}


def load(p):
    return json.loads((REPO / p).read_text())


# ------------------------------------------------------------ protocol freeze
@pytest.mark.parametrize("rel,want", sorted(FROZEN.items()))
def test_frozen_hash_unchanged(rel, want):
    assert hashlib.sha256((REPO / rel).read_bytes()).hexdigest() == want


@pytest.mark.parametrize("rel,want", sorted(DECISIONS.items()))
def test_historical_decision_unchanged(rel, want):
    assert load(rel)["decision"] == want


def test_level_1_3_still_declared_closed():
    t = (REPO / "closure" / "LEVEL_1_3_CLOSURE_REPORT.md").read_text()
    assert "LEVEL 1–3: CLOSED" in t or "LEVEL 1-3: CLOSED" in t


# ------------------------------------------------- negative results preserved
def test_d2_3_still_failed():
    d = load("level4/stage_d/results/stage_d_decision.json")
    assert [c for c in d["criteria"] if c["id"] == "D2.3"][0]["status"] == "FAIL"


def test_d2_5_still_mathematical_not_operational():
    assert load("level4/stage_d/results/d2_5_verdict.json")["verdict"] == \
        "MATHEMATICAL, NOT OPERATIONAL"


def test_t3_still_ambiguous():
    d = load("level4/stage_d/results/stage_d_decision.json")
    assert [c for c in d["criteria"] if c["id"] == "D3.2-t3"][0]["status"] == "AMBIGUOUS"


def test_d4_still_not_run():
    d = load("level4/stage_d/results/stage_d_decision.json")
    assert [c for c in d["criteria"] if c["id"] == "D4"][0]["status"] == "NOT RUN"


def test_stage_e_zero_of_three_preserved():
    e = load("level4/stage_e/results/stage_e_decision.json")
    assert e["n_tasks_supporting_H_E5"] == 0
    assert e["closure_mathematically_unreachable"] is True


def test_stage_e_task_c_unreliable_endpoints_excluded():
    c = load("level4/stage_e/results/stage_e_decision.json")["per_task"]["bike_sharing"]
    assert set(c["unreliable_endpoints"]) >= {"E2", "E3"}
    assert c["hypotheses"]["H_E1"]["status"] == "UNEVALUABLE"
    assert c["counts_toward_H_E5"] is False


def test_stage_e_p3_remains_exploratory():
    e = load("level4/stage_e/results/stage_e_decision.json")
    assert e["exploratory_policy_excluded"] == "P3_moderate_EXPLORATORY"


def test_stage_c_c6_failure_record_still_present():
    p = REPO / "level4/stage_c/notes/CRITERION_C6_DIAGNOSIS.md"
    assert p.exists() and len(p.read_text()) > 200


def test_stage_d_first_run_a11_failure_record_preserved():
    t = (REPO / "level4/stage_d/notes/FAILURE_DIAGNOSES.md").read_text()
    assert "A11" in t and "FAILED" in t


def test_stage_f_first_adversarial_run_preserved():
    """The failed-first record must never be deleted or overwritten."""
    p = RES / "adversarial_f_FIRST_RUN.json"
    assert p.exists()
    d = json.loads(p.read_text())
    assert d["n_passed"] == 11 and d["n_checks"] == 18


# ----------------------------------------------------------- final decision
def test_final_decision_label_is_from_the_fallback_taxonomy():
    d = load("level4/stage_f/results/final_decision.json")
    assert d["decision"] in {"LEVEL-4-CLOSED", "LEVEL-4-CLOSED-WITH-LIMITATIONS",
                             "LEVEL-4-PARTIAL", "LEVEL-4-FAILED"}


def test_final_decision_is_partial_with_unmet_mandatory_requirements():
    d = load("level4/stage_f/results/final_decision.json")
    assert d["decision"] == "LEVEL-4-PARTIAL"
    assert d["n_mandatory_unmet"] >= 1
    assert len(d["mandatory_unmet"]) == d["n_mandatory_unmet"]


def test_verdict_is_robust_to_the_mandatory_label_ambiguity():
    d = load("level4/stage_f/results/final_decision.json")
    assert d["verdict_robust_to_interpretation"]["both_readings_agree"] is True


def test_taxonomy_is_declared_as_a_fallback():
    d = load("level4/stage_f/results/final_decision.json")
    assert "FALLBACK" in d["taxonomy_source"].upper()


def test_closed_with_limitations_was_not_silently_adopted():
    d = load("level4/stage_f/results/final_decision.json")
    assert d["decision"] != "LEVEL-4-CLOSED-WITH-LIMITATIONS"
    assert any("ORIGINAL architecture" in t or "original architecture" in t
               for t in d["decision_rule_trace"])


def test_every_unmet_mandatory_requirement_cites_an_artifact():
    d = load("level4/stage_f/results/final_decision.json")
    for r in d["mandatory_unmet"]:
        assert (REPO / r["artifact"]).exists(), r


# ------------------------------------------------------------- claim guard
FORBIDDEN = ["detector-independent", "distribution-free", "production validated",
             "production-proven", "optimal reuse", "universally safe",
             "universally unstable", "real-world deployment validated",
             "first-ever sequential monitoring stability boundary",
             "completed level 4"]
NEG = ("not ", "never", "no ", "❌", "rather than", "cannot", "must not",
       "ruled out", "unreachable", "does not", "forbidden", "without")


def _scannable(p: Path) -> str:
    """Document text with declared forbidden-phrase contexts removed.

    Two exemptions, both narrow and both structural rather than blanket:
      1. a SECTION whose heading declares it lists forbidden/ruled-out wording;
      2. the "Forbidden wording" COLUMN of a claim-ledger table -- a column whose
         entire purpose is to enumerate banned phrases must be allowed to
         contain them. Only that column is dropped; every other cell in the same
         row is still scanned.
    """
    lines, out, skip = p.read_text().splitlines(), [], False
    forbidden_col = None
    for line in lines:
        if line.startswith("#"):
            low = line.lower()
            skip = ("forbidden" in low or "ruled out" in low
                    or "not supported" in low or "not claimed" in low)
        if skip:
            continue
        if line.startswith("|"):
            cells = line.split("|")
            if forbidden_col is None and "forbidden wording" in line.lower():
                for i, c in enumerate(cells):
                    if "forbidden wording" in c.lower():
                        forbidden_col = i
                        break
            if forbidden_col is not None and len(cells) > forbidden_col:
                cells[forbidden_col] = " "
                line = "|".join(cells)
        out.append(line)
    return "\n".join(out).lower().replace("*", "").replace("`", "")


FINAL_DOCS = ["level4/reports/LEVEL_4_FINAL_REPORT.md",
              "level4/reports/LEVEL_4_FINAL_LEDGER.md",
              "level4/stage_f/SCIENTIFIC_SYNTHESIS.md",
              "level4/stage_f/FINAL_DECISION.md"]


@pytest.mark.parametrize("word", FORBIDDEN)
def test_forbidden_wording_only_appears_negated(word):
    for rel in FINAL_DOCS:
        p = REPO / rel
        if not p.exists():
            continue
        txt = _scannable(p)
        for i in [m for m in range(len(txt)) if txt.startswith(word, m)]:
            w = txt[max(0, i - 130):i + len(word) + 60]
            assert any(n in w for n in NEG), (rel, w)


def test_claim_guard_would_catch_an_affirmative_violation(tmp_path):
    bad = tmp_path / "x.md"
    bad.write_text("# T\n\nThe method is distribution-free and production validated.\n")
    txt = _scannable(bad)
    i = txt.index("distribution-free")
    assert not any(n in txt[max(0, i - 130):i + 60] for n in NEG)


def test_novelty_wording_is_conservative():
    """Whitespace-normalised: the approved wording is a wrapped blockquote."""
    raw = (REPO / "level4/reports/LEVEL_4_FINAL_REPORT.md").read_text().lower()
    t = " ".join(raw.replace(">", " ").split())
    assert "exhaustive novelty is not established" in t
    assert "not currently persisted in the repository" in t
    for w in ("first-ever", "unprecedented"):
        for i in [m for m in range(len(t)) if t.startswith(w, m)]:
            assert any(n in t[max(0, i - 130):i + 60] for n in NEG), w


def test_final_report_states_level_1_3_closed_and_level_4_partial():
    t = (REPO / "level4/reports/LEVEL_4_FINAL_REPORT.md").read_text()
    assert "LEVEL-4-PARTIAL" in t
    assert "CLOSED" in t
    for label in ("STAGE-C-PARTIAL", "STAGE-D-PARTIAL", "STAGE-E-PARTIAL"):
        assert label in t


def test_deterministic_vs_stochastic_distinction_is_explicit():
    t = (REPO / "level4/stage_f/SCIENTIFIC_SYNTHESIS.md").read_text().lower()
    assert "deterministic" in t and "skeleton" in t
    assert "falsified" in t


# --------------------------------------------------------------- artifacts
@pytest.mark.parametrize("rel", [
    "level4/stage_f/README.md",
    "level4/stage_f/LEVEL4_REQUIREMENTS_RECONSTRUCTION.md",
    "level4/stage_f/INTEGRITY_AUDIT.md",
    "level4/stage_f/SCIENTIFIC_SYNTHESIS.md",
    "level4/stage_f/FINAL_DECISION.md",
    "level4/stage_f/notes/FAILURE_DIAGNOSES.md",
    "level4/stage_f/results/final_decision.json",
    "level4/stage_f/reproduce.sh",
    "level4/reports/LEVEL_4_FINAL_REPORT.md",
    "level4/reports/LEVEL_4_FINAL_LEDGER.md",
])
def test_required_stage_f_artifact_exists(rel):
    assert (REPO / rel).exists()


def test_stage_f_adversarial_suite_recorded():
    d = json.loads((RES / "adversarial_f.json").read_text())
    assert d["n_checks"] == 18
