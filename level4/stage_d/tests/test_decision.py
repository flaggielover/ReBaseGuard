"""The frozen decision rule and the artifacts it reads."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
PROTOCOL_SHA = "925adecf08c7234375333a26c3af934b005e0d8b4cfce470b77834d7245e8b2e"
ALLOWED = {"STAGE-D-INCONCLUSIVE", "STAGE-D-SR-FAILED",
           "STAGE-D-NONGAUSSIAN-PARTIAL", "STAGE-D-CLOSED-GENERALIZED",
           "STAGE-D-PARTIAL"}


def _d(n):
    return json.loads((RES / n).read_text())


def test_protocol_hash_unchanged():
    actual = hashlib.sha256((ROOT / "STAGE_D_PROTOCOL.md").read_bytes()).hexdigest()
    assert actual == PROTOCOL_SHA


def test_decision_label_is_one_of_the_frozen_five():
    assert _d("stage_d_decision.json")["decision"] in ALLOWED


def test_decision_is_partial_and_d2_3_is_the_reason():
    d = _d("stage_d_decision.json")
    assert d["decision"] == "STAGE-D-PARTIAL"
    assert d["gate_summary"]["D2_pass"] is False
    d23 = [c for c in d["criteria"] if c["id"] == "D2.3"][0]
    assert d23["status"] == "FAIL"


def test_d2_3_stays_failed_at_the_precommitted_primary_step():
    """Guards against a post-hoc smaller step being promoted to primary."""
    d = _d("d2_3_derivative.json")
    assert d["primary_step"] == 0.05
    assert d["criterion_met_all_m"] is False
    assert d["n_m_passing"] == 0


def test_richardson_is_labelled_diagnostic_only():
    assert "DIAGNOSTIC" in _d("d2_3_derivative.json")["richardson_note"].upper()


def test_d2_5_verdict_is_not_operational():
    v = _d("d2_5_verdict.json")
    assert v["verdict"] == "MATHEMATICAL, NOT OPERATIONAL"
    assert v["n_metrics_peaking_at_m_star"] == 0


def test_t3_ambiguity_is_preserved():
    d = _d("d3_nongaussian.json")
    t3 = [r for r in d["rows"] if r["family"] == "t3"][0]["per_m"][0]
    assert t3["lower_bound_exceeds_2"] is True
    assert t3["normalised_lower_bound_exceeds_2"] is False
    assert [c for c in _d("stage_d_decision.json")["criteria"]
            if c["id"] == "D3.2-t3"][0]["status"] == "AMBIGUOUS"


def test_naive_gamma_T_is_never_promoted():
    d = _d("d3_nongaussian.json")
    assert "DIAGNOSTIC" in d["d3_3_note"].upper()
    for r in d["rows"]:
        assert "DIAGNOSTIC_ONLY" in "".join(r["per_m"][0].keys())


def test_adversarial_suite_all_pass():
    assert _d("adversarial_d.json")["n_failed"] == 0


def test_d4_was_not_run():
    d4 = [c for c in _d("stage_d_decision.json")["criteria"] if c["id"] == "D4"][0]
    assert d4["status"] == "NOT RUN"


REPORTS = ["STAGE_D_REPORT.md", "STAGE_D_LEDGER.md"]


def _scannable(path: Path) -> str:
    """Report text with the explicitly declared forbidden-phrase block removed.

    A section whose job is to LIST banned phrases must be allowed to contain
    them -- the same exemption the A11 code guard grants itself. Everything
    else in the document is scanned.
    """
    txt = path.read_text()
    out, skipping = [], False
    for line in txt.splitlines():
        if line.startswith("#") or line.startswith("## "):
            skipping = "forbidden wording" in line.lower()
        if not skipping:
            out.append(line)
    return "\n".join(out).lower().replace("*", "").replace("`", "")


def test_the_forbidden_wordings_block_exists():
    """The exemption above is only sound if the block is actually declared."""
    for r in REPORTS:
        txt = (ROOT.parent / "reports" / r).read_text().lower()
        assert "forbidden wording" in txt or "explicitly ruled out" in txt


# A forbidden word is acceptable when negated, and -- for "certified" only --
# when explicitly ATTRIBUTED to an earlier stage. Stage D produced nothing
# certified, but it must be able to cite what Stage B and Level 1-3 did.
NEGATIONS = ("not ", "never", "no ", "❌", "rather than", "inherited",
             "nothing", "cannot", "must not", "ruled out")
ATTRIBUTIONS = ("stage b", "level 1", "level 2c", "rigorous-certified",
                "frozen-certified", "enclosure")


def _licensed(word: str, window: str) -> bool:
    if any(n in window for n in NEGATIONS):
        return True
    # attribution licenses only "certified", and only to a named earlier stage
    return word == "certified" and any(a in window for a in ATTRIBUTIONS)


@pytest.mark.parametrize("word", [
    "detector-independent", "distribution-free", "universal",
    "first stability boundary", "certified", "phase transition",
])
def test_forbidden_wordings_only_appear_negated_or_attributed(word):
    for r in REPORTS:
        txt = _scannable(ROOT.parent / "reports" / r)
        for i in [m for m in range(len(txt)) if txt.startswith(word, m)]:
            w = txt[max(0, i - 120):i + len(word) + 60]
            assert _licensed(word, w), (r, w)


def test_attribution_does_not_license_a_stage_d_certified_claim():
    """Meta-test: attribution must not become a loophole. A Stage D result
    called 'certified' with no earlier-stage attribution must still fail."""
    assert not _licensed("certified",
                         "the stage d monte carlo gamma_sr is certified above 2")
    assert _licensed("certified",
                     "inside the stage b certified enclosure")
    # attribution must not license the other banned words
    assert not _licensed("distribution-free",
                         "stage b shows this is distribution-free")


def test_the_guard_would_catch_an_affirmative_violation(tmp_path):
    """Meta-test: the exemption must not have disabled the guard."""
    bad = tmp_path / "STAGE_D_REPORT.md"
    bad.write_text("# X\n\nThe result is distribution-free and universal.\n")
    txt = _scannable(bad)
    i = txt.index("distribution-free")
    w = txt[max(0, i - 120):i + 60]
    assert not _licensed("distribution-free", w)


def test_confirmatory_seeds_are_disjoint_from_prior_work():
    prior = {1234, 1729, 2024, 2026, 4242, 5150, 8080, 31337, 90210,
             20260820, 20260821, 20260822, 20260901, 20260902, 20260931}
    assert {20261001, 20261002, 20261031}.isdisjoint(prior)
